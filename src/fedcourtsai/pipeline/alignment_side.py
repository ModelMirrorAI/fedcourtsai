"""The side-coding pass the score baselines read: its frame, its extract and its publish rule.

``docs/merits-alignment-baseline.md`` specifies the pass: at grant, one agent
reads the case as it then stood and records which party argues the
conservative position and a score ``s`` for how conservative the outcome will
be. This module is everything around that agent turn that needs no model:

- **The frame** (:func:`frame_rows`): every SCOTUS cert grant that opened a
  merits proceeding (:func:`fedcourtsai.corpus.opens_merits_proceeding`) and did
  not ride the cert order, granted in :data:`FIRST_GRANT_TERM` or later, on
  the live slice (:func:`fedcourtsai.corpus.is_live_slice`). That
  start covers every case decided from OT2022 on, the Terms the past-Term fits
  read, since a case is decided in the Term it is granted in or the next.
- **The extract** (:func:`build_extract`): for each frame case not yet coded,
  the text it stood on at grant — the caption, the petitioner as captioned, the
  court below, the grant date and the stored questions presented — and no
  outcome. The caption and petitioner are the corpus's as of its latest pull,
  so a party substituted after the grant shows under its new name: a timing
  difference, not an outcome. A case with no stored questions presented has
  nothing to code from and is counted, not guessed at. Each row's **mode** is
  decided here and kept off the coder's input, in a sidecar: ``replay`` if the
  case carried a merits judgment when the extract was cut, ``forward`` if not.
  The coder is not told which, so the mode cannot steer a code, and every
  ``replay`` code carries the contamination-risk flag.
- **Clean codes** (:func:`is_clean`): a ``forward`` code made within
  :data:`CLEAN_LAG_DAYS` of its grant and before its case's argument. Only
  these enter the clean check, since a forward code made long after its grant
  may read commentary on an argued case.
- **The publish rule** (:func:`publish`): a run's code lines must cover the
  extract exactly, keyed on the case id and docket number pair, and may add a
  case the committed file does not hold but never replace one. The file is
  append-only, because a code revised after its case moved is no longer a
  grant-time code.

Read-only against the corpus; the only file it writes is the artifact the
publish step is handed.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Final

from pydantic import ValidationError

from .. import corpus
from ..schemas import (
    AlignmentCodeMode,
    AlignmentSide,
    AlignmentSideCode,
    AlignmentSideCodes,
    AlignmentValence,
)
from ..supremecourt import october_term_year
from .decision_record import rode_the_order
from .documents import KIND_QUESTIONS_PRESENTED
from .prefetch import prefetch_by_case

#: The first grant Term the frame holds. A case is decided in its grant Term or
#: the next, so this start covers every decision from OT2022 on.
FIRST_GRANT_TERM: Final = 2021

#: The most rows one coding run is handed. A run is one headless turn under a
#: step clock, and only a complete code file publishes, so the extract is cut to
#: what a run can finish rather than to what the frame holds.
CODE_ROW_CEILING: Final = 400

#: The most days after its grant a forward code may be made and still count as
#: a grant-time code in the clean check. Argument ordinarily comes months after
#: a grant; an expedited case argued sooner is held by the argument date.
CLEAN_LAG_DAYS: Final = 30


class AlignmentSideError(ValueError):
    """A coding run's output that cannot be published."""


def is_clean(code: AlignmentSideCode, *, argued: date | None) -> bool:
    """Whether a code is a grant-time code the clean check may read.

    Forward, made within :data:`CLEAN_LAG_DAYS` of its grant, and, where the
    case has been argued, made before the argument: an expedited case can be
    argued inside the lag.
    """
    return (
        code.mode == AlignmentCodeMode.forward
        and (code.coded_at - code.granted).days <= CLEAN_LAG_DAYS
        and (argued is None or code.coded_at < argued)
    )


def codes_path(data_root: Path) -> Path:
    """The committed side-codes artifact."""
    return data_root / "merits-alignment" / "alignment-side-codes.json"


@dataclass(frozen=True)
class ExtractRow:
    """One case's grant-time text: the whole input the coder reads for it."""

    case_id: str
    docket_number: str
    caption: str
    petitioner: str | None
    court_below: str | None
    granted: str
    questions_presented: str


@dataclass(frozen=True)
class FrameCase:
    """A frame case before its text is read."""

    case_id: str
    docket_number: str
    caption: str
    petitioner: str | None
    court_below: str | None
    granted: date
    decided: bool


@dataclass(frozen=True)
class Extract:
    """One coding run's rows, each row's mode, and what the frame could not hand over."""

    rows: list[ExtractRow]
    modes: dict[str, AlignmentCodeMode]
    frame: int
    already_coded: int
    no_text: int
    deferred: int


def in_frame(row: corpus.CorpusRow, *, first_grant_term: int = FIRST_GRANT_TERM) -> bool:
    """Whether a corpus row is a merits grant the pass codes.

    The live-slice clause is :func:`read_extract`'s, applied in SQL there.
    """
    return (
        corpus.opens_merits_proceeding(row)
        and not rode_the_order(row)
        and row.date_cert_granted is not None
        and october_term_year(row.date_cert_granted) >= first_grant_term
        and bool(row.docket_number.strip())
    )


def frame_rows(
    rows: Iterable[corpus.CorpusRow], *, first_grant_term: int = FIRST_GRANT_TERM
) -> list[FrameCase]:
    """The frame's cases, in ``case_id`` order."""
    cases = []
    for row in rows:
        if not in_frame(row, first_grant_term=first_grant_term):
            continue
        assert row.date_cert_granted is not None  # in_frame checked it
        cases.append(
            FrameCase(
                case_id=row.case_id,
                docket_number=row.docket_number.strip(),
                caption=row.case_name,
                petitioner=row.petitioner_title,
                court_below=row.originating_court_name,
                granted=row.date_cert_granted,
                decided=row.merits_judgment is not None,
            )
        )
    return sorted(cases, key=lambda c: c.case_id)


def build_extract(
    cases: Sequence[FrameCase],
    texts: Mapping[str, str],
    coded: Iterable[str],
    *,
    ceiling: int = CODE_ROW_CEILING,
) -> Extract:
    """Cut one coding run's extract from the frame.

    ``texts`` maps a case id to its stored questions presented. Cases already
    ``coded`` are left out; of the rest, the earliest grants come first, so a
    frame larger than ``ceiling`` clears oldest first and every forward grant
    is coded within a run of the backlog clearing.
    """
    done = set(coded)
    owed = [c for c in cases if c.case_id not in done]
    with_text = [c for c in owed if texts.get(c.case_id, "").strip()]
    ordered = sorted(with_text, key=lambda c: (c.granted, c.case_id))
    batch = sorted(ordered[:ceiling], key=lambda c: c.case_id)
    return Extract(
        rows=[
            ExtractRow(
                case_id=c.case_id,
                docket_number=c.docket_number,
                caption=c.caption,
                petitioner=c.petitioner,
                court_below=c.court_below,
                granted=c.granted.isoformat(),
                questions_presented=texts[c.case_id],
            )
            for c in batch
        ],
        modes={
            c.case_id: AlignmentCodeMode.replay if c.decided else AlignmentCodeMode.forward
            for c in batch
        },
        frame=len(cases),
        already_coded=len(cases) - len(owed),
        no_text=len(owed) - len(with_text),
        deferred=max(len(with_text) - ceiling, 0),
    )


def read_extract(conn: corpus.ReadConnection, coded: Iterable[str]) -> Extract:
    """The extract the corpus behind ``conn`` cuts, given the cases already ``coded``."""
    cases = frame_rows(corpus.iter_rows(conn, court="scotus", live_slice=True))
    done = set(coded)
    texts: dict[str, str] = {}
    with prefetch_by_case(
        [c.case_id for c in cases if c.case_id not in done],
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="alignment-extract",
    ) as fetched:
        for case_id, documents in fetched:
            stored = next((d for d in documents if d.kind == KIND_QUESTIONS_PRESENTED), None)
            if stored is not None:
                texts[case_id] = stored.text
    return build_extract(cases, texts, done)


def extract_payload(extract: Extract) -> list[dict[str, object]]:
    """The extract file's rows, as the coder reads them."""
    return [asdict(row) for row in extract.rows]


def modes_payload(extract: Extract) -> dict[str, str]:
    """The sidecar's case id to mode map, which the coder never reads."""
    return {case_id: mode.value for case_id, mode in sorted(extract.modes.items())}


def read_code_lines(path: Path) -> list[dict[str, object]]:
    """A coding run's JSONL output, one object per non-blank line."""
    lines = []
    for number, raw in enumerate(path.read_text().splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AlignmentSideError(f"line {number}: not JSON ({exc.msg})") from exc
        if not isinstance(value, dict):
            raise AlignmentSideError(f"line {number}: not a JSON object")
        lines.append(value)
    return lines


_CODER_FIELDS: Final = frozenset(
    {"case_id", "docket_number", "conservative_side", "score", "valence", "note"}
)


def publish(
    prior: AlignmentSideCodes | None,
    extract_rows: Sequence[Mapping[str, object]],
    modes: Mapping[str, str],
    lines: Sequence[Mapping[str, object]],
    *,
    model: str,
    run_id: str,
    coded_at: date,
) -> AlignmentSideCodes:
    """Merge one run's code lines into the committed codes, append-only.

    The lines must name every extract row exactly once by its (case id, docket
    number) pair and nothing else, and carry only the coder's fields: the
    grant date, mode, contamination flag, model, run and day are the harness's,
    stamped here from the extract and the run, never read from the coder.
    """
    rows = {str(r["case_id"]): r for r in extract_rows}
    if len(rows) != len(extract_rows):
        raise AlignmentSideError("the extract names a case twice")
    if set(modes) != set(rows):
        raise AlignmentSideError("the modes sidecar does not cover the extract exactly")
    seen: dict[str, AlignmentSideCode] = {}
    for number, line in enumerate(lines, start=1):
        extra = set(line) - _CODER_FIELDS
        if extra:
            raise AlignmentSideError(
                f"line {number}: fields the coder does not write: {sorted(extra)}"
            )
        case_id = str(line.get("case_id", ""))
        row = rows.get(case_id)
        if row is None:
            raise AlignmentSideError(f"line {number}: {case_id!r} is not in the extract")
        if str(line.get("docket_number", "")) != row["docket_number"]:
            raise AlignmentSideError(f"line {number}: docket number does not match {case_id}")
        if case_id in seen:
            raise AlignmentSideError(f"line {number}: {case_id} coded twice")
        mode = AlignmentCodeMode(modes[case_id])
        score, note = line.get("score"), line.get("note")
        # A bool is an int in Python, and pydantic's lax mode reads "0.7" as a
        # float, so the coder's two free fields are type-checked here first.
        if isinstance(score, bool) or not isinstance(score, int | float):
            raise AlignmentSideError(f"line {number}: `score` is not a number")
        if not isinstance(note, str):
            raise AlignmentSideError(f"line {number}: `note` is not a string")
        try:
            seen[case_id] = AlignmentSideCode(
                case_id=case_id,
                docket_number=str(row["docket_number"]),
                granted=date.fromisoformat(str(row["granted"])),
                conservative_side=AlignmentSide(str(line.get("conservative_side"))),
                score=float(score),
                valence=AlignmentValence(str(line.get("valence"))),
                note=note,
                mode=mode,
                contamination_risk=mode == AlignmentCodeMode.replay,
                model=model,
                run_id=run_id,
                coded_at=coded_at,
            )
        except (ValueError, ValidationError) as exc:
            raise AlignmentSideError(f"line {number}: {exc}") from exc
    missing = sorted(set(rows) - set(seen))
    if missing:
        raise AlignmentSideError(f"{len(missing)} extract row(s) not coded, e.g. {missing[0]}")
    held = {e.case_id: e for e in (prior.entries if prior is not None else [])}
    replaced = sorted(set(held) & set(seen))
    if replaced:
        raise AlignmentSideError(
            f"{len(replaced)} case(s) already coded, e.g. {replaced[0]}: a code is never revised"
        )
    merged = {**held, **seen}
    return AlignmentSideCodes(entries=[merged[k] for k in sorted(merged)])


def render_run_report(codes: AlignmentSideCodes, *, run_id: str) -> str:
    """The review PR's block for one run: counts over the codes it added, no text.

    Counts and a mean only, never a note or a case: the block goes into a
    public PR body, and the codes themselves are the diff beside it.
    """
    added = [e for e in codes.entries if e.run_id == run_id]
    if not added:
        return f"run {run_id}: no codes added\n"
    by_mode = {m.value: sum(1 for e in added if e.mode == m) for m in AlignmentCodeMode}
    by_valence = {v.value: sum(1 for e in added if e.valence == v) for v in AlignmentValence}
    by_side = {s.value: sum(1 for e in added if e.conservative_side == s) for s in AlignmentSide}
    mean = sum(e.score for e in added) / len(added)
    granted = sorted(e.granted for e in added)
    return (
        f"run {run_id}: {len(added)} code(s) added, {len(codes.entries)} in the file\n"
        f"granted {granted[0].isoformat()} to {granted[-1].isoformat()}\n"
        "mode: " + ", ".join(f"{k} {v}" for k, v in by_mode.items()) + "\n"
        "valence: " + ", ".join(f"{k} {v}" for k, v in by_valence.items()) + "\n"
        "conservative side: " + ", ".join(f"{k} {v}" for k, v in by_side.items()) + "\n"
        f"mean score (P conservative side prevails): {mean:.3f}\n"
    )
