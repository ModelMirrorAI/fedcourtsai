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
from collections.abc import Callable, Iterable, Mapping, Sequence
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
from .schemas import (
    CountingWindow,
    EvaluatorConfig,
    FrozenProcessRecord,
    PredictorConfig,
    ProcessVersion,
)

# Human label the current process is stamped with. Bump on a deliberate,
# named process change; the digest moves on *any* input change regardless.
CURRENT_PROCESS_LABEL = "proc-v8"

# The blessed process digests, each mapped to its bless moment — the current
# label's blessing and the retroactivity record, not the counting rule (that is
# COUNTING_WINDOWS below): the six proc-v8
# baselines (claude/codex/gemini, predictor and evaluator each), read off
# `fedcourts process-digest --all`; set together with FROZEN_SINCE below,
# which a test pins. proc-v8 is a **full** freeze: all six digests are newly
# blessed at one carrying promotion. The predictor half moves because the
# predict contract's bytes move — the snapshot stamp's canonical form, the
# stakes read as a required number-or-null, the merits documents a granted
# docket now carries, and the entry forms the interim amicus count reads — and
# the evaluator half because the grading protocol's bytes move: the evaluate
# cell is handed the case's staged majority opinion at `record/opinion/`, and
# the mask's ground becomes a counted field the grader names rather than free
# text inside `basis`. The map holds one blessed process per actor, so
# proc-v7's six digests are replaced rather than kept beside these. This
# constant names the live fleet's processes alone; the de-counted digests of
# earlier labels and the census of what ran under them live in the freeze
# record. Keyed
# on the digest, never the label,
# so a process that drifted under an unchanged label is not silently blessed.
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
        # Every entry below is the audited carrying-merge time per the block
        # comment above: `2026-09-16T00:26:04Z`, the committed instant of the
        # merge `545e26e2b` that carried this label's two freeze commits to
        # `main`, which `promotion/2026-09-16` tags and the freeze record
        # carries the re-derivation command for. Nothing here is carried
        # forward from proc-v7, so every entry takes step 4's correction off
        # that one merge and all six carry the same value — one promotion
        # carries both halves, which is what makes this a full freeze.
        #
        # predictors: claude-baseline, codex-baseline, gemini-baseline.
        "sha256:1a0b2bef2e367cd589e4800fa04de5b5110b41bf1ea159b3c51669ccc722e89a": datetime(
            2026, 9, 16, 0, 26, 4, tzinfo=UTC
        ),
        "sha256:70fee158526caa6870d43ace70c3781db39f644379c86c363538ebdefa57547c": datetime(
            2026, 9, 16, 0, 26, 4, tzinfo=UTC
        ),
        "sha256:a9033e56819e775e561b802dec24bae437c17c751e5a7f5fa4b3eeb31383951f": datetime(
            2026, 9, 16, 0, 26, 4, tzinfo=UTC
        ),
        # evaluators: claude-judge, codex-judge, gemini-judge.
        "sha256:fbc0e9c364d846c5701fed0d34727d4ea7c0f002ee9337fe98f791fbb0479d13": datetime(
            2026, 9, 16, 0, 26, 4, tzinfo=UTC
        ),
        "sha256:9670e1c147a723e68534d88ec494cb2c7b7463dcf18dbadecadf3108f08383b1": datetime(
            2026, 9, 16, 0, 26, 4, tzinfo=UTC
        ),
        "sha256:dbdc90647bc81eec9b4de523188f1e46c5dcb64b5717a30da16b8886e4a6d4fe": datetime(
            2026, 9, 16, 0, 26, 4, tzinfo=UTC
        ),
    }
)

# The freeze instant — the **counting** boundary, set in the same commit that
# fills the map above (a test pins the coupling). The digest is a pure content
# hash, so a cell stamped *before* the freeze with the very bytes about to be
# blessed would otherwise read as frozen retroactively — pre-registration
# means the commitment preceded the run, and only a time cutoff can say so.
# Compared against the stamp's `stamped_at`, which the harness writes; anything
# at or after the instant is in. It sits at or after every bless moment in the
# map above — guessed generously late at the freeze commit, then verified at
# step 4 against the merge that actually landed and bumped where it came in
# early, never pulled back — so a cell minted in any window between the two
# lands as shakedown rather than as a counted cell. One
# shape inverts that order — an evaluator-half re-bless that holds this
# instant while swapping only the evaluator entries above, licensed because
# the enforced predictor half is then byte-identical to the prior `prereg/`
# tag's and such a label is audited by that byte comparison rather than by the
# date rule (the supersession notes in `docs/process-version.md`).
#
# proc-v8 is not that shape. It blesses both halves at one promotion, so the
# ordinary rule governs: the literal must be at or after the date of the
# promotion merge that carried this label's freeze commits to `main` (verified
# against `promotion/2026-09-16` before the `prereg/` tag is minted) and before
# the first run intended to count.
#
# The instant is that merge's own committed instant — the same
# `2026-09-16T00:26:04Z` every entry in the map above carries, which is the
# earliest value the rule allows. An instant behind the merge would count
# cells against a commitment still editable when they ran; the enforced half's
# bytes are new here, so nothing licenses one.
#
# Placing it *at* the merge rather than past it is what closes the window, and
# that window costs more than a few uncounted cells. A cell minted between the
# merge and a later instant carries a blessed digest and still fails
# `is_frozen`'s time limb, so the pre-freeze re-predict rule re-owes it and the
# event is paid for twice. Equality leaves no such cell to mint, so the window
# is empty by construction rather than by `run-predict`'s review hold keeping
# it so — the hold stays the control over *when* the first counted round
# spends, not over whether its cells can count.
FROZEN_SINCE: datetime | None = datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC)

# The counting registry: one window per blessing of a predictor digest, and
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
# proc-v8 opens one window per predictor digest, at FROZEN_SINCE (a test pins
# both that and that none of the three leaves this registry without a closing
# instant): claude-baseline, codex-baseline, gemini-baseline.
COUNTING_WINDOWS: tuple[CountingWindow, ...] = (
    CountingWindow(
        label="proc-v8",
        digest="sha256:1a0b2bef2e367cd589e4800fa04de5b5110b41bf1ea159b3c51669ccc722e89a",
        opens=datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC),
    ),
    CountingWindow(
        label="proc-v8",
        digest="sha256:70fee158526caa6870d43ace70c3781db39f644379c86c363538ebdefa57547c",
        opens=datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC),
    ),
    CountingWindow(
        label="proc-v8",
        digest="sha256:a9033e56819e775e561b802dec24bae437c17c751e5a7f5fa4b3eeb31383951f",
        opens=datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC),
    ),
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
      forecast the backlog re-owes. One stamped before it stays uncounted.

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
    for sibling in siblings():
        other = window_of(sibling)
        if other is None or other.opens >= window.opens:
            continue
        if other.revoked_at is None or process_version.stamped_at < other.revoked_at:
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
