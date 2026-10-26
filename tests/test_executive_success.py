"""Fixture-pinned tests for the executive-action scope rule and the executive success cut.

The scope rule (`pipeline.exec_action`) decides which applications the cut
reads, so the fixtures pin one caption per reason code. The cut
(`pipeline.executive_success`) publishes shares, so they pin the direction of a
win on each side of the docket and which rows sit beside the rate.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.exec_action import (
    EXEC_ACTION_RULE_VERSION,
    REASON_SCOPE,
    SCOPE_REASONS,
    exec_action_annotations,
    exec_action_rule,
)
from fedcourtsai.pipeline.executive_success import (
    Reread,
    Rereader,
    _success,
    executive_success,
)
from fedcourtsai.schemas import Disposition, ExecutiveSuccess, ExecutiveSuccessCell

runner = CliRunner()


def _row(case_id: str, case_name: str, **kwargs: object) -> corpus.CorpusRow:
    """One live-slice SCOTUS row: `last_live_polled` is what puts it in the slice."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        case_name=case_name,
        last_live_polled=date(2026, 9, 1),
        **kwargs,
    )


def _sg(role: str) -> corpus.CounselEntry:
    """The Solicitor General as counsel of record for one side."""
    party = "United States" if role == "respondent" else "Federal Respondents"
    return corpus.CounselEntry(
        party=party,
        attorney="D. John Sauer",
        role=corpus.CounselRole(role),
        counsel_of_record=True,
    )


@pytest.mark.parametrize(
    ("case_name", "counsel", "reason", "side"),
    [
        (
            "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al.",
            [],
            "gov-applicant",
            "applicant",
        ),
        ("Acme Corp. v. Jane Doe", ["petitioner"], "gov-applicant", "applicant"),
        (
            "Ohio, et al. v. Environmental Protection Agency, et al.",
            [],
            "challenge-to-executive-action",
            "respondent",
        ),
        (
            "Talen Montana, LLC v. Environmental Protection Agency",
            [],
            "challenge-to-executive-action",
            "respondent",
        ),
        ("Idaho v. United States", [], "challenge-to-executive-action", "respondent"),
        ("John Roe v. United States", [], "federal-prosecution", "respondent"),
        (
            "Jane Roe v. Vincent F. DeMarco, United States Marshal",
            ["respondent"],
            "federal-prosecution",
            "respondent",
        ),
        (
            "John Roe v. United States District Court for the District of Arizona",
            ["respondent"],
            "federal-court",
            "respondent",
        ),
        ("John Roe v. Pamela Bondi, Attorney General", [], "individual-claim", "respondent"),
        (
            "Jane Roe, et al. v. Austin, Secretary of Defense, et al.",
            [],
            "individual-group",
            "respondent",
        ),
        ("Acme Corp. v. Jane Doe", ["respondent"], "sg-respondent-only", "respondent"),
        ("Acme Corp. v. Jane Doe", [], "no-federal-party", None),
    ],
)
def test_each_caption_shape_reads_its_reason(
    case_name: str, counsel: list[str], reason: str, side: str | None
) -> None:
    row = _row(
        "scotus/1",
        case_name,
        docket_number="25A1",
        date_filed=date(2025, 6, 1),
        counsel=[_sg(role) for role in counsel],
    )
    annotation = exec_action_annotations(row, row.date_filed)
    assert (annotation.reason, annotation.government_side) == (reason, side)
    assert annotation.in_scope is REASON_SCOPE[annotation.reason]
    assert annotation.rule_version == EXEC_ACTION_RULE_VERSION


def test_the_reason_codes_are_registered_once() -> None:
    assert set(SCOPE_REASONS) == set(REASON_SCOPE)
    assert len(SCOPE_REASONS) == len(set(SCOPE_REASONS))
    assert exec_action_rule(EXEC_ACTION_RULE_VERSION) is exec_action_annotations
    with pytest.raises(KeyError):
        exec_action_rule("exec-action-v9")


def _app(
    case_id: str,
    case_name: str,
    docket_number: str,
    filed: date,
    disposition: Disposition | None,
    *,
    decided: date | None = None,
    kind: str | None = "substantive",
) -> corpus.CorpusRow:
    return _row(
        case_id,
        case_name,
        docket_number=docket_number,
        date_filed=filed,
        date_decided=decided or (filed if disposition is not None else None),
        disposition=disposition,
        application_kind=kind,
    )


def _success_corpus(db: Path) -> None:
    """Government and challenger applications under two administrations, and the exclusions."""
    noem = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
    epa = "Ohio, et al. v. Environmental Protection Agency, et al."
    rows = [
        _app("scotus/1", noem, "24A900", date(2025, 3, 1), Disposition.granted),
        _app("scotus/2", noem, "24A901", date(2025, 3, 2), Disposition.granted_in_part),
        _app("scotus/3", noem, "24A902", date(2025, 3, 3), Disposition.denied),
        _app("scotus/4", noem, "24A903", date(2025, 3, 4), Disposition.withdrawn),
        _app("scotus/5", noem, "24A904", date(2025, 3, 5), None),
        _app("scotus/6", noem, "24A905", date(2025, 3, 6), Disposition.granted, kind="unknown"),
        _app("scotus/7", noem, "24A906", date(2025, 3, 7), Disposition.granted, kind="extension"),
        _app("scotus/8", noem, "24A900", date(2025, 3, 1), Disposition.granted),  # duplicate
        _app("scotus/9", epa, "24A100", date(2024, 7, 1), Disposition.denied),
        _app("scotus/10", epa, "24A101", date(2024, 7, 2), Disposition.granted),
        _app("scotus/11", epa, "24A102", date(2024, 7, 3), Disposition.dismissed),
        _app(
            "scotus/12", "John Roe v. United States", "24A103", date(2024, 7, 4), Disposition.denied
        ),
        _app(
            "scotus/13",
            "Jane Roe, et al. v. Austin, Secretary of Defense, et al.",
            "24A104",
            date(2024, 7, 5),
            Disposition.denied,
        ),
        _app(  # decided after the replication moment below
            "scotus/14",
            noem,
            "25A10",
            date(2025, 9, 1),
            Disposition.granted,
            decided=date(2025, 11, 1),
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


def _cells(result: ExecutiveSuccess) -> dict[tuple[str | None, str], ExecutiveSuccessCell]:
    return {(c.administration, c.filer): c for c in result.cells}


def test_a_win_reads_in_the_executives_direction(tmp_path: Path) -> None:
    """A government grant (partial included) and a challenger's denial are both wins."""
    db = tmp_path / "corpus.db"
    _success_corpus(db)
    with corpus.connect(db) as conn:
        result = executive_success(conn, as_of_field="filed")
    cells = _cells(result)
    government = cells[("trump-47", "government")]
    # The unreadable-ask grant counts like any other row, and is tallied.
    assert (government.rows, government.unknown_ask) == (7, 1)
    assert (government.wins, government.decided) == (4, 5)
    assert government.success_rate == pytest.approx(4 / 5)
    assert (government.withdrawn, government.pending) == (1, 1)
    challenger = cells[("biden-46", "challenger")]
    assert (challenger.wins, challenger.decided, challenger.dismissed) == (1, 2, 1)
    pooled = cells[("biden-46", "all")]
    assert (pooled.wins, pooled.decided) == (1, 2)
    assert ("biden-46", "government") not in cells
    # No snapshot is stored, so every stored denial in scope keeps its label.
    assert result.reading == "finer"
    assert (result.reread_rows, result.reread_changed, result.reread_unobservable) == (3, 0, 3)


def test_the_finer_reading_relabels_a_stored_denial() -> None:
    """A partial grant becomes the government's win; a denial as moot leaves the rate."""
    db_rows: list[corpus.CorpusRow] = []
    noem = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
    epa = "Ohio, et al. v. Environmental Protection Agency, et al."
    db_rows.append(_app("scotus/1", noem, "24A902", date(2025, 3, 3), Disposition.denied))
    db_rows.append(_app("scotus/2", epa, "24A100", date(2024, 7, 1), Disposition.denied))
    db_rows.append(_app("scotus/3", epa, "24A101", date(2024, 7, 2), Disposition.granted))
    finer = {"24A902": "granted-in-part", "24A100": "dismissed-moot"}
    calls: list[str] = []

    def reread(rows: Sequence[corpus.CorpusRow]) -> list[Reread]:
        calls.extend(row.docket_number for row in rows)
        return [
            (finer[row.docket_number], None) if row.docket_number in finer else None for row in rows
        ]

    def cut(rereader: Rereader | None) -> ExecutiveSuccess:
        return _success(
            db_rows,
            as_of_field="filed",
            through=None,
            since=None,
            corpus_sha256="",
            scope_rule_version=EXEC_ACTION_RULE_VERSION,
            reread=rereader,
            latest_pull=None,
            latest_snapshot=None,
        )

    result = cut(reread)
    assert sorted(calls) == ["24A100", "24A902"]  # only stored denials are re-read
    cells = _cells(result)
    assert (cells[("trump-47", "government")].wins, cells[("trump-47", "government")].decided) == (
        1,
        1,
    )
    challenger = cells[("biden-46", "challenger")]
    assert (challenger.wins, challenger.decided, challenger.dismissed) == (0, 1, 1)
    assert challenger.dispositions == {"dismissed-moot": 1, "granted": 1}
    assert (result.reread_rows, result.reread_changed) == (2, 2)
    listed = {row.docket_number: row for row in result.review_rows}
    assert (listed["24A902"].stored_disposition, listed["24A902"].reading) == (
        "denied",
        "granted-in-part",
    )
    registered = cut(None)
    assert registered.reading == "registered"
    assert registered.reread_rows == 0
    assert _cells(registered)[("trump-47", "government")].wins == 0


def _live(docket: str, order: str, decided: str) -> dict[str, object]:
    """A supremecourt.gov-shaped docket payload whose last entry disposes of the application."""
    return {
        "ProceedingsandOrder": [
            {"Date": "2025-03-01", "Text": f"Application ({docket}) for a stay, submitted."},
            {"Date": decided, "Text": order},
        ]
    }


def test_the_rereader_reads_the_live_snapshot_and_respects_the_cut(tmp_path: Path) -> None:
    """A newer REST snapshot is skipped; an entry dated after `through` keeps the stored label."""
    noem = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _app(
                    "scotus/1",
                    noem,
                    "24A949",
                    date(2025, 3, 3),
                    Disposition.denied,
                    decided=date(2025, 4, 10),
                ),
                _app(
                    "scotus/2",
                    noem,
                    "24A790",
                    date(2025, 3, 4),
                    Disposition.denied,
                    decided=date(2025, 3, 6),
                ),
            ],
        )
        partial = "The application is granted in part and denied in part."
        corpus.upsert_snapshot(
            conn, "scotus/1", date(2025, 4, 11), _live("24A949", partial, "2025-04-10")
        )
        # A later CourtListener pull stores a REST payload beside the live one.
        corpus.upsert_snapshot(conn, "scotus/1", date(2025, 5, 1), {"docket_entries": []})
        moot = "Application (24A790) to vacate the order is denied as moot."
        corpus.upsert_snapshot(
            conn, "scotus/2", date(2025, 6, 2), _live("24A790", moot, "2025-06-01")
        )
        whole = executive_success(conn, as_of_field="filed")
        cut = executive_success(conn, as_of_field="filed", through=date(2025, 5, 1))
    listed = {row.docket_number: row.reading for row in whole.review_rows}
    assert listed == {"24A949": "granted-in-part", "24A790": "dismissed-moot"}
    assert (whole.reread_rows, whole.reread_changed, whole.reread_unobservable) == (2, 2, 0)
    government = _cells(whole)[("trump-47", "government")]
    assert (government.wins, government.decided, government.dismissed) == (1, 1, 1)
    # At the May cut the moot entry, dated June, had not happened: it stays denied.
    at_cut = {row.docket_number: row.reading for row in cut.review_rows}
    assert at_cut == {"24A949": "granted-in-part", "24A790": "denied"}
    assert (cut.reread_changed, cut.reread_after_through) == (1, 1)


def test_scope_and_exclusions_are_counted_beside_the_rate(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _success_corpus(db)
    with corpus.connect(db) as conn:
        result = executive_success(conn, as_of_field="filed")
    assert (result.duplicate_rows, result.extension_rows, result.applications) == (1, 1, 12)
    assert result.scope_reasons == {
        "gov-applicant": 7,
        "challenge-to-executive-action": 3,
        "individual-group": 1,
        "federal-prosecution": 1,
    }
    assert result.unknown_scope == {"biden-46": 1}
    listed = {row.docket_number: row for row in result.review_rows}
    assert "24A103" not in listed  # out of scope: not listed
    assert listed["24A104"].in_scope is None
    assert listed["24A902"].executive_won is False
    assert listed["24A100"].executive_won is True


def test_through_places_the_cut_at_a_past_moment(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _success_corpus(db)
    with corpus.connect(db) as conn:
        whole = executive_success(conn, as_of_field="filed")
        cut = executive_success(conn, as_of_field="filed", through=date(2025, 10, 1))
        later = executive_success(conn, as_of_field="filed", since=date(2025, 1, 1))
    assert _cells(whole)[("trump-47", "government")].decided == 5
    government = _cells(cut)[("trump-47", "government")]
    assert (government.rows, government.pending, government.decided) == (7, 2, 4)
    assert later.filed_before_since == 5
    assert ("biden-46", "challenger") not in _cells(later)


def test_resolved_attribution_reads_the_decision_date(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _app(  # filed under one administration, decided under the next
                    "scotus/1",
                    "Ohio v. Environmental Protection Agency",
                    "24A700",
                    date(2025, 1, 10),
                    Disposition.denied,
                    decided=date(2025, 2, 1),
                ),
            ],
        )
        filed = executive_success(conn, as_of_field="filed")
        resolved = executive_success(conn, as_of_field="resolved")
    assert [c.administration for c in filed.cells] == ["biden-46", "biden-46"]
    assert [c.administration for c in resolved.cells] == ["trump-47", "trump-47"]


def test_the_cut_refuses_what_it_cannot_cut(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _success_corpus(db)
    with corpus.connect(db) as conn:
        with pytest.raises(ValueError, match="unknown as-of"):
            executive_success(conn, as_of_field="argued")
        with pytest.raises(ValueError, match="unknown reading"):
            executive_success(conn, as_of_field="filed", reading="loose")  # type: ignore[arg-type]
        with pytest.raises(KeyError):
            executive_success(conn, as_of_field="filed", scope_rule_version="exec-action-v9")


def test_the_command_prints_the_cut_with_its_vintage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    _success_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(
        app, ["executive-success", "--as-of", "filed", "--through", "2025-10-01"]
    )
    assert result.exit_code == 0, result.output
    assert (
        "executive success (exec-action-v1 over party-v2 and sg-office-v1, as-of filed, "
        "through 2025-10-01)"
    ) in result.stderr
    assert "trump-47 government: executive won 3/4 = 75.0%" in result.stderr
    assert "finer reading re-read 3 stored denial(s)" in result.stderr
    assert "corpus latest pull never pulled" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["through"] == "2025-10-01"
    assert payload["scope_rule_version"] == "exec-action-v1"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--as-of", "argued"], "unknown --as-of"),
        (["--as-of", "filed", "--scope-rule", "exec-action-v9"], "unregistered scope rule"),
        (["--as-of", "filed", "--reading", "loose"], "unknown --reading"),
        (["--as-of", "filed", "--through", "October"], "unreadable --through"),
        (["--as-of", "filed", "--since", "April"], "unreadable --since"),
    ],
)
def test_the_command_refuses_what_it_cannot_cut(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, args: list[str], message: str
) -> None:
    corpus_root = tmp_path / "corpus"
    _success_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(app, ["executive-success", *args])
    assert result.exit_code == 2
    assert message in result.stderr


def test_the_command_fails_loud_without_a_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "empty"))
    result = runner.invoke(app, ["executive-success", "--as-of", "filed"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.stderr
