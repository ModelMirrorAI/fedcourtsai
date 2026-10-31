from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.corpus import CorpusRow
from fedcourtsai.pipeline.alignment_side import (
    AlignmentSideError,
    FrameCase,
    build_extract,
    codes_path,
    extract_payload,
    frame_rows,
    modes_payload,
    publish,
    read_code_lines,
)
from fedcourtsai.schemas import AlignmentCodeMode, AlignmentSideCode, AlignmentSideCodes

runner = CliRunner()


def _row(case_id: str, granted: date | None, **fields: object) -> CorpusRow:
    return CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=f"{case_id[-2:]}-1",
        case_name=f"A v. B ({case_id})",
        date_cert_granted=granted,
        disposition=fields.pop("disposition", "granted"),
        **fields,  # type: ignore[arg-type]
    )


def _case(case_id: str, granted: date, *, decided: bool = False) -> FrameCase:
    return FrameCase(
        case_id=case_id,
        docket_number=f"{case_id[-2:]}-1",
        caption="A v. B",
        petitioner="A",
        court_below="Court of Appeals",
        granted=granted,
        decided=decided,
    )


def test_the_frame_is_merits_grants_from_the_first_term() -> None:
    rows = [
        _row("scotus/11", date(2022, 1, 10)),  # OT2021: in
        _row("scotus/12", date(2021, 6, 1)),  # OT2020: before the frame
        _row("scotus/13", date(2023, 1, 9), disposition="gvr"),  # rode the order
        _row("scotus/14", None, disposition="denied"),
        _row("scotus/15", date(2025, 1, 10), merits_judgment="reversed"),
    ]
    cases = frame_rows(rows)
    assert [c.case_id for c in cases] == ["scotus/11", "scotus/15"]
    assert [c.decided for c in cases] == [False, True]


def test_the_extract_leaves_out_coded_and_textless_cases_and_cuts_oldest_first() -> None:
    cases = [
        _case("scotus/21", date(2024, 1, 5)),
        _case("scotus/22", date(2023, 1, 5), decided=True),
        _case("scotus/23", date(2022, 1, 5)),
        _case("scotus/24", date(2025, 1, 5)),
        _case("scotus/25", date(2025, 2, 5)),
    ]
    texts = {c.case_id: f"Whether {c.case_id}?" for c in cases if c.case_id != "scotus/24"}
    extract = build_extract(cases, texts, coded=["scotus/23"], ceiling=2)
    assert [r.case_id for r in extract.rows] == ["scotus/21", "scotus/22"]
    assert extract.modes == {
        "scotus/21": AlignmentCodeMode.forward,
        "scotus/22": AlignmentCodeMode.replay,
    }
    assert (extract.frame, extract.already_coded, extract.no_text, extract.deferred) == (
        5,
        1,
        1,
        1,
    )


def test_the_extract_hands_the_coder_no_mode_or_outcome() -> None:
    extract = build_extract(
        [_case("scotus/31", date(2024, 1, 5), decided=True)], {"scotus/31": "Whether?"}, []
    )
    (row,) = extract_payload(extract)
    assert set(row) == {
        "case_id",
        "docket_number",
        "caption",
        "petitioner",
        "court_below",
        "granted",
        "questions_presented",
    }
    assert modes_payload(extract) == {"scotus/31": "replay"}


def _extract(*ids: str) -> tuple[list[dict[str, object]], dict[str, str]]:
    rows: list[dict[str, object]] = [
        {"case_id": i, "docket_number": f"{i[-2:]}-1", "granted": "2025-01-10"} for i in ids
    ]
    return rows, {i: "forward" for i in ids}


def _line(case_id: str, **overrides: object) -> dict[str, object]:
    line: dict[str, object] = {
        "case_id": case_id,
        "docket_number": f"{case_id[-2:]}-1",
        "conservative_side": "respondent",
        "score": 0.7,
        "valence": "clear",
        "note": "Criminal procedure: the State defends the conviction.",
    }
    line.update(overrides)
    return line


STAMP = {"model": "claude-opus-5-5", "run_id": "123", "coded_at": date(2026, 11, 2)}


def test_publish_stamps_the_harness_fields() -> None:
    rows, modes = _extract("scotus/41", "scotus/42")
    modes["scotus/42"] = "replay"
    codes = publish(None, rows, modes, [_line("scotus/42"), _line("scotus/41")], **STAMP)  # type: ignore[arg-type]
    assert [e.case_id for e in codes.entries] == ["scotus/41", "scotus/42"]
    replay = codes.entries[1]
    assert replay.mode == "replay" and replay.contamination_risk
    assert replay.granted == date(2025, 1, 10) and replay.run_id == "123"
    assert not codes.entries[0].contamination_risk


@pytest.mark.parametrize(
    ("lines", "match"),
    [
        ([_line("scotus/51")], "not coded"),
        ([_line("scotus/51"), _line("scotus/52"), _line("scotus/52")], "coded twice"),
        ([_line("scotus/51"), _line("scotus/59")], "not in the extract"),
        ([_line("scotus/51"), _line("scotus/52", docket_number="99-9")], "docket number"),
        ([_line("scotus/51"), _line("scotus/52", mode="forward")], "does not write"),
        ([_line("scotus/51"), _line("scotus/52", score=1.5)], "line 2"),
        ([_line("scotus/51"), _line("scotus/52", conservative_side="both")], "line 2"),
    ],
)
def test_publish_refuses_a_run_that_does_not_cover_the_extract_cleanly(
    lines: list[dict[str, object]], match: str
) -> None:
    rows, modes = _extract("scotus/51", "scotus/52")
    with pytest.raises(AlignmentSideError, match=match):
        publish(None, rows, modes, lines, **STAMP)  # type: ignore[arg-type]


def test_a_code_is_never_revised() -> None:
    rows, modes = _extract("scotus/61")
    first = publish(None, rows, modes, [_line("scotus/61")], **STAMP)  # type: ignore[arg-type]
    with pytest.raises(AlignmentSideError, match="never revised"):
        publish(first, rows, modes, [_line("scotus/61", score=0.2)], **STAMP)  # type: ignore[arg-type]
    rows2, modes2 = _extract("scotus/62")
    merged = publish(first, rows2, modes2, [_line("scotus/62")], **STAMP)  # type: ignore[arg-type]
    assert [e.case_id for e in merged.entries] == ["scotus/61", "scotus/62"]


def test_the_contamination_flag_must_follow_the_mode() -> None:
    fields = {
        "case_id": "scotus/71",
        "docket_number": "71-1",
        "granted": date(2025, 1, 10),
        "conservative_side": "petitioner",
        "score": 0.5,
        "valence": "none",
        "note": "Fallback.",
        "mode": "replay",
        "contamination_risk": False,
        "model": "m",
        "run_id": "1",
        "coded_at": date(2026, 1, 1),
    }
    with pytest.raises(ValueError, match="contamination_risk"):
        AlignmentSideCode.model_validate(fields)
    with pytest.raises(ValueError, match="predate"):
        AlignmentSideCode.model_validate(
            {**fields, "contamination_risk": True, "coded_at": date(2024, 1, 1)}
        )


def test_the_artifact_holds_one_entry_per_case_in_order() -> None:
    rows, modes = _extract("scotus/81", "scotus/82")
    codes = publish(None, rows, modes, [_line("scotus/81"), _line("scotus/82")], **STAMP)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="sorted"):
        AlignmentSideCodes(entries=list(reversed(codes.entries)))


def test_code_lines_skip_blanks_and_refuse_non_objects(tmp_path: Path) -> None:
    path = tmp_path / "codes.jsonl"
    path.write_text(json.dumps(_line("scotus/91")) + "\n\n")
    assert len(read_code_lines(path)) == 1
    path.write_text("[1]\n")
    with pytest.raises(AlignmentSideError, match="not a JSON object"):
        read_code_lines(path)


def test_the_publish_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    rows, modes = _extract("scotus/95")
    (tmp_path / "extract.json").write_text(json.dumps(rows))
    (tmp_path / "modes.json").write_text(json.dumps(modes))
    (tmp_path / "codes.jsonl").write_text(json.dumps(_line("scotus/95")) + "\n")
    args = [
        "alignment-side-codes",
        "--extract",
        str(tmp_path / "extract.json"),
        "--modes",
        str(tmp_path / "modes.json"),
        "--codes",
        str(tmp_path / "codes.jsonl"),
        "--model",
        "claude-opus-5-5",
        "--run-id",
        "7",
        "--coded-at",
        "2026-11-02",
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    written = AlignmentSideCodes.model_validate_json(codes_path(tmp_path / "data").read_text())
    assert [e.case_id for e in written.entries] == ["scotus/95"]
    again = runner.invoke(app, args)
    assert again.exit_code == 1
    assert "never revised" in again.stderr


def test_the_extract_command_refuses_the_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    inside = tmp_path / "data" / "x.json"
    result = runner.invoke(
        app, ["alignment-side-extract", "--out", str(inside), "--modes-out", str(tmp_path / "m")]
    )
    assert result.exit_code == 2
    outside = runner.invoke(
        app,
        [
            "alignment-side-extract",
            "--out",
            str(tmp_path / "x.json"),
            "--modes-out",
            str(tmp_path / "m.json"),
        ],
    )
    assert outside.exit_code == 1  # no corpus
