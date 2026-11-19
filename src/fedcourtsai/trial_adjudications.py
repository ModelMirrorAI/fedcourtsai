"""The trial stage's adjudication list: ``config/trial-adjudications.yaml``, read and checked.

The resolver (:mod:`fedcourtsai.pipeline.trial_resolver`) sends an event to
triage when the record has moved on and its rule cannot read how
(``docs/trial-stage.md``, *How the stage registers*). A maintainer settles
such an event by a pull request that adds a row here: the event, the result,
the docket entry the result rests on and the day that entry was filed. The
watchlist pass (:mod:`fedcourtsai.pipeline.trial_events`) reads a row ahead of
the resolver's own rule, for an event it has already written and not yet
closed; a row for any other event does nothing.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import get_args

import yaml
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from . import ids
from .ai_watchlist import UniqueKeyLoader
from .pipeline import moments
from .pipeline.ai_candidates import DISTRICT_COURT
from .schemas import (
    TRIAL_RULINGS_GRANTED,
    Moment,
    TrialJudgmentLabel,
    TrialLeaveLabel,
    TrialRulingLabel,
)

#: The list's file, under the config root.
TRIAL_ADJUDICATIONS_FILENAME = "trial-adjudications.yaml"

_RULINGS = frozenset(get_args(TrialRulingLabel))
_JUDGMENTS = frozenset(get_args(TrialJudgmentLabel))


class Adjudication(BaseModel):
    """One triaged event a maintainer settled."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(description="`<court_id>/<docket_id>` of the docket that owns the event.")
    event_id: str
    result: str = Field(
        description="The ruling on a motion event, or the disposition on the judgment event."
    )
    leave: TrialLeaveLabel | None = Field(
        default=None,
        description="Leave to amend; owed on a dismissal granted in whole or in part, "
        "and refused anywhere else.",
    )
    entry_number: StrictInt = Field(ge=1, description="The docket entry the result rests on.")
    resolved_at: date = Field(description="The day that entry was filed.")

    @model_validator(mode="after")
    def _check(self) -> Adjudication:
        court, _, docket = self.case_id.partition("/")
        if not court or not docket.isdigit() or ids.case_id(court, int(docket)) != self.case_id:
            raise ValueError(f"{self.case_id!r} is not a `<court_id>/<docket_id>` case id")
        if not DISTRICT_COURT.fullmatch(court):
            raise ValueError(f"{self.case_id}: {court!r} is not a district court id")
        spec = moments.trial_spec_for(self.event_id)
        if spec is None:
            raise ValueError(f"{self.event_id!r} is not a declared trial event")
        allowed = _RULINGS if spec.per_motion else _JUDGMENTS
        if self.result not in allowed:
            raise ValueError(
                f"{self.event_id}: {self.result!r} is not one of {', '.join(sorted(allowed))}"
            )
        owes_leave = spec.moment == Moment.trial_dismissal and self.result in TRIAL_RULINGS_GRANTED
        if owes_leave != (self.leave is not None):
            raise ValueError(
                f"{self.event_id}: `leave` is recorded on a dismissal granted in whole or "
                "in part, and nowhere else"
            )
        return self


class TrialAdjudications(BaseModel):
    """The file: every settled event, at most one row each."""

    model_config = ConfigDict(extra="forbid")

    adjudications: list[Adjudication]

    @model_validator(mode="after")
    def _check(self) -> TrialAdjudications:
        seen: set[tuple[str, str]] = set()
        for row in self.adjudications:
            key = (row.case_id, row.event_id)
            if key in seen:
                raise ValueError(f"{row.case_id} {row.event_id} is adjudicated twice")
            seen.add(key)
        return self


def load_trial_adjudications(path: Path) -> dict[tuple[str, str], Adjudication]:
    """Each settled event by ``(case id, event id)``.

    A missing or empty file, a file with no ``adjudications`` and a repeated
    key are errors, not an empty list.
    """
    data = yaml.load(path.read_text(), Loader=UniqueKeyLoader)
    rows = TrialAdjudications.model_validate(data)
    return {(row.case_id, row.event_id): row for row in rows.adjudications}
