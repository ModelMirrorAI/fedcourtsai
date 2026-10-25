"""The option surface of every subcommand a corpus check may run without approval.

An auto check runs at `main`'s commit and posts the command's stdout publicly
unread, so what such a request can reach is the allowlisted commands' own
options, not only their names on ``config/corpus-check.yaml``'s allowlist. This
test pins each one's full parameter set, so widening an allowlisted command —
an output path, a URL, a flag that prints stored text — fails here, in a
maintainer-owned file, before it can run unapproved.
"""

from __future__ import annotations

from typer.main import get_command

from fedcourtsai import corpus_check as cc
from fedcourtsai.cli import app
from fedcourtsai.config import get_settings

#: Each allowlisted subcommand's parameters as (name, option strings, type name).
#: A change here is a change to what an unapproved check can post.
PINNED_SURFACE: dict[str, list[tuple[str, list[str], str]]] = {
    "corpus-info": [
        ("corpus_backend", ["--corpus-backend"], "str"),
        ("text_coverage", ["--text-coverage"], "boolean"),
        ("legacy_sample", ["--legacy-sample"], "boolean"),
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
    return [(str(p.name), list(p.opts), str(p.type.name)) for p in command.params]


def test_every_allowlisted_subcommand_has_a_pinned_surface() -> None:
    allowlist, problem = cc.load_config(get_settings().config_root).auto_allowlist()
    assert problem is None
    assert set(allowlist) == set(PINNED_SURFACE)


def test_each_allowlisted_subcommand_keeps_its_pinned_surface() -> None:
    for name, pinned in PINNED_SURFACE.items():
        assert _surface(name) == pinned, name


def test_no_allowlisted_subcommand_takes_a_path_or_file() -> None:
    for name in PINNED_SURFACE:
        for _param, _opts, type_name in _surface(name):
            assert type_name not in {"path", "file", "filename"}, name
