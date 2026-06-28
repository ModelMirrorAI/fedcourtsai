"""Shared test fixtures.

The :func:`fixture_corpus` fixture builds the synthetic corpus
(:mod:`fedcourtsai.fixture`) under a throwaway corpus root and points the CLI at
it, so the read commands run fully offline — no DVC remote, no CourtListener
token, no network — exactly as the offline local loop does.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from fedcourtsai import corpus, fixture


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
