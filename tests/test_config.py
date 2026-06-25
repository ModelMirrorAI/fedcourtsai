from pathlib import Path

from fedcourtsai.config import PullConfig, load_pull_config


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
    _write_tracking(tmp_path, "pull:\n  max_cases_per_run: 9\n  discover_new_filings: true\n")
    assert load_pull_config(tmp_path).max_cases_per_run == 9


def test_load_pull_config_defaults_when_file_missing(tmp_path: Path) -> None:
    cfg = load_pull_config(tmp_path / "absent")
    assert cfg == PullConfig()
    assert cfg.max_cases_per_run == 15
    assert cfg.skip_closed is True


def test_load_pull_config_defaults_when_section_absent(tmp_path: Path) -> None:
    _write_tracking(tmp_path, "seed:\n  source: bulk\n")
    assert load_pull_config(tmp_path) == PullConfig()
