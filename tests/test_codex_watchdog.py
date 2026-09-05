"""The codex cell watchdog, exercised against stand-ins for a wedged step.

`scripts/codex-watchdog.sh` exists because a hung codex cell outlives the
engine step's own `timeout-minutes` and takes the whole cell down with the job
cap — no capture tail, no artifact, and no logs, since GitHub drops a cancelled
job's. Killing the engine is not enough on its own: a wedge in the action's
node wrapper, or one that never reaches the engine at all, leaves the step
`in_progress` with nothing engine-shaped to match, so the watchdog escalates to
the step's own process tree.

Every claim about that is a claim about signals and process matching on a live
runner, so it gets driven here rather than read: processes whose command lines
and parentage the watchdog is pointed at, a one-second deadline, and the
outcomes that matter — the engine dies, the wedged step's tree dies with it,
the evidence lands, and nothing that names runner infrastructure is ever
signalled.

Every fixture here is a process this module spawned. The watchdog's discovery
is pointed at fixture-scoped patterns in `_run`, never at the defaults that
name a real runner, so the suite cannot signal the step that is running it.
"""

import contextlib
import os
import re
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHDOG = REPO_ROOT / "scripts" / "codex-watchdog.sh"
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


def _run(
    watchdog_dir: Path,
    match: str,
    runner_match: str = NO_MATCH,
    worker_match: str = NO_MATCH,
    grace_s: str = "2",
    min_step_age_s: str | None = None,
    deadline_s: str | None = None,
    arm_slack_s: str = TEST_ARM_SLACK,
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
            watchdog_dir = tmp_path / f"codex-watchdog-{infra.pid}"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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
        watchdog_dir = tmp_path / "codex-watchdog"
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


def test_the_shipped_floor_derives_from_the_deadline() -> None:
    """The floor is a ratio, and the ratio is what keeps a tail step out of range.

    Nothing else pins it: every test here runs a deadline of its own, so a
    change to how the shipped floor is derived — or a hard-coded seconds value
    slipped in its place — would pass the whole suite while narrowing the one
    bound that stands between the escalation and the steps that salvage a cell.
    """
    assert _shipped_default("WATCHDOG_MIN_STEP_AGE_S") == "$((deadline_s / 2))"
