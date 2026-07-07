"""Runtime settings, read from environment (prefix ``FEDCOURTS_``) or ``.env``.

Secrets (the CourtListener token) come from the environment only and are never
written to disk or committed.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
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
    # Interim date backfill (superseded by the replicated CourtListener database):
    # carve up to this many of each run's `max_cases_per_run` slots for dockets
    # whose corpus rows lack every decision-time date — total REST spend per run
    # is unchanged; the general rotation slows by the same count while the
    # dateless pool drains. 0 disables the backfill entirely.
    backfill_reserve: int = Field(default=0, ge=0)
    # Also target *unresolved* SCOTUS modern-cert shells from this October Term
    # forward (recent Terms first): past-Term petitions are near-certainly decided
    # upstream, so one fetch dates, resolves, and snapshots each — the feeder that
    # grows the cert back-test set. None keeps the backfill to already-resolved
    # rows only.
    backfill_unresolved_cert_min_term: int | None = Field(default=None, ge=1925)


def load_pull_config(config_root: Path) -> PullConfig:
    """Read the governor's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``pull`` section is absent, so the
    governor stays conservative rather than failing when config is missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return PullConfig.model_validate((data or {}).get("pull", {}))


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
