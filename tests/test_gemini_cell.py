"""The cell workflows' gemini step, driven against a stub engine.

`scripts/gemini-cell.sh` is the whole of that step: one headless gemini-cli
turn, retried in place when the turn ends on a transient fault. Every claim it
makes is a claim about what happens on a runner — which attempt retries, what
the output root holds when the retry starts, what the step exits with, what the
usage capture will read — so each is driven here rather than read: a stub
`gemini` on PATH that plays a scripted sequence of turns, and the real
`fedcourts` harness commands behind a stub `uv` that forwards to them.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from fedcourtsai.pipeline.runner import RunRequest, StubRunner
from fedcourtsai.schemas import UsageRole

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "gemini-cell.sh"

COURT, DOCKET, EVENT, RUN_ID = "scotus", "123", "evt-cert-decision", "20261002T212439Z"
PREDICTOR, EVALUATOR = "gemini-baseline", "gemini-judge"

INVALID_STREAM = {
    "type": "INVALID_STREAM",
    "message": "Invalid stream: The model returned an empty response or malformed tool call.",
}

# One scripted turn per line of the plan, consumed in order:
#   ok             a clean turn
#   ok-produce     a clean turn that writes the cell's judgment artifact
#   invalid        INVALID_STREAM in the JSON result, zero exit — after writing
#                  a half-finished reasoning.md, as a turn cut off mid-cell does
#   invalid-produce  the same, after writing a judgment artifact that holds to
#                    its schema
#   invalid-malformed  the same, after writing a judgment artifact its schema
#                    refuses
#   transient-exit-produce   a non-zero exit on a transient fault, after
#                  writing a valid judgment artifact and nothing else
#   transient-exit-complete  the same, after writing every file the cell owes
#   permanent      a non-zero exit whose stderr names a context-length fault
#   quota          a non-zero exit with gemini's terminal-quota wording
#   stderr-object  a non-zero exit leaving a stack and the error object on stderr
# Every turn appends one record to the telemetry log, as gemini-cli's local
# exporter does (it opens the file for append).
STUB_GEMINI = r"""#!/usr/bin/env bash
set -euo pipefail
n=$(( $(cat "$STUB_COUNT" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$STUB_COUNT"
turn=$(sed -n "${n}p" "$STUB_PLAN")
mkdir -p "$(dirname "$STUB_TELEMETRY")"
printf "$STUB_TELEMETRY_RECORD" "$n" >> "$STUB_TELEMETRY"
invalid="$STUB_INVALID_RESULT"
case "$turn" in
  ok) echo '{"session_id": "s", "response": "done"}' ;;
  ok-produce)
    mkdir -p "$STUB_OUT"; echo '{}' > "$STUB_OUT/$STUB_ARTIFACT"
    echo '{"session_id": "s", "response": "done"}' ;;
  invalid)
    mkdir -p "$STUB_OUT/scratch"; echo "half a draft" > "$STUB_OUT/reasoning.md"
    echo "notes" > "$STUB_OUT/scratch/notes.txt"
    echo "$invalid" ;;
  invalid-produce)
    mkdir -p "$STUB_OUT"; printf '%s' "$STUB_VALID_ARTIFACT" > "$STUB_OUT/$STUB_ARTIFACT"
    echo "$invalid" ;;
  invalid-malformed)
    mkdir -p "$STUB_OUT"; echo '{"granted": "perhaps"}' > "$STUB_OUT/$STUB_ARTIFACT"
    echo "$invalid" ;;
  invalid-flags)
    mkdir -p "$STUB_OUT"; echo '{"flags": []}' > "$STUB_OUT/flags.json"
    echo "$invalid" ;;
  transient-exit-produce)
    mkdir -p "$STUB_OUT"; printf '%s' "$STUB_VALID_ARTIFACT" > "$STUB_OUT/$STUB_ARTIFACT"
    echo "503 Service Unavailable" >&2; exit 144 ;;
  transient-exit-complete)
    mkdir -p "$STUB_OUT"; printf '%s' "$STUB_VALID_ARTIFACT" > "$STUB_OUT/$STUB_ARTIFACT"
    for doc in reasoning.md predicted_reasoning.md retrieval.md; do
      echo "prose" > "$STUB_OUT/$doc"
    done
    echo '{}' > "$STUB_OUT/tooling.json"
    echo "503 Service Unavailable" >&2; exit 144 ;;
  permanent) echo "API error: request exceeds the context length" >&2; exit 1 ;;
  stderr-object)
    echo "    at async GeminiChat.makeApiCallAndProcessStream (chunk.js:321564:28)" >&2
    echo "$STUB_STDERR_OBJECT" >&2
    exit 1 ;;
  quota)
    echo "TerminalQuotaError: You have exhausted your daily quota on this model. 429" >&2
    exit 1 ;;
  *) echo "stub gemini: no turn scripted for attempt $n" >&2; exit 99 ;;
esac
"""

# One api_response record per turn, shaped as the usage parser reads them.
TELEMETRY_RECORD = (
    '{\\n  "attributes": {"event.name": "gemini_cli.api_response", '
    + '"input_token_count": 100, "output_token_count": 10, "attempt": %s}\\n}\\n'
)
INVALID_RESULT = json.dumps({"session_id": "s", "response": "", "error": INVALID_STREAM})
# A failed exit's error object as gemini-cli leaves it, on stderr after the
# stack, with a credential-shaped value the annotation must not carry.
STDERR_OBJECT = json.dumps(
    {
        "session_id": "s",
        "error": {
            "type": "Error",
            "message": "exception TypeError: fetch failed sending request "
            + "key="
            + "AIza"
            + "Sy"
            + "0" * 33,
            "code": 1,
        },
    },
    indent=2,
)
# The fault as the step's annotation names it: the result's error, type and message.
INVALID_FAULT = f"{INVALID_STREAM['type']}: {INVALID_STREAM['message']}"

# `uv run fedcourts <args>` -> the real CLI from this environment.
CLI = 'import sys; from fedcourtsai.cli import app; sys.argv[0] = "fedcourts"; app()'
STUB_UV = f"""#!/usr/bin/env bash
[ "$1" = run ] || exit 97
shift
[ "$1" = fedcourts ] || exit 98
shift
# A harness command a test names here fails, as a broken environment would.
[ "$1" = "${{STUB_FAIL_COMMAND:-}}" ] && exit 1
exec {sys.executable} -c '{CLI}' "$@"
"""


def _valid_prediction(tmp_path: Path) -> str:
    """A ``prediction.json`` that holds to its schema, as the offline stub writes one."""
    scratch = tmp_path / "valid-artifact"
    request = RunRequest(
        role=UsageRole.predictor,
        court_id=COURT,
        docket_id=int(DOCKET),
        event_id=EVENT,
        actor_id=PREDICTOR,
        run_id=RUN_ID,
        prompt=Path(".github/prompts/predict.md"),
        data_root=scratch,
    )
    StubRunner().run(request)
    (written,) = scratch.rglob("prediction.json")
    return written.read_text()


def _run(
    tmp_path: Path,
    plan: list[str],
    *,
    role: str = "predict",
    deadline_minutes: int = 50,
    knobs: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    """Run the step's script over a scripted sequence of turns.

    Returns the finished process and the cell's output root.
    """
    stubs = tmp_path / "bin"
    stubs.mkdir(exist_ok=True)
    for name, body in (("gemini", STUB_GEMINI), ("uv", STUB_UV)):
        stub = stubs / name
        stub.write_text(body)
        stub.chmod(0o755)
    data_root = tmp_path / "data"
    events = data_root / "cases" / COURT / DOCKET / "events" / EVENT
    if role == "predict":
        actor = PREDICTOR
        out = events / "predictions" / PREDICTOR / RUN_ID
        root, artifact = out, "prediction.json"
    else:
        actor = EVALUATOR
        root = events / "evaluations" / EVALUATOR
        out = root / "alias-a" / RUN_ID
        artifact = "evaluation.json"
    (tmp_path / "plan").write_text("\n".join(plan) + "\n")
    runner_temp = tmp_path / "runner-temp"
    runner_temp.mkdir(exist_ok=True)
    env = {
        "PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}",
        "HOME": str(tmp_path),
        "RUNNER_TEMP": str(runner_temp),
        "FEDCOURTS_DATA_ROOT": str(data_root),
        "ENGINE_DEADLINE_MINUTES": str(deadline_minutes),
        "MODEL_ID": "gemini-test",
        "PROMPT": "a cell",
        "GEMINI_API_KEY": "not-a-key",
        "COURT_ID": COURT,
        "DOCKET_ID": DOCKET,
        "EVENT_ID": EVENT,
        "RUN_ID": RUN_ID,
        "STUB_PLAN": str(tmp_path / "plan"),
        "STUB_COUNT": str(tmp_path / "count"),
        "STUB_OUT": str(out),
        "STUB_ARTIFACT": artifact,
        "STUB_VALID_ARTIFACT": _valid_prediction(tmp_path),
        "STUB_TELEMETRY": str(tmp_path / ".gemini" / "telemetry.log"),
        "STUB_TELEMETRY_RECORD": TELEMETRY_RECORD,
        "STUB_INVALID_RESULT": INVALID_RESULT,
        "STUB_STDERR_OBJECT": STDERR_OBJECT,
        # No waiting between attempts unless a test asks for it.
        "GEMINI_RETRY_BACKOFF_S": "0",
        **(knobs or {}),
    }
    result = subprocess.run(
        ["bash", str(SCRIPT), role, actor],
        env=env,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    return result, root


def _attempts(tmp_path: Path) -> int:
    return int((tmp_path / "count").read_text())


def _warnings(result: subprocess.CompletedProcess[str]) -> list[str]:
    return [line for line in result.stdout.splitlines() if line.startswith("::warning::")]


def test_an_invalid_stream_is_retried_from_a_clean_output_root(tmp_path: Path) -> None:
    target = tmp_path / "result.json"
    result, root = _run(
        tmp_path, ["invalid", "invalid", "ok-produce"], knobs={"GEMINI_RESULT_FILE": str(target)}
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert _attempts(tmp_path) == 3
    # Each failed turn's half-draft and scratch directory were removed before
    # the next turn started, so what survives is the last turn's alone.
    assert sorted(p.name for p in root.iterdir()) == ["prediction.json"]
    warnings = _warnings(result)
    assert len(warnings) == 2
    assert all("ended transient; retrying" in w for w in warnings)
    assert all(w.endswith(f"; engine said: {INVALID_FAULT}") for w in warnings)
    assert f"predict {PREDICTOR} {COURT}/{DOCKET} {EVENT}" in warnings[0]
    # The telemetry log is left in place, so the usage and retrieval captures
    # read all three turns — the failed ones spent real tokens.
    telemetry = (tmp_path / ".gemini" / "telemetry.log").read_text()
    assert [f'"attempt": {n}' in telemetry for n in (1, 2, 3)] == [True, True, True]
    # The smoke's result file is the last attempt's result, not the first's.
    assert json.loads(target.read_text())["response"] == "done"


def test_the_attempts_are_capped(tmp_path: Path) -> None:
    result, root = _run(tmp_path, ["invalid", "invalid", "invalid"], knobs={})
    # The shipped cap is three; a fourth turn would find no plan and exit 99.
    assert _attempts(tmp_path) == 3
    # The last turn's exit status is the step's — a zero, as gemini gave it.
    assert result.returncode == 0
    (last,) = [w for w in _warnings(result) if "not retried" in w]
    assert "attempt 3/3 ended transient; not retried" in last
    assert last.endswith(f"; engine said: {INVALID_FAULT}")
    assert "all 3 attempts are spent" in last
    # The last turn's leavings are not reset: no retry follows to need it,
    # and the tail reads the cell as it stands.
    assert (root / "reasoning.md").is_file()


@pytest.mark.parametrize(
    ("turn", "verdict", "fault"),
    [
        ("permanent", "permanent", "API error: request exceeds the context length"),
        (
            "quota",
            "terminal_quota",
            "TerminalQuotaError: You have exhausted your daily quota on this model. 429",
        ),
    ],
)
def test_a_fault_that_cannot_clear_is_not_retried(
    tmp_path: Path, turn: str, verdict: str, fault: str
) -> None:
    result, _ = _run(tmp_path, [turn, "ok"])
    assert _attempts(tmp_path) == 1
    assert result.returncode == 1, "the step's exit status is the engine's"
    # The engine's stderr reaches the job log, not only the classifier's capture.
    assert "exhausted your daily quota" in result.stderr or "context length" in result.stderr
    (warning,) = _warnings(result)
    assert (
        f"attempt 1/3 ended {verdict}; not retried: the fault is not a transient one"
        + f"; engine said: {fault}"
        in warning
    )


def test_no_retry_starts_without_enough_of_the_deadline_left(tmp_path: Path) -> None:
    # A one-minute deadline with a two-minute floor for a retry: the first
    # attempt's fault is transient, and the time rule alone refuses the retry.
    result, _ = _run(
        tmp_path,
        ["invalid", "ok"],
        deadline_minutes=1,
        knobs={"GEMINI_RETRY_MIN_REMAINING_S": "120"},
    )
    assert _attempts(tmp_path) == 1
    (warning,) = _warnings(result)
    assert "not retried: under 120s of the 1-minute engine deadline would remain" in warning


def test_the_backoff_counts_against_the_deadline(tmp_path: Path) -> None:
    # Room for the floor, not for the floor plus the wait before the retry.
    result, _ = _run(
        tmp_path,
        ["invalid", "ok"],
        deadline_minutes=1,
        knobs={"GEMINI_RETRY_MIN_REMAINING_S": "40", "GEMINI_RETRY_BACKOFF_S": "30"},
    )
    assert _attempts(tmp_path) == 1
    assert "engine deadline would remain" in _warnings(result)[0]


def test_an_attempt_that_produced_the_cells_output_is_kept(tmp_path: Path) -> None:
    result, root = _run(tmp_path, ["invalid-produce", "ok"])
    assert _attempts(tmp_path) == 1
    assert (root / "prediction.json").is_file()
    (warning,) = _warnings(result)
    assert "the attempt produced the cell's output, which a retry would discard" in warning


def test_an_attempt_whose_output_fails_its_schema_is_retried(tmp_path: Path) -> None:
    # The tail would refuse a prediction its own model refuses, so nothing is
    # lost by retrying over it; the retry starts from a root without it.
    result, root = _run(tmp_path, ["invalid-malformed", "ok"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert _attempts(tmp_path) == 2
    assert not root.exists()
    (warning,) = _warnings(result)
    assert "retrying from a clean output root" in warning


def test_malformed_output_is_kept_when_its_schema_check_cannot_run(tmp_path: Path) -> None:
    # Only a clear verdict against the output discards it.
    result, root = _run(
        tmp_path, ["invalid-malformed", "ok"], knobs={"STUB_FAIL_COMMAND": "finalize-validates"}
    )
    assert _attempts(tmp_path) == 1
    assert (root / "prediction.json").is_file()
    (warning,) = _warnings(result)
    assert "the attempt produced the cell's output, which a retry would discard" in warning


def test_a_failing_transient_exit_over_a_whole_cell_concludes_clean(tmp_path: Path) -> None:
    # The fault arrived after the work: every owed file is there and the
    # prediction validates, so the step is not failed for the manner of its end.
    result, root = _run(tmp_path, ["transient-exit-complete", "ok"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert _attempts(tmp_path) == 1
    assert (root / "prediction.json").is_file()
    assert any("the step concludes clean" in w for w in _warnings(result)), _warnings(result)


def test_a_failing_transient_exit_over_a_partial_cell_stays_failed(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, ["transient-exit-produce", "ok"])
    assert result.returncode == 144
    assert _attempts(tmp_path) == 1
    assert not any("concludes clean" in w for w in _warnings(result))


@pytest.mark.parametrize("failing", ["finalize-complete", "finalize-validates"])
def test_a_whole_cell_stays_failed_when_a_check_cannot_run(tmp_path: Path, failing: str) -> None:
    result, _ = _run(
        tmp_path, ["transient-exit-complete", "ok"], knobs={"STUB_FAIL_COMMAND": failing}
    )
    assert result.returncode == 144
    assert not any("concludes clean" in w for w in _warnings(result))


def test_an_evaluate_retry_removes_only_what_the_failed_attempt_added(tmp_path: Path) -> None:
    # An evaluator's root holds earlier runs' committed work; the reset must
    # leave every byte of it and take only the failed turn's files.
    root = tmp_path / "data" / "cases" / COURT / DOCKET / "events" / EVENT / "evaluations"
    earlier = root / EVALUATOR / "alias-a" / "20260901T000000Z"
    earlier.mkdir(parents=True)
    (earlier / "evaluation.json").write_text('{"earlier": true}')
    result, evaluator_root = _run(tmp_path, ["invalid", "ok-produce"], role="evaluate")
    assert result.returncode == 0, result.stdout + result.stderr
    assert _attempts(tmp_path) == 2
    assert (earlier / "evaluation.json").read_text() == '{"earlier": true}'
    current = evaluator_root / "alias-a" / RUN_ID
    assert sorted(p.name for p in current.iterdir()) == ["evaluation.json"]


def test_an_attempt_that_wrote_its_flags_is_kept(tmp_path: Path) -> None:
    # A flags.json is the cell's written disclosure; a fresh session would know
    # nothing of what the failed turn flagged, so the reset declines.
    result, root = _run(tmp_path, ["invalid-flags", "ok"])
    assert _attempts(tmp_path) == 1
    assert (root / "flags.json").is_file()
    (warning,) = _warnings(result)
    assert "not retried: the attempt wrote the cell's flags.json" in warning


@pytest.mark.parametrize(
    ("failing", "reason"),
    [
        ("cell-output-snapshot", "there is no snapshot to reset the output root to"),
        ("cell-output-reset", "the output root could not be reset"),
        ("engine-attempt-class", "the attempt could not be classified"),
    ],
)
def test_a_harness_failure_means_no_retry(tmp_path: Path, failing: str, reason: str) -> None:
    # Every degraded branch ends on the attempt it met, never retrying over a
    # root it could not record or reset, nor on a verdict it could not reach.
    result, _ = _run(tmp_path, ["invalid", "ok"], knobs={"STUB_FAIL_COMMAND": failing})
    assert _attempts(tmp_path) == 1
    assert result.returncode == 0
    assert any(f"not retried: {reason}" in w for w in _warnings(result)), _warnings(result)


def test_a_clean_first_turn_is_the_only_turn(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, ["ok-produce", "ok"], knobs={"GEMINI_RESULT_FILE": ""})
    assert result.returncode == 0
    assert _attempts(tmp_path) == 1
    assert _warnings(result) == []
    # The JSON result still reaches the log, as the bare invocation's did.
    assert '"response": "done"' in result.stdout


@pytest.mark.parametrize("knob", ["GEMINI_MAX_ATTEMPTS", "GEMINI_RETRY_MIN_REMAINING_S"])
def test_a_malformed_knob_fails_before_the_engine_starts(tmp_path: Path, knob: str) -> None:
    result, _ = _run(tmp_path, ["ok"], knobs={knob: "3x"})
    assert result.returncode == 1
    assert not (tmp_path / "count").exists(), "the engine ran under a knob read as zero"


def test_the_annotation_names_a_fault_left_on_stderr(tmp_path: Path) -> None:
    """A failed exit's error object is read off stderr, screened, and named."""
    # A dropped model call is transient: the second turn runs, and both the
    # retry's annotation and the last attempt's name the fault.
    result, _ = _run(tmp_path, ["stderr-object", "stderr-object", "stderr-object"])
    assert _attempts(tmp_path) == 3
    warnings = _warnings(result)
    assert len(warnings) == 3
    assert "ended transient; retrying" in warnings[0]
    assert "attempt 3/3 ended transient; not retried: all 3 attempts are spent" in warnings[-1]
    for warning in warnings:
        assert warning.endswith(
            "; engine said: Error: exception TypeError: fetch failed sending request "
            + "key redacted:google-key"
        )
        assert "AIza" not in warning


def test_a_fault_the_harness_cannot_read_leaves_the_annotation_bare(tmp_path: Path) -> None:
    """The fault line is a nicety: its command failing changes no retry."""
    result, _ = _run(
        tmp_path, ["invalid", "ok"], knobs={"STUB_FAIL_COMMAND": "engine-attempt-fault"}
    )
    assert _attempts(tmp_path) == 2
    assert result.returncode == 0
    (warning,) = _warnings(result)
    assert warning.endswith(" ended transient; retrying from a clean output root in 0s")
