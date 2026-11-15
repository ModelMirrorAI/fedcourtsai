"""The option surface of every subcommand a corpus check may run without approval.

An auto check runs at `main`'s commit and posts the command's stdout publicly
unread, so what such a request can reach is the allowlisted commands' own
options, not only their names on ``config/corpus-check.yaml``'s allowlist. This
test pins each one's full parameter set, so widening an allowlisted command —
an output path, a URL, a flag that prints stored text — fails here, in a
maintainer-owned file, before it can run unapproved.
"""

from __future__ import annotations

from typing import Any

from typer.main import get_command

from fedcourtsai import corpus_check as cc
from fedcourtsai.cli import app
from fedcourtsai.config import get_settings

#: Each allowlisted subcommand's parameters as (name, option strings, type name).
#: A change here is a change to what an unapproved check can post.
PINNED_SURFACE: dict[str, list[tuple[str, list[str], str]]] = {
    "corpus-info": [
        ("corpus_backend", ["--corpus-backend"], "str"),
        ("text_coverage", ["--text-coverage"], "bool"),
        ("legacy_sample", ["--legacy-sample"], "bool"),
    ],
    "decision-census": [
        ("first_term", ["--first-term"], "int"),
        ("last_term", ["--last-term"], "int"),
    ],
    "caption-census": [
        ("rule_version", ["--rule-version"], "str"),
    ],
    "party-census": [
        ("as_of", ["--as-of"], "str"),
        ("rule_version", ["--rule-version"], "str"),
    ],
    "distribution-census": [
        ("baseline_parse", ["--baseline-parse"], "str"),
        ("candidate_parse", ["--candidate-parse"], "str"),
        ("version", ["--version"], "str"),
    ],
}


def _surface(name: str) -> list[tuple[str, list[str], str]]:
    command = getattr(get_command(app), "commands", {})[name]
    return [(str(p.name), list(p.opts), _type_name(p)) for p in command.params]


def _type_name(param: Any) -> str:
    """The parameter's annotated type as typer names it, a container's element included."""
    return str(param.bare_type())


def _reaches_the_filesystem(param: Any) -> bool:
    """Whether typer would hand the command a path or an open file for this parameter."""
    descriptor = param.type_descriptor
    name = _type_name(param)
    return bool(descriptor.is_path or descriptor.is_file) or "Path" in name or "File" in name


def test_every_allowlisted_subcommand_has_a_pinned_surface() -> None:
    allowlist, problem = cc.load_config(get_settings().config_root).auto_allowlist()
    assert problem is None
    assert set(allowlist) == set(PINNED_SURFACE)


def test_each_allowlisted_subcommand_keeps_its_pinned_surface() -> None:
    for name, pinned in PINNED_SURFACE.items():
        assert _surface(name) == pinned, name


def test_no_allowlisted_subcommand_takes_a_path_or_file() -> None:
    for name in PINNED_SURFACE:
        command = getattr(get_command(app), "commands", {})[name]
        for param in command.params:
            assert not _reaches_the_filesystem(param), f"{name}: {param.name}"
