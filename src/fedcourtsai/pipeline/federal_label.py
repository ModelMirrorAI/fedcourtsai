"""The federal-label cross-check: pending petitions a looser reading places federal.

The federal carve-in selects on the petitioner class a registered caption rule
reads. A federal petitioner the rule reads ``private`` or ``state`` is scored
with everyone else and, most often, never selected, and nothing downstream
says so until the grant. This census looks ahead of the outcome: over every
**pending** paid cert petition in predict scope whose band is not ``federal``,
it lists the ones a deliberately looser reading
(:func:`fedcourtsai.pipeline.unforecast.federal_signals`) places federal, while
there is still a conference to forecast. Pending means no stored resolution on
a docket of the current October Term or the two before it; an older open row
is a stale record, not a petition awaiting a conference.

Pending rows only, on purpose. One signal reads counsel entries a docket can
gain after its outcome, which is why no registered rule may use it; on a
petition not yet decided there is no outcome for it to carry. The check
selects nothing and moves no band: a confirmed miss is evidence for the next
registered caption version.

**The alarm** is a flagged petition the Solicitor General's office appears for
that is **not selected**: no forecast is coming for it. A flagged petition
that is selected will be forecast, under a band and base rate that may be the
wrong ones, and is a list for a person to read, as is every party-only flag.
The conference date printed beside an entry is the latest one the docket was
distributed for, which may already have passed.

``salience_version`` re-reads the bands under another registered scorer, to
ask what the check lists under a different caption rule; the selection latch
it prints stays the stored one, set by the active scorer.
Reads the corpus index; reads no snapshot and writes nothing.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import october_term_year
from .salience import scorer
from .unforecast import FEDERAL_BAND, FederalSignal, federal_signals

#: How many October Terms before the current one a pending docket may belong to.
PENDING_TERMS_BACK = 2


class FlaggedPetition(BaseModel):
    """One pending petition outside the ``federal`` band that a loose reading places federal."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    band: str
    signals: list[FederalSignal]
    selected: bool = Field(
        description="The row's stored salience selection latch, set by the active scorer"
    )
    distributed_for_conference: date | None = Field(
        description="The latest conference the docket was distributed for"
    )
    days_to_conference: int | None = Field(
        description="Days from the census day to the conference; negative once it has passed"
    )


class FederalLabelReport(BaseModel):
    """The federal-label cross-check over the pending paid docket."""

    model_config = ConfigDict(extra="forbid")

    as_of: date
    salience_version: str = Field(description="The scorer whose bands the census read")
    pending: int = Field(
        ge=0,
        description="Paid cert petitions in predict scope with no stored resolution, "
        "from the current October Term or the two before it",
    )
    federal: int = Field(ge=0, description="Those the scorer bands `federal`")
    flagged: list[FlaggedPetition] = Field(
        description="Those outside the band that a loose reading places federal, by docket"
    )
    alarms: list[str] = Field(
        description="Each alarm condition that holds, in words; empty when the census is quiet"
    )


def _pending_rows(conn: corpus.ReadConnection, *, today: date) -> list[corpus.CorpusRow]:
    oldest_term = october_term_year(today) - PENDING_TERMS_BACK
    cur = conn.execute(
        "SELECT case_id FROM cases WHERE court = 'scotus' AND disposition IS NULL "
        "AND date_cert_granted IS NULL AND date_cert_denied IS NULL "
        "AND predict_excluded = 0 AND docket_number GLOB '[0-9][0-9]-*' ORDER BY case_id"
    )
    case_ids = [str(record[0]) for record in cur]
    rows = (corpus.get_row(conn, case_id) for case_id in case_ids)
    return [
        row
        for row in rows
        if row is not None
        and corpus.is_modern_cert(row)
        and not corpus.is_ifp_petition(row)
        and corpus.out_of_scope_reason(row) is None
        and (corpus.scotus_term_year(row.docket_number) or 0) >= oldest_term
    ]


def federal_label_check(
    conn: corpus.ReadConnection, *, today: date, salience_version: str | None = None
) -> FederalLabelReport:
    """Cross-check the ``federal`` band on every pending paid petition in scope."""
    active = scorer(salience_version)
    version, band_of = active.version, active.band
    pending = federal = 0
    flagged: list[FlaggedPetition] = []
    for row in _pending_rows(conn, today=today):
        pending += 1
        band = band_of(row)
        if band == FEDERAL_BAND:
            federal += 1
            continue
        signals = federal_signals(row)
        if not signals:
            continue
        conference = row.distributed_for_conference
        flagged.append(
            FlaggedPetition(
                case_id=row.case_id,
                docket_number=row.docket_number,
                band=band,
                signals=signals,
                selected=row.salience_selected,
                distributed_for_conference=conference,
                days_to_conference=(conference - today).days if conference else None,
            )
        )
    flagged.sort(key=lambda f: f.docket_number)
    alarms = [
        f"{f.docket_number}: the Solicitor General's office appears for the petitioner, "
        f"band {f.band}, not selected, conference {f.distributed_for_conference}"
        for f in flagged
        if FederalSignal.sg_office_counsel in f.signals and not f.selected
    ]
    return FederalLabelReport(
        as_of=today,
        salience_version=version,
        pending=pending,
        federal=federal,
        flagged=flagged,
        alarms=alarms,
    )
