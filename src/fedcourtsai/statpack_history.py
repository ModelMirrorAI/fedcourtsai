"""The statpack build in force at provisioning, and the check a frozen anchor answers to.

A cert cell's ``context.cert_anchor`` is written at provisioning into
``record/context.json``, a file the cell's own workspace can reach, so every
field of it is a claim. Checking the record against itself proves nothing — an
edited record can name any older real build, any window, and the rate that
build pools to — so :func:`verify_cert_anchor` derives the anchor that was in
force from inputs the agent cannot reach, and accepts the record only where it
is that anchor:

- the **bound** is the predict cell's run id, the UTC timestamp the harness
  mints before the cell is provisioned and names its ledger directory with
  (never the document's own ``run_id`` or ``created_at``, the second of which
  is stamped after the agent has run);
- the **build** is the newest committed revision of ``metrics/statpack.json``
  at or before that bound, and the record must name its digest — an earlier
  build is refused even where it is real;
- the **window** is ``salience.base_rate_lookback_terms`` as committed in
  ``config/tracking.yaml`` at that build's commit;
- the **rate** is :func:`fedcourtsai.pipeline.base_rates.prediction_base_rate`
  over the scored context and that build under that window.

Two builds that publish identical figures share a digest
(:func:`fedcourtsai.pipeline.base_rates.statpack_digest`) and so verify as one.

The history is read through an injectable :class:`StatpackHistory`, so a test
hands in revisions directly; :class:`GitStatpackHistory` is the production
reader. It needs the full history the evaluate and analytics checkouts fetch: a
shallow clone sees only the revisions it holds, and an anchor its history
cannot place is refused rather than trusted. Blobs are read with
``cat-file blob`` under ``--no-replace-objects``, so a ``refs/replace`` entry
cannot stand a different object in for a committed one.
"""

from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

import yaml
from pydantic import ValidationError

from .config import TRACKING_FILENAME, SalienceConfig
from .pipeline.base_rates import prediction_base_rate, statpack_digest
from .schemas import CertAnchor, PredictionContext, StatPack

#: How far a frozen rate may sit from its re-pool over the build in force. Float
#: noise only: both sides run one pooler over one build and one window.
FROZEN_ANCHOR_TOLERANCE = 1e-9

_GIT_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class CommittedBuild:
    """One committed revision of ``metrics/statpack.json``."""

    sha: str
    committed_at: datetime
    statpack: StatPack | None
    """The parsed pack, or ``None`` where the blob does not parse as the current model."""


class StatpackHistory(Protocol):
    """The harness-side record a frozen anchor is checked against."""

    def newest_build(self, bound: datetime) -> CommittedBuild | None:
        """The newest committed statpack revision at or before ``bound``, or ``None``."""
        ...

    def lookback_terms_at(self, sha: str) -> int | None:
        """``salience.base_rate_lookback_terms`` as committed at ``sha``, or ``None``."""
        ...


class GitStatpackHistory:
    """:class:`StatpackHistory` over the repository ``metrics_root`` and ``config_root`` sit in."""

    def __init__(self, metrics_root: Path, config_root: Path) -> None:
        self._metrics_root = metrics_root
        self._config_root = config_root

    def newest_build(self, bound: datetime) -> CommittedBuild | None:
        """By committer date, over every revision reachable from ``HEAD``.

        ``None`` where git is missing, ``metrics_root`` is in no work tree, no
        revision is that old, or the chosen blob cannot be read.
        """
        log = _git(self._metrics_root, "log", "--format=%H %cI", "--", "statpack.json")
        if log is None:
            return None
        newest: tuple[datetime, str] | None = None
        for line in log.splitlines():
            sha, _, when = line.partition(" ")
            try:
                committed = datetime.fromisoformat(when)
            except ValueError:
                continue
            if committed <= bound and (newest is None or committed > newest[0]):
                newest = (committed, sha)
        if newest is None:
            return None
        text = _git(self._metrics_root, "cat-file", "blob", f"{newest[1]}:./statpack.json")
        if text is None:
            return None
        try:
            pack: StatPack | None = StatPack.model_validate_json(text)
        except ValueError:
            pack = None
        return CommittedBuild(sha=newest[1], committed_at=newest[0], statpack=pack)

    def lookback_terms_at(self, sha: str) -> int | None:
        text = _git(self._config_root, "cat-file", "blob", f"{sha}:./{TRACKING_FILENAME}")
        if text is None:
            return None
        try:
            data = yaml.safe_load(text) or {}
            return SalienceConfig.model_validate(data.get("salience", {})).base_rate_lookback_terms
        except (yaml.YAMLError, ValidationError, AttributeError):
            return None


def _git(cwd: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "--no-replace-objects", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout


def verify_cert_anchor(
    anchor: CertAnchor,
    context: PredictionContext,
    provisioned_by: datetime,
    history: StatpackHistory,
) -> str | None:
    """Why ``anchor`` is not the anchor in force at ``provisioned_by``, or ``None``.

    ``provisioned_by`` is the predict cell's harness-minted run-id time. The
    anchor verifies where it names the digest of the newest statpack build
    committed at or before it, records the lookback window configured at that
    build's commit, and carries the rate that build pools to over ``context``
    under that window — a null rate only where the pool is empty too.
    """
    build = history.newest_build(provisioned_by)
    if build is None:
        return f"no committed statpack build at or before {provisioned_by.isoformat()}"
    if build.statpack is None:
        return f"the statpack build in force ({build.sha[:12]}) does not parse"
    refusal = _in_force_refusal(anchor, build.sha, build.statpack, history)
    if refusal is not None:
        return refusal
    expected = prediction_base_rate(context, build.statpack, lookback_terms=anchor.lookback_terms)
    reproduces = (
        expected is None and anchor.rate is None
        if expected is None or anchor.rate is None
        else math.isclose(expected, anchor.rate, rel_tol=0.0, abs_tol=FROZEN_ANCHOR_TOLERANCE)
    )
    return None if reproduces else "the frozen rate does not re-pool from the build in force"


def _in_force_refusal(
    anchor: CertAnchor, sha: str, statpack: StatPack, history: StatpackHistory
) -> str | None:
    """Why ``anchor`` does not name the build and window in force at ``sha``, or ``None``."""
    in_force = statpack_digest(statpack)
    if anchor.statpack_digest != in_force:
        return (
            f"it names {anchor.statpack_digest}, not the build in force at provisioning "
            f"({sha[:12]}, {in_force})"
        )
    lookback = history.lookback_terms_at(sha)
    if lookback is None:
        return f"no configured lookback window is readable at {sha[:12]}"
    if anchor.lookback_terms != lookback:
        return (
            f"it records lookback_terms {anchor.lookback_terms}, not the {lookback} "
            f"configured at {sha[:12]}"
        )
    return None
