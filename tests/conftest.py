"""Shared test fixtures.

The :func:`fixture_corpus` fixture builds the synthetic corpus
(:mod:`fedcourtsai.fixture`) under a throwaway corpus root and points the CLI at
it, so the read commands run fully offline — no corpus remote, no CourtListener
token, no network — exactly as the offline local loop does.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fedcourtsai import casestore, corpus, fixture
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import Disposition, Prediction
from fedcourtsai.serialize import write_json


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


def seed_prediction(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    *,
    predictor_id: str = "claude-baseline",
) -> None:
    """Commit one minimal valid prediction into the ledger under ``data_root``.

    The evaluate paths now gate on a committed prediction existing for an event
    (nothing to score = no evaluator cell); tests asserting the evaluate
    handoff seed one with this instead of hand-rolling the layout.
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
    Only the path shape matters to the gate, so the body stays minimal.
    """
    path = (
        CasePaths(data_root, court, docket)
        .event(event_id)
        .evaluation(evaluator_id, predictor_id, run_id)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}")
