"""The committed statpack builds, read back from git, and the check a frozen anchor answers to.

A cert cell's ``context.cert_anchor`` is written at provisioning into
``record/context.json``, a file the cell's own workspace can reach. The
digest it names is therefore a claim, not a fact, until a committed build
carries it: :func:`verify_cert_anchor` finds that build in the history of
``metrics/statpack.json``, re-pools the anchor over it with the scorer's own
pooler, and accepts the record only where the rate reproduces and the build
was committed no later than the prediction it scores.

The history is read through an injectable :data:`StatpackHistory`, so a test
hands in revisions directly; :func:`git_statpack_history` is the production
reader. It walks ``git log`` from ``HEAD``, newest first, which needs the full
history the evaluate and analytics checkouts fetch: a shallow clone sees only
the revisions it holds, and a build it cannot see is refused rather than
trusted.
"""

from __future__ import annotations

import math
import subprocess
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .pipeline.base_rates import prediction_base_rate, statpack_digest
from .schemas import CertAnchor, PredictionContext, StatPack

#: One committed revision of the statpack: when it was committed, and its text.
StatpackRevision = tuple[datetime, str]

#: The revisions of ``metrics_root/statpack.json``, newest first.
StatpackHistory = Callable[[Path], Iterable[StatpackRevision]]

#: How far a frozen rate may sit from its re-pool over the build it names. Float
#: noise only: both sides run one pooler over one build and one window.
FROZEN_ANCHOR_TOLERANCE = 1e-9

_GIT_TIMEOUT_SECONDS = 30


def git_statpack_history(metrics_root: Path) -> Iterator[StatpackRevision]:
    """Every committed revision of ``metrics_root/statpack.json`` reachable from ``HEAD``.

    Newest first, lazily, so a caller that stops at its match reads no older
    revision. Yields nothing where git is missing, ``metrics_root`` is not in a
    work tree, or a read fails: an unreadable history verifies no anchor.
    """
    log = _git(metrics_root, "log", "--format=%H %cI", "--", "statpack.json")
    if log is None:
        return
    for line in log.splitlines():
        sha, _, when = line.partition(" ")
        text = _git(metrics_root, "show", f"{sha}:./statpack.json")
        if text is None:
            continue
        try:
            committed = datetime.fromisoformat(when)
        except ValueError:
            continue
        yield committed, text


def _git(cwd: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout


@dataclass(frozen=True)
class CommittedBuild:
    """The committed statpack whose digest a frozen anchor names."""

    committed_at: datetime
    statpack: StatPack


def find_statpack_build(
    digest: str, revisions: Iterable[StatpackRevision]
) -> CommittedBuild | None:
    """The newest committed revision whose :func:`statpack_digest` is ``digest``, or ``None``.

    A revision that does not parse as the current :class:`StatPack` is
    skipped: its digest under this model is not the one any reader computes.
    """
    for committed_at, text in revisions:
        try:
            pack = StatPack.model_validate_json(text)
        except ValueError:
            continue
        if statpack_digest(pack) == digest:
            return CommittedBuild(committed_at=committed_at, statpack=pack)
    return None


def verify_cert_anchor(
    anchor: CertAnchor,
    context: PredictionContext,
    predicted_at: datetime,
    revisions: Iterable[StatpackRevision],
) -> str | None:
    """Why ``anchor`` cannot be trusted, or ``None`` where it verifies.

    It verifies where a committed build carries the digest it names, that build
    was committed no later than ``predicted_at`` (the forecast cannot have been
    placed against a pack that did not exist yet), and
    :func:`prediction_base_rate` over ``context`` and that build, under the
    recorded window, yields the recorded rate — a null rate only where the pool
    is empty too.
    """
    build = find_statpack_build(anchor.statpack_digest, revisions)
    if build is None:
        return f"no committed statpack build carries {anchor.statpack_digest}"
    if build.committed_at > predicted_at:
        return (
            f"the statpack build {anchor.statpack_digest} was committed "
            f"{build.committed_at.isoformat()}, after the prediction"
        )
    expected = prediction_base_rate(context, build.statpack, lookback_terms=anchor.lookback_terms)
    if expected is None or anchor.rate is None:
        if expected is None and anchor.rate is None:
            return None
        return "the frozen rate does not re-pool from the build it names"
    if not math.isclose(expected, anchor.rate, rel_tol=0.0, abs_tol=FROZEN_ANCHOR_TOLERANCE):
        return "the frozen rate does not re-pool from the build it names"
    return None
