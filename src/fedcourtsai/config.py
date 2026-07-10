"""Runtime settings, read from environment (prefix ``FEDCOURTS_``) or ``.env``.

Secrets (the CourtListener token) come from the environment only and are never
written to disk or committed.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEDCOURTS_", env_file=".env", extra="ignore")

    data_root: Path = Path("data")
    config_root: Path = Path("config")
    corpus_root: Path = Path("corpus")
    metrics_root: Path = Path("metrics")
    # Recorded-cassette directory the offline `replay` engine reads instead of
    # calling a model (a captured real cell's output; see the runner). Unset in
    # production — replay is a test/dev backend — so the `replay` engine errors
    # clearly when no cassette is configured.
    replay_root: Path | None = None
    courtlistener_base_url: str = "https://www.courtlistener.com/api/rest/v4/"
    courtlistener_api_token: str | None = None
    # Seed reads CourtListener's *public bulk-data* CSV (no API token). Point this
    # at the bulk-data **base** directory and the backfill auto-discovers the latest
    # snapshot from the bucket listing; an explicit `.csv.bz2` file URL is honored as
    # a manual pin. Injected from the runner env; absent, `seed-backfill` no-ops.
    courtlistener_bulk_url: str | None = None
    request_timeout: float = 30.0
    # CourtListener per-token rate limits (issue #1); override via FEDCOURTS_* env.
    courtlistener_rpm: int = 5
    courtlistener_rph: int = 50
    courtlistener_rpd: int = 125
    # Longest single throttle wait the client may sleep. Minute-window pacing is
    # seconds; a longer wait means an hour/day window is exhausted, and sleeping
    # it out inside a CI job reads as a hang and gets the run killed at the job
    # timeout — so the client raises instead and the caller wraps up the run.
    courtlistener_max_wait: float = 300.0
    # How read-only consumers open the corpus: "local" reads the dvc-pulled file,
    # "ranged" queries the immutable blob in place on the DVC remote via HTTP
    # range requests (see fedcourtsai.corpus_ranged). Writers always open local.
    corpus_backend: Literal["local", "ranged"] = "local"
    # The DVC remote's bucket URL, supplied out of band exactly like the
    # workflows' `dvc remote add` step (never committed; see SECURITY.md). The
    # ranged backend resolves the corpus pointer against it. The bare workflow
    # variable name is accepted as an alias so the same runner env serves both.
    dvc_remote_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FEDCOURTS_DVC_REMOTE_URL", "DVC_REMOTE_URL"),
    )


def get_settings() -> Settings:
    return Settings()


TRACKING_FILENAME = "tracking.yaml"


class PullConfig(BaseModel):
    """The ``pull`` section of ``config/tracking.yaml`` — the API-budget governor.

    ``config/tracking.yaml`` is the single place to tune scope and the
    CourtListener budget; this models just the keys the governor enforces (extra
    keys, like the rotation/discovery toggles, are ignored).
    """

    model_config = ConfigDict(extra="ignore")

    # Hard per-run cap on dockets refreshed (~3 requests each). Sized to the
    # active CourtListener tier and how many windows the schedule runs per day, so
    # the day's total stays under the daily ceiling and a single run stays under
    # the hourly ceiling (tier-hr ÷ ~3).
    max_cases_per_run: int = Field(default=15, ge=0)
    # Don't spend budget re-fetching closed / resolved cases.
    skip_closed: bool = True
    # Reserve up to this many of each run's slots for the stalest predict-eligible
    # cases, so the SCOTUS-touched pilot set rotates ahead of the much larger
    # general active set. Unused reserve slots fall through to the normal
    # stalest-first rotation, so it never wastes budget; 0 disables the bias.
    eligible_refresh_reserve: int = Field(default=0, ge=0)
    # Discover newly-filed dockets in the tracked courts since the last run.
    discover_new_filings: bool = True
    # Hard cap on new dockets onboarded per run (its own slice of the budget,
    # separate from the refresh cap above).
    max_new_cases_per_run: int = Field(default=10, ge=0)
    # Wall-clock budget for one `pull-all` run, in minutes, checked between
    # cases (and between courts during discovery). Sized below the workflow's
    # job timeout so a run against a degraded upstream stops, defers the rest of
    # the rotation to the next window, and still lands its queues and corpus
    # writes — instead of being killed mid-run and losing everything.
    max_run_minutes: float = Field(default=25.0, gt=0)
    # Stop the refresh rotation after this many consecutive transient REST
    # failures (timeouts / 5xx / 429): the upstream is degraded, and each doomed
    # case burns a full retry cycle of budget and wall clock. Deterministic
    # per-case errors (e.g. a 404) never trip it. Deferred cases keep their
    # stalest-first position, so the next window retries them.
    max_consecutive_transient_failures: int = Field(default=5, ge=1)


def load_pull_config(config_root: Path) -> PullConfig:
    """Read the governor's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``pull`` section is absent, so the
    governor stays conservative rather than failing when config is missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return PullConfig.model_validate((data or {}).get("pull", {}))


class LiveConfig(BaseModel):
    """The ``live:`` section of ``tracking.yaml`` — the SCOTUS live channel (#472).

    The supremecourt.gov docket JSON has no API budget, so these caps bound
    wall-clock per cycle and upstream politeness, not spend: at the default
    ~1 req/s throttle a full cycle (discovery + refresh) stays around a minute.
    """

    model_config = ConfigDict(extra="ignore")

    # Pending petitions re-polled per cycle (the watchlist refresh rotation).
    max_cases_per_run: int = Field(default=30, ge=0)
    # New petitions onboarded from the Term's numbering frontier per cycle.
    max_new_cases_per_run: int = Field(default=25, ge=0)
    # Oldest October Term the refresh rotation reaches — the reachability
    # probe's floor (docs/live-sources-probe.md): full JSON coverage OT2017+.
    term_floor_year: int = Field(default=2017, ge=1925)
    # Polite-client pacing between requests, seconds.
    throttle_seconds: float = Field(default=1.0, gt=0)
    # Consecutive 404s that mark a numbering stream's frontier (serials are
    # assigned sequentially; the tolerance bridges an occasional withheld one).
    frontier_misses: int = Field(default=2, ge=1)
    # Per-document cap on extracted text stored in the corpus (#474): petitions
    # run 30-300 pages, and the cap is what keeps the DVC blob's growth sane.
    # ~150k characters is roughly 40 dense pages — the petition's argument in
    # full for a typical filing; a longer one is stored truncated (and flagged).
    document_text_cap: int = Field(default=150_000, ge=1_000)


def load_live_config(config_root: Path) -> LiveConfig:
    """Read the live channel's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``live`` section is absent,
    mirroring :func:`load_pull_config`.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return LiveConfig.model_validate((data or {}).get("live", {}))


class SeedLiveConfig(BaseModel):
    """The ``seed_live:`` section of ``tracking.yaml`` — the past-Term cert loader.

    Drives ``fedcourts seed-live-terms`` (the run-seed live-terms mode): a
    sequential walk of decided past Terms over the supremecourt.gov docket JSON
    that builds the cert back-test set. The sampling frame lives here so the
    set's construction is documented and reproducible: **every decided petition
    is ingested except denials, which are systematically sampled** — a denial
    is kept when its docket serial is a multiple of ``denial_sample_every``
    (deterministic per serial, so a resumed run keeps the same sample). No API
    budget: the caps bound per-invocation wall clock and upstream politeness.
    """

    model_config = ConfigDict(extra="ignore")

    # Two-digit October Terms to walk, in walk order. Floor OT2017 — the
    # reachability probe's full-JSON floor (docs/live-sources-probe.md).
    terms: list[int] = Field(default=[24, 23, 22, 21, 20, 19, 18, 17])
    # Keep a denial when serial % denial_sample_every == 0 (1 keeps every denial).
    denial_sample_every: int = Field(default=10, ge=1)
    # Docket-JSON probes per invocation = the run-seed loop's checkpoint chunk
    # (~10 min at the polite 1 req/s; document fetches ride on top).
    max_probes_per_run: int = Field(default=600, ge=0)
    # Per-invocation wall-clock backstop, minutes, checked between serials.
    max_run_minutes: float = Field(default=20.0, gt=0)
    # Consecutive 404s that mark a (Term, stream)'s frontier — for a finished
    # Term, the end of its docket sequence.
    frontier_misses: int = Field(default=2, ge=1)
    # Polite-client pacing between requests, seconds.
    throttle_seconds: float = Field(default=1.0, gt=0)
    # Oldest two-digit Term whose ingested petitions get their filed documents
    # fetched (#474): links are a rolling ~5-Term window upstream, near-zero
    # before ~OT2021, so older Terms load as metadata+proceedings-only rows.
    document_floor_term: int = Field(default=21, ge=0, le=99)
    # Per-document cap on extracted text stored in the corpus (see `live:`).
    document_text_cap: int = Field(default=150_000, ge=1_000)

    @field_validator("terms")
    @classmethod
    def _terms_in_served_range(cls, terms: list[int]) -> list[int]:
        # OT2017 is the probe-established floor; two-digit Term form above it.
        bad = [t for t in terms if not 17 <= t <= 99]
        if bad:
            raise ValueError(f"terms must be two-digit October Terms >= 17: {bad}")
        return terms


def load_seed_live_config(config_root: Path) -> SeedLiveConfig:
    """Read the past-Term loader's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``seed_live`` section is absent,
    mirroring :func:`load_live_config`.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return SeedLiveConfig.model_validate((data or {}).get("seed_live", {}))


def load_courts(config_root: Path) -> list[str]:
    """The tracked courts from ``config_root/tracking.yaml`` (``courts:``).

    The scope ``seed`` backfills and ``pull`` keeps current. Returns an empty
    list if the file or its ``courts`` key is absent, so callers degrade to a
    no-op rather than crashing on missing config.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    courts = (data or {}).get("courts", []) or []
    return [str(c).strip() for c in courts if str(c).strip()]


class PredictScope(StrEnum):
    """The prediction-scope gate the agentic predict/evaluate fan-out honors.

    Ingestion (seed/pull) is always full-coverage; this restricts only the
    expensive predict/evaluate stages (see ``docs/data-pipeline.md``).
    """

    # Only cases that have interacted with SCOTUS (the latched `predict_eligible`
    # flag) are in-scope — the pilot cost gate.
    scotus_touched = "scotus_touched"
    # No gate: every changed case with open events is in-scope (dev / back-testing).
    all = "all"


class PredictConfig(BaseModel):
    """The ``predict`` section of ``config/tracking.yaml`` — the fan-out gate.

    Models just the keys the predict/evaluate seams enforce; extra keys (the
    parallelism / skip-resolved knobs the workflow reads) are ignored.
    """

    model_config = ConfigDict(extra="ignore")

    # Which cases the agentic stages run on; `scotus_touched` is the pilot default.
    scope: PredictScope = PredictScope.scotus_touched


def load_predict_config(config_root: Path) -> PredictConfig:
    """Read the prediction-scope gate from ``config_root/tracking.yaml``.

    Falls back to defaults (the gate on) if the file or its ``predict`` section is
    absent, so the cost gate stays conservative rather than failing when config is
    missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return PredictConfig.model_validate((data or {}).get("predict", {}))


class SeedConfig(BaseModel):
    """The ``seed`` section of ``config/tracking.yaml`` — the bulk-backfill knobs.

    Seed spends no API budget; ``max_cases_per_run`` caps how many cases a single
    ``seed-backfill`` invocation loads. The run-seed workflow loops the command
    over one staged snapshot, committing after each pass, so this is the
    **per-checkpoint chunk size** — how much progress a crash can lose and how
    often the corpus blob is pushed — not the ceiling on a whole scheduled run
    (that is the workflow's wall-clock budget). Only the keys the backfill command
    needs are modeled (extra keys, like ``source``, are ignored).
    """

    model_config = ConfigDict(extra="ignore")

    # Cases loaded per `seed-backfill` invocation = the workflow loop's checkpoint
    # chunk (`--max-cases` may only lower it for a one-off run).
    max_cases_per_run: int = Field(default=2000, ge=0)
    # Committed cursor recording per-court backfill progress (resumable rebuild).
    cursor: Path = Path("config/seed-progress.yaml")


def load_seed_config(config_root: Path) -> SeedConfig:
    """Read the backfill settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``seed`` section is absent, so the
    backfill stays conservative rather than failing when config is missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return SeedConfig.model_validate((data or {}).get("seed", {}))
