from datetime import date
from pathlib import Path
from typing import Any, cast

from fedcourtsai import corpus
from fedcourtsai.courtlistener import CourtListenerClient
from fedcourtsai.pipeline.discover import discover_cases


def _docket(docket_id: int, court_url: str, date_filed: str, **kw: Any) -> dict[str, Any]:
    return {
        "id": docket_id,
        "court": f"https://www.courtlistener.com/api/rest/v4/courts/{court_url}/",
        "date_filed": date_filed,
        **kw,
    }


class FakeSearch:
    """Stand-in for the client's discovery API, recording how it was queried."""

    def __init__(self, by_court: dict[str, list[dict[str, Any]]]) -> None:
        self._by_court = by_court
        self.calls: list[tuple[str, date, int]] = []

    def iter_dockets(
        self, court: str, date_filed_gte: date, *, max_results: int
    ) -> list[dict[str, Any]]:
        self.calls.append((court, date_filed_gte, max_results))
        hits = [
            d
            for d in self._by_court.get(court, [])
            if date.fromisoformat(d["date_filed"]) >= date_filed_gte
        ]
        return hits[:max_results]


def _discover(client: FakeSearch, tmp_path: Path, **kw: Any) -> Any:
    return discover_cases(
        cast(CourtListenerClient, client),
        corpus.corpus_db_path(tmp_path / "corpus"),
        kw.pop("courts", ["ca9"]),
        max_new=kw.pop("max_new", 10),
        default_since=kw.pop("default_since", date(2026, 6, 1)),
    )


def test_discovery_onboards_docket_and_event(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(101, "ca9", "2026-06-10", case_name="Doe v. Roe")]})
    result = _discover(client, tmp_path)

    assert result.total == 1
    assert result.case_ids == ["ca9/101"]
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "ca9/101")
        events = corpus.events_for_case(conn, "ca9/101")
    assert row is not None and row.court == "ca9"
    # The predictable event is recorded as a corpus row, not a git event.yaml.
    assert len(events) == 1
    assert events[0].event_id == "evt-appeal-disposition"
    assert events[0].title == "Doe v. Roe"
    assert events[0].opened_at == date(2026, 6, 10)


def test_scotus_event_is_a_petition(tmp_path: Path) -> None:
    client = FakeSearch({"scotus": [_docket(7, "scotus", "2026-06-05")]})
    _discover(client, tmp_path, courts=["scotus"])
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        events = corpus.events_for_case(conn, "scotus/7")
    assert events[0].event_id == "evt-petition-disposition"


def test_watermark_advances_to_newest_filed(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-03"), _docket(2, "ca9", "2026-06-09")]})
    result = _discover(client, tmp_path)
    assert result.courts[0].watermark == date(2026, 6, 9)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 9)


def test_second_run_resumes_from_watermark(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-03"), _docket(2, "ca9", "2026-06-09")]})
    _discover(client, tmp_path)
    # Add a newer filing and re-run: the query must start at the stored watermark.
    client._by_court["ca9"].append(_docket(3, "ca9", "2026-06-12"))
    result = _discover(client, tmp_path)
    # Second call queried from the stored watermark, not default_since.
    assert client.calls[-1][1] == date(2026, 6, 9)
    assert "ca9/3" in result.case_ids


def test_budget_cap_limits_total_across_courts(tmp_path: Path) -> None:
    client = FakeSearch(
        {
            "ca9": [_docket(1, "ca9", "2026-06-02"), _docket(2, "ca9", "2026-06-03")],
            "ca1": [_docket(3, "ca1", "2026-06-04")],
        }
    )
    result = _discover(client, tmp_path, courts=["ca9", "ca1"], max_new=2)
    assert result.total == 2  # ca9 fills the budget; ca1 is not reached
    assert [c.court for c in result.courts] == ["ca9"]


def test_zero_budget_is_noop(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-02")]})
    result = _discover(client, tmp_path, max_new=0)
    assert result.total == 0
    assert client.calls == []


def test_court_with_no_new_filings_is_skipped(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": []})
    result = _discover(client, tmp_path)
    assert result.total == 0
    assert result.courts == []
    # An empty court must not write a watermark (nothing onboarded).
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") is None
