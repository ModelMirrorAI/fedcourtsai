"""The application extract: what a ``qp-topic-v1`` labeler reads for an emergency application.

Read-side only and deliberately not a prediction input. An application carries
no questions presented, so the text-only ``qp-topic-v0`` contract has nothing to
read on one; ``qp-topic-v1`` widens the frame to application dockets with a
different, still replay-safe input (``docs/qp-topic.md``, *Applications*). This
module builds that input, one row per application, from the row, its latest
live-shaped snapshot and its stored documents.

**What a row holds.** The docket number and case id (the join key pair, as in
the questions-presented extract), the caption, the court below, the docket
entries that predate the disposition, and the stored ``application`` text where
the content store holds one, cut to :data:`APPLICATION_TEXT_BUDGET` characters.
``input_kind`` says which of the two shapes a row is: ``application-text`` where
the application's own text is present, ``docket-only`` where the label must be
read from the caption and entries alone.

**What a row never holds** is anything that could encode the decision:

- The **cutoff** is the earlier of the first entry the registered disposition
  matcher (:func:`~fedcourtsai.pipeline.interim_signals.match_interim_disposition`)
  reads and the row's stored ``date_decided``. Only entries dated strictly
  before it are kept, so a filing docketed the same day as the order is
  dropped with it; an undated entry cannot be placed and is dropped too.
- An entry recording a **court action** is dropped whatever its date: a grant
  or denial of anything, a dismissal, a vacatur, an entered stay or an order.
  An administrative stay or a granted motion before the decision is not the
  outcome, but it is the Court's act, and a topic is read from what the parties
  filed. The application's own filing entry ("Application (24A1) for a stay of
  the injunction ordered by …") is kept even where it names an order below,
  unless the disposition matcher reads it.
- The application text is kept only when its document is dated before the
  cutoff or undated (the applicant's own opening filing, which precedes any
  ruling on it). Responses and replies are not read: the application states the
  dispute, and a narrower input is a smaller surface to audit.

**The population** is the live slice's application dockets, one row per docket
number, extensions left out: an extension asks for time, and its subject is the
case it extends, which the cert frame already labels. Substantive applications,
applications whose ask the parser could not read, and rows it never parsed all
enter, counted apart in the coverage tally, so a topic cut can reach every
interim forecast and say what it could not.

**Versioned.** ``application-extract-v1`` is this cutoff, this filter and this
budget; a change to any of them is a new label, since it changes what every
application label was read from.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Final, Literal

from .. import corpus
from .documents import KIND_APPLICATION
from .ingest import _live_entries
from .interim_signals import ApplicationKind, match_interim_disposition
from .party import docket_stratum
from .party_rates import docket_key
from .prefetch import prefetch_by_case

#: This extract rule's version.
APPLICATION_EXTRACT_RULE: Final[str] = "application-extract-v1"

#: The vocabulary an application row is labeled under.
APPLICATION_TOPIC_VERSION: Final[str] = "qp-topic-v1"

#: The most characters of stored application text a row carries. The opening
#: pages state the relief sought, the ruling below and why it matters, which is
#: what a subject is read from; the argument after them adds length, not subject.
APPLICATION_TEXT_BUDGET: Final[int] = 6000

#: The most pre-disposition entries a row carries, the earliest kept.
ENTRY_BUDGET: Final[int] = 40

InputKind = Literal["application-text", "docket-only"]

#: The ask, as the coverage tally names it.
AskKind = Literal["substantive", "unknown", "unparsed"]

#: The application's own filing entry, which names the relief sought and is kept
#: even where it quotes an order below.
_FILING_RE: Final = re.compile(r"^\s*applications?\s*\(\s*\d{2}A\d+\s*\)\s*(?:for|to)\b", re.I)

#: An entry recording the Court's own act, not a filing.
_COURT_ACTION_RE: Final = re.compile(
    r"\b(?:granted|denied|dismissed|vacated|stayed|ordered|administrative\s+stay"
    r"|stay\s+(?:is\s+)?entered|judgment\s+issued|mandate\s+issued)\b",
    re.IGNORECASE,
)

Payload = Mapping[str, Any] | None


@dataclass(frozen=True)
class ApplicationEntry:
    """One pre-disposition docket entry, as the labeler sees it."""

    date: str
    text: str


@dataclass(frozen=True)
class ApplicationExtractRow:
    """One application's whole labeling input under ``qp-topic-v1``."""

    case_id: str
    docket_number: str
    input_kind: InputKind
    caption: str
    lower_court: str | None
    text: str
    entries: tuple[ApplicationEntry, ...]

    def as_json(self) -> dict[str, Any]:
        """The extract file's row shape."""
        return {
            "case_id": self.case_id,
            "docket_number": self.docket_number,
            "input_kind": self.input_kind,
            "caption": self.caption,
            "lower_court": self.lower_court,
            "text": self.text,
            "entries": [{"date": entry.date, "text": entry.text} for entry in self.entries],
        }


@dataclass
class ApplicationExtract:
    """The rows one application labeling run reads, and the tally of the frame."""

    rows: list[ApplicationExtractRow] = field(default_factory=list)
    duplicate_rows: int = 0
    extension_rows: int = 0
    #: ``(Term, ask, input_kind)`` -> rows; Term ``None`` where the number has none.
    coverage: Counter[tuple[int | None, AskKind, InputKind]] = field(default_factory=Counter)


def _dated(value: str | None) -> date:
    """A document's entry date, an undated or unreadable one sorting before any cutoff."""
    try:
        return date.fromisoformat(str(value)[:10]) if value else date.min
    except ValueError:
        return date.min


def _cutoff(entries: Sequence[Mapping[str, Any]], decided: date | None) -> date | None:
    """The first date nothing may be read from: the first disposing entry, or the decision."""
    cutoff = decided
    for entry in entries:
        if match_interim_disposition(str(entry.get("description") or "")) is None:
            continue
        dated = entry.get("date_filed")
        if dated:
            found = date.fromisoformat(str(dated))
            cutoff = found if cutoff is None else min(cutoff, found)
        break
    return cutoff


def pre_disposition_entries(
    payload: Mapping[str, Any], decided: date | None
) -> tuple[date | None, tuple[ApplicationEntry, ...]]:
    """The cutoff and the entries a labeler may read, earliest first (module docstring)."""
    entries = _live_entries(payload)
    cutoff = _cutoff(entries, decided)
    kept: list[ApplicationEntry] = []
    for entry in entries:
        dated, text = entry.get("date_filed"), str(entry.get("description") or "").strip()
        if not dated or not text:
            continue
        if cutoff is not None and date.fromisoformat(str(dated)) >= cutoff:
            continue
        if match_interim_disposition(text) is not None:
            continue
        if _COURT_ACTION_RE.search(text) and not _FILING_RE.match(text):
            continue
        kept.append(ApplicationEntry(str(dated), text))
    return cutoff, tuple(kept[:ENTRY_BUDGET])


def application_row(
    row: corpus.CorpusRow, payload: Payload, documents: Iterable[corpus.CaseDocument]
) -> ApplicationExtractRow:
    """One application's extract row from its corpus row, snapshot and documents."""
    cutoff, entries = (
        pre_disposition_entries(payload, row.date_decided)
        if payload is not None
        else (row.date_decided, ())
    )
    text = ""
    for document in documents:
        if document.kind != KIND_APPLICATION or not document.text.strip():
            continue
        if cutoff is not None and _dated(document.entry_date) >= cutoff:
            continue
        text = document.text.strip()[:APPLICATION_TEXT_BUDGET]
        break
    lower_court = str(payload.get("LowerCourt") or "").strip() if payload is not None else ""
    return ApplicationExtractRow(
        case_id=row.case_id,
        docket_number=row.docket_number.strip(),
        input_kind="application-text" if text else "docket-only",
        caption=row.case_name.strip(),
        lower_court=lower_court or None,
        text=text,
        entries=entries,
    )


def _ask(kind: str | None) -> AskKind:
    if kind is None:
        return "unparsed"
    return "substantive" if kind == ApplicationKind.substantive.value else "unknown"


def application_frame(rows: Iterable[corpus.CorpusRow]) -> tuple[list[corpus.CorpusRow], int, int]:
    """The application frame: (rows, duplicate rows, extension rows), in input order."""
    seen: set[str] = set()
    frame: list[corpus.CorpusRow] = []
    duplicates = extensions = 0
    for row in rows:
        if docket_stratum(row) != "application":
            continue
        key = docket_key(row)
        if key is not None:
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
        if row.application_kind == ApplicationKind.extension.value:
            extensions += 1
            continue
        frame.append(row)
    return frame, duplicates, extensions


def application_extract(conn: corpus.ReadConnection) -> ApplicationExtract:
    """The application rows a ``qp-topic-v1`` labeling run reads, in ``case_id`` order.

    Reads each case's snapshot and documents through the registered payload
    path, prefetched as one batch, so the pass serves from the per-case content
    store under the corpus split and from the blob otherwise.
    """
    frame, duplicates, extensions = application_frame(
        corpus.iter_rows(conn, court="scotus", live_slice=True)
    )
    extract = ApplicationExtract(duplicate_rows=duplicates, extension_rows=extensions)

    def read(case_id: str) -> tuple[Payload, list[corpus.CaseDocument]]:
        found = corpus.latest_live_snapshot(conn, case_id)
        return (found[1] if found else None), corpus.documents_for_case(conn, case_id)

    by_case = {row.case_id: row for row in frame}
    with prefetch_by_case(
        [row.case_id for row in frame], read, thread_name_prefix="application-extract"
    ) as fetched:
        for case_id, (payload, documents) in fetched:
            row = by_case[case_id]
            extracted = application_row(row, payload, documents)
            extract.rows.append(extracted)
            term = corpus.scotus_application_term_year(row.docket_number)
            extract.coverage[(term, _ask(row.application_kind), extracted.input_kind)] += 1
    return extract
