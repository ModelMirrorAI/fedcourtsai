"""Same-question petitions: the TF-IDF match over stored questions-presented texts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.same_question import (
    Petition,
    QuestionIndex,
    same_question_petitions,
    status_on,
    terms,
    vide_agreement,
)

runner = CliRunner()

FELON = (
    "Whether 18 U.S.C. 922(g)(1), which bars firearm possession by anyone convicted "
    + "of a felony, violates the Second Amendment as applied to nonviolent offenders."
)
FELON_AGAIN = (
    "Whether the felon-in-possession ban of 18 U.S.C. 922(g)(1) violates the Second "
    + "Amendment as applied to a nonviolent offender."
)
PATENT = (
    "Whether claims directed to a method of detecting cell-free fetal DNA are patent "
    + "eligible under 35 U.S.C. 101 as a law of nature."
)
ARBITRATION = (
    "Whether the Federal Arbitration Act preempts a state rule barring waivers of "
    + "representative claims under the Private Attorneys General Act."
)
HABEAS = (
    "Whether a habeas petitioner must exhaust state remedies before raising an "
    + "ineffective assistance claim in a successive federal petition."
)


def _petition(
    case_id: str,
    text: str,
    *,
    docketed: date | None = date(2025, 1, 10),
    resolved: date | None = None,
    disposition: str | None = None,
    number: str | None = None,
) -> Petition:
    return Petition(
        case_id=case_id,
        docket_number=number or f"25-{case_id.rsplit('/', 1)[-1]}",
        docketed=docketed,
        resolved=resolved,
        disposition=disposition,
        text=text,
    )


def _index(*petitions: Petition) -> QuestionIndex:
    # The default ceiling ignores any term in over a fifth of the texts, which in a
    # five-text fixture drops every shared word; the ceiling is lifted so the
    # fixture measures the weighting instead.
    return QuestionIndex(petitions, max_df_share=1.0)


def test_terms_drop_function_words_and_add_pairs() -> None:
    assert terms("Whether the Court should overrule Chevron") == [
        "should",
        "overrule",
        "chevron",
        "should overrule",
        "overrule chevron",
    ]


def test_the_same_question_outscores_a_different_one() -> None:
    index = _index(
        _petition("scotus/1", FELON),
        _petition("scotus/2", FELON_AGAIN),
        _petition("scotus/3", PATENT),
        _petition("scotus/4", ARBITRATION),
        _petition("scotus/5", HABEAS),
    )
    scores = index.scores("scotus/1")
    assert max(scores, key=lambda case_id: scores[case_id]) == "scotus/2"
    assert scores["scotus/2"] > 2 * scores.get("scotus/3", 0.0)
    assert "scotus/1" not in scores


def test_an_identical_text_scores_one() -> None:
    index = _index(_petition("scotus/1", FELON), _petition("scotus/2", FELON))
    assert index.scores("scotus/1")["scotus/2"] == pytest.approx(1.0)


def test_a_term_in_too_many_texts_is_ignored() -> None:
    index = QuestionIndex(
        [_petition("scotus/1", FELON), _petition("scotus/2", FELON)], max_df_share=0.5
    )
    assert index.scores("scotus/1") == {}


def test_the_list_is_cut_to_the_cutoff() -> None:
    cutoff = date(2025, 3, 1)
    index = _index(
        _petition("scotus/1", FELON),
        _petition(
            "scotus/2",
            FELON,
            docketed=date(2025, 1, 2),
            resolved=date(2025, 2, 20),
            disposition="denied",
        ),
        _petition(
            "scotus/3",
            FELON,
            docketed=date(2025, 1, 3),
            resolved=date(2025, 4, 1),
            disposition="granted",
        ),
        _petition("scotus/4", FELON, docketed=date(2025, 3, 2)),
        _petition("scotus/5", FELON, docketed=None),
        _petition("scotus/6", HABEAS),
    )
    entries = same_question_petitions(index, "scotus/1", cutoff, threshold=0.5)
    # Docketed after the cutoff, or undated, is left out; a later grant reads as pending.
    assert [(e.case_id, e.status) for e in entries] == [
        ("scotus/2", "denied"),
        ("scotus/3", "pending"),
    ]
    assert all(e.score == 1.0 for e in entries)


def test_the_threshold_and_limit_bound_the_list() -> None:
    index = _index(*[_petition(f"scotus/{n}", FELON) for n in range(1, 6)])
    assert len(same_question_petitions(index, "scotus/1", date(2026, 1, 1), limit=2)) == 2
    assert same_question_petitions(index, "scotus/1", date(2026, 1, 1), threshold=1.01) == []


def test_status_is_pending_until_resolved() -> None:
    petition = _petition("scotus/1", FELON, resolved=date(2025, 5, 1), disposition="granted")
    assert status_on(petition, date(2025, 4, 30)) == "pending"
    assert status_on(petition, date(2025, 5, 1)) == "granted"


def test_the_vide_check_ranks_the_linked_petitions() -> None:
    index = _index(
        _petition("scotus/1", FELON, number="25-1"),
        _petition("scotus/2", FELON_AGAIN, number="25-2"),
        _petition("scotus/3", PATENT, number="25-3"),
        _petition("scotus/4", ARBITRATION, number="25-4"),
        _petition("scotus/5", PATENT, number="25-5"),
    )
    # 25-3's link is to a different question, and its best match is the unlinked copy.
    agreement = vide_agreement(index, {"scotus/1": ["25-2"], "scotus/3": ["25-4", "25-9", "25-3"]})
    assert agreement.petitions == 5
    assert agreement.linked == 2
    assert agreement.top1_linked == 1
    assert sum(agreement.link_scores.values()) == 2
    assert sum(n for n, _ in agreement.top1_by_score.values()) == 5


def test_the_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    assert runner.invoke(app, ["same-question"]).exit_code == 1  # no corpus yet
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass
    result = runner.invoke(app, ["same-question", "--docket", "25-1", "--as-of", "2026-01-01"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"lists": {"25-1": None}, "vide_check": None}
    assert runner.invoke(app, ["same-question", "--as-of", "Jan 1"]).exit_code == 2


def test_the_command_normalizes_and_bounds_its_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass
    result = runner.invoke(
        app, ["same-question", "--docket", "No. 25-123", "--as-of", "2026-01-01"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["lists"] == {"25-123": None}
    assert runner.invoke(app, ["same-question", "--threshold", "-0.1"]).exit_code == 2
