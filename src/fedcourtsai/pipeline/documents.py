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
and the QP derivation are pure and tested offline.
"""

from __future__ import annotations

import io
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx
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
# the QUESTION(S) PRESENTED heading to the first of these.
_QP_START_RE = re.compile(r"QUESTIONS?\s+PRESENTED", re.IGNORECASE)
_QP_END_RE = re.compile(
    r"PARTIES TO THE PROCEEDING|CORPORATE DISCLOSURE|RULE 29\.6|RELATED (?:CASES|PROCEEDINGS)"
    r"|TABLE OF CONTENTS|TABLE OF AUTHORITIES|LIST OF (?:ALL )?(?:PARTIES|PROCEEDINGS)"
    r"|OPINIONS? BELOW|IN THE\s+SUPREME COURT",
    re.IGNORECASE,
)
# A QP section beyond this is a parsing miss, not a question (they run a page).
_QP_MAX_CHARS = 4_000
# A captured section that is really a table-of-contents entry: a run of leader
# dots (to a page number). A petition's own TOC lists "QUESTIONS PRESENTED"
# with a page reference, so matching that entry instead of the real heading
# pulls in the TOC's dotted lines. pypdf preserves the leader dots, and a
# genuine QP body — prose — never carries them, so their run is the reliable
# tell. Tolerates the spaced form (". . . .") some fonts extract to.
_QP_TOC_RE = re.compile(r"(?:\.\s*){4,}")


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


def extract_questions_presented(petition_text: str) -> str | None:
    """The questions-presented section of a petition's text, or ``None``.

    Petitions front the QP page (Rule 14.1(a)), so the section runs from the
    QUESTION(S) PRESENTED heading to the next standard front-matter heading.
    But a petition's own table of contents lists that heading too, and matching
    the TOC entry captures the dotted TOC lines instead of the questions — so
    scan *every* occurrence and return the first whose body reads as prose (no
    leader-dot run), skipping the TOC entry wherever it falls.
    Length-capped: a runaway match means the end-heading regex missed, and a
    4-page "question" would only bury the signal it exists to surface.
    """
    for start in _QP_START_RE.finditer(petition_text):
        rest = petition_text[start.end() :]
        end = _QP_END_RE.search(rest)
        section = (rest[: end.start()] if end is not None else rest[:_QP_MAX_CHARS]).strip()
        if not section or _QP_TOC_RE.search(section):
            continue  # an empty capture or a dotted TOC entry — not the questions body
        return section[:_QP_MAX_CHARS]
    return None


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
    whenever the petition itself was (re)fetched. A missing or unextractable
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
            documents.append(
                corpus.CaseDocument(
                    case_id=case_id,
                    kind=KIND_QUESTIONS_PRESENTED,
                    url=petition.url,
                    entry_date=petition.entry_date,
                    fetched_at=today,
                    pages=0,
                    truncated=False,
                    text=questions,
                )
            )
    return documents
