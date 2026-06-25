from pathlib import Path
from typing import Any, cast

from fedcourtsai import corpus
from fedcourtsai.courtlistener import CourtListenerClient
from fedcourtsai.pipeline.pull import pull_case

DOCKET: dict[str, Any] = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "nature_of_suit": "Civil Rights",
}


class FakeClient:
    """Stand-in for CourtListenerClient returning canned docket facts."""

    def __init__(self, docket: dict[str, Any], entries: list[dict[str, Any]]) -> None:
        self._docket = docket
        self._entries = entries

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return self._docket

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return self._entries


def _pull(client: FakeClient, tmp_path: Path) -> Any:
    return pull_case(
        cast(CourtListenerClient, client),
        corpus.corpus_db_path(tmp_path / "corpus"),
        tmp_path / "data",
        "ca9",
        64512345,
    )


def test_first_pull_onboards_into_corpus(tmp_path: Path) -> None:
    result = _pull(FakeClient(DOCKET, [{"id": 1, "description": "Motion to stay"}]), tmp_path)
    assert result.case_id == "ca9/64512345"
    assert result.changed is True
    # The raw fact lands in the corpus, not in per-case git files.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
    assert row is not None
    assert row.court == "ca9"
    assert row.topic == "Civil Rights"
    assert result.snapshot.exists()  # transitional point-in-time snapshot


def test_no_legacy_git_files_written(tmp_path: Path) -> None:
    _pull(FakeClient(DOCKET, []), tmp_path)
    case_dir = tmp_path / "data" / "cases" / "ca9" / "64512345"
    assert not (case_dir / "case.yaml").exists()
    assert not (case_dir / "record" / "docket.json").exists()


def test_unchanged_second_pull_reports_no_change(tmp_path: Path) -> None:
    entries = [{"id": 1, "description": "Motion to stay"}]
    assert _pull(FakeClient(DOCKET, entries), tmp_path).changed is True
    assert _pull(FakeClient(DOCKET, entries), tmp_path).changed is False


def test_changed_docket_is_detected(tmp_path: Path) -> None:
    assert _pull(FakeClient(DOCKET, []), tmp_path).changed is True
    new_entry = [{"id": 2, "description": "Order granting stay"}]
    assert _pull(FakeClient(DOCKET, new_entry), tmp_path).changed is True
