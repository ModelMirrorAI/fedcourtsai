"""The test runner's shared command tree: one per app, and still the app's own."""

from __future__ import annotations

import typer
import typer.testing
from typer.testing import CliRunner

from fedcourtsai.cli import app
from tests import cli_build_cache


def test_the_runner_builds_each_apps_tree_once() -> None:
    build = typer.testing._get_command  # type: ignore[attr-defined]
    assert getattr(build, "_cached", False), "conftest did not install the cache"
    assert build(app) is build(app)


def test_another_app_gets_its_own_tree() -> None:
    other = typer.Typer()

    @other.command()
    def hello(name: str) -> None:
        print(f"hello {name}")

    build = typer.testing._get_command  # type: ignore[attr-defined]
    assert build(app) is not build(other)
    result = CliRunner().invoke(other, ["world"])
    assert result.exit_code == 0, result.output
    assert result.output == "hello world\n"


def test_invoke_builds_through_the_cache() -> None:
    # The patched name is only worth anything while `CliRunner.invoke` still
    # looks it up; a fresh app enters the cache only by being invoked.
    fresh = typer.Typer()

    @fresh.command()
    def ping() -> None:
        print("pong")

    assert fresh not in cli_build_cache._trees
    assert CliRunner().invoke(fresh, []).output == "pong\n"
    assert fresh in cli_build_cache._trees


def test_a_cached_tree_parses_every_invocation_afresh() -> None:
    # Click builds a new context per `main` call, so a usage error on one
    # invocation leaves nothing behind for the next.
    runner = CliRunner()
    assert runner.invoke(app, ["validate", "--no-such-flag"]).exit_code == 2
    assert runner.invoke(app, ["validate", "--help"]).exit_code == 0


def test_installing_twice_keeps_one_cache() -> None:
    before = typer.testing._get_command  # type: ignore[attr-defined]
    cli_build_cache.install()
    assert typer.testing._get_command is before  # type: ignore[attr-defined]
