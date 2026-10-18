"""No early-exiting `grep -q` downstream of a pipe in the repo's shell.

Every workflow step and script here runs under ``pipefail``. ``grep -q`` exits
on its first match without draining its input, so a writer still mid-output
takes SIGPIPE, the pipeline's status becomes the writer's 141, and an ``if``
reads that as *no match*. The pipe buffer usually hides it, which is what
makes it dangerous: a credential tripwire such as
``env | grep -E '^AWS_' | grep -qv ...`` passes on a leak exactly when the
environment is large enough to fill the buffer. Draining with
``grep ... > /dev/null``, or feeding a here-string, keeps the exit status and
cannot be cut short. The rule is about pipelines whose exit status decides
something; a downstream ``head`` or ``grep -m1`` that only captures a value,
with its status discarded (``|| true``), is not what this guards.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# A lexical tripwire for the common forms, not a shell parser: a single `|`
# (never `||`), then grep with -q in any flag cluster or --quiet/--silent.
PIPED_QUIET_GREP = re.compile(
    r"(?<!\|)\|(?!\|)\s*grep\b[^|;&]*\s(?:-[A-Za-z0-9]*q[A-Za-z]*|--quiet|--silent)\b"
)


def _shell_surfaces() -> list[Path]:
    github = ROOT / ".github"
    files = [*github.glob("workflows/*.yml"), *github.glob("actions/**/*.yml")]
    files += [*github.glob("actions/**/*.sh"), *(ROOT / "scripts").rglob("*.sh")]
    shebangs = (b"#!/bin/bash", b"#!/usr/bin/env bash", b"#!/bin/sh", b"#!/usr/bin/env sh")
    files += [
        path
        for path in (ROOT / "scripts").iterdir()
        if path.is_file() and path.read_bytes().startswith(shebangs)
    ]
    return sorted(set(files))


@pytest.mark.parametrize(
    "line",
    [
        "if env | grep -E '^AWS_' | grep -qvE '^AWS_REGION='; then",
        'printf \'%s\' "$cmd" | grep -Eq -- "$pat" && return 1',
        "cat log |grep -E -q denied",
        "echo x | grep --quiet x",
        "env | grep -E 'x' -q",
        "env | grep -m1 -q x",
        "env | grep --fixed-strings --silent x",
    ],
)
def test_the_pattern_catches_a_piped_quiet_grep(line: str) -> None:
    assert PIPED_QUIET_GREP.search(line)


@pytest.mark.parametrize(
    "line",
    [
        "if env | grep -E '^AWS_' | grep -vE '^AWS_REGION=' > /dev/null; then",
        'grep -Eq -- "$pat" <<<"$cmd" && return 1',
        "if grep -qiE 'rejected' \"$log\"; then",
        "test -f x || grep -q pat file",
    ],
)
def test_the_pattern_passes_a_draining_or_unpiped_grep(line: str) -> None:
    assert not PIPED_QUIET_GREP.search(line)


def test_no_shell_surface_pipes_into_a_quiet_grep() -> None:
    surfaces = _shell_surfaces()
    assert len(surfaces) > 10, "the scan found almost nothing to read"
    hits = [
        f"{path.relative_to(ROOT)}:{number}: {line.strip()}"
        for path in surfaces
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if PIPED_QUIET_GREP.search(line)
    ]
    assert not hits, "drain the grep (`> /dev/null`) or use a here-string:\n" + "\n".join(hits)
