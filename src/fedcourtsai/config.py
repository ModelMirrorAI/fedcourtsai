"""Runtime settings, read from environment (prefix ``FEDCOURTS_``) or ``.env``.

Secrets (the CourtListener token) come from the environment only and are never
written to disk or committed.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEDCOURTS_", env_file=".env", extra="ignore")

    data_root: Path = Path("data")
    config_root: Path = Path("config")
    courtlistener_base_url: str = "https://www.courtlistener.com/api/rest/v4/"
    courtlistener_api_token: str | None = None
    request_timeout: float = 30.0
    # CourtListener per-token rate limits (issue #1); override via FEDCOURTS_* env.
    courtlistener_rpm: int = 5
    courtlistener_rph: int = 50
    courtlistener_rpd: int = 125


def get_settings() -> Settings:
    return Settings()
