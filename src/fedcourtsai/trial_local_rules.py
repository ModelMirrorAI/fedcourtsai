"""The districts' default briefing periods: ``config/trial-local-rules.yaml``, read and checked.

The trial stage (``docs/trial-stage.md``) opens a motion event when the
motion's briefing closes, and where the docket states no deadline it counts
one from the district's local rule. This module reads those rules, one row per
district court, each citing the rule it was read from, the page it was read
on, the day it was read and the day that version took force. A court with no
row has no local-rule deadline: its motions open on the reply itself or on a
date the docket states.

The opener (:mod:`fedcourtsai.pipeline.trial_opener`) takes the rows as
:class:`~fedcourtsai.pipeline.trial_opener.DistrictRule` values and never reads
the file itself.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .pipeline.trial_opener import DistrictRule, LocalRule
from .pipeline.trial_resolver import MOTION_MOMENTS, TrialMoment

#: The rules' file, under the config root.
TRIAL_LOCAL_RULES_FILENAME = "trial-local-rules.yaml"


class Periods(BaseModel):
    """One kind of motion's periods, in calendar days."""

    model_config = ConfigDict(extra="forbid")

    opposition_days: int = Field(ge=1, le=90)
    #: ``null`` where the district allows no reply as of right.
    reply_days: int | None = Field(ge=1, le=90)


class CourtRule(Periods):
    """One district's row: its default periods and where they were read."""

    #: The rule, as the court cites it.
    cite: str = Field(min_length=1)
    #: The court's own page or document the rule was read on.
    source: str = Field(pattern=r"^https://[a-z0-9.-]+\.uscourts\.gov/")
    read_on: date
    #: The day the version read took force; a motion filed earlier gets no deadline.
    in_force: date
    #: What the reply period runs from: the opposition's filing, or the day it was due.
    reply_from: Literal["opposition", "opposition-due"] = "opposition"
    #: The motions the rule gives other periods, by moment.
    motions: dict[TrialMoment, Periods] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> CourtRule:
        if self.in_force > self.read_on:
            raise ValueError("in_force is after read_on: the rule read was not yet in force")
        stray = set(self.motions) - MOTION_MOMENTS
        if stray:
            raise ValueError(f"not a motion moment: {sorted(m.value for m in stray)}")
        return self

    def district_rule(self) -> DistrictRule:
        """This row as the opener reads it."""
        from_due = self.reply_from == "opposition-due"

        def periods(row: Periods) -> LocalRule:
            return LocalRule(row.opposition_days, row.reply_days, reply_from_due=from_due)

        return DistrictRule(
            default=periods(self),
            by_moment={moment: periods(row) for moment, row in self.motions.items()},
            in_force=self.in_force,
        )


class TrialLocalRules(BaseModel):
    """The file: every district's row, by CourtListener court id."""

    model_config = ConfigDict(extra="forbid")

    courts: dict[str, CourtRule] = Field(default_factory=dict)


def load_trial_local_rules(path: Path) -> dict[str, DistrictRule]:
    """Each district's rule by court id; a missing or unreadable file is an error."""
    data = yaml.safe_load(path.read_text())
    rules = TrialLocalRules.model_validate(data)
    return {court: row.district_rule() for court, row in rules.courts.items()}
