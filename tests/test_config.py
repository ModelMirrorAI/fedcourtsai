from pathlib import Path

import pytest
import yaml

from fedcourtsai.config import (
    PredictConfig,
    PredictScope,
    PullConfig,
    RunnerConfig,
    Settings,
    StatpackConfig,
    load_courts,
    load_predict_config,
    load_pull_config,
    load_runner_config,
    load_salience_config,
    load_statpack_config,
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


def test_load_runner_config_reads_retry_governor(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        "runner:\n  max_attempts: 5\n  backoff_base_seconds: 1.5\n  backoff_max_seconds: 45\n",
    )
    cfg = load_runner_config(tmp_path)
    assert cfg.max_attempts == 5
    assert cfg.backoff_base_seconds == 1.5
    assert cfg.backoff_max_seconds == 45.0


def test_load_runner_config_defaults_when_absent(tmp_path: Path) -> None:
    # Missing file and missing section both keep the conservative retry defaults.
    assert load_runner_config(tmp_path / "absent") == RunnerConfig()
    cfg = load_runner_config(tmp_path / "absent")
    assert cfg.max_attempts == 3
    assert cfg.backoff_base_seconds == 2.0
    assert cfg.backoff_max_seconds == 30.0


def test_runner_config_rejects_a_ceiling_below_the_base() -> None:
    with pytest.raises(ValueError, match="backoff_max_seconds must be >="):
        RunnerConfig(backoff_base_seconds=10.0, backoff_max_seconds=5.0)


def test_repo_tracking_yaml_carries_the_runner_retry_section() -> None:
    # The committed config pins the shipped retry governor the runners read.
    cfg = load_runner_config(Path("config"))
    assert cfg.max_attempts == 3
    assert cfg.backoff_base_seconds == 2.0
    assert cfg.backoff_max_seconds == 30.0


def test_load_statpack_config_reads_markdown_terms(tmp_path: Path) -> None:
    _write_tracking(tmp_path, "statpack:\n  markdown_terms: 3\n")
    assert load_statpack_config(tmp_path).markdown_terms == 3


def test_load_statpack_config_defaults_when_absent(tmp_path: Path) -> None:
    assert load_statpack_config(tmp_path / "absent") == StatpackConfig()
    assert load_statpack_config(tmp_path / "absent").markdown_terms == 10


def test_repo_tracking_yaml_carries_the_two_base_rate_windows() -> None:
    # The segment base rate's lookback exists in two places — in code for the cert
    # back-test, and as the Term table the predict/evaluate agents read. Both are
    # stated config pinned to the same value, so the scored baseline and the table
    # the agents anchor on share one window by construction. This pins the shipped
    # values: changing either re-bases published skill numbers, so it must be a
    # deliberate diff and never a drift.
    assert load_salience_config(Path("config")).base_rate_lookback_terms == 10
    assert load_statpack_config(Path("config")).markdown_terms == 10
    # The window is *stated*, so assert the keys are literally present — the
    # lookback's field default (0, unbounded) is the fallback for an absent file,
    # not the shipped choice, so deleting its key would silently widen the pool.
    tracking = yaml.safe_load((Path("config") / "tracking.yaml").read_text())
    assert "base_rate_lookback_terms" in tracking["salience"]
    assert "markdown_terms" in tracking["statpack"]


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
