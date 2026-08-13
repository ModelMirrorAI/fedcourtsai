"""The process-version stamp and the frozen-headline partition.

A prediction/evaluation is stamped with the *process* that produced it — the
prompt template, the resolved registry config for the actor, and the harness
commit — so headline metrics can reflect only the frozen, blessed process and
exclude the July/August shakedown runs without deleting them. Same doctrine as
the salience version (:data:`fedcourtsai.pipeline.salience.SALIENCE_VERSION`): a process
change is a *new* version, never an in-place edit, so any past ranking always
replays against the process that produced it.

Hybrid identity. The partition key is a content ``digest`` of the actual process
inputs, so a silent prompt or config change is automatically a distinct version;
``label`` is human-readable sugar. ``pipeline_sha`` is provenance only and is
deliberately excluded from the digest — see :class:`fedcourtsai.schemas.ProcessVersion`.

The freeze is a deliberate, explicit event: one "freeze commit" fills
:data:`FROZEN_PROCESS_DIGESTS` and :data:`FROZEN_SINCE` together — the
digest(s) a maintainer reads off ``fedcourts process-digest --all``, and the
instant a run's harness stamp must be at or after to count. The cutover
procedure and its verification live in ``docs/process-version.md``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .pricing import DEFAULT_MODELS
from .registry import (
    load_evaluators,
    load_mcp_servers,
    load_predictors,
    resolve_mcp_servers,
)
from .schemas import EvaluatorConfig, PredictorConfig, ProcessVersion

# Human label the current process is stamped with. Bump on a deliberate,
# named process change; the digest moves on *any* input change regardless.
CURRENT_PROCESS_LABEL = "proc-v2"

# The blessed process digests — the frozen-headline set: the six proc-v2
# baselines (claude/codex/gemini, predictor and evaluator each), read off
# `fedcourts process-digest --all`; set together with FROZEN_SINCE below,
# which a test pins. proc-v2 supersedes proc-v1 with zero cells ever stamped
# under it. Keyed on the digest, never the label, so a process that
# drifted under an unchanged label is not silently blessed. The predictor
# digests are the enforced membership filter (`is_frozen`); the evaluator
# entries are the freeze *record* of the blessed grading process — an
# evaluation's digest is recorded but only its timing is enforced, via
# `graded_post_freeze`.
FROZEN_PROCESS_DIGESTS: frozenset[str] = frozenset(
    {
        # predictors: claude-baseline, codex-baseline, gemini-baseline
        "sha256:1b5c8a972f0200cec3e32df9a376b380752ad38cc5bba2681a009edecc234495",
        "sha256:1d06f0fe3729954516e51f1f4d543d87738e9b170152c874c90dddfec0ae9b81",
        "sha256:80e343afbb36cee1512f5ffd90bf7aa353dfe1e19ca240eb005eb2f2f8a847fe",
        # evaluators: claude-judge, codex-judge, gemini-judge
        "sha256:297591be0d03b53be21c792f5f0a0f82dc4059f8e8e4162cca7e279d47855e8f",
        "sha256:02ca278d94e72dc4757c910394df87dae9b30096dfe36a76fa89349dfd288cfb",
        "sha256:1c07fe95c68db7b9a042a3bb51a4352b30aab0d64a78f67094b1d5463339ae19",
    }
)

# The freeze instant, set in the same commit that fills the set above (a test
# pins the coupling). The digest is a pure content hash, so a cell stamped
# *before* the freeze with the very bytes about to be blessed would otherwise
# read as frozen retroactively — pre-registration means the commitment
# preceded the run, and only a time cutoff can say so. Compared against the
# stamp's `stamped_at`, which the harness writes; anything at or after the
# instant is in. The literal must be at or after the date of the promotion
# merge that carried this commit to `main` (verified against
# `promotion/<YYYY-MM-DD>` before the `prereg/` tag is minted) and before the
# first run intended to count — see the cutover procedure in
# `docs/process-version.md`.
FROZEN_SINCE: datetime | None = datetime(2026, 8, 16, 0, 0, 0, tzinfo=UTC)

# The retrieval surface each engine's cells run with. Folded into the digest
# because it is a process input as much as the model or the prompt: a cell that
# can reach the open web is answering from a different information set than one
# that cannot, and without this a capability change would ride silently under
# the digest that blessed the runs made before it.
#
# The engines are configured in `CodexRunner.build_command` and the engine steps
# of run-predict / run-evaluate. Indexed rather than `.get`, so a new engine
# fails loudly here instead of defaulting to a surface nobody declared; the
# codex row is pinned to the runner's own argv by a test in `test_runner.py`.
ENGINE_RETRIEVAL: dict[str, tuple[str, ...]] = {
    "claude-code": ("web",),
    # Codex additionally needs the subprocess-network grant to reach the
    # localhost corpus service the other two engines reach unsandboxed.
    "codex": ("subprocess-network", "web"),
    "gemini": ("web",),
}


def compute_process_digest(prompt_bytes: bytes, config_canonical: dict[str, object]) -> str:
    """The reproducible content digest of one actor's process inputs.

    ``prompt_bytes`` is the prompt-template file verbatim (no normalization, so a
    whitespace-only edit is a legitimately new version). ``config_canonical`` is
    the resolved registry subset — see :func:`_predictor_config_canonical`. The
    two are joined by a NUL so no prompt/config boundary can be forged by content
    alone. Pure and deterministic: the same working tree always yields the same
    digest, which is what lets a maintainer compute a digest to bless.
    """
    canonical = json.dumps(config_canonical, sort_keys=True, separators=(",", ":")).encode()
    body = prompt_bytes + b"\x00" + canonical
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _resolved_model(engine: str, model: str | None) -> str:
    """The model that actually ran: the registry override, else the engine default.

    Hash the resolved value, not the raw ``model`` field — a null that falls back
    to ``DEFAULT_MODELS`` must move the digest when that default is bumped, or a
    model change would silently ride under the same process version.
    """
    return model or DEFAULT_MODELS[engine]


def _config_canonical(
    registry_path: Path, actor: PredictorConfig | EvaluatorConfig
) -> dict[str, object]:
    """The resolved registry subset that defines an actor's process.

    Predictor and evaluator entries share the same shape, so one helper serves
    both. Resolves the model (registry override, else engine default), the
    engine's retrieval surface, and the pinned MCP manifest *entries* (not just
    the ids a pin bump would leave unchanged), so any of them moving is a new
    process.
    """
    servers = resolve_mcp_servers(load_mcp_servers(registry_path), actor.mcp_servers)
    return {
        "engine": actor.engine,
        "model": _resolved_model(actor.engine, actor.model),
        "prompt_path": actor.prompt,
        "retrieval": list(ENGINE_RETRIEVAL[actor.engine]),
        # Exclude `description` — a manifest comment is documentation, not a
        # process input. Folding it in would bump every actor's version on a
        # cosmetic edit, and the actor-level description is already excluded
        # (only engine/model/prompt/mcp are hashed), so this keeps the two
        # consistent.
        "mcp_servers": [s.model_dump(mode="json", exclude={"description"}) for s in servers],
    }


def digest_for_actor(repo_root: Path, config_root: Path, role: str, actor_id: str) -> str:
    """Resolve one actor's process digest from the working tree.

    ``role`` is ``"predictor"`` or ``"evaluator"``. Loads the registry entry,
    reads its prompt-template bytes (``repo_root``-relative), and hashes both.
    Raises ``KeyError`` if the actor is not a registry id and ``OSError`` if its
    prompt file is missing — a genuine config inconsistency must fail loudly,
    never ship a cell with a fabricated-looking process version.
    """
    if role == "predictor":
        registry_path = config_root / "predictors.yaml"
        entry: PredictorConfig | EvaluatorConfig = _find(
            load_predictors(registry_path), actor_id, role
        )
    elif role == "evaluator":
        registry_path = config_root / "evaluators.yaml"
        entry = _find(load_evaluators(registry_path), actor_id, role)
    else:
        raise ValueError(f"role must be predictor or evaluator, not {role!r}")
    prompt_bytes = (repo_root / entry.prompt).read_bytes()
    return compute_process_digest(prompt_bytes, _config_canonical(registry_path, entry))


def _find(
    entries: list[PredictorConfig] | list[EvaluatorConfig], actor_id: str, role: str
) -> PredictorConfig | EvaluatorConfig:
    for entry in entries:
        if entry.id == actor_id:
            return entry
    raise KeyError(f"{role} {actor_id!r} is not in the registry")


def at_or_after_freeze(moment: datetime) -> bool:
    """Whether a moment is at or after :data:`FROZEN_SINCE` (trivially true unfrozen).

    A naive moment has no defined order against the timezone-aware freeze
    instant, so it reads as **before** the freeze by rule — excluded, never a
    comparison error taking down every scoreboard at once.
    """
    if FROZEN_SINCE is None:
        return True
    if moment.tzinfo is None:
        return False
    return moment >= FROZEN_SINCE


def graded_post_freeze(process_version: ProcessVersion | None) -> bool:
    """Whether an evaluation's own harness stamp is at or after the freeze.

    The time half only: the evaluator's digest is recorded but deliberately
    not enforced (the competitor being ranked is the predictor). Keyed on the
    evaluation's **harness-written** stamp, never its agent-written
    ``created_at`` — the pre-registration boundary must not rest on a clock
    the agent controls. While unfrozen this is a no-op; after the freeze an
    unstamped evaluation is out of frozen scope, the same doctrine as an
    unstamped prediction (local runs are unstamped and stay diagnostic).
    """
    if FROZEN_SINCE is None:
        return True
    return process_version is not None and at_or_after_freeze(process_version.stamped_at)


def is_frozen(process_version: ProcessVersion | None) -> bool:
    """Whether a cell's stamp is in the blessed frozen set, run post-freeze.

    An unstamped cell (``None``) is never frozen — its digest cannot be in the
    set — so the shakedown ledger is excluded from the headline for free. A
    stamped cell's ``stamped_at`` must also be at or after
    :data:`FROZEN_SINCE`: the digest says *which* process ran, never *when*,
    and a shakedown run of the very bytes later blessed is still a shakedown
    run.
    """
    if process_version is None or process_version.digest not in FROZEN_PROCESS_DIGESTS:
        return False
    return at_or_after_freeze(process_version.stamped_at)
