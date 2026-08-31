"""The stored-spelling convergence: marked docket numbers, and what must not match."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.docket_marking_migration import normalize_docket_markings

runner = CliRunner()

_MARKED = "19-1094 *** CAPITAL CASE ***"
_CLEAN = "19-1094"
# The shape the word match exists to protect: a circuit docket using `***` as a
# separator between numbers, which a shape match would eat a whole number out of.
_CONSOLIDATED = "Docket 17-2737***; 17-2741***; 17-2994***; August Term, 2017"


def _row(case_id: str, docket_number: str, *, court: str = "scotus") -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {"case_id": case_id, "court": court, "docket_number": docket_number}
    )


@contextmanager
def _seeded(tmp_path: Path, rows: list[corpus.CorpusRow]) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        conn.commit()
        yield conn


def _stored(tmp_path: Path, case_id: str) -> corpus.CorpusRow:
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        row = corpus.get_row(conn, case_id)
    assert row is not None
    return row


def test_dry_run_reports_the_rewrite_and_writes_nothing(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]) as conn:
        result = normalize_docket_markings(conn, apply=False)
        assert result.applied is False
        assert [(e.case_id, e.was, e.now) for e in result.rewritten] == [
            ("scotus/1", _MARKED, _CLEAN)
        ]
        stored = corpus.get_row(conn, "scotus/1")
    assert stored is not None
    assert stored.docket_number == _MARKED  # untouched
    assert stored.capital_case is False


def test_apply_rewrites_the_number_and_raises_the_flag(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]) as conn:
        result = normalize_docket_markings(conn, apply=True, max_rewrites=10)
    assert result.applied is True and result.refused is False
    stored = _stored(tmp_path, "scotus/1")
    assert stored.docket_number == _CLEAN
    assert stored.capital_case is True


def test_a_consolidated_circuit_docket_is_never_rewritten(tmp_path: Path) -> None:
    """The word match is the only thing protecting this row.

    Selection is court-agnostic, so nothing but the marking's wording keeps a
    consolidated docket that uses ``***`` as a *separator* out of the population —
    and a shape match would delete a whole docket number out of the column that is
    the record. Seeded on both courts so the protection is shown to be the wording
    rather than a court filter.
    """
    rows = [_row("ca2/1", _CONSOLIDATED, court="ca2"), _row("scotus/2", _CONSOLIDATED)]
    with _seeded(tmp_path, rows) as conn:
        result = normalize_docket_markings(conn, apply=True, max_rewrites=10)
    assert result.rewritten == []
    for case_id in ("ca2/1", "scotus/2"):
        stored = _stored(tmp_path, case_id)
        assert stored.docket_number == _CONSOLIDATED
        assert stored.capital_case is False


def test_a_marked_row_outside_scotus_is_still_repaired(tmp_path: Path) -> None:
    """The corpus check this drains is court-agnostic, so the repair is too."""
    with _seeded(tmp_path, [_row("ca9/1", _MARKED, court="ca9")]) as conn:
        result = normalize_docket_markings(conn, apply=True, max_rewrites=10)
    assert [e.case_id for e in result.rewritten] == ["ca9/1"]
    assert _stored(tmp_path, "ca9/1").docket_number == _CLEAN


def test_the_rewrite_leaves_the_identity_join_key_unchanged(tmp_path: Path) -> None:
    """Why the rewrite cannot mint a duplicate pair for the dedupe pass to find.

    Both channels reconcile on ``norm_dn``, which strips the annotation by shape,
    so the marked and marking-free spellings already compare equal to the join: no
    row moves into or out of a group, and the pair set is identical either side of
    the rewrite.
    """
    assert corpus.normalize_docket_number(_MARKED) == corpus.normalize_docket_number(_CLEAN)


def test_a_row_already_sharing_an_identity_is_flagged_not_skipped(tmp_path: Path) -> None:
    """A pre-existing collision is reported, and still repaired.

    The rewrite neither creates the collision (the join normalized the marking away
    already) nor resolves it — that is the dedupe pass's work — so leaving the
    marking in place would strand the row for no gain.
    """
    rows = [_row("scotus/1", _MARKED), _row("scotus/2", _CLEAN)]
    with _seeded(tmp_path, rows) as conn:
        result = normalize_docket_markings(conn, apply=False)
    assert [(e.case_id, e.shares_identity) for e in result.rewritten] == [("scotus/1", True)]


def test_apply_is_idempotent(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]) as conn:
        normalize_docket_markings(conn, apply=True, max_rewrites=10)
        again = normalize_docket_markings(conn, apply=True, max_rewrites=10)
    assert again.rewritten == []
    assert _stored(tmp_path, "scotus/1").capital_case is True


def test_the_bound_refuses_and_writes_nothing(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]) as conn:
        result = normalize_docket_markings(conn, apply=True, max_rewrites=0)
    assert result.refused is True and result.applied is False
    assert _stored(tmp_path, "scotus/1").docket_number == _MARKED


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["normalize-docket-markings"])
    assert dry.exit_code == 0, dry.output
    assert "would rewrite 1 marked docket number(s)" in dry.output
    assert _stored(tmp_path, "scotus/1").docket_number == _MARKED

    applied = runner.invoke(app, ["normalize-docket-markings", "--apply", "--max-rewrites", "5"])
    assert applied.exit_code == 0, applied.output
    assert "rewrote 1 marked docket number(s)" in applied.output
    assert _stored(tmp_path, "scotus/1").docket_number == _CLEAN

    again = runner.invoke(app, ["normalize-docket-markings"])
    assert again.exit_code == 0, again.output
    assert "would rewrite 0 marked docket number(s)" in again.output  # idempotent


def test_cli_apply_requires_an_explicit_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The maintainer states the number they read in the dry run; no default applies."""
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["normalize-docket-markings", "--apply"])
    assert result.exit_code == 2
    assert "--apply requires an explicit --max-rewrites" in result.output
    assert _stored(tmp_path, "scotus/1").docket_number == _MARKED


def test_cli_apply_refuses_above_the_bound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _seeded(tmp_path, [_row("scotus/1", _MARKED)]):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["normalize-docket-markings", "--apply", "--max-rewrites", "0"])
    assert result.exit_code == 1
    assert "refusing to apply 1 rewrites (--max-rewrites 0)" in result.output
    assert _stored(tmp_path, "scotus/1").docket_number == _MARKED


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["normalize-docket-markings"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.output
