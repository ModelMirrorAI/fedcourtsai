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
``label`` is human-readable sugar. ``pipeline_sha`` is deliberately excluded
from the digest; it is provenance, and the side test of every harness boundary
(:func:`boundary_side`) — see :class:`fedcourtsai.schemas.ProcessVersion`.

The freeze is a deliberate, explicit event: one "freeze commit" registers
:data:`FROZEN_PROCESS_DIGESTS` and :data:`FROZEN_SINCE` together, as rows of
the committed registry ``process_registry.json`` (:func:`load_process_registry`)
these constants are built from — the
digest(s) a maintainer reads off ``fedcourts process-digest --all``, each
carrying the instant it was blessed, and the instant a run's harness stamp
must be at or after to count. Those are **two** boundaries doing two jobs, and
they answer different questions even where they fall on the same moment:

- the **bless moment** — a digest's value in the map — is when that process's
  bytes became immutable on ``main``, so it is the *retroactivity* boundary. A
  cell stamped before it ran against a commitment that could still be edited,
  which is retroactive blessing and nothing licenses it. Auditable from git:
  it is the merge time of the promotion that carried the freeze commit.
- the **counting instant**, :data:`FROZEN_SINCE`, is when the current label's
  cells start counting, and it opens every window the label newly blesses.
  It sits at or after every bless moment: guessed generously late at the
  freeze commit, then verified at step 4 of the cutover against the merge
  that landed. Where it sits strictly later, cells minted in the window
  between the two land honestly in the ledger and are de-counted by timing —
  shakedown, not retroactivity. Where step 4 puts it *at* the merge, the
  window is zero-width and there is no such cell to mint.

**Counting is per window.** A predictor digest's blessing opens a
:class:`~fedcourtsai.schemas.CountingWindow` at its label's counting instant;
a successor that stops blessing it closes the window at the successor's
instant, and the window's cells keep counting under the label that opened it.
:data:`COUNTING_WINDOWS` is that registry and the counting rule: a prediction
is in scope where its digest has a window containing its stamp
(:func:`is_frozen`), and where one predictor holds cells from several windows
on one event only the earliest still-counting window's cell counts
(:func:`counted_on_event`). Only a **revocation** — a dated freeze-record
entry stating a defect — de-counts a window. An evaluation is gated on the
instant that opened its prediction's window (:func:`graded_in_window`), not on
a successor's. A later evaluator-half re-bless revises the map's evaluator
entries while holding the instant; a predictor-half re-bless closes the
superseded digests' windows and opens the new ones. The cutover procedure, its
verification, and the supersession shapes live in ``docs/process-version.md``.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cache
from importlib.resources import files
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal

from .pricing import DEFAULT_MODELS
from .registry import (
    load_evaluators,
    load_mcp_servers,
    load_predictors,
    resolve_mcp_servers,
)
from .schemas import (
    CountingWindow,
    Evaluation,
    EvaluatorConfig,
    FrozenProcessRecord,
    PredictorConfig,
    ProcessRegistry,
    ProcessVersion,
    RegistryInstant,
    RubricCount,
    WindowCount,
    WindowShare,
)

# Human label the current process is stamped with. Bump on a deliberate,
# named process change; the digest moves on *any* input change regardless.
CURRENT_PROCESS_LABEL = "proc-v9"

#: The committed frozen-process registry the freeze constants below are built
#: from: the labels and their counting instants, the digests the current label
#: blesses with their bless moments, every counting window, every evaluate
#: label that blessed each evaluator digest, and every harness boundary. Data,
#: not code, so a registration is a reviewed edit to one file and every instant
#: carries the merge it is audited against.
REGISTRY_RESOURCE = "process_registry.json"


def load_process_registry(text: str | None = None) -> ProcessRegistry:
    """The frozen-process registry, validated; ``text`` overrides the packaged file.

    Refuses a registration no merge has carried yet (``merge: null``): this
    module reads every registered instant as in force.
    """
    raw = (
        text
        if text is not None
        else files("fedcourtsai").joinpath(REGISTRY_RESOURCE).read_text(encoding="utf-8")
    )
    registry = ProcessRegistry.model_validate_json(raw)
    instants: list[RegistryInstant] = [entry.since for entry in registry.labels]
    instants += [blessing.blessed for blessing in registry.blessings]
    for window in registry.windows:
        instants.append(window.opens)
        if window.closes is not None:
            instants.append(window.closes)
    if any(instant.merge is None for instant in instants):
        raise ValueError(f"{REGISTRY_RESOURCE}: an instant carries no merge")
    return registry


def _utc(moment: datetime) -> datetime:
    """``moment`` on :data:`datetime.UTC`, the one clock every freeze constant reads."""
    return moment.astimezone(UTC)


_REGISTRY: Final[ProcessRegistry] = load_process_registry()

# The first label whose **cert** gradings carry a harness-stamped skill record
# (`stamp-cell --role evaluator`; `cli._cert_skill_record_for`): the Brier, the
# risk-set anchor pooled through the scorer's own pooler over the scored
# prediction's frozen `(band, salience_version, term)`, and the skill over
# them. Keyed on the label a grading is stamped with, never on the stamp's
# date, so a grading stamped under an earlier label keeps the registered
# reading — the evaluator's transcription off `metrics/statpack.md`, held only
# by the board's self-consistency check — through any later re-grade, and a
# scoring rule never changes inside one label's life.
HARNESS_CERT_ANCHOR_FROM = "proc-v9"

_LABEL_PATTERN = re.compile(r"proc-v(\d+)")


def label_ordinal(label: str | None) -> int | None:
    """The integer ``N`` of a ``proc-vN`` label, or ``None`` for any other string."""
    if label is None:
        return None
    match = _LABEL_PATTERN.fullmatch(label)
    return int(match.group(1)) if match else None


def harness_stamps_cert_anchor(label: str | None) -> bool:
    """Whether a cert grading stamped under ``label`` takes the harness's skill record.

    True from :data:`HARNESS_CERT_ANCHOR_FROM` on. False for an earlier label,
    for an unstamped record (``None``), and for a label that is not a
    ``proc-vN`` at all, so an unrecognised label keeps the registered reading
    rather than acquiring a new scoring rule by accident.
    """
    ordinal = label_ordinal(label)
    threshold = label_ordinal(HARNESS_CERT_ANCHOR_FROM)
    return ordinal is not None and threshold is not None and ordinal >= threshold


# The blessed process digests, each mapped to its bless moment — the current
# label's blessing and the retroactivity record, not the counting rule (that is
# COUNTING_WINDOWS below). Built from the registry's `blessings`: each digest is
# read off `fedcourts process-digest --all` and registered together with
# FROZEN_SINCE below, which a test pins. The map holds one
# blessed process per actor, so a digest a label stops blessing leaves it; the
# de-counted digests of the labels before proc-v8 and the census of what ran
# under every superseded digest live in the freeze record. Keyed on the
# digest, never the label, so a process that drifted under an unchanged label
# is not silently blessed.
#
# proc-v9 blesses four digests newly and carries two forward:
#
# - claude-baseline's predictor digest is new: the claude engine's default
#   model (`pricing.DEFAULT_MODELS`, a digest input) is claude-opus-5-5. This
#   is the predictor-half re-bless, so it closes the proc-v8 claude-baseline
#   window and opens a proc-v9 one (COUNTING_WINDOWS).
# - the three evaluator digests are new: the evaluate prompt's stakes-read
#   instruction says the predictors' `big_case_score` is in view and asks for
#   a read that does not anchor on it, its `qp-topics` leakage rule reads a
#   search that excludes the path as not touching it, and a frozen-band cert
#   cell's anchor is left to the stamp; claude-judge also takes the claude
#   default model. An evaluator digest records and never partitions, so this
#   half closes and opens no window.
# - codex-baseline's and gemini-baseline's predictor digests are byte-identical
#   to proc-v8's. They keep proc-v8's bless moment verbatim and their proc-v8
#   windows stay open and unbroken (a test asserts the bytes did not move).
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
    {blessing.digest: _utc(blessing.blessed.at) for blessing in _REGISTRY.blessings}
)

# The freeze instant — the **counting** boundary, the current label's `since`
# in the registry, registered in the same commit as the map above (a test pins
# the coupling). The digest is a pure content
# hash, so a cell stamped *before* the freeze with the very bytes about to be
# blessed would otherwise read as frozen retroactively — pre-registration
# means the commitment preceded the run, and only a time cutoff can say so.
# Compared against the stamp's `stamped_at`, which the harness writes; anything
# at or after the instant is in. It opens every window the current label newly
# blesses and closes every window it stops blessing; a carried-forward digest's
# window keeps the instant that opened it. It sits at or after every bless
# moment in the map above — guessed generously late at the freeze commit, then
# verified at step 4 against the merge that actually landed and bumped where it
# came in early, never pulled back — so a cell minted in any window between the
# two lands as shakedown rather than as a counted cell. One shape inverts that
# order — an evaluator-half re-bless that holds this instant while swapping
# only the evaluator entries above, licensed because the enforced predictor
# half is then byte-identical to the prior `prereg/` tag's and such a label is
# audited by that byte comparison rather than by the date rule (the
# supersession notes in `docs/process-version.md`).
#
# proc-v9 is not that shape: it newly blesses a predictor digest, so the
# instant moves and the ordinary rule governs — the instant must be at or after
# the merge of the promotion that carries this label's freeze commit to `main`
# and before the first run intended to count. That merge is not known at the
# freeze commit, so the instant is a **late** forecast,
# `2026-10-11T12:00:00Z`: after the promotion the maintainer is landing on
# 2026-10-10, and before `run-predict`'s first scheduled round on 2026-10-11
# (14:12Z), so no scheduled round falls between the merge and the instant. A
# cell the new claude digest stamps between that merge and the instant is
# honest shakedown, uncounted and re-owed; one stamped before the
# merge cannot exist, since nothing carries the new bytes until the merge does.
# Should the promotion slip past the instant, step 4 bumps it before the tag.
FROZEN_SINCE: datetime | None = next(
    (_utc(entry.since.at) for entry in _REGISTRY.labels if entry.label == CURRENT_PROCESS_LABEL),
    None,
)

# The counting registry, built from the registry's `windows`: one window per
# blessing of a predictor digest, and
# the counting rule every frozen-scope reader applies (`is_frozen`,
# `counted_on_event`, `graded_in_window`). A window opens at the counting
# instant of the label that blessed its digest and closes at the counting
# instant of the successor that stops blessing it, each as its `prereg/` tag
# records it. Closing de-counts nothing: a closed window's cells keep counting
# under the label that opened it. Only a revocation — `revoked_at`, on a dated
# freeze-record entry that states a defect from committed artifacts — de-counts
# a window, and its events are then re-owed afresh.
#
# A successor's freeze commit therefore *adds* to this tuple rather than
# replacing it: it sets `closes` on each window whose digest it stops blessing
# (to its own counting instant) and appends one window per digest it newly
# blesses, opening at that instant. A digest carried forward byte-identical
# keeps its window open and unbroken, still under the label that opened it; a
# digest blessed again after its window closed opens a second window. Keyed on
# the digest, like the bless map, so a process that drifted under an unchanged
# label is not silently counted.
#
# Predictor digests only: an evaluator digest records and never partitions,
# so it has no window; an evaluation's counting is its prediction's window's
# timing gate (`graded_in_window`).
#
# The labels before proc-v8 are not windows. Their digests were de-counted when
# each was superseded, under the rule then in force, and the freeze record's
# 2026-09-26 entry leaves them de-counted.
#
# proc-v8 opened one window per predictor digest at its counting instant,
# `2026-09-16T00:26:04Z` (a test pins that none of the three leaves this
# registry without a closing instant). proc-v9 closes claude-baseline's at
# FROZEN_SINCE and opens a proc-v9 window for the new claude-baseline digest
# there; codex-baseline's and gemini-baseline's stay open, still labelled
# proc-v8.
COUNTING_WINDOWS: tuple[CountingWindow, ...] = tuple(
    CountingWindow(
        label=window.label,
        digest=window.digest,
        predictor_id=window.predictor_id,
        opens=_utc(window.opens.at),
        closes=_utc(window.closes.at) if window.closes is not None else None,
        revoked_at=_utc(window.revoked_at) if window.revoked_at is not None else None,
    )
    for window in _REGISTRY.windows
)

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
# to the cells' profile by one in `test_process_version.py`; gemini's row is
# pinned by the same file's ledger-argv test, which fixes a live cell's whole
# command line, so a capability reaching gemini through a new flag has to move
# that test first.
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
    this and still predates its window's opening instant is an honest
    shakedown cell — it ran against a commitment already immutable on
    ``main``, and only timing keeps it out of the headline. A cell that
    *fails* it carries a digest blessed after it ran, which is retroactive
    blessing and no declaration licenses it.

    False for an unstamped cell and for an unblessed digest — neither has a
    bless moment to be after — and false for a naive ``stamped_at``, which has
    no defined order against the aware bless instant, the same exclusion rule
    :meth:`fedcourtsai.schemas.CountingWindow.contains` applies.
    """
    if process_version is None:
        return False
    bless = FROZEN_PROCESS_DIGESTS.get(process_version.digest)
    if bless is None or process_version.stamped_at.tzinfo is None:
        return False
    return process_version.stamped_at >= bless


def freeze_in_force() -> bool:
    """Whether a freeze is in force: a counting instant set and a window registered.

    While none is, there is a single process scope: every committed cell is in
    it, no grading is timing-gated, and the re-predict rule has no partition to
    repair. The two constants move together (a test pins it), so either reads
    the same on the live registry; requiring both keeps a registry patched
    without an instant — digest membership alone, no time gate — behaving as
    it reads.
    """
    return FROZEN_SINCE is not None and bool(COUNTING_WINDOWS)


def window_of(process_version: ProcessVersion | None) -> CountingWindow | None:
    """The window whose digest and span contain this stamp, revoked or not.

    ``None`` for an unstamped cell, for a digest no window names, and for a
    stamp outside every window of its digest — before the opening instant (a
    shakedown run of the very bytes later blessed) or at or after a close. A
    digest's windows never overlap (a test holds the registry to it), so at
    most one matches.
    """
    if process_version is None:
        return None
    for window in COUNTING_WINDOWS:
        if window.digest == process_version.digest and window.contains(process_version.stamped_at):
            return window
    return None


def is_frozen(process_version: ProcessVersion | None) -> bool:
    """Whether a cell's stamp lies in a counting window that still counts.

    The per-cell half of the counting rule: the digest must have a window in
    :data:`COUNTING_WINDOWS` whose span contains ``stamped_at``, and no
    revocation may have de-counted that window. A **closed** window still
    counts — closing is what a successor does, and it removes nothing. An
    unstamped cell (``None``) is never frozen, so the shakedown ledger is
    excluded from the headline for free; and the digest says *which* process
    ran, never *when*, so a shakedown run of the very bytes later blessed is
    still a shakedown run. The **counting** instant is the one gated here,
    never the digest's own bless moment.

    The event half — one counted forecast per predictor and event, the
    earliest window's — is :func:`counted_on_event`, and a reader that scores
    or stages a cell asks that one.
    """
    window = window_of(process_version)
    return window is not None and window.revoked_at is None


def _earliest_opening() -> datetime | None:
    """The earliest instant any registered window opens at, or ``None`` with none."""
    return min((window.opens for window in COUNTING_WINDOWS), default=None)


def counted_on_event(
    process_version: ProcessVersion | None,
    siblings: Callable[[], Iterable[ProcessVersion | None]],
) -> bool:
    """Whether this cell is in its predictor's counted window on the event.

    ``siblings`` yields the stamps of **every** prediction the same predictor
    committed on the same event (this one included), and is called only where
    the answer can depend on them. Three conditions:

    * the cell :func:`is_frozen` — in a window, and that window not revoked;
    * **the earliest window counts.** No sibling sits in a still-counting
      window that opened earlier. Where a predictor holds cells from several
      windows on one event — a named dispatch, or an attempt still open at a
      successor's instant — the earliest window's cell counts and a later
      window's counts in no window;
    * **a revocation never decides which existing forecast is scored.** Where a
      sibling sits in an earlier window that has since been revoked, this cell
      counts only if it was stamped at or after that revocation — the fresh
      forecast the backlog re-owes. One stamped before it stays uncounted, and
      an uncounted earlier-window cell does not block a later one: only a
      sibling that itself counts takes the count.

    Within one window every run is a candidate, and the run collapse picks the
    counted cell among them exactly as it does for a single window.

    Short-circuits without reading ``siblings`` for a cell in a window that
    opened at the earliest registered instant: nothing can sit in an earlier
    window, so there is nothing to lose the tie-break to or be revoked behind.
    """
    window = window_of(process_version)
    if process_version is None or window is None or window.revoked_at is not None:
        return False
    earliest = _earliest_opening()
    if earliest is None or window.opens <= earliest:
        return True
    stamps = list(siblings())
    return _unblocked(process_version, window, stamps)


def _unblocked(
    process_version: ProcessVersion, window: CountingWindow, stamps: list[ProcessVersion | None]
) -> bool:
    """Whether no sibling in an earlier window takes the count from this cell.

    An earlier **revoked** window's sibling blocks a cell stamped before the
    revocation, and never one stamped after it. An earlier **counting**
    window's sibling blocks only where it is itself counted — so a stale
    earlier-window cell that a revocation left uncounted does not stand in
    front of the fresh forecast made after that revocation. Recursion runs over
    strictly earlier windows, so it terminates.
    """
    for sibling in stamps:
        other = window_of(sibling)
        if sibling is None or other is None or other.opens >= window.opens:
            continue
        if other.revoked_at is not None:
            if process_version.stamped_at < other.revoked_at:
                return False
        elif _unblocked(sibling, other, stamps):
            return False
    return True


def staging_excluded(
    process_version: ProcessVersion | None,
    siblings: Callable[[], Iterable[ProcessVersion | None]],
) -> bool:
    """Whether a cell sits in a live window yet is not its predictor's counted cell.

    The cells :func:`counted_on_event` leaves counting nowhere. They are never
    the latest-run candidate — for evaluation staging, the scored-prediction
    fallback, or the stamp's ``prediction_run_id`` — so a later window's cell
    is not staged for grading in place of the earliest window's. Every other
    cell, in scope or not, stays a candidate exactly as before, so which run is
    latest is unchanged wherever the tie-break has nothing to decide.
    """
    return is_frozen(process_version) and not counted_on_event(process_version, siblings)


def graded_in_window(evaluation: ProcessVersion | None, prediction: ProcessVersion | None) -> bool:
    """Whether an evaluation's own harness stamp passes its prediction's window gate.

    The timing half of an evaluation's counting: stamped at or after the
    instant that **opened the graded prediction's window** — not a successor's
    later instant, so a closed window's cells keep the gradings made before
    the successor froze. The evaluator's digest is recorded but deliberately
    not enforced (the competitor being ranked is the predictor; its
    retroactivity is the evaluation-ledger tripwire's job). Keyed on the
    evaluation's **harness-written** stamp, never its agent-written
    ``created_at`` — the pre-registration boundary must not rest on a clock the
    agent controls. While no window is registered this is a no-op; otherwise
    an unstamped evaluation, a naive stamp, and a prediction in no window all
    fail it (local runs are unstamped and stay diagnostic).
    """
    if not freeze_in_force():
        return True
    window = window_of(prediction)
    if window is None or evaluation is None or evaluation.stamped_at.tzinfo is None:
        return False
    return evaluation.stamped_at >= window.opens


def frozen_process_record() -> FrozenProcessRecord:
    """The freeze constants as the board-embeddable provenance block.

    The boards publish ``process_scope`` but the partition's *definition* lives
    in this module's constants, so a built artifact records them via this
    record (:class:`fedcourtsai.schemas.FrozenProcessRecord`) — what "frozen"
    meant at build time, the counting windows included, answerable from the
    artifact alone. Deterministic: the constants change only with a freeze
    commit, so the same tree always yields the same record.
    """
    return FrozenProcessRecord(
        digests=sorted(FROZEN_PROCESS_DIGESTS),
        since=FROZEN_SINCE,
        windows=list(COUNTING_WINDOWS),
    )


def resolvable_runs[T](runs: Sequence[T], stamp: Callable[[T], ProcessVersion | None]) -> list[T]:
    """``runs`` less the cells :func:`staging_excluded` names, order kept.

    ``runs`` is every prediction one predictor committed on one event, and
    ``stamp`` reads each one's harness stamp. The one filter every
    latest-run resolution applies before it takes the newest — evaluation
    staging, the scored-prediction fallback, and the stamp's
    ``prediction_run_id`` — so all three resolve the same run.
    """
    stamps = [stamp(run) for run in runs]
    return [
        run
        for run, own in zip(runs, stamps, strict=True)
        if not staging_excluded(own, lambda: stamps)
    ]


def describe_windows(windows: Iterable[CountingWindow]) -> str:
    """A stable, human-readable listing of windows for a refusal message.

    Label plus opening instant, so two windows sharing a label stay distinct.
    """
    ordered = sorted(windows, key=lambda w: (w.opens, w.digest))
    return ", ".join(f"{w.label}@{w.opens.isoformat()}" for w in ordered)


class PooledWindowsError(ValueError):
    """Two of one predictor's counting windows share a label.

    Every by-protocol figure is published under ``(predictor_id, label)``, and
    every composition names a window by its label, so two windows under one
    label could not be told apart on any surface.
    """


#: One by-protocol series on a frozen-scope figure: a predictor and the
#: counting window its counted cells come from (``None`` on an all-versions
#: build, which keys on the predictor alone). The pooled default keys on the
#: predictor and lists these as its composition.
type Series = tuple[str, CountingWindow | None]


def series_sort_key(series: Series) -> tuple[str, float, str]:
    """A total order over series: predictor id, then the window's opening instant.

    One predictor's windows run in sequence, so this lists its series in the
    order its windows opened; the digest settles the (unregistrable) tie.
    """
    predictor_id, window = series
    if window is None:
        return (predictor_id, float("-inf"), "")
    return (predictor_id, window.opens.timestamp(), window.digest)


def window_label(window: CountingWindow | None) -> str | None:
    """The label a figure over ``window``'s cells is published under, or ``None``."""
    return window.label if window is not None else None


def refuse_shared_labels(series: Iterable[Series], *, surface: str) -> None:
    """Raise where two of one predictor's windows share a label.

    Every per-window figure is published under ``(predictor_id, label)``, so
    two windows that both carried one label would be two series under one
    name. A label blesses one digest per predictor, so the registry cannot
    produce this; the check keeps a hand-edited registry from doing it silently.
    """
    labels: dict[tuple[str, str], set[CountingWindow]] = {}
    for predictor_id, window in series:
        if window is not None:
            labels.setdefault((predictor_id, window.label), set()).add(window)
    shared = sorted(key for key, spans in labels.items() if len(spans) > 1)
    if shared:
        raise PooledWindowsError(
            f"{surface}: two counting windows share a label for "
            + ", ".join(
                f"{pid} ({describe_windows(labels[(pid, label)])})" for pid, label in shared
            )
            + " — a per-window figure could not name them apart"
        )


def co_current(windows: Iterable[CountingWindow]) -> bool:
    """Whether every window was open at one instant: the latest opening precedes every close.

    The windows a cross-engine comparison may read together. A closed window
    and the successor that closed it never ran together, so an event whose
    predictors' counted cells come from both is a **split event** and belongs
    to no complete grid. Windows that opened at one instant (``proc-v8``'s
    three) and a carried-forward window beside either side of a successor are
    co-current.
    """
    spans = list(windows)
    if not spans:
        return True
    latest = max(window.opens for window in spans)
    return all(window.closes is None or window.closes > latest for window in spans)


def pooled_windows(counts: Mapping[Series, int]) -> list[WindowCount]:
    """The (predictor, window) series a cross-predictor figure pools, each with its ``n``.

    The composition of a figure keyed on something other than the forecaster —
    a judge validation, a grader-agreement read, a calibration or a tool-usage
    correlation over every engine's cells (``docs/process-version.md``,
    *Pooled by default*). Listed whenever the figure is a frozen-scope pool, a
    single label included: the composition is part of the figure, not a
    warning shown only when there is something to warn about. Such a figure is
    never a rank key. An all-versions build (series without a window) lists
    nothing.
    """
    return [
        WindowCount(predictor_id=predictor_id, process_window=window.label, n=n)
        for (predictor_id, window), n in sorted(
            counts.items(), key=lambda item: series_sort_key(item[0])
        )
        if window is not None
    ]


def composition(counts: Mapping[CountingWindow, int]) -> list[WindowShare]:
    """The windows a pooled figure spans, each with its ``n``, in opening order.

    The composition every pooled frozen-scope figure states beside its value
    (``docs/process-version.md``, *Pooled by default*). Listed even for a
    single window: the composition is part of the figure, not a warning shown
    only when there is something to warn about. A window is named by its own
    label and opening instant — the window the cell's digest and stamp fall
    in — never by the label on the cell's stamp.
    """
    return [
        WindowShare(process_window=window.label, opens=window.opens, n=n)
        for window, n in sorted(counts.items(), key=lambda item: (item[0].opens, item[0].digest))
    ]


def composition_of[K](
    keys: Iterable[K], cell_windows: Mapping[K, CountingWindow]
) -> list[WindowShare]:
    """:func:`composition` over the cells ``keys`` name, each counted once per key.

    The makeup of a pooled figure whose population is a set of keyed cells (a
    grading, a cell): each key that ``cell_windows`` places in a window counts
    once toward that window's ``n``. A key with no window — an all-versions
    build — counts nowhere, so such a build lists nothing.
    """
    counts: dict[CountingWindow, int] = defaultdict(int)
    for key in keys:
        if (window := cell_windows.get(key)) is not None:
            counts[window] += 1
    return composition(counts)


#: A judge rubric: the evaluator and the evaluate digest on its harness stamp
#: (``None`` for an unstamped grading).
Rubric = tuple[str, str | None]


def rubric_of(evaluation: Evaluation) -> Rubric:
    """A grading's rubric: its ``evaluator_id`` with its harness stamp's digest."""
    stamp = evaluation.process_version
    return (evaluation.evaluator_id, stamp.digest if stamp is not None else None)


#: A panel figure's rubric signature: the sorted set of (evaluator, digest)
#: pairs its reads come from, in :func:`rubric_order`.
RubricSignature = tuple[Rubric, ...]

# Every evaluate label that blessed each evaluator digest, in blessing order,
# kept after those labels are superseded: `FROZEN_PROCESS_DIGESTS` holds only
# the digests the current label blesses, while a per-rubric reading over an
# older judge rubric is still named by the labels that blessed it.
#
# Built from the registry's `evaluate_blessing_labels`. Append-only. A label
# that newly blesses an evaluator digest adds it with
# that label; a label that carries a digest forward byte-identical appends
# itself to that digest's tuple. No entry or label is ever edited, removed or
# reordered, since a published reading's name would move with it. A test pins
# every live evaluator digest's tuple to contain `CURRENT_PROCESS_LABEL`.
#
# The map starts at `proc-v8` because `COUNTING_WINDOWS` does: no cell before
# the first window counts, so no earlier judge digest can appear in a
# frozen-scope point.
EVALUATE_BLESSING_LABELS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {digest: tuple(labels) for digest, labels in _REGISTRY.evaluate_blessing_labels.items()}
)


def blessing_labels(rubrics: Iterable[Rubric]) -> list[str]:
    """Every evaluate label that blessed these rubrics' digests, sorted.

    The union over the digests, each carrying every label that blessed it,
    carried-forward labels included. A name for a per-rubric reading, never a
    partition. An unstamped grading's digest and a digest no label blessed
    name nothing.
    """
    return sorted(
        {
            label
            for _, digest in rubrics
            if digest is not None
            for label in EVALUATE_BLESSING_LABELS.get(digest, ())
        }
    )


def rubric_order(rubric: Rubric) -> tuple[str, bool, str]:
    """The stable order rubrics list in: by evaluator, then digest, ``None`` first."""
    evaluator, digest = rubric
    return (evaluator, digest is not None, digest or "")


def rubric_listing(counts: Mapping[Rubric, int]) -> list[RubricCount]:
    """The rubrics a judge-dependent figure spans, each with its ``n``, in a stable order.

    Ordered by evaluator, then digest, an unstamped grading's ``None`` digest
    first. Listed whatever the count, so a figure over one rubric says which.
    """
    return [
        RubricCount(evaluator_id=evaluator, digest=digest, n=n)
        for (evaluator, digest), n in sorted(counts.items(), key=lambda item: rubric_order(item[0]))
    ]


def rubric_signature(rubrics: Iterable[Rubric]) -> RubricSignature | None:
    """The rubric signature of one panel point's reads, or ``None`` where they span two.

    A signature holds one digest per evaluator, so a point whose reads carry
    one evaluator under two digests spans two signatures and belongs to no
    per-rubric reading; it still counts in the pooled coverage value.
    """
    pairs = sorted(set(rubrics), key=rubric_order)
    evaluators = [evaluator for evaluator, _ in pairs]
    if len(set(evaluators)) != len(evaluators):
        return None
    return tuple(pairs)


def is_retired(predictor_id: str) -> bool:
    """Whether every counting window registered to ``predictor_id`` is closed or revoked.

    A retired predictor keeps its pooled record and its by-protocol cut but
    leaves the ranked set, so the paired events stop following an engine that
    no longer forecasts. Taking a predictor off the roster goes through a
    re-bless that closes its window, which is what lets this read the registry
    alone. A predictor no window names is not retired: the registry records
    every production window's predictor (a test holds it to that), so only a
    hand-built registry leaves one unnamed, and an unknown is not a retirement.

    A window with a ``closes`` is closed for this test whether or not that
    instant has passed: only a successor's freeze sets it, so the predictor's
    open window — if any — is the successor's, and a board carries no clock to
    read the instant against.
    """
    owned = [window for window in COUNTING_WINDOWS if window.predictor_id == predictor_id]
    return bool(owned) and all(
        window.closes is not None or window.revoked_at is not None for window in owned
    )


#: Which cells a boundary's change can reach. ``all`` and ``replay cells`` are
#: decidable from a cell's own committed record; the two docket-scoped reaches
#: are not (a docket's representation lives in the corpus's party data, and its
#: grant state is a fact about the docket at the cell's moment).
type BoundaryReach = Literal["self-represented dockets", "granted dockets", "all", "replay cells"]


@dataclass(frozen=True)
class HarnessBoundary:
    """A dated change to what a predict cell reads under an unchanged predictor digest.

    Composition, not a cut: the pooled default and the paired figure keep both
    sides and list how many cells sit on each. A cell's side is read by
    ancestry (:func:`boundary_side`), and ``at`` — the carrying commit's
    committer time — is for display only.
    """

    name: str
    #: The full SHA of the commit that carried the change to ``main``.
    merge: str
    #: That commit's committer time; display only, never the side test.
    at: datetime
    #: The predictors the boundary splits; ``None`` for every predictor.
    predictors: frozenset[str] | None
    #: The cells the change can reach.
    reach: BoundaryReach
    #: The change reached the corpus through a back-fill pass, so a cell after
    #: it may still read the earlier document set.
    gradual: bool = False


#: Every :class:`HarnessBoundary` dated since the earliest counting window
#: opened, in the order their carrying commits reached ``main``: the freeze
#: record's 2026-10-11 implementation-choices entry registers this list, and a
#: later change of the class joins the registry's `harness_boundaries` in the
#: PR that carries it. The scrubs
#: and the merits-brief selector reach every predictor; the ``proc-v9``
#: three split only the carried-forward codex and gemini windows, since the
#: same merge moved claude-baseline's digest.
HARNESS_BOUNDARIES: Final[tuple[HarnessBoundary, ...]] = tuple(
    HarnessBoundary(
        boundary.name,
        boundary.merge,
        _utc(boundary.at),
        frozenset(boundary.predictors) if boundary.predictors is not None else None,
        boundary.reach,
        gradual=boundary.gradual,
    )
    for boundary in _REGISTRY.harness_boundaries
)


class BoundaryHistoryError(RuntimeError):
    """The checkout cannot answer a boundary's ancestry test, so no side is read.

    Raised on a shallow clone and on a commit the checkout does not hold. Never
    answered by a guess: a cell filed on the wrong side of a boundary is a wrong
    count published as a right one.
    """


type BoundarySide = Literal["before", "after"]

#: An abbreviated or full lowercase hex commit id — all ``boundary_side`` will
#: hand to git, so no stamped value reaches a subprocess argv unchecked.
_SHA = re.compile(r"[0-9a-f]{7,40}")


def boundary_side(
    boundary: HarnessBoundary, pipeline_sha: str | None, *, repo: Path
) -> BoundarySide | None:
    """Which side of ``boundary`` a cell built at ``pipeline_sha`` sits on.

    ``after`` where the boundary's carrying commit is an ancestor of, or equal
    to, the cell's ``process_version.pipeline_sha`` — the "or equal" files a run
    started on that commit itself as post-change — else ``before``. ``None``
    for a cell with no ``pipeline_sha``, which sits on neither side and is
    counted as such by the caller. Read with ``git merge-base --is-ancestor``
    in ``repo``, cached per (commit, sha); raises
    :class:`BoundaryHistoryError` rather than guess where ``repo`` is shallow
    or lacks either commit.
    """
    if not pipeline_sha:
        return None
    for sha in (boundary.merge, pipeline_sha):
        if not _SHA.fullmatch(sha):
            raise BoundaryHistoryError(
                f"{sha!r} is not a commit sha: a harness-boundary side is read only off one"
            )
    return "after" if _is_ancestor(str(repo), boundary.merge, pipeline_sha) else "before"


def boundary_admits(boundary: HarnessBoundary, predictor_id: str, mode: str | None) -> bool:
    """Whether ``boundary`` counts a ``predictor_id`` cell run in ``mode``.

    The boundary's predictors and its mode decide; the docket-scoped reaches
    (self-represented, granted) are the boundary's printed scope, never a
    filter, since whether a docket was either at a cell's moment lives only in
    the corpus. ``replay cells`` admits replay-mode cells alone.
    """
    if boundary.predictors is not None and predictor_id not in boundary.predictors:
        return False
    return boundary.reach != "replay cells" or mode == "replay"


def _git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        check=False,
        text=True,
    )


@cache
def _require_full_history(repo: str) -> None:
    shallow = _git(repo, "rev-parse", "--is-shallow-repository")
    if shallow.returncode != 0:
        raise BoundaryHistoryError(f"{repo} is not a git checkout: {shallow.stderr.strip()}")
    if shallow.stdout.strip() == "true":
        raise BoundaryHistoryError(
            f"{repo} is a shallow clone: a harness-boundary side needs the full history — "
            "re-run from a full clone (`git fetch --unshallow`, or check out with fetch-depth 0)"
        )


@cache
def _require_commit(repo: str, sha: str) -> None:
    if _git(repo, "cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        raise BoundaryHistoryError(
            f"{repo} holds no commit {sha}: a harness-boundary side cannot be read — fetch "
            "the ref that carries it (`git fetch origin`), or run from a checkout that holds it"
        )


@cache
def _is_ancestor(repo: str, ancestor: str, descendant: str) -> bool:
    _require_full_history(repo)
    _require_commit(repo, ancestor)
    _require_commit(repo, descendant)
    result = _git(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    if result.returncode not in (0, 1):
        raise BoundaryHistoryError(
            f"git merge-base --is-ancestor {ancestor} {descendant} failed in {repo}: "
            + result.stderr.strip()
        )
    return result.returncode == 0


@contextmanager
def counting_windows(windows: Sequence[CountingWindow]) -> Iterator[None]:
    """Read the counting rule over ``windows`` instead of the registry, for one block.

    For the one reader that must see the ledger as a different registry would
    count it: a revoked window's figures over its resolved slice, which lift
    that window's revocation to show what the revocation removed
    (:func:`fedcourtsai.window_records.revoked_window_board`). Every counting
    function reads :data:`COUNTING_WINDOWS` at call time, so the whole rule —
    the event tie-break, the timing gate, staging's resolver — follows the
    override, and the committed registry is restored on exit whatever happens.
    Never used on a path that writes the ledger.
    """
    global COUNTING_WINDOWS  # noqa: PLW0603 - swapping the registry is the override
    saved = COUNTING_WINDOWS
    COUNTING_WINDOWS = tuple(windows)
    try:
        yield
    finally:
        COUNTING_WINDOWS = saved
