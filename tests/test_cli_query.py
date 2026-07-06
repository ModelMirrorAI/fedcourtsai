import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _rows(output: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def test_query_ranks_and_omits_opinion_text(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith"])
    assert result.exit_code == 0, result.output
    rows = _rows(result.stdout)
    # ca9/101 and ca9/102 both share judge smith; ca9/102 (decided later) ranks
    # first on recency, and the open ca9/103 is excluded by the resolved-only default.
    assert [r["case_id"] for r in rows] == ["ca9/102", "ca9/101"]
    assert "opinion_text" not in rows[0]


def test_query_full_includes_opinion_text(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca1", "--full"])
    assert result.exit_code == 0, result.output
    rows = _rows(result.stdout)
    assert rows[0]["case_id"] == "ca1/201"
    assert "dismissed for lack of jurisdiction" in str(rows[0]["opinion_text"])


def test_query_rows_carry_caption_and_derived_era(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith"])
    assert result.exit_code == 0, result.output
    row = _rows(result.stdout)[0]
    # The retrieval-judgment fields: caption stored on the row, era derived.
    assert row["case_name"] == "Cohen v. Pacific Mutual"
    assert row["era"] == "2020s"
    assert row["date_filed"] == "2022-06-02"


def test_query_era_filter(fixture_corpus: FixtureCorpus) -> None:
    kept = runner.invoke(app, ["query", "--court", "ca9", "--era", "2020s"])
    none = runner.invoke(app, ["query", "--court", "ca9", "--era", "1890s"])
    assert kept.exit_code == 0 and none.exit_code == 0
    assert _rows(kept.stdout) and not _rows(none.stdout)


def test_query_include_open(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "berzon", "--include-open"])
    assert result.exit_code == 0, result.output
    # berzon sits on ca9/101 (resolved) and ca9/103 (open); --include-open keeps both.
    assert {r["case_id"] for r in _rows(result.stdout)} == {"ca9/101", "ca9/103"}


def test_query_unknown_disposition_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--disposition", "nope"])
    assert result.exit_code == 2
    assert "Unknown disposition" in result.stderr


def test_query_missing_corpus_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = runner.invoke(app, ["query"])
    assert result.exit_code == 1
    assert "No corpus" in result.stderr
