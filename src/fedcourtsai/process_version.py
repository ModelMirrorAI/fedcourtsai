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
digest(s) a maintainer reads off ``fedcourts process-digest --all``, each
carrying the instant it was blessed, and the instant a run's harness stamp
must be at or after to count. Those are **two** boundaries doing two jobs,
and they are deliberately not the same moment:

- the **bless moment** — a digest's value in the map — is when that process's
  bytes became immutable on ``main``, so it is the *retroactivity* boundary. A
  cell stamped before it ran against a commitment that could still be edited,
  which is retroactive blessing and nothing licenses it. Auditable from git:
  it is the merge time of the promotion that carried the freeze commit.
- the **counting instant**, :data:`FROZEN_SINCE`, is when the headline starts
  counting. It is guessed generously late at the freeze commit, so cells
  minted in the window between the two boundaries land honestly in the ledger
  and are de-counted by timing — shakedown, not retroactivity.

A later evaluator-half re-bless revises the map's evaluator entries while
holding the instant; a predictor-half re-bless replaces the enforced entries
and puts the instant past the carrying promotion — by moving it, or by
leaving one that already sits there — de-counting every cell stamped under
the retired digests. Where that set holds a counted cell the move is licensed
only by a shakedown declaration dated before the de-counted claim window's
outcomes; where the prior instant has no cells yet, nothing counted moves and
the re-freeze is the plain supersession (the freeze record carries each). The
cutover procedure, its verification, and the supersession
notes live in ``docs/process-version.md``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType

from .pricing import DEFAULT_MODELS
from .registry import (
    load_evaluators,
    load_mcp_servers,
    load_predictors,
    resolve_mcp_servers,
)
from .schemas import EvaluatorConfig, FrozenProcessRecord, PredictorConfig, ProcessVersion

# Human label the current process is stamped with. Bump on a deliberate,
# named process change; the digest moves on *any* input change regardless.
CURRENT_PROCESS_LABEL = "proc-v6"

# The blessed process digests, each mapped to its bless moment — the
# frozen-headline set: the six proc-v6
# baselines (claude/codex/gemini, predictor and evaluator each), read off
# `fedcourts process-digest --all`; set together with FROZEN_SINCE below,
# which a test pins. proc-v6 is **fleet-wide**: all six digests move, because
# the two shared prompt templates' bytes move (the interim-arrival wording,
# the merits pool-guard wording, and the leakage bit's contract — the three
# amendment debts `docs/freeze-record.md` had standing) and, on the claude
# pair, the resolved model does too. The map holds one blessed process per
# actor, so every proc-v5 digest is replaced rather than kept beside these.
# Because the predictor digest is the enforced membership filter
# (`is_frozen`), retiring the predictor half **de-counts every prediction
# stamped under it** — the mechanism the third supersession shape in
# `docs/process-version.md` names, engaged here over an empty set. The label
# is the **first** shape, a re-freeze before the prior instant has any cells:
# nothing is stamped at or after the counting instant below, so nothing the
# retirement removes was ever counted and no declaration is called on. The
# freeze record carries the census and the condition it rests on. Keyed on the
# digest, never the label,
# so a process that drifted under an unchanged label is not silently blessed;
# the evaluator entries are the freeze *record* of the blessed grading
# process.
#
# Each digest maps to **the instant it was blessed**: the merge time of the
# promotion that carried its freeze commit to `main`, the moment its bytes
# stopped being editable. That is the retroactivity boundary the tripwire
# enforces (`at_or_after_bless`), and it is a different question from
# FROZEN_SINCE's — see this module's docstring. The value is read off git
# (`git log -1 --format=%cI <carrying merge>`) at step 4 of the cutover, so
# an auditor can re-derive every entry; a digest carried forward
# byte-identical from an earlier label keeps that label's bless moment,
# because those bytes have been immutable since then.
#
# These values are **auditable, not enforced**: nothing compares them against
# git at test time, only that each is aware and not in the future (which
# catches a forecast the cutover's step 4 never corrected). The witness is the
# dated entry in `docs/freeze-record.md`, which carries the merge and the
# command that yields it.
FROZEN_PROCESS_DIGESTS: Mapping[str, datetime] = MappingProxyType(
    {
        # Every entry below carries step 2's **forecast** bless moment — this
        # freeze commit's own date, the safe floor, since the carrying merge
        # is necessarily at or after it. Step 4 replaces all six with the real
        # merge time of the promotion that lands them on `main`; forecast
        # early rather than late, because a late forecast fires the tripwire
        # on every honest cell minted before the correction.
        #
        # predictors: claude-baseline, codex-baseline, gemini-baseline.
        "sha256:902b332565be0a00f1180796b6ba1b216567300921416c2c3730cc6bca40e485": datetime(
            2026, 9, 3, 0, 0, 0, tzinfo=UTC
        ),
        "sha256:5af41a53302ee9349ab3f210903b7f756bf27aa5d2a2392eb3394404bbad730f": datetime(
            2026, 9, 3, 0, 0, 0, tzinfo=UTC
        ),
        "sha256:8438d9682a88a0f972ba18fdcaa64f9587096015c4c99d4ba58e6440b0bde999": datetime(
            2026, 9, 3, 0, 0, 0, tzinfo=UTC
        ),
        # evaluators: claude-judge, codex-judge, gemini-judge. None carries
        # forward — the evaluate prompt's bytes move for all three — so none
        # keeps an earlier label's bless moment.
        "sha256:e84e8e5fbf47002aa9ed867db60f3f5eee82dcc3bfdd76e44a0b4aac09d5e631": datetime(
            2026, 9, 3, 0, 0, 0, tzinfo=UTC
        ),
        "sha256:e44173fbe316c7dc95412f3b1165f7ac37f6f41ac7d2bb4ef58d86dee7dca7a8": datetime(
            2026, 9, 3, 0, 0, 0, tzinfo=UTC
        ),
        "sha256:64ae1b0c392b62f88c952bbbcc44de2d9ea358f7a7c36dbc10d231f9ed3366c3": datetime(
            2026, 9, 3, 0, 0, 0, tzinfo=UTC
        ),
    }
)

# The freeze instant — the **counting** boundary, set in the same commit that
# fills the map above (a test pins the coupling). The digest is a pure content
# hash, so a cell stamped *before* the freeze with the very bytes about to be
# blessed would otherwise read as frozen retroactively — pre-registration
# means the commitment preceded the run, and only a time cutoff can say so.
# Compared against the stamp's `stamped_at`, which the harness writes; anything
# at or after the instant is in. It is deliberately guessed *late*, so it sits
# at or after every bless moment in the map above and a cell minted in the
# window between them lands as shakedown rather than as a counted cell. One
# shape inverts that order — the held-instant evaluator re-bless noted below,
# where the instant precedes the newly blessed entries' bless moment. While
# that window is open nothing mechanical gates it (`graded_post_freeze` has
# no digest limb, and the tripwire cannot see a digest the map does not yet
# hold); the gap stays empty because cells are minted from `main` — an
# audited convention, not an invariant. From the bless moment on, the
# evaluation-ledger tripwire detects any cell stamped inside the gap, so a
# violation is caught at the re-bless. The literal must be at or
# after the date of the promotion merge that carried this commit to `main`
# (verified against `promotion/<YYYY-MM-DD>` before the `prereg/` tag is
# minted) and before the first run intended to count — see the cutover in
# `docs/process-version.md`. The exception is an evaluator-half re-bless,
# which holds this instant while swapping only the evaluator entries above:
# the enforced predictor half is byte-identical to the prior `prereg/` tag's,
# so such a label is audited by that byte comparison rather than the date
# rule (the supersession notes in the same doc).
#
# The current value is unmoved from the label before it, and that is the
# **ordinary** rule rather than that exception — proc-v6 moves predictor
# bytes, so the exception cannot apply. The date rule is satisfied without a
# move because the instant already sits ahead of the carrying promotion, on
# the condition the freeze record registers: this must land on `main` at or
# before it. Should the promotion slip past, the instant is bumped in a
# follow-up promotion **before** the `prereg/` tag is minted, since a tag over
# a bad instant burns the label.
FROZEN_SINCE: datetime | None = datetime(2026, 9, 5, 0, 0, 0, tzinfo=UTC)

# The retrieval surface each engine's cells run with. Folded into the digest
# because it is a process input as much as the model or the prompt: a cell that
# can reach the open web is answering from a different information set than one
# that cannot, and without this a capability change would ride silently under
# the digest that blessed the runs made before it.
#
# The engines are configured in `CodexRunner.build_command` and the engine steps
# of run-predict / run-evaluate — plus, for codex's subprocess-network half, the
# permission profile `fedcourtsai.mcp` emits into the config.toml those steps
# select by name (codex-action refuses a sandbox override in `codex-args`, so
# the grant cannot ride on the step). Indexed rather than `.get`, so a new engine
# fails loudly here instead of defaulting to a surface nobody declared; the
# codex row is pinned to the runner's own argv by a test in `test_runner.py` and
# to the cells' profile by one in `test_process_version.py`.
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


def blessed_at(digest: str) -> datetime | None:
    """The instant ``digest`` was blessed, or ``None`` if it never was.

    The bless moment is the merge time of the promotion that carried the freeze
    commit naming this digest to ``main`` — when its bytes stopped being
    editable, and so the earliest a cell could have run against a *commitment*
    rather than a draft.
    """
    return FROZEN_PROCESS_DIGESTS.get(digest)


def at_or_after_bless(process_version: ProcessVersion | None) -> bool:
    """Whether a stamped cell was minted at or after its own digest was blessed.

    The **retroactivity** boundary, not the counting one: a cell that passes
    this and still predates :data:`FROZEN_SINCE` is an honest shakedown cell —
    it ran against a commitment already immutable on ``main``, and only timing
    keeps it out of the headline. A cell that *fails* it carries a digest
    blessed after it ran, which is retroactive blessing and no declaration
    licenses it.

    False for an unstamped cell and for an unblessed digest — neither has a
    bless moment to be after — and false for a naive ``stamped_at``, which has
    no defined order against the aware bless instant, the same exclusion rule
    :func:`at_or_after_freeze` applies.
    """
    if process_version is None:
        return False
    bless = FROZEN_PROCESS_DIGESTS.get(process_version.digest)
    if bless is None or process_version.stamped_at.tzinfo is None:
        return False
    return process_version.stamped_at >= bless


def graded_post_freeze(process_version: ProcessVersion | None) -> bool:
    """Whether an evaluation's own harness stamp is at or after the freeze.

    The time half only: the evaluator's digest is recorded but deliberately
    not enforced for counting (the competitor being ranked is the predictor;
    its retroactivity is the evaluation-ledger tripwire's job). Keyed on the
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
    run. The **counting** instant is the one gated here, never the digest's own
    bless moment — a cell minted in the window between them is a legitimate
    ledger cell that this correctly leaves out of the headline.
    """
    if process_version is None or process_version.digest not in FROZEN_PROCESS_DIGESTS:
        return False
    return at_or_after_freeze(process_version.stamped_at)


def frozen_process_record() -> FrozenProcessRecord:
    """The freeze constants as the board-embeddable provenance block.

    The boards publish ``process_scope`` but the partition's *definition* lives
    in this module's two constants, so a built artifact records them via this
    record (:class:`fedcourtsai.schemas.FrozenProcessRecord`) — what "frozen"
    meant at build time, answerable from the artifact alone. Deterministic:
    the constants change only with a freeze commit, so the same tree always
    yields the same record.
    """
    return FrozenProcessRecord(digests=sorted(FROZEN_PROCESS_DIGESTS), since=FROZEN_SINCE)
