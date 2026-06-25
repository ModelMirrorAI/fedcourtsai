from pathlib import Path

from fedcourtsai.config import (
    PullConfig,
    SeedConfig,
    load_courts,
    load_pull_config,
    load_seed_config,
)


def _write_tracking(root: Path, body: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "tracking.yaml").write_text(body)


def test_load_pull_config_reads_governor_keys(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        "pull:\n"
        "  max_cases_per_run: 15\n"
        "  skip_closed: true\n"
        "  rotation: oldest_last_pulled_first\n",
    )
    cfg = load_pull_config(tmp_path)
    assert cfg.max_cases_per_run == 15
    assert cfg.skip_closed is True


def test_load_pull_config_ignores_unmodeled_keys(tmp_path: Path) -> None:
    # tracking.yaml carries many tuning keys the governor does not model.
    _write_tracking(
        tmp_path, "pull:\n  max_cases_per_run: 9\n  rotation: oldest_last_pulled_first\n"
    )
    assert load_pull_config(tmp_path).max_cases_per_run == 9


def test_load_pull_config_reads_discovery_keys(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        "pull:\n  discover_new_filings: false\n  max_new_cases_per_run: 4\n",
    )
    cfg = load_pull_config(tmp_path)
    assert cfg.discover_new_filings is False
    assert cfg.max_new_cases_per_run == 4


def test_discovery_defaults(tmp_path: Path) -> None:
    cfg = load_pull_config(tmp_path / "absent")
    assert cfg.discover_new_filings is True
    assert cfg.max_new_cases_per_run == 10


def test_load_courts_reads_scope(tmp_path: Path) -> None:
    _write_tracking(tmp_path, "courts:\n  - scotus\n  - ca9\n  - ca1\n")
    assert load_courts(tmp_path) == ["scotus", "ca9", "ca1"]


def test_load_courts_empty_when_absent(tmp_path: Path) -> None:
    assert load_courts(tmp_path / "absent") == []
    _write_tracking(tmp_path, "pull:\n  max_cases_per_run: 1\n")
    assert load_courts(tmp_path) == []


def test_load_pull_config_defaults_when_file_missing(tmp_path: Path) -> None:
    cfg = load_pull_config(tmp_path / "absent")
    assert cfg == PullConfig()
    assert cfg.max_cases_per_run == 15
    assert cfg.skip_closed is True


def test_load_pull_config_defaults_when_section_absent(tmp_path: Path) -> None:
    _write_tracking(tmp_path, "seed:\n  source: bulk\n")
    assert load_pull_config(tmp_path) == PullConfig()


def test_load_seed_config_reads_backfill_keys(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        "seed:\n  source: bulk\n  max_cases_per_run: 2000\n  cursor: config/seed-progress.yaml\n",
    )
    cfg = load_seed_config(tmp_path)
    assert cfg.max_cases_per_run == 2000
    assert cfg.cursor == Path("config/seed-progress.yaml")


def test_load_seed_config_defaults_when_missing(tmp_path: Path) -> None:
    cfg = load_seed_config(tmp_path / "absent")
    assert cfg == SeedConfig()
    assert cfg.max_cases_per_run == 2000
