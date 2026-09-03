"""Filed-document selection and text extraction for predict inputs.

The input-richness half of the live-sources design: the docket JSON links every
filed PDF, and the questions presented plus the petition/BIO are the signals
cert prediction actually turns on. What is selected is keyed on the **filing**,
not on the docket form: the case-opening filing of a cert-form docket (a
petition for certiorari, certiorari before judgment, mandamus or habeas corpus,
or a direct appeal's statement as to jurisdiction — one ``petition`` kind, one
role), the ``application`` an interim docket is opened by, and every
non-amicus brief in opposition. Everything here is **pipeline-side** —
documents are fetched and text-extracted at ingest time (the live poller, on
the same distribution transition that queues prediction), stored in the
access-gated corpus, and materialized into the cell's gitignored ``record/``
path at provisioning — so the snapshot rule holds, every predictor in a
fan-out reads identical content, and agents never fetch.

Two findings shape the selection (docs/live-sources.md plus a live
check at implementation):

- **``QPLink`` is an outcome artifact, never an input.** The ``/qp/`` page is
  generated when certiorari is *granted* and opens with the grant order — its
  very presence leaks the outcome (it was present on 1/64 probed records: the
  granted one). The questions presented are instead derived from the petition
  PDF itself, whose QP page fronts the filing.
- **Document links are a rolling window** (~OT2021+), so fetching happens near
  filing time and a missing document is an expected condition.

Only :func:`fetch_case_documents` touches the network (through the polite
:class:`~fedcourtsai.supremecourt.SupremeCourtClient`); selection, extraction,
and the QP derivation are pure and tested offline. Extraction is pure *at its
default*: :func:`extract_pdf_text` takes an optional :data:`OcrPage` seam, and
the one effectful implementation — a tesseract call over a rendered page — is
injected by the recovery pass alone, so no other caller of this module carries
that dependency. Because the derivation is
pure, it can also be re-run over text already stored —
:func:`backfill_questions_presented`, the convergence sweep that carries an
extractor fix onto the rows an unchanged petition URL would otherwise freeze.
"""

from __future__ import annotations

import io
import logging
import re
import sqlite3
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .. import corpus
from ..supremecourt import SupremeCourtClient

# `_scored_segment` is the salience gate's paid modern-cert predicate, imported
# rather than restated: the censuses cut their frames with it, and `caption` is
# where the non-`analytics` definition lives (a test pins the two equal). The
# import direction is safe — `caption` reaches only `corpus`, `schemas`, and
# `supremecourt`, so nothing here closes a cycle.
from .caption import _scored_segment

# The interim lane's own reading of what an application asks for. Imported
# rather than restated so the selector fetches exactly the class the predict
# queue admits (:func:`interim_signals.is_predictable_application`), and so a
# change to either moves both. The import direction is safe — `interim_signals`
# reaches only `schemas` and `cert_signals`, neither of which reaches here.
from .interim_signals import ApplicationKind, application_kind
from .prefetch import prefetch_by_case

logger = logging.getLogger(__name__)

# Document kinds, in provisioning order. `questions_presented` is derived from
# the petition text rather than fetched (see the module docstring).
#
# `petition` is the **case-opening filing on a cert-form docket**, not only a
# petition for a writ of certiorari: the Court opens a cert-form docket on any
# of the family :data:`_CASE_OPENING_ENTRY_RE` matches, and all of them are the
# same document to every reader here — the one that asks the Court to take the
# case, fronting the questions presented under the same rules (Rule 14.1(a) for
# certiorari, Rule 20.2 for an extraordinary writ, Rule 18.3 for a direct
# appeal's jurisdictional statement). A kind per writ would fracture
# :data:`TEXT_COVERAGE_KINDS`, the questions-presented derivation, and the cell
# manifest across seven names for one role.
#
# `application` is the separate kind, because an application is a different ask
# on a different docket form: it seeks interim relief rather than review, it
# carries no questions-presented section, and keying it apart is what lets the
# coverage report's application-form count read as a gap that drains rather
# than a floor that cannot.
KIND_PETITION = "petition"
KIND_APPLICATION = "application"
KIND_BRIEF_IN_OPPOSITION = "brief-in-opposition"
KIND_QUESTIONS_PRESENTED = "questions-presented"

# The proceedings entry whose link carries the case-opening filing on a
# cert-form docket, in the Court's own words. Seven entry shapes open one:
#
#   "Petition for a writ of certiorari filed."
#   "Petition for a writ of certiorari before judgment filed."
#   "Petition for a writ of mandamus filed."
#   "Petition for a writ of mandamus and/or prohibition filed."
#   "Petition for a writ of prohibition filed."
#   "Petition for writ of habeas corpus filed."   <- no "a", the Clerk's spelling
#   "Statement as to jurisdiction filed."         <- a direct appeal
#
# The article is optional because the habeas form omits it; the writ vocabulary
# is closed rather than `\w+` because "petition for a writ of ... filed" also
# spells the front of an amicus entry supporting one, and a closed list keeps
# the widening to the shapes actually read off the docket. The `and motion`
# clause is the in-forma-pauperis pairing ("Petition for a writ of certiorari
# and motion for leave to proceed in forma pauperis filed."), which rides on
# every writ.
#
# Anchored at the entry's start, because the phrase also appears mid-sentence in
# a filing *about* the petition: "Motion of petitioner to dismiss the petition
# for a writ of mandamus filed." Docket order usually saves an unanchored
# reading — the real opening entry comes first — but not on the one docket shape
# this arm exists for, a Rule 34.6 filing whose opening entry carries no link,
# where the motion's PDF would then be stored as the petition. The cross-petition
# alternative keeps its own opening entry matchable for the same reason.
_CASE_OPENING_ENTRY_RE = re.compile(
    r"^\s*(?:conditional cross-)?petition for (?:a )?writ of"
    r" (?:certiorari(?: before judgment)?|mandamus(?: and/or prohibition)?"
    r"|prohibition|habeas corpus)"
    r"(?: and motion\b[^.]*)? filed"
    r"|^\s*statement as to jurisdiction filed",
    re.IGNORECASE,
)
# The link labels a case-opening entry carries, most specific first: every writ
# form posts its PDF as `Petition`, while a direct appeal's
# jurisdictional statement posts as `Jurisdictional Statement`. Both are named
# rather than left to the any-link fallback, so an entry that also carries an
# appendix or a motion link still yields the filing itself.
_CASE_OPENING_LINK_LABELS = ("petition", "jurisdictional statement")
# The application's own submission entry, on an application-form docket or on a
# cert docket an interim application was filed into:
#
#   "Application (26A203) for a stay of the mandate, submitted to Justice Kagan."
#
# Anchored the way `interim_signals.application_arrival_date` anchors: the
# number in its parentheses, then the filing verb within a bounded span. The
# verb is what keeps a *disposing* order out — "Applications for stays (23A349,
# 23A350) granted by the Court." names no submission — and the number is what
# keeps the ask clause readable for the extension test below.
#
# One thing this anchors that the arrival rule does not, and it has to: the
# entry's own **opening**, in `_RESPONSE_FILED_RE`'s idiom. The arrival rule is
# reading dates off entries it has already decided are the application's; a
# selector reads every entry on the docket, where "Response to application
# (26A203) … submitted" recites the number and carries the verb while linking
# the *respondent's* PDF. Requiring the entry to begin with an application
# number is what keeps a recital from being stored as the application.
# The plural disposing form is excluded twice over by it: "Applications for
# stays (23A349…" puts an `s` where the parenthesis has to be.
#
# Any A-number rather than the docket's own, which is the other place this
# differs from the arrival rule: that rule is dating *this* docket's stage and
# must not borrow a companion's entry, while a selector is asked only whether
# the entry it is looking at is an application being submitted. A cert docket
# carrying an interim application under its own separate A-number is exactly the
# case a docket-number anchor would miss.
_APPLICATION_ENTRY_RE = re.compile(
    r"^\s*application\s*\(\s*\d{2}A\d+\s*\).{0,200}?\bsubmitted\b", re.IGNORECASE
)
# A respondent's brief opposing the petition, as it reads on the docket. Two
# phrasings appear: the explicit "... in opposition ...", and — once the Court
# has called for a response — the bare "Brief of respondent(s) X ...". Both post
# as "filed" or, the day they land (before the Clerk formally accepts them),
# "submitted"; matching only "filed ... in opposition" systematically missed
# both a just-submitted BIO and a respondent's response brief that omits the
# "in opposition" words. Amicus / petitioner / reply / supplemental / in-support
# briefs are not oppositions.
_BIO_VERB_RE = re.compile(r"\b(?:filed|submitted)\b", re.IGNORECASE)
_BIO_OPPOSITION_RE = re.compile(r"\bin opposition\b", re.IGNORECASE)
_BIO_RESPONDENT_BRIEF_RE = re.compile(r"\bbrief\s+of\s+respondents?\b", re.IGNORECASE)
_BIO_EXCLUDE_RE = re.compile(
    r"\bamic|\breply\b|\bsupplement|\bpetitioner\b|\bin support\b", re.IGNORECASE
)


def _is_bio_entry(text: str) -> bool:
    """Whether a proceedings entry is a respondent's brief in opposition.

    Requires a filed/submitted brief that is either explicitly "in opposition"
    or a respondent's brief (the response the Court called for), and is not an
    amicus, petitioner, reply, supplemental, or in-support brief.
    """
    if "brief" not in text.lower() or not _BIO_VERB_RE.search(text):
        return False
    if _BIO_EXCLUDE_RE.search(text):
        return False
    return bool(_BIO_OPPOSITION_RE.search(text) or _BIO_RESPONDENT_BRIEF_RE.search(text))


# Where the questions-presented section of a petition ends: the next standard
# front-matter heading. Petitions front the QP page, so the section runs from
# the QUESTION(S) PRESENTED heading to the first of these that is *set as a
# heading* (:func:`_is_heading_match`), not merely spelled like one.
#
# The words of a phrase are joined by `\s+`, never a literal space, because a
# printed heading's words are separated by whatever the layout left between
# them and the extraction preserves that: one space, the extra blanks a
# justified caps line extracts with ("PARTIES  TO  THE  PROCEEDING"), a run of
# TABS where the filing sets its front matter in a table — some petitions
# extract with tabs as their only separator, no line break after the heading
# and the question running on the heading's own line — or a line break the
# printed heading wrapped at ("RELATED\nCASES"). A literal space reads every
# one of those as no terminator at all, and the cost is not a long section: the
# capture runs past the front matter into the table of contents, where the
# leader-dot rule discards it, so the heading is found and nothing is derived.
# Widening the separator shortens sections in practice (every corpus change it
# produced was a strict prefix of the old value); it is NOT shorten-only by
# construction — a new match rejected as a heading can consume span that hides
# a later old-accepted one — but that path degrades to an over-capture, never a
# fragment, which the section-end docstring already declares tolerated.
# Authoring constraint for the phrase tuple: word sequences whose only regex
# constructs are (?:...) groups and escaped literals — the blanket
# space-to-\s+ rewrite below would corrupt a space inside a character class.
_QP_START_RE = re.compile(r"QUESTIONS?\s+PRESENTED", re.IGNORECASE)
_QP_END_PHRASES = (
    "PARTIES TO THE PROCEEDING",
    "CORPORATE DISCLOSURE",
    r"RULE 29\.6",
    "RELATED (?:CASES|PROCEEDINGS)",
    "TABLE OF CONTENTS",
    "TABLE OF AUTHORITIES",
    "LIST OF (?:ALL )?(?:PARTIES|PROCEEDINGS)",
    "OPINIONS? BELOW",
    "IN THE SUPREME COURT",
)
_QP_END_RE = re.compile(
    "|".join(phrase.replace(" ", r"\s+") for phrase in _QP_END_PHRASES), re.IGNORECASE
)
# Title case as a petition sets a heading: a capitalized first word, then
# capitalized words and the lower-case function words that stay small in a title
# ("Parties to the Proceeding", "Table of Authorities"). Used with the position
# test in :func:`_is_heading_match`.
_QP_TITLE_CASE_RE = re.compile(
    r"[A-Z][A-Za-z0-9.]*(?:\s+(?:of|to|the|in|and|for|a|an)\b|\s+[A-Z0-9][A-Za-z0-9.]*)*"
)
# A QP section beyond this is a parsing miss, not a question (they run a page).
_QP_MAX_CHARS = 4_000
# Below this a capture is a front-matter crumb, not a question. The crumbs the
# scan lands on — a table-of-contents folio ("i"), a numbered heading stub ("I.
# In the") — run one to fifteen characters; a real QP page runs hundreds, and
# its shortest legitimate shape is the bare overrule question ("Whether Roe v.
# Wade should be overruled." — 40 characters). 40 is therefore a judgment on
# where to cut, not a measured boundary: it clears every observed crumb by a
# wide margin, and the questions it can cost are the handful pitched shorter
# still ("Whether Chevron should be overruled." — 36). That trade is the right
# way round because a capture under the floor degrades to the *empty*
# extraction, which the manifest labels as such and the labeling extract skips,
# while a fragment stored as text reads to every consumer as the question.
_QP_MIN_CHARS = 40
# A captured section that is really a table-of-contents entry, in the two forms
# a TOC aligns its page numbers. A petition's own TOC lists "QUESTIONS
# PRESENTED" with a page reference, so matching that entry instead of the real
# heading captures the TOC instead of the questions.
#
# Leader dots (to a page number): pypdf preserves them, and a genuine QP body —
# prose — never carries a run of them, so the run is the reliable tell.
# Tolerates the spaced form (". . . .") some fonts extract to, which is also why
# the run has to be long: a legal quotation elides with a four-dot ellipsis
# (". . . ."), so a shorter bound reads a question quoting a statute as a
# contents page. A printed leader runs the width of the line — dozens of dots —
# so eight is far below any real leader and far above any ellipsis.
_QP_TOC_RE = re.compile(r"(?:\.\s*){8,}")
# Space alignment: the same entry set flush-right with blanks instead of dots,
# which leaves the capture (everything *after* the heading text) as nothing but
# alignment and the folio the entry points at — roman in the front matter,
# arabic in the body. Bounded the way the dot rule bounds itself: a run of
# blanks no word spacing produces, and then the folio must be all that is left
# of the line. A real QP page cannot look like this — its heading is followed by
# the question, not by a bare number — so the rule stays a TOC discriminator
# rather than a page filter.
_QP_TOC_FOLIO = r"[ \t]{3,}(?:[ivx]{1,6}|\d{1,3})[ \t]*"
_QP_TOC_SPACES_RE = re.compile(rf"\A{_QP_TOC_FOLIO}(?:\n|\Z)", re.IGNORECASE)
# The same shape seen from the other side, for classifying an *already stored*
# QP text (whose leading alignment has long since been stripped): a line of the
# stored value that ends heading-text, blanks, folio is TOC residue. Folios only
# in the case front matter prints them — lower-case roman — because here a
# capitalized token *does* follow text on the line, and upper-case roman would
# read a justified line ending "under Title   VII" as a contents entry.
_QP_TOC_LINE_RE = re.compile(rf"\S{_QP_TOC_FOLIO}(?:\n|\Z)")


@dataclass(frozen=True)
class DocumentRef:
    """One fetchable filed document, selected from the docket JSON."""

    kind: str
    url: str
    entry_date: str | None
    description: str


@dataclass(frozen=True)
class ExtractedText:
    """The text recovered from one PDF, and how it was arrived at."""

    text: str
    pages: int
    truncated: bool
    ocr_derived: bool = False
    """Whether any page's text came from OCR rather than the PDF's text layer."""


# The OCR seam: a page index into the same PDF's `reader.pages` order (0-based)
# -> the text OCR read off that page's rendered image, or "" where it read
# nothing. Injected rather than imported so the extractor — which every fetching
# lane calls — carries no OCR dependency; only the recovery pass, whose own step
# installs tesseract, supplies one. An implementation should own its failures
# and return "" rather than raise; the extractor enforces that either way, since
# a raising renderer must cost its own page, never the digital pages beside it.
OcrPage = Callable[[int], str]


def _entry_link(
    entry: Mapping[str, Any], *, prefer: tuple[str, ...], fallback: bool = True
) -> tuple[str, str] | None:
    """(url, description) of the first preferred link on an entry, else its first.

    ``prefer`` is a label list in preference order, matched case-insensitively
    against the link's ``Description``, because one entry family can post its
    filing under more than one label — a cert petition as ``Petition``, a direct
    appeal's opening filing as ``Jurisdictional Statement``. The any-link
    fallback keeps an unforeseen label fetchable rather than dropping the entry,
    which is why the list is a preference and not a filter.

    ``fallback=False`` makes it a filter, for the one caller whose entries carry
    links that are reliably *not* the filing: an application entry posts
    ``Written Request`` and ``Proof of Service`` beside (or instead of) its
    ``Main Document``, and taking the first link there stores a covering letter
    as the application's text.
    """
    links = [link for link in entry.get("Links") or [] if isinstance(link, Mapping)]
    for label in prefer:
        for link in links:
            if str(link.get("Description", "")).strip().lower() == label:
                url = str(link.get("DocumentUrl") or "").strip()
                if url:
                    return url, str(link.get("Description", ""))
    if not fallback:
        return None
    for link in links:
        url = str(link.get("DocumentUrl") or "").strip()
        if url:
            return url, str(link.get("Description", ""))
    return None


def _is_application_entry(text: str) -> bool:
    """Whether an entry is an application's own submission, seeking relief.

    Two conditions, and the second is a **positive** test rather than an
    exclusion list. The entry must be a submission
    (:data:`_APPLICATION_ENTRY_RE`), and its ask must read *substantive* to
    :func:`~fedcourtsai.pipeline.interim_signals.application_kind` — the same
    predicate :func:`~fedcourtsai.pipeline.interim_signals.is_predictable_application`
    gates the interim predict queue on, so the selector fetches exactly the
    class that mints cells and nothing else.

    The alternative — "any submission that is not an extension of time" — is
    what the docket defeats. The Clerk writes renewals as "Application (24A797)
    **to extend further the time** from June 11 to July 11, submitted to Justice
    Kavanaugh", which no plain extension phrase catches, and the administrative
    family is wider than extensions anyway: leave to file a brief "in excess of
    the word limit" is the same kind of covering request. Each one selected is a
    wasted fetch, a lawyer's letter in the cell's ``record/documents/``, and a
    row on a coverage report whose kind then means two things. Reading the ask
    positively bounds the arm by what the interim stage can actually forecast.

    An ask the classifier cannot read (``unknown``) is not selected. That is the
    conservative direction and it costs no cell: the same reading keeps the
    docket out of the predict queue, so nothing is ever minted that would have
    wanted the document.

    The Clerk's **renewal** form falls out of the same rule rather than needing
    its own exclusion, which is where this differs from the arrival-date rule
    (``interim_signals._APPLICATION_RENEWAL_RE`` names it explicitly).
    "Application (26A118) refiled and submitted to Justice Alito." states no
    ask, so it reads ``unknown`` and is not selected on its own; a renewal that
    *does* restate the ask is, and on a docket carrying both, docket order takes
    the head entry first anyway. The arrival rule has to name the form because
    it is dating a stage and a renewal postdates the application's own first
    denial; a selector that already refuses an unreadable ask inherits the
    protection.
    """
    return (
        _APPLICATION_ENTRY_RE.search(text) is not None
        and application_kind([text]) is ApplicationKind.substantive
    )


def select_documents(payload: Mapping[str, Any]) -> list[DocumentRef]:
    """The fetchable predict-input documents on one docket JSON (pure).

    Three arms, all entry-keyed rather than form-keyed — the payload says which
    filings it carries, and nothing here needs to be told the docket's form.

    - The **case-opening filing** (:data:`_CASE_OPENING_ENTRY_RE`), stored as
      ``petition``: the ordinary cert petition, a petition for certiorari
      before judgment, for mandamus, for prohibition, or for habeas corpus, and
      a direct appeal's statement as to jurisdiction. One per docket, the first
      in docket order, taken from the entry's own ``Petition`` or
      ``Jurisdictional Statement`` link.
    - The **application** (:func:`_is_application_entry`), stored as
      ``application``: the entry submitting an application for **substantive**
      interim relief to a Justice, taken from its ``Main Document`` link and
      from no other. One per docket, the first in
      docket order — an application docket has one application, and a
      later entry naming the number is reciting it. Selected on a cert docket
      too where an interim application was filed into one, which is the right
      reading: the filing is real and the cell should read it. An
      administrative application — more time, more pages — is not selected.
    - **Every** non-amicus brief in opposition — a petition with multiple
      respondents draws a BIO from each, and taking only the last silently
      dropped the lead respondent's (the most predictive one) whenever a
      secondary respondent filed later. All distinct-URL BIOs are returned, in
      docket order; :func:`fetch_case_documents` combines them into the single
      ``brief-in-opposition`` document.

    ``QPLink`` is deliberately never selected: it is generated at grant time and
    leaks the outcome; the questions presented are derived from the petition
    text instead (:func:`extract_questions_presented`).
    """
    petition: DocumentRef | None = None
    application: DocumentRef | None = None
    bios: list[DocumentRef] = []
    seen_bio_urls: set[str] = set()
    for entry in payload.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        text = str(entry.get("Text") or "")
        entry_date = str(entry.get("Date") or "") or None
        if petition is None and _CASE_OPENING_ENTRY_RE.search(text):
            found = _entry_link(entry, prefer=_CASE_OPENING_LINK_LABELS)
            if found is not None:
                petition = DocumentRef(KIND_PETITION, found[0], entry_date, found[1])
        elif application is None and _is_application_entry(text):
            # No any-link fallback here: an application entry's other links are
            # the covering `Written Request` and `Proof of Service`, which are
            # not the filing (:func:`_entry_link`).
            found = _entry_link(entry, prefer=("main document",), fallback=False)
            if found is not None:
                # The entry text, not the generic "Main Document" label: it
                # names the ask and the Justice it went to, which is what a
                # reader of the manifest needs to know the document is.
                application = DocumentRef(KIND_APPLICATION, found[0], entry_date, text.strip())
        elif _is_bio_entry(text):
            found = _entry_link(entry, prefer=("main document",))
            if found is not None and found[0] not in seen_bio_urls:
                seen_bio_urls.add(found[0])
                # Carry the docket entry text (it names the respondent) as the
                # description, not the generic "Main Document" link label — it
                # heads this brief's block in the combined BIO document.
                bios.append(
                    DocumentRef(KIND_BRIEF_IN_OPPOSITION, found[0], entry_date, text.strip())
                )
    return [ref for ref in (petition, application, *bios) if ref is not None]


def primary_entry_matched(payload: Mapping[str, Any], *, kind: str) -> bool:
    """Whether the docket carries the entry that opens it, link or no link.

    :func:`select_documents` answers *what is fetchable*, which collapses two
    very different dockets onto the same empty list: one whose opening filing is
    on the docket with no PDF posted behind it — a Rule 34.6 paper filing, where
    the Court served nothing and no repair reaches it — and one carrying no such
    entry at all, which on a modern docket means the selector has no arm for the
    filing type. Only the second is a defect. This is the same entry test the
    selector's two primary arms apply, with the link requirement dropped, so a
    caller can tell them apart; it reads nothing about the opposition briefs,
    which open no case.

    ``kind`` is the docket form's primary document (:data:`KIND_PETITION` or
    :data:`KIND_APPLICATION`); any other kind matches nothing, since no other
    kind opens a docket.
    """
    for entry in payload.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        text = str(entry.get("Text") or "")
        if kind == KIND_PETITION and _CASE_OPENING_ENTRY_RE.search(text):
            return True
        if kind == KIND_APPLICATION and _is_application_entry(text):
            return True
    return False


def extract_pdf_text(
    data: bytes, *, char_cap: int, ocr_page: OcrPage | None = None
) -> ExtractedText:
    """Extract a PDF's text with pypdf, capped at ``char_cap`` characters.

    SCOTUS filings are born-digital under the 2017 e-filing mandate, so plain
    text extraction is reliable; a scanned paper filing (some IFP petitions)
    yields little or nothing — recorded as empty text, never a crash. The cap
    bounds corpus growth (petitions run 30-300 pages); truncation is flagged so
    provisioning can say so to the reading agent.

    With an ``ocr_page`` supplied — the recovery pass's lane, never a fetching
    one — a page whose own extraction yields nothing is read off its image
    instead. A guard rather than a filter: the recovery population is documents
    that extracted to nothing at all, but running it per page is what keeps a
    mostly-digital filing with a few scanned exhibit pages honest, since a page
    that *did* extract is never overwritten by a lossier reading of it. The cap
    and the truncation flag bound the result identically either way, so a
    recovered document is bounded exactly like a fetched one, and
    ``ocr_derived`` is set only where OCR actually contributed text. A raising
    ``ocr_page`` costs its own page and no more.
    """
    try:
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        total = 0
        truncated = False
        ocr_derived = False
        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if ocr_page is not None and not text.strip():
                try:
                    recovered = ocr_page(index)
                except Exception:  # broad by design: see below
                    # A renderer or OCR failure costs its own page and nothing
                    # else. Outside this guard the same raise would exit through
                    # the whole-document handler below, discarding every digital
                    # page that did extract and storing `pages=0` — which the
                    # recovery population reads as "a PDF that would not open",
                    # ejecting the row from the class permanently.
                    recovered = ""
                if recovered.strip():
                    text = recovered
                    ocr_derived = True
            parts.append(text)
            total += len(text)
            if total >= char_cap:
                truncated = True
                break
        joined = "\n".join(parts)
        if len(joined) > char_cap:
            joined = joined[:char_cap]
            truncated = True
        return ExtractedText(
            text=joined,
            pages=len(reader.pages),
            truncated=truncated,
            ocr_derived=ocr_derived,
        )
    except (PyPdfError, ValueError, TypeError):
        return ExtractedText(text="", pages=0, truncated=False)


def _is_toc_capture(capture: str) -> bool:
    """Whether a raw capture is a table-of-contents entry rather than a QP body.

    Both alignments a TOC uses — leader dots, and blanks to a flush-right folio
    (see the two regexes). Read the *raw* capture, before stripping: the blank
    run is the space form's evidence.
    """
    return bool(_QP_TOC_RE.search(capture) or _QP_TOC_SPACES_RE.match(capture))


def _is_heading_match(text: str, match: re.Match[str]) -> bool:
    """Whether an end-heading match is set as a heading rather than said in prose.

    Two ways a petition sets one, and the test takes either. **All caps** counts
    wherever it lands, since nothing in a question body shouts a front-matter
    heading's exact words. **Title case counts only at the start of a line** —
    the position a heading occupies — because title case alone cannot separate
    "Opinions Below" the heading from a sentence that opens on the same words,
    and line position alone cannot either, since extracted line breaks fall
    wherever the PDF put them.
    """
    span = match.group()
    if span == span.upper():
        return True
    if not _QP_TITLE_CASE_RE.fullmatch(span):
        return False  # sentence-case prose: "the opinion below", "in the Supreme Court"
    line_start = text.rfind("\n", 0, match.start()) + 1
    return not text[line_start : match.start()].strip()


def _qp_section_end(rest: str) -> int | None:
    """Where the questions-presented section ends in ``rest``, or ``None``.

    The first end-heading match that is set as a heading
    (:func:`_is_heading_match`). The vocabulary is matched case-insensitively —
    it has to be, since pypdf recovers a small-caps heading in whatever case the
    font stored — and several of its alternatives are also ordinary English:
    "the opinion below", "corporate disclosure", "related proceedings", "in the
    Supreme Court". Taking the first match outright therefore cuts a question
    short at the phrase inside it; walking on to the first match that is *set*
    as a heading keeps prose out of the terminator. A heading the extraction
    flattens past recognition costs an over-capture — the section runs to the
    next heading, or to the length cap — never a fragment, which is the failure
    that matters.
    """
    for match in _QP_END_RE.finditer(rest):
        if _is_heading_match(rest, match):
            return match.start()
    return None


def extract_questions_presented(petition_text: str) -> str | None:
    """The questions-presented section of a petition's text.

    Petitions front the QP page (Rule 14.1(a)), so the section runs from the
    QUESTION(S) PRESENTED heading to the next standard front-matter heading.
    But a petition's own table of contents lists that heading too, and matching
    the TOC entry captures the TOC lines instead of the questions — so scan
    *every* occurrence and return the first capture that reads as a question
    body: not a TOC entry (:func:`_is_toc_capture`), and at least
    :data:`_QP_MIN_CHARS` long, the floor below which a capture is a
    front-matter crumb. Length-capped at the other end too: a runaway match
    means the end-heading regex missed, and a 4-page "question" would only bury
    the signal it exists to surface.

    Three results, and the third is the point of the distinction: the section
    when one survives; ``None`` when the petition names no QUESTION(S) PRESENTED
    heading at all (nothing to derive, so no row is stored); and the **empty
    string** when the heading is there but no capture under it is usable — a
    degraded extraction, stored as an empty-text row so the documents manifest's
    ``empty_text`` flag labels it exactly as it labels a scanned filing with no
    text layer. A fragment stored as text reads to every downstream consumer as
    the questions this case presents.
    """
    heading_seen = False
    for start in _QP_START_RE.finditer(petition_text):
        heading_seen = True
        rest = petition_text[start.end() :]
        end = _qp_section_end(rest)
        capture = rest[:end] if end is not None else rest[:_QP_MAX_CHARS]
        if _is_toc_capture(capture):
            continue  # a TOC entry, dotted or space-aligned — not the questions body
        section = capture.strip()
        if len(section) < _QP_MIN_CHARS:
            continue  # an empty capture or a front-matter crumb
        return section[:_QP_MAX_CHARS]
    return "" if heading_seen else None


# The ways a selected document produces no stored row. A missing document is an
# expected condition here (the upstream link window is a rolling one), which is
# exactly why the skips have to be *recorded*: undifferentiated, a link the
# upstream did not serve and a transport failure leave the same trace — none —
# and the population that reaches prediction with no petition is then a count
# with no route attached to it. The reasons are kept apart because their repairs
# differ: a transport failure is worth re-attempting on the same URL, and a link
# that was not served is worth chasing to a different one.
FETCH_LOSS_HTTP_ERROR = "http-error"
FETCH_LOSS_UNAVAILABLE = "unavailable"
FETCH_LOSS_BIO_EMPTY = "bio-empty"
# The fourth reason is one step earlier than the three above, and it is the one
# loss they cannot see: they are raised inside the loops over
# `select_documents`' output, so a docket the pass was *asked* to fetch for and
# selected nothing on leaves no trace among them — and a case that reaches
# prediction with no document then looks exactly like a case that was never
# provisioned. Recorded per case, at the one place that knows selection came
# back empty.
FETCH_LOSS_NOT_SELECTED = "not-selected"
# What `not-selected` names in the log line's kind slot. Not a stored kind:
# selection produced no kind at all, so the line names the role the case ends
# without rather than a document that was chosen and then lost.
_NOT_SELECTED_KIND = "the primary document"


@dataclass(frozen=True)
class DocumentFetchLosses:
    """How many selected documents a fetch pass dropped, by reason.

    ``http_error`` is a transport failure the client's own retry did not clear;
    ``unavailable`` an upstream 404 (:meth:`SupremeCourtClient.get_document`
    returns ``None``) — the rolling-window miss; ``bio_empty`` a case whose
    opposition briefs were all selected and none fetched, so the combined
    ``brief-in-opposition`` row was never built. Those three are post-selection.
    ``not_selected`` is the pre-selection one: a case whose docket JSON
    nominated no document at all, so nothing was ever attempted for it — the
    class an upstream that posts no PDF (a Rule 34.6 paper filing) and a
    selector with no arm for the filing type both land in, and the reason the
    other three cannot see either. The last two count *cases*, not documents,
    and ``bio_empty`` does not partition the two above it: the per-brief
    failures that emptied the group are counted there as well. ``not_selected``
    is disjoint from all three by construction — nothing was selected, so
    nothing could fail. Both case counts are per *attempt*, not per distinct
    case: a docket the poller reaches twice in one process counts twice, which
    is the reading a pass-level record wants and the one the run log shows.
    """

    http_error: int = 0
    unavailable: int = 0
    bio_empty: int = 0
    not_selected: int = 0

    @property
    def records(self) -> int:
        """How many losses were recorded — a record count, not a document count.

        Named for what it sums, because the fields do not share a unit: the two
        fetch reasons count documents while ``bio_empty`` and ``not_selected``
        count cases, so a "total documents lost" reading of it would
        double-count every case whose whole opposition failed and over-count
        every case that selected nothing. What it is good for is the only
        question that needs one number: whether this pass lost anything at all.
        """
        return self.http_error + self.unavailable + self.bio_empty + self.not_selected


# Process-wide and monotonic within a run, read through `document_fetch_losses`.
# The fetch path is serial by construction — `provision_documents` is called
# from the live poller's own sequential walk, and nothing here rides the
# read-side prefetch pool — so the counter needs no lock.
_fetch_losses: Counter[str] = Counter()


def _record_fetch_loss(reason: str, case_id: str, kind: str, detail: str) -> None:
    """Count one dropped document and say so in the run log.

    Both halves matter and neither replaces the other: the counter is what a
    caller in the same process can assert on, and the warning is what survives
    into the run log of an ephemeral runner, where nothing reads a counter. The
    level is ``warning`` even for the expected 404, because the default root
    configuration discards anything below it and a silently discarded record is
    the condition this exists to end.
    """
    _fetch_losses[reason] += 1
    logger.warning("documents: dropped %s for %s (%s): %s", kind, case_id, reason, detail)


def document_fetch_losses() -> DocumentFetchLosses:
    """What this process has recorded, since start or the last reset.

    Nothing in the pipeline resets it: the poller's whole run is the unit a
    reader wants, and the run log carries the per-document detail either way.
    :func:`reset_document_fetch_losses` exists for a caller that wants one
    pass's record read apart from another's.
    """
    return DocumentFetchLosses(
        http_error=_fetch_losses[FETCH_LOSS_HTTP_ERROR],
        unavailable=_fetch_losses[FETCH_LOSS_UNAVAILABLE],
        bio_empty=_fetch_losses[FETCH_LOSS_BIO_EMPTY],
        not_selected=_fetch_losses[FETCH_LOSS_NOT_SELECTED],
    )


def reset_document_fetch_losses() -> None:
    """Zero the counter, so one pass's record is not read over another's."""
    _fetch_losses.clear()


def _combine_bio_documents(
    client: SupremeCourtClient,
    case_id: str,
    bio_refs: list[DocumentRef],
    *,
    stored_url: str | None,
    char_cap: int,
    today: date,
) -> corpus.CaseDocument | None:
    """Fetch every opposition brief and combine them into one BIO document.

    A petition with several respondents draws a BIO from each; they are stored
    as the single ``brief-in-opposition`` document with a per-brief header, so
    a fan-out reads the whole opposition as one byte-identical input. Idempotent
    on the *set* of URLs (a canonical join, so single-BIO cases stay
    byte-compatible with the old single-URL key): the set is re-fetched only
    when a brief is added or superseded. The combined text is capped at
    ``char_cap`` total, earliest brief first (the lead respondent's, typically);
    a failed fetch of one brief never drops the others, and each failure —
    plus the case-level case where none of them fetched — is recorded
    (:func:`document_fetch_losses`).
    """
    if not bio_refs:
        return None
    # Idempotency key is the SELECTED set: skip only when we already hold exactly
    # these briefs. Because the stored key records the set we actually *fetched*
    # (below), a brief that failed to download last poll — the rolling-window
    # "missing document is expected" case — leaves the stored key short of the
    # selected set, so the next poll re-fetches and self-heals instead of being
    # skipped forever.
    if stored_url == "|".join(sorted(ref.url for ref in bio_refs)):
        return None
    single = len(bio_refs) == 1
    fetched_urls: list[str] = []
    blocks: list[str] = []
    pages = 0
    truncated = False
    ocr_derived = False
    for ref in bio_refs:
        try:
            data = client.get_document(ref.url)
        except httpx.HTTPError:
            _record_fetch_loss(FETCH_LOSS_HTTP_ERROR, case_id, ref.kind, ref.url)
            continue
        if data is None:
            _record_fetch_loss(FETCH_LOSS_UNAVAILABLE, case_id, ref.kind, ref.url)
            continue
        extracted = extract_pdf_text(data, char_cap=char_cap)
        fetched_urls.append(ref.url)
        if single:
            blocks.append(extracted.text)  # a lone BIO stays raw (no header)
        else:
            heading = ref.description or "Brief in opposition"
            if ref.entry_date:
                heading = f"{heading} ({ref.entry_date})"
            blocks.append(f"=== {heading} ===\n{extracted.text}")
        pages += extracted.pages
        truncated = truncated or extracted.truncated
        # Any OCR-derived brief marks the whole combined row: the reader holds one
        # document, so the weaker provenance is the one that has to survive.
        ocr_derived = ocr_derived or extracted.ocr_derived
    if not fetched_urls:
        # Every selected brief failed, so the case ends the pass with no
        # opposition row despite the docket listing one — recorded apart from
        # the per-brief failures because it is the outcome a reader cares about.
        _record_fetch_loss(
            FETCH_LOSS_BIO_EMPTY,
            case_id,
            KIND_BRIEF_IN_OPPOSITION,
            f"{len(bio_refs)} selected brief(s), none fetched",
        )
        return None
    text = "\n\n".join(blocks)
    if len(text) > char_cap:
        text = text[:char_cap]
        truncated = True
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_BRIEF_IN_OPPOSITION,
        # The canonical join of the briefs actually FETCHED — the idempotency
        # key (see above), not a single fetchable URL — the individual
        # DocumentRef.url values are what fetch here. One reader does GET a
        # stored `CaseDocument.url` back, the OCR recovery pass, and it is sound
        # only because its population is petitions, whose stored URL is the one
        # link that was fetched. Widening that population to this kind would
        # hand it a pipe-joined set key as a URL.
        url="|".join(sorted(fetched_urls)),
        entry_date=bio_refs[-1].entry_date,  # the latest filing's date
        fetched_at=today,
        pages=pages,
        truncated=truncated,
        ocr_derived=ocr_derived,
        text=text,
    )


def fetch_case_documents(
    client: SupremeCourtClient,
    case_id: str,
    payload: Mapping[str, Any],
    *,
    stored_urls: Mapping[str, str],
    char_cap: int,
    today: date,
) -> list[corpus.CaseDocument]:
    """Fetch and extract this case's predict-input documents; return the rows.

    Idempotent against ``stored_urls`` (the already-stored kind → url mapping):
    a document whose URL is unchanged is not re-fetched, so a relist that
    re-fires the distribution trigger costs nothing when the filings are
    unchanged, while a superseding filing (a re-filed BIO at a new URL, or a new
    respondent's BIO joining the set) is. The multiple opposition briefs of a
    multi-respondent case are combined into the one ``brief-in-opposition``
    document (:func:`_combine_bio_documents`). The questions presented are
    **derived** from the petition text — never the outcome-bearing ``QPLink`` —
    whenever the petition itself was (re)fetched; a petition whose QP heading
    yields nothing usable stores the empty-text row the extractor's degraded
    result names, never a fragment.

    **Never from an ``application``.** The derivation is keyed on
    :data:`KIND_PETITION` alone, and deliberately: the questions-presented
    section is a *petition* convention (Rule 14.1(a), and Rule 20.2 for the
    extraordinary writs the same kind covers), while an application for interim
    relief fronts no such heading. A QP row derived from one would either be
    empty — an empty-text row indistinguishable in the coverage report from a
    scanned petition — or a false positive cut from a heading the application
    happens to quote, and it would enter the labeling extract as a question this
    case presents. An application docket therefore stores its ``application``
    text and no derived questions.

    A missing or unextractable
    document degrades to a skip / an empty-text row; an upstream error skips
    just that document, never the poll. Every such skip is recorded
    (:func:`document_fetch_losses`) and warned into the run log, because the
    degradation is exactly what makes a later "this case holds no petition"
    count unattributable otherwise.
    """
    refs = select_documents(payload)
    if not refs:
        # Selection came back empty on a docket the caller asked about, which is
        # the one loss the three post-selection reasons cannot see. Recorded
        # once per case, before any fetch: there is no kind and no URL to
        # attribute it to, and the count is of cases left with nothing.
        _record_fetch_loss(
            FETCH_LOSS_NOT_SELECTED,
            case_id,
            _NOT_SELECTED_KIND,
            "no case-opening, application, or opposition entry carried a document link",
        )
        return []
    bio_refs = [ref for ref in refs if ref.kind == KIND_BRIEF_IN_OPPOSITION]
    documents: list[corpus.CaseDocument] = []
    petition: corpus.CaseDocument | None = None
    for ref in refs:
        if ref.kind == KIND_BRIEF_IN_OPPOSITION:
            continue  # combined as a group below
        if stored_urls.get(ref.kind) == ref.url:
            continue
        try:
            data = client.get_document(ref.url)
        except httpx.HTTPError:
            _record_fetch_loss(FETCH_LOSS_HTTP_ERROR, case_id, ref.kind, ref.url)
            continue
        if data is None:
            _record_fetch_loss(FETCH_LOSS_UNAVAILABLE, case_id, ref.kind, ref.url)
            continue
        extracted = extract_pdf_text(data, char_cap=char_cap)
        document = corpus.CaseDocument(
            case_id=case_id,
            kind=ref.kind,
            url=ref.url,
            entry_date=ref.entry_date,
            fetched_at=today,
            pages=extracted.pages,
            truncated=extracted.truncated,
            ocr_derived=extracted.ocr_derived,
            text=extracted.text,
        )
        documents.append(document)
        if ref.kind == KIND_PETITION:
            petition = document
    bio = _combine_bio_documents(
        client,
        case_id,
        bio_refs,
        stored_url=stored_urls.get(KIND_BRIEF_IN_OPPOSITION),
        char_cap=char_cap,
        today=today,
    )
    if bio is not None:
        documents.append(bio)
    if petition is not None and petition.text:
        questions = extract_questions_presented(petition.text)
        if questions is not None:
            documents.append(_derived_questions_document(petition, questions, fetched_at=today))
    return documents


def _derived_questions_document(
    petition: corpus.CaseDocument, questions: str, *, fetched_at: date
) -> corpus.CaseDocument:
    """The ``questions-presented`` row derived from one stored petition.

    Its identity is the petition's — same case, same source URL, same docket
    entry — because that is what the text was read out of; ``pages`` is 0 and
    ``truncated`` false because nothing was paged or capped here.
    ``ocr_derived`` is the petition's rather than false for the same reason the
    identity is: text cut out of an OCR reading is an OCR reading, and the
    questions presented are exactly where a misread character costs most.
    """
    return corpus.CaseDocument(
        case_id=petition.case_id,
        kind=KIND_QUESTIONS_PRESENTED,
        url=petition.url,
        entry_date=petition.entry_date,
        fetched_at=fetched_at,
        pages=0,
        truncated=False,
        ocr_derived=petition.ocr_derived,
        text=questions,
    )


class QPBackfillResult(BaseModel):
    """What one questions-presented backfill pass found, and wrote."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the rows or only counted them")
    petitions: int = Field(
        ge=0, description="Cases carrying stored petition text the pass re-derived from"
    )
    no_petition_text: int = Field(
        ge=0,
        default=0,
        description="Live-slice cases whose petition row is absent or reads back "
        "empty — the population the pass could not judge; a climb is a content-store "
        "read degradation, not a converged corpus",
    )
    unchanged: int = Field(
        ge=0,
        description="Cases whose stored questions-presented text is already what "
        "the current extractor derives (a case owed nothing counts here too)",
    )
    updated: int = Field(ge=0, description="Rows rewritten (apply) or that would be (dry-run)")
    reasons: dict[str, int] = Field(
        default_factory=dict, description="Change distribution, reason class -> case count"
    )
    changes: dict[str, str] = Field(
        default_factory=dict,
        description="case_id -> reason class, untruncated: the record of which "
        "stored rows an applied pass rewrites",
    )
    refused: list[str] = Field(
        default_factory=list,
        description="Cases whose stored text is a full-length question the current "
        "extractor can no longer derive: reported for triage, never written, since "
        "emptying a substantive row is a rewrite this pass makes on its own "
        "reading only where the stored value is contents junk throughout — that "
        "heal carries its own reason class (`toc-junk-emptied`) so a dry run "
        "shows the emptied subset apart",
    )


def _qp_change_reason(stored: str, derived: str) -> str:
    """Why a stored questions-presented text is not what the extractor now derives.

    Named for the extraction hole each class comes from, most specific first: a
    table-of-contents capture (either alignment); a body cut short at a prose
    phrase the end-heading vocabulary also spells, which leaves the stored value
    a prefix of the full section; a front-matter crumb under the length floor;
    and anything else, which is a change worth a maintainer's eye before it is
    applied.
    """
    if _QP_TOC_RE.search(stored) or _QP_TOC_LINE_RE.search(stored):
        return "stale-toc-fragment"
    if stored and derived.startswith(stored):
        return "prose-terminator-fragment"
    if len(stored) < _QP_MIN_CHARS:
        return "below-floor"
    return "other-change"


def _qp_stored_is_fragment(stored: str) -> bool:
    """Whether a stored questions-presented value is contents junk throughout.

    True only when TOC-shaped stripping removed something *and* what remains
    is not question-sized. The refusal guard consults this rather than the
    per-line change classifier, because the two questions differ: a value
    that merely *contains* a contents line — a genuine question the old
    extractor captured with trailing TOC residue — classifies as a stale
    fragment line-wise, but blanking it would destroy the question; a value
    that is leader dots and folios all the way down is junk however far it
    clears the character floor, since the floor counts the dots.

    One predicate, applied per line, decides both halves — there is no
    separate whole-value check to disagree with the strip. A dot-leader run
    strips the *run*, not its line, keeping the line where its residue is
    itself question-sized: a single-line question quoting a statute through a
    long elision is prose around dots, not a leader. The two folio forms
    strip whole lines, whose residue is heading words that would only push
    real junk back over the floor — with the known bound that a justified
    genuine line ending in a bare page-number token is stripped with them,
    which bites only on a value already scraping the floor.
    """
    lines = stored.splitlines()
    kept: list[str] = []
    for line in lines:
        if _QP_TOC_RE.search(line):
            residue = _QP_TOC_RE.sub(" ", line).strip()
            if len(residue) >= _QP_MIN_CHARS:
                kept.append(residue)
            continue
        if _QP_TOC_LINE_RE.search(line) or _QP_TOC_SPACES_RE.match(line):
            continue
        kept.append(line)
    return len(kept) != len(lines) and len(" ".join(kept).strip()) < _QP_MIN_CHARS


def backfill_questions_presented(conn: sqlite3.Connection, *, apply: bool) -> QPBackfillResult:
    """Re-derive each case's questions presented from its **stored** petition text.

    The questions-presented row is derived, not fetched, so it carries whatever
    the extractor said on the day the petition was ingested — and the ingest
    path never re-derives it, because an unchanged petition URL is not
    re-fetched. This is the pass that closes that gap: over every SCOTUS case
    holding petition text (SQLite, or the per-case content store under the
    corpus-split mode), run the current :func:`extract_questions_presented` and
    rewrite the row only where its output differs from what is stored — a
    convergence sweep, not a re-extraction of PDFs, so it touches no network and
    re-reads no filing. Each rewrite is classified (:func:`_qp_change_reason`)
    so the dry run reads as triage rather than a count. Idempotent: a second
    pass over the same corpus reports everything unchanged. Where a case has
    petition text but no stored row and the extractor now derives one, the row
    is created; where it derives nothing, no empty row is invented for a case
    that never had one. One rewrite is withheld on principle: a stored text at
    or above :data:`_QP_MIN_CHARS` — a full-length question — is never replaced
    by the empty extraction, because that reading is as likely to be this pass
    misjudging a question as it is a bad row; those cases are listed
    (``refused``) for a maintainer to decide. The refusal does not extend to a
    stored value that is contents junk throughout
    (:func:`_qp_stored_is_fragment`): a run of leader dots clears the
    character floor by counting the dots, and protecting it would freeze
    exactly the junk this pass exists to heal — so it heals to the honest
    empty row however long it is, while a genuine question that merely
    carries trailing contents residue keeps the refusal. Dry-run unless
    ``apply``.

    The population is the live/historical slice (:func:`corpus.is_live_slice`):
    documents reach the corpus only on that channel, and the row predicate is
    what keeps the walk from a per-case content-store read for every SCOTUS row
    the bulk import ever wrote. Where payload reads are offloaded to the
    content store their latency is the pass's whole cost — a serial walk of
    the ~1,500-case population is what turned the first dispatched pass into a
    job-cap cancellation — so the document fetch goes through
    :func:`~fedcourtsai.pipeline.prefetch.prefetch_by_case`, which pools the
    reads there and keeps the SQLite fallback serial on its single-thread
    connection. Everything after a fetch — extraction, comparison,
    classification, the writes — is the same serial, ordered code either way,
    so pooled and serial fetching produce identical results. A fetch that
    raises aborts the whole pass, deliberately against the
    degrade-don't-crash default: this is a dispatch-gated convergence sweep
    whose apply verifies itself by re-running, and a silently partial ledger
    would read as a converged one.
    """
    petitions = unchanged = no_petition_text = 0
    reasons: Counter[str] = Counter()
    changes: dict[str, str] = {}
    refused: list[str] = []
    updates: list[corpus.CaseDocument] = []
    case_ids = [row.case_id for row in corpus.iter_rows(conn, court="scotus", live_slice=True)]

    def consider(case_id: str, documents: list[corpus.CaseDocument]) -> None:
        nonlocal petitions, unchanged, no_petition_text
        by_kind = {doc.kind: doc for doc in documents}
        petition = by_kind.get(KIND_PETITION)
        if petition is None or not petition.text.strip():
            no_petition_text += 1
            return
        petitions += 1
        stored = by_kind.get(KIND_QUESTIONS_PRESENTED)
        # `None` (no heading anywhere) and "" (a heading with nothing usable
        # under it) both mean "no questions to store" for an existing row.
        derived = extract_questions_presented(petition.text) or ""
        current = stored.text if stored is not None else ""
        if derived == current:
            unchanged += 1
            return
        if (
            not derived
            and len(current) >= _QP_MIN_CHARS
            # A stored TOC fragment over the floor is dots, not a question —
            # but only when it is fragment through and through: a genuine
            # question with a trailing contents line must keep the refusal.
            and not _qp_stored_is_fragment(current)
        ):
            refused.append(case_id)
            return
        if stored is None:
            # The row's provenance is the petition's, including its fetch date:
            # nothing was fetched here, so claiming today's date would date the
            # text to a fetch that did not happen.
            updates.append(
                _derived_questions_document(petition, derived, fetched_at=petition.fetched_at)
            )
            reason = "derived-anew"
        else:
            # `ocr_derived` travels with the text, not with the row: re-deriving
            # from a petition whose text a recovery pass read off page images
            # makes this an OCR reading too, and a stale marker would present it
            # as an extraction.
            updates.append(
                stored.model_copy(update={"text": derived, "ocr_derived": petition.ocr_derived})
            )
            if not derived and len(current) >= _QP_MIN_CHARS:
                # Reaching here empty-over-floor means the fragment test
                # lifted the refusal — the one heal that *empties* a
                # full-length value, so the ledger names it apart: the
                # emptied subset is the part of a dry run a maintainer
                # eyeballs before dispatching the apply.
                reason = "toc-junk-emptied"
            else:
                reason = _qp_change_reason(current, derived)
        reasons[reason] += 1
        changes[case_id] = reason

    # `documents_for_case` never touches `conn` where payload reads are
    # offloaded (the registered source serves it, and its Protocol requires
    # tolerance of concurrent reads), which is what makes handing the call to
    # the prefetch pool's worker threads sound; the mode cannot flip mid-pass
    # because nothing here re-registers the source.
    with prefetch_by_case(
        case_ids,
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="qp-backfill",
    ) as fetched:
        for case_id, documents in fetched:
            consider(case_id, documents)
    if apply and updates:
        corpus.upsert_documents(conn, updates)
    return QPBackfillResult(
        applied=apply,
        petitions=petitions,
        no_petition_text=no_petition_text,
        unchanged=unchanged,
        updated=len(updates),
        reasons=dict(sorted(reasons.items())),
        changes=dict(sorted(changes.items())),
        refused=sorted(refused),
    )


# The kinds a text-coverage measurement counts, fetched before derived — every
# text a cell reads directly. The order matters to how the report reads, because
# an empty row does not mean the same thing across it. The three fetched PDFs are
# the scanned-filing reading: nothing extracted means no text layer — with one
# asymmetry the table itself cannot show, since `ocr-recover-petitions`' own
# population is stored *petitions*, so an empty `application` is measured with no
# repair path behind it. The derived
# questions-presented row has a second cause — :func:`extract_questions_presented`
# returns the empty string where the heading is present but no capture under it
# is vouchable — so its column mixes scans with extraction refusals over
# petitions that do carry text, and an OCR decision reads the fetched rows.
#
# ``application`` is counted for the same reason the other fetched kinds are: it
# is text a cell reads directly, an application filed on paper stores empty
# exactly as a paper petition does, and leaving it out would make an
# application docket that holds only its application read as a case the pass
# never reached (``cases_read`` counts *these* kinds, not any document).
TEXT_COVERAGE_KINDS: tuple[str, ...] = (
    KIND_PETITION,
    KIND_APPLICATION,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_QUESTIONS_PRESENTED,
)

# The two halves the coverage counts are cut into, in report order.
SCORED_SEGMENT = "scored"
REST_SEGMENT = "rest"


class TextCoverageCut(BaseModel):
    """One document kind's stored/empty counts within one segment."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="The document kind counted, e.g. petition")
    segment: str = Field(
        description="`scored` (the salience gate's paid modern-cert segment) or "
        "`rest` (the remainder of the live slice)"
    )
    documents: int = Field(ge=0, description="Stored documents of this kind in this segment")
    empty: int = Field(
        ge=0,
        description="Of those, the ones whose stored text is empty or whitespace-only "
        "— the condition provisioning stamps on the cell manifest as `empty_text`",
    )

    @property
    def share(self) -> float | None:
        """``empty`` as a share of ``documents``, or ``None`` over an empty cut.

        ``None`` rather than zero, so a segment nothing was read for never
        reports as a segment measured at 0%.
        """
        return self.empty / self.documents if self.documents else None


class TextCoverage(BaseModel):
    """What one text-coverage pass read, and how much of it carried no text."""

    model_config = ConfigDict(extra="forbid")

    cases: int = Field(ge=0, description="Live-slice SCOTUS rows the pass walked")
    cases_read: int = Field(
        ge=0,
        description="Of those, the ones that served at least one counted document "
        "— the pass's own reach, so a run that could read almost nothing says so "
        "rather than reporting a share over the few cases it got",
    )
    distributed: int = Field(
        ge=0,
        description="Live-slice rows that reached a distribution transition — the "
        "moment `provision_documents` fetches. A stock, not a fetch population: a "
        "row distributed before the document channel existed, or written by the "
        "historical Term walker, was never fetched for at all",
    )
    distributed_without_petition: int = Field(
        ge=0,
        description="Of those, the ones holding no petition row at all. The other "
        "failure mode, and the one an extraction fix does not reach: there is "
        "nothing stored to re-extract. Petition-keyed and unfiltered, matching "
        "the stock it is taken over, so an application-form row counts here "
        "however complete it is — the queued counts are the form-keyed ones",
    )
    queued: int = Field(
        ge=0,
        description="Live-slice rows the pipeline queued for prediction — the "
        "decision-relevant denominator, since a missing primary document costs a "
        "cell only where a cell is minted",
    )
    queued_cert_forms: int = Field(
        ge=0,
        description="Of the queued rows, the cert-form dockets — the denominator "
        "`queued_without_petition` is a gap over, since a gap that drains is "
        "unreadable without the population it drains from",
    )
    queued_application_forms: int = Field(
        ge=0,
        description="Of the queued rows, the interim application dockets — the "
        "denominator `queued_without_application` is a gap over. The two form "
        "counts partition `queued`",
    )
    queued_without_petition: int = Field(
        ge=0,
        description="Of the queued **cert-form** rows, the ones holding no "
        "petition row: what a text-extraction fix cannot recover on the "
        "population that is predicted. Application-form dockets are measured "
        "against their own primary document instead "
        "(`queued_without_application`), since a petition is not the filing that "
        "opens one; `queued_without_petition_cases` names every case in it",
    )
    queued_without_application: int = Field(
        ge=0,
        description="Of the queued **application-form** rows, the ones holding no "
        "`application` document. Their own primary kind, not the petition they "
        "structurally never have: an application docket is complete when it holds "
        "its application, so this is a provisioning gap that drains as the "
        "documents store, not a floor. Counted apart from "
        "`queued_without_petition` rather than pooled into it, because the two "
        "populations are keyed on different documents; "
        "`queued_without_application_cases` names every case in it",
    )
    queued_without_petition_floor: int = Field(
        default=0,
        ge=0,
        description="Of the `queued_without_petition` cases, the ones whose newest "
        "stored docket payload nominates no case-opening document at all — the "
        "**structural floor**: a paper filing the Court posted no PDF behind, or a "
        "legacy docket whose proceedings list carries no document links. Without "
        "it a successful back-fill still reports its residue as an unexplained "
        "provisioning gap forever. Read off the *stored* payload, so it is the "
        "floor as the corpus holds it: a case counted here can still recover if "
        "upstream has since posted the link, which is what the fresh-fetch "
        "back-fill pass finds out",
    )
    queued_without_application_floor: int = Field(
        default=0,
        ge=0,
        description="The same reading on the application-form gap: candidates whose "
        "stored payload nominates no application document. Expected to be zero — "
        "an application docket posts its filing — so a non-zero value is a reading "
        "to chase rather than a floor to accept",
    )
    unopened_petitions: int = Field(
        ge=0,
        description="Of the empty petitions, the ones stored with zero pages — "
        "`extract_pdf_text`'s could-not-open branch rather than a page count with "
        "no text layer, so OCR is not the repair for them",
    )
    offloaded: bool = Field(
        description="Whether the payload reads were served by the per-case content "
        "store (the corpus-split shape) rather than by the blob's own tables"
    )
    cuts: list[TextCoverageCut] = Field(
        default_factory=list,
        description="Every kind x segment cell, zero-filled and in report order, "
        "so an unlisted cell is never an omitted one",
    )
    empty_documents: dict[str, list[str]] = Field(
        default_factory=dict,
        description="case_id -> the kinds that read back empty, in case_id order: "
        "the triage list an extraction fix would work from",
    )
    queued_without_petition_cases: list[str] = Field(
        default_factory=list,
        description="The `queued_without_petition` cases themselves, in case_id "
        "order: the triage list a provisioning fix works from, since the route a "
        "missing petition took is a per-case question and a count names no case",
    )
    queued_without_application_cases: list[str] = Field(
        default_factory=list,
        description="The `queued_without_application` cases themselves, in case_id "
        "order, enumerated for the reason the cert-form ledger beside it is: the "
        "gap is repaired case by case and a count names no case",
    )

    def kind_totals(self, kind: str) -> tuple[int, int]:
        """``(documents, empty)`` for one kind, pooled over both segments.

        Pooled across segments but never across kinds: the counted kinds do not
        share a cause of emptiness (:data:`TEXT_COVERAGE_KINDS`), so a total
        over all of them would be a number of nothing in particular.
        """
        cells = [cut for cut in self.cuts if cut.kind == kind]
        return sum(c.documents for c in cells), sum(c.empty for c in cells)


def _stored_payload_selects_none(conn: corpus.ReadConnection, case_id: str, *, kind: str) -> bool:
    """Whether this case's stored docket payload nominates no ``kind`` at all.

    The floor test behind ``queued_without_*_floor``: a gap the selector can see
    a link for is a provisioning gap that a re-run drains, while one whose own
    docket payload nominates nothing is a filing the Court posted no PDF for or a
    docket carrying no links at all — and no repair reaches either. False where
    no live-shaped snapshot is stored, which is not a floor but an unread case:
    the corpus cannot say, so the annotation does not claim.
    """
    snapshot = corpus.latest_live_snapshot(conn, case_id)
    if snapshot is None:
        return False
    _, payload = snapshot
    return not any(ref.kind == kind for ref in select_documents(payload))


def document_text_coverage(conn: corpus.ReadConnection) -> TextCoverage:
    """Count the stored documents whose text is empty, by kind and segment.

    The measurement behind an extraction decision: a filing that reaches the
    corpus as a scan with no text layer stores an empty string
    (:func:`extract_pdf_text` returns ``""``), and provisioning derives the
    cell manifest's ``empty_text`` from exactly that — ``not text.strip()`` —
    then writes it into the cell's manifest and never into a corpus column. So
    the share is not a column to query; it has to be counted off the stored
    text, which is what this does, under the same predicate the manifest
    stamps. Read per kind, not pooled: the counted kinds do not share one
    cause of emptiness (:data:`TEXT_COVERAGE_KINDS`).

    The population is the live/historical slice
    (:func:`corpus.is_live_slice`), for the reason
    :func:`backfill_questions_presented` walks it: documents reach the corpus
    on that channel only, so a bulk-import row has none by construction and
    walking it would buy a per-case content-store read for nothing. That frame
    is a walk, not a denominator anything is a rate over: most of it was never
    fetched for at all (a historical-Term row, or a petition outside the
    upstream link window), so ``cases_read`` is a reach count.

    Within the slice the counts split on the salience gate's scored segment
    (:func:`~fedcourtsai.pipeline.caption._scored_segment` — paid modern-cert).
    That is the segment the gate *scores*, not the set it selects, and in
    practice the split is paid against in forma pauperis: the cut is here
    because a paper filing is what arrives as a scan, and the fee class is the
    corpus's closest arrival-time reading of that.

    Two failure modes, reported apart because only one is an extraction
    problem. A stored document whose text is empty can be re-extracted; the
    cases with **no petition row at all** cannot, and they are counted over two
    denominators. ``distributed`` is the stock of rows that reached a
    distribution transition — the moment
    :func:`~fedcourtsai.pipeline.live.provision_documents` fetches — but it
    includes rows written before the document channel existed, which were never
    fetched for, so it is a stock rather than a failure rate. ``queued`` is the
    rows the pipeline queued for prediction, which is the population a missing
    petition actually costs a cell on. Reading the empty share without these
    beside it is how a decision gets made about the smaller of the two modes.

    On the queued count — the one a repair is planned against — the gap is
    **keyed on the docket form's own primary document**, on
    :func:`corpus.is_scotus_application_form`: a cert-form row is measured
    against its ``petition`` (``queued_without_petition``), an application-form
    row against its ``application`` (``queued_without_application``). Two
    populations rather than one, because the two forms are opened by different
    filings and pooling them would report a docket as missing a document the
    Court never expected it to hold. Neither is a floor: an application docket
    that holds its application is as complete as a cert docket that holds its
    petition, and the count drains as the documents store — which is why each
    carries its own denominator (``queued_cert_forms``,
    ``queued_application_forms``, partitioning ``queued``), since a gap that
    drains is unreadable against a population it is not a gap over. The wide
    ``distributed`` stock stays petition-keyed and unfiltered, matching what it
    is. And because the route a real gap took is a per-case question — a case
    whose documents were never provisioned reads exactly like one whose fetch
    was attempted and served nothing — both classes are enumerated
    (``queued_without_petition_cases``, ``queued_without_application_cases``)
    and not only counted.

    Each gap also carries its **floor**: of the cases in it, how many hold a
    stored docket payload that nominates no such document at all
    (:func:`_stored_payload_selects_none`). A gap the selector can see a link for
    is a provisioning gap and drains; one whose own docket posts no PDF — a Rule
    34.6 paper filing — or carries no document links at all does not, and reading
    the two as one number reports a converged corpus as a permanent defect. Read
    off the stored payload rather than a fresh fetch, so it is the floor as the
    corpus holds it and the fetching repair is what settles a case upstream has
    since posted a link for; and read only over the gap lists, so it costs one
    extra content-store read per gap case rather than per row of the frame.

    Split-aware by construction: every read goes through
    :func:`corpus.documents_for_case`, which the registered payload source
    serves from the per-case content store under the corpus-split mode and the
    blob's own tables otherwise. ``offloaded`` records which served this pass,
    since a blob-only read of a split corpus finds no documents at all and must
    not read as a corpus with none. One degradation the counts cannot
    self-limit on: served from the store, a document whose text leaf is missing
    reads back as ``text=""`` (:func:`~fedcourtsai.casestore.read_documents`),
    which is indistinguishable here from a scanned filing — the manifest
    served, so the case counts as reached. A partially mirrored store therefore
    inflates the very number this produces, and only the store's own
    completeness rules that out.

    The document fetch rides :func:`~fedcourtsai.pipeline.prefetch.prefetch_by_case`
    for the reason the questions-presented backfill does: offloaded, the read
    is a network GET per case and a serial walk of the population is the whole
    cost of the pass. Everything after the fetch is serial and in population
    order either way, so the two schedules count identically.
    """
    tallies = {
        (kind, segment): [0, 0]
        for segment in (SCORED_SEGMENT, REST_SEGMENT)
        for kind in TEXT_COVERAGE_KINDS
    }
    empty_documents: dict[str, list[str]] = {}
    queued_without_petition_cases: list[str] = []
    queued_without_application_cases: list[str] = []
    cases_read = unopened_petitions = 0
    distributed_without_petition = queued_without_petition = queued_without_application = 0
    # Materialized before the fetch: `iter_rows` rides `conn`, which under the
    # offloaded schedule must not be walked while readers are in flight.
    rows = [row for row in corpus.iter_rows(conn, court="scotus") if corpus.is_live_slice(row)]
    segments = {
        row.case_id: SCORED_SEGMENT if _scored_segment(row) else REST_SEGMENT for row in rows
    }
    # `distribution_count` is None on a row whose proceedings were never parsed,
    # so a parsed non-zero count is the widest reading of "this case reached the
    # moment a document would be fetched". Wider than the set actually fetched
    # for: the whole pre-channel back catalogue distributed too, and nothing was
    # ever attempted for it. A stock, which is why `queued` is printed beside it.
    distributed = {row.case_id for row in rows if (row.distribution_count or 0) > 0}
    # The narrow denominator beside it: a missing petition costs a prediction
    # only where one was minted.
    queued = {row.case_id for row in rows if row.predict_queued_at is not None}
    # The rows whose primary document is an `application` rather than a
    # `petition`. The frame is already SCOTUS-only, which is the gate the
    # predicate's callers owe.
    application_forms = {
        row.case_id for row in rows if corpus.is_scotus_application_form(row.docket_number)
    }
    case_ids = list(segments)
    with prefetch_by_case(
        case_ids,
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="text-coverage",
    ) as fetched:
        for case_id, documents in fetched:
            segment = segments[case_id]
            counted = 0
            has_petition = has_application = False
            for document in documents:
                tally = tallies.get((document.kind, segment))
                if tally is None:  # a kind this measurement does not count
                    continue
                counted += 1
                has_petition = has_petition or document.kind == KIND_PETITION
                has_application = has_application or document.kind == KIND_APPLICATION
                tally[0] += 1
                if not document.text.strip():
                    tally[1] += 1
                    empty_documents.setdefault(case_id, []).append(document.kind)
                    # Zero pages is `extract_pdf_text`'s could-not-open branch,
                    # not a page count with no text layer: a different repair.
                    if document.kind == KIND_PETITION and not document.pages:
                        unopened_petitions += 1
            # Counted kinds, not any document: the reach number must stay the
            # population the cuts are computed over as new kinds are stored.
            if counted:
                cases_read += 1
            # The wide stock stays petition-keyed and unfiltered, which is what
            # its field description says it is.
            if not has_petition and case_id in distributed:
                distributed_without_petition += 1
            # The queued gap is form-keyed: each docket form is measured against
            # the document that opens it, so neither count reports a docket as
            # missing a filing the Court never expected it to hold.
            if case_id in queued:
                if case_id in application_forms:
                    if not has_application:
                        queued_without_application += 1
                        queued_without_application_cases.append(case_id)
                elif not has_petition:
                    queued_without_petition += 1
                    queued_without_petition_cases.append(case_id)
    # The floor annotation, read after the walk and only over the gap cases —
    # a second content-store read each, over a list in the tens rather than the
    # thousands, so it is bought at the size of the gap and not of the frame.
    # Serial for the same reason: the pool exists for a per-case read of the
    # whole population, and this is not one.
    petition_floor = sum(
        _stored_payload_selects_none(conn, case_id, kind=KIND_PETITION)
        for case_id in queued_without_petition_cases
    )
    application_floor = sum(
        _stored_payload_selects_none(conn, case_id, kind=KIND_APPLICATION)
        for case_id in queued_without_application_cases
    )
    return TextCoverage(
        cases=len(case_ids),
        cases_read=cases_read,
        distributed=len(distributed),
        distributed_without_petition=distributed_without_petition,
        queued=len(queued),
        # The two form denominators partition `queued`, so each gap prints
        # against the population it drains from rather than against every
        # queued row of either form.
        queued_cert_forms=len(queued - application_forms),
        queued_application_forms=len(queued & application_forms),
        queued_without_petition=queued_without_petition,
        queued_without_application=queued_without_application,
        queued_without_petition_floor=petition_floor,
        queued_without_application_floor=application_floor,
        unopened_petitions=unopened_petitions,
        offloaded=corpus.payload_reads_offloaded(),
        # Zero-filled and ordered by construction (kind within segment), so the
        # report is the same shape whatever the corpus held.
        cuts=[
            TextCoverageCut(kind=kind, segment=segment, documents=stored, empty=blank)
            for (kind, segment), (stored, blank) in tallies.items()
        ],
        # `iter_rows` yields in case_id order, the prefetch preserves input
        # order, and `documents_for_case` orders by kind — so the ledgers are
        # deterministic on either schedule, without a re-sort.
        empty_documents=empty_documents,
        queued_without_petition_cases=queued_without_petition_cases,
        queued_without_application_cases=queued_without_application_cases,
    )


@dataclass(frozen=True)
class QpExtractRow:
    """One extract row: the whole input a ``qp-topic-v0`` labeler is entitled to.

    Text-only by design (``docs/qp-topic.md``) — no docket context, no case
    name, no outcome — so a label can never encode a decision the text
    predates. ``case_id`` and ``docket_number`` are the key *pair* the reference
    join is checked on, not context: a half-matching pair is a mis-join.
    """

    case_id: str
    docket_number: str
    text: str


@dataclass(frozen=True)
class QpExtract:
    """The rows one labeling run reads, plus what the pass declined to hand it."""

    rows: list[QpExtractRow]
    skipped: int


def _in_label_scope(row: corpus.CorpusRow) -> bool:
    """Whether a row belongs to the labeling extract's population.

    Exactly the frame the docket pack's question-presented topic section is
    computed over — SCOTUS, :func:`corpus.is_live_slice`,
    :func:`corpus.is_modern_cert` — so every labeled row has a published home
    and nothing in the section's frame is unlabelable. The live-slice clause is
    also what keeps the walk off hundreds of thousands of bulk-import rows, and
    it costs no coverage: documents reach the corpus only on that channel.

    Narrowing further is not free, and the predict-scope rules
    (:data:`corpus.OUT_OF_SCOPE_RULES`) are the tempting narrowing to reject.
    On a QP-bearing population the only one that bites is the in-forma-pauperis
    exclusion, while the hand reference set spans both fee streams — so an
    extract that dropped IFP rows would have to carry the reference set's own
    back in to keep the publication gate's coverage floor reachable, and an IFP
    row inside such an extract would then be a certain reference-set member.
    Fee class rides in the docket number every row carries, so that is a
    membership probe handed to the labeler, on a set whose membership predicts
    cert grants. The frame stays wide because the alternative leaks the
    measurement.
    """
    return corpus.is_live_slice(row) and corpus.is_modern_cert(row)


def questions_presented_extract(conn: corpus.ReadConnection, *, scoped: bool = True) -> QpExtract:
    """The stored ``questions-presented`` texts a labeling run reads.

    Two selections, and they read the corpus differently on purpose.

    ``scoped`` (the default, and the only form a dispatch uses) walks the
    labeling population — :func:`_in_label_scope` — and reads each case's
    documents through :func:`corpus.documents_for_case`, so the pass serves from
    the per-case content store wherever payload reads are offloaded and from the
    blob otherwise. That is the only shape that works under the corpus split at
    all: the split writer leaves the blob's ``documents`` table empty and the
    store is the system of record for it, so a bulk read of that table sees a
    payload-free index and reports nothing. Population-scale per-case reads go
    through :func:`~fedcourtsai.pipeline.prefetch.prefetch_by_case`, which pools
    them against the store and stays serial on the single-thread connection.

    ``scoped=False`` is the unscoped measurement form: one bulk join over the
    blob's own ``documents`` table, every stored questions-presented row
    whatever its case. It answers "what is in this blob" — a question about a
    file, not about a population — so against a split blob it returns nothing,
    correctly: the texts are not in the file. (Its CLI caller treats an empty
    result as a mis-wired run and exits non-zero, since an empty extract is
    never a labeling task.)

    A row whose case carries no docket number, or whose stored text is empty, is
    skipped and counted rather than guessed at: the docket number is half the
    key the reference join is checked on, and an empty extraction (what the
    extractor stores for a capture it cannot vouch for) is nothing to label.
    Rows come back in ``case_id`` order under either selection.
    """
    rows: list[QpExtractRow] = []
    skipped = 0

    def consider(case_id: str, docket_number: object, text: object) -> None:
        nonlocal skipped
        number = str(docket_number or "").strip()
        body = str(text or "")
        if not number or not body.strip():
            skipped += 1
            return
        rows.append(QpExtractRow(case_id, number, body))

    if scoped:
        scope = {
            row.case_id: row.docket_number
            for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
            if _in_label_scope(row)
        }
        # `documents_for_case` never touches `conn` where payload reads are
        # offloaded (the registered source serves it, and its Protocol requires
        # tolerance of concurrent reads), which is what makes handing the call
        # to the prefetch pool's worker threads sound.
        with prefetch_by_case(
            sorted(scope),
            lambda case_id: corpus.documents_for_case(conn, case_id),
            thread_name_prefix="qp-extract",
        ) as fetched:
            for case_id, documents in fetched:
                stored = next(
                    (doc for doc in documents if doc.kind == KIND_QUESTIONS_PRESENTED), None
                )
                if stored is None:
                    # Not a skip: a case with no stored questions is outside the
                    # QP-bearing population, not a row the pass declined.
                    continue
                consider(case_id, scope[case_id], stored.text)
        return QpExtract(rows, skipped)

    cursor = conn.execute(
        "SELECT d.case_id, c.docket_number, d.text FROM documents AS d "
        "LEFT JOIN cases AS c ON c.case_id = d.case_id "
        "WHERE d.kind = ? ORDER BY d.case_id",
        (KIND_QUESTIONS_PRESENTED,),
    )
    for record in cursor:
        consider(str(record[0]), record[1], record[2])
    return QpExtract(rows, skipped)
