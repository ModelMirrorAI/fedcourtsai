"""The promotion-record writer: the workflow's shape, and its plumbing run end to end.

Two halves. The shape tests pin ``.github/workflows/promotion-record.yml``
against the writer requirements docs/process-version.md lists: what triggers
it, how a promotion merge is told from every other push to ``main``, which job
holds which permission, when the data App token exists and which step reads
it, the order tags → apply → commit → jail → push, and the refspecs.

The plumbing tests run ``.github/actions/promotion-record/write.sh`` against a
synthetic promotion (the history ``tests/test_promotion_record.py`` builds) with
a local bare repository standing in for GitHub, so the fetch, the plan, the
local tags, the apply, the one-parent commit, the jail and the push — and the
re-plan when ``main`` advances under it — run against git rather than a
stand-in. A shim maps ``uv run --locked fedcourts`` onto this environment's
``fedcourts``, so the code the script runs is the code under test.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from fedcourtsai.promotion_record import FREEZE_RECORD_PATH, REGISTRY_PATH, tag_message
from tests.test_promotion_record import MERGED_AT, _git, _promote

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "promotion-record.yml"
WRITER = ROOT / ".github" / "actions" / "promotion-record" / "write.sh"


def _workflow() -> dict[Any, Any]:
    data: dict[Any, Any] = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return data


def _steps(job: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = _workflow()["jobs"][job]["steps"]
    return steps


def _step(job: str, name: str) -> dict[str, Any]:
    return next(step for step in _steps(job) if step.get("name") == name)


def _index(job: str, predicate: Any) -> int:
    return next(i for i, step in enumerate(_steps(job)) if predicate(step))


# --- the workflow's shape ----------------------------------------------------


def test_it_runs_on_a_push_to_main_and_on_a_recovery_dispatch_only() -> None:
    triggers = _workflow()[True]  # yaml reads the bare `on:` key as a boolean
    assert set(triggers) == {"push", "workflow_dispatch"}
    assert triggers["push"] == {"branches": ["main"]}
    assert set(triggers["workflow_dispatch"]["inputs"]) == {"merge"}
    assert _workflow()["permissions"] == {}


def test_classify_holds_no_secret_and_only_read_scopes() -> None:
    job = _workflow()["jobs"]["classify"]
    assert job["permissions"] == {"contents": "read", "pull-requests": "read"}
    assert "environment" not in job
    text = yaml.safe_dump(job)
    assert "secrets." not in text and "vars." not in text


def test_classify_requires_a_two_parent_merge_of_a_same_repo_staging_to_main_pr() -> None:
    run = _step("classify", "Classify the pushed commit")["run"]
    # A dispatch input is refused unless it is a full SHA, before any API call.
    assert "^[0-9a-f]{40}$" in run
    assert run.index("^[0-9a-f]{40}$") < run.index("gh api")
    # Two parents; on a push, the first parent is the tip the push replaced.
    assert '"${#parent_list[@]}" -ne 2' in run
    assert '"${parent_list[0]}" != "$BEFORE"' in run
    # The commit closed exactly one merged PR, base main, head staging, same repo,
    # whose merge commit is this one.
    for clause in (
        ".merged_at != null",
        '.base.ref == \\"main\\"',
        '.head.ref == \\"staging\\"',
        '.head.repo.full_name == \\"${REPO}\\"',
        '.merge_commit_sha == \\"${sha}\\"',
        "if length == 1",
    ):
        assert clause in run, clause
    # Anything else stops green, writing nothing.
    assert "not a promotion merge" in run and "exit 0" in run


def test_write_runs_only_for_a_promotion_on_prod_in_its_own_concurrency_group() -> None:
    job = _workflow()["jobs"]["write"]
    assert job["if"] == "needs.classify.outputs.promotion == 'true'"
    assert job["environment"] == "prod"
    assert job["concurrency"] == {"group": "promotion-record", "cancel-in-progress": False}
    assert job["permissions"] == {"contents": "read"}


def test_write_checks_out_main_without_persisted_credentials() -> None:
    checkout = _steps("write")[0]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"] == {"ref": "main", "persist-credentials": False, "fetch-depth": 0}
    setup = next(s for s in _steps("write") if "setup-python-env" in str(s.get("uses", "")))
    assert setup["with"] == {"restore-cache": "false"}


ATTEMPTS = (1, 2, 3)


def test_each_attempt_mints_after_its_jail_and_only_its_push_and_revoke_read_the_token() -> None:
    steps = _steps("write")
    for n in ATTEMPTS:
        prepare = _index("write", lambda s, n=n: s.get("id") == f"prepare{n}")
        validate = _index("write", lambda s, n=n: s.get("id") == f"validate{n}")
        mint = _index("write", lambda s, n=n: s.get("id") == f"app-token-{n}")
        push = _index("write", lambda s, n=n: s.get("id") == f"push{n}")
        assert prepare < validate < mint < push, n
        assert steps[mint]["uses"].startswith("actions/create-github-app-token@")
        assert steps[mint]["with"] == {
            "client-id": "${{ vars.DATA_APP_CLIENT_ID }}",
            "private-key": "${{ secrets.DATA_APP_PRIVATE_KEY }}",
            "permission-contents": "write",
        }
        readers = [
            step.get("id") or step.get("name")
            for step in steps
            if f"steps.app-token-{n}.outputs" in yaml.safe_dump(step)
        ]
        expected = (
            [f"push{n}"]
            + ([f"Revoke the attempt-{n} token"] if n < 3 else [])
            + ["Revoke the remaining tokens"]
        )
        assert readers == expected, (n, readers)
        # Prepare and validate — fetch, plan, tag, apply, commit, jail — hold no secret
        # and read no token.
        for index in (prepare, validate):
            dumped = yaml.safe_dump(steps[index])
            assert "secrets." not in dumped and "app-token" not in dumped, n
        assert steps[prepare]["run"] == (
            'bash .github/actions/promotion-record/write.sh prepare "$MERGE"'
        )
        assert steps[validate]["run"] == "bash .github/actions/promotion-record/write.sh validate"
        run = steps[push]["run"]
        assert "bash .github/actions/promotion-record/write.sh push" in run
        assert '"$APP_SLUG" != "fedcourtsai-data"' in run
        # A lease rejection records `rejected` for the next attempt; nothing re-plans here.
        assert '"$status" -eq 3' in run and "rejected=true" in run
        assert "prepare" not in run
        assert steps[push]["env"]["BASE"] == f"${{{{ steps.validate{n}.outputs.base }}}}"


def test_a_later_attempt_runs_only_after_a_rejection_and_revokes_the_last_token_first() -> None:
    steps = _steps("write")
    for n in (2, 3):
        group = [
            step
            for step in steps
            if step.get("id") in {f"prepare{n}", f"validate{n}", f"app-token-{n}", f"push{n}"}
            or step.get("name") == f"Revoke the attempt-{n - 1} token"
        ]
        assert len(group) == 5
        assert {step.get("if") for step in group} == {
            f"steps.push{n - 1}.outputs.rejected == 'true'"
        }
        revoke = _index(
            "write", lambda s, n=n: s.get("name") == f"Revoke the attempt-{n - 1} token"
        )
        prepare = _index("write", lambda s, n=n: s.get("id") == f"prepare{n}")
        assert revoke < prepare
        assert "-X DELETE" in steps[revoke]["run"] and "installation/token" in steps[revoke]["run"]
    remaining = _step("write", "Revoke the remaining tokens")
    assert remaining["if"] == "always()"
    assert _steps("write").index(remaining) > _index("write", lambda s: s.get("id") == "push3")
    for n in ATTEMPTS:
        assert f"$TOKEN_{n}" in remaining["run"], n
    final = _step("write", "Refuse a record main kept outrunning")
    assert final["if"] == "steps.push3.outputs.rejected == 'true'" and "exit 1" in final["run"]
    upload = _step("write", "Upload the plan")
    assert upload["if"] == "always()"
    assert _steps("write").index(upload) > _index("write", lambda s: s.get("id") == "push3")


def test_report_rides_the_ambient_token_and_triggers_nothing() -> None:
    job = _workflow()["jobs"]["report"]
    assert job["needs"] == ["classify", "write"]
    assert job["if"] == "always() && needs.classify.outputs.promotion == 'true'"
    assert job["permissions"] == {"issues": "write", "pull-requests": "write"}
    text = yaml.safe_dump(job)
    assert "secrets." not in text and "environment" not in job
    run = _step("report", "Surface what the plan left for a maintainer")["run"]
    for group in ("free_text", "stale_placeholders", "stale_pending"):
        assert f".{group}" in run, group


def test_the_writer_orders_tags_apply_commit_jail_and_pushes_by_explicit_refspec() -> None:
    text = WRITER.read_text(encoding="utf-8")
    body = text[text.index("prepare() {") : text.index("validate() {")]
    order = [
        "fetch\n",
        "promotion-record --merge",
        "tag_locally",
        "--apply",
        "git commit",
        "assert-promotion-record-diff",
        '>"$state"',
    ]
    positions = [body.index(marker) for marker in order]
    assert positions == sorted(positions), order
    push = text[text.index("push() {") :]
    assert '"refs/tags/${name}:refs/tags/${name}"' in push
    assert '"${head}:refs/heads/main"' in push
    assert '--force-with-lease="refs/heads/main:${base}"' in push
    assert not re.search(r"push[^\n]*(--force(?!-with-lease)|\s-f\b)", text)
    # Tags are pushed before the record commit.
    assert push.index("refs/tags/") < push.index("refs/heads/main")
    # The push never plans: a lease rejection is exit 3, for the next attempt.
    assert "prepare" not in push.split("case ")[0]
    assert "return 3" in push
    # Remote-tracking refs, never local branches, and every tag.
    assert "refs=(--main-ref origin/main --staging-ref origin/staging)" in text
    assert "--tags" in text


def test_the_writer_never_puts_the_token_in_a_url_or_a_config_file() -> None:
    text = WRITER.read_text(encoding="utf-8")
    assert "x-access-token:${" not in text.replace("x-access-token:%s", "")
    assert "git config" not in text
    assert "extraheader=" in text
    # Every push blanks an ambient header first and runs no hook.
    assert "-c core.hooksPath=/dev/null -c http.extraHeader=" in text
    assert "push --no-verify" in text


# --- the plumbing, end to end ------------------------------------------------


def _shim(tmp_path: Path) -> Path:
    """A ``uv`` on PATH that runs this environment's ``fedcourts`` for ``uv run --locked``."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fedcourts = Path(sys.executable).with_name("fedcourts")
    shim = bin_dir / "uv"
    shim.write_text(
        "#!/usr/bin/env bash\n"
        'if [ "$1" = run ] && [ "$2" = --locked ] && [ "$3" = fedcourts ]; then\n'
        f'  shift 3; exec "{fedcourts}" "$@"\n'
        "fi\n"
        'echo "unexpected uv call: $*" >&2; exit 2\n',
        encoding="utf-8",
    )
    shim.chmod(0o700)
    return bin_dir


def _setup(tmp_path: Path) -> tuple[Path, Path, str, dict[str, str]]:
    """A synthetic promotion pushed to a bare remote, and a fresh checkout of it."""
    repo, merge = _promote(tmp_path)
    remote = tmp_path / "remote.git"
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    _git(repo, "push", "-q", str(remote), "main", "staging")
    work = tmp_path / "work"
    _git(tmp_path, "clone", "-q", str(remote), str(work))
    _git(work, "config", "user.email", "writer@users.noreply.github.com")
    _git(work, "config", "user.name", "writer")
    _git(work, "config", "core.autocrlf", "false")
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    env = {
        **os.environ,
        "PATH": f"{_shim(tmp_path)}{os.pathsep}{os.environ['PATH']}",
        "GITHUB_REPOSITORY": "owner/repo",
        "RUNNER_TEMP": str(runner_temp),
        "GITHUB_OUTPUT": str(tmp_path / "output"),
        "PROMOTION_RECORD_REMOTE": str(remote),
    }
    return work, remote, merge, env


def _run(work: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRITER), *args],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _outputs(env: dict[str, str]) -> dict[str, str]:
    lines = Path(env["GITHUB_OUTPUT"]).read_text(encoding="utf-8").splitlines()
    return dict(line.split("=", 1) for line in lines)


def _validate(work: Path, env: dict[str, str]) -> dict[str, str]:
    Path(env["GITHUB_OUTPUT"]).write_text("", encoding="utf-8")
    validated = _run(work, env, "validate")
    assert validated.returncode == 0, validated.stderr + validated.stdout
    return _outputs(env)


def _push(work: Path, env: dict[str, str], outputs: dict[str, str]) -> Any:
    return _run(
        work,
        {
            **env,
            "WRITE_TOKEN": "unused-by-a-file-remote",
            "BASE": outputs["base"],
            "HEAD_SHA": outputs["head"],
        },
        "push",
    )


def _prepare_and_push(work: Path, env: dict[str, str], merge: str) -> dict[str, str]:
    prepared = _run(work, env, "prepare", merge)
    assert prepared.returncode == 0, prepared.stderr + prepared.stdout
    outputs = _validate(work, env)
    pushed = _push(work, env, outputs)
    assert pushed.returncode == 0, pushed.stderr + pushed.stdout
    return outputs


def test_the_writer_records_a_promotion_end_to_end(tmp_path: Path) -> None:
    work, remote, merge, env = _setup(tmp_path)
    outputs = _prepare_and_push(work, env, merge)
    head = _git(remote, "rev-parse", "main")
    # The record commit is the jailed one, with exactly one parent: the merge.
    assert head == outputs["head"]
    assert _git(remote, "rev-list", "--parents", "-n", "1", head).split() == [head, merge]
    # The tag names the merge, annotated, carrying the plan's message.
    assert _git(remote, "rev-parse", "promotion/2026-10-13^{commit}") == merge
    plan_file = Path(env["RUNNER_TEMP"]) / "promotion-record" / "plan.json"
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    assert tag_message(remote, "promotion/2026-10-13") == plan["promotion_tag"]["message"]
    assert _git(remote, "rev-parse", "prereg/proc-v10^{commit}") == merge
    # The fills and stamps landed: the merge's SHA and committer time on main.
    record = _git(remote, "show", f"main:{FREEZE_RECORD_PATH}")
    when = MERGED_AT.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert f"merge\n  commit `{merge}`, merged `{when}`" in record
    assert "`<FILL: apply run id>`" in record  # free text is never filled
    registry = json.loads(_git(remote, "show", f"main:{REGISTRY_PATH}"))
    assert registry["labels"][-1]["since"] == {"at": when, "merge": merge, "source": "merge"}


def test_a_second_run_adopts_the_tags_and_commits_nothing(tmp_path: Path) -> None:
    work, remote, merge, env = _setup(tmp_path)
    _prepare_and_push(work, env, merge)
    head = _git(remote, "rev-parse", "main")
    again = _run(work, env, "prepare", merge)
    # The record commit already landed, so the merge's placeholders and pending
    # rows are gone from main's tip: the re-plan stamps nothing and fills nothing.
    assert again.returncode == 0, again.stderr + again.stdout
    assert "adopting promotion/2026-10-13" in again.stdout
    assert _validate(work, env)["head"] == ""
    assert _git(remote, "rev-parse", "main") == head


def _advance_main(tmp_path: Path, remote: Path) -> str:
    """A data commit lands on main from elsewhere; returns the new tip."""
    other = tmp_path / "other"
    _git(tmp_path, "clone", "-q", str(remote), str(other))
    _git(other, "config", "user.email", "data@users.noreply.github.com")
    _git(other, "config", "user.name", "data")
    (other / "data.txt").write_text("a data commit\n", encoding="utf-8")
    _git(other, "add", "data.txt")
    _git(other, "commit", "-q", "-m", "data")
    _git(other, "push", "-q", "origin", "main")
    return _git(remote, "rev-parse", "main")


def test_main_advancing_rejects_the_push_and_the_next_attempt_re_plans(tmp_path: Path) -> None:
    work, remote, merge, env = _setup(tmp_path)
    assert _run(work, env, "prepare", merge).returncode == 0
    first = _validate(work, env)
    advanced = _advance_main(tmp_path, remote)
    rejected = _push(work, env, first)
    # The push never re-plans: it reports the rejection as exit 3 and stops.
    assert rejected.returncode == 3, rejected.stderr + rejected.stdout
    assert _git(remote, "rev-parse", "main") == advanced
    # The next attempt prepares from scratch on the new tip, holding no token.
    retried = _prepare_and_push(work, env, merge)
    head = _git(remote, "rev-parse", "main")
    assert head == retried["head"] != first["head"]
    assert _git(remote, "rev-list", "--parents", "-n", "1", head).split() == [head, advanced]


def test_a_re_prepare_whose_jail_refuses_pushes_nothing(tmp_path: Path) -> None:
    """A refused re-plan ends the attempt: no state file, so no validate and no push."""
    work, remote, merge, env = _setup(tmp_path)
    assert _run(work, env, "prepare", merge).returncode == 0
    first = _validate(work, env)
    advanced = _advance_main(tmp_path, remote)
    assert _push(work, env, first).returncode == 3
    # From now on the jail refuses.
    shim = Path(env["PATH"].split(os.pathsep)[0]) / "uv"
    honest = shim.read_text(encoding="utf-8")
    shim.write_text(
        honest.replace(
            "shift 3;",
            'shift 3; if [ "$1" = assert-promotion-record-diff ]; then '
            + 'echo "JAIL REFUSED" >&2; exit 1; fi;',
        ),
        encoding="utf-8",
    )
    again = _run(work, env, "prepare", merge)
    assert again.returncode != 0 and "JAIL REFUSED" in again.stderr
    Path(env["GITHUB_OUTPUT"]).write_text("", encoding="utf-8")
    assert _run(work, env, "validate").returncode != 0
    assert _git(remote, "rev-parse", "main") == advanced
    # A later attempt, the jail honest again, re-plans onto the advanced tip and lands.
    shim.write_text(honest, encoding="utf-8")
    recovered = _prepare_and_push(work, env, merge)
    head = _git(remote, "rev-parse", "main")
    assert head == recovered["head"]
    assert _git(remote, "rev-list", "--parents", "-n", "1", head).split() == [head, advanced]


def test_validate_refuses_a_record_commit_off_the_base(tmp_path: Path) -> None:
    work, _remote, merge, env = _setup(tmp_path)
    assert _run(work, env, "prepare", merge).returncode == 0
    state = Path(env["RUNNER_TEMP"]) / "promotion-record" / "state"
    lines = state.read_text(encoding="utf-8").splitlines()
    state.write_text(f"{lines[0]}\nhead={merge}\n", encoding="utf-8")
    refused = _run(work, env, "validate")
    assert refused.returncode != 0 and "only parent" in refused.stdout


def test_a_date_another_commit_holds_takes_the_next_suffix(tmp_path: Path) -> None:
    work, remote, merge, env = _setup(tmp_path)
    # The canonical name was already taken by another commit before the writer ran.
    _git(remote, "tag", "-a", "promotion/2026-10-13", "-m", "earlier", "staging")
    _prepare_and_push(work, env, merge)
    assert _git(remote, "rev-parse", "promotion/2026-10-13-2^{commit}") == merge
    assert _git(remote, "rev-parse", "promotion/2026-10-13^{commit}") != merge


def test_a_tag_planted_between_prepare_and_push_is_refused_not_replaced(tmp_path: Path) -> None:
    work, remote, merge, env = _setup(tmp_path)
    assert _run(work, env, "prepare", merge).returncode == 0
    outputs = _validate(work, env)
    planted = _git(remote, "rev-parse", "staging")
    _git(remote, "tag", "-a", "promotion/2026-10-13", "-m", "planted", planted)
    pushed = _push(work, env, outputs)
    assert pushed.returncode not in (0, 3)
    assert "already exists" in pushed.stderr + pushed.stdout
    # The remote tag is untouched and the record commit never pushed.
    assert _git(remote, "rev-parse", "promotion/2026-10-13^{commit}") == planted
    assert _git(remote, "rev-parse", "main") == merge


def test_a_push_that_is_not_a_promotion_merge_is_refused(tmp_path: Path) -> None:
    work, _remote, _merge, env = _setup(tmp_path)
    staging_tip = _git(work, "rev-parse", "origin/staging")
    prepared = _run(work, env, "prepare", staging_tip)
    assert prepared.returncode != 0
    assert "promotion" in (prepared.stderr + prepared.stdout)


@pytest.mark.parametrize("subcommand", ["", "bogus"])
def test_the_writer_refuses_an_unknown_subcommand(tmp_path: Path, subcommand: str) -> None:
    work, _remote, _merge, env = _setup(tmp_path)
    assert _run(work, env, *([subcommand] if subcommand else [])).returncode == 2


def test_no_repo_code_runs_in_the_write_job_after_its_last_token() -> None:
    """The pending-row check runs in `report`, which holds no data App credential."""
    steps = _steps("write")
    remaining = _index("write", lambda s: s.get("name") == "Revoke the remaining tokens")
    for step in steps[remaining + 1 :]:
        run = step.get("run", "")
        assert "uv run" not in run and "write.sh" not in run, step.get("name")
    assert not any("--check-main" in step.get("run", "") for step in steps)
    check = _step("report", "Check main holds no pending registration")
    assert "promotion-record --check-main origin/main" in check["run"]
    assert "env" not in check
    report = _workflow()["jobs"]["report"]
    assert "environment" not in report and "secrets." not in yaml.safe_dump(report)
    setup = next(s for s in _steps("report") if "setup-python-env" in str(s.get("uses", "")))
    assert setup["with"] == {"restore-cache": "false"}
