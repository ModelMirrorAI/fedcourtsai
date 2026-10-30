"""`fedcourts pdf-text`: a cell reads a PDF with the pinned extractor, installing nothing."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.cli import app
from tests.test_documents import _pdf_pages

runner = CliRunner()


def test_prints_every_page_in_order(tmp_path: Path) -> None:
    pdf = tmp_path / "brief.pdf"
    pdf.write_bytes(_pdf_pages(["Question presented", "Argument"]))
    result = runner.invoke(app, ["pdf-text", str(pdf)])
    assert result.exit_code == 0, result.output
    assert result.stdout.index("Question presented") < result.stdout.index("Argument")
    assert "2 page(s)" in result.stderr
    assert "cut at" not in result.stderr


def test_reports_a_cut_at_the_character_cap(tmp_path: Path) -> None:
    pdf = tmp_path / "brief.pdf"
    pdf.write_bytes(_pdf_pages(["Question presented"]))
    result = runner.invoke(app, ["pdf-text", str(pdf), "--max-chars", "8"])
    assert result.exit_code == 0, result.output
    assert result.stdout == "Question\n"
    assert "cut at --max-chars 8" in result.stderr


def test_a_scanned_pdf_prints_nothing_and_says_so(tmp_path: Path) -> None:
    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(_pdf_pages([""]))
    result = runner.invoke(app, ["pdf-text", str(pdf)])
    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == ""
    assert "no extractable text" in result.stderr


def test_a_missing_or_unreadable_file_exits_one(tmp_path: Path) -> None:
    missing = runner.invoke(app, ["pdf-text", str(tmp_path / "absent.pdf")])
    assert missing.exit_code == 1
    assert "no file at" in missing.stderr
    junk = tmp_path / "junk.pdf"
    junk.write_bytes(b"not a pdf")
    unreadable = runner.invoke(app, ["pdf-text", str(junk)])
    assert unreadable.exit_code == 1
    assert "not a readable PDF" in unreadable.stderr


def test_a_file_over_the_byte_cap_is_refused_unread(tmp_path: Path) -> None:
    pdf = tmp_path / "brief.pdf"
    pdf.write_bytes(_pdf_pages(["Question presented"]))
    result = runner.invoke(app, ["pdf-text", str(pdf), "--max-bytes", "10"])
    assert result.exit_code == 1
    assert "over --max-bytes 10" in result.stderr
    assert result.stdout == ""


def test_an_extractor_failure_is_an_unreadable_pdf(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(_data: bytes, *, char_cap: int) -> object:
        raise RecursionError(char_cap)

    monkeypatch.setattr(cli, "extract_pdf_text", boom)
    pdf = tmp_path / "brief.pdf"
    pdf.write_bytes(_pdf_pages(["Question presented"]))
    result = runner.invoke(app, ["pdf-text", str(pdf)])
    assert result.exit_code == 1
    assert "not a readable PDF" in result.stderr
