"""Shared test fixtures.

The :func:`fixture_corpus` fixture builds the synthetic corpus
(:mod:`fedcourtsai.fixture`) under a throwaway corpus root and points the CLI at
it, so the read commands run fully offline — no corpus remote, no CourtListener
token, no network — exactly as the offline local loop does.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

from fedcourtsai import casestore, corpus, fixture, process_version
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import salience as salience_module
from fedcourtsai.pipeline.salience import SalienceScorer
from fedcourtsai.schemas import Disposition, Evaluation, Prediction, ProcessVersion
from fedcourtsai.serialize import write_json


@pytest.fixture(autouse=True)
def _clear_pointer_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep an ambient corpus-pointer override out of every test's settings.

    ``eval "$(scripts/corpus-env staging)"`` exports the override into an
    interactive shell, and any test that touches ``get_settings()`` would
    inherit that live redirection — a gate result must not depend on which
    pair the invoking shell was flipped to.
    """
    for name in ("FEDCOURTS_CORPUS_POINTER", "CORPUS_POINTER"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def _reset_casestore_transport() -> Iterator[None]:
    """Keep the process-wide casestore transport cache from leaking across tests.

    The corpus write seams consult a cached transport; without this a test that
    sets ``FEDCOURTS_CASESTORE_URL`` (or injects one) could leave the store active
    for later tests in any file.
    """
    casestore.reset_active_transport()
    yield
    casestore.reset_active_transport()


class DictSnapshotSource:
    """A payload read source over a dict of stored snapshots.

    Just enough of :class:`fedcourtsai.corpus.PayloadReadSource` to serve
    ``latest_snapshot``, the one method the snapshot-reading sweeps exercise.
    Records the thread each read ran on, so a test can pin a pass's fetch
    schedule — which cases are read at all, and that none is read twice.
    """

    def __init__(self, snapshots: Mapping[str, tuple[date, dict[str, Any]] | None]) -> None:
        self._snapshots = snapshots
        self.read_threads: dict[str, list[int]] = {}
        self._lock = threading.Lock()

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        with self._lock:
            self.read_threads.setdefault(case_id, []).append(threading.get_ident())
        return self._snapshots.get(case_id)

    def snapshot_at(self, case_id: str, *, before: date) -> tuple[date, dict[str, Any]] | None:
        return None

    def latest_live_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        return None

    def documents_for_case(self, case_id: str) -> list[corpus.CaseDocument]:
        return []

    def opinion_text(self, case_id: str) -> str | None:
        return None


@dataclass(frozen=True)
class FixtureCorpus:
    """A built fixture corpus and the roots the CLI reads it from."""

    corpus_root: Path
    data_root: Path

    @property
    def db_path(self) -> Path:
        return corpus.corpus_db_path(self.corpus_root)


@pytest.fixture
def fixture_corpus(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FixtureCorpus:
    """Build the synthetic fixture corpus and configure the CLI to read it offline.

    Sets ``FEDCOURTS_CORPUS_ROOT`` / ``FEDCOURTS_DATA_ROOT`` to throwaway paths and
    clears the CourtListener token so a command that reaches for the remote would
    fail loudly rather than silently use ambient credentials.
    """
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    fixture.build_fixture_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.delenv("FEDCOURTS_COURTLISTENER_API_TOKEN", raising=False)
    return FixtureCorpus(corpus_root=corpus_root, data_root=data_root)


def frozen_stamp() -> ProcessVersion:
    """A harness stamp inside the frozen partition: blessed digest, post-freeze.

    ``is_frozen`` is a membership test over
    :data:`fedcourtsai.process_version.FROZEN_PROCESS_DIGESTS` plus a time
    bound, so any blessed digest serves; the stamp is read off the module rather
    than written out, so a freeze cutover moves it without touching a test.
    """
    since = process_version.FROZEN_SINCE or datetime(2026, 1, 1, tzinfo=UTC)
    return ProcessVersion(
        label=process_version.CURRENT_PROCESS_LABEL,
        digest=sorted(process_version.FROZEN_PROCESS_DIGESTS)[0],
        stamped_at=since,
    )


def seed_prediction(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    *,
    predictor_id: str = "claude-baseline",
    frozen: bool = False,
) -> None:
    """Commit one minimal valid prediction into the ledger under ``data_root``.

    The evaluate paths now gate on a committed prediction existing for an event
    (nothing to score = no evaluator cell); tests asserting the evaluate
    handoff seed one with this instead of hand-rolling the layout.

    ``frozen`` stamps it into the frozen process partition. The default leaves
    it unstamped — a shakedown cell, which is what the pre-freeze ledger holds —
    so a gate that asks whether a claimable board counts the cohort
    (:func:`fedcourtsai.store.event_has_claimable_prediction`) sees the harder
    case unless a test asks for the easier one.
    """
    run_id = "20260101T000000Z"
    write_json(
        CasePaths(data_root, court, docket).event(event_id).prediction(predictor_id, run_id),
        Prediction(
            case_id=f"{court}/{docket}",
            event_id=event_id,
            predictor_id=predictor_id,
            engine="claude-code",
            model="claude-fable-5",
            run_id=run_id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.05,
            predicted_disposition=Disposition.denied,
            process_version=frozen_stamp() if frozen else None,
        ),
    )


def seed_evaluation(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    *,
    evaluator_id: str = "claude-judge",
    predictor_id: str = "claude-baseline",
    run_id: str = "20260101T000000Z",
) -> None:
    """Commit one minimal evaluation into the ledger under ``data_root``.

    The counterpart of :func:`seed_prediction`, for the already-evaluated gate.
    A schema-true body, not a stub: the gate tests, and the roll-ups that
    collapse a cell's re-runs, both have to *read* these files.
    """
    write_json(
        CasePaths(data_root, court, docket)
        .event(event_id)
        .evaluation(evaluator_id, predictor_id, run_id),
        Evaluation(
            case_id=f"{court}/{docket}",
            event_id=event_id,
            predictor_id=predictor_id,
            evaluator_id=evaluator_id,
            engine="claude-code",
            run_id=run_id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
        ),
    )


def _toy_scorer() -> SalienceScorer:
    """A second registered salience version: two bands, its own carve-out and scale.

    Nothing about it resembles sal-v1, on purpose. Sharing a band vocabulary
    would let a cross-version bug produce a plausible number instead of an
    error; with a disjoint one, a band leaking across versions raises.
    """
    return SalienceScorer(
        version="sal-toy",
        score=lambda row: 0.9 if row.cvsg_date is not None else 0.1,
        band=lambda row: "hot" if row.cvsg_date is not None else "cold",
        bands=("hot", "cold"),
        carve_out=lambda row, score, floor: row.cvsg_date is not None,
    )


@pytest.fixture
def two_versions(monkeypatch: pytest.MonkeyPatch) -> SalienceScorer:
    """Register a toy scorer beside the active one for the duration of a test.

    Every claim the scorer registry makes is about what happens when a SECOND
    version exists, so the single shipped version cannot exercise any of it — a
    loop over one entry passes with the loop deleted. This fixture is the only
    way the multi-version paths run at all.
    """
    toy = _toy_scorer()
    monkeypatch.setattr(
        salience_module, "SCORERS", MappingProxyType({**salience_module.SCORERS, toy.version: toy})
    )
    return toy


def open_freeze_window() -> tuple[str, datetime] | None:
    """One digest and a stamp inside the live `[bless, instant)` window, or None.

    The shape a predict round lands while the counting instant is still ahead:
    a blessed digest, minted after the promotion that made its bytes immutable
    and before the headline starts counting. Read off the module so a freeze
    cutover moves every window test at once, and returns ``None`` where no
    such window is open — nothing blessed, no instant, or the instant already
    reached — which the callers turn into a skip.

    The latest-blessed digest is the one a round stamps under the current
    predictor-half re-bless, where it is the enforced half; after an
    evaluator-half re-bless it would be an evaluator digest instead, and the
    window it reports simply closes.

    The stamp is taken from the instant's edge rather than the bless moment's,
    so these tests keep running for the whole life of a late-guessed instant
    instead of only the day after the promotion.
    """
    since = process_version.FROZEN_SINCE
    if not process_version.FROZEN_PROCESS_DIGESTS or since is None:
        return None
    digest, blessed = max(process_version.FROZEN_PROCESS_DIGESTS.items(), key=lambda kv: kv[1])
    minted = since - timedelta(seconds=1)
    return None if minted < blessed else (digest, minted)


def bless_process(
    monkeypatch: pytest.MonkeyPatch,
    *digests: str,
    since: datetime | None = None,
    blessed_at: datetime = datetime(1970, 1, 1, tzinfo=UTC),
) -> None:
    """Patch the frozen digest map AND the freeze instant together.

    Patching the map alone is an incomplete freeze by construction: the real
    module-level ``FROZEN_SINCE`` would leak into the test, which is exactly
    how a test goes red on the actual freeze commit. ``since`` defaults to
    ``None`` — no time gate — because most tests exercise digest membership;
    pass an instant to exercise the cutoff itself.

    ``blessed_at`` is the *other* boundary — when the digests became immutable
    on ``main``, which the retroactivity tripwire reads. It defaults to the
    epoch, so every stamp a test invents is trivially post-bless; pass it only
    to exercise that boundary.
    """
    monkeypatch.setattr(
        process_version,
        "FROZEN_PROCESS_DIGESTS",
        MappingProxyType({digest: blessed_at for digest in digests}),
    )
    monkeypatch.setattr(process_version, "FROZEN_SINCE", since)
