"""Option help against the vocabularies it names.

`--help` is how a cell agent discovers what it may ask for, so a value the
command accepts but the help omits is functionally missing from the tool even
though it works. Every list below is rendered from its source rather than
restated, and these pin that the two stay in step — including the two the code
cannot render (a workflow input description, and a help string carrying a gloss
per value), which is exactly where a test has to stand in.
"""

from __future__ import annotations

import re
from typing import get_args

from typer.testing import CliRunner

from fedcourtsai.cert_backtest import CERT_BACKTEST_SCOPES
from fedcourtsai.cli import CELL_MODES, app
from fedcourtsai.config import CorpusBackend
from fedcourtsai.pipeline.runner import available_backends
from fedcourtsai.schemas import Engine, UsageRole

runner = CliRunner()


def _help(*command: str) -> str:
    """The command's rendered help, flattened for matching.

    rich box-wraps and colours the output, and both differ between a local shell
    and CI — so the escape codes come out, the box rule comes out, and runs of
    whitespace collapse before anything is matched.
    """
    result = runner.invoke(app, [*command, "--help"], env={"COLUMNS": "200", "NO_COLOR": "1"})
    assert result.exit_code == 0, result.output
    plain = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    return " ".join(plain.replace("│", " ").split())


def _option_help(rendered: str, option: str) -> str:
    """Just one option's help text, up to where the next option begins.

    Matching the whole page is too weak here: these vocabularies also appear in
    command docstrings and in neighbouring options, so a page-wide search passes
    even when the option itself has dropped a value.
    """
    # Anchor on the option *row*, which carries a metavar — the bare flag also
    # appears in command docstrings, and slicing from there reads the prose.
    row = re.search(rf"{re.escape(option)} <", rendered)
    assert row is not None, f"{option} has no option row in the rendered help"
    tail = rendered[row.end() :]
    following = re.search(r" --[a-z]", tail)
    return tail[: following.start()] if following else tail


def test_cert_backtest_scope_help_names_every_population() -> None:
    """`CERT_BACKTEST_SCOPES` is imported into the CLI already and used to build
    this command's own error message, so the help was the odd copy out. It
    carries a gloss per scope, so it cannot be a plain join — which is precisely
    why it needs a test rather than a render."""
    segment = _option_help(_help("cert-backtest"), "--scope")
    missing = [scope for scope in CERT_BACKTEST_SCOPES if f"'{scope}'" not in segment]
    assert not missing, f"--scope help omits populations the command accepts: {missing}"


def test_the_engine_helps_name_every_registered_backend() -> None:
    """Two commands offer the runner backends. A sixth backend must not require
    remembering both spots.

    Asserted as the joined run, not value-by-value: every backend name also
    appears elsewhere on these help pages (in the command docstring), so a
    per-value search passes even when the option itself lists none of them.
    """
    assert ", ".join(available_backends()) in _help("cert-backtest")
    assert " | ".join(available_backends()) in _help("local-cascade")


def test_mcp_config_client_help_names_every_engine() -> None:
    rendered = _help("mcp-config")
    assert " | ".join(e.value for e in Engine) in rendered


def test_the_registry_role_help_names_every_role() -> None:
    for command in ("mcp-config", "mcp-serve"):
        rendered = _help(command)
        assert " | ".join(r.value for r in UsageRole) in rendered, command


def test_the_corpus_backend_help_names_every_backend() -> None:
    """The Literal has one definition (`config.CorpusBackend`, re-exported by
    `corpus`); the help renders from it rather than being a third copy."""
    rendered = _help("query")
    assert " / ".join(get_args(CorpusBackend)) in rendered


def test_provision_snapshot_mode_help_names_every_cell_mode() -> None:
    rendered = _help("provision-snapshot")
    assert " | ".join(CELL_MODES) in rendered


def test_enum_typed_options_let_typer_render_the_choices() -> None:
    """`record-usage --engine` / `--role` are typed as their enums, so typer puts
    the choice list in the metavar itself. Restating it in the help would be a
    second copy to drift, so the help must stay free of one."""
    rendered = _help("record-usage")
    for value in [e.value for e in Engine] + [r.value for r in UsageRole]:
        assert value in rendered, f"typer should render {value!r} from the enum type"
    assert "Engine that ran." in rendered
