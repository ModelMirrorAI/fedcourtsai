"""run-ops' ops-metrics push, executed against a local remote.

The ops snapshot is the one copy of the day's ops report, and the public status
page reads the ``status.json`` it carries, so a push that fails loses both until
the next run. Two things make a push fail that have nothing to do with the
snapshot: the validate writer advancing the shared branch, and a transient
GitHub error (``remote: fatal error in commit_refs``). These tests run the
step's own shell body against a bare repository, with a ``git`` shim that fails
chosen pushes the way GitHub does and a ``sleep`` shim that returns at once, and
hold it to:

* **retry** — a branch advance plus a transient failure still lands the
  snapshot, rebased on top of the advance, with the advance kept;
* **fail loudly** — a push that never succeeds fails the step with an error,
  after the bounded number of attempts.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
RUN_OPS = ROOT / ".github" / "workflows" / "run-ops.yml"
STEP = "Append the snapshot to the ops-metrics branch"

GIT_SHIM = """#!/usr/bin/env bash
# Fail the first $FAIL_PUSHES pushes as GitHub's commit_refs blip does.
for arg in "$@"; do
  if [ "$arg" = "push" ]; then
    n=$(cat "$PUSH_COUNT" 2>/dev/null || echo 0)
    n=$((n + 1))
    echo "$n" > "$PUSH_COUNT"
    if [ "$n" -le "$FAIL_PUSHES" ]; then
      echo "remote: fatal error in commit_refs" >&2
      echo " ! [remote rejected]     ops-metrics -> ops-metrics (failure)" >&2
      exit 1
    fi
    break
  fi
done
exec "$REAL_GIT" "$@"
"""


def _step_body() -> str:
    workflow = yaml.safe_load(RUN_OPS.read_text(encoding="utf-8"))
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if step.get("name") == STEP:
                return str(step["run"])
    raise AssertionError(f"run-ops has no step named {STEP!r}")


def _git(cwd: Path, *args: str, env: dict[str, str]) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, capture_output=True, text=True
    ).stdout


def _setup(tmp_path: Path, fail_pushes: int) -> tuple[Path, Path, dict[str, str]]:
    real_git = shutil.which("git")
    assert real_git is not None
    home = tmp_path / "home"
    home.mkdir()
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@users.noreply.github.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@users.noreply.github.com",
    }
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin), env=env)

    # A writer's clone seeds main and the orphan ops-metrics branch.
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", str(origin), str(seed), env=env)
    (seed / "README").write_text("main\n")
    _git(seed, "add", "-A", env=env)
    _git(seed, "commit", "-m", "main", env=env)
    _git(seed, "push", "origin", "HEAD:main", env=env)
    _git(seed, "checkout", "--orphan", "ops-metrics", env=env)
    _git(seed, "rm", "-rf", ".", env=env)
    (seed / "latest.json").write_text("{}\n")
    _git(seed, "add", "-A", env=env)
    _git(seed, "commit", "-m", "ops: snapshot old", env=env)
    _git(seed, "push", "origin", "ops-metrics", env=env)

    # The run's checkout, with origin/ops-metrics fetched as the step expects.
    work = tmp_path / "work"
    _git(tmp_path, "clone", str(origin), str(work), env=env)
    _git(
        work, "fetch", "origin", "+refs/heads/ops-metrics:refs/remotes/origin/ops-metrics", env=env
    )
    (work / "new-ops.json").write_text('{"day": "new"}\n')
    (work / "status.json").write_text('{"status": "new"}\n')

    # The validate writer advances the branch after the fetch.
    (seed / "corpus-validation.json").write_text('{"verdict": "pass"}\n')
    _git(seed, "add", "-A", env=env)
    _git(seed, "commit", "-m", "validate: corpus verdict", env=env)
    _git(seed, "push", "origin", "ops-metrics", env=env)

    shims = tmp_path / "shims"
    shims.mkdir()
    (shims / "git").write_text(GIT_SHIM)
    (shims / "sleep").write_text("#!/usr/bin/env bash\nexit 0\n")
    for shim in shims.iterdir():
        shim.chmod(0o755)
    runner_temp = tmp_path / "runner-temp"
    runner_temp.mkdir()
    run_env = {
        **env,
        "PATH": f"{shims}{os.pathsep}{env['PATH']}",
        "REAL_GIT": real_git,
        "FAIL_PUSHES": str(fail_pushes),
        "PUSH_COUNT": str(tmp_path / "push-count"),
        "RUNNER_TEMP": str(runner_temp),
        "REF_NAME": "main",
    }
    script = tmp_path / "step.sh"
    script.write_text(_step_body())
    return work, script, run_env


@pytest.mark.parametrize("fail_pushes", [0, 1, 2])
def test_an_advanced_branch_and_transient_failures_still_land_the_snapshot(
    tmp_path: Path, fail_pushes: int
) -> None:
    work, script, env = _setup(tmp_path, fail_pushes=fail_pushes)
    result = subprocess.run(
        ["bash", "-e", str(script)], check=False, cwd=work, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "::warning::ops-metrics push failed" in result.stdout
    origin = tmp_path / "origin.git"
    files = _git(origin, "ls-tree", "--name-only", "ops-metrics", env=env).split()
    assert {"corpus-validation.json", "latest.json", "status.json"} <= set(files)
    log = _git(origin, "log", "--format=%s", "ops-metrics", env=env).splitlines()
    assert log[0].startswith("ops: snapshot ")
    assert log[1] == "validate: corpus verdict"
    # The first push always fails (the advance, or the shim's blip); the
    # rebased retry after the last blip lands.
    assert (tmp_path / "push-count").read_text().strip() == str(max(fail_pushes, 1) + 1)


def test_a_push_that_never_succeeds_fails_the_step_loudly(tmp_path: Path) -> None:
    work, script, env = _setup(tmp_path, fail_pushes=100)
    result = subprocess.run(
        ["bash", "-e", str(script)], check=False, cwd=work, env=env, capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "::error::could not push the ops snapshot to ops-metrics after 5 attempts" in (
        result.stdout
    )
    assert (tmp_path / "push-count").read_text().strip() == "5"
