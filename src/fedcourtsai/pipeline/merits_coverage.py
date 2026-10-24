"""Merits forecast coverage: every plenary grant, and what became of its forecast.

The merits stream forecasts each grant that opens a merits proceeding, but a
grant can fall out of that stream at several seams — no merits event was ever
minted, the event exists but the predict scope refuses it, the case was decided
or terminated before a round reached it, or the grant went stale. Each seam is
correct on its own terms, and none of them reports itself, so a missing case is
silent. This census sets the corpus's plenary grants against the merits events
and the committed predictions, and gives every grant exactly one status, so a
release can state how many eligible cases it covers and name the ones it does
not.

The population is every SCOTUS modern cert docket whose grant opens a merits
proceeding (:func:`fedcourtsai.corpus.opens_merits_proceeding`), keyed to the
October Term of its grant date. A grant whose disposition rode the cert order —
a judgment dated on or before the grant
(:func:`fedcourtsai.pipeline.judgment.judgment_rode_the_grant_order`) — is a
cert-stage fact the merits stream never forecasts, so it is counted apart as
``order_riding`` and given no status. Reads the corpus index and the git
ledger's committed predictions; reads no snapshot and writes nothing. Counts
docket rows, so a consolidated set counts once per docket.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..matrix import event_has_predictions
from ..schemas import MERITS_PROCEEDING_DISPOSITIONS, Stage
from ..store import merits_event_forecastable
from ..supremecourt import october_term_year
from . import moments
from .judgment import judgment_rode_the_grant_order


class MeritsCoverageStatus(StrEnum):
    """What became of one plenary grant's merits forecast, first match wins.

    ``forecast`` and ``owed`` are the stream working; ``terminated``,
    ``decided_unforecast``, ``stale`` and ``out_of_scope`` are documented
    refusals or a case the forward stream never reached; ``no_event`` and
    ``not_forecastable`` are the coverage holes this census exists to find.
    """

    forecast = "forecast"
    """At least one committed prediction on one of the case's merits events."""
    terminated = "terminated"
    """The proceeding ended with no disposition (`merits_terminated`)."""
    decided_unforecast = "decided_unforecast"
    """A merits judgment is latched and no prediction was ever committed."""
    stale = "stale"
    """Pending on the record past the stale-grant bound (`is_stale_unparsed_grant`)."""
    out_of_scope = "out_of_scope"
    """A predict-scope rule refuses the case, whether or not a merits event was minted."""
    no_event = "no_event"
    """Pending, in scope, and the corpus holds no open merits event: nothing can be forecast."""
    owed = "owed"
    """An open, forecastable merits event awaiting its first predict round."""
    not_forecastable = "not_forecastable"
    """A merits event exists, in scope, but the merits admission refuses it."""


#: The statuses that name a hole in the stream rather than a decision.
GAP_STATUSES = frozenset({MeritsCoverageStatus.no_event, MeritsCoverageStatus.not_forecastable})


class MeritsCoverageEntry(BaseModel):
    """One plenary grant that has no committed merits prediction."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    term: int = Field(description="October Term of the grant date")
    date_cert_granted: date
    status: MeritsCoverageStatus
    detail: str | None = Field(
        default=None,
        description="The predict-scope reason for `out_of_scope`, the termination "
        "for `terminated`, whether a merits event existed for `decided_unforecast`, "
        "and a resolved merits event for `no_event`",
    )


class MeritsCoverageTerm(BaseModel):
    """One grant Term's merits coverage."""

    model_config = ConfigDict(extra="forbid")

    term: int = Field(description="October Term of the grant date")
    plenary_grants: int = Field(
        ge=0, description="Grants opening a merits proceeding that did not ride the cert order"
    )
    order_riding: int = Field(
        ge=0,
        description="Grant-family rows whose judgment is dated on or before the grant — "
        "a cert-stage disposition carried under a `granted` label, given no status",
    )
    statuses: dict[str, int] = Field(
        description="`plenary_grants` split by `MeritsCoverageStatus`; the values sum to it"
    )


class MeritsCoverage(BaseModel):
    """The merits coverage census over a range of grant Terms."""

    model_config = ConfigDict(extra="forbid")

    as_of: date = Field(description="The day the forecastability and staleness rules read")
    terms: list[MeritsCoverageTerm]
    uncovered: list[MeritsCoverageEntry] = Field(
        description="Every plenary grant in range without a committed prediction, "
        "in Term then docket order"
    )
    gaps: int = Field(
        ge=0,
        description="Entries whose status is `no_event` or `not_forecastable`: "
        "eligible grants the stream cannot reach",
    )


#: The declared merits moments' event ids, read in the ledger whatever the corpus holds.
_MERITS_EVENT_IDS = frozenset(spec.event_id for spec in moments.moments_for(Stage.merits))


def _merits_events(conn: corpus.ReadConnection, case_id: str) -> list[corpus.CorpusEvent]:
    return [
        e
        for e in corpus.events_for_case(conn, case_id)
        if e.stage == Stage.merits or e.event_id in _MERITS_EVENT_IDS
    ]


def _has_prediction(data_root: Path, case_id: str, events: list[corpus.CorpusEvent]) -> bool:
    """Whether the ledger holds a prediction on any merits event of the case.

    Reads the ledger under every declared merits event id as well as the
    corpus's own merits events, so a committed forecast counts even where its
    corpus event row is missing or carries no stage.
    """
    court, docket = case_id.split("/", 1)
    event_ids = _MERITS_EVENT_IDS | {e.event_id for e in events}
    return any(event_has_predictions(data_root, court, int(docket), eid) for eid in event_ids)


def classify_grant(  # noqa: PLR0911 - one return per status, in the enum's order
    conn: corpus.ReadConnection, data_root: Path, row: corpus.CorpusRow, *, today: date
) -> tuple[MeritsCoverageStatus, str | None]:
    """``(status, detail)`` for one plenary grant, first match in the enum's order."""
    events = _merits_events(conn, row.case_id)
    if _has_prediction(data_root, row.case_id, events):
        return MeritsCoverageStatus.forecast, None
    if row.merits_terminated is not None:
        return MeritsCoverageStatus.terminated, str(row.merits_terminated)
    if row.merits_judgment is not None:
        minted = "merits event minted" if events else "no merits event"
        return MeritsCoverageStatus.decided_unforecast, minted
    if corpus.is_stale_unparsed_grant(row, today=today):
        return MeritsCoverageStatus.stale, None
    # Before the event check: the mint refuses an out-of-scope grant its event,
    # so a missing event there is the documented refusal, not a hole.
    reason = corpus.out_of_scope_reason_full(conn, row)
    if reason is not None:
        return MeritsCoverageStatus.out_of_scope, reason
    open_events = [e for e in events if not e.resolved]
    if not open_events:
        resolved = "merits event resolved, no judgment latched" if events else None
        return MeritsCoverageStatus.no_event, resolved
    if any(merits_event_forecastable(e, row, today) for e in open_events):
        return MeritsCoverageStatus.owed, None
    return MeritsCoverageStatus.not_forecastable, None


def _rode_the_order(row: corpus.CorpusRow) -> bool:
    # The judgment-date half of `decision_record.rode_the_order` only: the
    # population is already the merits-proceeding labels, so no cert-order
    # label can reach here.
    return (
        row.merits_decided is not None
        and row.date_cert_granted is not None
        and judgment_rode_the_grant_order(row.merits_decided, row.date_cert_granted)
    )


def merits_coverage(
    conn: corpus.ReadConnection,
    data_root: Path,
    *,
    first_term: int,
    last_term: int,
    today: date,
) -> MeritsCoverage:
    """Census every plenary grant made in ``first_term``..``last_term`` against its forecast."""
    terms = {t: (Counter[str](), [0]) for t in range(first_term, last_term + 1)}
    plenary: dict[int, int] = dict.fromkeys(terms, 0)
    uncovered: list[MeritsCoverageEntry] = []
    rows = (
        row
        for disposition in sorted(MERITS_PROCEEDING_DISPOSITIONS)
        for row in corpus.iter_rows(conn, court="scotus", disposition=disposition)
    )
    for row in rows:
        granted = row.date_cert_granted
        if granted is None or not corpus.opens_merits_proceeding(row):
            continue
        if not corpus.is_modern_cert(row):
            continue
        term = october_term_year(granted)
        if term not in terms:
            continue
        statuses, order_riding = terms[term]
        if _rode_the_order(row):
            order_riding[0] += 1
            continue
        plenary[term] += 1
        status, detail = classify_grant(conn, data_root, row, today=today)
        statuses[status.value] += 1
        if status != MeritsCoverageStatus.forecast:
            uncovered.append(
                MeritsCoverageEntry(
                    case_id=row.case_id,
                    docket_number=row.docket_number,
                    term=term,
                    date_cert_granted=granted,
                    status=status,
                    detail=detail,
                )
            )
    uncovered.sort(key=lambda e: (e.term, e.docket_number))
    return MeritsCoverage(
        as_of=today,
        terms=[
            MeritsCoverageTerm(
                term=term,
                plenary_grants=plenary[term],
                order_riding=order_riding[0],
                statuses=dict(sorted(statuses.items())),
            )
            for term, (statuses, order_riding) in terms.items()
        ],
        uncovered=uncovered,
        gaps=sum(e.status in GAP_STATUSES for e in uncovered),
    )
