"""The run gate (:mod:`fedcourtsai.run_gate`): its decision, its allow-list, and
its isolation.

The workflow shape — that the gate opens and closes every gated workflow and
every job between waits on it — is ``test_workflow_auth_gate.py``'s. This
exercises the *decision*: a dispatch needs a listed human or a bot listed for
that workflow, a re-run needs a listed human, an unchosen first attempt of a
known event passes, and anything unreadable — the context, the event, the
allow-list — refuses. It also pins what makes the gate the maintainer's alone:
the module imports nothing but the standard library and runs by path under
``python3 -I -S`` from a checkout holding only itself and the allow-list.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from fedcourtsai import run_gate
from fedcourtsai.run_gate import (
    DISPATCHERS_PATH,
    Dispatchers,
    DispatchersError,
    decide,
    load_dispatchers,
    main,
    parse_dispatchers,
)

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "src" / "fedcourtsai" / "run_gate.py"

MAINTAINER = "maintainer"
AGENT = "agent-account"
DISPATCH_BOT = "pipeline-dispatch[bot]"

CONFIG = Dispatchers(humans=(MAINTAINER,), bots={"run-predict.yml": (DISPATCH_BOT,)})


def _decide(
    *,
    event: str = "workflow_dispatch",
    actor: str = MAINTAINER,
    triggering: str | None = None,
    attempt: str = "1",
    workflow: str = "run-predict.yml",
    config: Dispatchers = CONFIG,
) -> bool:
    return decide(
        event_name=event,
        actor=actor,
        triggering_actor=actor if triggering is None else triggering,
        run_attempt=attempt,
        workflow_file=workflow,
        config=config,
    ).authorized


# --- The decision -----------------------------------------------------------


def test_a_listed_human_may_dispatch_any_gated_workflow() -> None:
    assert _decide(workflow="run-predict.yml")
    assert _decide(workflow="run-pull.yml")


def test_an_unlisted_dispatcher_is_refused_and_named() -> None:
    decision = decide(
        event_name="workflow_dispatch",
        actor=AGENT,
        triggering_actor=AGENT,
        run_attempt="1",
        workflow_file="run-pull.yml",
        config=CONFIG,
    )
    assert not decision.authorized
    assert AGENT in decision.message
    assert "run-pull.yml" in decision.message


def test_logins_compare_case_insensitively() -> None:
    """GitHub logins are case-insensitive, and the context may carry either case."""
    assert _decide(actor=MAINTAINER.upper())
    assert _decide(actor=DISPATCH_BOT.upper())


def test_a_pipeline_bot_may_dispatch_only_the_workflow_listed_for_it() -> None:
    assert _decide(actor=DISPATCH_BOT, workflow="run-predict.yml")
    assert not _decide(actor=DISPATCH_BOT, workflow="run-evaluate.yml")
    assert not _decide(actor=DISPATCH_BOT, workflow="run-pull.yml")


def test_a_pipeline_bot_never_re_runs() -> None:
    """Even the workflow it may dispatch: a bot's re-run is refused."""
    assert not _decide(actor=DISPATCH_BOT, triggering=DISPATCH_BOT, attempt="2")


def test_a_maintainer_may_re_run_a_chained_round() -> None:
    assert _decide(actor=DISPATCH_BOT, triggering=MAINTAINER, attempt="2")


def test_the_agent_may_not_re_run_anything() -> None:
    for event in ("workflow_dispatch", "schedule", "push", "pull_request"):
        assert not _decide(event=event, actor=MAINTAINER, triggering=AGENT, attempt="2"), event


def test_a_re_run_does_not_launder_an_unlisted_dispatch() -> None:
    """The dispatch rule binds at every attempt: `actor` stays the dispatcher's,
    so a listed human re-running an unlisted login's dispatch is still refused."""
    assert not _decide(actor=AGENT, triggering=MAINTAINER, attempt="2")


def test_an_unchosen_first_attempt_passes_whoever_the_actor() -> None:
    for event in ("schedule", "push", "pull_request"):
        assert _decide(event=event, actor=AGENT, attempt="1"), event
        assert _decide(event=event, actor="", triggering="", attempt="1"), event


@pytest.mark.parametrize(
    "event",
    [
        "repository_dispatch",
        "workflow_run",
        "workflow_call",
        "pull_request_target",
        "issues",
        "",
        "Schedule",
    ],
)
def test_an_event_the_gate_does_not_name_refuses(event: str) -> None:
    """Fail closed on the event too: a trigger added later is refused until the
    gate names it, even on a first attempt by a listed human."""
    decision = decide(
        event_name=event,
        actor=MAINTAINER,
        triggering_actor=MAINTAINER,
        run_attempt="1",
        workflow_file="run-predict.yml",
        config=CONFIG,
    )
    assert not decision.authorized
    assert "refusing to run" in decision.message


def test_a_re_run_of_a_scheduled_run_needs_a_listed_human() -> None:
    assert _decide(event="schedule", actor=AGENT, triggering=MAINTAINER, attempt="3")
    assert not _decide(event="schedule", actor=MAINTAINER, triggering=AGENT, attempt="3")


@pytest.mark.parametrize("attempt", ["", " ", "0", "-1", "two", "1.5", "²"])
def test_an_unparseable_attempt_refuses(attempt: str) -> None:
    assert not _decide(event="schedule", attempt=attempt)


def test_a_blank_dispatcher_refuses() -> None:
    assert not _decide(actor="", triggering=MAINTAINER)
    assert not _decide(actor="   ", triggering=MAINTAINER)


def test_a_blank_re_runner_refuses() -> None:
    assert not _decide(event="schedule", triggering="", attempt="2")


def test_a_blank_workflow_refuses() -> None:
    assert not _decide(workflow="")


def test_an_empty_allow_list_refuses_every_dispatch_and_re_run() -> None:
    empty = Dispatchers(humans=())
    assert not _decide(config=empty)
    assert not _decide(event="schedule", attempt="2", config=empty)
    assert _decide(event="schedule", config=empty)


def test_the_rerunner_list_is_comma_delimited_at_both_ends() -> None:
    """The re-run guard matches `,<login>,` against it, so each login must sit
    between delimiters, and an empty list must not read as `,,` (which a blank
    triggering actor would format to)."""
    assert Dispatchers(humans=("a", "b-c")).rerunner_list() == ",a,b-c,"
    assert Dispatchers(humans=()).rerunner_list() == ""
    rerunners = Dispatchers(humans=("modelmirror",)).rerunner_list()
    assert ",modelmirror-agent," not in rerunners
    assert ",mirror," not in rerunners


# --- The allow-list ---------------------------------------------------------


def test_the_parser_reads_a_well_formed_file() -> None:
    text = '{"humans": ["maintainer"], "bots": {"run-predict.yml": ["pipeline-dispatch[bot]"]}}'
    assert parse_dispatchers(text) == CONFIG
    assert parse_dispatchers('{"humans": []}') == Dispatchers(humans=())


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty file"),
        pytest.param('["maintainer"]', id="not an object"),
        pytest.param('{"bots": {}}', id="no humans key"),
        pytest.param('{"humans": "maintainer"}', id="humans not a list"),
        pytest.param('{"humans": [1]}', id="login not a string"),
        pytest.param('{"humans": ["maintainer"], "human": ["x"]}', id="unknown key"),
        pytest.param('{"humans": ["a"], "humans": ["b"]}', id="duplicate top-level key"),
        pytest.param(
            '{"humans": [], "bots": {"run-predict.yml": ["a[bot]"], "run-predict.yml": []}}',
            id="duplicate workflow key",
        ),
        pytest.param('{"humans": ["pipeline-dispatch[bot]"]}', id="bot listed as human"),
        pytest.param('{"humans": ["a,b"]}', id="comma in a login"),
        pytest.param('{"humans": ["-lead"]}', id="leading hyphen"),
        pytest.param('{"humans": [""]}', id="blank login"),
        pytest.param('{"humans": ["Maintainer", "maintainer"]}', id="duplicate login"),
        pytest.param('{"humans": [], "bots": ["x[bot]"]}', id="bots not an object"),
        pytest.param('{"humans": [], "bots": {"run-predict.yml": ["maint"]}}', id="bot not [bot]"),
        pytest.param('{"humans": [], "bots": {"run-predict": ["x[bot]"]}}', id="bad workflow"),
        pytest.param('{"humans": ["maintainer"]', id="not JSON"),
    ],
)
def test_the_parser_refuses_a_malformed_file(text: str) -> None:
    with pytest.raises(DispatchersError):
        parse_dispatchers(text)


def test_the_loader_refuses_a_missing_file(tmp_path: Path) -> None:
    """No default allow-list: an unreadable file must refuse, never admit."""
    with pytest.raises(DispatchersError, match="cannot read"):
        load_dispatchers(tmp_path / "dispatchers.json")


def test_the_committed_allow_list_loads() -> None:
    config = load_dispatchers(ROOT / DISPATCHERS_PATH)
    assert config.humans


def test_the_committed_allow_list_admits_the_train_dispatch_and_nothing_wider() -> None:
    """The dispatch App may start integration-test (the promotion train's gate
    suite) and run-predict (the chained rounds), as a first attempt only: it
    re-runs nothing, and it starts no other gated workflow."""
    config = load_dispatchers(ROOT / DISPATCHERS_PATH)
    bot = "fedcourtsai-dispatch[bot]"

    def allowed(workflow: str, attempt: str = "1", triggering: str = bot) -> bool:
        return decide(
            event_name="workflow_dispatch",
            actor=bot,
            triggering_actor=triggering,
            run_attempt=attempt,
            workflow_file=workflow,
            config=config,
        ).authorized

    assert allowed("integration-test.yml")
    assert allowed("run-predict.yml")
    assert not allowed("integration-test.yml", attempt="2")
    for workflow in ("run-pull.yml", "run-evaluate.yml", "promotion-prep.yml", "run-repair.yml"):
        assert not allowed(workflow), workflow


# --- The entry point --------------------------------------------------------


def _argv(config: Path, *, actor: str, attempt: str = "1") -> list[str]:
    return [
        *("--workflow", "run-predict.yml"),
        *("--event-name", "workflow_dispatch"),
        *("--actor", actor),
        *("--triggering-actor", actor),
        *("--run-attempt", attempt),
        *("--config", str(config)),
    ]


def test_main_authorizes_and_publishes_the_attempt_and_re_runners(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = tmp_path / "dispatchers.json"
    config.write_text('{"humans": ["maintainer", "deputy"]}')
    output = tmp_path / "github_output"
    output.write_text("earlier=kept\n")
    code = main([*_argv(config, actor="deputy", attempt="2"), "--github-output", str(output)])
    assert code == 0
    assert "Authorized run-predict.yml" in capsys.readouterr().out
    assert output.read_text() == "earlier=kept\nattempt=2\nrerunners=,maintainer,deputy,\n"


def test_main_refuses_with_a_workflow_error_and_writes_no_outputs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = tmp_path / "dispatchers.json"
    config.write_text('{"humans": ["maintainer"]}')
    output = tmp_path / "github_output"
    assert main([*_argv(config, actor=AGENT), "--github-output", str(output)]) == 1
    err = capsys.readouterr().err
    assert err.startswith("::error::") and AGENT in err
    assert not output.exists()


def test_main_refuses_on_a_missing_allow_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(_argv(tmp_path / "absent.json", actor=MAINTAINER)) == 1
    err = capsys.readouterr().err
    assert err.startswith("::error::") and "refusing to run" in err


# --- Isolation --------------------------------------------------------------


def test_the_module_imports_only_the_standard_library() -> None:
    """Every import is a top-level stdlib module (or `__future__`), and none is
    relative: the gate must not run any code the package, its dependencies or
    its lockfile decide, since none of those are owned by the maintainer."""
    tree = ast.parse(MODULE.read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0 and node.module, "run_gate.py makes a relative import"
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and getattr(node.func, "id", "") == "__import__":
            pytest.fail("run_gate.py imports dynamically")
    allowed = set(sys.stdlib_module_names) | {"__future__"}
    assert imported <= allowed, f"non-stdlib imports: {sorted(imported - allowed)}"
    assert "importlib" not in imported


def test_the_module_runs_by_path_from_a_checkout_of_itself_and_the_allow_list(
    tmp_path: Path,
) -> None:
    """The authorize job's exact shape: a sparse checkout holding only the gate
    and the allow-list, run by path under `-I -S` (no site packages, user or
    system, no script directory on the path, no PYTHON* environment), from
    the checkout root."""
    gate = tmp_path / "src" / "fedcourtsai" / "run_gate.py"
    gate.parent.mkdir(parents=True)
    gate.write_text(MODULE.read_text())
    allow_list = tmp_path / DISPATCHERS_PATH
    allow_list.parent.mkdir(parents=True)
    allow_list.write_text((ROOT / DISPATCHERS_PATH).read_text())
    human = load_dispatchers(allow_list).humans[0]
    output = tmp_path / "out"

    def run(actor: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                "src/fedcourtsai/run_gate.py",
                *("--workflow", "run-predict.yml"),
                *("--event-name", "workflow_dispatch"),
                *("--actor", actor),
                *("--triggering-actor", actor),
                *("--run-attempt", "1"),
                *("--github-output", str(output)),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    allowed = run(human)
    assert allowed.returncode == 0, allowed.stderr
    assert output.read_text().startswith("attempt=1\nrerunners=,")
    refused = run("modelmirror-agent")
    assert refused.returncode == 1
    assert refused.stderr.startswith("::error::")


def test_the_module_is_its_own_entry_point() -> None:
    assert run_gate.__name__ == "fedcourtsai.run_gate"
    assert 'if __name__ == "__main__":' in MODULE.read_text()
