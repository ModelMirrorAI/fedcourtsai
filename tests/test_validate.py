"""Corpus-integrity + referential validation: the checks, the library, and the CLI."""

import sqlite3
from datetime import date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    CorpusScopeAudit,
    CorpusValidation,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    FlagCategory,
    Outcome,
    PredictableEvent,
    Prediction,
    SeedProgress,
    UsageRole,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.validate import (
    CHECK_CASE_DATES,
    CHECK_DOMAIN_VALUES,
    CHECK_EVALUATION_TARGETS,
    CHECK_LEDGER_EVENTS_IN_GIT,
    CHECK_LEDGER_REFERENCES,
    CHECK_NO_DUPLICATES,
    CHECK_REQUIRED_COLUMNS,
    CHECK_ROW_COUNT_MONOTONIC,
    CHECK_SEED_CURSOR,
    CHECK_SNAPSHOT_NOT_FUTURE,
    check_ledger_events_in_git,
    check_no_duplicates,
    run_corpus_validation,
    run_ledger_referential_checks,
    run_scope_audit,
    validate_ledger,
)

runner = CliRunner()

TODAY = date(2026, 6, 27)


def _verdict_by_check(verdict: CorpusValidation) -> dict[str, bool]:
    return {c.name: c.passed for c in verdict.checks}


def _seed_corpus(db: Path) -> None:
    """A small, clean corpus: one case, one event, one (past-dated) snapshot."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="ca9/1", court="ca9", disposition=Disposition.granted)],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-motion-stay",
                    case_id="ca9/1",
                    court="ca9",
                    kind=EventKind.motion,
                )
            ],
        )
        corpus.upsert_snapshot(conn, "ca9/1", date(2026, 1, 1), {"docket": "ca9/1"})


def _open_petition(
    case_id: str, court: str = "scotus", *, resolved: bool = False
) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id="evt-petition-disposition",
        case_id=case_id,
        court=court,
        kind=EventKind.petition,
        resolved=resolved,
    )


def _seed_scope_corpus(db: Path) -> None:
    """A corpus exercising every scope-audit branch: in-scope, both exclusions
    (recoverable + bare), a resolved exclusion, and a non-SCOTUS open event."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # Stale-unresolvable (#333), recoverable — carries a citation signal.
                corpus.CorpusRow(
                    case_id="scotus/1004191",
                    court="scotus",
                    docket_number="01-7700",
                    citations=["537 U.S. 1"],
                ),
                # Stale-unresolvable (#333), bare — no recoverability signal.
                corpus.CorpusRow(case_id="scotus/1004289", court="scotus", docket_number="93-7515"),
                # Historical-mandatory (#309), bare.
                corpus.CorpusRow(case_id="scotus/1001931", court="scotus", docket_number="801"),
                # In scope: a recent open petition — counts toward the denominator only.
                corpus.CorpusRow(case_id="scotus/2400001", court="scotus", docket_number="24-101"),
                # Out of scope but already resolved — must not be counted (not open).
                corpus.CorpusRow(case_id="scotus/1005000", court="scotus", docket_number="00-100"),
                # A lower court open event — excluded (predicates are SCOTUS-only).
                corpus.CorpusRow(case_id="ca9/9", court="ca9", docket_number="9"),
            ],
        )
        corpus.upsert_events(
            conn,
            [
                _open_petition("scotus/1004191"),
                _open_petition("scotus/1004289"),
                _open_petition("scotus/1001931"),
                _open_petition("scotus/2400001"),
                _open_petition("scotus/1005000", resolved=True),
                _open_petition("ca9/9", court="ca9"),
            ],
        )


def test_run_scope_audit_skips_without_corpus(tmp_path: Path) -> None:
    audit = run_scope_audit(corpus_db_path=tmp_path / "absent.db")
    assert audit.skipped is True and audit.exclusions == []


def test_run_scope_audit_tallies_open_exclusions_with_recoverable_split(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed_scope_corpus(db)
    audit = run_scope_audit(corpus_db_path=db)

    assert audit.skipped is False
    # Denominator: the four open SCOTUS events (the resolved one and the ca9 one excluded).
    assert audit.scotus_open_events == 4
    by_reason = {e.reason: e for e in audit.exclusions}
    assert set(by_reason) == {
        "pre-1925 mandatory-jurisdiction matter (#309)",
        "stale unresolvable old SCOTUS petition (#333)",
    }
    stale = by_reason["stale unresolvable old SCOTUS petition (#333)"]
    assert (stale.cases, stale.open_events, stale.recoverable) == (2, 2, 1)
    assert stale.sample_cases == ["scotus/1004191", "scotus/1004289"]
    hist = by_reason["pre-1925 mandatory-jurisdiction matter (#309)"]
    assert (hist.cases, hist.open_events, hist.recoverable) == (1, 1, 0)
    # The one in-scope open event (recent Term 24-101) lands in the unclassified breakdown.
    assert {u.reason: u.open_events for u in audit.unclassified} == {
        "recent or current Term (legitimately pending)": 1
    }


def test_run_scope_audit_buckets_unclassified_by_reason(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # recent Term, unresolved -> "recent or current Term"
                corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="24-101"),
                # original-jurisdiction docket the parser can't read -> "Term not parseable"
                corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="22O141"),
                # open event but a disposition is recorded -> "carries a disposition signal"
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="10-5",
                    disposition=Disposition.denied,
                ),
                # no docket number at all -> "no docket number"
                corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number=""),
            ],
        )
        corpus.upsert_events(conn, [_open_petition(f"scotus/{n}") for n in (1, 2, 3, 4)])
    audit = run_scope_audit(corpus_db_path=db)

    assert audit.exclusions == []  # none match an exclusion predicate
    assert {u.reason: u.open_events for u in audit.unclassified} == {
        "recent or current Term (legitimately pending)": 1,
        "docket Term not parseable (a format the predicate skips)": 1,
        "carries a disposition signal (open despite a recorded decision)": 1,
        "no docket number": 1,
    }


def _write_event(data_root: Path, court: str, docket: int, event: str) -> Path:
    """Write an ``event.yaml`` so the event exists in the git ledger tree."""
    ep = CasePaths(data_root, court, docket).event(event)
    write_yaml(
        ep.event_file,
        PredictableEvent(
            event_id=event, case_id=f"{court}/{docket}", kind=EventKind.motion, title="Motion"
        ),
    )
    return ep.event_file


def _write_outcome(data_root: Path, court: str, docket: int, event: str) -> Path:
    ep = CasePaths(data_root, court, docket).event(event)
    outcome = Outcome(
        case_id=f"{court}/{docket}",
        event_id=event,
        resolved_at=date(2026, 1, 2),
        actual_disposition=Disposition.granted,
        actual_granted=1,
    )
    write_json(ep.outcome, outcome)
    return ep.outcome


def _write_prediction(data_root: Path, court: str, docket: int, event: str, predictor: str) -> None:
    ep = CasePaths(data_root, court, docket).event(event)
    prediction = Prediction(
        case_id=f"{court}/{docket}",
        event_id=event,
        predictor_id=predictor,
        engine=Engine.claude_code,
        run_id="2026-01-01T00-00-00Z",
        created_at=datetime(2026, 1, 1),
        input_snapshot="record/snapshots/2026-01-01.json",
        granted=1,
        probability=0.9,
        predicted_disposition=Disposition.granted,
    )
    write_json(ep.prediction(predictor, "2026-01-01T00-00-00Z"), prediction)


def _write_evaluation(
    data_root: Path, court: str, docket: int, event: str, predictor: str, evaluator: str
) -> None:
    ep = CasePaths(data_root, court, docket).event(event)
    evaluation = Evaluation(
        case_id=f"{court}/{docket}",
        event_id=event,
        predictor_id=predictor,
        evaluator_id=evaluator,
        engine=Engine.claude_code,
        run_id="2026-02-01T00-00-00Z",
        created_at=datetime(2026, 2, 1),
        correct=1,
    )
    write_json(ep.evaluation(evaluator, predictor, "2026-02-01T00-00-00Z"), evaluation)


def _run(db: Path, data_root: Path, **kw: object) -> CorpusValidation:
    return run_corpus_validation(
        corpus_db_path=db,
        data_root=data_root,
        seed_cursor=kw.get("seed_cursor"),  # type: ignore[arg-type]
        today=kw.get("today", TODAY),  # type: ignore[arg-type]
        baseline_count=kw.get("baseline_count"),  # type: ignore[arg-type]
    )


# --- clean corpus -------------------------------------------------------------


def test_clean_corpus_passes(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    _write_prediction(data_root, "ca9", 1, "evt-motion-stay", "p1")
    _write_evaluation(data_root, "ca9", 1, "evt-motion-stay", "p1", "e1")

    verdict = _run(db, data_root, baseline_count=1)
    assert verdict.ok
    assert not verdict.skipped
    assert verdict.corpus_rows == 1
    assert verdict.corpus_events == 1
    assert all(c.passed for c in verdict.checks)


# --- absent corpus ------------------------------------------------------------


def test_absent_corpus_is_skipped(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"  # never created
    verdict = _run(db, tmp_path / "data")
    assert verdict.skipped
    assert verdict.ok
    assert verdict.checks == []


# --- B: append-only row count -------------------------------------------------


def test_non_monotonic_row_count_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)  # one row
    verdict = _run(db, tmp_path / "data", baseline_count=5)
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_ROW_COUNT_MONOTONIC] is False


def test_no_baseline_is_a_pass(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    verdict = _run(db, tmp_path / "data")  # no baseline
    assert _verdict_by_check(verdict)[CHECK_ROW_COUNT_MONOTONIC] is True


# --- B: future-dated snapshot -------------------------------------------------


def test_future_dated_snapshot_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "ca9/1", date(2099, 1, 1), {"docket": "ca9/1"})
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_SNAPSHOT_NOT_FUTURE] is False


# --- B: required columns ------------------------------------------------------


def test_empty_court_fails_required_columns(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute("UPDATE cases SET court = '' WHERE case_id = 'ca9/1'")
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_REQUIRED_COLUMNS] is False


# --- C: orphan ledger references ----------------------------------------------


def test_orphan_outcome_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    # An outcome for an event the corpus does not define.
    _write_outcome(data_root, "ca9", 1, "evt-motion-ghost")
    verdict = _run(db, data_root)
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_LEDGER_REFERENCES] is False


def test_orphan_case_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    _write_outcome(data_root, "ca9", 999, "evt-motion-stay")  # case not in corpus
    verdict = _run(db, data_root)
    assert _verdict_by_check(verdict)[CHECK_LEDGER_REFERENCES] is False


# --- C: evaluation targets a prediction ---------------------------------------


def test_evaluation_without_prediction_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    # An evaluation of p1, but no prediction by p1 for this event.
    _write_evaluation(data_root, "ca9", 1, "evt-motion-stay", "p1", "e1")
    verdict = _run(db, data_root)
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_EVALUATION_TARGETS] is False


# --- C: seed cursor reconciliation --------------------------------------------


def test_seed_cursor_desync_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)  # only ca9 has rows
    cursor = SeedProgress.model_validate({"courts": {"ca9": {"offset": 1}, "ca1": {"offset": 100}}})
    verdict = _run(db, tmp_path / "data", seed_cursor=cursor)
    assert not verdict.ok
    cursor_check = next(c for c in verdict.checks if c.name == CHECK_SEED_CURSOR)
    assert not cursor_check.passed
    assert any("ca1" in p for p in cursor_check.problems)


def test_seed_cursor_reconciles(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    cursor = SeedProgress.model_validate({"courts": {"ca9": {"offset": 1}}})
    verdict = _run(db, tmp_path / "data", seed_cursor=cursor)
    assert _verdict_by_check(verdict)[CHECK_SEED_CURSOR] is True


# --- B: case-date ordering ----------------------------------------------------


def test_future_decided_date_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute("UPDATE cases SET date_decided = '2099-01-01' WHERE case_id = 'ca9/1'")
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_CASE_DATES] is False


def test_decided_before_filed_within_baseline_passes(tmp_path: Path) -> None:
    # A `date_decided < date_filed` row is a faithful upstream quirk (#171); within
    # the accepted baseline the check passes but still records the true count, so the
    # monitor can read it.
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET date_filed = '2026-02-01', date_decided = '2026-01-01' "
            "WHERE case_id = 'ca9/1'"
        )
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    check = next(c for c in verdict.checks if c.name == CHECK_CASE_DATES)
    assert check.passed
    assert check.failures == 1
    assert verdict.ok


def test_decided_before_filed_above_baseline_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A material climb above the accepted floor must still fail — the regression
    # signal #171 relies on. Drop the baseline to 0 so a single bad row trips it.
    monkeypatch.setattr("fedcourtsai.validate._CASE_DATE_ORDER_BASELINE", 0)
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET date_filed = '2026-02-01', date_decided = '2026-01-01' "
            "WHERE case_id = 'ca9/1'"
        )
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_CASE_DATES] is False


def test_ordered_dates_pass(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET date_filed = '2026-01-01', date_decided = '2026-02-01' "
            "WHERE case_id = 'ca9/1'"
        )
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert _verdict_by_check(verdict)[CHECK_CASE_DATES] is True


# --- B: domain vocabulary + tracked courts ------------------------------------


def test_unknown_disposition_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute("UPDATE cases SET disposition = 'bogus' WHERE case_id = 'ca9/1'")
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_DOMAIN_VALUES] is False


def test_untracked_court_fails_when_set_supplied(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)  # corpus court is ca9
    verdict = run_corpus_validation(
        corpus_db_path=db,
        data_root=tmp_path / "data",
        seed_cursor=None,
        today=TODAY,
        tracked_courts=["ca1"],  # ca9 is not tracked
    )
    assert not verdict.ok
    check = next(c for c in verdict.checks if c.name == CHECK_DOMAIN_VALUES)
    assert not check.passed
    assert any("ca9/1" in p for p in check.problems)


def test_tracked_court_passes(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    verdict = run_corpus_validation(
        corpus_db_path=db,
        data_root=tmp_path / "data",
        seed_cursor=None,
        today=TODAY,
        tracked_courts=["ca9"],
    )
    assert _verdict_by_check(verdict)[CHECK_DOMAIN_VALUES] is True


def test_no_tracked_set_skips_court_membership(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)  # ca9, which no court set is supplied to vet
    verdict = _run(db, tmp_path / "data")  # tracked_courts defaults to None
    assert _verdict_by_check(verdict)[CHECK_DOMAIN_VALUES] is True


# --- B: duplicate hardening (snapshots + whitespace-variant ids) --------------


def test_duplicate_snapshot_fails(tmp_path: Path) -> None:
    # The (case_id, snapshot_date) primary key blocks an exact duplicate through
    # the normal write path, so simulate the constraint-free rebuild the check
    # defends against: bare tables with no unique constraints, then a forged dup.
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        "CREATE TABLE cases (case_id TEXT, court TEXT);"
        "CREATE TABLE events (case_id TEXT, event_id TEXT);"
        "CREATE TABLE snapshots (case_id TEXT, snapshot_date TEXT, payload TEXT);"
    )
    conn.execute("INSERT INTO cases VALUES ('ca9/1', 'ca9')")
    conn.executemany(
        "INSERT INTO snapshots VALUES (?, ?, ?)",
        [("ca9/1", "2026-01-01", "{}"), ("ca9/1", "2026-01-01", "{}")],
    )
    conn.commit()
    check = check_no_duplicates(conn)
    conn.close()
    assert not check.passed
    assert any("snapshot" in p for p in check.problems)


def test_whitespace_variant_case_id_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        # A second case id that is the same id but for a trailing space: a distinct
        # primary key, yet one logical id that collides on every referential join.
        conn.execute("INSERT INTO cases (case_id, court) VALUES ('ca9/1 ', 'ca9')")
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    check = next(c for c in verdict.checks if c.name == CHECK_NO_DUPLICATES)
    assert not check.passed
    assert any("whitespace-variant" in p for p in check.problems)


# --- C (git-only): events exist in the git ledger -----------------------------


def test_git_orphan_outcome_fails(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    # An outcome with no event.yaml beside it — an orphan referencing a non-existent
    # event, caught without any corpus.
    _write_outcome(data_root, "ca9", 1, "evt-motion-ghost")
    check = check_ledger_events_in_git(data_root)
    assert not check.passed
    assert check.checked == 1
    assert check.failures == 1


def test_git_event_present_passes(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_event(data_root, "ca9", 1, "evt-motion-stay")
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    _write_prediction(data_root, "ca9", 1, "evt-motion-stay", "p1")
    check = check_ledger_events_in_git(data_root)
    assert check.passed
    assert check.checked == 2  # the event.yaml itself is not a judgment artifact


def test_git_declared_ids_must_match_path(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_event(data_root, "ca9", 1, "evt-motion-stay")
    # Write a well-formed outcome, then move it under a different event directory so
    # its declared (case_id, event_id) no longer matches where it sits.
    ep_other = CasePaths(data_root, "ca9", 1).event("evt-motion-other")
    outcome = Outcome(
        case_id="ca9/1",
        event_id="evt-motion-stay",
        resolved_at=date(2026, 1, 2),
        actual_disposition=Disposition.granted,
        actual_granted=1,
    )
    write_json(ep_other.outcome, outcome)
    check = check_ledger_events_in_git(data_root)
    assert not check.passed
    assert any("declares" in p for p in check.problems)


def test_run_ledger_referential_checks_is_corpus_free(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_event(data_root, "ca9", 1, "evt-motion-stay")
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    _write_prediction(data_root, "ca9", 1, "evt-motion-stay", "p1")
    _write_evaluation(data_root, "ca9", 1, "evt-motion-stay", "p1", "e1")
    checks = run_ledger_referential_checks(data_root)
    names = {c.name for c in checks}
    assert names == {CHECK_LEDGER_EVENTS_IN_GIT, CHECK_EVALUATION_TARGETS}
    assert all(c.passed for c in checks)


# --- corpus that does not open ------------------------------------------------


def test_unopenable_corpus_fails_not_crashes(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    db.write_text("this is not a sqlite database")
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert not verdict.skipped
    assert [c.name for c in verdict.checks] == ["corpus_opens"]


# --- A: ledger schema conformance (git-only) ----------------------------------


def test_validate_ledger_passes_clean_artifacts(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    _write_prediction(data_root, "ca9", 1, "evt-motion-stay", "p1")
    result = validate_ledger(data_root)
    assert result.ok
    assert result.checked == 2
    assert result.invalid == 0
    assert result.problems == []


def test_validate_ledger_flags_malformed_artifact(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    out = _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    # Corrupt the outcome so it no longer matches its schema.
    out.write_text('{"not": "an outcome"}\n')
    result = validate_ledger(data_root)
    assert not result.ok
    assert result.invalid == 1
    assert any(str(out) in p for p in result.problems)


def test_validate_ledger_empty_tree_is_a_pass(tmp_path: Path) -> None:
    result = validate_ledger(tmp_path / "data")  # never created
    assert result.ok
    assert result.checked == 0


def test_validate_ledger_checks_flags_file(tmp_path: Path) -> None:
    # A committed flags.json is schema law like any other artifact: a good one passes.
    data_root = tmp_path / "data"
    ep = CasePaths(data_root, "ca9", 1).event("evt-motion-stay")
    write_json(
        ep.prediction_flags("p1", "r1"),
        AgentFlags(
            case_id="ca9/1",
            run_id="r1",
            role=UsageRole.predictor,
            actor_id="p1",
            flags=[AgentFlag(category=FlagCategory.data_quality, message="snapshot looks thin")],
        ),
    )
    result = validate_ledger(data_root)
    assert result.ok
    assert result.checked == 1


def test_validate_ledger_flags_malformed_flags_file(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    ep = CasePaths(data_root, "ca9", 1).event("evt-motion-stay")
    flags = ep.prediction_flags("p1", "r1")
    flags.parent.mkdir(parents=True)
    flags.write_text('{"flags": []}\n')  # empty list violates min_length
    result = validate_ledger(data_root)
    assert not result.ok
    assert result.invalid == 1


# --- CLI ----------------------------------------------------------------------


def _cli_env(tmp_path: Path, corpus_root: Path) -> dict[str, str]:
    """A CLI env whose seed cursor points at a fresh (empty) tmp path.

    Without this the cursor falls back to the repo's real ``config/seed-progress.yaml``
    (its path is CWD-relative), which would desync against the tiny test corpus.
    """
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    cursor = tmp_path / "seed-progress.yaml"  # never created -> empty cursor
    (config_root / "tracking.yaml").write_text(f"seed:\n  cursor: {cursor}\n")
    return {
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
    }


def test_cli_writes_verdict_and_summary(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"
    db = corpus.corpus_db_path(corpus_root)
    _seed_corpus(db)
    out = tmp_path / "verdict.json"
    result = runner.invoke(
        app,
        ["validate-corpus", "--out", str(out), "--today", TODAY.isoformat()],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 0, result.output
    assert "corpus-validation: OK" in result.output
    verdict = read_model(out, CorpusValidation)
    assert verdict.ok


def test_cli_absent_corpus_exits_zero(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"  # no corpus.db
    out = tmp_path / "verdict.json"
    result = runner.invoke(
        app,
        ["validate-corpus", "--out", str(out)],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 0, result.output
    assert "skipped" in result.output
    assert read_model(out, CorpusValidation).skipped


def test_cli_scope_audit_writes_audit_and_summary(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"
    _seed_scope_corpus(corpus.corpus_db_path(corpus_root))
    out = tmp_path / "scope-audit.json"
    result = runner.invoke(
        app,
        ["corpus-scope-audit", "--out", str(out)],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 0, result.output
    assert "corpus-scope-audit: 3 out-of-scope open event(s)" in result.output
    audit = read_model(out, CorpusScopeAudit)
    assert audit.scotus_open_events == 4
    assert {e.reason for e in audit.exclusions} == {
        "pre-1925 mandatory-jurisdiction matter (#309)",
        "stale unresolvable old SCOTUS petition (#333)",
    }


def test_cli_scope_audit_absent_corpus_exits_zero(tmp_path: Path) -> None:
    out = tmp_path / "scope-audit.json"
    result = runner.invoke(
        app,
        ["corpus-scope-audit", "--out", str(out)],
        env=_cli_env(tmp_path, tmp_path / "corpus"),
    )
    assert result.exit_code == 0, result.output
    assert "skipped" in result.output
    assert read_model(out, CorpusScopeAudit).skipped


def test_cli_validate_flags_git_orphan(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    # A judgment with no event.yaml beside it — a PR-time orphan the gate must catch.
    _write_outcome(data_root, "ca9", 1, "evt-motion-ghost")
    result = runner.invoke(app, ["validate", str(data_root)])
    assert result.exit_code == 1, result.output
    assert "ORPHAN" in result.output


def test_cli_validate_passes_consistent_ledger(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_event(data_root, "ca9", 1, "evt-motion-stay")
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    result = runner.invoke(app, ["validate", str(data_root)])
    assert result.exit_code == 0, result.output
    assert "OK" in result.output


def test_cli_failed_verdict_exits_nonzero(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"
    db = corpus.corpus_db_path(corpus_root)
    _seed_corpus(db)
    out = tmp_path / "verdict.json"
    result = runner.invoke(
        app,
        ["validate-corpus", "--out", str(out), "--baseline-count", "100"],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 1, result.output
    assert "corpus-validation: FAIL" in result.output
    # The verdict is still written even though the check failed (loud-not-fatal).
    assert not read_model(out, CorpusValidation).ok
