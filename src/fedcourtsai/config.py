"""Runtime settings, read from environment (prefix ``FEDCOURTS_``) or ``.env``.

Secrets (the CourtListener token) come from the environment only and are never
written to disk or committed.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEDCOURTS_", env_file=".env", extra="ignore")

    data_root: Path = Path("data")
    config_root: Path = Path("config")
    corpus_root: Path = Path("corpus")
    metrics_root: Path = Path("metrics")
    courtlistener_base_url: str = "https://www.courtlistener.com/api/rest/v4/"
    courtlistener_api_token: str | None = None
    # Seed reads CourtListener's *public bulk-data* CSV (no API token). May be the
    # bulk-data *directory* (e.g. `.../bulk-data/`) — seed then resolves the latest
    # `dockets-YYYY-MM-DD` file and follows new snapshots automatically — or a
    # pinned file URL. Injected from the runner env; absent, `seed-backfill` no-ops.
    courtlistener_bulk_url: str | None = None
    seed_snapshot: str | None = None
    request_timeout: float = 30.0
    # CourtListener per-token rate limits (issue #1); override via FEDCOURTS_* env.
    courtlistener_rpm: int = 5
    courtlistener_rph: int = 50
    courtlistener_rpd: int = 125


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

    # ~15 dockets ≈ 45 requests, under the 50/hr ceiling, so a run finishes
    # without the rate limiter forcing long sleeps. A hard per-run cap.
    max_cases_per_run: int = Field(default=15, ge=0)
    # Don't spend budget re-fetching closed / resolved cases.
    skip_closed: bool = True
    # Discover newly-filed dockets in the tracked courts since the last run.
    discover_new_filings: bool = True
    # Hard cap on new dockets onboarded per run (its own slice of the budget,
    # separate from the refresh cap above).
    max_new_cases_per_run: int = Field(default=10, ge=0)


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


class SeedConfig(BaseModel):
    """The ``seed`` section of ``config/tracking.yaml`` — the bulk-backfill knobs.

    Seed spends no API budget; ``max_cases_per_run`` is a CI-time / PR-size
    guardrail on how many cases one chunk loads from the bulk snapshot. Only the
    keys the backfill command needs are modeled (extra keys, like ``source``, are
    ignored).
    """

    model_config = ConfigDict(extra="ignore")

    # Cases materialized per scheduled run; a hard per-run cap (`--max-cases` may
    # only lower it for a one-off run).
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
