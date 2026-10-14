"""The committed frozen-process registry and the freeze constants built from it.

The golden values below are the constants as the module held them before the
registry existed, copied verbatim; the registry must keep reproducing them
exactly, types, order and clock included.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import get_args

import pytest

from fedcourtsai import process_version
from fedcourtsai.process_version import (
    COUNTING_WINDOWS,
    EVALUATE_BLESSING_LABELS,
    FROZEN_PROCESS_DIGESTS,
    FROZEN_SINCE,
    HARNESS_BOUNDARIES,
    BoundaryReach,
    HarnessBoundary,
    load_process_registry,
)
from fedcourtsai.schemas import CountingWindow, ProcessRegistry, RegistryBoundaryReach

_SRC = Path(process_version.__file__)
_REGISTRY_FILE = _SRC.with_name("process_registry.json")

_V8 = datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC)
_V9_MERGE = datetime(2026, 10, 11, 0, 12, 2, tzinfo=UTC)
_V9_SINCE = datetime(2026, 10, 11, 12, 0, 0, tzinfo=UTC)
_CODEX_AND_GEMINI = frozenset({"codex-baseline", "gemini-baseline"})

GOLDEN_DIGESTS = {
    "sha256:605201bd8358473bcb8e7d59ee2d236d7be099756241333eec0f386b3400b734": _V9_MERGE,
    "sha256:70fee158526caa6870d43ace70c3781db39f644379c86c363538ebdefa57547c": _V8,
    "sha256:a9033e56819e775e561b802dec24bae437c17c751e5a7f5fa4b3eeb31383951f": _V8,
    "sha256:167b7d71693168778880bf001df7e3a46c6d61d57061d8e66ecf6801d88ebd12": _V9_MERGE,
    "sha256:18a76b9301aef6770b5c5f9965dd6fcabb2a929964a56be2151405ce878e0456": _V9_MERGE,
    "sha256:225580440df0f97970177cf3b0e8e5175d0c2fa66da329dacb7f80a875718300": _V9_MERGE,
}

GOLDEN_WINDOWS = (
    CountingWindow(
        label="proc-v8",
        digest="sha256:1a0b2bef2e367cd589e4800fa04de5b5110b41bf1ea159b3c51669ccc722e89a",
        predictor_id="claude-baseline",
        opens=_V8,
        closes=_V9_SINCE,
    ),
    CountingWindow(
        label="proc-v8",
        digest="sha256:70fee158526caa6870d43ace70c3781db39f644379c86c363538ebdefa57547c",
        predictor_id="codex-baseline",
        opens=_V8,
    ),
    CountingWindow(
        label="proc-v8",
        digest="sha256:a9033e56819e775e561b802dec24bae437c17c751e5a7f5fa4b3eeb31383951f",
        predictor_id="gemini-baseline",
        opens=_V8,
    ),
    CountingWindow(
        label="proc-v9",
        digest="sha256:605201bd8358473bcb8e7d59ee2d236d7be099756241333eec0f386b3400b734",
        predictor_id="claude-baseline",
        opens=_V9_SINCE,
    ),
)

GOLDEN_BLESSING_LABELS = {
    "sha256:fbc0e9c364d846c5701fed0d34727d4ea7c0f002ee9337fe98f791fbb0479d13": ("proc-v8",),
    "sha256:9670e1c147a723e68534d88ec494cb2c7b7463dcf18dbadecadf3108f08383b1": ("proc-v8",),
    "sha256:dbdc90647bc81eec9b4de523188f1e46c5dcb64b5717a30da16b8886e4a6d4fe": ("proc-v8",),
    "sha256:167b7d71693168778880bf001df7e3a46c6d61d57061d8e66ecf6801d88ebd12": ("proc-v9",),
    "sha256:18a76b9301aef6770b5c5f9965dd6fcabb2a929964a56be2151405ce878e0456": ("proc-v9",),
    "sha256:225580440df0f97970177cf3b0e8e5175d0c2fa66da329dacb7f80a875718300": ("proc-v9",),
}

_SCRUB_0921 = "a2f84f2eedb4e3b3dcc222522a55b8a93ae1eff0"
_PROMOTION_0929 = "adccd9c427be6e1dd4b43d92b2472d7d21fd8d24"
_PROMOTION_1001 = "b09c2d0bbe9a3f0fb8c38ac8b077e1d29d73020b"
_PROMOTION_1003 = "41d003e28da4232d772031bf142a773afea52ff5"
_PROMOTION_1010 = "6460e93061a0f4d6a06c14b5b1526346aba7a353"
_PROMOTION_1011_2 = "c432a95a9073bcae6651eb6b75fddd30aefbd8d8"
_SR: BoundaryReach = "self-represented dockets"

GOLDEN_BOUNDARIES = (
    HarnessBoundary(
        "pro-se-document-scrub",
        _SCRUB_0921,
        datetime(2026, 9, 21, 18, 1, 19, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "scrub-ocr-and-served-values",
        _PROMOTION_0929,
        datetime(2026, 9, 29, 23, 30, 38, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "pro-se-snapshot-scrub",
        _PROMOTION_0929,
        datetime(2026, 9, 29, 23, 30, 38, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "scrub-pro-se-respondent",
        _PROMOTION_1001,
        datetime(2026, 10, 1, 16, 15, 45, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "scrub-pro-se-amicus",
        _PROMOTION_1001,
        datetime(2026, 10, 1, 16, 15, 45, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "scrub-in-re-self-filer",
        _PROMOTION_1003,
        datetime(2026, 10, 3, 19, 8, 49, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "scrub-titled-joinder-self-filer",
        _PROMOTION_1003,
        datetime(2026, 10, 3, 19, 8, 49, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "merits-brief-spellings-consolidated-lead",
        _PROMOTION_1003,
        datetime(2026, 10, 3, 19, 8, 49, tzinfo=UTC),
        None,
        "granted dockets",
        gradual=True,
    ),
    HarnessBoundary(
        "predict-cell-record-hide",
        _PROMOTION_1010,
        datetime(2026, 10, 11, 0, 12, 2, tzinfo=UTC),
        _CODEX_AND_GEMINI,
        "all",
    ),
    HarnessBoundary(
        "widened-document-kinds-freshness",
        _PROMOTION_1010,
        datetime(2026, 10, 11, 0, 12, 2, tzinfo=UTC),
        _CODEX_AND_GEMINI,
        "all",
        gradual=True,
    ),
    HarnessBoundary(
        "replay-moment-cut",
        _PROMOTION_1010,
        datetime(2026, 10, 11, 0, 12, 2, tzinfo=UTC),
        _CODEX_AND_GEMINI,
        "replay cells",
    ),
    HarnessBoundary(
        "merits-brief-partial-support",
        _PROMOTION_1011_2,
        datetime(2026, 10, 11, 23, 41, 22, tzinfo=UTC),
        None,
        "granted dockets",
        gradual=True,
    ),
)


def test_the_bless_map_reproduces_its_golden_values_in_order() -> None:
    assert isinstance(FROZEN_PROCESS_DIGESTS, MappingProxyType)
    assert list(FROZEN_PROCESS_DIGESTS.items()) == list(GOLDEN_DIGESTS.items())
    assert all(moment.tzinfo is UTC for moment in FROZEN_PROCESS_DIGESTS.values())


def test_the_counting_instant_reproduces_its_golden_value() -> None:
    assert FROZEN_SINCE == _V9_SINCE
    assert FROZEN_SINCE is not None and FROZEN_SINCE.tzinfo is UTC


def test_the_counting_windows_reproduce_their_golden_values_in_order() -> None:
    assert isinstance(COUNTING_WINDOWS, tuple)
    assert COUNTING_WINDOWS == GOLDEN_WINDOWS
    assert repr(COUNTING_WINDOWS) == repr(GOLDEN_WINDOWS)


def test_the_blessing_labels_reproduce_their_golden_values_in_order() -> None:
    assert isinstance(EVALUATE_BLESSING_LABELS, MappingProxyType)
    assert list(EVALUATE_BLESSING_LABELS.items()) == list(GOLDEN_BLESSING_LABELS.items())


def test_the_harness_boundaries_reproduce_their_golden_values_in_order() -> None:
    assert isinstance(HARNESS_BOUNDARIES, tuple)
    assert HARNESS_BOUNDARIES == GOLDEN_BOUNDARIES
    assert repr(HARNESS_BOUNDARIES) == repr(GOLDEN_BOUNDARIES)


def test_the_committed_registry_round_trips_through_its_model() -> None:
    raw = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    registry = ProcessRegistry.model_validate(raw)
    assert json.loads(registry.model_dump_json()) == json.loads(
        ProcessRegistry.model_validate_json(registry.model_dump_json()).model_dump_json()
    )
    assert registry == load_process_registry()


def test_the_boundary_reach_vocabulary_is_one_vocabulary() -> None:
    assert get_args(BoundaryReach.__value__) == get_args(RegistryBoundaryReach)


def test_a_registration_no_merge_carried_is_refused() -> None:
    raw = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    raw["labels"][-1]["since"]["merge"] = None
    with pytest.raises(ValueError, match="carries no merge"):
        load_process_registry(json.dumps(raw))


def test_a_registry_instant_off_utc_is_refused() -> None:
    raw = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    raw["labels"][-1]["since"]["at"] = "2026-10-11T08:00:00-04:00"
    with pytest.raises(ValueError, match="UTC"):
        load_process_registry(json.dumps(raw))


def test_the_registry_is_the_single_source_of_the_freeze_constants() -> None:
    """No freeze instant, digest or boundary SHA is spelled in the module itself."""
    source = _SRC.read_text(encoding="utf-8")
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    assert not re.search(r"datetime\(\s*20\d\d,", code), "a dated literal outside the registry"
    for digest in (*GOLDEN_DIGESTS, *GOLDEN_BLESSING_LABELS, *(w.digest for w in GOLDEN_WINDOWS)):
        assert digest not in code, digest
    for boundary in GOLDEN_BOUNDARIES:
        assert boundary.merge not in code, boundary.name
