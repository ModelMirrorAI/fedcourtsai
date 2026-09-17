"""The case-centric big-case board (``fedcourts big-cases`` / :mod:`analytics`).

Every test builds its own ledger under ``tmp_path`` with :func:`_write_read`,
which commits one prediction (and, on request, the event definition and the
outcome) under the canonical case tree. The board is ledger-only, so a ledger is
the whole input: no corpus, no config, no clock.
"""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics
from fedcourtsai.cli import app
from fedcourtsai.metrics_refresh import render_refresh_pr
from fedcourtsai.paths import CasePaths
from fedcourtsai.process_version import CURRENT_PROCESS_LABEL
from fedcourtsai.schemas import (
    BigCaseBoard,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
)
from fedcourtsai.serialize import write_json, write_yaml

runner = CliRunner()

_EVENT = "evt-petition-disposition"


def _stamp(when: datetime) -> ProcessVersion:
    """A harness stamp at ``when`` — what the collapse orders on."""
    return ProcessVersion(label="proc-test", digest="sha256:" + "0" * 64, stamped_at=when)


def _write_read(  # noqa: PLR0913 - one keyword per artifact field a test varies
    data_root: Path,
    case_id: str,
    predictor_id: str,
    run_id: str,
    *,
    event_id: str = _EVENT,
    big_case_score: float | None = None,
    big_case_rationale: str | None = None,
    created_at: datetime = datetime(2026, 6, 20, tzinfo=UTC),
    stamped_at: datetime | None = None,
    title: str | None = "Test event",
    resolved_at: date | None = None,
    mode: str | None = "forward",
    probability: float = 0.7,
) -> None:
    """Commit one prediction, with the event definition and outcome it needs."""
    court, _, docket = case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(event_id)
    if title is not None:
        write_yaml(
            event.event_file,
            PredictableEvent(
                event_id=event_id,
                case_id=case_id,
                kind=EventKind.petition,
                title=title,
                resolved=resolved_at is not None,
            ),
        )
    write_json(
        event.prediction(predictor_id, run_id),
        Prediction(
            case_id=case_id,
            event_id=event_id,
            predictor_id=predictor_id,
            engine=Engine.claude_code,
            run_id=run_id,
            created_at=created_at,
            input_snapshot="corpus",
            granted=1,
            probability=probability,
            predicted_disposition=Disposition.granted,
            confidence=0.6,
            big_case_score=big_case_score,
            big_case_rationale=big_case_rationale,
            process_version=_stamp(stamped_at) if stamped_at is not None else None,
            context=(
                PredictionContext(
                    mode=mode, snapshot_date=date(2026, 6, 1), signals_observable=True
                )
                if mode is not None
                else None
            ),
        ),
    )
    if resolved_at is not None:
        write_json(
            event.outcome,
            Outcome(
                case_id=case_id,
                event_id=event_id,
                resolved_at=resolved_at,
                actual_disposition=Disposition.granted,
                actual_granted=1,
            ),
        )


def _board(data_root: Path, *, repo_url: str = analytics.DEFAULT_REPO_TREE_URL) -> BigCaseBoard:
    return analytics.build_big_case_board(data_root=data_root, repo_url=repo_url)


def test_the_case_mean_is_taken_over_the_predictors_that_scored_it(tmp_path: Path) -> None:
    # Three predictors, one of which declared no view: the mean is over two.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_read(tmp_path, "scotus/1", "codex-baseline", "r1", big_case_score=0.6)
    _write_read(
        tmp_path,
        "scotus/1",
        "gemini-baseline",
        "r1",
        big_case_score=None,
        big_case_rationale="no view: the stakes turn on facts the snapshot does not carry",
    )
    (row,) = _board(tmp_path).rows
    assert (row.mean_big_case_score, row.n) == (0.7, 2)  # (0.8 + 0.6) / 2, not / 3
    assert (row.score_min, row.score_max, row.score_range) == (0.6, 0.8, 0.2)
    declined = next(read for read in row.current_reads if read.predictor_id == "gemini-baseline")
    assert declined.big_case_score is None
    # A rationale is what makes this a *declared* no view rather than a missing
    # read, and it travels with the null.
    assert declined.big_case_rationale is not None
    assert (_board(tmp_path).declared_no_view, _board(tmp_path).missing_reads) == (1, 0)


def test_an_unscored_read_is_never_imputed_as_a_zero(tmp_path: Path) -> None:
    # The arithmetic difference is the whole point: imputing zero would rank this
    # case at 0.4 rather than 0.8, which is a fabricated panel opinion.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_read(tmp_path, "scotus/1", "codex-baseline", "r1", big_case_score=None)
    (row,) = _board(tmp_path).rows
    assert (row.mean_big_case_score, row.n) == (0.8, 1)


def test_a_case_whose_every_current_read_is_unscored_is_off_the_board(tmp_path: Path) -> None:
    # The population is "at least one score", so a case with none is absent
    # rather than present with an empty mean.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=None)
    _write_read(tmp_path, "scotus/2", "claude-baseline", "r1", big_case_score=0.4)
    board = _board(tmp_path)
    assert [row.case_id for row in board.rows] == ["scotus/2"]
    assert board.cases == 1
    # The absent case's unscored read is not counted either — every read figure
    # sums the rows — and the case itself is published as a dropped one, so
    # `cases` is never read as the whole predicted population.
    assert (board.current_reads, board.scored_reads, board.missing_reads) == (1, 1, 0)
    assert board.cases_without_score == 1


def test_the_collapse_takes_the_newest_run_by_cell_clock_not_by_directory_name(
    tmp_path: Path,
) -> None:
    # The lexically later run carries the OLDER harness stamp, so ordering on the
    # directory name would pick the superseded read.
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "20260101T000000Z",
        big_case_score=0.9,
        stamped_at=datetime(2026, 6, 20, tzinfo=UTC),
    )
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "20260202T000000Z",
        big_case_score=0.1,
        stamped_at=datetime(2026, 5, 1, tzinfo=UTC),
    )
    (row,) = _board(tmp_path).rows
    (current,) = row.current_reads
    assert (current.run_id, current.big_case_score) == ("20260101T000000Z", 0.9)
    assert (row.mean_big_case_score, row.n) == (0.9, 1)
    # The superseded run is still visible under its event — history, never averaged.
    (event,) = row.events
    assert len(event.reads) == 1  # one read per predictor per event, also collapsed


def test_the_collapse_crosses_events_so_a_later_moment_supersedes_an_earlier_one(
    tmp_path: Path,
) -> None:
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "r1",
        event_id="evt-petition-disposition",
        big_case_score=0.4,
        stamped_at=datetime(2026, 5, 1, tzinfo=UTC),
        title="Petition moment",
    )
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "r2",
        event_id="evt-order-response-requested-disposition",
        big_case_score=0.9,
        stamped_at=datetime(2026, 6, 1, tzinfo=UTC),
        title="Response moment",
    )
    (row,) = _board(tmp_path).rows
    (current,) = row.current_reads
    assert (current.event_id, current.big_case_score) == (
        "evt-order-response-requested-disposition",
        0.9,
    )
    assert row.mean_big_case_score == 0.9  # the earlier moment is not averaged in
    # Both events are listed, each with the predictor's newest read of it.
    assert [(event.event_id, event.reads[0].big_case_score) for event in row.events] == [
        ("evt-order-response-requested-disposition", 0.9),
        ("evt-petition-disposition", 0.4),
    ]


def test_the_caption_comes_from_the_event_the_newest_current_read_sits_on(
    tmp_path: Path,
) -> None:
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "r1",
        event_id="evt-petition-disposition",
        big_case_score=0.4,
        stamped_at=datetime(2026, 5, 1, tzinfo=UTC),
        title="Petition moment",
    )
    _write_read(
        tmp_path,
        "scotus/1",
        "codex-baseline",
        "r2",
        event_id="evt-order-response-requested-disposition",
        big_case_score=0.6,
        stamped_at=datetime(2026, 6, 1, tzinfo=UTC),
        title="Response moment",
    )
    (row,) = _board(tmp_path).rows
    assert (row.caption, row.caption_event_id) == (
        "Response moment",
        "evt-order-response-requested-disposition",
    )


def test_a_case_whose_event_definition_is_absent_reports_no_caption(tmp_path: Path) -> None:
    # `validate` refuses a prediction under an undefined event; the board reports
    # the absence rather than failing on it.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5, title=None)
    (row,) = _board(tmp_path).rows
    assert (row.caption, row.caption_event_id) == (None, _EVENT)


def test_rows_sort_by_mean_then_by_n_then_by_case_id(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(tmp_path, "scotus/1", "codex-baseline", "r1", big_case_score=0.5)
    _write_read(tmp_path, "scotus/2", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(tmp_path, "scotus/3", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(tmp_path, "scotus/4", "claude-baseline", "r1", big_case_score=0.9)
    board = _board(tmp_path)
    # 0.9 first; then the three 0.5s, the n=2 ahead of the two n=1, which tie on
    # the mean and on n and so fall back to the case id.
    assert [(row.case_id, row.n) for row in board.rows] == [
        ("scotus/4", 1),
        ("scotus/1", 2),
        ("scotus/2", 1),
        ("scotus/3", 1),
    ]
    assert [(entry.n, entry.cases) for entry in board.coverage] == [(2, 1), (1, 3)]


def test_status_and_the_outcome_come_from_the_committed_outcome_files(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(
        tmp_path,
        "scotus/2",
        "claude-baseline",
        "r1",
        big_case_score=0.5,
        resolved_at=date(2026, 6, 23),
    )
    _write_read(
        tmp_path,
        "scotus/3",
        "claude-baseline",
        "r1",
        event_id="evt-petition-disposition",
        big_case_score=0.5,
        resolved_at=date(2026, 6, 23),
    )
    _write_read(
        tmp_path,
        "scotus/3",
        "claude-baseline",
        "r2",
        event_id="evt-order-response-requested-disposition",
        big_case_score=0.5,
    )
    statuses = {row.case_id: row.status for row in _board(tmp_path).rows}
    assert statuses == {
        "scotus/1": "pending",
        "scotus/2": "resolved",
        "scotus/3": "partly_resolved",
    }
    decided = next(row for row in _board(tmp_path).rows if row.case_id == "scotus/2")
    (event,) = decided.events
    assert (event.actual_disposition, event.resolved_at) == ("granted", date(2026, 6, 23))


def test_each_event_read_carries_the_headline_forecast_beside_the_stakes_score(
    tmp_path: Path,
) -> None:
    # The stakes number never travels alone: a reader who sees only it is one
    # step from reading it as an odds number.
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "r1",
        big_case_score=0.5,
        probability=0.23,
        mode="replay",
    )
    ((event,),) = [row.events for row in _board(tmp_path).rows]
    (read,) = event.reads
    assert (read.probability, read.predicted_disposition, read.granted) == (0.23, "granted", 1)
    assert (read.confidence, read.mode) == (0.6, "replay")


def test_a_cell_written_before_the_context_block_existed_reports_no_mode(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5, mode=None)
    ((event,),) = [row.events for row in _board(tmp_path).rows]
    assert event.reads[0].mode is None


def test_cell_links_are_the_repo_relative_path_under_the_configured_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A repo-relative data root, as the workflow runs it: the path spells itself
    # the way the repository does, so it is a link.
    monkeypatch.chdir(tmp_path)
    _write_read(Path("data"), "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    ((event,),) = [
        row.events for row in _board(Path("data"), repo_url="https://example/tree/main").rows
    ]
    (read,) = event.reads
    assert read.cell_path == (
        "data/cases/scotus/1/events/evt-petition-disposition/predictions/claude-baseline/r1"
    )
    assert read.cell_url == f"https://example/tree/main/{read.cell_path}"


def test_an_absolute_data_root_publishes_the_path_but_no_link(tmp_path: Path) -> None:
    # The path would be the build machine's, and a filesystem path concatenated
    # onto the repository URL is a link to nothing that belongs in a published
    # artifact.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    ((event,),) = [
        row.events for row in _board(tmp_path, repo_url="https://example/tree/main").rows
    ]
    (read,) = event.reads
    assert read.cell_path.startswith("/")
    assert read.cell_url is None


def test_an_empty_repository_url_publishes_paths_without_links(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    ((event,),) = [row.events for row in _board(tmp_path, repo_url="").rows]
    assert event.reads[0].cell_url is None


def _write_grading(
    data_root: Path,
    case_id: str,
    predictor_id: str,
    prediction_run_id: str | None,
    *,
    evaluator_id: str = "claude-judge",
    event_id: str = _EVENT,
    leakage_suspected: bool | None = True,
) -> None:
    """Commit one grading of a prediction — the board reads only its leakage bit."""
    court, _, docket = case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(event_id)
    write_json(
        event.evaluation(evaluator_id, predictor_id, "e1"),
        Evaluation(
            case_id=case_id,
            event_id=event_id,
            predictor_id=predictor_id,
            evaluator_id=evaluator_id,
            engine=Engine.claude_code,
            run_id="e1",
            created_at=datetime(2026, 6, 24, tzinfo=UTC),
            correct=1,
            prediction_run_id=prediction_run_id,
            leakage_suspected=leakage_suspected,
        ),
    )


def test_a_leakage_flagged_read_is_marked_on_the_read_and_on_its_row(tmp_path: Path) -> None:
    # The board does not drop the cell the scored boards drop — that is the
    # registered carve-out — so the mark is what keeps the row readable.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_read(tmp_path, "scotus/1", "codex-baseline", "r1", big_case_score=0.6)
    _write_grading(tmp_path, "scotus/1", "claude-baseline", "r1")
    board = _board(tmp_path)
    (row,) = board.rows
    assert row.leakage_suspected
    assert board.rows_with_leakage_flag == 1
    marked = {read.predictor_id: read.leakage_suspected for read in row.current_reads}
    assert marked == {"claude-baseline": True, "codex-baseline": False}
    # The mean is unchanged: the board reports the contamination, it does not
    # silently re-weight around it.
    assert (row.mean_big_case_score, row.n) == (0.7, 2)


def test_a_grading_naming_no_run_flags_every_run_of_that_predictor_on_the_event(
    tmp_path: Path,
) -> None:
    # A grading written before the harness stamped `prediction_run_id` names no
    # run; dropping a recorded suspicion because the record is old is the wrong
    # direction on a surface that publishes the cell's number.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_grading(tmp_path, "scotus/1", "claude-baseline", None)
    (row,) = _board(tmp_path).rows
    assert row.leakage_suspected


def test_a_grading_of_another_run_does_not_flag_this_one(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_grading(tmp_path, "scotus/1", "claude-baseline", "r0")
    (row,) = _board(tmp_path).rows
    assert not row.leakage_suspected
    assert _board(tmp_path).rows_with_leakage_flag == 0


def test_a_clean_grading_flags_nothing(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_grading(tmp_path, "scotus/1", "claude-baseline", "r1", leakage_suspected=False)
    _write_grading(
        tmp_path, "scotus/1", "claude-baseline", "r1", evaluator_id="c", leakage_suspected=None
    )
    assert not _board(tmp_path).rows[0].leakage_suspected


def test_an_unscored_read_splits_on_whether_it_declared_a_view(tmp_path: Path) -> None:
    # The two are different records and the prompt amendment is what separates
    # them: before it the field was optional, so an absence pooled "could not
    # place the stakes" with "never engaged the question".
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(
        tmp_path,
        "scotus/1",
        "codex-baseline",
        "r1",
        big_case_score=None,
        big_case_rationale="the stakes turn on facts the snapshot does not carry",
    )
    _write_read(tmp_path, "scotus/1", "gemini-baseline", "r1", big_case_score=None)
    board = _board(tmp_path)
    assert (board.current_reads, board.scored_reads) == (3, 1)
    assert (board.declared_no_view, board.missing_reads) == (1, 1)
    # The three partition: no read is counted twice and none is lost.
    assert board.scored_reads + board.declared_no_view + board.missing_reads == board.current_reads


def test_the_board_publishes_what_the_rank_column_can_support(tmp_path: Path) -> None:
    # Two rows whose means differ by 0.01 while each row's own panel spans 0.4:
    # the gap between neighbours is far smaller than the disagreement inside one.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.8)
    _write_read(tmp_path, "scotus/1", "codex-baseline", "r1", big_case_score=0.4)
    _write_read(tmp_path, "scotus/2", "claude-baseline", "r1", big_case_score=0.79)
    _write_read(tmp_path, "scotus/2", "codex-baseline", "r1", big_case_score=0.39)
    board = _board(tmp_path)
    assert (board.median_adjacent_gap, board.median_score_range) == (0.01, 0.4)
    rendered = analytics.render_big_case_markdown(board)
    assert "median gap between neighbouring rows is **0.010**" in rendered
    assert "median spread inside a row's own panel is **0.400**" in rendered


def test_a_single_row_board_publishes_no_adjacent_gap(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    board = _board(tmp_path)
    assert (board.median_adjacent_gap, board.median_score_range) == (None, 0.0)


def test_the_board_carries_its_reading_rules_and_the_process_label(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    provenance = _board(tmp_path).provenance
    assert provenance is not None
    assert provenance.process_label == CURRENT_PROCESS_LABEL
    # The registered carve-out travels inside the artifact, verbatim.
    assert "neither scored nor ranked" in provenance.reading_rule
    assert "neither the forward-claim exclusion nor the leakage exclusion" in (
        provenance.reading_rule
    )
    assert "two populations" in provenance.no_time_series
    assert "mean over its moments" in provenance.leaderboard_divergence
    # The three caveats the reviewers' reading turns on, each registered rather
    # than left to the renderer: the forecast that rides beside the stakes read,
    # the contamination a ledger-direct read admits, and the version blindness.
    assert "is not a claimable one" in provenance.reading_rule
    assert "partly a read of the disposition" in provenance.leakage_note
    assert "Version-blind on purpose" in provenance.version_scope
    assert "coarse band, never an ordering" in provenance.rank_resolution
    assert "salience gate" in provenance.population


def test_the_board_stamps_no_clock_and_no_commit(tmp_path: Path) -> None:
    # Byte-stability is what makes an unchanged day open no PR, and a self-stamp
    # would break it on every run.
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    payload = _board(tmp_path).model_dump()
    assert not {"generated_at", "created_at", "commit", "pipeline_sha"} & set(payload)


def test_build_big_case_board_is_deterministic(tmp_path: Path) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(tmp_path, "scotus/2", "codex-baseline", "r1", big_case_score=0.5)
    assert _board(tmp_path).model_dump_json() == _board(tmp_path).model_dump_json()
    assert analytics.render_big_case_markdown(_board(tmp_path)) == (
        analytics.render_big_case_markdown(_board(tmp_path))
    )


def test_an_absent_ledger_builds_the_empty_board(tmp_path: Path) -> None:
    board = _board(tmp_path / "absent")
    assert (board.cases, board.rows, board.predictors) == (0, [], [])
    assert board.provenance is not None  # the reading rules do not depend on the data


def test_the_markdown_leads_with_the_reading_rules_and_marks_a_null_as_no_view(
    tmp_path: Path,
) -> None:
    _write_read(tmp_path, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    _write_read(tmp_path, "scotus/1", "codex-baseline", "r1", big_case_score=None)
    rendered = analytics.render_big_case_markdown(_board(tmp_path))
    head, _, table = rendered.partition("| # | case |")
    assert head.startswith("# Big-case board")
    assert "neither scored nor ranked" in head  # the caveat is above the numbers, not below
    assert "says nothing about how likely any of them is to be granted" in head
    # The declining predictor's column is an em dash, and the footer says why.
    assert "| 1 | `scotus/1` | Test event | 0.500 | 1 | 0.000 | 0.50 | — | pending | — |" in table
    assert "**not as a zero**" in head


def test_the_empty_board_renders_its_own_state(tmp_path: Path) -> None:
    rendered = analytics.render_big_case_markdown(_board(tmp_path / "absent"))
    assert "no committed prediction carries a stakes read yet" in rendered


def test_a_caption_cannot_break_the_markdown_table(tmp_path: Path) -> None:
    # The caption is docket text this project did not write.
    _write_read(
        tmp_path,
        "scotus/1",
        "claude-baseline",
        "r1",
        big_case_score=0.5,
        title="A | B\nand a second line",
    )
    rendered = analytics.render_big_case_markdown(_board(tmp_path))
    lines = rendered.splitlines()
    header = next(line for line in lines if line.startswith("| # | case |"))
    row = next(line for line in lines if line.startswith("| 1 |"))
    assert "A \\| B and a second line" in row
    # The escaped pipe and the folded newline leave the row with exactly the
    # header's cell count: a raw caption would have split it into two cells.
    assert row.replace("\\|", "").count("|") == header.count("|")


def test_cli_big_cases_writes_both_files_and_reruns_byte_identically(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_read(data_root, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    json_out = tmp_path / "big-cases.json"
    md_out = tmp_path / "big-cases.md"
    args = [
        "big-cases",
        "--out",
        str(json_out),
        "--markdown-out",
        str(md_out),
    ]
    env = {"FEDCOURTS_DATA_ROOT": str(data_root)}
    result = runner.invoke(app, args, env=env)
    assert result.exit_code == 0, result.output
    board = BigCaseBoard.model_validate_json(json_out.read_text())
    assert board.cases == 1
    assert md_out.read_text().startswith("# Big-case board")
    first_json, first_md = json_out.read_text(), md_out.read_text()
    assert runner.invoke(app, args, env=env).exit_code == 0
    assert (json_out.read_text(), md_out.read_text()) == (first_json, first_md)


def test_cli_big_cases_defaults_under_the_metrics_root(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_read(data_root, "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    result = runner.invoke(
        app,
        ["big-cases"],
        env={
            "FEDCOURTS_DATA_ROOT": str(data_root),
            "FEDCOURTS_METRICS_ROOT": str(tmp_path / "metrics"),
        },
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "metrics/big-cases.json").is_file()
    assert (tmp_path / "metrics/big-cases.md").is_file()


def test_the_refresh_pr_reports_the_board_without_naming_a_case(tmp_path: Path) -> None:
    # Registered in the refresh order, so a changed board reaches the PR body —
    # and headlined by denominators, since the body is quoted out of context.
    _write_read(tmp_path / "data", "scotus/1", "claude-baseline", "r1", big_case_score=0.5)
    board = _board(tmp_path / "data")
    write_json(tmp_path / "metrics/big-cases.json", board)
    (tmp_path / "metrics/big-cases.md").write_text(analytics.render_big_case_markdown(board))
    pr = render_refresh_pr(["metrics/big-cases.json", "metrics/big-cases.md"], tmp_path, run_id="1")
    assert pr is not None
    assert "1 case(s) ranked over 1 scored stakes read(s) of 1" in pr.body
    assert "human-readable big-case-board companion" in pr.body
    assert "Test event" not in pr.body
