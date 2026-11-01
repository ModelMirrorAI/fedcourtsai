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
from fedcourtsai.pipeline.controversy import (
    CONTROVERSY_RULE_VERSION,
    ControversyLinks,
    controversy_links,
    group_controversies,
)
from fedcourtsai.pipeline.exec_action import (
    EXEC_ACTION_RULE_VERSION,
    EXEC_ACTION_RULE_VERSION_V1,
    REASON_SCOPE,
    SCOPE_REASONS,
    exec_action_annotations,
    exec_action_annotations_v2,
    exec_action_rule,
)
from fedcourtsai.pipeline.executive_success import (
    Fetcher,
    Payload,
    _success,
    executive_success,
)
from fedcourtsai.pipeline.interim_signals import is_overlength_request
from fedcourtsai.schemas import (
    Disposition,
    ExecutiveControversyCell,
    ExecutiveSuccess,
    ExecutiveSuccessCell,
)

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
    assert annotation.rule_version == EXEC_ACTION_RULE_VERSION_V1
    # v2 reads the caption the same way where it has no snapshot to read.
    v2 = exec_action_annotations_v2(row, row.date_filed)
    assert (v2.reason, v2.government_side, v2.rule_version) == (
        reason,
        side,
        EXEC_ACTION_RULE_VERSION,
    )


def test_the_reason_codes_are_registered_once() -> None:
    assert set(SCOPE_REASONS) == set(REASON_SCOPE)
    assert len(SCOPE_REASONS) == len(set(SCOPE_REASONS))
    assert exec_action_rule(EXEC_ACTION_RULE_VERSION_V1) is exec_action_annotations
    assert exec_action_rule(EXEC_ACTION_RULE_VERSION) is exec_action_annotations_v2
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
    finer = {
        "24A902": _live("24A902", "The application is granted in part.", "2025-03-03"),
        "24A100": _live("24A100", "Application (24A100) denied as moot.", "2024-07-01"),
    }
    calls: list[str] = []

    def fetch(rows: Sequence[corpus.CorpusRow]) -> list[Payload]:
        calls.extend(row.docket_number for row in rows)
        return [finer.get(row.docket_number) for row in rows]

    def cut(fetcher: Fetcher | None) -> ExecutiveSuccess:
        return _success(
            db_rows,
            as_of_field="filed",
            through=None,
            since=None,
            corpus_sha256="",
            scope_rule_version=EXEC_ACTION_RULE_VERSION,
            fetch=fetcher,
            reading="finer",
            latest_pull=None,
            latest_snapshot=None,
        )

    result = cut(fetch)
    # One batch fetch covers every counted row; only the stored denials are re-read.
    assert sorted(calls) == ["24A100", "24A101", "24A902"]
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
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    result = runner.invoke(
        app, ["executive-success", "--as-of", "filed", "--through", "2025-10-01"]
    )
    assert result.exit_code == 0, result.output
    assert (
        "executive success (exec-action-v2 over party-v2 and sg-office-v1, as-of filed, "
        "through 2025-10-01)"
    ) in result.stderr
    assert "trump-47 government: executive won 3/4 = 75.0%" in result.stderr
    assert "finer reading re-read 3 stored denial(s)" in result.stderr
    assert (
        "trump-47 government by controversy (controversy-v2): executive won 1/1"
    ) in result.stderr
    assert "corpus latest pull never pulled" in result.stderr
    assert "policy areas (policy-area-v1):" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["through"] == "2025-10-01"
    assert payload["scope_rule_version"] == "exec-action-v2"


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


def _links(
    docket: str,
    *,
    lower: set[tuple[str, str]] | None = None,
    named: set[str] | None = None,
    caption: tuple[str, str] | None = None,
    order: tuple[str, date, str, str] | None = None,
    court: str = "",
    filed: date | None = None,
    ended: date | None = None,
) -> ControversyLinks:
    return ControversyLinks(
        docket,
        frozenset(lower or ()),
        frozenset(named or ()),
        caption,
        order=order,
        lower_court=court,
        filed=filed,
        ended=ended or filed,
    )


def test_controversy_links_read_the_case_below_the_order_and_the_caption() -> None:
    noem = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
    row = _app("scotus/1", noem, "24A884", date(2025, 3, 1), Disposition.granted)
    payload = {
        "LowerCourt": "United States Court of Appeals for the Ninth Circuit",
        "LowerCourtCaseNumbers": "(25-1234, 25-1235)",
        "ProceedingsandOrder": [
            {"Date": "2025-03-01", "Text": "Application (24A884) for a stay, submitted."},
            {"Date": "2025-04-01", "Text": "Applications (24A884, 24A885) granted."},
        ],
    }
    links = controversy_links(row, payload, government_applicant=True, decided=True)
    court = "united states court of appeals for the ninth circuit"
    assert links.lower_cases == {(court, "25-1234"), (court, "25-1235")}
    assert links.named == {"24A885"}  # its own number is not a link
    assert links.caption == ("kristi noem", "jane doe")
    # A challenger's caption names an agency many challenges share: no caption key.
    assert controversy_links(row, None, government_applicant=False, decided=True) == _links(
        "24A884"
    )
    # Undecided at the cut: the disposing order had not happened, so it links nothing.
    assert not controversy_links(row, payload, government_applicant=True, decided=False).named


def test_controversies_are_the_connected_sets_of_any_link() -> None:
    ids = group_controversies(
        [
            _links("24A95", lower={("ca9", "25-1")}),
            _links("24A105", lower={("ca9", "25-1")}, named={"24A300"}),
            _links("24A300"),  # joined through 24A105's order
            _links("24A400", caption=("noem", "doe"), filed=date(2025, 3, 1)),
            _links("25A1", caption=("noem", "doe"), filed=date(2025, 4, 1)),
            _links("24A500", lower={("ca1", "25-1")}),  # same number, another court
            _links("24A600", named={"24A999"}),  # names an application outside the cut
        ]
    )
    assert ids == {
        "24A95": "24A95",
        "24A105": "24A95",
        "24A300": "24A95",
        "24A400": "24A400",
        "25A1": "24A400",
        "24A500": "24A500",
        "24A600": "24A600",
    }


def test_a_controversy_takes_its_last_decided_application() -> None:
    """Won at the first application, lost on the renewed one: the controversy is a loss."""
    noem = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
    board = "Kristi Noem, Secretary of Homeland Security v. Board of Education"
    rows = [
        _app("scotus/1", noem, "24A900", date(2025, 3, 1), Disposition.granted),
        _app(
            "scotus/2",
            noem,
            "24A950",
            date(2025, 4, 1),
            Disposition.denied,
            decided=date(2025, 5, 1),
        ),
        _app("scotus/3", board, "24A960", date(2025, 4, 2), Disposition.withdrawn),
    ]
    result = _success(
        rows,
        as_of_field="filed",
        through=None,
        since=None,
        corpus_sha256="",
        scope_rule_version=EXEC_ACTION_RULE_VERSION,
        fetch=None,
        reading="registered",
        latest_pull=None,
        latest_snapshot=None,
    )
    assert result.controversy_rule_version == CONTROVERSY_RULE_VERSION
    cells = {(c.administration, c.filer): c for c in result.controversy_cells}
    government = cells[("trump-47", "government")]
    assert (government.controversies, government.applications) == (2, 3)
    assert (government.determinate, government.indeterminate, government.wins) == (1, 1, 0)
    assert government.success_rate == 0
    assert cells[("trump-47", "all")].controversies == 2
    listed = {row.docket_number: row.controversy_id for row in result.review_rows}
    assert listed == {"24A900": "24A900", "24A950": "24A900", "24A960": "24A960"}


def test_controversy_cells_sit_beside_the_application_cells(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _success_corpus(db)
    with corpus.connect(db) as conn:
        result = executive_success(conn, as_of_field="filed")
    cells = {(c.administration, c.filer): c for c in result.controversy_cells}
    # One caption joins every government application: 25A10, filed in September,
    # is within CAPTION_LINK_DAYS of the March ones. The last decided, a grant, wins.
    government = cells[("trump-47", "government")]
    assert (government.controversies, government.applications, government.wins) == (1, 7, 1)
    listed = {row.docket_number: row for row in result.review_rows}
    assert listed["25A10"].controversy_id == "24A900"
    # Challengers' applications share no caption key and no snapshot: one controversy each.
    challenger = cells[("biden-46", "challenger")]
    assert (challenger.controversies, challenger.determinate, challenger.wins) == (3, 2, 1)
    # The unknown-scope row is listed but never grouped.
    assert listed["24A104"].controversy_id is None


_NOEM = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
_OHIO = "Ohio, et al. v. Environmental Protection Agency, et al."


def _grouped(
    rows: Sequence[corpus.CorpusRow],
    payloads: dict[str, dict[str, object]] | None = None,
    *,
    as_of_field: str = "filed",
) -> ExecutiveSuccess:
    found = payloads or {}

    def fetch(wanted: Sequence[corpus.CorpusRow]) -> list[Payload]:
        return [found.get(row.docket_number) for row in wanted]

    return _success(
        rows,
        as_of_field=as_of_field,
        through=None,
        since=None,
        corpus_sha256="",
        scope_rule_version=EXEC_ACTION_RULE_VERSION,
        fetch=fetch,
        reading="registered",
        latest_pull=None,
        latest_snapshot=None,
    )


def _ids(result: ExecutiveSuccess) -> dict[str, str | None]:
    return {row.docket_number: row.controversy_id for row in result.review_rows}


def _controversy_cells(
    result: ExecutiveSuccess,
) -> dict[tuple[str | None, str], ExecutiveControversyCell]:
    return {(c.administration, c.filer): c for c in result.controversy_cells}


def test_one_order_deciding_both_sides_is_a_both_controversy() -> None:
    order = _live("24A900", "Applications (24A900, 24A100) granted.", "2025-03-10")
    rows = [
        _app("scotus/1", _NOEM, "24A900", date(2025, 3, 1), Disposition.granted),
        _app("scotus/2", _OHIO, "24A100", date(2025, 3, 2), Disposition.granted),
    ]
    result = _grouped(rows, {"24A900": order})
    assert _ids(result) == {"24A100": "24A100", "24A900": "24A100"}
    both = _controversy_cells(result)[("trump-47", "both")]
    assert (both.controversies, both.applications, both.determinate) == (1, 2, 1)
    # The challenger's grant, decided last, decides it: the executive lost.
    assert (both.wins, result.controversy_unlinked) == (0, 1)
    assert _controversy_cells(result)[("trump-47", "all")].controversies == 1


def test_the_case_below_links_challengers_and_absent_snapshots_are_counted() -> None:
    below: dict[str, object] = {
        "LowerCourt": "United States Court of Appeals for the Fifth Circuit",
        "LowerCourtCaseNumbers": "(24-60231)",
    }
    rows = [
        _app("scotus/1", _OHIO, "24A100", date(2024, 7, 1), Disposition.denied),
        _app("scotus/2", _OHIO, "24A101", date(2024, 7, 2), Disposition.denied),
        _app("scotus/3", _OHIO, "24A102", date(2024, 7, 3), Disposition.granted),
    ]
    result = _grouped(rows, {"24A100": below, "24A101": below})
    assert _ids(result) == {"24A100": "24A100", "24A101": "24A100", "24A102": "24A102"}
    challenger = _controversy_cells(result)[("biden-46", "challenger")]
    assert (challenger.controversies, challenger.wins, challenger.determinate) == (2, 1, 2)
    assert result.controversy_unlinked == 1


def test_a_same_day_tie_goes_to_the_later_docketed_application() -> None:
    """24A105 is docketed after 24A95 though it sorts first as a string."""
    rows = [
        _app("scotus/1", _NOEM, "24A95", date(2025, 3, 1), Disposition.granted),
        _app("scotus/2", _NOEM, "24A105", date(2025, 3, 1), Disposition.denied),
    ]
    result = _grouped(rows)
    assert _ids(result) == {"24A105": "24A95", "24A95": "24A95"}
    assert _controversy_cells(result)[("trump-47", "government")].wins == 0


def test_a_controversy_takes_its_first_dated_applications_administration() -> None:
    rows = [
        _app("scotus/1", _NOEM, "24A10", date(2025, 1, 10), None),
        _app(
            "scotus/2",
            _NOEM,
            "24A11",
            date(2025, 1, 15),
            Disposition.granted,
            decided=date(2025, 3, 1),
        ),
    ]
    # Filed: the first application, filed before the transition, places it.
    filed = _controversy_cells(_grouped(rows))
    assert set(filed) == {("biden-46", "government"), ("biden-46", "all")}
    # Resolved: the first is pending and undated, so the decided one places it.
    resolved = _controversy_cells(_grouped(rows, as_of_field="resolved"))
    assert resolved[("trump-47", "government")].wins == 1


def test_spelling_and_parsing_do_not_break_the_grouping() -> None:
    rows = [
        _app("scotus/1", _NOEM, "24a900 ", date(2025, 3, 1), Disposition.granted),
        _app("scotus/2", _NOEM, "24A901", date(2025, 3, 2), Disposition.granted, kind=None),
        _app("scotus/3", _NOEM, "24A902", date(2025, 3, 3), Disposition.denied),
    ]
    order = _live("24A902", "Applications (24A900, 24A902) denied.", "2025-03-03")
    result = _grouped(rows, {"24A902": order})
    # A lower-case, padded number is grouped under its own spelling; the
    # never-parsed row is counted beside its cell and grouped with nothing.
    assert _ids(result) == {"24A901": None, "24A902": "24a900 ", "24a900 ": "24a900 "}


# Submission entries as the docket records them (scotus 17A132, 23A55, 17A212, 22A702).
_OVERLENGTH_ASKS = [
    "Application (17A132) of Donald J. Trump, President of the United States, et al. "
    + "to file a consolidated petitioners' brief on the merits and a consolidated reply "
    + "brief on the merits in excess of the word limits, submitted to The Chief Justice.",
    "Application (23A55) for leave to file briefs on the merits in excess of the word "
    + "limits, submitted to Justice Alito.",
    "Application (17A212) to file petition for a writ of certiorari in excess of page "
    + "limits, submitted to Justice Kagan.",
    "Application (22A702) of the parties to file consolidated briefs on the merits in "
    + "excess of the word limits, submitted to Justice Barrett.  VIDED.",
]


@pytest.mark.parametrize("ask", _OVERLENGTH_ASKS)
def test_an_overlength_request_is_read_from_its_submission_entry(ask: str) -> None:
    granted = "Application granted by The Chief Justice."
    assert is_overlength_request([ask, granted])


@pytest.mark.parametrize(
    "texts",
    [
        # A stay is substantive whatever a later entry says about word limits.
        [
            "Application (24A1) for a stay, submitted to Justice Alito.",
            "Application (24A2) to file a response in excess of the word limit granted.",
        ],
        ["Application (24A1) to extend the time to file a petition, submitted to Justice Alito."],
        # A filer named first, then a stay and leave together: the stay makes it substantive.
        [
            "Application (17A132) of Donald J. Trump, President of the United States, et al. "
            + "for a stay pending appeal and for leave to file in excess of the word limits, "
            + "submitted to The Chief Justice."
        ],
        ["Response to application filed in excess of the word limit."],  # no ask clause
        [],
    ],
)
def test_other_asks_are_not_overlength_requests(texts: list[str]) -> None:
    assert not is_overlength_request(texts)


def _submitted(docket: str, ask: str, day: str = "2025-03-01") -> dict[str, object]:
    """A live payload whose only entry is the application's submission."""
    return {"ProceedingsandOrder": [{"Date": day, "Text": f"Application ({docket}) {ask}"}]}


def test_v2_sets_a_procedural_request_out_of_scope() -> None:
    fcc = "Federal Communications Commission, et al. v. Consumers' Research, et al."
    row = _app("scotus/1", fcc, "24A754", date(2025, 1, 24), Disposition.granted, kind="unknown")
    payload = _submitted(
        "24A754",
        "for leave to file a consolidated response brief on the merits in excess of the "
        + "word limit, submitted to Justice Alito.",
    )
    annotation = exec_action_annotations_v2(row, row.date_filed, payload)
    assert (annotation.reason, annotation.in_scope) == ("procedural-request", False)
    assert annotation.government_side == "applicant"
    # v1 reads the caption only, and so does v2 without the snapshot.
    assert exec_action_annotations(row, row.date_filed, payload).reason == "gov-applicant"
    assert exec_action_annotations_v2(row, row.date_filed).reason == "gov-applicant"
    # A stored substantive ask is never re-read.
    substantive = _app("scotus/2", fcc, "24A755", date(2025, 1, 24), Disposition.granted)
    assert exec_action_annotations_v2(substantive, None, payload).reason == "gov-applicant"
    # No government party: nothing for step 4 to narrow.
    private = _app(
        "scotus/3", "Acme Corp. v. Jane Doe", "24A756", date(2025, 1, 24), None, kind="unknown"
    )
    assert exec_action_annotations_v2(private, None, payload).reason == "no-federal-party"
    # A row the caption already sets out of scope keeps its caption reason.
    prosecution = _app(
        "scotus/4", "John Roe v. United States", "24A757", date(2025, 1, 24), None, kind="unknown"
    )
    assert exec_action_annotations_v2(prosecution, None, payload).reason == "federal-prosecution"


def test_the_cut_leaves_procedural_requests_out_and_dates_undated_rows(tmp_path: Path) -> None:
    """A word-limit grant is no win, and an empty docketed date takes the first entry's."""
    trump = "Donald J. Trump, President of the United States, et al. v. Jane Doe, et al."
    rows = [
        # Undated, procedural: a grant that would read as the government's win.
        _row(
            "scotus/1",
            trump,
            docket_number="17A824",
            date_decided=date(2018, 2, 8),
            disposition=Disposition.granted,
            application_kind="unknown",
        ),
        # Undated, substantive: the transgender-service shape.
        _row(
            "scotus/2",
            trump,
            docket_number="18A625",
            date_decided=date(2019, 1, 22),
            disposition=Disposition.granted,
            application_kind="substantive",
        ),
        # Undated and no snapshot: it keeps no filing date.
        _row(
            "scotus/3",
            trump,
            docket_number="18A700",
            date_decided=date(2019, 2, 1),
            disposition=Disposition.denied,
            application_kind="substantive",
        ),
    ]
    payloads: dict[str, dict[str, object]] = {
        "17A824": _submitted(
            "17A824",
            "for leave to file the brief of petitioners in excess of the word limits, "
            + "submitted to Justice Kennedy.",
            "2018-02-05",
        ),
        "18A625": {
            "ProceedingsandOrder": [
                {"Date": "2018-12-13", "Text": "Application (18A625) for a stay, submitted."},
                {"Date": "2019-01-22", "Text": "Application (18A625) granted."},
            ]
        },
    }
    result = _grouped(rows, payloads)
    listed = {row.docket_number: row for row in result.review_rows}
    assert "17A824" not in listed  # out of scope, so not listed for review
    assert result.scope_reasons["procedural-request"] == 1
    assert (listed["18A625"].date_filed, listed["18A625"].date_source) == (
        date(2018, 12, 13),
        "first-entry",
    )
    assert listed["18A625"].administration == "trump-45"
    assert (listed["18A700"].date_filed, listed["18A700"].date_source) == (None, None)
    assert listed["18A700"].administration is None
    assert result.filed_from_first_entry == 2  # 17A824 and 18A625 took the fallback
    government = _cells(result)[("trump-45", "government")]
    assert (government.rows, government.wins, government.decided) == (1, 1, 1)
    # Under exec-action-v1 the word-limit grant still counts, as a win.
    v1 = _success(
        rows,
        as_of_field="filed",
        through=None,
        since=None,
        corpus_sha256="",
        scope_rule_version=EXEC_ACTION_RULE_VERSION_V1,
        fetch=lambda wanted: [payloads.get(row.docket_number) for row in wanted],
        reading="registered",
        latest_pull=None,
        latest_snapshot=None,
    )
    assert _cells(v1)[("trump-45", "government")].wins == 2


def test_since_skips_reading_undated_rows_that_ended_before_it() -> None:
    fetched: list[str] = []

    def fetch(wanted: Sequence[corpus.CorpusRow]) -> list[Payload]:
        fetched.extend(row.docket_number for row in wanted)
        return [None for _ in wanted]

    rows = [
        _row(
            "scotus/1",
            _NOEM,
            docket_number="16A1",
            date_decided=date(2016, 9, 1),
            disposition=Disposition.denied,
            application_kind="substantive",
        ),
        _row(
            "scotus/2",
            _NOEM,
            docket_number="25A2",
            date_decided=date(2025, 9, 1),
            disposition=Disposition.denied,
            application_kind="substantive",
        ),
    ]
    _success(
        rows,
        as_of_field="filed",
        through=None,
        since=date(2017, 1, 20),
        corpus_sha256="",
        scope_rule_version=EXEC_ACTION_RULE_VERSION,
        fetch=fetch,
        reading="registered",
        latest_pull=None,
        latest_snapshot=None,
    )
    assert "16A1" not in fetched
    assert "25A2" in fetched


def _referred(
    docket: str, decided: str, court: str = "D.C. Circuit", opinion: str = "opinion"
) -> dict[str, object]:
    """One cluster's companion order, as the Court enters it on each docket.

    The lead docket links the detached opinion where its companions name it.
    """
    order = (
        f"Application ({docket}) for stay presented to The Chief Justice and by him referred "
        + "to the Court is denied.  Justice Thomas would grant the application. "
        + f"(detached {opinion})"
    )
    return {
        "LowerCourt": court,
        "LowerCourtCaseNumbers": f"({docket[-3:]}-1)",  # a different case below each
        "ProceedingsandOrder": [
            {"Date": "2024-07-23", "Text": f"Application ({docket}) for a stay, submitted."},
            {"Date": decided, "Text": order},
        ],
    }


def test_one_order_text_on_one_day_joins_a_cluster_across_cases_below() -> None:
    west_virginia = "West Virginia, et al. v. Environmental Protection Agency, et al."
    edison = "Edison Electric Institute, et al. v. Environmental Protection Agency, et al."
    labor = "Acme Corp. v. Department of Labor, et al."
    decided = date(2024, 10, 16)
    rows = [
        _app(
            "scotus/1",
            west_virginia,
            "24A95",
            date(2024, 7, 23),
            Disposition.denied,
            decided=decided,
        ),
        _app("scotus/2", edison, "24A116", date(2024, 7, 29), Disposition.denied, decided=decided),
        _app("scotus/3", _OHIO, "24A117", date(2024, 7, 29), Disposition.denied, decided=decided),
        # The same text on another day joins nothing.
        _app(
            "scotus/4",
            _OHIO,
            "24A300",
            date(2024, 9, 1),
            Disposition.denied,
            decided=date(2024, 11, 1),
        ),
        # The same text and day against another agency joins nothing.
        _app("scotus/5", labor, "24A301", date(2024, 9, 2), Disposition.denied, decided=decided),
    ]
    payloads = {
        "24A95": _referred(
            "24A95", "2024-10-16", opinion="<a href='https://example.test/24a95.pdf'>opinion</a>"
        ),
        "24A116": _referred("24A116", "2024-10-16"),
        "24A117": _referred("24A117", "2024-10-16"),
        "24A300": _referred("24A300", "2024-11-01"),
        "24A301": _referred("24A301", "2024-10-16"),
    }
    ids = _ids(_grouped(rows, payloads))
    assert ids["24A116"] == ids["24A117"] == ids["24A95"] == "24A95"
    assert ids["24A300"] == "24A300"
    assert ids["24A301"] == "24A301"


def test_a_shared_caption_joins_only_close_in_time_and_court() -> None:
    biden = "Joseph R. Biden, Jr., President of the United States, et al. v. Missouri, et al."
    eighth: dict[str, object] = {"LowerCourt": "Eighth Circuit"}
    fifth: dict[str, object] = {"LowerCourt": "Fifth Circuit"}
    rows = [
        # A vaccine rule in 2021 and a loan plan in 2024: one caption, two policies.
        _app(
            "scotus/1",
            biden,
            "21A240",
            date(2021, 12, 16),
            Disposition.granted,
            decided=date(2022, 1, 13),
        ),
        _app(
            "scotus/2",
            biden,
            "24A173",
            date(2024, 8, 13),
            Disposition.denied,
            decided=date(2024, 8, 28),
        ),
        # Renewed on the next appeal within weeks: one controversy.
        _app(
            "scotus/3",
            biden,
            "24A190",
            date(2024, 9, 20),
            Disposition.granted,
            decided=date(2024, 10, 1),
        ),
        # Close in time but from another circuit: apart.
        _app(
            "scotus/4",
            biden,
            "24A200",
            date(2024, 9, 25),
            Disposition.denied,
            decided=date(2024, 10, 2),
        ),
    ]
    payloads = {"21A240": eighth, "24A173": eighth, "24A190": eighth, "24A200": fifth}
    ids = _ids(_grouped(rows, payloads))
    assert ids["21A240"] == "21A240"
    assert ids["24A173"] == ids["24A190"] == "24A173"
    assert ids["24A200"] == "24A200"


def test_an_undated_row_decided_after_the_cut_but_filed_before_it_is_pending() -> None:
    """The first entry places it in the window; its later decision had not happened."""
    row = _row(
        "scotus/1",
        _NOEM,
        docket_number="25A50",
        date_decided=date(2025, 11, 1),
        disposition=Disposition.granted,
        application_kind="substantive",
    )
    payload = _submitted("25A50", "for a stay, submitted to Justice Alito.", "2025-09-01")
    result = _success(
        [row],
        as_of_field="filed",
        through=date(2025, 10, 1),
        since=None,
        corpus_sha256="",
        scope_rule_version=EXEC_ACTION_RULE_VERSION,
        fetch=lambda wanted: [payload for _ in wanted],
        reading="registered",
        latest_pull=None,
        latest_snapshot=None,
    )
    assert (result.applications, result.filed_after_through) == (1, 0)
    government = _cells(result)[("trump-47", "government")]
    assert (government.rows, government.pending, government.decided) == (1, 1, 0)


def test_one_order_text_on_one_day_needs_one_court_below() -> None:
    decided = date(2024, 10, 16)
    rows = [
        _app("scotus/1", _OHIO, "24A117", date(2024, 7, 29), Disposition.denied, decided=decided),
        _app("scotus/2", _OHIO, "24A118", date(2024, 7, 29), Disposition.denied, decided=decided),
    ]
    payloads = {
        "24A117": _referred("24A117", "2024-10-16"),
        "24A118": _referred("24A118", "2024-10-16", court="Fifth Circuit"),
    }
    assert _ids(_grouped(rows, payloads)) == {"24A117": "24A117", "24A118": "24A118"}


def test_a_shared_caption_runs_from_a_pending_applications_filing_and_needs_a_date() -> None:
    rows = [
        # Pending at the cut: the window runs from its filing.
        _app("scotus/1", _NOEM, "25A10", date(2025, 3, 1), None),
        _app("scotus/2", _NOEM, "25A20", date(2025, 5, 1), Disposition.granted),
        _app("scotus/3", _NOEM, "25A30", date(2026, 1, 15), Disposition.granted),
        # No filing date at all, and no snapshot to date it: it caption-joins nothing.
        _row(
            "scotus/4",
            _NOEM,
            docket_number="25A40",
            disposition=Disposition.granted,
            application_kind="substantive",
        ),
    ]
    ids = _ids(_grouped(rows))
    assert ids["25A10"] == ids["25A20"] == "25A10"
    assert ids["25A30"] == "25A30"  # more than 210 days after 25A20's decision
    assert ids["25A40"] == "25A40"
