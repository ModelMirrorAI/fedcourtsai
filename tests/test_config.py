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
    load_spend_config,
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
    # push the corpus and write its queues after the rotation stops.
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


def test_repo_tracking_yaml_carries_the_salience_spend_controls() -> None:
    """Pin the shipped, pre-registered spend controls of the salience gate.

    These values size the tournament to the bootstrapping envelope
    (``docs/budget.md``): capacities that bind at typical cohort sizes, the
    always-include floor, and the interim reserve carved out inside the
    per-conference envelope. A silent edit to any of them re-sizes the whole
    program's spend and coverage, so it must fail a test the same way a lookback
    drift does — a deliberate diff, never a drift.
    """
    cfg = load_salience_config(Path("config"))
    assert cfg.per_conference_capacity == 12
    assert cfg.long_conference_capacity == 24
    assert cfg.interim_reserve_slots == 5
    assert cfg.floor == 0.28
    assert cfg.arrival_sample_rate == 0.05
    # The reserve is defined *inside* the per-conference envelope: the selection
    # pass fills ranks up to ``capacity - reserve``, which must stay positive.
    assert cfg.interim_reserve_slots < cfg.per_conference_capacity


def test_repo_tracking_yaml_arms_the_spend_backstop() -> None:
    """Pin the shipped ex-post spend ceiling and its window.

    The one control that reads measured spend rather than bounding a single
    run: sized to sit above every legitimate month and within days of a
    runaway burst — a mis-set capacity knob minting whole cohorts — per the
    derivation in docs/budget.md. A silent edit re-sizes the program's
    worst-case spend, so it fails a test the way the salience capacities do.
    """
    cfg = load_spend_config(Path("config"))
    assert cfg.ceiling_usd == 2500.0
    assert cfg.window_days == 30
    # The window is *stated*: its field default is also 30, so deleting the
    # key would still pass the assertion above — require the literal key.
    tracking = yaml.safe_load((Path("config") / "tracking.yaml").read_text())
    assert "window_days" in tracking["spend"]


_STORE_ENV = (
    "FEDCOURTS_CORPUS_BASE_URL",
    "CORPUS_BASE_URL",
    "FEDCOURTS_CORPUS_REMOTE_URL",
    "CORPUS_REMOTE_URL",
    "FEDCOURTS_DVC_REMOTE_URL",
    "DVC_REMOTE_URL",
    "FEDCOURTS_CASESTORE_URL",
    "CASESTORE_URL",
    "FEDCOURTS_CORPUS_SPLIT",
)


@pytest.fixture
def clean_store_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """No ambient corpus addressing — a maintainer's shell carries the real thing."""
    for name in _STORE_ENV:
        monkeypatch.delenv(name, raising=False)


@pytest.mark.usefixtures("clean_store_env")
def test_base_url_derives_both_store_halves(monkeypatch: pytest.MonkeyPatch) -> None:
    # One address per environment: the halves are segments beneath it, so an
    # index read and a payload read cannot answer from different environments.
    monkeypatch.setenv("CORPUS_BASE_URL", "s3://estate/pfx")
    settings = Settings()
    assert settings.corpus_remote_url == "s3://estate/pfx/store"
    assert settings.casestore_url == "s3://estate/pfx/casestore/v1"


@pytest.mark.usefixtures("clean_store_env")
def test_a_trailing_slash_on_the_base_does_not_double(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORPUS_BASE_URL", "s3://estate/ ")
    assert Settings().corpus_remote_url == "s3://estate/store"


@pytest.mark.usefixtures("clean_store_env")
def test_an_explicit_half_outranks_the_base(monkeypatch: pytest.MonkeyPatch) -> None:
    # The transition shape: an environment that still names a half individually
    # keeps that half exactly, while the other still derives.
    monkeypatch.setenv("CORPUS_BASE_URL", "s3://estate")
    monkeypatch.setenv("CASESTORE_URL", "s3://named/store")
    settings = Settings()
    assert settings.casestore_url == "s3://named/store"
    assert settings.corpus_remote_url == "s3://estate/store"


@pytest.mark.usefixtures("clean_store_env")
def test_a_blank_half_does_not_defeat_the_base(monkeypatch: pytest.MonkeyPatch) -> None:
    # An env layer that forwards a possibly-unset variable raw — a workflow's
    # `${{ vars.… }}`, corpus-env's prod restore — passes the empty string. It
    # must read as absent, or wiring that still mentions a half would blank out
    # the address the base URL derives.
    monkeypatch.setenv("CORPUS_BASE_URL", "s3://estate")
    monkeypatch.setenv("CASESTORE_URL", "  ")
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", "")
    settings = Settings()
    assert settings.casestore_url == "s3://estate/casestore/v1"
    assert settings.corpus_remote_url == "s3://estate/store"


@pytest.mark.usefixtures("clean_store_env")
def test_no_addressing_at_all_leaves_both_halves_unset() -> None:
    # The offline fixture loop: one self-contained blob, no store, no split.
    settings = Settings()
    assert settings.corpus_remote_url is None
    assert settings.casestore_url is None
    assert settings.corpus_split is False


@pytest.mark.usefixtures("clean_store_env")
def test_the_split_follows_the_content_store_address(monkeypatch: pytest.MonkeyPatch) -> None:
    # The store's address is the mode: under the split the payloads live only
    # in the store, so a configured store with the reads pointed elsewhere —
    # and the mode on with nowhere to read — are both unrepresentable.
    assert Settings().corpus_split is False
    monkeypatch.setenv("CASESTORE_URL", "s3://named/store")
    assert Settings().corpus_split is True
    monkeypatch.delenv("CASESTORE_URL")
    monkeypatch.setenv("CORPUS_BASE_URL", "s3://estate")
    assert Settings().corpus_split is True


@pytest.mark.usefixtures("clean_store_env")
def test_the_split_flag_overrides_the_inference(monkeypatch: pytest.MonkeyPatch) -> None:
    # The compatibility shim, for an environment that still states the mode as
    # its own setting: an explicit value wins over the store's address, in both
    # directions. An empty value is an absent setting, not "off" — every env
    # layer that forwards an unset variable raw passes the empty string.
    monkeypatch.setenv("CORPUS_BASE_URL", "s3://estate")
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "0")
    assert Settings().corpus_split is False
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    assert Settings().corpus_split is True
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "")
    assert Settings().corpus_split is True
    monkeypatch.delenv("CORPUS_BASE_URL")
    assert Settings().corpus_split is False


def test_corpus_pointer_empty_env_reads_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    # corpus-env's prod restore and any workflow-variable fallback pass an
    # unset override through as the empty string, which must mean "the
    # committed pointer, unchanged" — not crash settings resolution.
    for name in ("FEDCOURTS_CORPUS_POINTER", "CORPUS_POINTER"):
        monkeypatch.delenv(name, raising=False)
    assert Settings().corpus_pointer is None
    monkeypatch.setenv("FEDCOURTS_CORPUS_POINTER", "")
    assert Settings().corpus_pointer is None
    monkeypatch.setenv("FEDCOURTS_CORPUS_POINTER", '{"key": "index/sha256/x"}')
    assert Settings().corpus_pointer == '{"key": "index/sha256/x"}'


def test_corpus_pointer_prefixed_name_outranks_bare(monkeypatch: pytest.MonkeyPatch) -> None:
    # Same alias discipline as the store URLs: both spellings accepted, the
    # FEDCOURTS_-prefixed one wins, so corpus-env moves them together.
    monkeypatch.setenv("CORPUS_POINTER", "bare")
    assert Settings().corpus_pointer == "bare"
    monkeypatch.setenv("FEDCOURTS_CORPUS_POINTER", "prefixed")
    assert Settings().corpus_pointer == "prefixed"


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
