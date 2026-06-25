"""Stable identifier and slug helpers.

IDs are designed to be filesystem-safe and stable across pulls so that git
history for a given case / event / prediction stays coherent over time.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

_SLUG_RE = re.compile(r"[^a-z0-9._-]+")


def slugify(value: str) -> str:
    """Lowercase, filesystem-safe slug (no whitespace, slashes, or quotes).

    Runs of disallowed characters collapse to a single hyphen.
    """
    s = _SLUG_RE.sub("-", value.strip().lower())
    return s.strip("-") or "x"


def case_id(court_id: str, docket_id: int) -> str:
    """Canonical case identifier, e.g. ``ca9/64512345``."""
    return f"{slugify(court_id)}/{docket_id}"


def event_id(kind: str, label: str) -> str:
    """Event identifier, e.g. ``evt-motion-stay-pending-appeal``."""
    return f"evt-{slugify(kind)}-{slugify(label)}"


def run_id(now: datetime | None = None) -> str:
    """UTC timestamp run id, e.g. ``20260624T103000Z``.

    A run id namespaces one predictor/evaluator invocation so multiple runs
    never collide on disk.
    """
    now = now or datetime.now(UTC)
    return now.strftime("%Y%m%dT%H%M%SZ")


_RUN_ID_FMT = "%Y%m%dT%H%M%SZ"


def parse_run_id(value: str) -> datetime:
    """Inverse of :func:`run_id`: a UTC-aware datetime from a run-id timestamp.

    Raises ``ValueError`` if ``value`` is not a ``YYYYMMDDThhmmssZ`` stamp, so
    callers can fall back to an explicit timestamp.
    """
    return datetime.strptime(value, _RUN_ID_FMT).replace(tzinfo=UTC)
