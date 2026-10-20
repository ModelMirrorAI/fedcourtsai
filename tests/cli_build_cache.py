"""One Click command tree per Typer app, built once per test process.

`typer.testing.CliRunner.invoke` converts the Typer app into its Click group
on every call, and for this CLI that conversion walks every registered
command's signature — a cost each of the suite's in-process CLI invocations
paid again. The tree it builds is a pure function of the app's registrations,
which no test changes after import, and Click re-parses argv and builds a
fresh context on every ``main`` call, so one tree serves every invocation.

Keyed on the app object itself (a Typer app hashes by identity), so a test
that builds its own Typer app gets its own tree. If typer stops routing
``invoke`` through ``typer.testing._get_command``, :func:`install` changes
nothing: every other test runs correctly at the uncached speed, and
``tests/test_cli_build_cache.py`` fails to say the cache is gone.
"""

from __future__ import annotations

import typer.testing
from typer import Typer
from typer._click.core import Command

_trees: dict[Typer, Command] = {}


def install() -> None:
    """Route the test runner's app-to-command conversion through the cache."""
    build = getattr(typer.testing, "_get_command", None)
    if build is None or getattr(build, "_cached", False):
        return

    def cached(typer_instance: Typer) -> Command:
        tree = _trees.get(typer_instance)
        if tree is None:
            tree = _trees[typer_instance] = build(typer_instance)
        return tree

    cached._cached = True  # type: ignore[attr-defined]
    typer.testing._get_command = cached  # type: ignore[attr-defined]
