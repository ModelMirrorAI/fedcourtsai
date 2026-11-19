"""The districts' briefing periods: the file's checks, and the committed rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from fedcourtsai.ai_watchlist import AI_WATCHLIST_FILENAME, load_ai_watchlist
from fedcourtsai.pipeline.trial_opener import DistrictRule, LocalRule, survey_dockets
from fedcourtsai.pipeline.trial_resolver import TrialMoment
from fedcourtsai.trial_local_rules import (
    TRIAL_LOCAL_RULES_FILENAME,
    TrialLocalRules,
    load_trial_local_rules,
)

_CONFIG = Path(__file__).resolve().parents[1] / "config"


def _row(**changes: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "cite": "Local Rule 7.1",
        "source": "https://www.xxd.uscourts.gov/local-rules",
        "read_on": "2026-11-19",
        "in_force": "2026-01-01",
        "opposition_days": 14,
        "reply_days": 7,
    }
    return {**row, **changes}


def _load(tmp_path: Path, row: dict[str, Any]) -> dict[str, DistrictRule]:
    path = tmp_path / TRIAL_LOCAL_RULES_FILENAME
    path.write_text(yaml.safe_dump({"courts": {"xxd": row}}), encoding="utf-8")
    return load_trial_local_rules(path)


def test_a_row_reads_as_the_openers_district_rule(tmp_path: Path) -> None:
    row = _row(
        reply_days=None,
        reply_from="opposition-due",
        motions={"trial-summary-judgment": {"opposition_days": 21, "reply_days": 14}},
    )
    assert _load(tmp_path, row) == {
        "xxd": DistrictRule(
            default=LocalRule(14, None, reply_from_due=True),
            by_moment={TrialMoment.summary_judgment: LocalRule(21, 14, reply_from_due=True)},
            in_force=date(2026, 1, 1),
        )
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "https://example.com/local-rules"},  # not the court's own site
        {"in_force": "2026-12-01"},  # read before it took force
        {"opposition_days": 0},
        {"reply_from": "service"},
        {"motions": {"trial-judgment": {"opposition_days": 14, "reply_days": 7}}},
        {"motions": {"trial-dismissal": {"opposition_days": 21}}},  # reply_days unstated
        {"notes": "an unknown key"},
    ],
)
def test_a_malformed_row_is_refused(tmp_path: Path, changes: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _load(tmp_path, _row(**changes))


def test_a_row_must_state_its_reply_period_even_as_none() -> None:
    row = _row()
    del row["reply_days"]
    with pytest.raises(ValidationError):
        TrialLocalRules.model_validate({"courts": {"xxd": row}})


def test_a_missing_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        load_trial_local_rules(tmp_path / TRIAL_LOCAL_RULES_FILENAME)


def test_every_district_the_watchlist_reads_has_a_committed_row() -> None:
    rules = load_trial_local_rules(_CONFIG / TRIAL_LOCAL_RULES_FILENAME)
    watchlist = load_ai_watchlist(_CONFIG / AI_WATCHLIST_FILENAME)
    courts = {case_id.partition("/")[0] for case_id, _ in survey_dockets(watchlist)}
    assert courts <= set(rules), sorted(courts - set(rules))


def test_the_committed_rows_carry_the_periods_their_rules_state() -> None:
    rules = load_trial_local_rules(_CONFIG / TRIAL_LOCAL_RULES_FILENAME)
    sj, dismissal = TrialMoment.summary_judgment, TrialMoment.dismissal
    day = date(2026, 11, 1)
    assert rules["cand"].for_motion(dismissal, day) == LocalRule(14, 7, reply_from_due=True)
    assert rules["nysd"].for_motion(sj, day) == LocalRule(14, 7)
    assert rules["flmd"].for_motion(dismissal, day) == LocalRule(21, None)
    assert rules["flmd"].for_motion(sj, day) == LocalRule(21, 14)
    assert rules["flmd"].for_motion(TrialMoment.preliminary_injunction, day) == LocalRule(14, None)
    assert rules["flnd"].for_motion(sj, day) == LocalRule(21, 7)
    assert rules["paed"].for_motion(sj, day) == LocalRule(14, None)
    assert rules["txed"].for_motion(sj, day) == LocalRule(21, 7)
    # Delaware's amended rules took force on September 1, 2026.
    assert rules["ded"].for_motion(dismissal, date(2026, 8, 31)) is None
    assert rules["ded"].for_motion(dismissal, date(2026, 9, 1)) == LocalRule(14, 7)
