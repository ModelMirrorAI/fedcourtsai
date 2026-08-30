"""Back-fill of the dated interim/merits signals no automatic channel revisits.

``response_requested_at``, ``response_filed_at`` and ``merits_brief_filed`` are
derived at ingest by :func:`map_live_docket` from the proceedings list. A row
whose last poll predates those columns carries the undated
:attr:`response_requested` flag with no date beside it, and no automatic channel
corrects that: the live poller serves the **undecided** slice, so a decided row
has left the rotation, and the flag is a max-latched boolean a later write cannot
turn back into a question. Only a re-read aimed at the row — ``refresh-dockets``
on named rows, or a Term re-walk — would otherwise reach it, which is a fetch
against upstream for a fact already stored. The columns are recoverable from the corpus alone —
the newest stored live snapshot is the same payload the original ingest read — so
this pass re-parses it with the same pure parsers rather than re-fetching.

**A sibling of :func:`~fedcourtsai.pipeline.ingest.backfill_live_signals`, not a
widening of it**, and the reason is that pass's predicate rather than its
mechanism. A NULL ``distribution_count`` is the parse-coverage sentinel for the
whole live-signal family — it is what makes a NULL ``cvsg_date`` read as *never
parsed* rather than *no CVSG* — and the signals pass consumes that sentinel,
writing ``distribution_count`` **unconditionally**, with no max latch. That write
is sound only because its predicate guarantees the column was NULL. Widening the
predicate to also select rows missing a response date would admit rows whose
count is already stored, and a payload served with its proceedings degraded parses
as a confident ``0`` — so the widening would let this repair silently overwrite a
good stored count with a degraded one, which is exactly the regression the max
latch exists to reject. The two passes also want different shapes: that one is an
unattended hook on a writer entrypoint returning a bare count pair, this one is a
bounded maintenance sweep a maintainer reads before applying.

The three columns are fill-in only, matching the latch family they sit in on the
upsert path: a stored value is never overwritten, so a row already carrying a date
keeps it and the pass converges. That also makes a degraded parse cheap here in a
way it is not for a count — an empty or absent proceedings list yields ``None``
from every parser below, which fills nothing, rather than a confident zero that
asserts a fact. Rows with no stored live-shaped snapshot to parse are counted and
reported, never failed: under the corpus-split mode the payloads live in the
content store, and a poll that 404-stamped without storing one leaves nothing to
re-read.

Like its ``set_*`` siblings the write is a direct ``UPDATE`` of the index and
**never the casestore mirror**, so a store-side rebuild from ``case.json`` would
resurrect the pre-sweep NULLs.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date

from .. import corpus
from ..schemas import MERITS_PROCEEDING_DISPOSITIONS
from .cert_signals import proceedings_entries
from .interim_signals import response_filed_date, response_requested_date
from .merits_signals import respondent_brief_date
from .prefetch import prefetch_by_case

_MERITS_PROCEEDING_VALUES = frozenset(d.value for d in MERITS_PROCEEDING_DISPOSITIONS)
_MERITS_PROCEEDING_SQL = ", ".join(f"'{v}'" for v in sorted(_MERITS_PROCEEDING_VALUES))

# Two arms over the live slice: a flagged response with no date beside it, and a
# granted docket with no merits brief read off it. Both are gaps a stored snapshot
# can close, and the first is unreachable by any poll — a flagged row is decided,
# so the rotation has left it. The second overlaps the rotation slightly: a grant
# still undecided with an open merits-stage event is retained by `live_rotation`,
# and its next poll re-parses the same column. Selecting those anyway is harmless
# rather than redundant — the poll and this pass run the same parsers over the
# same payload, and the column is fill-in only, so whichever writes first wins and
# the other is a no-op. Excluding them would need this pass to re-implement the
# rotation predicate to save a write it already agrees with.
#
# The grant date alone does *not* select the second arm: the column's own writer
# gates on the disposition too (`cert_granted is not None and disposition in
# MERITS_PROCEEDING_DISPOSITIONS`), because a GVR, a summary reversal and a
# granted application all keep `date_cert_granted` while opening no merits
# proceeding to be briefed (`corpus.opens_merits_proceeding`). Selecting on the
# date alone would write a brief date onto a case that has no merits proceeding —
# a value no channel would ever write, and one that never self-corrects, the
# column being fill-in only. Rendered from the same frozenset the writer reads, so
# the sweep's population cannot drift from the column's.
_REVISIT_SQL = (
    "(response_requested = 1 AND response_requested_at IS NULL) "
    "OR (date_cert_granted IS NOT NULL AND merits_brief_filed IS NULL "
    f"    AND disposition IN ({_MERITS_PROCEEDING_SQL}))"
)


@dataclass
class ResponseFieldFill:
    """The dated signals one row gains, carrying only what was NULL before."""

    case_id: str
    response_requested_at: date | None = None
    response_filed_at: date | None = None
    merits_brief_filed: date | None = None


@dataclass
class ResponseBackfillResult:
    """What the dated-signal back-fill wrote (or would write on a dry run)."""

    applied: bool = False
    filled: list[ResponseFieldFill] = field(default_factory=list)
    #: Rows the revisit predicate selected — the denominator the fills are a
    #: fraction of.
    candidates: int = 0
    #: Selected rows with no stored live-shaped snapshot to parse. Not evidence
    #: of a clean corpus, just of an unreadable one, which is why it is reported
    #: beside the fill count rather than folded into it.
    no_snapshot: int = 0
    #: Rows whose newest live snapshot discloses no proceedings list at all, so
    #: the signals are unobservable from it rather than absent.
    no_proceedings: int = 0
    #: Rows read and parsed that yielded nothing to fill. Not the converged
    #: population: an undated request (the flag sets, the date does not) and a
    #: merits brief simply not filed yet both land here and stay candidates.
    unchanged: int = 0
    #: True when ``apply`` was asked for but the blast-radius bound refused it.
    #: Nothing is written in that case — the plan is reported and abandoned.
    refused: bool = False


def _stored_date(record: sqlite3.Row, column: str) -> date | None:
    raw = record[column]
    return date.fromisoformat(str(raw)) if raw else None


def backfill_response_fields(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_fills: int | None = None,
) -> ResponseBackfillResult:
    """Re-derive the dated interim/merits signals from each row's newest snapshot.

    ``max_fills`` is the blast-radius bound and lives here rather than in the
    caller, so a code caller is bounded on the same terms as the command. Over the
    bound nothing is written and ``refused`` is set.
    """
    result = ResponseBackfillResult(applied=apply)
    rows = conn.execute(
        "SELECT case_id, date_cert_granted, disposition, response_requested_at, "
        f"response_filed_at, merits_brief_filed FROM cases "
        f"WHERE {corpus.LIVE_SLICE_SQL} AND ({_REVISIT_SQL}) ORDER BY case_id"
    ).fetchall()
    result.candidates = len(rows)
    if not rows:
        return result

    # The grant date is carried only where the disposition opens a merits
    # proceeding, so `respondent_brief_date` reads nothing on a GVR or a summary
    # reversal. Gating the *fill* and not merely the selection is what closes the
    # arm-1 route to the same bad write: a flagged response on a GVR row is
    # selected by the response arm, and would otherwise still have a brief date
    # derived from its grant date on the way past.
    pending = [
        (
            str(record["case_id"]),
            (
                _stored_date(record, "date_cert_granted")
                if str(record["disposition"] or "") in _MERITS_PROCEEDING_VALUES
                else None
            ),
            _stored_date(record, "response_requested_at"),
            _stored_date(record, "response_filed_at"),
            _stored_date(record, "merits_brief_filed"),
        )
        for record in rows
    ]
    with prefetch_by_case(
        [case_id for case_id, *_ in pending],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="response-backfill",
    ) as fetched:
        for (case_id, granted_on, had_requested, had_filed, had_brief), (_, snapshot) in zip(
            pending, fetched, strict=True
        ):
            if snapshot is None:
                result.no_snapshot += 1
                continue
            _, payload = snapshot
            entries = proceedings_entries(payload)
            if not entries:
                # An absent or empty proceedings list makes these signals
                # unobservable from this payload, not absent from the docket.
                result.no_proceedings += 1
                continue
            fill = ResponseFieldFill(
                case_id=case_id,
                response_requested_at=(None if had_requested else response_requested_date(entries)),
                response_filed_at=None if had_filed else response_filed_date(entries),
                # `granted_on` is None unless the disposition opens a merits
                # proceeding, and the parser reads nothing without it — so this is
                # the disposition gate as much as the date one.
                merits_brief_filed=(
                    None if had_brief else respondent_brief_date(payload, granted_on=granted_on)
                ),
            )
            if (
                fill.response_requested_at is None
                and fill.response_filed_at is None
                and fill.merits_brief_filed is None
            ):
                result.unchanged += 1
                continue
            result.filled.append(fill)

    if apply and max_fills is not None and len(result.filled) > max_fills:
        result.refused = True
        result.applied = False
        return result
    if not apply:
        return result

    with conn:
        for fill in result.filled:
            # Fill-in only, matching the latch family these columns sit in on the
            # upsert path: a value another channel stamped is never overwritten.
            conn.execute(
                "UPDATE cases SET "
                "response_requested_at = COALESCE(response_requested_at, ?), "
                "response_filed_at = COALESCE(response_filed_at, ?), "
                "merits_brief_filed = COALESCE(merits_brief_filed, ?) "
                "WHERE case_id = ?",
                (
                    fill.response_requested_at.isoformat() if fill.response_requested_at else None,
                    fill.response_filed_at.isoformat() if fill.response_filed_at else None,
                    fill.merits_brief_filed.isoformat() if fill.merits_brief_filed else None,
                    fill.case_id,
                ),
            )
    return result
