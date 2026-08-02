"""The process-version digest and the frozen-headline partition.

A cell is stamped with a content digest of the process that produced it (the
prompt template, the resolved registry config, and the engine's retrieval
surface), so headline metrics can reflect only
the frozen, blessed process. These lock the two properties the stamp rests on:
the digest is *reproducible* (a maintainer can compute a digest to bless) and
*sensitive* (any real process change moves it), and `is_frozen` gates on the
digest, never the label.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from fedcourtsai import process_version
from fedcourtsai.process_version import _config_canonical
from fedcourtsai.registry import load_predictors
from fedcourtsai.schemas import ProcessVersion

CONFIG = Path("config")
REPO = Path(".")


def test_the_digest_is_reproducible() -> None:
    a = process_version.compute_process_digest(b"prompt", {"engine": "claude-code", "model": "m"})
    b = process_version.compute_process_digest(b"prompt", {"engine": "claude-code", "model": "m"})
    assert a == b
    assert a.startswith("sha256:")


def test_the_digest_moves_on_any_real_process_change() -> None:
    base = process_version.compute_process_digest(
        b"prompt", {"engine": "claude-code", "model": "m"}
    )
    # A whitespace-only prompt edit is a legitimately new version.
    assert base != process_version.compute_process_digest(
        b"prompt ", {"engine": "claude-code", "model": "m"}
    )
    # A model change is a new version.
    assert base != process_version.compute_process_digest(
        b"prompt", {"engine": "claude-code", "model": "m2"}
    )


def test_a_cosmetic_mcp_description_edit_does_not_bump_the_version() -> None:
    """A manifest comment is documentation, not a process input — editing it
    must not re-version every actor. The resolved config the digest hashes
    excludes the MCP `description`, consistent with the actor-level one."""
    entry = next(p for p in load_predictors(CONFIG / "predictors.yaml") if p.mcp_servers)
    canonical = _config_canonical(CONFIG / "predictors.yaml", entry)
    servers = canonical["mcp_servers"]
    assert isinstance(servers, list) and servers, "the fixture predictor pins a server"
    assert all("description" not in server for server in servers)


def test_the_prompt_config_boundary_cannot_be_forged() -> None:
    """The NUL join means shifting a byte across the prompt/config boundary is a
    different digest, so two distinct processes can't collide by concatenation."""
    assert process_version.compute_process_digest(
        b"ab", {"x": "c"}
    ) != process_version.compute_process_digest(b"a", {"x": "bc"})


def test_digest_for_actor_resolves_from_the_real_registry() -> None:
    """Each enabled actor has a resolvable, distinct digest — the value
    `process-digest --all` prints for a maintainer to bless."""
    digests = {
        actor: process_version.digest_for_actor(REPO, CONFIG, "predictor", actor)
        for actor in ("claude-baseline", "codex-baseline", "gemini-baseline")
    }
    # Same prompt, different engine/model -> genuinely different processes.
    assert len(set(digests.values())) == 3
    assert all(d.startswith("sha256:") for d in digests.values())


def test_the_retrieval_surface_is_hashed_into_the_digest() -> None:
    """Dropping the retrieval surface from the canonical config would leave a
    capability change riding under the identity that blessed the earlier runs."""
    entry = next(p for p in load_predictors(CONFIG / "predictors.yaml") if p.engine == "codex")
    canonical = _config_canonical(CONFIG / "predictors.yaml", entry)
    assert canonical["retrieval"] == list(process_version.ENGINE_RETRIEVAL[entry.engine])


def test_a_capability_change_moves_the_digest(monkeypatch: pytest.MonkeyPatch) -> None:
    """The point of hashing the surface: revoke codex's web reach and the
    digest must move, so its cells cannot be pooled with web-enabled ones."""
    before = process_version.digest_for_actor(REPO, CONFIG, "predictor", "codex-baseline")
    monkeypatch.setitem(process_version.ENGINE_RETRIEVAL, "codex", ("subprocess-network",))
    after = process_version.digest_for_actor(REPO, CONFIG, "predictor", "codex-baseline")
    assert before != after


def test_the_live_codex_cells_declare_the_surface_they_run_with() -> None:
    """The tournament's cells are configured by the workflows, not the runner
    seam, so the declared surface is pinned to the args those steps pass."""
    workflows = Path(".github") / "workflows"
    declared = process_version.ENGINE_RETRIEVAL["codex"]
    for name in ("run-predict.yml", "run-evaluate.yml"):
        text = (workflows / name).read_text()
        assert ("web" in declared) == ("web_search=live" in text), name
        assert ("subprocess-network" in declared) == (
            "sandbox_workspace_write.network_access=true" in text
        ), name


def test_an_unknown_actor_fails_loudly() -> None:
    """A registry typo must not resolve to a fabricated-looking digest."""
    with pytest.raises(KeyError):
        process_version.digest_for_actor(REPO, CONFIG, "predictor", "no-such-predictor")


def _pv(digest: str) -> ProcessVersion:
    return ProcessVersion(
        label="proc-v1", digest=digest, stamped_at=datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_is_frozen_gates_on_the_digest_not_the_label(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(process_version, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    assert process_version.is_frozen(_pv("sha256:blessed"))
    # Same label, unblessed digest — a process that drifted under an unchanged
    # label must NOT read as frozen.
    assert not process_version.is_frozen(_pv("sha256:drifted"))
    # An unstamped shakedown cell is never frozen.
    assert not process_version.is_frozen(None)


def test_the_frozen_set_is_empty_until_the_freeze_commit() -> None:
    """The shakedown state: nothing is blessed yet, so nothing is frozen."""
    assert frozenset() == process_version.FROZEN_PROCESS_DIGESTS
    assert not process_version.is_frozen(_pv("sha256:anything"))
