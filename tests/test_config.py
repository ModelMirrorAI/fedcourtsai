from pathlib import Path

import pytest

from fedcourtsai.config import (
    PredictConfig,
    PredictScope,
    PullConfig,
    Settings,
    load_courts,
    load_predict_config,
    load_pull_config,
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


def test_load_pull_config_reads_degradation_keys(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        "pull:\n  max_run_minutes: 10\n  max_consecutive_transient_failures: 3\n",
    )
    cfg = load_pull_config(tmp_path)
    assert cfg.max_run_minutes == 10.0
    assert cfg.max_consecutive_transient_failures == 3


def test_degradation_defaults_stay_under_the_job_timeout(tmp_path: Path) -> None:
    # The deadline default must leave the workflow job (45 min) ample headroom to
    # push the corpus and file handoffs after the rotation stops.
    cfg = load_pull_config(tmp_path / "absent")
    assert cfg.max_run_minutes == 25.0
    assert cfg.max_consecutive_transient_failures == 5


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
    _write_tracking(tmp_path, "live:\n  max_cases_per_run: 30\n")
    assert load_pull_config(tmp_path) == PullConfig()


def test_load_predict_config_reads_scope(tmp_path: Path) -> None:
    _write_tracking(tmp_path, "predict:\n  scope: all\n  max_parallel: 4\n")
    assert load_predict_config(tmp_path).scope == PredictScope.all


def test_load_predict_config_defaults_to_scotus_docket(tmp_path: Path) -> None:
    # Missing file, missing section, and a section without `scope` all keep the gate on.
    assert load_predict_config(tmp_path / "absent") == PredictConfig()
    assert load_predict_config(tmp_path / "absent").scope == PredictScope.scotus_docket
    _write_tracking(tmp_path, "predict:\n  max_parallel: 4\n")
    assert load_predict_config(tmp_path).scope == PredictScope.scotus_docket


def test_repo_tracking_yaml_carries_default_scope() -> None:
    # The committed config pins the documented default the workflows read.
    assert load_predict_config(Path("config")).scope == PredictScope.scotus_docket


def test_corpus_split_empty_env_reads_as_off(monkeypatch: pytest.MonkeyPatch) -> None:
    # The workflows wire FEDCOURTS_CORPUS_SPLIT from a repository variable; an
    # unset variable lands in the job env as the empty string, which must read
    # as the default (off) — not crash settings resolution.
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "")
    assert Settings().corpus_split is False
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    assert Settings().corpus_split is True
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "0")
    assert Settings().corpus_split is False


def test_corpus_service_url_reads_its_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    # The service backend's target: the name is deliberately clear of the
    # Gemini CLI's credential-name refusal regex so cells can allowlist it.
    monkeypatch.delenv("FEDCOURTS_CORPUS_SERVICE_URL", raising=False)
    assert Settings().corpus_service_url is None
    monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", "http://127.0.0.1:8377")
    assert Settings().corpus_service_url == "http://127.0.0.1:8377"


def test_corpus_backend_accepts_service(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "service")
    assert Settings().corpus_backend == "service"
