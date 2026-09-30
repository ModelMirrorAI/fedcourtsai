"""The interim-docket back-fill: enumeration, ownership, the live seam, the bound."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import cli as cli_module
from fedcourtsai import corpus
from fedcourtsai.analytics import _InterimAcc
from fedcourtsai.pipeline import application_backfill as backfill_module
from fedcourtsai.pipeline.application_backfill import (
    ApplicationBackfillResult,
    DocketCache,
    backfill_applications,
    render_ledger,
)
from fedcourtsai.pipeline.live import discover_live, ingest_live_payload
from fedcourtsai.schemas import EventKind
from fedcourtsai.supremecourt import live_application_id
from tests.conftest import seed_prediction
from tests.test_live import _client, _payload

TODAY = date(2026, 9, 30)


def _application(number: str, *, decided: bool = True) -> dict[str, Any]:
    """A trimmed application docket: a stay ask, referred and denied when ``decided``."""
    proceedings: list[dict[str, Any]] = [
        {
            "Date": "Mar 13 2025",
            "Text": f"Application ({number}) for a stay, submitted to The Chief Justice.",
        }
    ]
    if decided:
        proceedings += [
            {"Date": "Mar 20 2025", "Text": f"Application ({number}) referred to the Court."},
            {
                "Date": "Apr 04 2025",
                "Text": f"Application ({number}) for stay presented to The Chief Justice and "
                + "by him referred to the Court is denied.",
            },
        ]
    return _payload(number, proceedings=proceedings)


class _Upstream:
    """A served set of application dockets, recording every name requested."""

    def __init__(self, served: dict[str, dict[str, Any]], *, failing: str | None = None) -> None:
        self.served = served
        self.failing = failing
        self.requested: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        self.requested.append(name)
        if name == self.failing:
            return httpx.Response(500)
        if name in self.served:
            return httpx.Response(200, json=self.served[name])
        return httpx.Response(404)


def _stub(db: Path, docket_id: int, number: str) -> None:
    """A CourtListener-shaped stub row: a number and a filing date, nothing live."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/{docket_id}",
                    court="scotus",
                    docket_number=number,
                    date_filed=date(2025, 3, 13),
                )
            ],
        )


def _seeded(tmp_path: Path) -> tuple[Path, Path, _Upstream]:
    """24A1 unstored, 24A2 and 24A5 stubs, 24A3 live-owned, 24A4 withheld upstream."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    _stub(db, 72416101, "24A2")
    _stub(db, 72416555, "24A5")
    ingest_live_payload(
        db,
        data_root,
        _application("24A3"),
        live_application_id(24, 3),
        today=date(2026, 8, 6),
        form="application",
    )
    upstream = _Upstream({n: _application(n) for n in ("24A1", "24A2", "24A3", "24A5")})
    return db, data_root, upstream


def test_the_dry_run_reads_the_unowned_serials_and_writes_nothing(tmp_path: Path) -> None:
    db, data_root, upstream = _seeded(tmp_path)
    with corpus.connect(db) as conn:
        before = corpus.get_row(conn, "scotus/72416101")

    with _client(upstream.handler) as client:
        result = backfill_applications(client, db, data_root, today=TODAY, end_misses=2)

    (ledger,) = result.terms
    assert [row.docket_number for row in result.candidates] == ["24A1", "24A2", "24A5"]
    assert [row.action for row in result.candidates] == ["onboard", "enrich", "enrich"]
    # Identity is the live join's: the stubs keep their ids, the unstored serial
    # takes the reserved-range mint.
    assert [row.case_id for row in result.candidates] == [
        f"scotus/{live_application_id(24, 1)}",
        "scotus/72416101",
        "scotus/72416555",
    ]
    first = result.candidates[0]
    assert first.application_kind == "substantive"
    assert first.referred_to_court is True
    assert first.disposition == "denied"
    assert first.date_decided == date(2025, 4, 4)
    # The live-owned serial is counted and never fetched; the withheld serial is
    # below the stored maximum, so it is a gap rather than the end.
    assert "24A3" not in upstream.requested
    assert ledger.live_owned == 1
    assert ledger.withheld == [4]
    assert ledger.stopped == "end"
    assert ledger.stored_max_serial == 5
    assert upstream.requested[-2:] == ["24A6", "24A7"]
    assert not result.applied and result.written == []
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/72416101") == before
        assert corpus.get_row(conn, f"scotus/{live_application_id(24, 1)}") is None
    assert "would land 3 row(s)" in render_ledger(result)


def test_the_apply_lands_through_the_live_seam_and_the_control_reads_zero(
    tmp_path: Path,
) -> None:
    db, data_root, upstream = _seeded(tmp_path)
    with _client(upstream.handler) as client:
        result = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, apply=True, max_rows=3
        )
    assert result.applied
    assert result.written == [
        f"scotus/{live_application_id(24, 1)}",
        "scotus/72416101",
        "scotus/72416555",
    ]
    with corpus.connect(db) as conn:
        enriched = corpus.get_row(conn, "scotus/72416101")
        live_owned = corpus.get_row(conn, f"scotus/{live_application_id(24, 3)}")
        assert corpus.latest_snapshot(conn, "scotus/72416101") is not None
    assert enriched is not None and live_owned is not None
    assert enriched.last_live_polled == TODAY
    assert enriched.application_kind == "substantive"
    assert enriched.referred_to_court is True
    assert enriched.disposition == "denied"
    assert enriched.counsel
    # The live-owned row was never touched.
    assert live_owned.last_live_polled == date(2026, 8, 6)

    with _client(_Upstream(upstream.served).handler) as client:
        control = backfill_applications(client, db, data_root, today=TODAY, end_misses=2)
    assert control.candidates == []
    assert control.terms[0].live_owned == 4


def test_a_backfilled_row_is_the_row_live_discovery_writes(tmp_path: Path) -> None:
    """No fork of the mapping: the same payload lands the same row either way."""
    payload = _application("24A1")
    upstream = _Upstream({"24A1": payload})
    discovered_db = corpus.corpus_db_path(tmp_path / "discovered" / "corpus")
    with _client(upstream.handler) as client:
        discover_live(client, discovered_db, tmp_path / "d1", 24, max_new=5, today=TODAY)
    backfilled_db = corpus.corpus_db_path(tmp_path / "backfilled" / "corpus")
    with _client(upstream.handler) as client:
        backfill_applications(
            client, backfilled_db, tmp_path / "d2", today=TODAY, apply=True, max_rows=1
        )
    case_id = f"scotus/{live_application_id(24, 1)}"
    with corpus.connect(discovered_db) as a, corpus.connect(backfilled_db) as b:
        discovered = corpus.get_row(a, case_id)
        assert discovered is not None and discovered.application_kind == "substantive"
        assert discovered == corpus.get_row(b, case_id)
        events = corpus.events_for_case(a, case_id)
        assert events and events == corpus.events_for_case(b, case_id)
        assert corpus.latest_snapshot(a, case_id) == corpus.latest_snapshot(b, case_id)


def test_the_apply_refuses_above_its_bound_and_on_a_failed_read(tmp_path: Path) -> None:
    db, data_root, upstream = _seeded(tmp_path)
    with _client(upstream.handler) as client:
        over = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, apply=True, max_rows=2
        )
    assert over.refused and "above the bound of 2" in over.refused
    assert not over.applied and over.written == []

    failing = _Upstream(upstream.served, failing="24A5")
    with _client(failing.handler) as client:
        broken = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, apply=True, max_rows=10
        )
    assert broken.terms[0].stopped == "upstream-error"
    assert broken.refused and "upstream-error" in broken.refused
    with corpus.connect(db) as conn:
        stub = corpus.get_row(conn, "scotus/72416101")
    assert stub is not None and stub.last_live_polled is None

    with pytest.raises(ValueError, match="max_rows"):
        backfill_applications(client, db, data_root, today=TODAY, apply=True)


def test_a_record_served_under_another_number_is_held_back(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    upstream = _Upstream({"24A1": _application("24A9")})
    with _client(upstream.handler) as client:
        result = backfill_applications(client, db, tmp_path / "data", today=TODAY, end_misses=1)
    assert result.candidates == []
    (held,) = result.terms[0].held
    assert held["docket"] == "24A1"


def test_the_fetch_limit_and_the_dev_cache(tmp_path: Path) -> None:
    db, data_root, upstream = _seeded(tmp_path)
    cache = DocketCache(tmp_path / "cache")
    with _client(upstream.handler) as client:
        sampled = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, limit=2, cache=cache
        )
    assert sampled.terms[0].stopped == "limit"
    assert [row.docket_number for row in sampled.candidates] == ["24A1", "24A2"]
    # A re-read serves the cached records without asking upstream again.
    silent = _Upstream({})
    with _client(silent.handler) as client:
        again = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, limit=2, cache=cache
        )
    assert silent.requested == []
    assert [row.docket_number for row in again.candidates] == ["24A1", "24A2"]
    with pytest.raises(ValueError, match="host-scoped"):
        backfill_applications(
            client, db, data_root, today=TODAY, apply=True, max_rows=1, cache=cache
        )


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--apply"], "requires an explicit --max-rows"),
        (["--apply", "--max-rows", "1", "--cache-dir", "c"], "--cache-dir"),
        (["--term", "99"], "out of reach"),
        (["--term", "23", "--apply", "--max-rows", "1"], "no pre-registered apply"),
        (["--term", "16"], "out of reach"),
        (["--limit", "0"], "must be positive"),
    ],
)
def test_the_command_refuses_before_any_fetch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, args: list[str], message: str
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setattr(
        backfill_module,
        "backfill_applications",
        lambda *a, **k: pytest.fail("the refusal must precede the walk"),
    )
    result = CliRunner().invoke(cli_module.app, ["backfill-applications", *args])
    assert result.exit_code == 2
    plain = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
    assert message in " ".join(plain.split())


def test_the_term_read_of_the_identity_join_agrees_with_the_single_join(tmp_path: Path) -> None:
    """One read per Term, the same answer per number: lowest id, same normalization."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _stub(db, 100, "24A7")
    _stub(db, 50, "24A7 ")
    _stub(db, 60, "No. 24a8")
    _stub(db, 70, "24-7")
    with corpus.connect(db) as conn:
        matches = corpus.scotus_case_ids_by_docket_number_prefix(conn, "24A")
        assert matches == {"24A7": "scotus/50", "24A8": "scotus/60"}
        for number in ("24A7", "24A8", "24A9"):
            assert matches.get(number) == corpus.scotus_case_id_by_docket_number(conn, number)
        with pytest.raises(ValueError, match="prefix"):
            corpus.scotus_case_ids_by_docket_number_prefix(conn, "24A*")


def test_an_apply_refuses_a_walk_stopped_by_its_limit_or_deadline(tmp_path: Path) -> None:
    db, data_root, upstream = _seeded(tmp_path)
    with _client(upstream.handler) as client:
        limited = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, apply=True, max_rows=10, limit=1
        )
        clock = iter([0.0, 0.0, 100.0])
        late = backfill_applications(
            client,
            db,
            data_root,
            today=TODAY,
            end_misses=2,
            apply=True,
            max_rows=10,
            deadline=50.0,
            time_fn=lambda: next(clock, 100.0),
        )
    assert limited.refused and "limit" in limited.refused
    assert late.terms[0].stopped == "deadline"
    assert [row.docket_number for row in late.candidates] == ["24A1", "24A2"]
    assert late.refused and "deadline" in late.refused
    assert not limited.applied and not late.applied
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, f"scotus/{live_application_id(24, 1)}") is None


def test_misses_past_the_stored_maximum_that_a_later_record_ends_are_withheld(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _stub(db, 72416101, "24A2")
    upstream = _Upstream({n: _application(n) for n in ("24A1", "24A2", "24A5")})
    with _client(upstream.handler) as client:
        result = backfill_applications(client, db, tmp_path / "data", today=TODAY, end_misses=3)
    (ledger,) = result.terms
    assert ledger.withheld == [3, 4]
    assert [row.docket_number for row in result.candidates] == ["24A1", "24A2", "24A5"]
    assert ledger.last_served == 5 and ledger.stopped == "end"


def test_a_row_whose_open_event_carries_a_prediction_is_held_back(tmp_path: Path) -> None:
    """Left to the live rotation, which writes the evaluate queue this pass never does."""
    db, data_root, upstream = _seeded(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-motion-disposition",
                    case_id="scotus/72416101",
                    court="scotus",
                    kind=EventKind.motion,
                    title="Disposition of the application",
                )
            ],
        )
    seed_prediction(data_root, "scotus", 72416101, "evt-motion-disposition")
    with _client(upstream.handler) as client:
        result = backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, apply=True, max_rows=10
        )
    assert "24A2" not in [row.docket_number for row in result.candidates]
    assert result.terms[0].held == [
        {"docket": "24A2", "reason": "an open event carries a committed prediction"}
    ]
    with corpus.connect(db) as conn:
        stub = corpus.get_row(conn, "scotus/72416101")
    assert stub is not None and stub.last_live_polled is None


def test_the_out_ledger_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db, _, upstream = _seeded(tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(db.parent))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setattr(cli_module, "SupremeCourtClient", lambda **_: _client(upstream.handler))
    out = tmp_path / "ledger.json"
    result = CliRunner().invoke(
        cli_module.app, ["backfill-applications", "--end-misses", "2", "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    assert "would land 3 row(s)" in result.output
    ledger = ApplicationBackfillResult.model_validate_json(out.read_text())
    assert [row.docket_number for row in ledger.candidates] == ["24A1", "24A2", "24A5"]


def test_an_applied_stub_moves_from_unparsed_into_the_interim_pool(tmp_path: Path) -> None:
    """The move the freeze-record entry registers, read through the statpack's own counter."""
    db, data_root, upstream = _seeded(tmp_path)

    def counts() -> tuple[int, int, int]:
        acc = _InterimAcc()
        with corpus.connect(db) as conn:
            for case_id in ("scotus/72416101", "scotus/72416555"):
                row = corpus.get_row(conn, case_id)
                assert row is not None
                acc.add(row)
        return acc.unparsed, acc.substantive_resolved, acc.substantive_granted

    assert counts() == (2, 0, 0)
    with _client(upstream.handler) as client:
        backfill_applications(
            client, db, data_root, today=TODAY, end_misses=2, apply=True, max_rows=3
        )
    assert counts() == (0, 2, 0)
