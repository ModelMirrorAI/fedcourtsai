"""Petition-document selection and text extraction for predict inputs.

The input-richness half of the live-sources design: the docket JSON links every
filed PDF, and the questions presented plus the petition/BIO are the signals
cert prediction actually turns on. Everything here is **pipeline-side** —
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
and the QP derivation are pure and tested offline. Because the derivation is
pure, it can also be re-run over text already stored —
:func:`backfill_questions_presented`, the convergence sweep that carries an
extractor fix onto the rows an unchanged petition URL would otherwise freeze.
"""

from __future__ import annotations

import io
import re
import sqlite3
from collections import Counter
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .. import corpus
from ..supremecourt import SupremeCourtClient

# Document kinds, in provisioning order. `questions_presented` is derived from
# the petition text rather than fetched (see the module docstring).
KIND_PETITION = "petition"
KIND_BRIEF_IN_OPPOSITION = "brief-in-opposition"
KIND_QUESTIONS_PRESENTED = "questions-presented"

# The proceedings entry whose link carries the petition PDF. The BIO entry is
# matched by :func:`_is_bio_entry` below (its phrasing varies more).
_PETITION_ENTRY_RE = re.compile(
    r"petition for a writ of certiorari(?: and motion\b[^.]*)? filed", re.IGNORECASE
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
# Concurrent content-store readers for the backfill's document fetch. The pass
# is one GET per live-slice case — ~1,500 today — and serial GET latency is
# what cancelled the first dispatched pass against the seed job's cap; sixteen
# bounded workers hold the scan to minutes without meaningfully loading the
# store. Read only where payload reads are offloaded — the registered source's
# Protocol requires concurrent-read safety, and one warm-up read constructs
# its lazy client before the pool exists — while the SQLite path stays serial
# on its single-thread connection.
_QP_BACKFILL_READERS = 16
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
    """The text pypdf recovered from one PDF."""

    text: str
    pages: int
    truncated: bool


def _entry_link(entry: Mapping[str, Any], *, prefer: str | None) -> tuple[str, str] | None:
    """(url, description) of the preferred link on a proceedings entry, or first."""
    links = [link for link in entry.get("Links") or [] if isinstance(link, Mapping)]
    if prefer is not None:
        for link in links:
            if str(link.get("Description", "")).strip().lower() == prefer:
                url = str(link.get("DocumentUrl") or "").strip()
                if url:
                    return url, str(link.get("Description", ""))
    for link in links:
        url = str(link.get("DocumentUrl") or "").strip()
        if url:
            return url, str(link.get("Description", ""))
    return None


def select_documents(payload: Mapping[str, Any]) -> list[DocumentRef]:
    """The fetchable predict-input documents on one docket JSON (pure).

    The petition (its own link on the filing entry) and **every** non-amicus
    brief in opposition — a petition with multiple respondents draws a BIO from
    each, and taking only the last silently dropped the lead respondent's (the
    most predictive one) whenever a secondary respondent filed later. All
    distinct-URL BIOs are returned, in docket order; :func:`fetch_case_documents`
    combines them into the single ``brief-in-opposition`` document. ``QPLink``
    is deliberately never selected: it is generated at grant time and leaks the
    outcome; the questions presented are derived from the petition text instead
    (:func:`extract_questions_presented`).
    """
    petition: DocumentRef | None = None
    bios: list[DocumentRef] = []
    seen_bio_urls: set[str] = set()
    for entry in payload.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        text = str(entry.get("Text") or "")
        entry_date = str(entry.get("Date") or "") or None
        if petition is None and _PETITION_ENTRY_RE.search(text):
            found = _entry_link(entry, prefer="petition")
            if found is not None:
                petition = DocumentRef(KIND_PETITION, found[0], entry_date, found[1])
        elif _is_bio_entry(text):
            found = _entry_link(entry, prefer="main document")
            if found is not None and found[0] not in seen_bio_urls:
                seen_bio_urls.add(found[0])
                # Carry the docket entry text (it names the respondent) as the
                # description, not the generic "Main Document" link label — it
                # heads this brief's block in the combined BIO document.
                bios.append(
                    DocumentRef(KIND_BRIEF_IN_OPPOSITION, found[0], entry_date, text.strip())
                )
    return [ref for ref in (petition, *bios) if ref is not None]


def extract_pdf_text(data: bytes, *, char_cap: int) -> ExtractedText:
    """Extract a PDF's text with pypdf, capped at ``char_cap`` characters.

    SCOTUS filings are born-digital under the 2017 e-filing mandate, so plain
    text extraction is reliable; a scanned paper filing (some IFP petitions)
    yields little or nothing — recorded as empty text, never a crash. The cap
    bounds corpus growth (petitions run 30-300 pages); truncation is flagged so
    provisioning can say so to the reading agent.
    """
    try:
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        total = 0
        truncated = False
        for page in reader.pages:
            text = page.extract_text() or ""
            parts.append(text)
            total += len(text)
            if total >= char_cap:
                truncated = True
                break
        joined = "\n".join(parts)
        if len(joined) > char_cap:
            joined = joined[:char_cap]
            truncated = True
        return ExtractedText(text=joined, pages=len(reader.pages), truncated=truncated)
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
    a failed fetch of one brief never drops the others.
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
    for ref in bio_refs:
        try:
            data = client.get_document(ref.url)
        except httpx.HTTPError:
            continue
        if data is None:
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
    if not fetched_urls:
        return None
    text = "\n\n".join(blocks)
    if len(text) > char_cap:
        text = text[:char_cap]
        truncated = True
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_BRIEF_IN_OPPOSITION,
        # The canonical join of the briefs actually FETCHED — the idempotency
        # key (see above), not a single fetchable URL. Nothing GETs a stored
        # CaseDocument.url; the individual DocumentRef.url values are what fetch.
        url="|".join(sorted(fetched_urls)),
        entry_date=bio_refs[-1].entry_date,  # the latest filing's date
        fetched_at=today,
        pages=pages,
        truncated=truncated,
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
    result names, never a fragment. A missing or unextractable
    document degrades to a skip / an empty-text row; an upstream error skips
    just that document, never the poll.
    """
    refs = select_documents(payload)
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
            continue
        if data is None:
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
    """
    return corpus.CaseDocument(
        case_id=petition.case_id,
        kind=KIND_QUESTIONS_PRESENTED,
        url=petition.url,
        entry_date=petition.entry_date,
        fetched_at=fetched_at,
        pages=0,
        truncated=False,
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
    job-cap cancellation — so the document fetch runs on a bounded reader pool
    there (:data:`_QP_BACKFILL_READERS`), consumed lazily in input order and
    warmed by one serial read so the source's lazily built client is
    constructed on this thread, never raced. The SQLite fallback keeps the
    serial loop: its local reads never needed the help, and the connection
    must stay on one thread. Everything after a fetch — extraction,
    comparison, classification, the writes — is the same serial, ordered code
    either way, so pooled and serial fetching produce identical results. A
    fetch that raises aborts the whole pass, deliberately against the
    degrade-don't-crash default: this is a dispatch-gated convergence sweep
    whose apply verifies itself by re-running, and a silently partial ledger
    would read as a converged one.
    """
    petitions = unchanged = no_petition_text = 0
    reasons: Counter[str] = Counter()
    changes: dict[str, str] = {}
    refused: list[str] = []
    updates: list[corpus.CaseDocument] = []
    case_ids = [
        row.case_id for row in corpus.iter_rows(conn, court="scotus") if corpus.is_live_slice(row)
    ]

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
            updates.append(stored.model_copy(update={"text": derived}))
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

    if corpus.payload_reads_offloaded() and case_ids:
        # The offloaded branch never touches `conn` inside
        # `documents_for_case` (the registered source serves it, and the
        # Protocol requires it to tolerate concurrent reads), which is what
        # makes handing the call to worker threads sound; the mode cannot
        # flip mid-pass because nothing here re-registers the source. The
        # first case is read serially on purpose: the source builds its
        # client lazily on first use behind a broad catch that caches the
        # outcome, so a pool-first call would race sixteen constructions and
        # a losing thread's cached failure would silently empty the pass.
        # Client *calls* tolerate threads; construction does not.
        first = corpus.documents_for_case(conn, case_ids[0])
        with ThreadPoolExecutor(
            max_workers=_QP_BACKFILL_READERS, thread_name_prefix="qp-backfill"
        ) as pool:
            consider(case_ids[0], first)
            fetched = pool.map(
                lambda case_id: corpus.documents_for_case(conn, case_id), case_ids[1:]
            )
            # Consumed lazily, in input order: results free as they are
            # processed, so peak memory is the in-flight window, not the
            # population's whole document text.
            for case_id, documents in zip(case_ids[1:], fetched, strict=True):
                consider(case_id, documents)
    else:
        for case_id in case_ids:
            consider(case_id, corpus.documents_for_case(conn, case_id))
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
