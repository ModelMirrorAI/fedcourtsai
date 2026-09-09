"""The engine cell watchdog, exercised against stand-ins for a wedged step.

`scripts/engine-watchdog.sh` exists because a hung cell outlives the engine
step's own `timeout-minutes` and takes the whole cell down with the job cap — no
capture tail, no artifact, and no logs, since GitHub drops a cancelled job's. It
has two triggers, and both are driven here.

The **completion sentinel** is the one that fires on the observed failure: the
agent writes every output its contract names and then the step's teardown never
concludes, so a watchdog that waits for a deadline is documenting the death of
work that had already succeeded. When the required outputs are all present,
parse, and stop changing, the step's tree is ended and the cell's own tail
salvages it.

The **deadline** stays behind it for a wedge that completes nothing. Killing the
engine is not enough on its own there: a wedge in the action's node wrapper, or
one that never reaches the engine at all, leaves the step `in_progress` with
nothing engine-shaped to match, so the watchdog escalates to the step's own
process tree.

Every claim about either is a claim about files and signals on a live runner, so
it gets driven here rather than read: processes whose command lines and
parentage the watchdog is pointed at, output files written and rewritten under
its nose, and the outcomes that matter — the engine dies, the wedged step's tree
dies with it, a finished cell's step is ended while its output is intact, the
evidence lands, and nothing that names runner infrastructure is ever signalled.

Every fixture here is a process this module spawned. The watchdog's discovery
is pointed at fixture-scoped patterns in `_run`, never at the defaults that
name a real runner, so the suite cannot signal the step that is running it.
"""

import contextlib
import json
import os
import re
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHDOG = REPO_ROOT / "scripts" / "engine-watchdog.sh"
# Fast enough for a test, slow enough that a loaded machine cannot slip a
# fixture's whole lifetime between two polls: everything here is a race between
# the watchdog's clock and a fixture's, and a one-second margin is none.
FAST_POLL = {"WATCHDOG_DEADLINE_S": "3", "WATCHDOG_POLL_S": "1"}
# The arming slack ships at two seconds because on a runner the guarded step is
# started *after* the watchdog. A fixture is started before it, so the suite
# widens this rather than racing it; the test that is about the slack sets it
# back down.
TEST_ARM_SLACK = "120"
# A pattern that names nothing: the value every discovery route this suite is
# not exercising is pinned to, so a route left unset can never fall back to a
# default that names the runner executing the test.
NO_MATCH = "watchdog-selftest-matches-nothing"
# Stands in for the arm step's comment-only App mint. Distinctive so the tests
# can assert it reaches the sink's Authorization header and reaches nothing else.
CHECKIN_TOKEN = "ghs-watchdog-selftest-token"
# The armed body the arm step hands over. Every PATCHed body must open with
# the whole of it: the marker line, or the next find-by-marker would miss the
# comment the watchdog just rewrote, and the arming line, which is what a
# reader of a run that never came back has to go on.
CHECKIN_BASE = (
    "<!-- codex-watchdog: R/scotus/24-1/evt-x/codex-selftest -->\n"
    + "### selftest\n"
    + "armed_at=2026-09-07T12:00:00Z deadline_s=3 fire_eta=2026-09-07T12:00:03Z"
)


def _run(  # noqa: PLR0913, PLR0917 - one parameter per knob the script reads
    watchdog_dir: Path,
    match: str,
    runner_match: str = NO_MATCH,
    worker_match: str = NO_MATCH,
    grace_s: str = "2",
    min_step_age_s: str | None = None,
    deadline_s: str | None = None,
    arm_slack_s: str = TEST_ARM_SLACK,
    checkin_url: str = "",
    checkin_base: str = "",
    heartbeat_s: str = "0",
    sentinel_paths: list[Path] | None = None,
    output_dir: Path | None = None,
    quiesce_s: str = "2",
) -> subprocess.CompletedProcess[str]:
    # Fail closed on the way in, so a future test cannot hand a discovery route
    # a pattern broad enough to name a process this suite did not spawn. Every
    # fixture marker carries this process's pid.
    for pattern in (match, runner_match, worker_match):
        assert pattern == NO_MATCH or str(os.getpid()) in pattern, (
            f"watchdog test pattern {pattern!r} is not scoped to this test's own processes"
        )
    env = {
        **os.environ,
        **FAST_POLL,
        "WATCHDOG_DIR": str(watchdog_dir),
        "WATCHDOG_MATCH": match,
        # Both routes to the step are fixture-scoped. The infrastructure
        # refusal list is deliberately left at its shipped value, so what the
        # tests exercise is the pattern that actually ships.
        "WATCHDOG_RUNNER_MATCH": runner_match,
        "WATCHDOG_WORKER_MATCH": worker_match,
        "WATCHDOG_STEP_GRACE_S": grace_s,
        "WATCHDOG_ARM_SLACK_S": arm_slack_s,
        # No codex home in the test: the home listing is best-effort, and its
        # absence must not stop the kill.
        "CODEX_HOME": str(watchdog_dir / "absent"),
        # The off-runner channel, empty for every test that is not about it —
        # spelled out rather than left to the ambient environment, so a
        # developer shell that happens to export one cannot make the suite
        # PATCH a real comment.
        "WATCHDOG_CHECKIN_URL": checkin_url,
        "WATCHDOG_CHECKIN_TOKEN": CHECKIN_TOKEN if checkin_url else "",
        "WATCHDOG_CHECKIN_BASE": checkin_base,
        "WATCHDOG_HEARTBEAT_S": heartbeat_s,
        # The completion sentinel, empty for every test that is not about it —
        # spelled out for the same reason the check-in trio is, so an ambient
        # value can never arm a reaper a test did not ask for.
        "WATCHDOG_SENTINEL_PATHS": "\n".join(str(p) for p in sentinel_paths or ()),
        "WATCHDOG_OUTPUT_DIR": str(output_dir) if output_dir else "",
        "WATCHDOG_QUIESCE_S": quiesce_s,
    }
    # Left to derive itself from the deadline unless a test is about the floor,
    # so every other test inherits whatever shape ships.
    if min_step_age_s is not None:
        env["WATCHDOG_MIN_STEP_AGE_S"] = min_step_age_s
    if deadline_s is not None:
        env["WATCHDOG_DEADLINE_S"] = deadline_s
    return subprocess.run(
        ["bash", str(WATCHDOG)],
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


#: A wedged process that ignores SIGTERM, which is what makes the watchdog's
#: SIGKILL escalation reachable — a `sleep` dies on the first signal and never
#: exercises it.
DEAF = "trap '' TERM; while :; do sleep 1; done"


def _named(argv: str, body: str | None = None) -> subprocess.Popen[bytes]:
    """A process this module owns, wearing `argv` as its command line.

    `exec -a` is what puts the marker where `pgrep -f` reads it — the same way
    the shipped patterns name the action's invocation. A `body` runs under a
    shell that keeps that name; without one the process is a bare `sleep`,
    since `bash -c` with a single command execs it and loses the name.
    """
    inner = "sleep 300" if body is None else f'bash -c "{body}"'
    return subprocess.Popen(["bash", "-c", f'exec -a "{argv}" {inner}'])


def _gone(pid: int) -> bool:
    """True once `pid` is dead or a reaped-pending zombie, as the script reads it."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return True
    return stat.rsplit(") ", 1)[1].split(" ", 1)[0] == "Z"


def _await(predicate, timeout: float = 30.0) -> bool:  # type: ignore[no-untyped-def]
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return False


def _read_pid(path: Path, timeout: float = 15.0) -> int:
    assert _await(lambda: path.exists() and path.read_text().strip().isdigit(), timeout), (
        f"the fixture never reported a pid at {path}"
    )
    pid = int(path.read_text().strip())
    assert _await(lambda: Path(f"/proc/{pid}").exists(), timeout)
    return pid


class WorkerTree:
    """A stand-in for the runner's per-job worker and the step it is waiting on.

    The runner starts each step as a child of its worker process, which is the
    parentage the watchdog anchors on. Here the "worker" is a bash process
    wearing a caller-chosen command line, and the "step" is its child — so the
    discovery route under test is the real one, driven entirely against
    processes this test spawned.
    """

    def __init__(
        self,
        tmp_path: Path,
        worker_argv: str,
        step_script: str,
        later_after_s: int = 0,
    ) -> None:
        self.tmp_path = tmp_path
        step = tmp_path / "step.sh"
        step.write_text(step_script)
        lines = [f'bash "{step}" &', f'echo $! > "{tmp_path}/step.pid"']
        if later_after_s:
            # A stand-in for the next step of the tail: the same worker's child,
            # started after the deadline has already identified its target.
            later = tmp_path / "later.sh"
            later.write_text(f'exec -a "watchdog-selftest-later-{os.getpid()}" sleep 300\n')
            lines += [
                f"sleep {later_after_s}",
                f'bash "{later}" &',
                f'echo $! > "{tmp_path}/later.pid"',
            ]
        # The worker outlives its children, as the runner's own does: a worker
        # that exited when its step did would make "was it signalled?"
        # unreadable. It keeps its own pid and command line to do so — a
        # backgrounded `sleep` would be one more live child of the worker, which
        # is the shape of a *later* step and has no business in this fixture.
        lines += ["wait", f'exec -a "{worker_argv}" sleep 300']
        worker = tmp_path / "worker.sh"
        worker.write_text("\n".join(lines) + "\n")
        self.proc = subprocess.Popen(["bash", "-c", f'exec -a "{worker_argv}" bash "{worker}"'])
        self.step_pid = _read_pid(tmp_path / "step.pid")

    def close(self) -> None:
        for pid_file in ("step.pid", "grandchild.pid", "later.pid"):
            path = self.tmp_path / pid_file
            if path.exists() and path.read_text().strip().isdigit():
                with contextlib.suppress(OSError):
                    os.kill(int(path.read_text().strip()), 9)
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait(timeout=10)


def test_the_watchdog_kills_the_wedged_engine_and_leaves_its_evidence(tmp_path: Path) -> None:
    # A process the watchdog's pattern matches, standing in for `codex exec`.
    marker = f"fedcourts-watchdog-selftest-{os.getpid()}"
    victim = _named(marker)
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
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
        # No step process was pointed at in this fixture, and the marker says
        # so rather than claiming an escalation that never happened.
        assert "escalation=no step process was identified" in fired
    finally:
        if victim.poll() is None:  # pragma: no cover - only on a failed kill
            victim.kill()
            victim.wait(timeout=10)


def test_the_default_pattern_names_the_engine_and_nothing_beside_it() -> None:
    """The pattern the workflows actually run, against the argv it must select.

    The tests above drive a pattern of their own, so nothing else checks the
    one that ships — and a pattern that matches nothing fails *silently*: the
    watchdog stands down at its deadline with the engine untouched. Matched
    here rather than killed on, so the shipped pattern is exercised without
    this suite signalling a real engine.
    """
    pattern = _shipped_default("WATCHDOG_MATCH")

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


def _shipped_default(var: str) -> str:
    """The default the workflows run with, read out of the script itself."""
    default = re.search(rf'{var}:-(.+?)\}}"', WATCHDOG.read_text())
    assert default is not None, f"{var} has no default in the script"
    return default.group(1)


def test_a_deadline_that_matched_nothing_still_ends_the_step(tmp_path: Path) -> None:
    # Reaching the deadline with no engine match means either the engine never
    # spawned or the pattern no longer names it. Recording that is half the
    # answer; the other half is that the step still has to end, or the cell
    # burns the job cap exactly as before — so the action's own step process is
    # killed on this path too, by its argv where that still names it.
    marker = f"fedcourts-watchdog-runner-{os.getpid()}"
    runner = _named(marker)
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(watchdog_dir, f"watchdog-selftest-absent-{os.getpid()}", runner_match=marker)
        assert done.returncode == 0, done.stdout + done.stderr
        assert runner.wait(timeout=30) != 0
        stood_down = (watchdog_dir / "STOOD_DOWN").read_text()
        assert "stood_down_at=" in stood_down
        assert not (watchdog_dir / "FIRED").exists()
        assert (watchdog_dir / "process-tree.txt").stat().st_size > 0
        assert "escalation=the step's tree was ended" in stood_down
    finally:
        if runner.poll() is None:  # pragma: no cover - only on a failed kill
            runner.kill()
            runner.wait(timeout=10)


def test_a_step_that_never_spawned_an_engine_is_ended_by_parentage(tmp_path: Path) -> None:
    """The never-spawned shape: nothing engine-shaped, and no usable argv either.

    This is the failure the argv route cannot reach — the action's entry
    command may not match, and there is no `codex exec` to match at all. The
    step is found as the live child of the worker, and its tree is ended so the
    step concludes below the job cap.
    """
    worker_argv = f"Runner.Worker watchdog-selftest-{os.getpid()}"
    tree = WorkerTree(tmp_path, worker_argv, "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert _await(lambda: _gone(tree.step_pid)), "the wedged step outlived the watchdog"

        stood_down = (watchdog_dir / "STOOD_DOWN").read_text()
        assert "escalation=the step's tree was ended" in stood_down
        assert str(tree.step_pid) in stood_down.split("step_tree=")[1]
        assert (watchdog_dir / "process-tree-escalation.txt").stat().st_size > 0

        # The anchor is read, never signalled: killing the worker force-kills
        # the job, which is the outcome the whole script exists to prevent.
        assert tree.proc.poll() is None, "the watchdog signalled the runner's worker process"
    finally:
        tree.close()


def test_a_step_that_outlives_the_engine_kill_has_its_tree_ended(tmp_path: Path) -> None:
    """The wedged-wrapper shape: the engine dies and the step keeps running.

    A grandchild of the step is in the fixture because the runner waits on the
    step's output, not only on its entry process — a lingering descendant keeps
    the step `in_progress` after the entry is gone, so the whole tree goes.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker)
    step_script = (
        f"bash -c 'exec -a \"watchdog-selftest-grandchild-{os.getpid()}\" sleep 300' &\n"
        + f'echo $! > "{tmp_path}/grandchild.pid"\n'
        + "wait\n"
    )
    tree = WorkerTree(
        tmp_path,
        f"Runner.Worker watchdog-selftest-{os.getpid()}",
        step_script,
        later_after_s=3,
    )
    try:
        grandchild_pid = _read_pid(tmp_path / "grandchild.pid")
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir, marker, worker_match=f"watchdog-selftest-{os.getpid()}", grace_s="6"
        )
        assert done.returncode == 0, done.stdout + done.stderr

        assert engine.wait(timeout=30) != 0
        assert _await(lambda: _gone(tree.step_pid)), "the wedged step outlived the watchdog"
        assert _await(lambda: _gone(grandchild_pid)), "a descendant kept holding the step open"

        fired = (watchdog_dir / "FIRED").read_text()
        assert "escalation=the step outlived the engine kill and its tree was ended" in fired
        assert str(grandchild_pid) in fired.split("escalated_pids=")[1]
        assert tree.proc.poll() is None, "the watchdog signalled the runner's worker process"

        # The worker's *other* child appeared after the deadline had already
        # identified its target. On a runner that is the tail step which
        # salvages the cell, so it must survive an escalation aimed at the step
        # the deadline actually found.
        later_pid = _read_pid(tmp_path / "later.pid")
        assert not _gone(later_pid), "the watchdog signalled a step it never identified"
    finally:
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_a_step_that_ends_with_the_engine_is_not_escalated_to(tmp_path: Path) -> None:
    """The healthy kill: the engine dies, the step concludes, nothing else is touched.

    The grace window exists so the ordinary case — killing the engine fails the
    step within seconds — never reaches the tree kill at all. It is a ceiling,
    not a wait: the watchdog stops as soon as the step it identified is gone,
    which is why a generous grace costs a healthy cell nothing.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker)
    # The step concludes on its own two seconds in, as a step whose engine was
    # just killed does.
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 8\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        started = time.monotonic()
        done = _run(
            watchdog_dir, marker, worker_match=f"watchdog-selftest-{os.getpid()}", grace_s="30"
        )
        elapsed = time.monotonic() - started
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=30) != 0

        fired = (watchdog_dir / "FIRED").read_text()
        assert "escalation=the step ended with the engine" in fired
        assert fired.split("escalated_pids=")[1].splitlines()[0] == ""
        assert not (watchdog_dir / "process-tree-escalation.txt").exists()
        # It stopped when the step did, well inside the 30s grace it was given.
        assert elapsed < 20, f"the watchdog waited out its grace ({elapsed:.1f}s) needlessly"
        assert tree.proc.poll() is None, "the watchdog signalled the runner's worker process"
    finally:
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_infrastructure_named_processes_are_never_signalled(tmp_path: Path) -> None:
    """Discovery may propose a process; the refusal list disposes.

    The argv route is pointed straight at a process wearing runner-
    infrastructure arguments here — the case a mis-set pattern could produce on
    a real runner; the parentage route gets the same treatment in its own test.
    Signalling such a process would force-kill the job, which is the failure
    this script exists to prevent, so it is refused however it was found.
    """
    for argv in (
        f"/home/runner/actions-runner/bin/Runner.Worker watchdog-selftest-{os.getpid()}",
        f"/home/runner/actions-runner/bin/Runner.Listener run watchdog-selftest-{os.getpid()}",
    ):
        infra = _named(argv)
        try:
            watchdog_dir = tmp_path / f"engine-watchdog-{infra.pid}"
            done = _run(
                watchdog_dir,
                f"watchdog-selftest-absent-{os.getpid()}",
                runner_match=f"watchdog-selftest-{os.getpid()}",
            )
            assert done.returncode == 0, done.stdout + done.stderr
            assert infra.poll() is None, "the watchdog signalled runner infrastructure"
            stood_down = (watchdog_dir / "STOOD_DOWN").read_text()
            assert "escalation=no step process was identified" in stood_down
        finally:
            infra.kill()
            infra.wait(timeout=10)


def test_the_shipped_refusal_list_names_the_runners_own_processes() -> None:
    """The refusal pattern against real runner argv, and against the step it must not spare.

    The tests above drive the refusal with fixtures; this one checks the
    pattern that ships still names the processes whose death is a force-killed
    job — and still leaves the action's own entry process selectable, since
    refusing that would leave every wedge unbounded.
    """
    infra = _shipped_default("WATCHDOG_INFRA_MATCH")
    refused = [
        # The hosted layout the cells actually run on, and the self-hosted one.
        "/home/runner/runners/2.328.0/bin/Runner.Worker spawnclient 102 105",
        "/home/runner/actions-runner/bin/Runner.Worker spawnclient 102 105",
        "/home/runner/actions-runner/bin/Runner.Listener run --startuptype service",
        "/home/runner/actions-runner/bin/runsvc.sh",
    ]
    step = (
        "/opt/hostedtoolcache/node/20.19.0/x64/bin/node "
        "/home/runner/work/_actions/openai/codex-action/86365089/dist/main.js run-codex-exec"
    )
    for argv in refused:
        assert re.search(infra, argv), f"the refusal list does not name {argv}"
    assert not re.search(infra, step), "the refusal list would spare the action's own step process"


def test_a_step_younger_than_the_deadline_is_not_the_step_it_guards(tmp_path: Path) -> None:
    """A tail step is a child of the same worker, and must survive.

    The steps that salvage the cell run after the engine step ends — and if the
    watchdog is still armed when one of them starts, parentage alone would name
    it. What separates them is age: the guarded step has been running the whole
    deadline, a tail step is seconds old. Here the fixture step is young and the
    floor is set above it, so discovery must refuse it.
    """
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            min_step_age_s="600",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not _gone(tree.step_pid), "the watchdog ended a step it was never armed for"
        stood_down = (watchdog_dir / "STOOD_DOWN").read_text()
        assert "escalation=no step process was identified" in stood_down
    finally:
        tree.close()


def test_a_process_that_predates_the_arming_is_not_the_step_it_guards(tmp_path: Path) -> None:
    """The other end of the window: the sidecars and their kin.

    Background processes from earlier steps outlive the steps that started them.
    They are not the step the runner is waiting on, and the watchdog can tell
    because it was armed after the guarded step's own step began — so anything
    older than the watchdog itself is refused, whatever its parentage says.
    """
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        time.sleep(10)  # the fixture is now comfortably older than the watchdog
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            # The shipped slack, since this test is about what it excludes.
            arm_slack_s="2",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not _gone(tree.step_pid), "the watchdog ended a process older than itself"
        stood_down = (watchdog_dir / "STOOD_DOWN").read_text()
        assert "escalation=no step process was identified" in stood_down
    finally:
        tree.close()


def test_a_step_that_ignores_sigterm_is_killed(tmp_path: Path) -> None:
    """A wedged tree need not answer the polite signal, which is the whole point."""
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker, DEAF)
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", DEAF + "\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(watchdog_dir, marker, worker_match=f"watchdog-selftest-{os.getpid()}")
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=60) != 0, "the engine survived a watchdog that gave up on TERM"
        assert _await(lambda: _gone(tree.step_pid)), "the step survived a SIGTERM it ignored"
        assert "escalating to SIGKILL" in done.stdout
        assert tree.proc.poll() is None, "the watchdog signalled the runner's worker process"
    finally:
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_a_descendant_outliving_the_step_entry_still_ends_the_step(tmp_path: Path) -> None:
    """The runner waits on the step's output, not only on its entry process.

    So a step whose entry exits while a descendant holds its stdout open is
    still `in_progress`, and reporting that as "the step ended with the engine"
    would be a marker a maintainer cannot trust. Survival is measured over the
    whole tree recorded at the deadline, which is what makes this case escalate.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker)
    step_script = (
        f"bash -c 'exec -a \"watchdog-selftest-grandchild-{os.getpid()}\" sleep 300' &\n"
        + f'echo $! > "{tmp_path}/grandchild.pid"\n'
        + "sleep 8\n"  # the entry process concludes; its descendant does not
    )
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", step_script)
    try:
        grandchild_pid = _read_pid(tmp_path / "grandchild.pid")
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir, marker, worker_match=f"watchdog-selftest-{os.getpid()}", grace_s="12"
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert _await(lambda: _gone(tree.step_pid))
        assert _await(lambda: _gone(grandchild_pid)), "a lingering descendant held the step open"
        fired = (watchdog_dir / "FIRED").read_text()
        assert "escalation=the step outlived the engine kill and its tree was ended" in fired
    finally:
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_parentage_never_proposes_an_infrastructure_named_step(tmp_path: Path) -> None:
    """The refusal list applies to the parentage route too, not only to argv.

    A process wearing runner-infrastructure arguments is the worker's own live
    child here, which is the shape parentage would otherwise select outright.
    """
    infra_argv = f"/home/runner/actions-runner/bin/Runner.Worker watchdog-selftest-{os.getpid()}"
    tree = WorkerTree(
        tmp_path,
        f"watchdog-selftest-anchor-{os.getpid()}",
        f'exec -a "{infra_argv}" sleep 300\n',
    )
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-anchor-{os.getpid()}",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not _gone(tree.step_pid), "parentage selected a process naming runner infrastructure"
        assert (
            "escalation=no step process was identified" in (watchdog_dir / "STOOD_DOWN").read_text()
        )
    finally:
        tree.close()


def test_a_descendant_the_step_spawned_late_is_still_ended(tmp_path: Path) -> None:
    """The age window decides which *step* is guarded, never which of its children.

    A wedged step spawns most of what holds it open during its run — the engine
    after the installs, a call that never returns — so those processes are far
    younger than the step itself. They are the guarded step by parentage, and
    applying the window to them would refuse exactly what the tree kill exists
    to reach. Here the floor is set high enough to bite, and the late
    descendant must still be ended.
    """
    tree = WorkerTree(
        tmp_path,
        f"Runner.Worker watchdog-selftest-{os.getpid()}",
        f"sleep 10\nbash -c 'exec -a \"watchdog-selftest-late-{os.getpid()}\" sleep 300' &\n"
        + f'echo $! > "{tmp_path}/grandchild.pid"\n'
        + "wait\n",
    )
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            # The step is ~15s old when this fires, well over the floor; the
            # descendant it spawned is ~5s old, well under it.
            deadline_s="15",
            min_step_age_s="8",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        # Read from the file rather than waited for: by now it should be dead,
        # and the file existing is what proves it ever ran.
        late_pid = int((tmp_path / "grandchild.pid").read_text().strip())
        assert _await(lambda: _gone(tree.step_pid)), "the guarded step was not ended"
        assert _await(lambda: _gone(late_pid)), (
            "a process the step spawned mid-run was refused, so the step stays open"
        )
        assert tree.proc.poll() is None, "the watchdog signalled the runner's worker process"
    finally:
        tree.close()


#: One cell's completion set, in the shape `fedcourts cell-outputs` emits it: a
#: per-candidate pair under an alias directory plus the judge-level files beside
#: them, which is the evaluate role's contract and the deeper of the two layouts.
def _outputs(out_dir: Path) -> list[Path]:
    return [
        out_dir / "sentinel-alias" / "run" / "evaluation.json",
        out_dir / "sentinel-alias" / "run" / "evaluation.md",
        out_dir / "run" / "retrieval.md",
        out_dir / "run" / "tooling.json",
    ]


def _write_outputs(paths: list[Path]) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"graded": true}\n' if path.suffix == ".json" else "notes\n")


def test_a_completed_cell_has_its_wedged_step_reaped(tmp_path: Path) -> None:
    """The failure this exists for: the work is done and the step will not end.

    An agent has been seen writing every file it owes, validating them, printing
    its closing token count — and then the step froze in that state until the job
    cap deleted the lot. So the reaper does not wait for a deadline it would only
    use to document the loss: complete, parsing, quiescent output ends the step
    while the output is still there, and the cell's own tail salvages it.

    The fixture step is seconds old when this fires, far under the deadline's own
    age floor — which is the point. The floor answers "did this begin after the
    deadline started counting", and at a sentinel the sharper question is
    available: the step that wrote the output began before the output was
    complete, and no tail step can have.
    """
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths)
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", DEAF + "\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        started = time.monotonic()
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            deadline_s="120",
            grace_s="6",
            sentinel_paths=paths,
            output_dir=out_dir,
            quiesce_s="2",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert time.monotonic() - started < 60, "the reaper waited out the deadline it pre-empts"
        assert _await(lambda: _gone(tree.step_pid)), "the finished cell's step was not ended"

        reaped = (watchdog_dir / "REAPED").read_text()
        assert "sentinel_at=" in reaped
        assert "reaped_at=" in reaped
        assert f"outputs={len(paths)}" in reaped
        assert "escalation=the completed cell's step tree was ended" in reaped
        # Neither deadline marker: the reap is a different verdict, and a cell
        # that ends this way has to be readable as one whose work survived.
        assert not (watchdog_dir / "FIRED").exists()
        assert not (watchdog_dir / "STOOD_DOWN").exists()
        # A process forest taken *after* the agent finished is the one capture
        # that can name whatever is holding a completed step open.
        assert (watchdog_dir / "process-tree.txt").stat().st_size > 0
        assert tree.proc.poll() is None, "the watchdog signalled the runner's worker process"
    finally:
        tree.close()


def test_continuing_writes_hold_the_reap_off(tmp_path: Path) -> None:
    """Complete is not finished: an agent revising a draft must never be cut off.

    Every output file exists and parses here from the first poll, so completeness
    alone would reap immediately — and the cell is still writing. Quiescence is
    what separates the two, and the deadline is left to be the bound instead,
    which is the conservative outcome.
    """
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths)
    # A stand-in for the agent still rewriting a document it has already written.
    churn = subprocess.Popen(["bash", "-c", f'while :; do touch "{paths[1]}"; sleep 1; done'])
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            deadline_s="14",
            sentinel_paths=paths,
            output_dir=out_dir,
            quiesce_s="8",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not (watchdog_dir / "REAPED").exists(), "a cell mid-edit was reaped"
        # The observation itself still happened, and is still the durable proof
        # that the output existed — it is the *reap* the writes hold off.
        assert "completion sentinel observed at" in done.stdout
        assert (watchdog_dir / "STOOD_DOWN").exists(), "the deadline did not stand in for the reap"
    finally:
        churn.kill()
        churn.wait(timeout=10)
        tree.close()


def test_an_incomplete_output_set_is_a_cell_still_working(tmp_path: Path) -> None:
    """One missing file is a cell that has not finished, whatever the rest says.

    The sentinel is the *whole* contract, not a quorum of it: a judge that has
    written two of its three candidates is mid-run, and reaping there would
    destroy exactly the work the reaper exists to save.
    """
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths[:-1])
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            deadline_s="8",
            sentinel_paths=paths,
            output_dir=out_dir,
            quiesce_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not (watchdog_dir / "REAPED").exists()
        assert "completion sentinel observed at" not in done.stdout
        assert (watchdog_dir / "STOOD_DOWN").exists()
    finally:
        tree.close()


def test_output_that_does_not_parse_is_not_a_completion(tmp_path: Path) -> None:
    """A half-written JSON file is the shape a mid-write poll actually sees.

    Existence alone would call that finished. The parse is deliberately all the
    sentinel asks — a schema check belongs in the tail's `validate`, which can
    route a malformed cell to a draft PR, and which a reaper cannot do anything
    with except decline to save the work.
    """
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths)
    (out_dir / "run" / "tooling.json").write_text('{"graded": tr')
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            deadline_s="8",
            sentinel_paths=paths,
            output_dir=out_dir,
            quiesce_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not (watchdog_dir / "REAPED").exists()
        assert "completion sentinel observed at" not in done.stdout
    finally:
        tree.close()


def test_an_empty_required_file_is_not_a_written_one(tmp_path: Path) -> None:
    """A zero-byte file is what a truncated write leaves behind.

    Existence alone would call it done — and for the two prose documents, which
    no parse can vet, size is the only thing standing between "written" and
    "created". The conservative reading is the whole point of the sentinel, so
    the branch that enforces it gets its own fixture.
    """
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths)
    (out_dir / "run" / "retrieval.md").write_text("")
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            deadline_s="8",
            sentinel_paths=paths,
            output_dir=out_dir,
            quiesce_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not (watchdog_dir / "REAPED").exists()
        assert "completion sentinel observed at" not in done.stdout
    finally:
        tree.close()


def test_a_reap_with_no_step_to_end_writes_no_marker(tmp_path: Path) -> None:
    """`REAPED` is a claim that the watchdog ended a step, so it must have.

    The marker is not only a record: the disarm step reads it to set `AGENT_OK`,
    which routes the cell to the run's ready PR rather than the draft one. A
    marker written before discovery would make that claim on a path where the
    watchdog signalled nothing — reachable whenever the engine step concludes on
    its own between the poll that saw quiescence and the disarm step's signal,
    and a cell that stopped early is exactly the one a maintainer should see.

    Here the sentinel is satisfied with no step to find at all, and the run has
    to fall through to its deadline rather than claim a reap.
    """
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths)
    sink = CheckinSink()
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            deadline_s="14",
            sentinel_paths=paths,
            output_dir=out_dir,
            quiesce_s="2",
            checkin_url=sink.url,
            checkin_base=CHECKIN_BASE,
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert "completion sentinel observed at" in done.stdout
        assert not (watchdog_dir / "REAPED").exists(), (
            "a reap that ended nothing still claimed the step as its own"
        )
        # It said so once, off the runner, and then let the deadline stand.
        phases = _phases(sink.bodies)
        declined = [line for line in phases if line.startswith("reap declined:")]
        assert len(declined) == 1, phases
        assert (watchdog_dir / "STOOD_DOWN").exists()
    finally:
        sink.close()


def test_the_sentinel_is_inert_before_the_cell_writes_anything(tmp_path: Path) -> None:
    """Nothing on disk yet is the state the watchdog is armed in.

    The output directory does not exist for the first minutes of every cell, and
    the poll runs from the first second — so an absent tree has to be an ordinary
    "not finished", never an error that stops the loop and takes the deadline
    with it.
    """
    out_dir = tmp_path / "never-created"
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            deadline_s="6",
            sentinel_paths=_outputs(out_dir),
            output_dir=out_dir,
            quiesce_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not (watchdog_dir / "REAPED").exists()
        # The deadline still ran and still ended the step, which is the property
        # an exception in the poll would have silently cost.
        assert (watchdog_dir / "STOOD_DOWN").exists()
        assert _await(lambda: _gone(tree.step_pid))
    finally:
        tree.close()


def test_no_sentinel_leaves_the_deadline_as_the_only_bound(tmp_path: Path) -> None:
    """An arm step that could not compute the output set must still arm a deadline.

    `cell-outputs` is bounded and best-effort in the workflows for the same
    reason the check-in is: the kill duty is primary. An empty list therefore has
    to read as "no reaper", never as "every required output is present".
    """
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(
            watchdog_dir,
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert "no completion sentinel was configured" in done.stdout
        assert not (watchdog_dir / "REAPED").exists()
        assert (watchdog_dir / "STOOD_DOWN").exists()
    finally:
        tree.close()


class CheckinSink:
    """A stand-in for the telemetry comment's REST endpoint, on localhost.

    The off-runner channel is the only account of a wedge that survives a
    cancelled job, so what it actually PATCHes has to be driven rather than
    read: the sink records each body and each Authorization header, and the
    tests below assert the sequence, the payload's strictness, and that the
    token reaches the header and nowhere else.
    """

    def __init__(self, fail_first: int = 0) -> None:
        self.bodies: list[str] = []
        self.auth: list[str] = []
        # PATCHes answered 500 instead of recorded, so a test can drive the
        # HTTP-failure half of a send: curl exits 0 on an HTTP error, and what
        # the watchdog does with that status is a behavior of its own.
        self.rejected: list[str] = []
        self._fail_first = fail_first
        sink = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def do_PATCH(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                payload = json.loads(self.rfile.read(length) or b"{}")
                if len(sink.rejected) < sink._fail_first:
                    sink.rejected.append(str(payload.get("body", "")))
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"{}")
                    return
                sink.bodies.append(str(payload.get("body", "")))
                sink.auth.append(self.headers.get("Authorization") or "")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"{}")

            def log_message(self, format: str, *args: Any) -> None:
                """Silent: the handler's default logging writes to the suite's stderr."""

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}/issues/comments/1"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=10)


def _phases(bodies: list[str]) -> list[str]:
    """The check-in lines of the last (and so most complete) body, stamps stripped.

    Everything past the armed base the arm step handed over — which the watchdog
    appends to and must never replace.
    """
    if not bodies:
        return []
    tail = bodies[-1][len(CHECKIN_BASE) :]
    return [line.split("] ", 1)[-1] for line in tail.splitlines() if line]


def test_the_watchdog_reports_every_state_off_the_runner(tmp_path: Path) -> None:
    """Arm → deadline → discovery → fire → escalation, on a channel a cancel cannot erase.

    This is the whole reason the channel exists: the diagnostics bundle, the
    disarm step that publishes it, the step summary and the job log are all
    runner-local, and the wedge they document is what cancels the runner — so a
    guard relying on them alone cannot even be observed to have fired. Each
    state is PATCHed onto this cell's
    comment as it happens, so the record is already off the runner by the time
    the kill is attempted.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker, DEAF)
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", DEAF + "\n")
    sink = CheckinSink()
    try:
        done = _run(
            tmp_path / "engine-watchdog",
            marker,
            worker_match=f"watchdog-selftest-{os.getpid()}",
            grace_s="4",
            checkin_url=sink.url,
            checkin_base=CHECKIN_BASE,
            heartbeat_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=60) != 0
        assert _await(lambda: _gone(tree.step_pid))

        phases = _phases(sink.bodies)
        # The order is the account: a reader has to be able to tell a watchdog
        # still counting from one that reached its deadline, and one that found
        # its target from one that refused every candidate.
        for expected in (
            "watching: deadline_s=3",
            "deadline reached after 3s",
            "FIRED: the engine was still running",
            "engine SIGTERM issued",
            "step tree SIGTERM issued",
            "outcome: fired",
        ):
            assert any(line.startswith(expected) for line in phases), (expected, phases)
        assert [line.startswith("watching") for line in phases].index(True) == 0
        assert phases[-1].startswith("outcome: fired")
        # A beat while it waits, which is what separates a live watchdog from
        # one whose runner was cancelled out from under it.
        assert any(line.startswith("waiting: elapsed=") for line in phases)
        # Both carry the runner's headroom: the record is the only account of
        # a resource trajectory that survives the runner.
        assert any(line.startswith("watching:") and "mem_avail_mb=" in line for line in phases)
        assert any(line.startswith("waiting:") and "load1=" in line for line in phases)
        # The deaf fixtures force both escalations, and both are reported.
        assert any("SIGKILL issued" in line for line in phases)

        # Every body opens with the whole armed base the arm step handed over.
        # The marker half is what the next find-by-marker matches on; the arming
        # half is the fire ETA and the run link, and a watchdog that composed
        # its body from the marker alone would erase both on its first
        # heartbeat — leaving the record that outlives the runner unable to say
        # when the deadline was due or which run it belonged to.
        assert all(body.startswith(CHECKIN_BASE) for body in sink.bodies)
        assert all("fire_eta=2026-09-07T12:00:03Z" in body for body in sink.bodies)
        # The body accumulates: each PATCH is the whole record so far, because a
        # comment has no append — so every body is a prefix of the next.
        assert len(sink.bodies) > 1
        assert all(
            later.startswith(earlier)
            for earlier, later in zip(sink.bodies, sink.bodies[1:], strict=False)
        ), "a PATCH replaced the record instead of extending it"
        assert all(auth == f"Bearer {CHECKIN_TOKEN}" for auth in sink.auth)
    finally:
        sink.close()
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_a_failed_send_rides_the_next_landed_send(tmp_path: Path) -> None:
    """An HTTP failure is read out, recorded once per diagnosis, delivered late.

    curl exits 0 on an HTTP error, so a 500 — or the 401 every deadline-path
    codex cell is expected to meet once its token's hour lapses — used to read
    as a landed send. The failure appends a `send-failed:` line to the
    accumulated body instead: one line per *diagnosis* rather than per failure
    (the stamps between two such lines already say how long a diagnosis held),
    no channel probe when the status itself proves the transport reached the
    host, and the next send that lands uploads the whole history.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker, DEAF)
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", DEAF + "\n")
    sink = CheckinSink(fail_first=2)
    try:
        done = _run(
            tmp_path / "engine-watchdog",
            marker,
            worker_match=f"watchdog-selftest-{os.getpid()}",
            grace_s="4",
            checkin_url=sink.url,
            checkin_base=CHECKIN_BASE,
            heartbeat_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=60) != 0
        assert _await(lambda: _gone(tree.step_pid))

        assert len(sink.rejected) == 2, "the sink did not refuse the first two sends"
        phases = _phases(sink.bodies)
        failed = [line for line in phases if line.startswith("send-failed:")]
        # Two consecutive identical 500s are one diagnosis, so one line.
        assert len(failed) == 1, failed
        assert failed[0].startswith("send-failed: curl_exit=0 http=500"), failed
        # An HTTP status in hand proves the host was reached: no probe.
        assert "probe_exit=" not in failed[0]
        assert "mem_avail_mb=" in failed[0]
        # The late-delivered record still opens with the whole armed base, and
        # the check-in host never enters what the record says.
        assert all(body.startswith(CHECKIN_BASE) for body in sink.bodies)
        assert "127.0.0.1" not in sink.bodies[-1][len(CHECKIN_BASE) :]
    finally:
        sink.close()
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_a_dead_channel_cannot_delay_the_deadline(tmp_path: Path) -> None:
    """Every send refused at the socket: the fire still lands on the wall clock.

    The probe path runs exactly when the network is dead, so its cost has to
    be bounded — at most one `--max-time`'d request per new diagnosis — and
    the deadline is derived from the wall clock rather than counted in polls,
    so no amount of telemetry latency can move the fire toward the step cap
    whose kill would cancel the job and drop the record.
    """
    with socket.socket() as placeholder:
        placeholder.bind(("127.0.0.1", 0))
        closed_port = placeholder.getsockname()[1]
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker, DEAF)
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", DEAF + "\n")
    started = time.monotonic()
    try:
        done = _run(
            tmp_path / "engine-watchdog",
            marker,
            worker_match=f"watchdog-selftest-{os.getpid()}",
            grace_s="4",
            checkin_url=f"http://127.0.0.1:{closed_port}/issues/comments/1",
            checkin_base=CHECKIN_BASE,
            heartbeat_s="1",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=60) != 0
        assert _await(lambda: _gone(tree.step_pid))
        # A refused connect is curl exit 7, and it is said locally even though
        # nothing can land off the runner.
        assert "the off-runner check-in did not land (curl_exit=7" in done.stdout
        # Well under the budget a per-send stall would blow: the 3s deadline
        # plus the graces and kill escalations, not the ~dozen failed sends.
        assert time.monotonic() - started < 60
    finally:
        tree.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_the_off_runner_payload_is_stricter_than_the_published_bundle(tmp_path: Path) -> None:
    """Counts, pids, phases, timestamps, kernel-owned vitals and probe exit
    codes — never argv, never a path, never the token.

    The bundle rides a cell artifact and expires with it; this comment sits on a
    public issue forever, so it takes the harder rule. It is composed only from
    sources the agent cannot write — the script's own variables, plus
    /proc/meminfo and /proc/loadavg — for the same reason: WATCHDOG_DIR is
    writable by the very agent the watchdog may be about to kill, and a body
    read back off that directory would let the agent choose what a public
    issue says.

    Driven with the sentinel armed, because the sentinel is the newest way for
    file-derived text to reach the record: it is handed a list of paths and it
    reads those files every poll. Neither the paths nor a byte of their contents
    may appear — the counts and the observation timestamp are the whole of what
    it may say — and the fixture writes a distinctive marker *into* an output
    file so the contents half is checked rather than assumed.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker)
    sink = CheckinSink()
    out_dir = tmp_path / "cell"
    paths = _outputs(out_dir)
    _write_outputs(paths)
    content_marker = f"watchdog-selftest-file-content-{os.getpid()}"
    (out_dir / "run" / "retrieval.md").write_text(f"{content_marker}\n")
    try:
        done = _run(
            tmp_path / "engine-watchdog",
            marker,
            checkin_url=sink.url,
            checkin_base=CHECKIN_BASE,
            heartbeat_s="1",
            sentinel_paths=paths,
            output_dir=out_dir,
            # Long enough that the deadline is reached first, so this exercises
            # the sentinel's *observation* without the reap ending the run early.
            quiesce_s="600",
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=30) != 0
        record = "\n".join(sink.bodies)
        assert "completion sentinel observed at" in record, "the sentinel never fired here"
        assert marker not in record, "a matched process's argv reached the public record"
        assert str(tmp_path) not in record, "a runner path reached the public record"
        assert "retrieval.md" not in record, "a sentinel path reached the public record"
        assert content_marker not in record, "an output file's contents reached the public record"
        assert content_marker not in done.stdout + done.stderr
        assert CHECKIN_TOKEN not in record, "the token was echoed into the record it authorises"
        # Nor into the watchdog's own log, which rides the published artifact.
        # (The process dump beside it cannot settle the argv question either way:
        # it is written after the check-in's curl has already exited, so the
        # guarantee that keeps the token out of argv is the `--config` pipe the
        # `checkin` function uses, not anything observable here.)
        assert CHECKIN_TOKEN not in done.stdout + done.stderr
        # The pid of the process it killed is the one identifier that does
        # belong here: it is what ties this record to the bundle beside it.
        assert any(str(engine.pid) in body for body in sink.bodies)
    finally:
        sink.close()
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_the_discovery_tally_separates_a_refusal_from_an_empty_field(tmp_path: Path) -> None:
    """`roots=0` has two very different causes, and they have opposite fixes.

    A floor set too high refuses candidates it should have accepted; a runner
    whose shape moved proposes none at all. Without a tally both read as the
    same silent stand-down, so it rides the record: candidates seen, and how
    many each refusal turned away.
    """
    tree = WorkerTree(tmp_path, f"Runner.Worker watchdog-selftest-{os.getpid()}", "sleep 300\n")
    sink = CheckinSink()
    try:
        done = _run(
            tmp_path / "engine-watchdog",
            f"watchdog-selftest-absent-{os.getpid()}",
            worker_match=f"watchdog-selftest-{os.getpid()}",
            min_step_age_s="600",  # the floor refuses the fixture step
            checkin_url=sink.url,
            checkin_base=CHECKIN_BASE,
        )
        assert done.returncode == 0, done.stdout + done.stderr
        assert not _gone(tree.step_pid)
        discovery = next(line for line in _phases(sink.bodies) if line.startswith("discovery: "))
        assert "roots=0 engine_matched=0" in discovery
        # The candidate was seen and refused on age, which is the reading the
        # bare `roots=0` could not give.
        assert "refused_age=1" in discovery
        assert _phases(sink.bodies)[-1].startswith("outcome: stood_down")
    finally:
        sink.close()
        tree.close()


def test_no_check_in_url_leaves_the_kill_duty_untouched(tmp_path: Path) -> None:
    """The arm step's check-in is best-effort, so the watchdog must work without one.

    A watchdog that refused to arm without a telemetry channel would trade the
    duty it exists for against its own reporting — the wrong way round.
    """
    marker = f"fedcourts-watchdog-engine-{os.getpid()}"
    engine = _named(marker)
    try:
        watchdog_dir = tmp_path / "engine-watchdog"
        done = _run(watchdog_dir, marker, heartbeat_s="1")  # no URL, no token
        assert done.returncode == 0, done.stdout + done.stderr
        assert engine.wait(timeout=30) != 0
        assert (watchdog_dir / "FIRED").exists()
        assert "check-in" not in done.stdout
    finally:
        if engine.poll() is None:  # pragma: no cover - only on a failed kill
            engine.kill()
            engine.wait(timeout=10)


def test_the_shipped_floor_derives_from_the_deadline() -> None:
    """The floor is a ratio, and the ratio is what keeps a tail step out of range.

    Nothing else pins it: every test here runs a deadline of its own, so a
    change to how the shipped floor is derived — or a hard-coded seconds value
    slipped in its place — would pass the whole suite while narrowing the one
    bound that stands between the escalation and the steps that salvage a cell.
    """
    assert _shipped_default("WATCHDOG_MIN_STEP_AGE_S") == "$((deadline_s / 2))"
