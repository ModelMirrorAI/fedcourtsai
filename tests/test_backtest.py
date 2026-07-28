"""Back-testing harness: selection, scoring, the reference baselines, and the CLI."""

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.backtest import (
    BacktestFeatures,
    BacktestItem,
    BacktestPrediction,
    ConstantBacktester,
    PriorIndex,
    PriorVoteBacktester,
    default_backtesters,
    run_backtest,
    select_backtest_set,
)
from fedcourtsai.cli import app
from fedcourtsai.pipeline.outcome import is_machine_readable
from fedcourtsai.schemas import Backtest, Disposition
from fedcourtsai.serialize import read_model
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _row(case_id: str, disposition: Disposition | None, **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "disposition": disposition,
        "date_filed": date(2025, 1, 1),
        "date_decided": date(2026, 1, 1) if disposition else None,
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def _seed(db: Path, rows: list[corpus.CorpusRow]) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


# --- selection ----------------------------------------------------------------


def test_select_keeps_only_machine_readable_resolved(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row("ca9/1", Disposition.granted),
            _row("ca9/2", Disposition.denied),
            _row("ca9/3", None),  # unresolved
            _row("ca9/4", Disposition.other),  # decided but unclassified
        ],
    )
    with corpus.connect(db) as conn:
        items = select_backtest_set(conn)
    assert [i.features.case_id for i in items] == ["ca9/1", "ca9/2"]
    assert items[0].actual_disposition == Disposition.granted


def test_select_features_hide_the_outcome(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, [_row("ca9/1", Disposition.granted, opinion_text="grant", summary="won")])
    with corpus.connect(db) as conn:
        item = select_backtest_set(conn)[0]
    # Features carry no field that reveals the disposition (no opinion/summary/
    # date_decided, and no reporter citations — those exist only once decided).
    assert set(vars(item.features)) == {
        "case_id",
        "court",
        "topic",
        "judges",
        "date_filed",
        "year",
    }


def test_select_court_and_limit_filters(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row("ca1/1", Disposition.granted, court="ca1"),
            _row("ca9/1", Disposition.granted),
            _row("ca9/2", Disposition.denied),
        ],
    )
    with corpus.connect(db) as conn:
        assert [i.features.case_id for i in select_backtest_set(conn, court="ca9")] == [
            "ca9/1",
            "ca9/2",
        ]
        assert len(select_backtest_set(conn, limit=1)) == 1


# --- reference baselines ------------------------------------------------------


def _features(case_id: str = "ca9/1", **kw: object) -> BacktestFeatures:
    # year=2026 puts the trial after the 2025 priors `_row` seeds (their year is
    # date_filed's, the best signal a non-SCOTUS row carries).
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "topic": None,
        "judges": (),
        "date_filed": date(2025, 1, 1),
        "year": 2026,
    }
    base.update(kw)
    return BacktestFeatures(**base)  # type: ignore[arg-type]


def test_constant_backtester_is_constant() -> None:
    bt = ConstantBacktester(id="constant-denied", disposition=Disposition.denied)
    pred = bt.predict(_features())
    assert pred == BacktestPrediction(Disposition.denied, 0.0)
    granted = ConstantBacktester(id="c", disposition=Disposition.granted).predict(_features())
    assert granted.probability_granted == 1.0


def test_prior_vote_majority_and_granted_share(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row("ca9/10", Disposition.granted, judges=["smith"]),
            _row("ca9/11", Disposition.granted, judges=["smith"]),
            _row("ca9/12", Disposition.denied, judges=["smith"]),
        ],
    )
    with corpus.connect(db) as conn:
        bt = PriorVoteBacktester(conn)
        pred = bt.predict(_features("ca9/99", judges=("smith",)))
    # 2 granted / 1 denied among the priors -> majority granted, P(granted)=2/3.
    assert pred.predicted_disposition == Disposition.granted
    assert pred.probability_granted == 2 / 3


def test_prior_vote_excludes_the_case_under_test(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    # The only resolved case is the one being predicted. Its own year equals the
    # trial's, and the strict decided_before cutoff excludes the cutoff year —
    # so the vote can never retrieve the case itself (or its contemporaries).
    _seed(db, [_row("ca9/1", Disposition.granted, judges=["smith"])])
    with corpus.connect(db) as conn:
        pred = PriorVoteBacktester(conn).predict(_features("ca9/1", judges=("smith",), year=2025))
    assert pred == BacktestPrediction(Disposition.denied, 0.0)


def test_prior_vote_never_consults_later_history(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            # Earlier than the 2026 trial (year = date_filed 2025): the only vote.
            _row("ca9/10", Disposition.denied, judges=["smith"]),
            # Later than the trial: hindsight, never consulted.
            _row("ca9/11", Disposition.granted, judges=["smith"], date_filed=date(2027, 1, 1)),
            _row("ca9/12", Disposition.granted, judges=["smith"], date_filed=date(2027, 2, 1)),
        ],
    )
    with corpus.connect(db) as conn:
        pred = PriorVoteBacktester(conn).predict(_features("ca9/99", judges=("smith",)))
    # Unmasked, the 2-1 granted majority would win; time-masked it must not.
    assert pred == BacktestPrediction(Disposition.denied, 0.0)


def test_prior_vote_without_a_replay_clock_falls_back_to_the_floor(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, [_row("ca9/10", Disposition.granted, judges=["smith"])])
    with corpus.connect(db) as conn:
        pred = PriorVoteBacktester(conn).predict(_features("ca9/99", judges=("smith",), year=None))
    # No derivable year -> no prior can be proven earlier -> the conservative floor.
    assert pred == BacktestPrediction(Disposition.denied, 0.0)


def test_prior_vote_builds_its_index_once(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, [_row("ca9/1", Disposition.granted, judges=["smith"])])
    with corpus.connect(db) as conn:
        bt = PriorVoteBacktester(conn)
        bt.predict(_features("ca9/99", judges=("smith",)))
        built = bt._index
        bt.predict(_features("ca9/98", judges=("smith",)))
    # The whole point of the index: one resolved-slice scan per replay, not per trial.
    assert built is not None
    assert bt._index is built


def test_prior_vote_never_predicts_an_unscoreable_label(tmp_path: Path) -> None:
    # `other` is decided-but-unclassified. The scored set drops it, so a vote for
    # it is wrong by construction — the pool must apply the same bar the scored
    # set does, even when `other` is the outright majority of the history.
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row(f"ca9/{i}", Disposition.other, judges=["smith"], date_decided=date(2026, 1, i))
            for i in range(1, 6)
        ]
        + [_row("ca9/90", Disposition.denied, judges=["smith"])],
    )
    with corpus.connect(db) as conn:
        pred = PriorVoteBacktester(conn).predict(_features("ca9/99", judges=("smith",)))
    # 5 `other` vs 1 denied: a pool that admitted `other` would vote for it.
    assert pred.predicted_disposition == Disposition.denied
    assert pred.probability_granted == 0.0


def test_prior_vote_reads_the_population_not_the_most_recent_slice(tmp_path: Path) -> None:
    # No judges, so relevance falls back to most-recent-decision order — the
    # SCOTUS case, where nothing narrows the pool. A capped vote reads the top of
    # that order and inherits its composition; the population says the opposite.
    # 25 denied decided early, 21 granted decided late, all before the trial.
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [_row(f"ca9/d{i}", Disposition.denied, date_decided=date(2025, 1, 1)) for i in range(25)]
        + [
            _row(f"ca9/g{i}", Disposition.granted, date_decided=date(2025, 12, 1))
            for i in range(21)
        ],
    )
    with corpus.connect(db) as conn:
        uncapped = PriorVoteBacktester(conn).predict(_features("ca9/99"))
        capped = PriorVoteBacktester(conn, limit=20).predict(_features("ca9/99"))
    # The population is 25 denied / 21 granted, so the honest majority is denied.
    assert uncapped.predicted_disposition == Disposition.denied
    assert uncapped.probability_granted == 21 / 46
    # The 20 most recently decided are all grants — the sampling defect, pinned
    # so the uncapped default cannot regress back to it unnoticed.
    assert capped.predicted_disposition == Disposition.granted
    assert capped.probability_granted == 1.0


# --- prior index parity with retrieve_priors -----------------------------------


def test_prior_index_matches_retrieve_priors(tmp_path: Path) -> None:
    """The index must reproduce `retrieve_priors` exactly — same rows, same order.

    Covers every semantic branch: pure recency order (no features), required judge
    overlap, required citation overlap, both filters combined (score sums), the
    decided_before cutoff (alone and with overlap filters; a year-less row is
    excluded under any cutoff), an undated-but-resolved row (sorts after dated
    ones), unresolved rows excluded, a foreign court, and a no-match query.
    """
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row(
                "ca9/1",
                Disposition.granted,
                judges=["alpha", "beta"],
                citations=["1 U.S. 1"],
                date_decided=date(2026, 3, 1),
            ),
            _row(
                "ca9/2",
                Disposition.denied,
                judges=["beta"],
                citations=["1 U.S. 1", "2 U.S. 2"],
                date_filed=date(2024, 1, 1),
                date_decided=date(2026, 2, 1),
            ),
            _row(
                "ca9/3",
                Disposition.dismissed,
                judges=["gamma"],
                date_filed=date(2023, 1, 1),
                date_decided=date(2026, 1, 5),
            ),
            # Resolved but undated: recency sorts it after every dated row, and
            # no year is derivable, so any decided_before cutoff excludes it.
            _row("ca9/4", Disposition.denied, judges=["alpha"], date_filed=None, date_decided=None),
            # Unresolved: never a prior.
            _row("ca9/5", None, judges=["alpha"]),
            # Another court: never mixed into ca9 retrievals.
            _row("ca1/6", Disposition.granted, court="ca1", judges=["alpha"]),
            # Decided but never disposition-labeled: `retrieve_priors` returns it
            # (a decision date closes a case), the index deliberately does not
            # (the prior-vote baseline needs a label to vote with) — one of the
            # two designed asymmetries between the retrieval paths.
            _row("ca9/7", None, judges=["alpha"], date_decided=date(2026, 4, 1)),
            # Decided but unclassified (`other`): also returned by
            # `retrieve_priors` and also withheld by the index — the scored set
            # drops `other`, so a vote for it could never be correct. The second
            # designed asymmetry.
            _row(
                "ca9/8",
                Disposition.other,
                judges=["alpha"],
                date_filed=date(2023, 6, 1),
                date_decided=date(2026, 5, 1),
            ),
        ],
    )
    queries: list[tuple[str, tuple[str, ...], tuple[str, ...], int | None]] = [
        ("ca9", (), (), None),
        ("ca9", ("alpha",), (), None),
        ("ca9", ("alpha", "gamma"), (), None),
        ("ca9", (), ("1 U.S. 1",), None),
        ("ca9", (), ("2 U.S. 2",), None),
        ("ca9", ("beta",), ("1 U.S. 1",), None),
        ("ca9", ("nobody",), (), None),
        ("ca1", ("alpha",), (), None),
        ("nowhere", (), (), None),
        ("ca9", (), (), 2026),
        ("ca9", (), (), 2024),
        ("ca9", (), (), 1900),
        ("ca9", ("alpha", "beta"), (), 2026),
        ("ca9", ("beta",), ("1 U.S. 1",), 2025),
    ]
    with corpus.connect(db) as conn:
        index = PriorIndex.build(conn)
        for court, judges, citations, decided_before in queries:
            # `None` is what the production caller passes, so parity has to hold
            # there and not only at the truncated limits.
            for limit in (1, 3, 10, None):
                # Parity holds over the disposition-labeled subset: fetch wide,
                # drop the label-less rows `retrieve_priors` alone returns, then
                # truncate — so limits compare like against like.
                wide = corpus.retrieve_priors(
                    conn,
                    corpus.PriorQuery(
                        court=court,
                        judges=list(judges),
                        citations=list(citations),
                        decided_before=decided_before,
                        resolved_only=True,
                    ),
                    limit=50,
                )
                expected = [
                    r
                    for r in wide
                    if r.disposition is not None and is_machine_readable(Disposition(r.disposition))
                ][:limit]
                got = index.top(court, judges, citations, limit, decided_before=decided_before)
                assert [c.case_id for c in got] == [r.case_id for r in expected], (
                    court,
                    judges,
                    citations,
                    decided_before,
                    limit,
                )
        # Both asymmetries, pinned: the unlabeled decided row and the `other`
        # row retrieve through `retrieve_priors` but never through the index.
        full = corpus.retrieve_priors(conn, corpus.PriorQuery(court="ca9"), limit=50)
        indexed = [c.case_id for c in index.top("ca9", (), (), 50)]
        assert "ca9/7" in [r.case_id for r in full] and "ca9/7" not in indexed
        assert "ca9/8" in [r.case_id for r in full] and "ca9/8" not in indexed


# --- scoring ------------------------------------------------------------------


def _item(case_id: str, actual: Disposition) -> BacktestItem:
    return BacktestItem(_features(case_id), actual)


def test_run_backtest_scores_and_ranks() -> None:
    items = [
        _item("ca9/1", Disposition.denied),
        _item("ca9/2", Disposition.denied),
        _item("ca9/3", Disposition.granted),
    ]
    always_denied = ConstantBacktester(id="denied", disposition=Disposition.denied)
    always_granted = ConstantBacktester(id="granted", disposition=Disposition.granted)
    report = run_backtest([always_granted, always_denied], items)
    assert report.predictors_evaluated == 2
    assert report.events_scored == 3
    # always-denied gets 2/3 dispositions right; always-granted 1/3 -> denied ranks first.
    assert [e.predictor_id for e in report.entries] == ["denied", "granted"]
    denied = report.entries[0]
    assert denied.rank == 1
    assert denied.accuracy == 2 / 3
    assert denied.granted_accuracy == 2 / 3
    # Brier: denied predicts P=0; two actual-denied (0) + one actual-granted (1) -> 1/3.
    assert denied.mean_brier_score == 1 / 3


def test_run_backtest_empty_is_zero_count() -> None:
    report = run_backtest([], [])
    assert report.predictors_evaluated == 0
    assert report.events_scored == 0
    assert report.entries == []


def test_default_backtesters_are_the_reference_baselines(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        ids = [bt.id for bt in default_backtesters(conn)]
    assert ids == ["constant-denied", "prior-vote"]


# --- CLI ----------------------------------------------------------------------


def test_cli_writes_valid_report(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    out = tmp_path / "backtest.json"
    result = runner.invoke(app, ["backtest", "--out", str(out)])
    assert result.exit_code == 0, result.output
    report = read_model(out, Backtest)
    # Every machine-readable resolved fixture case is a back-test trial (the
    # fixture carries no `other`-disposition rows, so resolved == scored).
    expected = sum(1 for c in fixture.FIXTURE_CASES if c.disposition is not None)
    assert report.events_scored == expected
    assert report.predictors_evaluated == 2
    assert {e.predictor_id for e in report.entries} == {"constant-denied", "prior-vote"}
    # Deterministic: a second run reproduces the file byte for byte.
    first = out.read_text()
    runner.invoke(app, ["backtest", "--out", str(out)])
    assert out.read_text() == first


def test_cli_missing_corpus_writes_empty_report(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"  # no corpus.db created
    out = tmp_path / "backtest.json"
    result = runner.invoke(
        app,
        ["backtest", "--out", str(out)],
        env={"FEDCOURTS_CORPUS_ROOT": str(corpus_root)},
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, Backtest)
    assert report.predictors_evaluated == 0
    assert report.events_scored == 0
    assert report.entries == []


# --- the always-deny floor, per court ------------------------------------------
#
# Raw accuracy on this set is close to meaningless on its own: a constant
# predictor scores its slice's base rate exactly, and the pooled figure is
# dominated by whichever court happens to have the most resolved events. The
# per-court floor is what separates skill from arithmetic.


def _court_item(court: str, docket: int, actual: Disposition) -> BacktestItem:
    return BacktestItem(
        features=_features(f"{court}/{docket}", court=court),
        actual_disposition=actual,
    )


def test_a_constant_predictor_scores_exactly_the_floor_everywhere() -> None:
    """Lift zero, overall and in every court — the signal that it learned nothing.

    The property that makes the floor worth reporting: without it, this predictor's
    accuracy is indistinguishable from a real one's.
    """
    items = [_court_item("ca9", i, Disposition.denied) for i in range(7)]
    items += [_court_item("ca9", 100 + i, Disposition.granted) for i in range(3)]
    items += [_court_item("scotus", i, Disposition.denied) for i in range(4)]

    report = run_backtest(
        [ConstantBacktester(id="constant-denied", disposition=Disposition.denied)], items
    )
    entry = report.entries[0]
    assert entry.accuracy == entry.always_denied_accuracy
    assert entry.lift_over_always_denied == 0.0
    for court in entry.courts:
        assert court.accuracy == court.always_denied_accuracy
        assert court.lift_over_always_denied == 0.0
    # And the floors genuinely differ by court, so this is not a degenerate case.
    assert {c.court: round(c.always_denied_accuracy, 3) for c in entry.courts} == {
        "ca9": 0.7,
        "scotus": 1.0,
    }


def test_the_per_court_cut_exposes_a_failure_the_pooled_figure_hides() -> None:
    """A predictor can be at the floor on a large court and far below it on a small
    one, and the pooled lift averages the failure away.

    This is the shape the real corpus takes: one court supplies most of the resolved
    events at a near-zero floor, so a pooled number is effectively that court's and
    says nothing about the population actually predicted.
    """
    # 90 ca4 events that are never `denied` (floor 0), plus 10 SCOTUS events that
    # almost always are (floor 0.9).
    items = [_court_item("ca4", i, Disposition.dismissed) for i in range(90)]
    items += [_court_item("scotus", i, Disposition.denied) for i in range(9)]
    items.append(_court_item("scotus", 99, Disposition.granted))

    report = run_backtest(
        [ConstantBacktester(id="constant-granted", disposition=Disposition.granted)], items
    )
    entry = report.entries[0]
    by_court = {c.court: c for c in entry.courts}
    # On SCOTUS it is catastrophic against that court's own floor...
    assert by_court["scotus"].always_denied_accuracy == 0.9
    assert by_court["scotus"].lift_over_always_denied == pytest.approx(-0.8)
    # ...but the pooled lift is an order of magnitude smaller, because ca4's 90
    # events carry a floor of zero and dominate the average.
    pooled = entry.lift_over_always_denied
    assert pooled is not None
    assert pooled == pytest.approx(-0.08)
    assert pooled > by_court["scotus"].lift_over_always_denied


def test_lift_is_presentational_and_never_reorders_entries() -> None:
    """Ranking stays on accuracy then Brier. The pooled floor mixes outcome
    vocabularies, so ordering on it would promote an incomparable number."""
    items = [_court_item("scotus", i, Disposition.denied) for i in range(9)]
    items.append(_court_item("scotus", 99, Disposition.granted))

    report = run_backtest(
        [
            ConstantBacktester(id="b-granted", disposition=Disposition.granted),
            ConstantBacktester(id="a-denied", disposition=Disposition.denied),
        ],
        items,
    )
    # a-denied is at the floor (lift 0), b-granted far below it — and accuracy puts
    # them in that same order here, so assert the ranking key rather than the outcome.
    assert [e.predictor_id for e in report.entries] == ["a-denied", "b-granted"]
    assert [e.rank for e in report.entries] == [1, 2]
    assert report.entries[0].accuracy > report.entries[1].accuracy


def test_courts_are_id_ordered_and_cover_every_scored_court() -> None:
    items = [_court_item(c, 1, Disposition.denied) for c in ("scotus", "ca1", "ca9")]
    entry = run_backtest(
        [ConstantBacktester(id="c", disposition=Disposition.denied)], items
    ).entries[0]
    assert [c.court for c in entry.courts] == ["ca1", "ca9", "scotus"]
    assert sum(c.events_scored for c in entry.courts) == entry.events_scored
