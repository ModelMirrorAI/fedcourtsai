"""The codex cell watchdog, exercised against a stand-in for a wedged engine.

`scripts/codex-watchdog.sh` exists because a hung `codex exec` outlives the
engine step's own `timeout-minutes` and takes the whole cell down with the job
cap — no capture tail, no artifact, and no logs, since GitHub drops a cancelled
job's. Every claim about it is a claim about signals and process matching on a
live runner, so it gets driven here rather than read: a process whose command
line the watchdog is pointed at, a one-second deadline, and the outcomes that
matter — it fires and leaves evidence, or it matches nothing, records that, and
still ends the step.
"""

import os
import re
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHDOG = REPO_ROOT / "scripts" / "codex-watchdog.sh"
# Fast enough for a test, and the same knob the workflows leave at its default.
FAST_POLL = {"WATCHDOG_DEADLINE_S": "1", "WATCHDOG_POLL_S": "1"}


def _run(
    watchdog_dir: Path, match: str, runner_match: str = "watchdog-no-such-runner"
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        **FAST_POLL,
        "WATCHDOG_DIR": str(watchdog_dir),
        "WATCHDOG_MATCH": match,
        "WATCHDOG_RUNNER_MATCH": runner_match,
        # No codex home in the test: the home listing is best-effort, and its
        # absence must not stop the kill.
        "CODEX_HOME": str(watchdog_dir / "absent"),
    }
    return subprocess.run(
        ["bash", str(WATCHDOG)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_the_watchdog_kills_the_wedged_engine_and_leaves_its_evidence(tmp_path: Path) -> None:
    # A process the watchdog's pattern matches, standing in for `codex exec`:
    # `exec -a` puts the marker in its command line, which is what `pgrep -f`
    # reads — the same way the real pattern names the action's invocation.
    marker = f"fedcourts-watchdog-selftest-{os.getpid()}"
    victim = subprocess.Popen(["bash", "-c", f'exec -a "{marker}" sleep 120'])
    try:
        watchdog_dir = tmp_path / "codex-watchdog"
        done = _run(watchdog_dir, marker)
        assert done.returncode == 0, done.stdout + done.stderr

        # The step's failure is the point: the engine process is gone.
        assert victim.wait(timeout=30) != 0

        # And the evidence a cancelled job would have destroyed is on disk,
        # ready to ride the cell artifact.
        fired = (watchdog_dir / "FIRED").read_text()
        assert f"pids={victim.pid}" in fired
        assert "fired_at=" in fired
        assert not (watchdog_dir / "STOOD_DOWN").exists()
        assert (watchdog_dir / "process-tree.txt").stat().st_size > 0
        assert marker in (watchdog_dir / "engine-proc.txt").read_text()
    finally:
        if victim.poll() is None:  # pragma: no cover - only on a failed kill
            victim.kill()
            victim.wait(timeout=10)


def test_the_default_pattern_names_the_engine_and_nothing_beside_it() -> None:
    """The pattern the workflows actually run, against the argv it must select.

    The two tests above drive a pattern of their own, so nothing else checks
    the one that ships — and a pattern that matches nothing fails *silently*:
    the watchdog stands down at its deadline and the hang runs on to the job
    cap exactly as before. Matched here rather than killed on, so the shipped
    pattern is exercised without this suite signalling a real engine.
    """
    default = re.search(
        r'WATCHDOG_MATCH:-(.+?)\}"', (REPO_ROOT / "scripts" / "codex-watchdog.sh").read_text()
    )
    assert default is not None
    pattern = default.group(1)

    # The action's own invocation (`runCodexExec` resolves `codex` to a path,
    # then appends the subcommand and this flag), and a decoy that merely
    # quotes it — a diagnostic step, a comment, a predictor id.
    engine = "/usr/local/bin/codex exec --skip-git-repo-check --cd /tmp"
    decoy = "codex-baseline cell watching for 'codex exec --skip-git-repo-check'"
    procs = [
        subprocess.Popen(["bash", "-c", f'exec -a "{argv}" sleep 60']) for argv in (engine, decoy)
    ]
    try:
        time.sleep(0.5)  # let both `exec` into their stand-in command lines
        matched = subprocess.run(
            ["pgrep", "-u", str(os.getuid()), "-f", "--", pattern],
            capture_output=True,
            text=True,
            check=False,
        )
        found = {int(line) for line in matched.stdout.split()}
        assert procs[0].pid in found, "the shipped pattern does not name the engine's invocation"
        assert procs[1].pid not in found, "the shipped pattern matches a process that quotes it"
    finally:
        for proc in procs:
            proc.kill()
            proc.wait(timeout=10)


def test_a_deadline_that_matched_nothing_still_ends_the_step(tmp_path: Path) -> None:
    # Reaching the deadline with no engine match means either the pattern no
    # longer names the engine or the wedge is in one of the action's earlier
    # phases. Recording that is half the answer; the other half is that the
    # step still has to end, or the cell burns the job cap exactly as before —
    # so the action's own step process is killed on this path too.
    marker = f"fedcourts-watchdog-runner-{os.getpid()}"
    runner = subprocess.Popen(["bash", "-c", f'exec -a "{marker}" sleep 120'])
    try:
        watchdog_dir = tmp_path / "codex-watchdog"
        done = _run(
            watchdog_dir,
            f"fedcourts-watchdog-matches-nothing-{time.time_ns()}",
            runner_match=marker,
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert runner.wait(timeout=30) != 0
        stood_down = (watchdog_dir / "STOOD_DOWN").read_text()
        assert "stood_down_at=" in stood_down
        assert not (watchdog_dir / "FIRED").exists()
        assert (watchdog_dir / "process-tree.txt").stat().st_size > 0
    finally:
        if runner.poll() is None:  # pragma: no cover - only on a failed kill
            runner.kill()
            runner.wait(timeout=10)
