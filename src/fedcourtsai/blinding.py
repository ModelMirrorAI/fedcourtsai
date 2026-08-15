"""Blinded prediction staging, so a grade is formed before the grader knows whose claim it is.

An evaluator that can see *which* predictor wrote a rationale anchors on it, and
`reasoning_quality` — the one number an evaluator authors rather than computes —
then partly measures the anchor. That number is not diagnostic-only: it is the
semantic side of the pre-registered judge-validation tau-b
(`metrics/claim-scores.json`), it feeds the leaderboard's
`mean_reasoning_quality`, and it is the stand-in for the semantic claim grades
until opinion ingestion lands. `docs/outcome-decomposition.md` states blinding as
the precondition on scoring semantic claims; it applies with equal force here.

Two pure, deterministic halves bracket the agent call:

1. :func:`provision_blinded_predictions` copies each predictor's latest
   prediction into ``record/blinded/<alias>/``, masking the identity fields and
   scrubbing identifying strings out of the prose and the transcript, and writes
   the alias map to a directory **outside** the case tree. ``record/`` is
   gitignored, so the staged copy rides the cell's artifact and is never
   committed.
2. :func:`unblind_evaluations` reads that map back, renames each
   ``evaluations/<evaluator>/<alias>/<run>/`` directory to the real predictor id,
   rewrites the ``predictor_id`` field inside each ``evaluation.json``, and
   resolves every alias the evaluator wrote into its prose, flags, and captured
   log — so nothing alias-keyed reaches the ledger or the run PR.

**Ordering.** Un-aliasing must run **before** ``stamp-cell --role evaluator``.
The stamp joins the evaluation to its prediction through
``predictions_dir.glob(f"{evaluation.predictor_id}/*/prediction.json")`` and
returns ``None`` on no match. The stamp assigns whatever that join produced, so
under an alias it *silently* writes no ``claim_scores`` block rather than
failing (the ``base_rate_salience_version`` is loud only where the evaluation
records a ``risk_set`` basis, whose null version fails the stamp). The
self-check is ``validate data``'s ``check_evaluation_targets``, which resolves
the same join and reports an orphan loudly — so an alias that survives to the
gate fails it rather than shipping.

**What this is, and what it is not.** It is an *anti-anchoring* measure enforced
by a prompt contract, not a sandbox. It removes every route by which identity
reaches the grader incidentally: no predictor id, evaluator id, engine name, or
model name survives in the staged bytes or in a staged filename, the alias order
is not the registry's order, and the map does not sit in the tree the grader is
told to open. It does not, and cannot, stop a grader that sets out to break it —
three routes stay open by construction, and the honest reading of any blinded
number depends on naming them:

- **The permutation is recomputable.** The shuffle is keyed on the run, case, and
  event — all three stated in the evaluator's own kickoff prompt — and this
  module is in the checkout the cell runs in. Deliberately re-deriving the
  mapping is a few lines. What the keying buys is that the alias is not the
  registry's sort order, so nothing is inverted by *accident* or by inspection.
- **The committed record is still on disk.** ``events/<event_id>/predictions/``
  names every predictor, and the checkout carries its history. The prompt
  forbids reading it; nothing prevents it.
- **The call-class profile is not masked, though the tool names are.** The
  staged ``calls`` keep everything the leakage grading reads, with each
  ``tool`` normalized to the engine-neutral classes below — each engine's raw
  vocabulary is disjoint from the others' while the registry holds one
  predictor per engine, so a raw name on the grader's required reading path
  would name the candidate. What the rename cannot hide is the *shape*: an
  engine that reads through its shell stages a log of nothing but ``shell``,
  which narrows the guessing space the way prose style does.
- **Style is not masked.** Three candidates over three known engines is a small
  guessing space, and an engine may recognise its own prose.

The first two routes run through a tool call, and tool calls are captured
harness-side into the cell's own ``retrieval_log.json`` — best-effort capture
(an unrecognized log yields ``[]`` and the record is head-truncated at 500
calls), reviewable by a maintainer, and checked by nothing automatically. So a
blinded grade should be read as "formed with the predictor's name removed",
never as "formed blind".
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from . import ids
from .paths import CasePaths, EventPaths
from .pricing import DEFAULT_MODELS, MODEL_RATES
from .registry import load_evaluators, load_predictors
from .schemas import EvaluatorConfig, PredictorConfig
from .serialize import write_raw_json, write_text

#: Alias directories are opaque and ordinal-free in meaning: ``candidate-a`` is
#: not "the first predictor" under any ordering a reader could invert.
ALIAS_PREFIX: Final = "candidate-"

#: The shape an alias may take, enforced on read as well as on write. The map is
#: a file on the runner, so its contents are treated as untrusted input: an alias
#: or a predictor id is joined into a path, and only a single safe component may
#: ever be.
_SAFE_COMPONENT: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_ALIAS_SHAPE: Final = re.compile(rf"{re.escape(ALIAS_PREFIX)}[a-z]+\Z")

#: Default home for the alias maps: **outside** the case tree the grader is told
#: to open. Relative, so it resolves against the working directory — at the repo
#: root that is the gitignored ``/.blinding/``. It is a default for local use,
#: not a contract: a workflow passes ``--map-dir`` explicitly, pointing at the
#: runner's own temp directory, so the key is not in the checkout at all.
DEFAULT_MAP_DIR: Final = Path(".blinding")

#: What a scrubbed identifying run is replaced with. Deliberately visible rather
#: than deleted, and shaped like the harness's other redaction marker
#: (``[redacted:rule]`` in ``retrieval_log.json``), so a grader reads a gap as
#: removed text rather than as a typo or as retrieved content.
IDENTITY_REDACTION: Final = "[redacted:identity]"

#: Engine, vendor, and model-family words scrubbed from every staged byte, on top
#: of the full identifiers :func:`identity_terms` reads from the registries and
#: the pricing tables. This list catches the *bare* family name a model uses when
#: it names itself in prose; the full identifiers catch the exact spellings.
#: Matched case-insensitively, and only where no letter or digit precedes and no
#: letter follows — so ``GPT5`` and ``claude-baseline`` match while ``Claudette``
#: does not. A rare false positive costs one redaction marker in prose, which is
#: the cheap side.
ENGINE_TERMS: Final[tuple[str, ...]] = (
    "anthropic",
    "claude",
    "codex",
    "fable",
    "gemini",
    "gpt",
    "haiku",
    "openai",
    "opus",
    "sonnet",
)

#: The prose documents are staged under **harness-chosen** names rather than the
#: names the prediction's pointers happen to carry, because a pointer is the
#: agent's own word and a filename is as identifying as its contents (a
#: ``claude-notes.md`` in the directory listing defeats the whole barrier). The
#: masked ``prediction.json``'s pointers are rewritten to these names, so the
#: contract "follow the pointer" still resolves.
STAGED_REASONING: Final = "reasoning.md"
STAGED_FORECAST: Final = "predicted_reasoning.md"

#: Copied under their own names. ``usage.json``, ``tooling.json``, ``flags.json``,
#: and ``attempt.json`` are **not** staged: dropping beats masking where a file's
#: content is free text a mask cannot make safe, and none of them is an input the
#: grade needs. The cost is real and named in the evaluate prompt — a predictor's
#: own leakage disclosure lives in its ``flags.json``, so the blinded grader sees
#: that disclosure only where the predictor also made it in prose.
FIXED_STAGED_FILES: Final[tuple[str, ...]] = ("retrieval.md", "retrieval_log.json")


class BlindingError(RuntimeError):
    """Blinded staging or un-aliasing cannot proceed correctly.

    Always raised rather than worked around. A degraded blinding ships an
    unmasked identity to the grader; a degraded un-aliasing ships alias-keyed
    evaluations into the ledger. Neither is recoverable after the fact.
    """


@dataclass(frozen=True)
class BlindedCandidate:
    """One staged candidate: its alias, the predictor behind it, and what was copied."""

    alias: str
    predictor_id: str
    source: Path
    staged: tuple[str, ...]


@dataclass(frozen=True)
class BlindingResult:
    """What one :func:`provision_blinded_predictions` call produced."""

    root: Path
    map_path: Path
    candidates: tuple[BlindedCandidate, ...]


# --- alias assignment ---------------------------------------------------------


def alias_for_index(index: int) -> str:
    """The ``index``-th alias name: ``candidate-a`` … ``candidate-z``, ``candidate-aa``, …

    Spreadsheet-column naming, so the scheme has no ceiling at 26 candidates and
    never has to renumber when one is added.
    """
    if index < 0:
        raise BlindingError(f"alias index must be non-negative, not {index}")
    letters = ""
    n = index
    while True:
        letters = chr(ord("a") + n % 26) + letters
        n = n // 26 - 1
        if n < 0:
            break
    return ALIAS_PREFIX + letters


def _shuffle_key(seed: str, predictor_id: str) -> str:
    """A keyed, deterministic sort key for one predictor under one cell's seed."""
    return hashlib.sha256(f"{seed}\x00{predictor_id}".encode()).hexdigest()


def assign_aliases(
    predictor_ids: Iterable[str], *, case_id: str, event_id: str, run_id: str
) -> dict[str, str]:
    """Alias → predictor id, under a keyed shuffle seeded on the cell's identity.

    **Not** predictor-id sort order. Ordering the candidates alphabetically would
    make the alias a lookup any reader performs by inspection — read the
    registry, sort, read off the mapping — so the order is a hash of the cell's
    identity joined with each predictor id. Deterministic, so the same cell
    always assigns the same aliases and a recovery run agrees with the original.

    Deterministic *and* keyed on public inputs, which is the honest limit: the
    seed's three parts are all in the evaluator's kickoff prompt, so this defeats
    inversion by inspection, not inversion by intent (see the module docstring).

    The seed carries the **case** as well as the run and the event, because a
    ``run_id`` is shared across a whole fan-out: seeded on the run and event
    alone, every case in a run would share one permutation.
    """
    seed = "\x00".join((run_id, case_id, event_id))
    ordered = sorted(predictor_ids, key=lambda pid: (_shuffle_key(seed, pid), pid))
    return {alias_for_index(i): pid for i, pid in enumerate(ordered)}


# --- scrubbing ----------------------------------------------------------------


def identity_terms(config_root: Path, *, extra: Iterable[str] = ()) -> tuple[str, ...]:
    """Every string the staged copy must not contain, longest first.

    Read from the sources of truth rather than restated, so a new engine, a
    ``model:`` override, or a re-priced model cannot leak by omission: every
    registered predictor and evaluator id, engine, and model (enabled or not — a
    disabled actor's id still names it), every value in
    :data:`fedcourtsai.pricing.DEFAULT_MODELS` and every key of ``MODEL_RATES``,
    the bare family words in :data:`ENGINE_TERMS`, and ``extra`` (the predictor
    directories actually present, so an id retired from the registry but still on
    disk is covered).

    Full identifiers are carried whole rather than split into components. A split
    would add terms like ``pro``, ``sol``, and ``code`` — all of which occur in
    ordinary legal prose (``pro se``, the U.S. Code), and scrubbing those would
    eat the substance the grade is formed from. Longest-first ordering is what
    makes the whole-identifier terms win: the alternation the pattern builds is
    leftmost-first per position, so ``claude-fable-5`` must be offered before
    ``claude`` or the model would be scrubbed in pieces and its tail left legible.
    """
    terms: set[str] = {*ENGINE_TERMS, *extra, *DEFAULT_MODELS.values(), *MODEL_RATES}
    actors: list[PredictorConfig | EvaluatorConfig] = [
        *load_predictors(config_root / "predictors.yaml"),
        *load_evaluators(config_root / "evaluators.yaml"),
    ]
    for entry in actors:
        terms.update({entry.id, str(entry.engine), entry.model or ""})
    return tuple(sorted((term for term in terms if term), key=lambda t: (-len(t), t)))


def scrub_pattern(terms: Sequence[str]) -> re.Pattern[str]:
    """A case-insensitive, boundary-anchored alternation over ``terms``.

    The boundaries are asymmetric on purpose. Nothing alphanumeric may *precede*
    a match, so a term that is the tail of a longer word does not fire; but only
    a **letter** may not follow, so a digit-suffixed self-reference — ``GPT5``,
    ``Claude4``, ``Gemini2.5``, which is exactly how a model spells its own name
    in prose — is caught. ``Claudette`` still does not match: the following ``t``
    blocks it.
    """
    if not terms:
        # An empty alternation would match everywhere; refuse rather than
        # silently scrub nothing under a pattern that looks like it works.
        raise BlindingError("cannot build a scrub pattern from an empty term set")
    body = "|".join(re.escape(term) for term in terms)
    return re.compile(rf"(?<![A-Za-z0-9])(?:{body})(?![A-Za-z])", re.IGNORECASE)


def scrub_text(text: str, pattern: re.Pattern[str]) -> str:
    """Replace every identifying run in ``text`` with :data:`IDENTITY_REDACTION`."""
    return pattern.sub(IDENTITY_REDACTION, text)


def scrub_json(value: Any, pattern: re.Pattern[str]) -> Any:
    """``scrub_text`` over every string in a decoded JSON document, keys included.

    Keys are scrubbed too. On a well-formed artifact every key is a schema field
    name and the pass is a no-op, but this module only checks that its input
    decodes to an object — the guarantee that keys are schema names belongs to
    ``validate``, not here, and a barrier should not rest on a check it does not
    perform. Non-string scalars pass through untouched.
    """
    if isinstance(value, str):
        return scrub_text(value, pattern)
    if isinstance(value, list):
        return [scrub_json(item, pattern) for item in value]
    if isinstance(value, dict):
        return {
            scrub_text(str(key), pattern): scrub_json(item, pattern) for key, item in value.items()
        }
    return value


# --- masking ------------------------------------------------------------------


def _relativize_snapshot(value: object) -> object:
    """Reduce ``input_snapshot`` to its final path component.

    The field is the agent's own word and each engine spells it differently — a
    repo-rooted ``data/cases/<court>/<docket>/record/snapshots/<day>.json``, a
    ``record/``-relative path, or a bare filename. The spelling is a stylistic
    fingerprint and the leading path merely restates the case the grader already
    knows, so all of them collapse to the filename (both separators, since the
    agent chose the spelling). A non-path sentinel (``missing``, ``none``) has no
    separator and passes through unchanged — that residue is not maskable without
    destroying the field's meaning, and it is style rather than identity.
    """
    if not isinstance(value, str):
        return value
    return value.replace("\\", "/").rsplit("/", 1)[-1]


def mask_prediction(
    payload: Mapping[str, Any],
    *,
    alias: str,
    pattern: re.Pattern[str],
    staged_prose: Mapping[str, str],
) -> dict[str, Any]:
    """The blinded view of one ``prediction.json``.

    ``predictor_id`` becomes the alias; ``engine`` and ``model`` become null;
    ``process_version`` is dropped entirely (its digest is a per-predictor
    fingerprint — the resolved engine, model, and prompt hashed together — so it
    identifies the candidate, and it is no input to a grade); ``input_snapshot``
    is relativized. ``staged_prose`` maps each pointer field to the harness-chosen
    name the document was actually staged under, and a pointer whose document was
    **not** staged is dropped rather than left naming a file the grader will not
    find — a dangling pointer would read as a broken cell rather than an absent
    document.

    Every other field is carried through with only the identity scrub applied:
    the probability, the disposition, the votes, the claims, the
    ``semantic_claims`` propositions a merits cell carries, and the frozen
    ``context`` the base-rate lookup needs. The scrub reaches strings anywhere in
    the document, so a rationale string inside ``claims`` — or a semantic
    proposition, which is free text the predictor wrote — can carry a
    ``[redacted:identity]`` marker; the numeric fields a grade is computed from
    cannot be touched by it.

    The result is deliberately **not** a schema-valid :class:`Prediction`: a
    ``Prediction`` requires an ``engine``. That is a property worth keeping — a
    staged copy can never be mistaken for, or committed as, a real prediction,
    because it would fail the gate on sight.
    """
    masked = scrub_json(dict(payload), pattern)
    if not isinstance(masked, dict):  # pragma: no cover - a JSON object by construction
        raise BlindingError("prediction.json does not decode to a JSON object")
    masked.pop("process_version", None)
    # Assigned after the scrub so the pattern cannot eat what the harness chose.
    masked["predictor_id"] = alias
    masked["engine"] = None
    masked["model"] = None
    for field in ("reasoning_doc", "predicted_reasoning_doc"):
        staged = staged_prose.get(field)
        if staged is not None:
            masked[field] = staged
        else:
            masked.pop(field, None)
    if "input_snapshot" in payload:
        masked["input_snapshot"] = _relativize_snapshot(payload["input_snapshot"])
    return masked


# Each engine logs its own tool vocabulary and the vocabularies are disjoint,
# so on the staged copy a raw name is an engine fingerprint. The classes keep
# what the leakage grading distinguishes — whether a call reached the shell,
# the local tree, the web, or an MCP surface — and MCP names keep their
# server and method (the outcome-bearing detail), spelled one way for every
# engine. The map includes the payload-TYPE names the capture falls back to
# where a provider-side call carries no tool name (``web_search_call``,
# ``local_shell_call`` — see ``retrieval._tool_name``'s callers): the hosted
# web search is exactly the row the leakage doctrine singles out, so it must
# stage as ``web-search``, not vanish into ``other``. Anything outside the
# map collapses to "other": pass-through would leak whatever engine-specific
# name the map has not met. The MCP server segment is ``[a-z0-9]+`` because
# the registry schema constrains server ids to exactly that — an underscore
# in a server id would make the two engines' spellings normalize differently
# and the surviving separator would fingerprint the engine; the schema's
# ``id`` rule is the guarantee this class depends on, as ``tool_usage``'s
# twin regex already records. Neutrality of the ``mcp:`` class itself rests
# on the registry giving every predictor the same server set — a
# per-predictor server would name its candidate straight through this seam.
_MCP_TOOL: Final = re.compile(r"^mcp_{1,2}([a-z0-9]+)_{1,2}(.+)$")
_NEUTRAL_TOOL_CLASSES: Final[dict[str, str]] = {
    "bash": "shell",
    "exec": "shell",
    "local_shell_call": "shell",
    "run_shell_command": "shell",
    "read": "file-read",
    "read_file": "file-read",
    "read_many_files": "file-read",
    "apply_patch": "file-write",
    "write": "file-write",
    "edit": "file-write",
    "write_file": "file-write",
    "replace": "file-write",
    "glob": "file-search",
    "grep": "file-search",
    "grep_search": "file-search",
    "list_directory": "file-search",
    "search_file_content": "file-search",
    "websearch": "web-search",
    "google_web_search": "web-search",
    "web_search": "web-search",
    "web_search_call": "web-search",
    "webfetch": "web-fetch",
    "web_fetch": "web-fetch",
}


def neutral_tool_class(tool: str) -> str:
    """The engine-neutral class a staged call's ``tool`` name is spelled as."""
    lowered = tool.lower()
    mcp = _MCP_TOOL.match(lowered)
    if mcp:
        return f"mcp:{mcp.group(1)}:{mcp.group(2)}"
    return _NEUTRAL_TOOL_CLASSES.get(lowered, "other")


def mask_retrieval_log(
    payload: Mapping[str, Any], *, alias: str, pattern: re.Pattern[str]
) -> dict[str, Any]:
    """The blinded view of one ``retrieval_log.json``.

    ``actor_id`` becomes the alias and ``engine`` becomes null; every captured
    string is scrubbed, because a query slice routinely quotes the cell's own
    output path (``predictions/<predictor_id>/…``). ``mode`` and the call list
    survive — the leakage grading is keyed on the first and reads the second, and
    a blinded log the grader cannot grade would trade one contract for another —
    but each call's ``tool`` is respelled as its engine-neutral class
    (:func:`neutral_tool_class`): the raw vocabularies are disjoint per engine,
    so a raw name would identify the candidate on the grader's own required
    reading path. The query slice and ``retrieved_doc_date`` pass through
    untouched.
    """
    masked = scrub_json(dict(payload), pattern)
    if not isinstance(masked, dict):  # pragma: no cover - a JSON object by construction
        raise BlindingError("retrieval_log.json does not decode to a JSON object")
    masked["actor_id"] = alias
    masked["engine"] = None
    calls = masked.get("calls")
    if isinstance(calls, list):
        for call in calls:
            if isinstance(call, dict) and isinstance(call.get("tool"), str):
                call["tool"] = neutral_tool_class(call["tool"])
    return masked


# --- staging ------------------------------------------------------------------


def _read_json(path: Path) -> dict[str, Any]:
    try:
        decoded = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise BlindingError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise BlindingError(f"{path} does not decode to a JSON object")
    return decoded


def _plain_filename(pointer: str, source: Path) -> str:
    """A prose pointer, confirmed to name a file in the prediction's own directory.

    The same rule ``validate``'s ``check_prediction_docs`` enforces on the
    committed record, re-checked here because this one *reads* a pointer the
    agent wrote: one carrying a separator or ``..`` would reach outside the cell.
    """
    if not pointer or "/" in pointer or "\\" in pointer or pointer in {".", ".."}:
        raise BlindingError(f"{source}: prose pointer {pointer!r} is not a plain filename")
    return pointer


def _cell_clock(directory: Path) -> datetime:
    """The prediction's harness clock, or the epoch when unreadable.

    The tolerant mirror of :func:`fedcourtsai.integrity.cell_clock` — the
    process stamp, else ``created_at`` — over the raw payload, because this
    runs pre-agent on whatever bytes are committed and must not crash the
    staging step on a malformed file. Parsed (never compared as strings) so a
    ``Z`` suffix and a ``+00:00`` offset order identically, and normalized
    aware so writers' clocks always compare.
    """
    try:
        payload = json.loads((directory / "prediction.json").read_text())
    except (OSError, ValueError):
        return _EPOCH
    process = payload.get("process_version")
    stamp = process.get("stamped_at") if isinstance(process, dict) else None
    raw = stamp if isinstance(stamp, str) else payload.get("created_at")
    if not isinstance(raw, str):
        return _EPOCH
    try:
        clock = datetime.fromisoformat(raw)
    except ValueError:
        return _EPOCH
    return clock if clock.tzinfo is not None else clock.replace(tzinfo=UTC)


# Sorts an unreadable prediction before every readable one, without crashing.
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def latest_prediction_dirs(event_paths: EventPaths) -> dict[str, Path]:
    """Each predictor's latest prediction run directory for the event.

    One alias means one candidate, so a predictor that ran the event more than
    once contributes its newest cell and no other. "Newest" is the **first**
    maximum of the harness clock (the process stamp, else ``created_at`` —
    :func:`fedcourtsai.integrity.cell_clock`) over the run directories in name
    order — which is
    exactly the stratified join's rule over path-sorted runs — the harness
    clock — the rule every
    downstream join already uses
    (:func:`fedcourtsai.store.iter_stratified_evaluations`, and the stamp's
    ``claim_scores`` and base-rate-version lookups). It has to be that rule down
    to the tiebreak: if the grader read one run while the harness scored the
    evaluation's claims against another, the two halves of a cell would describe
    different predictions and nothing would say so.
    """
    root = event_paths.predictions_dir
    if not root.is_dir():
        return {}
    latest: dict[str, Path] = {}
    for predictor_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        runs = sorted(r for r in predictor_dir.iterdir() if (r / "prediction.json").is_file())
        if runs:
            latest[predictor_dir.name] = max(runs, key=_cell_clock)
    return latest


def _stage_candidate(
    *, source: Path, dest: Path, alias: str, pattern: re.Pattern[str]
) -> tuple[str, ...]:
    """Copy one prediction's blinded view into ``dest``; return the filenames written."""
    prediction = _read_json(source / "prediction.json")
    written: list[str] = ["prediction.json"]

    # Pointer in, harness-chosen name out, so no agent-chosen filename reaches the
    # directory listing. The prose is staged first because the masked pointers
    # have to name what is actually there: `mask_prediction` is told what landed.
    pointers = [
        ("reasoning_doc", prediction.get("reasoning_doc") or STAGED_REASONING, STAGED_REASONING)
    ]
    forecast = prediction.get("predicted_reasoning_doc")
    if isinstance(forecast, str) and forecast:
        pointers.append(("predicted_reasoning_doc", forecast, STAGED_FORECAST))
    staged_prose: dict[str, str] = {}
    for field, pointer, staged_name in pointers:
        path = source / _plain_filename(str(pointer), source)
        if path.is_file():
            write_text(dest / staged_name, scrub_text(path.read_text(), pattern))
            staged_prose[field] = staged_name
            written.append(staged_name)

    write_raw_json(
        dest / "prediction.json",
        mask_prediction(prediction, alias=alias, pattern=pattern, staged_prose=staged_prose),
    )

    for name in FIXED_STAGED_FILES:
        path = source / name
        if not path.is_file():
            continue
        if name.endswith(".json"):
            write_raw_json(
                dest / name, mask_retrieval_log(_read_json(path), alias=alias, pattern=pattern)
            )
        else:
            write_text(dest / name, scrub_text(path.read_text(), pattern))
        written.append(name)
    return tuple(sorted(written))


def map_path_for(map_dir: Path, *, court: str, docket: int, event_id: str, run_id: str) -> Path:
    """Where one cell's alias map lives — outside the case tree, by construction.

    The map is the one file that undoes the blinding, so it does not go where the
    grader is sent: the prompt has the evaluator list ``record/blinded/``, and a
    map beside it would be found by an ``ls`` that nobody had to intend. Keeping
    it in its own directory makes accidental exposure impossible; a grader with a
    shell can still go looking, which the module docstring states plainly.

    The name is legible rather than hashed, so a maintainer recovering a run can
    tell which cell a map belongs to; every component is sanitized because it is
    joined into a path.
    """
    slug = "-".join((court, str(docket), event_id, run_id))
    return map_dir / f"{re.sub(r'[^A-Za-z0-9._-]', '_', slug)}.json"


def provision_blinded_predictions(
    *,
    data_root: Path,
    config_root: Path,
    court: str,
    docket: int,
    event_id: str,
    run_id: str,
    map_dir: Path = DEFAULT_MAP_DIR,
) -> BlindingResult:
    """Stage every predictor's latest prediction under an opaque alias.

    Writes ``record/blinded/<alias>/`` per candidate, and the alias map into
    ``map_dir`` (outside the case tree — see :func:`map_path_for`). ``record/`` is
    gitignored, so the staging area rides the evaluate cell's uploaded artifact
    and the ``collect`` job never ``git add``s it.

    The staging area holds exactly **one** cell's candidates: it is rewritten from
    scratch each call, so a re-run never leaves a stale candidate behind for the
    grader to score twice, and a second event on the same case replaces the first
    rather than joining it. The map records which cell it is for and
    :func:`read_blinding_map` refuses a map minted for another, so a clobber is a
    hard failure rather than a mis-key.

    Raises :class:`BlindingError` when the event carries no prediction at all: an
    evaluate cell with nothing to score is a matrix fault, and handing the grader
    an empty directory would have it write an empty cell instead of failing.
    """
    case_paths = CasePaths(data_root, court, docket)
    event_paths = case_paths.event(event_id)
    sources = latest_prediction_dirs(event_paths)
    if not sources:
        raise BlindingError(
            f"no prediction to blind for {ids.case_id(court, docket)} {event_id}: "
            "an evaluate cell was scheduled for an event with nothing to score"
        )

    aliases = assign_aliases(
        sources, case_id=ids.case_id(court, docket), event_id=event_id, run_id=run_id
    )
    pattern = scrub_pattern(identity_terms(config_root, extra=sources))

    root = case_paths.blinded_predictions
    # `court`/`docket` reach here from a caller's arguments and compose a delete
    # target; confirm it is the path it is supposed to be before removing it.
    cases_root = (data_root / "cases").resolve()
    if not root.resolve().is_relative_to(cases_root):
        raise BlindingError(f"refusing to stage outside {cases_root}: {root}")
    if root.exists():
        shutil.rmtree(root)
    candidates = tuple(
        BlindedCandidate(
            alias=alias,
            predictor_id=predictor_id,
            source=sources[predictor_id],
            staged=_stage_candidate(
                source=sources[predictor_id],
                dest=case_paths.blinded_prediction_dir(alias),
                alias=alias,
                pattern=pattern,
            ),
        )
        for alias, predictor_id in aliases.items()
    )
    map_path = map_path_for(map_dir, court=court, docket=docket, event_id=event_id, run_id=run_id)
    write_raw_json(
        map_path,
        {
            "case_id": ids.case_id(court, docket),
            "event_id": event_id,
            "run_id": run_id,
            "aliases": dict(aliases),
        },
    )
    return BlindingResult(root=root, map_path=map_path, candidates=candidates)


# --- un-aliasing --------------------------------------------------------------


def read_blinding_map(
    map_path: Path, *, case_id: str, event_id: str, run_id: str
) -> dict[str, str]:
    """The alias → predictor mapping for this cell, or a hard failure.

    Every gap is fatal: a missing map, a map that does not parse, a map whose
    ``aliases`` block is the wrong shape, and a map minted for a different case,
    event, or run. The last is the one worth spelling out — a stale map left by an
    earlier cell on a reused checkout would re-key this cell's evaluations onto
    another cell's candidates, which is worse than not un-aliasing at all.

    Both sides of every entry are shape-checked, because both are joined into a
    path and the file sits on a runner an agent has a shell on. An alias must look
    like an alias and a predictor id must be a single safe path component; a
    ``..`` on either side would rename a cell out of its own lane.
    """
    if not map_path.is_file():
        raise BlindingError(f"no blinding map at {map_path}: the cell was never blinded")
    try:
        payload = json.loads(map_path.read_text())
    except (OSError, ValueError) as exc:
        raise BlindingError(f"blinding map {map_path} is not readable JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise BlindingError(f"blinding map {map_path} does not decode to a JSON object")
    for field, expected in (("case_id", case_id), ("event_id", event_id), ("run_id", run_id)):
        found = payload.get(field)
        if found != expected:
            raise BlindingError(
                f"blinding map {map_path} is for {field} {found!r}, not {expected!r}"
            )
    aliases = payload.get("aliases")
    if not isinstance(aliases, dict) or not aliases:
        raise BlindingError(f"blinding map {map_path} carries no usable `aliases` block")
    resolved: dict[str, str] = {}
    for alias, predictor_id in aliases.items():
        if not isinstance(alias, str) or not _ALIAS_SHAPE.match(alias):
            raise BlindingError(f"blinding map {map_path}: {alias!r} is not an alias")
        if not isinstance(predictor_id, str) or not _SAFE_COMPONENT.match(predictor_id):
            raise BlindingError(
                f"blinding map {map_path}: {predictor_id!r} is not a single path component"
            )
        resolved[alias] = predictor_id
    return resolved


def _alias_resolver(aliases: Mapping[str, str]) -> re.Pattern[str]:
    """A boundary-anchored alternation over the cell's alias names, longest first.

    Case-insensitive like the blinding-direction resolver above (the aliases
    are handed out lowercase, but a judge writing prose capitalizes a
    sentence-initial ``Candidate-a``, and an alias that survives un-aliasing
    ships unresolvable to the maintainer in the run PR's flag roll-up — the
    one channel whose key is thrown away with the runner). The right boundary
    is deliberately tighter than that resolver's: a digit after the token
    (``candidate-a1``) proves it is not the alias, so it must not resolve.
    The non-capturing group is load-bearing — ``|`` binds loosest, so without
    it the lookbehind would anchor only the first alternative and the
    lookahead only the last, leaving every middle alias unbounded.
    """
    body = "|".join(re.escape(alias) for alias in sorted(aliases, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9])(?:{body})(?![A-Za-z0-9])", re.IGNORECASE)


def _resolve_aliases_in_tree(root: Path, aliases: Mapping[str, str]) -> None:
    """Rewrite every alias the evaluator wrote under ``root`` to its real predictor id.

    Renaming the directories is not enough. An evaluator names the candidate in
    prose it was told to write — ``evaluation.md``, ``leakage.notes``, and above
    all a ``flags.json`` note on a leakage finding, which the ``collect`` job
    rolls into the run PR and the Actions summary. That note ships to a
    maintainer, and the only key that would resolve it is thrown away with the
    runner. So the alias is resolved everywhere it was written, not only where it
    was a path.

    **Only a file that actually changes is rewritten.** Re-emitting an unchanged
    file is not a no-op here: this writes through the repo's canonical
    serializers, and an agent-written JSON does not match their formatting, so a
    touch-everything pass would reformat files this cell never wrote. Those land
    in the ``collect`` job's diff as modifications, and the append-only path jail
    rejects any non-addition — silently costing the whole run its auto-merge.

    Safe because the ``candidate-`` namespace is reserved to this module — nothing
    else in a cell's output can carry one — and idempotent, since a resolved file
    holds no alias for a second pass to find.
    """
    if not root.is_dir():
        return
    resolver = _alias_resolver(aliases)

    # Lowered once: the resolver matches case-insensitively, the map's keys
    # are the lowercase forms it handed out, and a lookup miss must stay
    # impossible whatever case a key arrives in.
    lowered = {alias.lower(): predictor for alias, predictor in aliases.items()}

    def _sub(text: str) -> str:
        return resolver.sub(lambda m: lowered[m.group(0).lower()], text)

    def _walk(value: Any) -> Any:
        if isinstance(value, str):
            return _sub(value)
        if isinstance(value, list):
            return [_walk(item) for item in value]
        if isinstance(value, dict):
            return {_sub(str(key)): _walk(item) for key, item in value.items()}
        return value

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if not resolver.search(text):
            continue
        if path.suffix == ".json":
            try:
                decoded = json.loads(text)
            except ValueError as exc:
                raise BlindingError(f"{path} is not readable JSON: {exc}") from exc
            write_raw_json(path, _walk(decoded))
        else:
            write_text(path, _sub(text))


def unblind_evaluations(
    *,
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    evaluator_id: str,
    run_id: str,
    map_dir: Path = DEFAULT_MAP_DIR,
) -> tuple[tuple[str, str], ...]:
    """Rename each alias-keyed evaluation onto its real predictor, and resolve the aliases.

    Moves ``evaluations/<evaluator>/<alias>/<run>/`` to
    ``evaluations/<evaluator>/<predictor_id>/<run>/``, rewrites ``predictor_id``
    inside each ``evaluation.json``, and resolves every alias the evaluator wrote
    into its prose, flags, tooling report, and captured log
    (:func:`_resolve_aliases_in_tree`). Returns the ``(alias, predictor_id)``
    pairs it moved, in alias order.

    **Runs before ``stamp-cell --role evaluator``.** The stamp joins an
    evaluation to its prediction on the ``predictor_id`` field and returns
    ``None`` on no match, so an alias reaching the stamp costs the cell its
    ``claim_scores`` block silently rather than loudly (a ``risk_set`` basis
    left without its ``base_rate_salience_version`` does fail the stamp, but
    only on that basis). ``validate data``'s
    ``check_evaluation_targets`` is the backstop for the same join, and it does
    fail loudly — so the order is: un-alias, stamp, validate.

    Idempotent: a second call over an already-un-aliased cell finds no alias
    directories and returns nothing. Every other anomaly is fatal, and each is
    checked *before* anything moves — an alias directory carrying no
    ``evaluation.json``, a destination that already exists, a destination outside
    the event's own tree, a file that does not parse, or any alias-shaped
    directory left under the evaluator after the sweep. A half-applied rename
    would leave a cell that a retry then sweeps clean and calls a success, which
    for a step whose contract is "hard-fail rather than degrade" is the one
    outcome that must not be reachable.
    """
    case_paths = CasePaths(data_root, court, docket)
    event_paths = case_paths.event(event_id)
    aliases = read_blinding_map(
        map_path_for(map_dir, court=court, docket=docket, event_id=event_id, run_id=run_id),
        case_id=ids.case_id(court, docket),
        event_id=event_id,
        run_id=run_id,
    )

    planned: list[tuple[str, str, Path, Path]] = []
    base = event_paths.base.resolve()
    for alias in sorted(aliases):
        predictor_id = aliases[alias]
        source = event_paths.evaluation_dir(evaluator_id, alias, run_id)
        if not source.is_dir():
            continue
        if not (source / "evaluation.json").is_file():
            raise BlindingError(f"{source} carries no evaluation.json to un-alias")
        dest = event_paths.evaluation_dir(evaluator_id, predictor_id, run_id)
        if dest.exists():
            raise BlindingError(
                f"cannot un-alias {source} onto {dest}: the destination already exists"
            )
        if not dest.resolve().parent.is_relative_to(base):
            raise BlindingError(f"refusing to un-alias {source} outside {base}: {dest}")
        planned.append((alias, predictor_id, source, dest))

    for _, predictor_id, source, dest in planned:
        dest.parent.mkdir(parents=True, exist_ok=True)
        source.rename(dest)
        # The alias level above is now empty unless the evaluator wrote outside
        # its run; leaving a stray one would trip the sweep below, which is
        # exactly the intent.
        if not any(source.parent.iterdir()):
            source.parent.rmdir()
        payload = _read_json(dest / "evaluation.json")
        payload["predictor_id"] = predictor_id
        write_raw_json(dest / "evaluation.json", payload)

    # Only what *this* cell produced — the destinations just moved, plus the
    # evaluator's own run-keyed files (its `flags.json`, `tooling.json`,
    # `retrieval.md`, and captured log). Scoping matters as much here as it does
    # for an agent: the evaluator directory also holds every earlier committed
    # run for this event, and the harness has no more business rewriting those
    # than a cell has writing outside its lane.
    for _, _, _, dest in planned:
        _resolve_aliases_in_tree(dest, aliases)
    _resolve_aliases_in_tree(event_paths.evaluation_cell_dir(evaluator_id, run_id), aliases)
    _assert_no_alias_survives(event_paths.evaluator_dir(evaluator_id))
    return tuple((alias, predictor_id) for alias, predictor_id, _, _ in planned)


def _assert_no_alias_survives(evaluator_dir: Path) -> None:
    """Fail if any alias-shaped directory is left under the evaluator.

    Catches the case the map cannot: an evaluator that invented an alias it was
    never given, or wrote one under a run id other than its own. Either way the
    directory would reach the ledger keyed on a name no predictor answers to.
    """
    if not evaluator_dir.is_dir():
        return
    stray = sorted(
        child.name
        for child in evaluator_dir.iterdir()
        if child.is_dir() and child.name.lower().startswith(ALIAS_PREFIX)
    )
    if stray:
        raise BlindingError(
            f"alias directories survive un-aliasing under {evaluator_dir}: {', '.join(stray)}"
        )
