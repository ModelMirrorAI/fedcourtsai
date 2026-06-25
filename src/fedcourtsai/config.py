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


def load_pull_config(config_root: Path) -> PullConfig:
    """Read the governor's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``pull`` section is absent, so the
    governor stays conservative rather than failing when config is missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return PullConfig.model_validate((data or {}).get("pull", {}))
