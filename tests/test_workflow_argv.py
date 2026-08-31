"""The shell reader two workflow-parity suites execute what they find from.

`tests/workflow_argv.py` decides what
`tests/test_workflow_repair_cli_parity.py` and `tests/test_collect_issueless.py`
run against the CLI, which puts it in an awkward position: a bug that makes it
return *less* leaves both suites green while covering less, and a bug that makes
it return something *wrong* reports a CLI usage error — pointing at `cli.py` for
what is really a parser artefact. Neither is visible from those suites (the
repair one carries a count tripwire, which sees dropped invocations but not
malformed ones).

So the reader's refusals are pinned here, against the constructions it does not
read rather than the ones it does. Everything below asserts the same property:
it raises rather than guessing. What it does read is exercised for real by the
two suites, over the actual workflow files.
"""

from __future__ import annotations

import pytest

from tests.workflow_argv import (
    UnresolvedToken,
    command_argv,
    expand,
    logical_lines,
    shell_arrays,
)

FEDCOURTS = ("uv", "run", "fedcourts")


def test_a_continued_command_line_is_read_as_one() -> None:
    """Every multi-flag invocation in these workflows is `\\`-continued."""
    body = 'uv run fedcourts thing --parse "$LABEL" \\\n  --apply\n'
    assert command_argv(body, FEDCOURTS) == [["thing", "--parse", "$LABEL", "--apply"]]
    assert len(logical_lines(body)) == 1, "the two physical lines are one command"


def test_a_quoted_preview_of_a_command_is_not_a_command() -> None:
    """The re-grade's dry run echoes what an apply would run. Counting that as an
    invocation would have the parity suite execute a maintainer-facing string."""
    body = 'echo "would run: uv run fedcourts stamp-cell --regrade" | tee -a "$SUMMARY"\n'
    assert command_argv(body, FEDCOURTS) == []


def test_a_pipeline_or_redirection_does_not_become_argv() -> None:
    body = "uv run fedcourts thing 2>&1 | tee -a /tmp/x.txt\nuv run fedcourts other >plan.json\n"
    assert command_argv(body, FEDCOURTS) == [["thing"], ["other"]]


def test_a_command_separator_glued_to_a_word_still_ends_the_command() -> None:
    """`shlex` attaches `;` to the token before it, so `data; then` lexes as
    `data;` — which would otherwise be handed to the CLI as an argument."""
    assert command_argv("uv run fedcourts validate data; then\n", FEDCOURTS) == [
        ["validate", "data"]
    ]


def test_the_outer_command_substitution_is_unwrapped() -> None:
    """The composite captures its plan: `plan=$("$FEDCOURTS" collect-plan …)`.
    Its punctuation glues onto the program name and the final argument."""
    body = 'plan=$("$FEDCOURTS" collect-plan --role "$ROLE" "${matrix_args[@]}")\n'
    assert command_argv(body, ("$FEDCOURTS",)) == [
        ["collect-plan", "--role", "$ROLE", "${matrix_args[@]}"]
    ]


def test_a_nested_command_substitution_is_refused_not_flattened() -> None:
    """Flattening splices the inner command's words in as arguments — argv the
    workflow never passes, failing against the CLI as if the CLI had drifted."""
    with pytest.raises(UnresolvedToken, match="nested command substitution"):
        command_argv("uv run fedcourts thing --bar $(cat x.txt)\n", FEDCOURTS)


def test_shell_the_lexer_cannot_read_is_refused_not_skipped() -> None:
    """Skipping it would remove an invocation from a caller's coverage silently."""
    with pytest.raises(UnresolvedToken, match="cannot lex"):
        command_argv("uv run fedcourts thing --bar don't\n", FEDCOURTS)


def test_both_states_of_a_conditional_flag_array_are_available() -> None:
    """The idiom a step builds a mode- or option-dependent flag with. An empty
    initializer followed by a populated append must yield the flags, not [] —
    otherwise the branch-taken side of every conditional goes unexercised."""
    body = "apply_args=()\nif [ x = y ]; then\n  apply_args+=(--apply)\nfi\n"
    assert shell_arrays(body) == {"apply_args": ["--apply"]}


def test_an_absent_array_expands_to_nothing() -> None:
    """The branch-not-taken side: a legitimate state, not a missing value."""
    assert expand(["run", "${apply_args[@]}"], arrays={}, values={}) == ["run"]


def test_an_unknown_scalar_is_refused() -> None:
    """A workflow that starts reading a new input must fail the caller's test
    until the caller says what that input holds."""
    with pytest.raises(UnresolvedToken, match="REPAIR_TARGET"):
        expand(["--parse", "${REPAIR_TARGET}"], arrays={}, values={})


@pytest.mark.parametrize("token", ["${RUN:-none}", "x$COUNT", "${A}${B}"])
def test_an_expansion_the_reader_does_not_understand_is_refused(token: str) -> None:
    """The closing sweep. These match neither substitution pattern, and passing
    one through as a literal hands the CLI an argument that reads exactly like
    the drift the caller is testing for."""
    with pytest.raises(UnresolvedToken, match="left unsubstituted"):
        expand(["--flag", token], arrays={}, values={"RUN": "r", "COUNT": "1", "A": "a", "B": "b"})
