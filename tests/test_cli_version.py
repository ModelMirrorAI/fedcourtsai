from importlib.metadata import version

from typer.testing import CliRunner

from fedcourtsai.cli import app

runner = CliRunner()


def test_version_flag_prints_version_and_exits_clean() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version("fedcourtsai")
