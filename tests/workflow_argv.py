"""Read a workflow's embedded CLI invocations back out as argv.

A ``uv run fedcourts …`` string inside a workflow or composite action is a call
site no Python check reaches: it is matched against the CLI for the first time
when the job runs, so a flag renamed in ``cli.py`` surfaces there as a usage
error rather than here as a red test. These helpers recover the invocation from
the YAML — the command line, the shell arrays it splices in, and the values
standing in for the inputs it reads out of the environment — so a test can run
the same argv the job would.

The parsing is deliberately shallow: it handles the two constructions these call
sites actually use — a ``\\``-continued command line, and an argv array built
under a conditional — and raises on anything it cannot resolve rather than
guessing, so a new construction fails loudly instead of dropping silently out of
the coverage it was supposed to be under.
"""

from __future__ import annotations

import re
import shlex
from collections.abc import Mapping, Sequence

#: Tokens that end a command and begin shell plumbing. Everything after one of
#: these belongs to a pipeline or a redirection, not to the program's argv.
_TERMINATORS = frozenset({"|", "||", "&&", ";", "&"})

#: A redirection token: bare ``>``/``>>``, or one carrying its fd (``2>&1``,
#: ``2>plan-stderr.txt``, ``>plan.json``).
_REDIRECT = re.compile(r"^[0-9]*>>?")

_SCALAR = re.compile(r"^\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?$")
_ARRAY = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\[@\]\}$")

#: ``name=(…)`` and ``name+=(…)`` — the argv-array idiom these steps build a
#: conditional flag with. Both forms are accumulated, so an empty initializer
#: followed by a populated append yields the flags the guarded branch adds.
_ARRAY_ASSIGN = re.compile(r"^[ \t]*([A-Za-z_][A-Za-z0-9_]*)\+?=\(([^)]*)\)", re.MULTILINE)

#: ``name=$( … )`` capturing a whole command — the one substitution form these
#: call sites wrap an invocation in.
_OUTER_SUBSTITUTION = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]*=)?\$\((?P<inner>.*)\)")


class UnresolvedToken(AssertionError):
    """A shell token the caller supplied no value for.

    Raised rather than passed through as a literal ``$FOO``: an unsubstituted
    variable would reach the CLI as a nonsense argument and could be mistaken
    for the very drift these helpers exist to detect.
    """


def logical_lines(body: str) -> list[str]:
    """The step body's command lines, with ``\\`` continuations joined."""
    return body.replace("\\\n", " ").splitlines()


def shell_arrays(body: str) -> dict[str, list[str]]:
    """Every argv array the body builds, in its populated form.

    The value is what the array holds once its guarded branch has run — the
    caller picks that state or the empty one to cover both sides of the
    conditional.
    """
    arrays: dict[str, list[str]] = {}
    for name, contents in _ARRAY_ASSIGN.findall(body):
        arrays.setdefault(name, []).extend(shlex.split(contents))
    return arrays


def _unwrap_substitution(line: str) -> str:
    """Take the ``name=$( … )`` wrapper off a captured command, and only that one.

    The wrapper's punctuation glues onto the neighbouring tokens
    (``plan=$("$FEDCOURTS"`` … ``"${matrix_args[@]}")``), hiding both the program
    name and the last argument, so it has to come off before lexing. A *nested*
    substitution is refused rather than flattened: flattening would splice the
    inner command's own words into this command's argv, and a caller executing
    that argv would read the resulting usage error as CLI drift — the one
    conclusion this module exists to make trustworthy.
    """
    unwrapped = _OUTER_SUBSTITUTION.fullmatch(line.strip())
    if unwrapped is not None:
        line = unwrapped.group("inner")
    if "$(" in line:
        raise UnresolvedToken(
            f"nested command substitution in a line naming the CLI: {line!r}; "
            "its words would be spliced into the argv as arguments"
        )
    return line


def command_argv(body: str, program: Sequence[str]) -> list[list[str]]:
    """Every invocation of ``program`` in ``body``, as unexpanded argv.

    ``program`` is the token sequence that names the CLI — ``("uv", "run",
    "fedcourts")`` for a workflow step, ``("$FEDCOURTS",)`` for a composite that
    calls the pinned binary. Matching whole tokens rather than a substring is
    what keeps an *echoed* preview of a command (``echo "would run: uv run
    fedcourts …"``) out of the result: the quoted preview lexes to one token, so
    it cannot match a token sequence.
    """
    invocations: list[list[str]] = []
    marker = program[-1]
    for line in logical_lines(body):
        if line.lstrip().startswith("#") or marker not in line:
            continue
        try:
            tokens = shlex.split(_unwrap_substitution(line))
        except ValueError as exc:
            # Shell this lexer cannot read. Dropping it would remove an
            # invocation from the caller's coverage without saying so.
            raise UnresolvedToken(f"cannot lex a line naming the CLI: {line!r}") from exc
        index = 0
        while index <= len(tokens) - len(program):
            if tokens[index : index + len(program)] != list(program):
                index += 1
                continue
            argv: list[str] = []
            for token in tokens[index + len(program) :]:
                if token in _TERMINATORS or _REDIRECT.match(token):
                    break
                # `shlex` glues a command separator onto the word before it, so
                # `… data; then` lexes as `data;` — which would otherwise reach
                # the CLI as an argument rather than ending the command.
                if token.endswith(";"):
                    if token[:-1]:
                        argv.append(token[:-1])
                    break
                argv.append(token)
            invocations.append(argv)
            index += len(program) + len(argv)
    return invocations


def expand(
    argv: Sequence[str],
    *,
    arrays: Mapping[str, Sequence[str]],
    values: Mapping[str, str],
) -> list[str]:
    """Substitute shell variables into a concrete argv.

    ``${name[@]}`` splices in ``arrays[name]`` (absent means the guarded branch
    was not taken, which is a legitimate state and expands to nothing);
    ``$NAME`` / ``${NAME}`` takes ``values[NAME]``. An unknown scalar raises
    :class:`UnresolvedToken` — a workflow that starts reading a new input should
    fail the test until the test says what that input holds.

    The splice runs first and its contents go through the scalar pass with
    everything else, because an array built under a guard is exactly where a
    conditional flag carries a dispatch input — ``args+=(--max-cases
    "${REPAIR_BOUND}")`` — and a splice exempt from that pass would leave the
    value unexpanded. An array naming another array is not re-spliced; nothing
    writes that shape, and the closing sweep refuses it rather than dropping it.

    The returned argv carries no ``$`` anywhere, and the closing sweep enforces
    that rather than trusting the two forms above to have covered every token: a
    default (``${NAME:-x}``) or an interpolation (``x$NAME``) matches neither
    pattern, and passing one through as a literal would hand the CLI a nonsense
    argument that reads exactly like the drift a caller is testing for.
    """
    spliced: list[str] = []
    for token in argv:
        array = _ARRAY.match(token)
        if array is not None:
            spliced.extend(arrays.get(array.group(1), ()))
            continue
        spliced.append(token)
    expanded: list[str] = []
    for token in spliced:
        scalar = _SCALAR.match(token)
        if scalar is None:
            expanded.append(token)
            continue
        name = scalar.group(1)
        if name not in values:
            raise UnresolvedToken(
                f"the workflow passes ${{{name}}}, which this test supplies no value for"
            )
        expanded.append(values[name])
    unresolved = [token for token in expanded if "$" in token]
    if unresolved:
        raise UnresolvedToken(
            f"shell expansion this parser does not read, left unsubstituted: {unresolved}"
        )
    return expanded
