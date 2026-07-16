"""Engine-runner seam: produce a predict/evaluate cell's artifacts behind an interface.

The live ``run-predict`` / ``run-evaluate`` workflows hand one matrix cell to a
coding agent (``claude-code-action`` or the Codex equivalent), which reasons over
the snapshot and writes the cell's artifacts at the canonical paths. That agent
call costs tokens and only runs inside Actions, so the cell *mechanics* — where
output lands, that it is schema-valid, that ``validate`` accepts it — cannot be
exercised in pytest or locally.

This module is the seam that makes those mechanics testable, mirroring the
:mod:`fedcourtsai.backtest` ``Backtester`` seam (where ``ConstantBacktester`` /
``PriorVoteBacktester`` are offline reference engines). A :class:`Runner` takes
the cell inputs — court, docket, event, the acting predictor/evaluator id, the
run id, the role, the prompt template, and the output root — and is responsible
for writing that cell's artifacts at the paths :mod:`fedcourtsai.ids` /
:mod:`fedcourtsai.paths` resolve. The agentic engines target the same seam in the
workflow; the offline :class:`StubRunner` here writes deterministic, schema-valid
canned artifacts with no model call and no network, so its output is byte-stable
and identical in *shape* to what the workflow produces.

Three families of backend target this seam. The offline :class:`StubRunner` is the
fast reference used in tests and ``local-cascade --engine stub``. The agentic
:class:`ClaudeCodeRunner` / :class:`CodexRunner` / :class:`GeminiRunner` drive the
*real* headless agents (``claude`` / ``codex`` / ``gemini``) over the identical
cell contract — the same inline-identifier kickoff prompt and env vars, the same
registry prompt template, the same output paths the live workflows use — so
``local-cascade`` and the cert back-test can exercise a real engine end-to-end
exactly as CI would. The live workflows still invoke their engine through the CLI
directly (or an action wrapper); these backends are the library mirror of that,
not a replacement for it.

The third is the offline :class:`ReplayRunner`: it emits a *captured real cell's*
prediction from a committed cassette instead of calling a model. The stub's output
is intentionally trivial (the ``denied``/0.0 floor), so it cannot catch a bug in the
code that *consumes* realistic agent output — the scoring metrics, the leaderboard
roll-up. Replay closes that gap: a recorded prediction carries a real calibrated
probability and panel votes, so an evaluate cell run over it computes a non-degenerate
Brier score and vote accuracy, and the leaderboard rolls up real numbers — all
offline and token-free. It reuses the stub's evaluate path (the deterministic
scoring is exactly the consume path under test); only the prediction is replayed.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from ..config import get_settings
from ..ids import case_id as make_case_id
from ..ids import parse_run_id
from ..paths import CasePaths, EventPaths
from ..pricing import DEFAULT_MODELS
from ..schemas import Disposition, Engine, Evaluation, Outcome, Prediction, UsageRole
from ..serialize import read_model, write_json
from .evaluate import brier_score, is_correct, vote_accuracy

# Canned values the stub reports. Deterministic by construction — no clock, no
# randomness — so the same request always produces byte-identical artifacts. The
# disposition is the trivial floor (`denied`/0.0), the same baseline
# `ConstantBacktester` uses, so the stub commits to nothing it could be "right"
# about by luck.
_STUB_DISPOSITION = Disposition.denied
_STUB_PROBABILITY = 0.0
_STUB_GRANTED = 0
_STUB_REASONING_QUALITY = 0.5
# A canned mid-scale stakes read, so the stub's prediction carries the same
# optional field a real predictor emits (exercised by the cert back-test's
# big-case capture); a fixed value, like the reasoning-quality floor.
_STUB_BIG_CASE_SCORE = 0.5


@dataclass(frozen=True)
class RunRequest:
    """The inputs one predict/evaluate cell receives, role-tagged.

    These are exactly what the workflow passes a cell: the case (``court_id`` /
    ``docket_id``) and ``event_id`` to act on, the acting ``actor_id`` (the
    ``predictor_id`` for a predict cell, the ``evaluator_id`` for an evaluate
    cell), the shared ``run_id``, the ``role`` that selects which artifacts to
    produce, the ``prompt`` template the live engine would follow, and the
    ``data_root`` output root the artifacts are written under.

    ``prompt`` is carried for parity with the live engine (which reads it) even
    though the stub does not consult it; it is part of the cell contract.

    ``decided_before`` is the back-test replay clock: set only when a decided
    case is replayed as of a past moment (the cert back-test's engine replay),
    it is exported to the cell as ``DECIDED_BEFORE`` so the agent's corpus
    retrieval masks history from that year on. Live cells never set it.
    """

    role: UsageRole
    court_id: str
    docket_id: int
    event_id: str
    actor_id: str
    run_id: str
    prompt: Path
    data_root: Path
    decided_before: int | None = None

    @property
    def case_id(self) -> str:
        return make_case_id(self.court_id, self.docket_id)

    @property
    def event_paths(self) -> EventPaths:
        return CasePaths(self.data_root, self.court_id, self.docket_id).event(self.event_id)


class Runner(Protocol):
    """An engine that produces one cell's artifacts at the canonical paths.

    The same seam the agentic engines target in the workflow: given a
    :class:`RunRequest`, write the cell's artifacts (a prediction pair for a
    predict cell, an evaluation pair per scored predictor for an evaluate cell)
    and return the paths written, in sorted order.
    """

    @property
    def backend(self) -> str: ...

    def run(self, request: RunRequest) -> list[Path]: ...


def _created_at(run_id: str) -> datetime:
    """The cell's ``created_at``, derived from the run id so the stub has no clock.

    Run ids are UTC timestamps (:func:`fedcourtsai.ids.run_id`), so reusing the
    run id's instant keeps the stub a pure function of its request.
    """
    return parse_run_id(run_id)


def _input_snapshot(request: RunRequest) -> str:
    """The canonical snapshot path the cell would have read, as a stable string.

    The workflow provisions a case's latest corpus snapshot under ``record/`` and
    the predictor reads it; the stub names that same path (dated from the run id)
    so its ``input_snapshot`` matches the shape of a real prediction. Rendered
    relative to the data root's parent (typically repo-relative, e.g.
    ``data/cases/...``) when possible, else as an absolute path.
    """
    case = CasePaths(request.data_root, request.court_id, request.docket_id)
    snapshot = case.snapshot(_created_at(request.run_id).date().isoformat())
    try:
        return snapshot.relative_to(request.data_root.parent).as_posix()
    except ValueError:
        return snapshot.as_posix()


def _write_text(path: Path, text: str) -> None:
    """Write a newline-terminated markdown note, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n")


@dataclass(frozen=True)
class StubRunner:
    """Offline reference engine: writes deterministic, schema-valid canned artifacts.

    The runner counterpart to ``ConstantBacktester`` — no model call, no network,
    fully determined by the request. A predict cell yields ``prediction.json`` +
    ``reasoning.md``; an evaluate cell scores every predictor that produced a
    prediction for the event and yields an ``evaluation.json`` + ``evaluation.md``
    pair each, with the quantitative fields computed by the same
    :mod:`fedcourtsai.pipeline.evaluate` helpers the live evaluator must match.
    Output is byte-stable and identical in shape to what the workflow commits, so
    ``validate`` accepts it.
    """

    backend: str = "stub"
    engine: Engine = Engine.claude_code

    def run(self, request: RunRequest) -> list[Path]:
        if request.role == UsageRole.predictor:
            return self._predict(request)
        return self._evaluate(request)

    def _predict(self, request: RunRequest) -> list[Path]:
        events = request.event_paths
        prediction = Prediction(
            case_id=request.case_id,
            event_id=request.event_id,
            predictor_id=request.actor_id,
            engine=self.engine,
            run_id=request.run_id,
            created_at=_created_at(request.run_id),
            input_snapshot=_input_snapshot(request),
            granted=_STUB_GRANTED,
            probability=_STUB_PROBABILITY,
            predicted_disposition=_STUB_DISPOSITION,
            big_case_score=_STUB_BIG_CASE_SCORE,
        )
        json_path = events.prediction(request.actor_id, request.run_id)
        md_path = events.reasoning(request.actor_id, request.run_id)
        write_json(json_path, prediction)
        _write_text(md_path, self._reasoning_md(request))
        return sorted([json_path, md_path])

    def _evaluate(self, request: RunRequest) -> list[Path]:
        events = request.event_paths
        if not events.outcome.is_file():
            # Nothing to score until the event resolves; mirrors the prompt's
            # "if there is no outcome.json, there is nothing to evaluate".
            return []
        outcome = read_model(events.outcome, Outcome)
        written: list[Path] = []
        for predictor_id, prediction in self._latest_predictions(events):
            evaluation = Evaluation(
                case_id=request.case_id,
                event_id=request.event_id,
                predictor_id=predictor_id,
                evaluator_id=request.actor_id,
                engine=self.engine,
                run_id=request.run_id,
                created_at=_created_at(request.run_id),
                correct=is_correct(prediction, outcome),
                brier_score=brier_score(prediction, outcome),
                vote_accuracy=vote_accuracy(prediction, outcome),
                reasoning_quality=_STUB_REASONING_QUALITY,
            )
            dir_ = events.evaluation_dir(request.actor_id, predictor_id, request.run_id)
            json_path = events.evaluation(request.actor_id, predictor_id, request.run_id)
            write_json(json_path, evaluation)
            _write_text(dir_ / "evaluation.md", self._evaluation_md(request, predictor_id))
            written.extend([json_path, dir_ / "evaluation.md"])
        return sorted(written)

    @staticmethod
    def _latest_predictions(events: EventPaths) -> list[tuple[str, Prediction]]:
        """Each predictor's latest prediction for the event, in predictor-id order.

        One evaluate cell scores every predictor once (the
        ``evaluations/<evaluator>/<predictor>/<run>`` layout has no slot for a
        predictor's run id), so where a predictor has several runs the stub scores
        its most recent — the largest ``run_id``, which sorts chronologically.
        """
        predictions_root = events.base / "predictions"
        if not predictions_root.is_dir():
            return []
        scored: list[tuple[str, Prediction]] = []
        for predictor_dir in sorted(p for p in predictions_root.iterdir() if p.is_dir()):
            runs = sorted(
                run_dir
                for run_dir in predictor_dir.iterdir()
                if (run_dir / "prediction.json").is_file()
            )
            if not runs:
                continue
            prediction = read_model(runs[-1] / "prediction.json", Prediction)
            scored.append((predictor_dir.name, prediction))
        return scored

    def _reasoning_md(self, request: RunRequest) -> str:
        return (
            f"# Stub prediction for {request.event_id}\n\n"
            f"Deterministic offline stub output for case `{request.case_id}`, "
            f"predictor `{request.actor_id}`, run `{request.run_id}`. No model was "
            "called and no facts were read; the prediction is the trivial "
            f"`{_STUB_DISPOSITION.value}` floor with P(granted) "
            f"{_STUB_PROBABILITY:.1f}. This document stands in for a real "
            "predictor's qualitative analysis so the cell mechanics can be "
            "exercised offline.\n"
        )

    def _evaluation_md(self, request: RunRequest, predictor_id: str) -> str:
        return (
            f"# Stub evaluation of {predictor_id} for {request.event_id}\n\n"
            f"Deterministic offline stub scoring for case `{request.case_id}`, "
            f"evaluator `{request.actor_id}`, run `{request.run_id}`. The "
            "quantitative fields are computed in code from the prediction and the "
            "realized outcome; the reasoning-quality score is a fixed canned value "
            f"({_STUB_REASONING_QUALITY:.1f}). This document stands in for a real "
            "evaluator's qualitative write-up so the cell mechanics can be "
            "exercised offline.\n"
        )


# --- agentic engine backends ---------------------------------------------------
#
# The live `run-predict` / `run-evaluate` workflows hand a cell to a headless
# coding agent (`claude-code-action` / `codex-action`). These backends drive the
# *same* agents through their CLIs against the identical cell contract — the
# COURT_ID / DOCKET_ID / EVENT_ID / actor / RUN_ID env vars, the registry prompt
# file, and the canonical output paths — so a `local-cascade` run reproduces what
# CI does. They cannot run offline (a binary + auth are required), so the command
# construction is unit-tested through the `command_runner` seam while the default
# shells out for real.

# Default models + turn cap, matching the run-predict / run-evaluate workflows.
# The models come from the shared pricing table so this local mirror cannot
# drift from what the workflows' matrix resolves.
_CLAUDE_MODEL = DEFAULT_MODELS["claude-code"]
_CODEX_MODEL = DEFAULT_MODELS["codex"]
_GEMINI_MODEL = DEFAULT_MODELS["gemini"]
_MAX_TURNS = 120

# A command executor: run argv with env, return the process exit code. Injected so
# tests can assert on the constructed command without spawning a real agent.
CommandRunner = Callable[[Sequence[str], Mapping[str, str]], int]


class EngineUnavailable(RuntimeError):
    """The engine CLI is not installed on PATH."""

    def __init__(self, binary: str) -> None:
        super().__init__(
            f"the {binary!r} CLI is not on PATH; install it (the devcontainer ships "
            "`claude`) or use the offline `--engine stub` backend"
        )


class EngineFailed(RuntimeError):
    """The engine CLI exited non-zero for a cell."""


@dataclass(frozen=True)
class EngineCommand:
    """One agent invocation: the argv to run and the cell env vars to set."""

    argv: list[str]
    env: dict[str, str]


def _cell_env(request: RunRequest, model: str) -> dict[str, str]:
    """The cell env-var contract the workflow exports, role-tagged.

    Byte-identical to the env ``run-predict.yml`` / ``run-evaluate.yml`` set for a
    cell: the case + event ids, the shared run id, the acting id under
    ``PREDICTOR_ID`` (predict) or ``EVALUATOR_ID`` (evaluate), and the model the
    engine runs (``MODEL_ID`` — the agent copies it into its artifact's ``model``
    field). ``DECIDED_BEFORE`` appears only on back-test replay cells (the live
    workflows never set ``decided_before``). Auth and any other secrets are
    inherited from the ambient environment, never assembled here.
    """
    actor_var = "PREDICTOR_ID" if request.role == UsageRole.predictor else "EVALUATOR_ID"
    env = {
        "COURT_ID": request.court_id,
        "DOCKET_ID": str(request.docket_id),
        "EVENT_ID": request.event_id,
        actor_var: request.actor_id,
        "RUN_ID": request.run_id,
        "MODEL_ID": model,
    }
    if request.decided_before is not None:
        env["DECIDED_BEFORE"] = str(request.decided_before)
    return env


def _claude_instruction(request: RunRequest, model: str) -> str:
    """The kickoff prompt, mirroring what the live workflows give their engines.

    The cell identifiers ride inline in the prompt text (with the env vars as a
    secondary channel), exactly as ``run-predict.yml`` / ``run-evaluate.yml``
    now phrase it: some engines sanitize the shell environment in CI, so the
    prompt — not the env — is the contract's delivery channel, and the local
    harness keeps the same shape so a cell reads identically here and in CI.
    (The workflows' extra sentence about commenting on the triggering issue is
    omitted: a local cell has no issue.)
    """
    prompt = request.prompt.as_posix()
    if request.role == UsageRole.predictor:
        task = f"Read {prompt} and AGENTS.md, then produce the prediction for this cell:"
        actor_line = f"PREDICTOR_ID={request.actor_id}"
        blocked_doc = "reasoning.md"
    else:
        task = (
            f"Read {prompt} and AGENTS.md, then score every predictor's prediction "
            "for this cell against its outcome.json:"
        )
        actor_line = f"EVALUATOR_ID={request.actor_id}"
        blocked_doc = "evaluation.md"
    return (
        f"{task}\n"
        "\n"
        f"COURT_ID={request.court_id}\n"
        f"DOCKET_ID={request.docket_id}\n"
        f"EVENT_ID={request.event_id}\n"
        f"{actor_line}\n"
        f"RUN_ID={request.run_id}\n"
        f"MODEL_ID={model}\n"
        "\n"
        "These values are authoritative; the same identifiers are exported as "
        "environment variables on engines that pass them through, but if "
        "`$COURT_ID` expands empty in your shell, use the literals above. "
        "Write only the output files the prompt contract names for your cell. "
        "Do not commit, push, or open a PR. You run headless with no "
        "interactive input; if you are blocked, record it in flags.json and "
        f"explain it in {blocked_doc}, then finish — do not wait for a reply."
    )


def _produced_artifacts(request: RunRequest) -> list[Path]:
    """The cell's output files that exist after an agent run, in sorted order.

    The agent writes at the canonical paths derived from the env contract; this
    collects what landed so the runner reports it (and the caller can validate it).
    A predict cell writes its prediction pair; an evaluate cell writes one pair per
    predictor it scored, under this evaluator + run.
    """
    events = request.event_paths
    if request.role == UsageRole.predictor:
        candidates: list[Path] = [
            events.prediction(request.actor_id, request.run_id),
            events.reasoning(request.actor_id, request.run_id),
        ]
    else:
        base = events.base / "evaluations" / request.actor_id
        candidates = [
            *base.glob(f"*/{request.run_id}/evaluation.json"),
            *base.glob(f"*/{request.run_id}/evaluation.md"),
        ]
    return sorted(p for p in candidates if p.is_file())


def _run_subprocess(argv: Sequence[str], env: Mapping[str, str]) -> int:
    """Default :data:`CommandRunner`: spawn the agent, inheriting stdio."""
    try:
        return subprocess.run(list(argv), env=dict(env), check=False).returncode
    except FileNotFoundError as exc:
        raise EngineUnavailable(str(argv[0])) from exc


@dataclass(frozen=True)
class AgenticRunner:
    """Drive a headless coding-agent CLI over one cell, off the shared seam.

    Subclasses supply :meth:`build_command`; this overlays the ambient environment
    with the cell contract, runs the command, fails loudly on a non-zero exit, and
    returns the artifacts the agent produced at the canonical paths. The
    ``command_runner`` seam lets tests assert on the built command without spawning
    an agent.
    """

    backend: str
    engine: Engine
    model: str
    # Default resolved in run() rather than stored as the field default: a
    # function-valued dataclass default reads to static analysis as a method on
    # the instance, so `self.command_runner(argv, env)` looks like a 3-arg call
    # to a 2-arg function. Keeping the default off the class sidesteps that.
    command_runner: CommandRunner | None = None

    def build_command(self, request: RunRequest) -> EngineCommand:  # pragma: no cover
        raise NotImplementedError

    def run(self, request: RunRequest) -> list[Path]:
        command = self.build_command(request)
        run_command = self.command_runner or _run_subprocess
        code = run_command(command.argv, {**os.environ, **command.env})
        if code != 0:
            raise EngineFailed(
                f"{self.backend} exited {code} for cell {request.actor_id}/{request.event_id}"
            )
        return _produced_artifacts(request)


@dataclass(frozen=True)
class ClaudeCodeRunner(AgenticRunner):
    """Run the ``claude`` CLI headless, mirroring ``run-predict``'s claude-code step.

    Auth is inherited from the environment: ``ANTHROPIC_API_KEY`` (pay-per-token,
    as CI uses) or — for local iteration that does not bill per token — the
    subscription ``CLAUDE_CODE_OAUTH_TOKEN`` from ``claude setup-token``.
    """

    backend: str = "claude-code"
    engine: Engine = Engine.claude_code
    model: str = _CLAUDE_MODEL
    max_turns: int = _MAX_TURNS

    def build_command(self, request: RunRequest) -> EngineCommand:
        argv = [
            "claude",
            "-p",
            _claude_instruction(request, self.model),
            "--model",
            self.model,
            "--max-turns",
            str(self.max_turns),
            "--permission-mode",
            "bypassPermissions",
        ]
        return EngineCommand(argv=argv, env=_cell_env(request, self.model))


@dataclass(frozen=True)
class CodexRunner(AgenticRunner):
    """Run the ``codex`` CLI headless, mirroring ``run-evaluate``'s codex step.

    Codex gets the same inline-identifier kickoff prompt as the other engines
    (as the workflow's ``prompt`` input now does); auth is the inherited
    ``OPENAI_API_KEY``.
    """

    backend: str = "codex"
    engine: Engine = Engine.codex
    model: str = _CODEX_MODEL

    def build_command(self, request: RunRequest) -> EngineCommand:
        argv = [
            "codex",
            "exec",
            "--model",
            self.model,
            "--sandbox",
            "workspace-write",
            _claude_instruction(request, self.model),
        ]
        return EngineCommand(argv=argv, env=_cell_env(request, self.model))


@dataclass(frozen=True)
class GeminiRunner(AgenticRunner):
    """Run the ``gemini`` CLI headless, mirroring ``run-predict``'s Gemini step.

    Gemini drives its CLI directly — ``gemini --yolo --model M --prompt P
    --output-format json`` — the same headless call the workflow makes (the
    upstream ``run-gemini-cli`` action pulls unpinned actions the org's
    SHA-pinning policy rejects, so it is bypassed there too). Auth is the
    inherited ``GEMINI_API_KEY``; a headless run must trust the workspace
    explicitly (``GEMINI_CLI_TRUST_WORKSPACE=true``) or the CLI exits 55. As in
    the workflow, the cell identifiers ride inline in the prompt: Gemini's CLI
    sanitizer runs strict whenever ``GITHUB_SHA`` is set and strips every custom
    env var from the agent's shell **unless the workspace's
    ``.gemini/settings.json`` allowlists it** under
    ``security.environmentVariableRedaction.allowed`` — which the workflows
    (run-predict / run-evaluate / run-backtest) write with the ``_cell_env``
    contract, so in CI that contract reaches the shell too. The inline channel
    stays authoritative and is the fallback that always holds: a harness run with
    no such settings file (a bare local invocation) has only the prompt.
    """

    backend: str = "gemini"
    engine: Engine = Engine.gemini
    model: str = _GEMINI_MODEL

    def build_command(self, request: RunRequest) -> EngineCommand:
        argv = [
            "gemini",
            "--yolo",
            "--model",
            self.model,
            "--prompt",
            _claude_instruction(request, self.model),
            "--output-format",
            "json",
        ]
        env = {**_cell_env(request, self.model), "GEMINI_CLI_TRUST_WORKSPACE": "true"}
        return EngineCommand(argv=argv, env=env)


# --- replay backend ------------------------------------------------------------
#
# The offline `replay` engine emits a captured real cell's prediction from a
# committed cassette, then scores it with the stub's deterministic evaluate path.
# It exists to exercise the *consumers* of realistic agent output (the scoring
# metrics, the leaderboard roll-up) — which the stub's trivial floor cannot — with
# no model call and no network.

_CASSETTE_PREDICTION = "prediction.json"
_CASSETTE_REASONING = "reasoning.md"


class ReplayUnavailable(EngineUnavailable):
    """The ``replay`` backend was selected but no cassette directory is configured."""

    def __init__(self) -> None:
        RuntimeError.__init__(
            self,
            "the 'replay' backend needs a cassette directory; set FEDCOURTS_REPLAY_ROOT "
            "to a recorded cassette (see tests/cassettes) or use the offline `--engine stub`",
        )


@dataclass(frozen=True)
class ReplayRunner(StubRunner):
    """Offline engine that replays a captured prediction, then scores it for real.

    A predict cell re-emits the cassette's recorded ``prediction.json`` /
    ``reasoning.md`` — a real calibrated forecast with panel votes — rebinding only
    the cell *identity* (case, event, predictor, run) to the request while keeping
    the recorded forecast verbatim. An evaluate cell reuses :class:`StubRunner`'s
    evaluate path unchanged, so the deterministic scoring (Brier, vote accuracy) —
    the consume path under test — runs over realistic input rather than the stub
    floor. The cassette is read-only; nothing here calls a model or the network.
    """

    backend: str = "replay"
    cassette_root: Path | None = None

    def _predict(self, request: RunRequest) -> list[Path]:
        if self.cassette_root is None:
            raise ReplayUnavailable
        recorded = read_model(self.cassette_root / _CASSETTE_PREDICTION, Prediction)
        # Keep the recorded forecast (probability, disposition, votes, …); rebind
        # only the identity fields to the cell being produced.
        prediction = recorded.model_copy(
            update={
                "case_id": request.case_id,
                "event_id": request.event_id,
                "predictor_id": request.actor_id,
                "run_id": request.run_id,
                "created_at": _created_at(request.run_id),
                "input_snapshot": _input_snapshot(request),
            }
        )
        events = request.event_paths
        json_path = events.prediction(request.actor_id, request.run_id)
        md_path = events.reasoning(request.actor_id, request.run_id)
        write_json(json_path, prediction)
        _write_text(md_path, (self.cassette_root / _CASSETTE_REASONING).read_text())
        return sorted([json_path, md_path])


def _make_replay_runner() -> Runner:
    """Construct the replay runner from the configured cassette directory.

    Reads ``FEDCOURTS_REPLAY_ROOT`` via the settings so the zero-arg registry can
    build it; raises :class:`ReplayUnavailable` when no cassette is configured.
    """
    root = get_settings().replay_root
    if root is None:
        raise ReplayUnavailable
    return ReplayRunner(cassette_root=root)


# Backends keyed by name, mirroring how the workflow selects an engine: the
# offline `stub` and `replay` plus the three real agents `local-cascade` and the
# cert back-test can drive.
_BACKENDS: dict[str, Callable[[], Runner]] = {
    "stub": StubRunner,
    "claude-code": ClaudeCodeRunner,
    "codex": CodexRunner,
    "gemini": GeminiRunner,
    "replay": _make_replay_runner,
}


def get_runner(backend: str = "stub") -> Runner:
    """Return the runner for ``backend`` (default the offline ``stub``).

    ``stub`` is deterministic and offline; ``replay`` is also offline but emits a
    captured prediction from the configured cassette (``FEDCOURTS_REPLAY_ROOT``);
    ``claude-code`` / ``codex`` / ``gemini`` drive the real headless agents
    (network + auth required). Raises ``KeyError`` for an unknown backend, naming
    the ones available, and :class:`ReplayUnavailable` if ``replay`` has no cassette.
    """
    try:
        factory = _BACKENDS[backend]
    except KeyError:
        raise KeyError(
            f"unknown runner backend {backend!r}; available: {sorted(_BACKENDS)}"
        ) from None
    return factory()
