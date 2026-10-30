"""The statpack build in force at provisioning, and the check a frozen anchor answers to.

A cert cell's ``context.cert_anchor`` is written at provisioning into
``record/context.json``, a file the cell's own workspace can reach, so every
field of it is a claim. Checking the record against itself proves nothing — an
edited record can name any older real build, any window, and the rate that
build pools to — so :func:`verify_cert_anchor` derives the anchor that was in
force from harness-side inputs, and accepts the record only where it is that
anchor:

- the **bound** is the predict cell's run id, the UTC timestamp the harness
  mints in the plan job and names its ledger directory with (never the
  document's own ``run_id`` or ``created_at``, the second of which is stamped
  after the agent has run);
- the **build** is the revision of ``metrics/statpack.json`` in force on
  ``main`` at that bound: the newest first-parent commit of ``main`` touching
  the file whose committer time is at or before it. First-parent, because a
  statpack refresh lands through a merge, and the merge's time is when it
  reached ``main``; the branch commit beneath it is dated earlier and was never
  in force on its own. The record must name its digest — an earlier build is
  refused even where it is real — with one exception, :data:`CHECKOUT_SLACK`:
  a cell checks out the commit its run was triggered on, before the plan job
  mints the run id, so where the build in force landed inside that slack before
  the bound, the build it replaced is accepted too;
- the **window** is ``salience.base_rate_lookback_terms`` as committed in
  ``config/tracking.yaml`` at that build's commit;
- the **rate** is :func:`fedcourtsai.pipeline.base_rates.prediction_base_rate`
  over the scored context and that build under that window.

Two builds that publish identical figures share a digest
(:func:`fedcourtsai.pipeline.base_rates.statpack_digest`) and so verify as one.

The history is read through an injectable :class:`StatpackHistory`, so a test
hands in revisions directly; :class:`GitStatpackHistory` is the production
reader. Where it runs matters, because the evaluate cell's agent runs as the
same user in the same checkout before the stamp and can commit there, back-date
a revision, move a ref or edit the repository's git config. The evaluate
workflow therefore hands the stamp a bare clone of ``main`` it makes *after*
the agent's step, from the repository URL with the user's and the system's git
config ignored, and the reader walks that clone's ``main``; an anchor naming a
commit that is not on it is refused. Read off the checkout (the default, for a
local run), the check is only as good as that checkout. A shallow history sees
only the revisions it holds, and an anchor it cannot place is refused rather
than trusted. Blobs are read with ``cat-file blob`` under
``--no-replace-objects``, so a ``refs/replace`` entry cannot stand a different
object in for a committed one.
"""

from __future__ import annotations

import math
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol

import yaml
from pydantic import ValidationError

from .config import SalienceConfig
from .pipeline.base_rates import prediction_base_rate, statpack_digest
from .schemas import CertAnchor, PredictionContext, StatPack

#: How far a frozen rate may sit from its re-pool over the build in force. Float
#: noise only: both sides run one pooler over one build and one window.
FROZEN_ANCHOR_TOLERANCE = 1e-9

#: How long before the run-id bound a build may have landed and still leave the
#: one it replaced acceptable. A predict cell checks out the commit its run was
#: triggered on, and the plan job mints the run id later, after any queueing
#: for a runner or a concurrency slot; a refresh landing between the two is a
#: build the cell never saw. Over the forty most recent successful run-predict
#: runs before 2026-10-30, trigger to mint took about 70 seconds in the
#: typical run and 425 s, 1706 s, 4153 s and 19978 s in the four that queued,
#: the longest a dispatch that waited 5.5 hours for its first job. Six hours
#: covers that with margin. The cost is bounded: inside the slack a record may
#: name either of two consecutive real builds, each re-pooled here, and never
#: an older one.
CHECKOUT_SLACK = timedelta(hours=6)

#: The production paths, relative to the repository root.
STATPACK_PATH = "metrics/statpack.json"
TRACKING_PATH = "config/tracking.yaml"

#: The branch a checkout's landings are read from where no bare clone is given.
DEFAULT_REF = "origin/main"

_GIT_TIMEOUT_SECONDS = 120


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
        """The statpack revision in force on ``main`` at ``bound``, or ``None``."""
        ...

    def build_before(self, build: CommittedBuild) -> CommittedBuild | None:
        """The revision ``build`` replaced on ``main``, or ``None``."""
        ...

    def lookback_terms_at(self, sha: str) -> int | None:
        """``salience.base_rate_lookback_terms`` as committed at ``sha``, or ``None``."""
        ...


class GitStatpackHistory:
    """:class:`StatpackHistory` over ``ref``'s first-parent history in ``repo``.

    ``repo`` is a work tree or a bare repository; ``ref`` is the branch whose
    landing order counts (``main`` in a bare clone of it, ``origin/main`` in a
    checkout).
    """

    def __init__(self, repo: Path, ref: str) -> None:
        self._repo = repo
        self._ref = ref

    def _landings(self) -> list[tuple[datetime, str]]:
        """Every first-parent commit of ``ref`` touching the statpack, newest first."""
        log = _git(
            self._repo, "log", "--first-parent", "--format=%H %cI", self._ref, "--", STATPACK_PATH
        )
        landings = []
        for line in (log or "").splitlines():
            sha, _, when = line.partition(" ")
            try:
                landings.append((datetime.fromisoformat(when), sha))
            except ValueError:
                continue
        return landings

    def _read(self, landed: datetime, sha: str) -> CommittedBuild | None:
        text = _git(self._repo, "cat-file", "blob", f"{sha}:{STATPACK_PATH}")
        if text is None:
            return None
        try:
            pack: StatPack | None = StatPack.model_validate_json(text)
        except ValueError:
            pack = None
        return CommittedBuild(sha=sha, committed_at=landed, statpack=pack)

    def newest_build(self, bound: datetime) -> CommittedBuild | None:
        """The newest landing at or before ``bound``, by its own committer time.

        ``None`` where git is missing, ``repo`` holds no ``ref``, no landing is
        that old, or the chosen blob cannot be read.
        """
        for landed, sha in self._landings():
            if landed <= bound:
                return self._read(landed, sha)
        return None

    def build_before(self, build: CommittedBuild) -> CommittedBuild | None:
        landings = self._landings()
        for index, (_, sha) in enumerate(landings):
            if sha == build.sha:
                if index + 1 < len(landings):
                    return self._read(*landings[index + 1])
                return None
        return None

    def lookback_terms_at(self, sha: str) -> int | None:
        text = _git(self._repo, "cat-file", "blob", f"{sha}:{TRACKING_PATH}")
        if text is None:
            return None
        try:
            data = yaml.safe_load(text) or {}
            return SalienceConfig.model_validate(data.get("salience", {})).base_rate_lookback_terms
        except (yaml.YAMLError, ValidationError, AttributeError):
            return None


def _git(cwd: Path, *args: str) -> str | None:
    # The user's and the system's config are not read: the agent that ran
    # before the stamp could have written the first.
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    try:
        out = subprocess.run(
            ["git", "--no-replace-objects", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT_SECONDS,
            env=env,
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
    anchor verifies where it names the digest of the build in force on ``main``
    at that bound — or of the build that one replaced, where the replacement
    landed within :data:`CHECKOUT_SLACK` before the bound — records the lookback
    window configured at the named build's commit, and carries the rate that
    build pools to over ``context`` under that window (a null rate only where
    the pool is empty too). The refusal reported is the build in force's.
    """
    build = history.newest_build(provisioned_by)
    if build is None:
        return f"no committed statpack build at or before {provisioned_by.isoformat()}"
    refusal = _build_refusal(anchor, context, build, history)
    if refusal is None:
        return None
    if provisioned_by - build.committed_at <= CHECKOUT_SLACK:
        replaced = history.build_before(build)
        if replaced is not None and _build_refusal(anchor, context, replaced, history) is None:
            return None
    return refusal


def _build_refusal(
    anchor: CertAnchor, context: PredictionContext, build: CommittedBuild, history: StatpackHistory
) -> str | None:
    """Why ``anchor`` is not the anchor ``build`` yields over ``context``, or ``None``."""
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
