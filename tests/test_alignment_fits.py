from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.alignment_fits import (
    AlignmentFitError,
    calibration_of,
    frozen_fit,
    publish_fit,
)
from fedcourtsai.pipeline.alignment_score import (
    MIN_FIT_DECISIONS,
    fit_calibration,
    outcome_cases,
    score_readout,
)
from fedcourtsai.pipeline.merits_lineups import MeritsLineup
from fedcourtsai.schemas import (
    ALIGNMENT_FIT_FLOOR,
    AlignmentFits,
    AlignmentSideCode,
    AlignmentSideCodes,
    AlignmentTermFit,
    Judgment,
)

from .test_alignment_score import BENCH, _code, _positions, _record

runner = CliRunner()

FROZEN_ON = date(2026, 11, 3)


def _history(
    terms: dict[int, bool],
) -> tuple[list[AlignmentSideCode], list[MeritsLineup], dict[str, tuple[Judgment, date]]]:
    """Forty won 0.8 codes per Term, ideological 6-3s where the Term maps to True."""
    codes: list[AlignmentSideCode] = []
    lineups: list[MeritsLineup] = []
    judgments: dict[str, tuple[Judgment, date]] = {}
    n = 0
    for term, ideological in terms.items():
        for _ in range(40):
            n += 1
            code, lineup = _record(n, ideological=ideological, term=term)
            codes.append(code)
            lineups.append(lineup)
            judgments[code.case_id] = (Judgment.reversed, date(term + 1, 6, 1))
    return sorted(codes, key=lambda c: c.case_id), lineups, judgments


POSITIONS = _positions({2021: BENCH, 2022: BENCH, 2023: BENCH, 2024: BENCH})


def test_the_fit_matches_the_readouts_out_of_sample_reading() -> None:
    codes, lineups, judgments = _history({2022: True, 2023: False})
    fit = frozen_fit(codes, judgments, lineups, POSITIONS, term=2023, frozen_on=FROZEN_ON)
    readout = score_readout(
        codes, judgments, lineups, first_term=2023, last_term=2023, positions=POSITIONS
    )
    [term] = readout.terms
    assert term.votes_out_of_sample is not None
    assert fit.k == term.votes_out_of_sample.k
    assert fit.transform_decisions == 40
    assert fit.k_decisions == 40
    assert fit.contamination_risk == 40
    assert fit.latest_decision_read == date(2023, 6, 1)
    assert fit.positions == BENCH
    # Every OT2022 vote splits along the ordering, so the likelihood climbs to the grid's top.
    assert fit.k_at_grid_edge
    assert fit.consolidated == 0
    ahead = frozen_fit(codes, judgments, lineups, POSITIONS, term=2023, frozen_on=date(2023, 9, 1))
    assert ahead.k == fit.k and ahead.transform == fit.transform
    assert ahead.codes_digest == fit.codes_digest
    calibration = calibration_of(fit)
    assert calibration is not None
    # The transform fitted on OT2022's 40 won codes maps 0.8 to 41/42.
    assert calibration.apply(0.8) == pytest.approx(41 / 42)


def test_the_transform_matches_the_readouts_over_a_mixed_history() -> None:
    codes, lineups, judgments = _history({2022: True, 2023: False})
    # Mixed scores and outcomes, so the transform has more than one block.
    for i, code in enumerate(codes):
        if i % 3 == 0:
            judgments[code.case_id] = (Judgment.affirmed, judgments[code.case_id][1])
    codes = [c.model_copy(update={"score": 0.3 + (i % 5) / 10}) for i, c in enumerate(codes)]
    fit = frozen_fit(codes, judgments, lineups, POSITIONS, term=2024, frozen_on=FROZEN_ON)
    expected = fit_calibration(
        [(c.score, c.conservative_prevailed) for c in outcome_cases(codes, judgments)]
    )
    calibration = calibration_of(fit)
    assert expected is not None and calibration is not None
    assert len(expected.knots) > 1
    assert calibration.knots == expected.knots
    readout = score_readout(
        codes, judgments, lineups, first_term=2024, last_term=2024, positions=POSITIONS
    )
    [term] = readout.terms
    assert term.votes_out_of_sample is not None
    assert fit.k == term.votes_out_of_sample.k


def test_the_schema_fit_floor_is_the_fitters() -> None:
    assert ALIGNMENT_FIT_FLOOR == MIN_FIT_DECISIONS


def test_nothing_decided_on_or_after_the_term_opening_moves_the_fit() -> None:
    codes, lineups, judgments = _history({2022: True})
    before = frozen_fit(codes, judgments, lineups, POSITIONS, term=2023, frozen_on=FROZEN_ON)
    more_codes, more_lineups, more_judgments = _history({2022: True, 2023: False})
    # Another Term of codes and lineups, and a decision on the opening day itself.
    late = _code(999, score=0.1, term=2023)
    more_judgments[late.case_id] = (Judgment.reversed, date(2023, 10, 1))
    after = frozen_fit(
        sorted([*more_codes, late], key=lambda c: c.case_id),
        more_judgments,
        more_lineups,
        POSITIONS,
        term=2023,
        frozen_on=FROZEN_ON,
    )
    assert after == before


def test_the_digest_moves_with_any_code_the_transform_read() -> None:
    codes, lineups, judgments = _history({2022: True})
    fit = frozen_fit(codes, judgments, lineups, POSITIONS, term=2023, frozen_on=FROZEN_ON)
    moved = [codes[0].model_copy(update={"score": 0.7}), *codes[1:]]
    refit = frozen_fit(moved, judgments, lineups, POSITIONS, term=2023, frozen_on=FROZEN_ON)
    assert refit.codes_digest != fit.codes_digest


def test_below_the_fit_floor_neither_baseline_has_a_fit() -> None:
    codes, lineups, judgments = _history({2022: True})
    fit = frozen_fit(codes, judgments, lineups, POSITIONS, term=2022, frozen_on=FROZEN_ON)
    assert fit.transform is None
    assert fit.k is None
    assert fit.transform_decisions == 0
    assert fit.latest_decision_read is None
    assert calibration_of(fit) is None


def test_without_prior_positions_the_spread_is_not_fitted() -> None:
    codes, lineups, judgments = _history({2022: True})
    late_release = _positions({2022: BENCH}, published=date(2023, 10, 2))
    fit = frozen_fit(codes, judgments, lineups, late_release, term=2023, frozen_on=FROZEN_ON)
    assert fit.transform is not None
    assert fit.positions is None
    assert fit.k is None


def _fit(term: int, **changes: object) -> AlignmentTermFit:
    calibration = fit_calibration([(0.8, True)] * 40)
    assert calibration is not None
    fields: dict[str, object] = {
        "term": term,
        "opened": date(term, 10, 1),
        "frozen_on": date(term, 9, 1),
        "codes_digest": "0" * 64,
        "latest_decision_read": date(term, 6, 30),
        "transform": [list(k) for k in calibration.knots],
        "transform_decisions": 40,
        "k": 1.5,
        "k_decisions": 40,
        "k_at_grid_edge": False,
        "consolidated": 0,
        "positions": BENCH,
        "positions_source": "test",
        "contamination_risk": 40,
    }
    fields.update(changes)
    return AlignmentTermFit.model_validate(fields)


def test_publishing_is_append_only() -> None:
    first = publish_fit(None, _fit(2025))
    both = publish_fit(first, _fit(2024))
    assert [e.term for e in both.entries] == [2024, 2025]
    with pytest.raises(AlignmentFitError, match="never revised"):
        publish_fit(both, _fit(2025, k=2.0))


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"opened": date(2025, 10, 6)}, "1 October"),
        ({"latest_decision_read": date(2025, 10, 1)}, "before its Term opened"),
        ({"transform": [[0.5, 0.6], [0.4, 0.7]]}, "strictly increasing"),
        ({"transform": [[0.4, 0.7], [0.5, 0.6]]}, "non-decreasing"),
        ({"transform": [[0.4, 1.0]]}, "inside"),
        ({"positions": None}, "a spread is fitted only"),
        ({"contamination_risk": 41}, "cannot exceed"),
        ({"k": None, "k_at_grid_edge": True}, "needs a fitted spread"),
        ({"transform_decisions": 29, "contamination_risk": 29}, "fit floor's decisions"),
        ({"k_decisions": 29}, "fit floor's lineups"),
    ],
)
def test_the_schema_refuses_a_fit_that_reads_past_its_opening_or_is_malformed(
    changes: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        _fit(2025, **changes)


def test_the_file_holds_one_entry_per_term_in_order() -> None:
    with pytest.raises(ValidationError):
        AlignmentFits(entries=[_fit(2025), _fit(2024)])
    with pytest.raises(ValidationError):
        AlignmentFits(entries=[_fit(2025), _fit(2025)])


def _setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data = tmp_path / "data"
    codes_file = data / "merits-alignment" / "alignment-side-codes.json"
    codes_file.parent.mkdir(parents=True)
    codes_file.write_text(
        AlignmentSideCodes(entries=[_code(1, score=0.8)]).model_dump_json(indent=2)
    )
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    db = corpus.corpus_db_path(root)
    db.parent.mkdir(parents=True)
    with corpus.connect(db):
        pass
    return data


def test_the_cli_prints_the_entry_and_writes_the_file_append_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = _setup(tmp_path, monkeypatch)
    printed = runner.invoke(app, ["alignment-fit", "--term", "2026"])
    assert printed.exit_code == 0, printed.output
    entry = json.loads(printed.stdout.strip().splitlines()[-1])
    assert entry["term"] == 2026
    assert entry["transform"] is None
    fits_file = data / "merits-alignment" / "alignment-fits.json"
    assert not fits_file.exists()
    written = runner.invoke(app, ["alignment-fit", "--term", "2026", "--out", str(fits_file)])
    assert written.exit_code == 0, written.output
    assert [e.term for e in AlignmentFits.model_validate_json(fits_file.read_text()).entries] == [
        2026
    ]
    again = runner.invoke(app, ["alignment-fit", "--term", "2026", "--out", str(fits_file)])
    assert again.exit_code == 2
    assert "already fitted" in again.output


def test_the_cli_refuses_a_missing_codes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    result = runner.invoke(app, ["alignment-fit", "--term", "2026"])
    assert result.exit_code == 1
    assert "no side codes" in result.output
