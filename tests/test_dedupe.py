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
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.pipeline.ingest import UNSAMPLED_WEIGHT
from fedcourtsai.schemas import Disposition, EventKind, Outcome, PredictableEvent
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.supremecourt import live_docket_id

runner = CliRunner()

# The upstream (CourtListener-keyed) and live-minted ids of one duplicated
# docket: the live id is minted from the Term-form number (Term 25, serial 5184).
_KEEP = "scotus/73274969"
_DROP = f"scotus/{live_docket_id(25, 5184)}"
# A minted forecast moment (both halves owed at the mint) and the case-level
# baseline that is not one (its ledger half is owed at first touch or
# resolution), so the two travel differently through a merge.
_MINTED = "evt-petition-arrival-disposition"
_BASELINE = "evt-petition-disposition"


def _event_paths(data_root: Path, case_id: str, event_id: str) -> EventPaths:
    court, _, docket = case_id.partition("/")
    return CasePaths(data_root, court, int(docket)).event(event_id)


def _write_ledger_event(
    data_root: Path, case_id: str, event_id: str, *, with_outcome: bool = True
) -> EventPaths:
    """The committed half of one event: `event.yaml`, and its `outcome.json`."""
    paths = _event_paths(data_root, case_id, event_id)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=event_id, case_id=case_id, kind=EventKind.petition, title="Cert petition"
        ),
    )
    if with_outcome:
        write_json(
            paths.outcome,
            Outcome(
                case_id=case_id,
                event_id=event_id,
                resolved_at=date(2026, 1, 12),
                actual_disposition=Disposition.denied,
                actual_granted=0,
            ),
        )
    return paths


def _corpus_event(case_id: str, event_id: str) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(event_id=event_id, case_id=case_id, court="scotus", kind="petition")


def _move(event_id: str, *, restamp_only: bool = False) -> dedupe.LedgerMove:
    return dedupe.LedgerMove(
        event_id=event_id, from_case=_DROP, to_case=_KEEP, restamp_only=restamp_only
    )


def _write_cell_output(paths: EventPaths) -> None:
    """A committed prediction under an event — the shape no restamp here rewrites."""
    prediction_dir = paths.prediction_dir("claude-baseline", "20260112T000000Z")
    prediction_dir.mkdir(parents=True)
    (prediction_dir / "prediction.json").write_text("{}\n")


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
        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
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
        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
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
        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
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
        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
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
        dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
        documents = corpus.documents_for_case(conn, _KEEP)
    assert [d.url for d in documents] == ["https://example.test/newer.pdf"]


def test_the_survivor_takes_the_pair_minimum_weight(tmp_path: Path) -> None:
    """The min-latch the missed identity join kept from firing: the live twin's
    weight-1 write asserts the petition was included with certainty, so the
    survivor's inverse inclusion probability regresses to 1 — exactly what the
    ingestion upsert lands when two channels weight one row."""
    rows = _pair_rows(keep_sample_weight=10, drop_sample_weight=1)
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
        assert result.dropped == [_DROP]
        kept = corpus.get_row(conn, _KEEP)
    assert kept is not None
    assert kept.sample_weight == 1


def test_a_missing_weight_asserts_nothing_and_is_skipped(tmp_path: Path) -> None:
    """A null is absence, not certainty, so it does not win the minimum.

    Reading it as 1 would make this merge a silent re-weighting of the legacy
    sampling frame: `pull` never writes the column at all, so the
    CourtListener-keyed survivor's null is the common case, and a minimum taken
    over it strips the live twin's sampled weight on the strength of a column
    nobody wrote. The merge observed nothing about the block; it may not decide
    the block's weight.
    """
    # A corpus per case: `_seeded` upserts, and the weight upsert min-latches a
    # stored value, so a shared database would carry one case's 10 into the next
    # and the fall-through would never be reached.
    #
    # The survivor's column was never written; the live twin carries the walk's
    # sampled weight. The pair's only assertion is the 10, and it stands.
    with _seeded(tmp_path / "twin", _pair_rows(drop_sample_weight=10)) as conn:
        assert dedupe.find_live_duplicates(conn)[0].weight == 10
    # Symmetrically on the other side.
    with _seeded(tmp_path / "survivor", _pair_rows(keep_sample_weight=10)) as conn:
        assert dedupe.find_live_duplicates(conn)[0].weight == 10
    # Neither row weighted: the fall-through, and only then.
    with _seeded(tmp_path / "neither", _pair_rows()) as conn:
        assert dedupe.find_live_duplicates(conn)[0].weight == UNSAMPLED_WEIGHT


def test_an_asserted_certainty_still_wins_the_minimum(tmp_path: Path) -> None:
    """Skipping nulls narrows what the minimum reads, never what it means.

    Where both rows weighted, the smaller still wins — the min-latch the missed
    identity join kept from firing.
    """
    rows = _pair_rows(keep_sample_weight=10, drop_sample_weight=1)
    with _seeded(tmp_path, rows) as conn:
        assert dedupe.find_live_duplicates(conn)[0].weight == 1


def test_a_dry_run_writes_nothing(tmp_path: Path) -> None:
    rows = _pair_rows(keep_sample_weight=10, drop_sample_weight=1)
    with _seeded(tmp_path, rows) as conn:
        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=False)
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

        result = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
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
        first = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
        second = dedupe.dedupe_live_rows(conn, tmp_path / "data", apply=True)
    assert first.dropped == [_DROP]
    assert second.pairs == 0
    assert second.dropped == []
    assert second.skipped == []


def test_a_minted_moments_ledger_half_moves_with_its_row(tmp_path: Path) -> None:
    """A minted moment owes both halves at its mint, so re-keying the corpus row
    without the directory leaves the shape `minted_moments_defined_in_ledger`
    fails on — and most minted moments have no re-mint trigger to heal it."""
    data_root = tmp_path / "data"
    old_paths = _write_ledger_event(data_root, _DROP, _MINTED)
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == [_DROP]
        assert result.ledger_moves == [_move(_MINTED)]
        assert [event.event_id for event in corpus.events_for_case(conn, _KEEP)] == [_MINTED]

    new_paths = _event_paths(data_root, _KEEP, _MINTED)
    assert not old_paths.base.exists()
    assert read_model(new_paths.event_file, PredictableEvent).case_id == _KEEP
    assert read_model(new_paths.outcome, Outcome).case_id == _KEEP


def test_a_survivor_side_directory_refuses_the_whole_pair(tmp_path: Path) -> None:
    """Two committed definitions of one moment are a judgement call, not a merge:
    the pair is reported for triage and neither twin is touched at all."""
    data_root = tmp_path / "data"
    _write_ledger_event(data_root, _DROP, _MINTED)
    _write_ledger_event(data_root, _KEEP, _MINTED)
    with _seeded(tmp_path, _pair_rows(drop_originating_court_name="Supreme Court of Ohio")) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED), _corpus_event(_KEEP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == []
        assert result.ledger_moves == []
        assert len(result.skipped) == 1
        assert "exist under both ids" in result.skipped[0].conflicts[0]
        # Nothing of the pair moved: not the rows, not the twin's events, and
        # not the fill-in the merge would otherwise have made on the survivor.
        assert corpus.get_row(conn, _DROP) is not None
        survivor = corpus.get_row(conn, _KEEP)
        assert survivor is not None and survivor.originating_court_name is None
        assert [event.case_id for event in corpus.events_for_case(conn, _DROP)] == [_DROP]
    assert _event_paths(data_root, _DROP, _MINTED).base.is_dir()
    keep_event = read_model(_event_paths(data_root, _KEEP, _MINTED).event_file, PredictableEvent)
    assert keep_event.case_id == _KEEP


def test_committed_cell_output_under_the_moment_refuses_the_pair(tmp_path: Path) -> None:
    """A prediction names its own case id inside its own file, which this move
    does not rewrite — carrying the directory across would trade one broken
    reference for another, so the pair goes to triage instead."""
    data_root = tmp_path / "data"
    paths = _write_ledger_event(data_root, _DROP, _MINTED)
    _write_cell_output(paths)
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == []
        assert "holds committed cell output" in result.skipped[0].conflicts[0]
        assert corpus.get_row(conn, _DROP) is not None
    assert paths.base.is_dir()


def test_cell_output_under_a_baseline_event_refuses_the_pair(tmp_path: Path) -> None:
    """The refusal looks past the moments this merge would move: the row delete
    reaches every event of the twin, so a prediction committed under the
    case-level baseline — which no move carries — would be orphaned all the
    same, into a `ledger_references_exist` failure."""
    data_root = tmp_path / "data"
    minted_paths = _write_ledger_event(data_root, _DROP, _MINTED)
    baseline_paths = _write_ledger_event(data_root, _DROP, _BASELINE)
    _write_cell_output(baseline_paths)
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED), _corpus_event(_DROP, _BASELINE)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == []
        assert result.ledger_moves == []
        assert _BASELINE in result.skipped[0].conflicts[0]
        assert corpus.get_row(conn, _DROP) is not None
    # The minted moment's directory does not move on a refused pair either.
    assert minted_paths.base.is_dir()
    assert not _event_paths(data_root, _KEEP, _MINTED).base.exists()


def test_one_blocking_moment_moves_neither_of_the_pairs_directories(tmp_path: Path) -> None:
    """The refusal is whole-pair, not per-event: a second minted moment that
    would have moved cleanly stays put, because a twin merged in part leaves the
    case split across two ids with no handle to finish it."""
    data_root = tmp_path / "data"
    other = "evt-order-cvsg-disposition"
    movable = _write_ledger_event(data_root, _DROP, other)
    _write_ledger_event(data_root, _DROP, _MINTED)
    _write_ledger_event(data_root, _KEEP, _MINTED)  # the collision
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED), _corpus_event(_DROP, other)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == []
        assert result.ledger_moves == []
        assert "exist under both ids" in result.skipped[0].conflicts[0]
        assert corpus.get_row(conn, _DROP) is not None
    assert movable.base.is_dir()
    assert not _event_paths(data_root, _KEEP, other).base.exists()


def test_an_unreadable_survivor_document_sends_the_pair_to_triage(tmp_path: Path) -> None:
    """Whether a survivor-side directory is an interrupted move is a question its
    documents answer; when one will not read, the pair is reported instead —
    one bad file must not abort a pass that may already have written."""
    data_root = tmp_path / "data"
    paths = _event_paths(data_root, _KEEP, _MINTED)
    paths.base.mkdir(parents=True)
    paths.event_file.write_text("event_id: [unclosed\n")
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == []
        assert result.ledger_moves == []
        assert "could not be read" in result.skipped[0].conflicts[0]
        assert corpus.get_row(conn, _DROP) is not None


def test_a_case_baseline_directory_stays_where_it_is(tmp_path: Path) -> None:
    """A case-level baseline is outside the mint rule — its ledger half is owed
    at first touch or at resolution — so its row re-keys with no ledger move."""
    data_root = tmp_path / "data"
    paths = _write_ledger_event(data_root, _DROP, _BASELINE)
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _BASELINE)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == [_DROP]
        assert result.ledger_moves == []
        assert [event.event_id for event in corpus.events_for_case(conn, _KEEP)] == [_BASELINE]
    assert paths.base.is_dir()
    assert not _event_paths(data_root, _KEEP, _BASELINE).base.exists()
    assert read_model(paths.event_file, PredictableEvent).case_id == _DROP


def test_a_dry_run_reports_the_move_and_touches_no_directory(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    old_paths = _write_ledger_event(data_root, _DROP, _MINTED)
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=False)
        assert result.applied is False
        assert result.ledger_moves == [_move(_MINTED)]
        assert corpus.get_row(conn, _DROP) is not None
    assert old_paths.base.is_dir()
    assert read_model(old_paths.event_file, PredictableEvent).case_id == _DROP
    assert not _event_paths(data_root, _KEEP, _MINTED).base.exists()


def test_an_interrupted_move_converges_on_the_next_apply(tmp_path: Path) -> None:
    """The crash window between the move and the restamp: the directory is
    already at the survivor with its documents still naming the dropped case.
    The restamp is unconditional on the target, so the next pass finishes it."""
    data_root = tmp_path / "data"
    paths = _event_paths(data_root, _KEEP, _MINTED)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=_MINTED, case_id=_DROP, kind=EventKind.petition, title="Cert petition"
        ),
    )
    write_json(
        paths.outcome,
        Outcome(
            case_id=_DROP,
            event_id=_MINTED,
            resolved_at=date(2026, 1, 12),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == [_DROP]
        assert result.ledger_moves == [_move(_MINTED, restamp_only=True)]
    assert read_model(paths.event_file, PredictableEvent).case_id == _KEEP
    assert read_model(paths.outcome, Outcome).case_id == _KEEP


def test_a_converged_survivor_directory_is_not_reported_as_a_move(tmp_path: Path) -> None:
    """A survivor-side directory already naming the survivor is nothing to do:
    the twin carries no committed half, so the merge reports no ledger work."""
    data_root = tmp_path / "data"
    _write_ledger_event(data_root, _KEEP, _MINTED)
    with _seeded(tmp_path, _pair_rows()) as conn:
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
        result = dedupe.dedupe_live_rows(conn, data_root, apply=True)
        assert result.dropped == [_DROP]
        assert result.ledger_moves == []
    survivor_event = read_model(
        _event_paths(data_root, _KEEP, _MINTED).event_file, PredictableEvent
    )
    assert survivor_event.case_id == _KEEP


def test_the_capital_flag_survives_the_merge() -> None:
    # The pair population IS the annotated-spelling join misses, so the live
    # twin is exactly the row that saw the capital marking; the CourtListener
    # survivor's confident False must not erase it. The DB max-latch cannot
    # save a merged False either: the upsert lands on the survivor's own
    # stored 0, and the twin is then deleted.
    keep, drop = _pair_rows(drop_capital_case=True)
    merged = dedupe._merged_row(keep, drop, weight=1)
    assert merged.capital_case is True


def test_every_plain_bool_column_has_an_explicit_merge_rule() -> None:
    """A plain-bool column can never ride the generic fill loop: `_lacks(False)`
    is false, so a drop-side True is silently discarded. Every non-Optional
    bool on the storage row must therefore appear in `_MERGE_SPECIAL` with its
    own rule (or in the allowlist below, with the docstring's reason)."""
    # Scope columns the merge deliberately leaves to their own machinery: the
    # eligibility mirror re-derives from the court predicate, and the exclusion
    # latch is the scope reconcile's to re-decide from the merged facts.
    allowlisted = {"predict_eligible", "predict_excluded"}
    plain_bools = {
        name for name, field in corpus.CorpusRow.model_fields.items() if field.annotation is bool
    }
    unruled = plain_bools - dedupe._MERGE_SPECIAL - allowlisted
    assert not unruled, f"plain-bool columns without an explicit merge rule: {sorted(unruled)}"


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


def test_cli_lists_the_ledger_moves_beside_the_dropped_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    _write_ledger_event(data_root, _DROP, _MINTED)
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, _pair_rows())
        corpus.upsert_events(conn, [_corpus_event(_DROP, _MINTED)])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))

    result = runner.invoke(app, ["dedupe-live-rows"])
    assert result.exit_code == 0, result.output
    assert f"would move ledger event directory {_DROP}/{_MINTED} -> {_KEEP}/{_MINTED}" in (
        result.output
    )
    assert _event_paths(data_root, _DROP, _MINTED).base.is_dir()

    applied = runner.invoke(app, ["dedupe-live-rows", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert f"moved ledger event directory {_DROP}/{_MINTED}" in applied.output
    assert _event_paths(data_root, _KEEP, _MINTED).event_file.is_file()


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["dedupe-live-rows"])
    assert result.exit_code == 1
