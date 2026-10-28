"""The committed frozen-process registry and the freeze constants built from it.

The golden values below pin the constants as they stood when they moved into
the registry, copied verbatim, and a commit on `staging` extends them with
what a promotion stamped once that stamp has synced back; the registry must
keep reproducing them exactly, types, order and clock included. The harness
boundaries are pinned as a prefix: the promotion record stamps a pending
boundary into the registry on `main` in a commit that may touch nothing else,
so a stamped row can follow the golden ones until that extension, and must
never move one of them.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Any, get_args

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
    bless_moments,
    counting_instant,
    load_process_registry,
    registered_windows,
)
from fedcourtsai.schemas import CountingWindow, ProcessRegistry, RegistryBoundaryReach

_SRC = Path(process_version.__file__)
_REGISTRY_FILE = _SRC.with_name("process_registry.json")

_V8 = datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC)
_V9_MERGE = datetime(2026, 10, 11, 0, 12, 2, tzinfo=UTC)
_V9_SINCE = datetime(2026, 10, 11, 12, 0, 0, tzinfo=UTC)
_V10 = datetime(2026, 10, 20, 15, 24, 42, tzinfo=UTC)
_V11 = datetime(2026, 10, 23, 2, 37, 11, tzinfo=UTC)
_V12 = datetime(2026, 10, 25, 13, 40, 46, tzinfo=UTC)
_V13 = datetime(2026, 10, 26, 19, 0, 50, tzinfo=UTC)
_CODEX_AND_GEMINI = frozenset({"codex-baseline", "gemini-baseline"})

# proc-v14 replaces all six blessings with its own pending six, which bless
# nothing until the carrying merge stamps them, so the carried map is empty.
GOLDEN_DIGESTS: dict[str, datetime] = {}

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
        closes=_V10,
    ),
    CountingWindow(
        label="proc-v8",
        digest="sha256:a9033e56819e775e561b802dec24bae437c17c751e5a7f5fa4b3eeb31383951f",
        predictor_id="gemini-baseline",
        opens=_V8,
        closes=_V10,
    ),
    CountingWindow(
        label="proc-v9",
        digest="sha256:605201bd8358473bcb8e7d59ee2d236d7be099756241333eec0f386b3400b734",
        predictor_id="claude-baseline",
        opens=_V9_SINCE,
        closes=_V11,
    ),
    CountingWindow(
        label="proc-v10",
        digest="sha256:7ab92dd4fb4d5e0889c4269bb2921676ad3917b6f86f71c8b26d3ac34a6574a4",
        predictor_id="codex-baseline",
        opens=_V10,
        closes=_V11,
    ),
    CountingWindow(
        label="proc-v10",
        digest="sha256:bee46e92d923594056bdb6c9770521ef5251b0d065c5957262d7f5a55dd7b434",
        predictor_id="gemini-baseline",
        opens=_V10,
        closes=_V11,
    ),
    CountingWindow(
        label="proc-v11",
        digest="sha256:d1487fc0280716c03c4f119b557b1579b0bb65df0fa4efa158a88ae02a6e5e54",
        predictor_id="claude-baseline",
        opens=_V11,
        closes=_V12,
    ),
    CountingWindow(
        label="proc-v11",
        digest="sha256:a711152d3e0082a9f5311e40348116c753247aba102ddc60e5979c7d292abe64",
        predictor_id="codex-baseline",
        opens=_V11,
        closes=_V12,
    ),
    CountingWindow(
        label="proc-v11",
        digest="sha256:c4213d78e7a7a6fc5f13d070a3bda326254c0189b7979f5e7b91a23d5608ad66",
        predictor_id="gemini-baseline",
        opens=_V11,
        closes=_V12,
    ),
    CountingWindow(
        label="proc-v12",
        digest="sha256:457d3e0e44be5ed4d2a5da50b0078129a08c0cd4d35108569ee058c53759513f",
        predictor_id="claude-baseline",
        opens=_V12,
        closes=_V13,
    ),
    CountingWindow(
        label="proc-v12",
        digest="sha256:87e57da6f663878435c82b1f527cb13eea1017130fcdb13b134e759583db60f4",
        predictor_id="codex-baseline",
        opens=_V12,
        closes=_V13,
    ),
    CountingWindow(
        label="proc-v12",
        digest="sha256:8057aacc92139d6caed4284137fd96ec5c008ddd60fa0c75a0752793369e07c9",
        predictor_id="gemini-baseline",
        opens=_V12,
        closes=_V13,
    ),
    CountingWindow(
        label="proc-v13",
        digest="sha256:6a176c287cf54ff3c7de82a67dbbf153048d395193187e205f3c702afbdec40d",
        predictor_id="claude-baseline",
        opens=_V13,
    ),
    CountingWindow(
        label="proc-v13",
        digest="sha256:2827480e4427976147d8ad3250fc8ca8c9495e0a5808fe47a872abc6d649d354",
        predictor_id="codex-baseline",
        opens=_V13,
    ),
    CountingWindow(
        label="proc-v13",
        digest="sha256:b69b2b3af71da1fd0e4e736ddb5424dd331c8787bfdbe0f6d354cb7b12fa2745",
        predictor_id="gemini-baseline",
        opens=_V13,
    ),
)

GOLDEN_BLESSING_LABELS = {
    "sha256:fbc0e9c364d846c5701fed0d34727d4ea7c0f002ee9337fe98f791fbb0479d13": ("proc-v8",),
    "sha256:9670e1c147a723e68534d88ec494cb2c7b7463dcf18dbadecadf3108f08383b1": ("proc-v8",),
    "sha256:dbdc90647bc81eec9b4de523188f1e46c5dcb64b5717a30da16b8886e4a6d4fe": ("proc-v8",),
    "sha256:167b7d71693168778880bf001df7e3a46c6d61d57061d8e66ecf6801d88ebd12": (
        "proc-v9",
        "proc-v10",
        "proc-v11",
        "proc-v12",
        "proc-v13",
    ),
    "sha256:18a76b9301aef6770b5c5f9965dd6fcabb2a929964a56be2151405ce878e0456": ("proc-v9",),
    "sha256:225580440df0f97970177cf3b0e8e5175d0c2fa66da329dacb7f80a875718300": ("proc-v9",),
    "sha256:a8610eecc95ddfab4763c4b2056b85e833dbe35bc9d90341fc3c90ee907261ac": (
        "proc-v10",
        "proc-v11",
        "proc-v12",
        "proc-v13",
    ),
    "sha256:6a88d3dcf20acc9908a7ca956cd62ad956d273ad8a3cf2a747beafe3955873a4": (
        "proc-v10",
        "proc-v11",
        "proc-v12",
        "proc-v13",
    ),
    "sha256:d49940aa59545ae61ff1c7616dd728f88b92876dd07685360b026942d9e689ad": ("proc-v14",),
    "sha256:63369e6cd3c723179ec731eaf64d7c72ea6f94b019ed903b42ef802fdbec09b1": ("proc-v14",),
    "sha256:c81e77e1c3f1c46a310a1914a457fb5fc35b57c54a52e2135ef90ac3569d4714": ("proc-v14",),
}

_SCRUB_0921 = "a2f84f2eedb4e3b3dcc222522a55b8a93ae1eff0"
_PROMOTION_0929 = "adccd9c427be6e1dd4b43d92b2472d7d21fd8d24"
_PROMOTION_1001 = "b09c2d0bbe9a3f0fb8c38ac8b077e1d29d73020b"
_PROMOTION_1003 = "41d003e28da4232d772031bf142a773afea52ff5"
_PROMOTION_1010 = "6460e93061a0f4d6a06c14b5b1526346aba7a353"
_PROMOTION_1011_2 = "c432a95a9073bcae6651eb6b75fddd30aefbd8d8"
_PROMOTION_1016 = "1c1cd1f257e1bcbcd4f5339173fff2dab68ed317"
_PROMOTION_1018 = "dbb042ca4bd6b6d6f4fcb1f02e0d175ac76d0f2c"
_PROMOTION_1020 = "7d4f2c6c58e01b22f17adb850b5203418f71925e"
_PROMOTION_1022 = "76323ef6e884a97d42fbd41aac078312d7b4e167"
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
    HarnessBoundary(
        "scrub-withheld-petitioner-block",
        _PROMOTION_1016,
        datetime(2026, 10, 16, 20, 17, 17, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "single-entry-trigger-placement",
        _PROMOTION_1016,
        datetime(2026, 10, 16, 20, 17, 17, tzinfo=UTC),
        None,
        "all",
    ),
    HarnessBoundary(
        "query-clock-prior-last-pull-mask",
        _PROMOTION_1016,
        datetime(2026, 10, 16, 20, 17, 17, tzinfo=UTC),
        None,
        "all",
    ),
    HarnessBoundary(
        "scrub-scanned-caption-residuals",
        _PROMOTION_1018,
        datetime(2026, 10, 18, 1, 6, 13, tzinfo=UTC),
        None,
        _SR,
    ),
    HarnessBoundary(
        "interim-pool-one-row-per-number",
        _PROMOTION_1018,
        datetime(2026, 10, 18, 1, 6, 13, tzinfo=UTC),
        None,
        "all",
        gradual=True,
    ),
    HarnessBoundary("scrub-ohio-reporter-citation", _PROMOTION_1020, _V10, None, _SR),
    HarnessBoundary(
        "merits-judgment-parser-summary-ruling-consolidated",
        _PROMOTION_1020,
        _V10,
        None,
        "granted dockets",
        gradual=True,
    ),
    HarnessBoundary(
        "cert-exit-guard-and-plural-nouns", _PROMOTION_1020, _V10, None, "all", gradual=True
    ),
    HarnessBoundary(
        "direct-appeal-plenary-review-grant", _PROMOTION_1020, _V10, None, "all", gradual=True
    ),
    HarnessBoundary(
        "merits-brief-confession-of-error",
        _PROMOTION_1022,
        datetime(2026, 10, 22, 22, 40, 22, tzinfo=UTC),
        None,
        "granted dockets",
        gradual=True,
    ),
    HarnessBoundary(
        "vide-related-dockets",
        _PROMOTION_1022,
        datetime(2026, 10, 22, 22, 40, 22, tzinfo=UTC),
        None,
        "all",
    ),
)


#: The merges the golden values above were stamped by. A label's instants are
#: stamped on `main` by its carrying merge, in a commit that may touch nothing
#: but the registry and the freeze record, so until a `staging` commit extends
#: the goldens the constants are compared as they read with every instant a
#: later merge stamped put back to pending: each known row still compares
#: exactly, and only rows a carrying merge has stamped since are let through.
_GOLDEN_MERGES = frozenset(
    {
        "545e26e2b753ac79701a4fd638689a8d48654bce",
        "6460e93061a0f4d6a06c14b5b1526346aba7a353",
        "7d4f2c6c58e01b22f17adb850b5203418f71925e",
        "fd98eda9327806f1a0eed032377e05e480c6c33e",
        "51cca3cb5eab4d7fa8ab3701f1dbae103d1a00c0",
        "728efab06a9ad44bf39523c7181827d4eade70de",
    }
)


def _unstamped(node: Any) -> Any:
    if isinstance(node, dict):
        if set(node) == {"at", "merge", "source"} and node["merge"] not in _GOLDEN_MERGES:
            return {"at": None, "merge": None, "source": "merge"}
        return {key: _unstamped(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_unstamped(value) for value in node]
    return node


def _as_the_goldens_know_it() -> ProcessRegistry:
    raw = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    rows = {key: _unstamped(raw[key]) for key in ("labels", "blessings", "windows")}
    return load_process_registry(
        json.dumps({**raw, **rows}), current_label=process_version.CURRENT_PROCESS_LABEL
    )


def test_the_bless_map_reproduces_its_golden_values_in_order() -> None:
    assert isinstance(FROZEN_PROCESS_DIGESTS, MappingProxyType)
    known = bless_moments(_as_the_goldens_know_it())
    assert list(known.items()) == list(GOLDEN_DIGESTS.items())
    assert all(
        FROZEN_PROCESS_DIGESTS[digest] == moment for digest, moment in GOLDEN_DIGESTS.items()
    )
    assert all(moment.tzinfo is UTC for moment in FROZEN_PROCESS_DIGESTS.values())


def test_the_counting_instant_reproduces_its_golden_value() -> None:
    assert counting_instant(_as_the_goldens_know_it()) == _V13
    assert FROZEN_SINCE is not None and FROZEN_SINCE.tzinfo is UTC
    assert FROZEN_SINCE >= _V13


def test_the_counting_windows_reproduce_their_golden_values_in_order() -> None:
    assert isinstance(COUNTING_WINDOWS, tuple)
    known = registered_windows(_as_the_goldens_know_it())
    assert known == GOLDEN_WINDOWS
    assert repr(known) == repr(GOLDEN_WINDOWS)


def test_the_blessing_labels_reproduce_their_golden_values_in_order() -> None:
    assert isinstance(EVALUATE_BLESSING_LABELS, MappingProxyType)
    assert list(EVALUATE_BLESSING_LABELS.items()) == list(GOLDEN_BLESSING_LABELS.items())


def test_the_harness_boundaries_reproduce_their_golden_values_in_order() -> None:
    assert isinstance(HARNESS_BOUNDARIES, tuple)
    pinned = HARNESS_BOUNDARIES[: len(GOLDEN_BOUNDARIES)]
    assert pinned == GOLDEN_BOUNDARIES
    assert repr(pinned) == repr(GOLDEN_BOUNDARIES)


def test_the_committed_registry_round_trips_through_its_model() -> None:
    raw = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    registry = ProcessRegistry.model_validate(raw)
    assert json.loads(registry.model_dump_json()) == json.loads(
        ProcessRegistry.model_validate_json(registry.model_dump_json()).model_dump_json()
    )
    assert registry == load_process_registry()


def test_the_boundary_reach_vocabulary_is_one_vocabulary() -> None:
    assert get_args(BoundaryReach.__value__) == get_args(RegistryBoundaryReach)


def test_a_half_pending_instant_is_refused() -> None:
    """An instant is pending only with both `at` and `merge` null; one alone is refused."""
    raw = _raw()
    raw["labels"][-1]["since"]["merge"] = None
    with pytest.raises(ValueError, match="together, or neither"):
        load_process_registry(json.dumps(raw))


def test_a_carried_label_cannot_go_back_to_pending() -> None:
    """Only the label a PR registers may be pending; a carried one keeps its stamp."""
    raw = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    raw["labels"][0]["since"] = {"at": None, "merge": None, "source": "merge"}
    with pytest.raises(ValueError, match="may be pending"):
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


def _stamped(node: Any, at: str) -> Any:
    """``node`` with every pending instant stamped ``at``, as a carrying merge would."""
    if isinstance(node, dict):
        if node.get("at", "") is None and node.get("merge", "") is None:
            return {**node, "at": at, "merge": "f" * 40}
        return {key: _stamped(value, at) for key, value in node.items()}
    if isinstance(node, list):
        return [_stamped(value, at) for value in node]
    return node


def _raw() -> dict[str, Any]:
    """The committed registry with any pending rows stamped, so a mutation is its only fault."""
    loaded: dict[str, Any] = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
    carried = max(entry["since"]["at"] for entry in loaded["labels"] if entry["since"]["at"])
    after = datetime.fromisoformat(carried) + timedelta(hours=1)
    stamped: dict[str, Any] = _stamped(loaded, after.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return stamped


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda r: r["labels"].pop(), f"no label row for {process_version.CURRENT_PROCESS_LABEL}"),
        (lambda r: r["labels"].append(r["labels"][0]), "a label has two rows"),
        (lambda r: r["blessings"].append(r["blessings"][0]), "a digest is blessed twice"),
        (lambda r: r["blessings"][0].update(label="proc-v7"), "proc-v7 has no label row"),
        (lambda r: r["windows"][1].update(label="proc-v7"), "proc-v7 has no label row"),
        (
            lambda r: r["windows"][1]["opens"].update(at="2026-09-17T00:00:00Z"),
            "does not open at its label's counting instant",
        ),
        (
            lambda r: r["windows"][0]["closes"].update(at="2026-10-12T00:00:00Z"),
            "closes off every label's counting instant",
        ),
    ],
    ids=[
        "no-current-label",
        "duplicate-label",
        "duplicate-blessing",
        "blessing-unknown-label",
        "window-unknown-label",
        "window-off-its-since",
        "close-off-every-since",
    ],
)
def test_an_inconsistent_registry_is_refused(mutate: Any, match: str) -> None:
    raw = _raw()
    mutate(raw)
    with pytest.raises(ValueError, match=match):
        load_process_registry(json.dumps(raw))


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda r: r["windows"][0].update(revoked_at="2026-10-12T00:00:00"), "revocation is UTC"),
        (
            lambda r: r["windows"][0].update(revoked_at="2026-10-12T00:00:00-04:00"),
            "revocation is UTC",
        ),
        (lambda r: r["harness_boundaries"][0].update(at="2026-09-21T18:01:19"), "boundary time"),
        (
            lambda r: r["harness_boundaries"][0].update(at="2026-09-21T14:01:19-04:00"),
            "boundary time",
        ),
    ],
    ids=["naive-revocation", "offset-revocation", "naive-boundary", "offset-boundary"],
)
def test_a_registry_datetime_off_utc_is_refused(mutate: Any, match: str) -> None:
    raw = _raw()
    mutate(raw)
    with pytest.raises(ValueError, match=match):
        load_process_registry(json.dumps(raw))


def _committed_at(sha: str) -> datetime:
    """``sha``'s committer time from this checkout's history, or skip where it is absent."""
    repo = _SRC.parents[2]
    shallow = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--is-shallow-repository"],
        capture_output=True,
        text=True,
        check=False,
    )
    if shallow.returncode != 0:
        pytest.skip("not a git checkout, so no merge's committer time is readable")
    if shallow.stdout.strip() == "true":
        pytest.skip("a shallow checkout lacks the merges the registry is audited against")
    found = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%cI", sha],
        capture_output=True,
        text=True,
        check=False,
    )
    if found.returncode != 0 or not found.stdout.strip():
        pytest.skip(f"{sha} is not in this checkout's history")
    return datetime.fromisoformat(found.stdout.strip())


def _registered_instants() -> list[tuple[str, Any]]:
    registry = load_process_registry()
    instants: list[tuple[str, Any]] = [(f"since {e.label}", e.since) for e in registry.labels]
    instants += [(f"blessed {b.actor_id}", b.blessed) for b in registry.blessings]
    for w in registry.windows:
        instants.append((f"opens {w.label} {w.predictor_id}", w.opens))
        if w.closes is not None:
            instants.append((f"closes {w.label} {w.predictor_id}", w.closes))
    return instants


@pytest.mark.parametrize(
    "instant", [i for _, i in _registered_instants()], ids=[n for n, _ in _registered_instants()]
)
def test_every_instant_is_audited_against_its_merge(instant: Any) -> None:
    """A ``merge`` instant is its merge's committer time; a ``hand`` one is at or after it."""
    if instant.pending:
        pytest.skip("pending: no merge has carried it yet, so there is nothing to audit")
    committed = _committed_at(instant.merge)
    if instant.source == "merge":
        assert instant.at == committed
    else:
        assert instant.at >= committed


@pytest.mark.parametrize("boundary", GOLDEN_BOUNDARIES, ids=[b.name for b in GOLDEN_BOUNDARIES])
def test_every_boundary_time_is_its_merge_s_committer_time(boundary: HarnessBoundary) -> None:
    assert boundary.at == _committed_at(boundary.merge)
