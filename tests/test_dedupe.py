"""The live-minted duplicate dedupe: pair detection, safety checks, and the drop."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, dedupe
from fedcourtsai.cli import app
from fedcourtsai.schemas import Disposition
from fedcourtsai.supremecourt import live_docket_id

runner = CliRunner()

# The upstream (CourtListener-keyed) and live-minted ids of one duplicated
# docket: the live id is minted from the Term-form number (Term 25, serial 5184).
_KEEP = "scotus/73274969"
_DROP = f"scotus/{live_docket_id(25, 5184)}"


def _row(case_id: str, docket_number: str, **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket_number,
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def _pair_rows(**kw: object) -> list[corpus.CorpusRow]:
    """The canonical duplicate pair: plain upstream spelling, annotated live one."""
    keep_kw = {k.removeprefix("keep_"): v for k, v in kw.items() if k.startswith("keep_")}
    drop_kw = {k.removeprefix("drop_"): v for k, v in kw.items() if k.startswith("drop_")}
    return [
        _row(_KEEP, "25-5184", **keep_kw),
        _row(_DROP, "25-5184 *** CAPITAL CASE ***", **drop_kw),
    ]


@contextmanager
def _seeded(tmp_path: Path, rows: list[corpus.CorpusRow]) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        yield conn


def test_finds_the_cross_range_pair_and_only_it(tmp_path: Path) -> None:
    rows = [
        *_pair_rows(),
        # Unrelated singletons in both ranges match nothing.
        _row("scotus/73277512", "25-385"),
        _row(f"scotus/{live_docket_id(25, 401)}", "25-401"),
        # Two upstream ids sharing a number are not this rule's pattern.
        _row("scotus/111", "24-9001"),
        _row("scotus/112", "24-9001"),
        # Nor are two live-minted ids sharing one.
        _row(f"scotus/{live_docket_id(24, 501)}", "24-501"),
        _row(f"scotus/{live_docket_id(24, 502)}", "24-501"),
        # Nor a three-row group, even with a live id inside it.
        _row("scotus/113", "23-777"),
        _row("scotus/114", "23-777"),
        _row(f"scotus/{live_docket_id(23, 777)}", "23-777"),
    ]
    with _seeded(tmp_path, rows) as conn:
        pairs = dedupe.find_live_duplicates(conn)
    assert len(pairs) == 1
    assert pairs[0].keep == _KEEP
    assert pairs[0].drop == _DROP
    assert pairs[0].agreed is True


def test_a_disagreeing_pair_is_skipped_and_reported_never_dropped(tmp_path: Path) -> None:
    rows = _pair_rows(
        keep_date_filed=date(2025, 9, 1),
        drop_date_filed=date(2025, 9, 2),
    )
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, apply=True)
        assert result.pairs == 1
        assert result.dropped == []
        assert len(result.skipped) == 1
        assert result.skipped[0].pair.agreed is False
        assert any("date_filed" in c for c in result.skipped[0].conflicts)
        # Both rows survive an apply run: the dry-run report is the triage list.
        assert corpus.get_row(conn, _DROP) is not None


def test_none_on_one_side_agrees_toward_the_richer_value(tmp_path: Path) -> None:
    """A channel that never asserted a fact cannot contradict the one that did —
    and the survivor keeps the richer value the agreement accepted."""
    rows = _pair_rows(drop_disposition=Disposition.denied, drop_date_filed=date(2025, 9, 1))
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, apply=True)
        assert result.dropped == [_DROP]
        kept = corpus.get_row(conn, _KEEP)
    assert kept is not None
    assert kept.disposition == Disposition.denied.value
    assert kept.date_filed == date(2025, 9, 1)


def test_a_date_decided_disagreement_also_skips(tmp_path: Path) -> None:
    """`date_decided` gets the same treatment as the other two facts: a pair
    disagreeing on it lands on the triage list, so a decision date carried by
    only one side is never silently the survivor's problem."""
    rows = _pair_rows(
        keep_date_decided=date(2026, 1, 12),
        drop_date_decided=date(2026, 1, 20),
    )
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, apply=True)
        assert result.dropped == []
        assert any("date_decided" in c for c in result.skipped[0].conflicts)
        assert corpus.get_row(conn, _DROP) is not None


def test_live_only_facts_survive_the_drop(tmp_path: Path) -> None:
    """The merge is the write the missed join withheld: signals only the live
    channel supplies — the conference stamps, the lower-court name, a document,
    a snapshot — move onto the survivor rather than vanishing with the twin."""
    rows = _pair_rows(
        keep_distribution_count=1,
        drop_distribution_count=3,
        drop_distributed_for_conference=date(2026, 1, 9),
        drop_originating_court_name="Supreme Court of Ohio",
        drop_date_cert_denied=date(2026, 1, 12),
    )
    with _seeded(tmp_path, rows) as conn:
        corpus.upsert_snapshot(conn, _DROP, date(2025, 12, 1), {"CaseNumber": "25-5184"})
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=_DROP,
                    kind="petition",
                    url="https://example.test/p.pdf",
                    fetched_at=date(2025, 12, 1),
                    text="petition text",
                )
            ],
        )
        result = dedupe.dedupe_live_rows(conn, apply=True)
        assert result.dropped == [_DROP]
        kept = corpus.get_row(conn, _KEEP)
        assert kept is not None
        assert kept.distribution_count == 3  # max: proceedings only grow
        assert kept.distributed_for_conference == date(2026, 1, 9)
        assert kept.originating_court_name == "Supreme Court of Ohio"
        assert kept.date_cert_denied == date(2026, 1, 12)
        documents = corpus.documents_for_case(conn, _KEEP)
        assert [d.kind for d in documents] == ["petition"]
        snapshot = corpus.latest_snapshot(conn, _KEEP)
        assert snapshot is not None and snapshot[0] == date(2025, 12, 1)


def test_a_survivor_side_document_takes_precedence(tmp_path: Path) -> None:
    """Only the live channel writes documents, so a same-kind document already
    on the survivor is the fresher fetch; the twin's copy is not moved."""
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=_KEEP,
                    kind="petition",
                    url="https://example.test/newer.pdf",
                    fetched_at=date(2026, 2, 1),
                    text="newer",
                ),
                corpus.CaseDocument(
                    case_id=_DROP,
                    kind="petition",
                    url="https://example.test/older.pdf",
                    fetched_at=date(2025, 12, 1),
                    text="older",
                ),
            ],
        )
        dedupe.dedupe_live_rows(conn, apply=True)
        documents = corpus.documents_for_case(conn, _KEEP)
    assert [d.url for d in documents] == ["https://example.test/newer.pdf"]


def test_the_survivor_takes_the_pair_minimum_weight(tmp_path: Path) -> None:
    """The min-latch the missed identity join kept from firing: the live twin's
    weight-1 write asserts the petition was included with certainty, so the
    survivor's inverse inclusion probability regresses to 1 — exactly what the
    ingestion upsert lands when two channels weight one row."""
    rows = _pair_rows(keep_sample_weight=10, drop_sample_weight=1)
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, apply=True)
        assert result.dropped == [_DROP]
        kept = corpus.get_row(conn, _KEEP)
    assert kept is not None
    assert kept.sample_weight == 1


def test_a_missing_weight_reads_as_one(tmp_path: Path) -> None:
    rows = _pair_rows(keep_sample_weight=10)  # the live twin asserts no weight
    with _seeded(tmp_path, rows) as conn:
        pairs = dedupe.find_live_duplicates(conn)
    assert pairs[0].weight == 1


def test_a_dry_run_writes_nothing(tmp_path: Path) -> None:
    rows = _pair_rows(keep_sample_weight=10, drop_sample_weight=1)
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, apply=False)
        assert result.applied is False
        assert result.dropped == [_DROP]
        kept = corpus.get_row(conn, _KEEP)
        assert corpus.get_row(conn, _DROP) is not None
    assert kept is not None
    assert kept.sample_weight == 10


def test_apply_removes_the_dropped_case_from_all_four_tables(tmp_path: Path) -> None:
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=_DROP,
                    court="scotus",
                    kind="petition",
                ),
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=_KEEP,
                    court="scotus",
                    kind="petition",
                ),
            ],
        )
        corpus.upsert_snapshot(conn, _DROP, date(2025, 9, 1), {"docket": {}})
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=_DROP,
                    kind="petition",
                    url="https://example.test/p.pdf",
                    fetched_at=date(2025, 9, 1),
                    text="petition text",
                )
            ],
        )

        result = dedupe.dedupe_live_rows(conn, apply=True)
        assert result.applied is True
        assert result.dropped == [_DROP]

        assert corpus.get_row(conn, _DROP) is None
        for table in ("cases", "events", "snapshots", "documents"):
            count = conn.execute(
                f"SELECT COUNT(*) AS n FROM {table} WHERE case_id = ?", (_DROP,)
            ).fetchone()["n"]
            assert count == 0, table
        # The survivor and its own rows are untouched.
        assert corpus.get_row(conn, _KEEP) is not None
        assert len(corpus.events_for_case(conn, _KEEP)) == 1


def test_a_second_run_finds_nothing(tmp_path: Path) -> None:
    with _seeded(tmp_path, _pair_rows()) as conn:
        first = dedupe.dedupe_live_rows(conn, apply=True)
        second = dedupe.dedupe_live_rows(conn, apply=True)
    assert first.dropped == [_DROP]
    assert second.pairs == 0
    assert second.dropped == []
    assert second.skipped == []


def test_cli_dry_run_reports_and_preserves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, _pair_rows())
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))

    result = runner.invoke(app, ["dedupe-live-rows"])
    assert result.exit_code == 0, result.output
    assert "dry-run" in result.output
    assert "would drop 1 live-minted row(s)" in result.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        assert corpus.get_row(conn, _DROP) is not None

    applied = runner.invoke(app, ["dedupe-live-rows", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "applied" in applied.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        assert corpus.get_row(conn, _DROP) is None


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["dedupe-live-rows"])
    assert result.exit_code == 1
