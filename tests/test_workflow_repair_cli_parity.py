"""`run-repair`'s embedded CLI strings, executed against the fixture corpus.

`run-repair.yml` is dispatch-only, so its eleven maintenance passes are argv that
nothing runs until a maintainer runs one — in front of the maintainer, at the
moment they most want it to work. A flag renamed in `cli.py` leaves the workflow
string behind, and the whole cost of that drift lands on the dispatch as a usage
error, after an App token has been minted, a role assumed and the corpus-write
lock taken. The workflow linters cannot see it: to `actionlint` the string is
opaque shell, and to the Python gate the workflow is not code.

These tests close the seam. Each pass's argv is read back out of the workflow
rather than retyped here — a copy would drift exactly as the workflow does — its
selector inputs are filled with representative values, and the command is
executed against the offline fixture corpus. What they prove is *parity*, not a
pass's behaviour: every flag the workflow passes still exists and still parses.
Some tests go a step further, where a pass couples to something argv parity
cannot see. The qp pass's convergence gate couples to the CLI's *output
wording*: that test replays the step's own invocations over a purpose-seeded
corpus and asserts the workflow's grepped literal against the converged summary.
The two fetching passes' slice deadlines couple to a *number in the same step* —
each is the step's `timeout-minutes` less what the step must still do once the
pass stops taking work — and nothing at runtime holds the two together, so those
tests read both out of the YAML and assert the difference. The document
back-fill's write witness couples to *field names* in a shell JSON pipeline no
type checker sees, so a third reads them back against the ledger model.
The passes' own semantics are pinned at their unit seams
(`tests/test_dedupe.py`, `tests/test_distribution_rederive.py`,
`tests/test_docket_marking_migration.py`, `tests/test_response_backfill.py`,
`tests/test_attribution_migration.py`, `tests/test_disposition_convergence.py`,
`tests/test_sampled_frame_repair.py`, `tests/test_documents.py`,
`tests/test_document_backfill.py` and
`tests/test_cli_stamp.py`), which is why a
near-empty fixture corpus is enough here — a pass with nothing to do still
parses every flag it was given.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.cli import app
from fedcourtsai.pipeline.document_backfill import (
    DocumentBackfillResult,
    estimated_candidate_seconds,
)
from fedcourtsai.pipeline.ocr_recovery import (
    DOCUMENT_BUDGET_SECONDS,
    ESTIMATED_CANDIDATE_OVERHEAD_SECONDS,
)
from tests.conftest import seed_evaluation, seed_prediction
from tests.test_documents import _seed_qp_backfill_corpus
from tests.workflow_argv import command_argv, expand, logical_lines, shell_arrays

ROOT = Path(__file__).resolve().parent.parent
RUN_REPAIR = ROOT / ".github" / "workflows" / "run-repair.yml"

#: The token sequence a workflow step names the CLI with.
FEDCOURTS = ("uv", "run", "fedcourts")

#: The blast-radius bound a maintainer reads off a dry-run ledger. Any positive
#: integer serves — the workflow's own grammar is `^[1-9][0-9]*$` — since what
#: is under test is that the flag carrying it still exists.
REPAIR_BOUND = "1"

#: A *registered* distribution parse. The re-derivation refuses an unregistered
#: label with its own error (`tests/test_distribution_rederive.py`), so an
#: unregistered stand-in would mask a renamed `--parse` behind a refusal.
REPAIR_PARSE_LABEL = "dist-v2"

#: One re-grade subject, in the `court/docket/event/run_id/actor` grammar the
#: workflow greps a dispatch's cell list against. Asserted against that pattern
#: below, so this literal cannot drift from what a dispatch would accept.
REGRADE_CELL = "scotus/1/evt-petition-disposition/20260101T000000Z/claude-judge"

#: Invocations that move the blob itself. They reach the S3 corpus remote, which
#: the offline gate holds no credentials for and must not acquire — so their
#: bodies are never run. Their *argv* still is, with ``--help`` appended: Click
#: parses every option before the eager help callback fires, so a renamed flag
#: on one of these is still exit 2 here rather than a usage error mid-dispatch.
#: Skipping them outright would leave `--missing-pointer` checked nowhere.
REMOTE_COMMANDS = frozenset({"corpus-push", "corpus-pull"})

#: Exit 1 is a pass declining to run; only these are allowed, each keyed to what
#: the *fixture* corpus lacks rather than to anything about the argv. The
#: fixture stores no petition text, so the questions-presented backfill refuses
#: the blob outright — after parsing every flag it was handed.
BENIGN_REFUSALS = {
    "backfill-questions-presented": "no stored petition text",
    # Same fixture, same reason from the other side: the OCR recovery reads the
    # petition *rows*, and a corpus holding none is the wrong blob rather than a
    # converged class — the refusal that tells a misconfigured content store
    # apart from a corpus with nothing left to repair.
    "ocr-recover-petitions": "no stored petitions",
    # The same refusal a third time, on the population rather than the
    # documents: the fixture holds no row queued for prediction or selected by
    # the salience gate, so the document back-fill has no denominator to walk.
    # Reaching it is also what keeps this pass's argv offline here — the refusal
    # fires on the walk, before a candidate, a docket fetch or a client exists.
    "backfill-documents": "no predict-relevant live-slice rows",
}


def _workflow() -> dict[Any, Any]:
    data = yaml.safe_load(RUN_REPAIR.read_text())
    assert isinstance(data, dict)
    return data


def _passes() -> list[str]:
    """The selectable maintenance passes, from the dispatch form itself."""
    workflow = _workflow()
    # `on:` parses as the YAML boolean True.
    triggers = workflow.get("on") or workflow.get(True)
    assert isinstance(triggers, dict)
    options = triggers["workflow_dispatch"]["inputs"]["repair"]["options"]
    # `none` is the form's initial state, which the selector gate refuses.
    return [str(option) for option in options if option != "none"]


def _invokes_cli(step: dict[str, Any]) -> bool:
    return "run" in step and bool(command_argv(str(step["run"]), FEDCOURTS))


def _steps_for(pass_name: str) -> list[dict[str, Any]]:
    """The CLI-invoking steps a dispatch of ``pass_name`` runs, found by its gate.

    Keyed on the `inputs.repair == '<pass>'` equality the workflow gates on,
    rather than on a table of step names kept here: a pass that loses its step,
    or grows a second one, then changes what this test covers instead of
    silently falling out of it. The gate is read at both levels because the
    workflow uses both — the corpus passes share one job and gate per step,
    while the re-grade has a job of its own and gates there.
    """
    gate = f"inputs.repair == '{pass_name}'"
    return [
        step
        for _, job, step in _cli_steps()
        if gate in str(step.get("if", "")) + str(job.get("if", ""))
    ]


def _cli_steps() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """Every CLI-invoking step in the workflow, tagged with the job it sits in."""
    return [
        (str(job_id), job, step)
        for job_id, job in _workflow()["jobs"].items()
        if isinstance(job, dict)
        for step in job.get("steps", [])
        if _invokes_cli(step)
    ]


def _ungated_cli_steps() -> list[dict[str, Any]]:
    """The CLI-invoking steps no pass gate selects — every corpus-pass dispatch
    runs these, whichever of them it named (the re-grade has its own job,
    which none of them are in).

    Keyed on ``(job, step name)``, not the name alone: two jobs carrying a
    same-named CLI step would otherwise drop the ungated one from coverage.
    """
    gated = {
        (job_id, str(step["name"]))
        for name in _passes()
        for job_id, _, step in _cli_steps()
        if step in _steps_for(name)
    }
    return [step for job_id, _, step in _cli_steps() if (job_id, str(step["name"])) not in gated]


def _regrade_fields() -> dict[str, str]:
    """The re-grade loop's per-cell shell variables, split as the workflow splits.

    The step reads `IFS=/ read -r court docket event run actor`, so the argv is
    built from the cell id's five fields rather than from the input directly.
    """
    court, docket, event, run, actor = REGRADE_CELL.split("/")
    return {"court": court, "docket": docket, "event": event, "run": run, "actor": actor}


def _values() -> dict[str, str]:
    """What each shell variable the pass argv reads stands for in this test."""
    return {
        "REPAIR_BOUND": REPAIR_BOUND,
        # Only the re-derivation splices `REPAIR_TARGET` into argv directly; the
        # re-grade reads its own target through the five fields below.
        "REPAIR_TARGET": REPAIR_PARSE_LABEL,
        **_regrade_fields(),
    }


def _pass_invocations(pass_name: str) -> list[list[str]]:
    """Every concrete argv a dispatch of ``pass_name`` can hand the CLI.

    Both states of each conditional flag array are covered — the branch taken
    and the branch not — because a dispatch chooses between them by `repair_mode`
    and `repair_options`, and a flag that only appears on one side is exactly the
    kind that goes unexercised until someone selects it.
    """
    seen: set[tuple[str, ...]] = set()
    invocations: list[list[str]] = []
    for step in _steps_for(pass_name):
        body = str(step["run"])
        for arrays in ({}, shell_arrays(body)):
            for argv in command_argv(body, FEDCOURTS):
                concrete = _runnable(expand(argv, arrays=arrays, values=_values()))
                if concrete and tuple(concrete) not in seen:
                    seen.add(tuple(concrete))
                    invocations.append(concrete)
    return invocations


def _runnable(argv: list[str]) -> list[str]:
    """One workflow argv in the form this test executes it."""
    if argv and argv[0] in REMOTE_COMMANDS:
        return [*argv, "--help"]
    return argv


def _run(argv: list[str], tmp_path: Path) -> None:
    """Execute one workflow-derived argv against a throwaway fixture corpus.

    Applying is as safe as dry-running here — the corpus is a per-invocation
    temporary built from `fedcourtsai.fixture`, and the blob push that would
    make a write durable is filtered out above — so both sides of `repair_mode`
    are executed rather than only the cheaper one.
    """
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    fixture.build_fixture_corpus(corpus.corpus_db_path(corpus_root))
    if argv[0] == "stamp-cell":
        _seed_stamped_cell(data_root)
    env = {
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(data_root),
        # Offline is a property of the test, not a hope about the commands: a
        # pass that reached for the upstream or the content store finds no
        # credential and no endpoint, and fails loudly rather than quietly
        # running against whatever the invoking shell was configured for. The
        # backend is pinned for the same reason `_clear_pointer_override` is
        # autouse in conftest — an ambient `ranged` would send every dry run at
        # the real remote instead of the fixture built two lines above.
        "FEDCOURTS_COURTLISTENER_API_TOKEN": "",
        "FEDCOURTS_CASESTORE_URL": "",
        "FEDCOURTS_CORPUS_BACKEND": "local",
    }
    result = CliRunner().invoke(app, argv, env=env)
    rendered = " ".join(argv)

    # Exit 2 is Click's usage error — an option the CLI no longer defines, or a
    # value it can no longer convert. That is precisely the drift under test, so
    # it is named separately from any other failure.
    assert result.exit_code != 2, (
        f"run-repair passes argv the CLI no longer accepts: `fedcourts {rendered}`\n{result.output}"
    )
    if result.exit_code == 0:
        return
    expected = BENIGN_REFUSALS.get(argv[0])
    assert expected is not None and expected in result.output, (
        f"`fedcourts {rendered}` failed with no declared benign refusal\n{result.output}"
    )


def _seed_stamped_cell(data_root: Path) -> None:
    """A committed, stamped evaluation for `REGRADE_CELL` to re-grade.

    The re-grade reads the git ledger rather than the corpus, and refuses a cell
    carrying no `process_version` — a re-grade preserves the stamp of the process
    that produced the record. So the subject is laid down the way production
    lays it down: the cell is written, then stamped, and only then re-graded.
    """
    fields = _regrade_fields()
    court, docket, event = fields["court"], int(fields["docket"]), fields["event"]
    seed_prediction(data_root, court, docket, event)
    seed_evaluation(data_root, court, docket, event, evaluator_id=fields["actor"])
    stamped = CliRunner().invoke(
        app,
        [
            "stamp-cell",
            *("--court", court),
            *("--docket", str(docket)),
            *("--event", event),
            *("--run-id", fields["run"]),
            *("--role", "evaluator"),
            *("--actor", fields["actor"]),
            *("--stamped-at", "2026-01-01T00:00:00Z"),
            *("--pipeline-sha", "sha-abc"),
        ],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert stamped.exit_code == 0, stamped.output


@pytest.mark.parametrize("pass_name", _passes())
def test_every_run_repair_pass_still_parses_against_the_cli(pass_name: str, tmp_path: Path) -> None:
    """Each pass's own argv, executed. The drift detector for every one of them."""
    invocations = _pass_invocations(pass_name)
    assert invocations, (
        f"no `uv run fedcourts` invocation found for repair={pass_name} — either the "
        "pass stopped calling the CLI, or its step is no longer gated on its own "
        "selector value and this test is now covering nothing"
    )
    for index, argv in enumerate(invocations):
        _run(argv, tmp_path / f"{pass_name}-{index}")


def test_the_repair_prerequisites_still_parse_against_the_cli(tmp_path: Path) -> None:
    """The ungated steps every dispatch runs, whichever pass it selected.

    The dedupe runs before any pass and in both modes, so drift here breaks
    every one at once — and it breaks them *before* the selected pass, which reads
    as the pass being broken.
    """
    invocations: list[list[str]] = []
    for step in _ungated_cli_steps():
        body = str(step["run"])
        for argv in command_argv(body, FEDCOURTS):
            concrete = _runnable(expand(argv, arrays=shell_arrays(body), values=_values()))
            if concrete:
                invocations.append(concrete)

    assert invocations, "the prerequisite steps invoke no CLI command; this test covers nothing"
    for index, argv in enumerate(invocations):
        _run(argv, tmp_path / f"prerequisite-{index}")


def test_the_parser_accounts_for_every_cli_invocation_the_workflow_writes() -> None:
    """The tripwire under the coverage above, which is otherwise unfalsifiable.

    Every other test here asserts that what the parser *found* still works. None
    of them can notice what it failed to find — a construction it does not
    understand drops silently, and the pass stays green while running fewer
    commands than a dispatch would. So account for all of them: each written
    `uv run fedcourts` is either an invocation the parser returned or the
    re-grade's echoed preview, which it must exclude precisely because a quoted
    preview is not a command.

    Counted over the shell the steps actually run, with comment lines dropped —
    the same text the parser reads. Counting the raw file instead would make
    prose fail this: a step comment or a dispatch-input description that named
    the command would report itself as parser drift.
    """
    commands = "\n".join(
        line
        for job in _workflow()["jobs"].values()
        if isinstance(job, dict)
        for step in job.get("steps", [])
        if "run" in step
        for line in logical_lines(str(step["run"]))
        if not line.lstrip().startswith("#")
    )
    parsed = sum(
        len(command_argv(str(step["run"]), FEDCOURTS))
        for job in _workflow()["jobs"].values()
        if isinstance(job, dict)
        for step in job.get("steps", [])
        if "run" in step
    )
    previews = sum(
        line.count("uv run fedcourts") for line in commands.splitlines() if "would run:" in line
    )

    assert parsed + previews == commands.count("uv run fedcourts"), (
        "the argv parser does not account for every CLI invocation run-repair writes; "
        "an invocation it cannot read is one this file silently stopped covering"
    )


def test_the_regrade_cell_grammar_admits_this_tests_subject() -> None:
    """The representative cell id is checked against the workflow's own pattern.

    Both the selector gate and the step of record grep a dispatched cell list
    with this regex, so a subject that did not match it would be testing an argv
    no dispatch could produce.
    """
    (step,) = _steps_for("regrade-stale")
    (pattern,) = re.findall(r"pattern='([^']+)'", str(step["run"]))
    assert re.match(pattern, REGRADE_CELL), (
        f"{REGRADE_CELL!r} is not a cell id run-repair would accept"
    )


#: What the OCR step holds back between the slice deadline it passes and its own
#: `timeout-minutes`: the witness re-read, the blob push, the pointer commit, and
#: the work a started candidate can run past the deadline. The arithmetic is
#: stated beside the invocation; this number is the same one, here so the two
#: halves of it cannot move apart.
OCR_DEADLINE_RESERVE_SECONDS = 660


def test_the_ocr_slice_deadline_keeps_its_reserve_under_the_steps_own_cap() -> None:
    """The deadline and the step cap are one number, written in two places.

    The deadline is derived from the cap — everything the step must still do
    once the pass stops taking work has to fit in the difference — but nothing
    couples them at runtime: raise the cap alone and the pass leaves runner
    minutes unspent; widen the deadline alone and the kill this guard exists to
    prevent is back, silently, on the next heavy slice.
    """
    (step,) = [
        step
        for step in _steps_for("ocr-recovery")
        if "--deadline-seconds" in str(step.get("run", ""))
    ]
    cap = int(step["timeout-minutes"]) * 60
    (argv,) = [
        invocation
        for invocation in command_argv(str(step["run"]), FEDCOURTS)
        if "--deadline-seconds" in invocation
    ]
    deadline = float(argv[argv.index("--deadline-seconds") + 1])
    assert deadline == cap - OCR_DEADLINE_RESERVE_SECONDS, (
        f"the OCR slice deadline ({deadline:.0f}s) no longer leaves "
        f"{OCR_DEADLINE_RESERVE_SECONDS}s under the step's {cap}s cap"
    )
    # And whatever the number is, it has to hold the most expensive candidate
    # the pass can estimate, or the head of the class is declined every dispatch
    # and the backlog freezes instead of draining.
    assert deadline > ESTIMATED_CANDIDATE_OVERHEAD_SECONDS + DOCUMENT_BUDGET_SECONDS


#: What the document back-fill's apply holds back between the slice deadline it
#: passes and its own `timeout-minutes`: the walk-only witness re-read, the blob
#: push, the pointer commit, and the work a started candidate can run past the
#: deadline. As with the OCR reserve above, the arithmetic is stated beside the
#: invocation and repeated here so the two halves cannot move apart.
DOCUMENT_BACKFILL_DEADLINE_RESERVE_SECONDS = 540

#: And what its *dry run* holds back, which is smaller because a dry run commits
#: and pushes nothing: only a started candidate's own docket fetch follows it.
DOCUMENT_BACKFILL_DRY_RESERVE_SECONDS = 120


@pytest.mark.parametrize(
    ("apply", "reserve"),
    [
        (True, DOCUMENT_BACKFILL_DEADLINE_RESERVE_SECONDS),
        (False, DOCUMENT_BACKFILL_DRY_RESERVE_SECONDS),
    ],
    ids=["apply", "dry-run"],
)
def test_the_document_backfill_deadlines_keep_their_reserve_under_the_step_cap(
    apply: bool, reserve: int
) -> None:
    """Both of this pass's deadlines are derived from the one step cap.

    Its dry run is deadlined as well as its apply, because both spend paced
    upstream round trips — the dry run fetches every candidate's docket JSON —
    so neither is free to run to the step's kill. The two reserves differ only
    in what still has to happen after the pass stops taking work: a dry run
    writes nothing, so it holds back the overshoot alone.
    """
    (step,) = [
        step
        for step in _steps_for("document-backfill")
        if "--deadline-seconds" in str(step.get("run", ""))
    ]
    cap = int(step["timeout-minutes"]) * 60
    (argv,) = [
        invocation
        for invocation in command_argv(str(step["run"]), FEDCOURTS)
        if "--deadline-seconds" in invocation and ("--apply" in invocation) == apply
    ]
    deadline = float(argv[argv.index("--deadline-seconds") + 1])
    assert deadline == cap - reserve, (
        f"the document back-fill's {'apply' if apply else 'dry-run'} deadline "
        f"({deadline:.0f}s) no longer leaves {reserve}s under the step's {cap}s cap"
    )
    # And whatever the number is, it has to hold a candidate's whole estimate in
    # the mode it runs in, or the head of the class is declined every dispatch
    # and the backlog freezes instead of draining.
    assert deadline > estimated_candidate_seconds(apply=apply)


def test_the_document_backfills_witness_reads_the_ledger_fields_its_pass_writes() -> None:
    """The convergence check names fields `DocumentBackfillResult` actually has.

    The step reads its verdict out of the ledger by field name, in a shell
    `grep`/`json` pipeline no type checker sees — so a renamed field would turn
    the witness into a `KeyError` on the run that was going to prove the write
    landed, which is the one run where a silent failure costs the most.
    """
    (step,) = [
        step
        for step in _steps_for("document-backfill")
        if "ledger_field" in str(step.get("run", ""))
    ]
    read = set(re.findall(r"ledger_field /tmp/[a-z-]+\.txt ([a-z_]+)", str(step["run"])))
    assert read, "the witness reads no ledger field; this test now covers nothing"
    assert read <= set(DocumentBackfillResult.model_fields), (
        f"the witness reads ledger field(s) the pass does not write: "
        f"{sorted(read - set(DocumentBackfillResult.model_fields))}"
    )


def test_the_regrade_dry_run_preview_names_the_argv_it_would_run() -> None:
    """A dry-run re-grade invokes nothing — it echoes what an apply would run.

    That preview is the whole product of the dispatch: the maintainer reads it
    and decides whether to apply. Because it is a hand-written string beside the
    real command rather than a rendering of it, the two can drift, and a preview
    that names flags the apply does not use is a maintainer approving something
    other than what runs.
    """
    (step,) = _steps_for("regrade-stale")
    body = str(step["run"])
    (executed,) = command_argv(body, FEDCOURTS)

    (preview,) = [line for line in body.splitlines() if "would run:" in line]
    previewed = preview.split("uv run fedcourts", 1)[1].rstrip('" \\')

    def _flags(tokens: list[str]) -> list[str]:
        return [token for token in tokens if token.startswith("--")]

    assert _flags(previewed.split()) == _flags(executed), (
        "the re-grade's dry-run preview and the command it previews disagree on flags"
    )


#: The presence-required convergence grep, in the one polarity the qp pass
#: uses: `if ! grep -q "<literal>" /tmp/qp-verify.txt` fails the dispatch when
#: the literal is absent. Anchored on the `!` so a future must-be-ABSENT grep
#: over the same file cannot be mistaken for a literal the converged run has
#: to print.
_CONVERGENCE_GREP = re.compile(r'!\s*grep -q "([^"]+)" /tmp/qp-verify\.txt')


def test_the_qp_convergence_grep_matches_a_converged_run(tmp_path: Path) -> None:
    """The literal the workflow greps is a substring of the converged summary.

    The questions-presented apply gates its corpus push on grepping the
    re-run's summary line — a literal in workflow shell coupled to an f-string
    in `cli.py`, and neither gate sees the pair: to `actionlint` the grep is
    opaque shell, and to the Python gate the workflow is not code. A rewording
    of either side turns the convergence check into an unconditional failure,
    discovered mid-dispatch after the corpus-write lock is taken. So the
    coupling is executed here: both the literal *and* the invocations it is
    grepped from are read out of the workflow, never retyped, and the literal
    is asserted against the output of the re-run the step actually gates on.
    """
    greps = _CONVERGENCE_GREP.findall(RUN_REPAIR.read_text())
    assert greps, "run-repair.yml no longer greps a qp convergence literal"
    (step,) = _steps_for("qp-backfill")
    argvs = [
        argv
        for argv in command_argv(str(step["run"]), FEDCOURTS)
        if argv and argv[0] not in REMOTE_COMMANDS
    ]
    assert argvs, "the qp-backfill step no longer invokes the CLI"
    corpus_root = tmp_path / "corpus"
    _seed_qp_backfill_corpus(corpus_root)
    env = {
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        # Offline is a property of the test, exactly as `_run` pins it: with
        # an ambient casestore URL or split flag, the apply would mirror
        # writes to a real per-case content store.
        "FEDCOURTS_COURTLISTENER_API_TOKEN": "",
        "FEDCOURTS_CASESTORE_URL": "",
        "FEDCOURTS_CORPUS_SPLIT": "0",
        "FEDCOURTS_CORPUS_BACKEND": "local",
    }
    output = ""
    for argv in argvs:
        result = CliRunner().invoke(app, argv, env=env)
        assert result.exit_code == 0, f"{' '.join(argv)}: {result.output}"
        output = result.output
    for literal in greps:
        assert literal in output, (
            f"run-repair.yml greps {literal!r} for convergence, but the step's own "
            f"re-run prints no such line over a converged corpus — either the "
            f"wording drifted, or the apply no longer converges (the counts are in "
            f"the output above)"
        )
