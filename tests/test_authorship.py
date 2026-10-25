"""The authorship tally: who has written from each argument sitting, as of a day."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus, provision
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cascade
from fedcourtsai.pipeline.authorship import authorship_tally, tally_record
from fedcourtsai.schemas import AuthorshipTally
from fedcourtsai.serialize import read_model
from fedcourtsai.supremecourt import ArgumentSitting

_OCTOBER = ArgumentSitting(2025, date(2025, 10, 6), date(2025, 10, 15))
_NOVEMBER = ArgumentSitting(2025, date(2025, 11, 3), date(2025, 11, 12))


def _opinion(
    case_id: str | None, docket: str, argued: str, decided: str, kind: str, author: str | None
) -> tuple[object, ...]:
    return (2025, docket, 1, docket, case_id, argued, decided, kind, author)


def _seed(tmp_path: Path) -> Path:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    rows = [
        corpus.CorpusRow(
            case_id="scotus/1",
            court="scotus",
            docket_number="24-1",
            merits_argued=date(2025, 10, 6),
            merits_decided=date(2026, 1, 20),
        ),
        corpus.CorpusRow(
            case_id="scotus/2",
            court="scotus",
            docket_number="24-2",
            merits_argued=date(2025, 10, 7),
            merits_decided=date(2026, 3, 4),
        ),
        # Argued, then dismissed with no opinion: decided, no author.
        corpus.CorpusRow(
            case_id="scotus/3",
            court="scotus",
            docket_number="24-3",
            merits_argued=date(2025, 10, 14),
            merits_decided=date(2025, 12, 1),
        ),
        corpus.CorpusRow(
            case_id="scotus/4",
            court="scotus",
            docket_number="25-4",
            merits_argued=date(2025, 11, 4),
        ),
        # Between the sittings: in none.
        corpus.CorpusRow(
            case_id="scotus/5",
            court="scotus",
            docket_number="25-5",
            merits_argued=date(2025, 10, 25),
        ),
    ]
    opinions = [
        _opinion("scotus/1", "24-1", "2025-10-06", "2026-01-20", "opinion-of-the-court", "Kagan"),
        _opinion("scotus/2", "24-2", "2025-10-07", "2026-03-04", "plurality", "Alito"),
        # Linked to no corpus row: keyed by its docket.
        _opinion(None, "24-9", "2025-10-08", "2026-02-01", "per-curiam", None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_argument_sittings(conn, [_NOVEMBER, _OCTOBER], read_at=date(2026, 6, 1))
        conn.executemany(
            "INSERT INTO opinions (term, listing_number, position, docket, case_id, argued, "
            "decided, kind, author, words, word_rule, document_url, read_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 10, 'w/1', 'u', '2026-06-01')",
            opinions,
        )
        conn.commit()
    return db


def test_the_tally_reads_each_sitting_as_of_the_day(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    with corpus.connect_readonly(db) as conn:
        late = authorship_tally(conn, term=2025, as_of=date(2026, 3, 10))
        early = authorship_tally(conn, term=2025, as_of=date(2026, 1, 25))
        before = authorship_tally(conn, term=2025, as_of=date(2025, 10, 7))
    october, november = late
    assert october.sitting == _OCTOBER and november.sitting == _NOVEMBER
    assert [case.key for case in october.cases] == [
        "scotus/1",
        "scotus/2",
        "docket:24-9",
        "scotus/3",
    ]
    assert october.authors == ("Kagan", "Alito") and not october.undecided
    assert "Kagan" not in october.yet_to_write and "Alito" not in october.yet_to_write
    assert len(october.yet_to_write) == len(october.bench) - 2
    assert [case.key for case in november.undecided] == ["scotus/4"]
    # Earlier, the plurality is not yet out: its case is undecided, its author unread.
    october_then = early[0]
    assert october_then.authors == ("Kagan",)
    assert [case.key for case in october_then.undecided] == ["scotus/2"]
    # Before the November sitting opened, and before the October one closed.
    assert [tally.sitting for tally in before] == [_OCTOBER]
    assert [case.key for case in before[0].cases] == ["scotus/1", "scotus/2"]


def test_no_stored_sittings_is_an_empty_tally(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db):
        pass
    with corpus.connect_readonly(db) as conn:
        assert authorship_tally(conn, term=2025, as_of=date(2026, 6, 1)) == []
        assert corpus.argument_sittings(conn) == []


def _seed_one(
    tmp_path: Path, rows: list[corpus.CorpusRow], opinions: list[tuple[object, ...]]
) -> Path:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_argument_sittings(conn, [_OCTOBER, _NOVEMBER], read_at=date(2026, 6, 1))
        conn.executemany(
            "INSERT INTO opinions (term, listing_number, position, docket, case_id, argued, "
            "decided, kind, author, dockets, words, word_rule, document_url, read_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 10, 'w/1', 'u', '2026-06-01')",
            opinions,
        )
        conn.commit()
    return db


def _row(case_id: str, docket: str, argued: date) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id, court="scotus", docket_number=docket, merits_argued=argued
    )


def test_an_unlinked_opinion_joins_its_docket_s_row(tmp_path: Path) -> None:
    db = _seed_one(
        tmp_path,
        [_row("scotus/1", "24-1", date(2025, 10, 6))],
        [
            (
                2025,
                "1",
                1,
                "24-1",
                None,
                "2025-10-06",
                "2026-01-20",
                "opinion-of-the-court",
                "Kagan",
                '["24-1"]',
            )
        ],
    )
    with corpus.connect_readonly(db) as conn:
        october = authorship_tally(conn, term=2025, as_of=date(2026, 1, 25))[0]
    assert [(case.key, case.author, case.recorded) for case in october.cases] == [
        ("scotus/1", "Kagan", True)
    ]


def test_a_case_sits_once_where_its_opinion_places_it(tmp_path: Path) -> None:
    db = _seed_one(
        tmp_path,
        [_row("scotus/2", "24-2", date(2025, 10, 7))],
        [
            (
                2025,
                "2",
                1,
                "24-2",
                "scotus/2",
                "2025-11-04",
                "2026-03-04",
                "opinion-of-the-court",
                "Alito",
                '["24-2"]',
            )
        ],
    )
    with corpus.connect_readonly(db) as conn:
        october, november = authorship_tally(conn, term=2025, as_of=date(2026, 3, 10))
    assert october.cases == ()
    assert [(case.key, case.argued, case.author) for case in november.cases] == [
        ("scotus/2", date(2025, 11, 4), "Alito")
    ]


def test_a_decision_folds_in_its_consolidated_dockets(tmp_path: Path) -> None:
    db = _seed_one(
        tmp_path,
        [_row("scotus/1", "24-1", date(2025, 10, 6)), _row("scotus/7", "24-7", date(2025, 10, 6))],
        [
            (
                2025,
                "1",
                1,
                "24-1",
                "scotus/1",
                "2025-10-06",
                "2026-01-20",
                "opinion-of-the-court",
                "Kagan",
                '["24-1", "24-7"]',
            )
        ],
    )
    with corpus.connect_readonly(db) as conn:
        before = authorship_tally(conn, term=2025, as_of=date(2026, 1, 1))[0]
        after = authorship_tally(conn, term=2025, as_of=date(2026, 1, 25))[0]
    # Before the decision, one case per docket; after it, one case.
    assert [case.key for case in before.undecided] == ["scotus/1", "scotus/7"]
    assert [case.key for case in after.cases] == ["scotus/1"] and not after.undecided


def test_a_decision_the_record_has_not_read_is_unrecorded(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    with corpus.connect_readonly(db) as conn:
        october = authorship_tally(conn, term=2025, as_of=date(2026, 3, 10))[0]
    # scotus/3 was dismissed after argument: decided, with no opinion read.
    assert [case.key for case in october.unrecorded] == ["scotus/3"]


def test_a_blob_without_the_sittings_table_reads_as_none(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        conn.execute("DROP TABLE argument_sittings")
        conn.commit()
    with corpus.connect_readonly(db, migrate=False) as conn:
        assert corpus.argument_sittings(conn) == []
        assert authorship_tally(conn, term=2025, as_of=date(2026, 6, 1)) == []


# --- a merits cell's record ----------------------------------------------------

_ARGUED = "evt-argument-judgment"


def test_only_the_post_argument_moment_carries_a_tally() -> None:
    assert provision.carries_authorship_tally(_ARGUED)
    assert not provision.carries_authorship_tally("evt-petition-disposition")
    assert not provision.carries_authorship_tally("evt-order-judgment")


def test_the_tally_reads_through_the_day_before_the_exclusive_cutoff() -> None:
    snapshot = date(2026, 1, 25)
    assert provision.authorship_tally_as_of(date(2026, 1, 21), snapshot, "forward") == date(
        2026, 1, 20
    )
    assert provision.authorship_tally_as_of(None, snapshot, "forward") == snapshot
    # Argument days and sittings are as stored now, which a replay cell's moment predates.
    assert provision.authorship_tally_as_of(date(2026, 1, 21), snapshot, "replay") is None
    assert provision.authorship_tally_as_of(None, snapshot, "replay") is None


def test_a_cell_is_given_the_tally_of_the_term_in_progress(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    with corpus.connect_readonly(db) as conn:
        after = provision.authorship_tally_for(
            conn, _ARGUED, cutoff=date(2026, 1, 21), snapshot_date=date(2026, 1, 25), mode="forward"
        )
        on = provision.authorship_tally_for(
            conn, _ARGUED, cutoff=date(2026, 1, 20), snapshot_date=date(2026, 1, 25), mode="forward"
        )
        cert = provision.authorship_tally_for(
            conn,
            "evt-petition-disposition",
            cutoff=None,
            snapshot_date=date(2026, 1, 25),
            mode="forward",
        )
    assert after is not None and after.term == 2025 and after.as_of == date(2026, 1, 20)
    assert ("scotus/1", "Kagan") in {(case.key, case.author) for case in after.sittings[0].cases}
    # A decision on the cutoff day itself is not read.
    assert on is not None and all(case.author is None for case in on.sittings[0].cases)
    assert cert is None


def _placement() -> provision.Placement:
    return provision.Placement(
        snapshot_date=date(2026, 1, 25),
        payload={},
        documents=[],
        provenance="as-stored",
        boundary=None,
        dropped_entries=0,
        dropped_documents=0,
    )


def test_the_record_carries_the_tally_only_once_it_is_released(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    paths = CasePaths(tmp_path / "data", "scotus", 1)
    tally = AuthorshipTally(term=2025, as_of=date(2026, 1, 20))
    held = provision.write_cell_record(
        paths, "scotus/1", _placement(), mode="forward", cutoff=None, authorship_tally=tally
    )
    assert held.authorship_tally is None and not paths.authorship_tally.exists()
    monkeypatch.setattr(provision, "AUTHORSHIP_TALLY_WITHHELD", False)
    written = provision.write_cell_record(
        paths, "scotus/1", _placement(), mode="forward", cutoff=None, authorship_tally=tally
    )
    assert written.authorship_tally == tally
    assert read_model(paths.authorship_tally, AuthorshipTally) == tally
    # The next cell provisioned in the same tree, with no tally, does not inherit it.
    provision.write_cell_record(paths, "scotus/1", _placement(), mode="forward", cutoff=None)
    assert not paths.authorship_tally.exists()


def test_the_cli_and_the_record_write_the_same_file(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    with corpus.connect_readonly(db) as conn:
        tally = authorship_tally(conn, term=2025, as_of=date(2026, 3, 10))
        given = provision.authorship_tally_for(
            conn, _ARGUED, cutoff=date(2026, 3, 11), snapshot_date=date(2026, 3, 12), mode="forward"
        )
    assert given == tally_record(tally, term=2025, as_of=date(2026, 3, 10))


def _boom(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("the tally was read while held back")


def test_a_held_tally_is_never_read_at_either_call_site(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(provision, "authorship_tally_for", _boom)
    db = tmp_path / "absent.db"
    assert (
        cli._read_authorship_tally(
            "local", db, _ARGUED, cutoff=None, snapshot_date=date(2026, 1, 25), mode="forward"
        )
        is None
    )
    placement = _placement()
    read = provision.CellRead(
        latest=None, documents=[], events=[], row=None, cutoff=None, dated=None
    )
    assert (
        cascade._read_authorship_tallies(
            db, "local", {_ARGUED: placement}, {_ARGUED: read}, {_ARGUED: "forward"}
        )
        == {}
    )


def test_a_released_tally_is_read_and_a_bad_one_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(provision, "AUTHORSHIP_TALLY_WITHHELD", False)
    db = _seed(tmp_path)
    tally = cli._read_authorship_tally(
        "local",
        db,
        _ARGUED,
        cutoff=date(2026, 1, 21),
        snapshot_date=date(2026, 1, 25),
        mode="forward",
    )
    assert tally is not None and tally.as_of == date(2026, 1, 20)
    read = provision.CellRead(
        latest=None, documents=[], events=[], row=None, cutoff=date(2026, 1, 21), dated=None
    )
    found = cascade._read_authorship_tallies(
        db, "local", {_ARGUED: _placement()}, {_ARGUED: read}, {_ARGUED: "forward"}
    )
    assert found == {_ARGUED: tally}

    def unreadable(*_args: object, **_kwargs: object) -> None:
        raise ValueError("a sitting before the roster's floor")

    monkeypatch.setattr(provision, "authorship_tally_for", unreadable)
    assert (
        cli._read_authorship_tally(
            "local", db, _ARGUED, cutoff=None, snapshot_date=date(2026, 1, 25), mode="forward"
        )
        is None
    )
    assert "::warning::no authorship tally: a sitting before" in capsys.readouterr().err
    assert (
        cascade._read_authorship_tallies(
            db, "local", {_ARGUED: _placement()}, {_ARGUED: read}, {_ARGUED: "forward"}
        )
        == {}
    )


def test_the_tally_command_prints_the_file_shape(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _seed(tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")
    result = CliRunner().invoke(
        cli.app, ["authorship-tally", "--term", "2025", "--as-of", "2026-03-10"]
    )
    assert result.exit_code == 0, result.output
    printed = AuthorshipTally.model_validate_json(result.stdout)
    assert printed.term == 2025 and [len(s.cases) for s in printed.sittings] == [4, 1]
