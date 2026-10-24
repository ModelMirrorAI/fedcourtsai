"""The argument-features parse: who the Justices questioned, by advocate side, from a transcript.

The fixtures are synthetic but in the reporter's format, calibrated against
the Court's OT2024 transcripts: the furniture the cleaner removes, the
appearances and contents that name every advocate before the argument opens,
the speaker labels, and the segment headers as the reporter wraps them.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.corpus import CaseDocument
from fedcourtsai.pipeline.argument_features import (
    ASSIGNMENT,
    parse_argument_features,
    read_header,
)
from fedcourtsai.pipeline.documents import KIND_ARGUMENT_TRANSCRIPT, clean_transcript_text
from fedcourtsai.provision import staged_argument_features
from fedcourtsai.schemas import ArgumentFeatures, ArgumentParseCoverage, ArgumentTurnCount

runner = CliRunner()

# A whole argument as pypdf extracts it, before the cleaner: a margin line
# number, the review header and the reporter's footer, the contents (whose
# "ORAL ARGUMENT OF:" lines open no segment), the Chief Justice calling the
# case, four segments, the closing line and the word index after it.
_RAW = [
    "1",
    "Official - Subject to Final Review",
    "IN THE SUPREME COURT OF THE UNITED STATES",
    "APPEARANCES:",
    "JANE ROE, ESQUIRE, Washington, D.C.; on behalf",
    "of the Petitioners.",
    "C O N T E N T S",
    "ORAL ARGUMENT OF: PAGE:",
    "JANE ROE, ESQ.",
    "On behalf of the Petitioners 3",
    "REBUTTAL ARGUMENT OF:",
    "JANE ROE, ESQ.",
    "On behalf of the Petitioners 40",
    "Heritage Reporting Corporation",
    "P R O C E E D I N G S",
    "(10:00 a.m.)",
    "CHIEF JUSTICE ROBERTS: We will hear",
    "argument this morning in Case 25-100.",
    "Ms. Roe.",
    "ORAL ARGUMENT OF JANE ROE",
    "ON BEHALF OF THE PETITIONERS",
    "MS. ROE: Mr. Chief Justice, and may it",
    "please the Court: the statute is clear.",
    "2",
    "JUSTICE KAGAN: Why is it clear?",
    "MS. ROE: Because it says so.",
    "JUSTICE THOMAS: What about the",
    "Official",
    "history?",
    "(Laughter.)",
    "MS. ROE: The history agrees.",
    "CHIEF JUSTICE ROBERTS: Thank you, counsel.",
    "Mr. Doe.",
    "ORAL ARGUMENT OF JOHN DOE",
    "FOR THE UNITED STATES, AS AMICUS CURIAE,",
    "SUPPORTING THE PETITIONERS",
    "MR. DOE: Mr. Chief Justice, and may it please the Court:",
    "JUSTICE KAGAN: Does the government agree?",
    "MR. DOE: It does.",
    "ORAL ARGUMENT OF RICHARD ROW",
    "ON BEHALF OF THE RESPONDENT",
    "MR. ROW: Mr. Chief Justice:",
    "JUSTICE KAGAN: Isn't the text against you?",
    "MR. ROW: No.",
    "JUSTICE GORUSCH: One more question.",
    "MR. ROW: Yes.",
    "JUSTICE BARRETT: And the purpose --",
    "MS. ROE: May I respond?",
    "REBUTTAL ARGUMENT OF JANE ROE",
    "ON BEHALF OF THE PETITIONERS",
    "MS. ROE: Briefly.",
    "CHIEF JUSTICE ROBERTS: Thank you. The case is submitted.",
    "(Whereupon, at 11:00 a.m., the case was",
    "submitted.)",
    "abuse [1] 5:9",
]


def _features() -> ArgumentFeatures:
    return parse_argument_features(clean_transcript_text("\n".join(_RAW)))


def _count(turns: int, words: int) -> ArgumentTurnCount:
    return ArgumentTurnCount(turns=turns, words=words)


def test_each_justice_turn_counts_toward_the_side_of_its_segment() -> None:
    features = _features()
    by_justice = {row.justice: row for row in features.justices}
    assert list(by_justice) == ["Barrett", "Kagan", "Roberts", "Thomas"]
    kagan = by_justice["Kagan"]
    assert kagan.by_side == {
        "petitioner": _count(1, 4),
        "respondent": _count(1, 5),
        "united-states-supporting-petitioner": _count(1, 4),
    }
    assert kagan.by_alignment == {"petitioner": _count(2, 8), "respondent": _count(1, 5)}
    assert kagan.total == _count(3, 13)
    # The lone "Official" line and the "(Laughter.)" parenthetical are not speech.
    assert by_justice["Thomas"].by_side == {"petitioner": _count(1, 4)}
    # The Chief Justice's closing of a segment counts with it, and the rebuttal is
    # the petitioner's; calling the case falls in no segment.
    assert by_justice["Roberts"].by_side == {"petitioner": _count(2, 11)}
    # "--" carries no letter, so it is not a word.
    assert by_justice["Barrett"].by_side == {"respondent": _count(1, 3)}
    assert features.side_totals == {
        "petitioner": _count(4, 19),
        "respondent": _count(2, 8),
        "united-states-supporting-petitioner": _count(1, 4),
    }
    assert features.alignment_totals == {"petitioner": _count(5, 23), "respondent": _count(2, 8)}
    assert features.assignment == ASSIGNMENT


def test_segments_are_read_from_the_body_headers_alone() -> None:
    segments = _features().segments
    assert [(s.kind, s.role, s.supports, s.side) for s in segments] == [
        ("argument", "petitioner", "petitioner", "petitioner"),
        (
            "argument",
            "united-states-amicus",
            "petitioner",
            "united-states-supporting-petitioner",
        ),
        ("argument", "respondent", "respondent", "respondent"),
        ("rebuttal", "petitioner", "petitioner", "petitioner"),
    ]
    assert segments[1].header == (
        "ORAL ARGUMENT OF JOHN DOE FOR THE UNITED STATES, AS AMICUS CURIAE, "
        + "SUPPORTING THE PETITIONERS"
    )
    respondent = segments[2]
    # Kagan, the unresolved label and Barrett; the advocate the header names; and
    # the petitioner's counsel speaking in the respondent's time.
    assert respondent.justice == _count(3, 11)
    assert respondent.advocate == _count(3, 5)
    assert respondent.other_turns == 1
    assert segments[0].advocate == _count(3, 20)


def test_coverage_counts_what_it_could_not_attribute() -> None:
    coverage = _features().coverage
    assert coverage.segments == coverage.segments_attributed == 4
    assert coverage.justice_turns == 9
    assert coverage.justice_turns_attributed == 7
    assert coverage.justice_turns_outside_segments == 1
    # The misprinted label is reported as printed, and counted toward no Justice.
    assert coverage.justice_turns_unresolved == 1
    assert coverage.unresolved_labels == ["JUSTICE GORUSCH"]
    assert coverage.closing_line
    assert coverage.notes == []


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (
            "ORAL ARGUMENT OF PAUL D. CLEMENT ON BEHALF OF THE RESPONDENT, "
            + "IN SUPPORT OF THE PETITIONER",
            ("respondent", "petitioner", None),
        ),
        (
            "ORAL ARGUMENT OF CHRISTOPHER G. MICHEL, COURT-APPOINTED AMICUS CURIAE "
            + "IN SUPPORT OF THE JUDGMENT BELOW",
            ("amicus", "respondent", None),
        ),
        (
            "ORAL ARGUMENT OF YAIRA DUBIN FOR THE UNITED STATES, AS AMICUS CURIAE, "
            + "SUPPORTING THE PETITIONERS",
            ("united-states-amicus", "petitioner", None),
        ),
        (
            "ORAL ARGUMENT OF ASHLEY ROBERTSON FOR THE UNITED STATES, AS AMICUS CURIAE, "
            + "SUPPORTING VACATUR AND REMAND",
            ("united-states-amicus", "neither", None),
        ),
        (
            "ORAL ARGUMENT OF A. B. CEE FOR THE UNITED STATES, AS AMICUS CURIAE, "
            + "SUPPORTING NEITHER PARTY",
            ("united-states-amicus", "neither", None),
        ),
        (
            "ORAL ARGUMENT OF A. B. CEE FOR TEXAS, ET AL., AS AMICUS CURIAE, "
            + "SUPPORTING RESPONDENT FELIX",
            ("amicus", "respondent", None),
        ),
        (
            "ORAL ARGUMENT OF MITHUN MANSINGHANI ON BEHALF OF THE PETITIONERS IN CASE 23-1067",
            ("petitioner", "petitioner", "23-1067"),
        ),
        (
            "ORAL ARGUMENT OF J. BENJAMIN AGUIÑAGA ON BEHALF OF THE APPELLANT IN CASE 24-109",
            ("petitioner", "petitioner", "24-109"),
        ),
        (
            "ORAL ARGUMENT OF A. B. CEE ON BEHALF OF THE APPELLEES",
            ("respondent", "respondent", None),
        ),
        (
            "ORAL ARGUMENT OF SETH P. WAXMAN ON BEHALF OF RESPONDENTS GROWTH ENERGY AND "
            + "RENEWABLE FUELS ASSOCIATION IN SUPPORT OF THE PETITIONER",
            ("respondent", "petitioner", None),
        ),
        (
            "ORAL ARGUMENT OF A. B. CEE ON BEHALF OF THE FEDERAL RESPONDENTS, "
            + "SUPPORTING THE PETITIONERS",
            ("respondent", "petitioner", None),
        ),
        ("ORAL ARGUMENT OF A. B. CEE, COURT-APPOINTED AMICUS CURIAE", ("amicus", None, None)),
        ("ORAL ARGUMENT OF A. B. CEE", (None, None, None)),
    ],
)
def test_a_header_names_role_position_and_case(
    header: str, expected: tuple[str | None, str | None, str | None]
) -> None:
    assert read_header(header) == expected


def _argument(*segments: list[str], close: bool = True) -> str:
    lines = ["P R O C E E D I N G S", "CHIEF JUSTICE ROBERTS: We will hear argument."]
    for segment in segments:
        lines.extend(segment)
    if close:
        lines.extend(["(Whereupon, at 11:00 a.m., the case was", "submitted.)"])
    return "\n".join(lines)


def test_a_party_supporting_the_other_side_aligns_with_it() -> None:
    features = parse_argument_features(
        _argument(
            ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
            ["JUSTICE ALITO: Why reverse?"],
            [
                "ORAL ARGUMENT OF BEN BEE ON BEHALF OF THE",
                "RESPONDENT, IN SUPPORT OF THE PETITIONER",
                "MR. BEE: We agree.",
            ],
            ["JUSTICE ALITO: Then who defends it?"],
            [
                "ORAL ARGUMENT OF CAL CEE,",
                "COURT-APPOINTED AMICUS CURIAE",
                "IN SUPPORT OF THE JUDGMENT BELOW",
                "MR. CEE: I do.",
            ],
            ["JUSTICE ALITO: Good."],
        )
    )
    assert [s.side for s in features.segments] == [
        "petitioner",
        "respondent",
        "amicus-supporting-respondent",
    ]
    alito = features.justices[0]
    assert alito.by_side == {
        "amicus-supporting-respondent": _count(1, 1),
        "petitioner": _count(1, 2),
        "respondent": _count(1, 4),
    }
    assert alito.by_alignment == {"petitioner": _count(2, 6), "respondent": _count(1, 1)}


def test_a_segment_with_no_side_is_counted_apart_and_noted() -> None:
    features = parse_argument_features(
        _argument(
            ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
            ["JUSTICE ALITO: Why?"],
            ["ORAL ARGUMENT OF DEE DEE,", "COURT-APPOINTED AMICUS CURIAE", "MS. DEE: Hm."],
            ["JUSTICE ALITO: And you?", "JUSTICE SOTOMAYOR: Yes?"],
        )
    )
    segment = features.segments[1]
    assert (segment.role, segment.supports, segment.side) == ("amicus", None, None)
    by_justice = {row.justice: row for row in features.justices}
    assert by_justice["Alito"].by_side == {"petitioner": _count(1, 1)}
    assert by_justice["Alito"].unattributed == _count(1, 2)
    assert by_justice["Sotomayor"].by_side == {}
    assert by_justice["Sotomayor"].total == _count(0, 0)
    coverage = features.coverage
    assert (coverage.segments_attributed, coverage.segments_unattributed) == (1, 1)
    assert coverage.justice_turns_unattributed_segment == 2
    assert features.side_totals == {"petitioner": _count(1, 1)}
    assert coverage.notes == [
        "segment 1: no side read from header "
        + "'ORAL ARGUMENT OF DEE DEE, COURT-APPOINTED AMICUS CURIAE'"
    ]


def test_a_rebuttal_naming_no_side_is_the_petitioners() -> None:
    features = parse_argument_features(
        _argument(["REBUTTAL ARGUMENT OF ANN AY", "MS. AY: Briefly.", "JUSTICE KAGAN: Go on."])
    )
    assert features.segments[0].side == "petitioner"
    assert features.justices[0].by_side == {"petitioner": _count(1, 2)}
    assert features.coverage.notes == [
        "segment 0: rebuttal header names no side; counted with the petitioner"
    ]


def test_consolidated_and_divided_segments_sum_under_their_side() -> None:
    features = parse_argument_features(
        _argument(
            [
                "ORAL ARGUMENT OF ANN AY",
                "ON BEHALF OF THE PETITIONERS IN CASE 23-1067",
                "MS. AY: Reverse.",
                "JUSTICE JACKSON: Why?",
            ],
            [
                "ORAL ARGUMENT OF BEN BEE",
                "ON BEHALF OF THE PETITIONERS IN CASE 23-1068",
                "MR. BEE: Also reverse.",
                "JUSTICE JACKSON: Why again?",
            ],
        )
    )
    assert [(s.side, s.case_number) for s in features.segments] == [
        ("petitioner", "23-1067"),
        ("petitioner", "23-1068"),
    ]
    assert features.side_totals == {"petitioner": _count(2, 3)}


def test_header_variants_the_reporter_prints_still_open_a_segment() -> None:
    features = parse_argument_features(
        _argument(
            ["ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
            ["JUSTICE KAGAN: Why?"],
            ["ORAL ARGUMENT BY BEN BEE", "ON BEHALF OF THE RESPONDENT", "MR. BEE: Affirm."],
            ["JUSTICE KAGAN: Why not?"],
        )
    )
    assert [s.side for s in features.segments] == ["petitioner", "respondent"]
    assert features.coverage.justice_turns_attributed == 2


def test_margin_line_numbers_kept_on_the_text_line_are_not_words() -> None:
    lines = _argument(
        ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
        ["JUSTICE THOMAS: One question", "about the record."],
    ).splitlines()
    numbered = "\n".join(f"{n % 25 + 1} {line}" for n, line in enumerate(lines))
    features = parse_argument_features(numbered)
    assert features.justices[0].by_side == {"petitioner": _count(1, 5)}
    assert features.coverage.closing_line


def test_without_a_closing_line_the_parse_says_so() -> None:
    features = parse_argument_features(
        _argument(
            ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
            ["JUSTICE THOMAS: Why?"],
            close=False,
        )
    )
    assert not features.coverage.closing_line
    assert features.coverage.notes == ["no reporter's closing line: parsed to the end of the text"]


def test_a_closing_line_the_cleaner_missed_still_ends_the_argument() -> None:
    # No comma after "Whereupon", so the cleaner keeps the word index; the
    # parse still stops at the closing line rather than counting the index.
    text = "\n".join(
        [
            "P R O C E E D I N G S",
            "ORAL ARGUMENT OF ANN AY",
            "ON BEHALF OF THE PETITIONER",
            "MS. AY: Reverse.",
            "CHIEF JUSTICE ROBERTS: The case is submitted.",
            "(Whereupon at 11:19 a.m., the case was",
            "submitted.)",
            "abuse [1] 5:9",
            "accept [2] 7:1 9:4",
        ]
    )
    features = parse_argument_features(clean_transcript_text(text))
    assert features.justices[0].by_side == {"petitioner": _count(1, 4)}


def test_a_text_with_no_header_attributes_nothing() -> None:
    features = parse_argument_features("JUSTICE KAGAN: Hello.\nMR. AY: Hello.")
    coverage = features.coverage
    assert (coverage.segments, coverage.justice_turns) == (0, 1)
    assert coverage.justice_turns_outside_segments == 1
    assert features.justices == []
    assert coverage.notes == [
        "no 'P R O C E E D I N G S' line: parsed from the start of the text",
        "no reporter's closing line: parsed to the end of the text",
        "no segment header read: every turn is outside a segment",
    ]


def test_the_parse_is_deterministic() -> None:
    text = clean_transcript_text("\n".join(_RAW))
    first = parse_argument_features(text).model_dump_json()
    assert parse_argument_features(text).model_dump_json() == first


def test_coverage_refuses_counts_that_do_not_partition() -> None:
    with pytest.raises(ValidationError, match="do not sum"):
        ArgumentParseCoverage(
            segments=1,
            segments_attributed=1,
            segments_unattributed=0,
            justice_turns=3,
            justice_turns_attributed=1,
            justice_turns_outside_segments=1,
            justice_turns_unresolved=0,
            justice_turns_unattributed_segment=0,
            unresolved_labels=[],
            unrecognized_label_lines=0,
            unrecognized_labels=[],
            closing_line=True,
            notes=[],
        )


def test_features_refuse_totals_that_are_not_the_rows_sums() -> None:
    features = _features()
    data = features.model_dump(mode="json")
    data["side_totals"]["petitioner"]["turns"] += 1
    with pytest.raises(ValidationError, match="side_totals"):
        ArgumentFeatures.model_validate(data)
    data = features.model_dump(mode="json")
    data["justices"][0]["total"]["words"] += 1
    with pytest.raises(ValidationError, match="by_side"):
        ArgumentFeatures.model_validate(data)
    data = features.model_dump(mode="json")
    data["segments"].pop()
    with pytest.raises(ValidationError, match=r"coverage\.segments"):
        ArgumentFeatures.model_validate(data)


def test_cli_prints_the_features_and_a_coverage_line(tmp_path: Path) -> None:
    transcript = tmp_path / "argument-transcript.txt"
    transcript.write_text(clean_transcript_text("\n".join(_RAW)), encoding="utf-8")
    result = runner.invoke(app, ["argument-features", str(transcript)])
    assert result.exit_code == 0, result.output
    assert ArgumentFeatures.model_validate(json.loads(result.stdout)) == _features()
    assert "4 segment(s), 0 with no side; 9 Justice turn(s): 7 attributed" in result.stderr
    missing = runner.invoke(app, ["argument-features", str(tmp_path / "absent.txt")])
    assert missing.exit_code == 1
    binary = tmp_path / "argument-transcript.pdf"
    binary.write_bytes(b"%PDF-1.4\n\xff\xfe\x00")
    refused = runner.invoke(app, ["argument-features", str(binary)])
    assert refused.exit_code == 1
    assert "is not UTF-8 text" in refused.stderr


def test_an_advocate_is_matched_by_a_whole_word_of_the_header() -> None:
    # "LEE" is inside "APPELLEES", but is not a word of the header.
    features = parse_argument_features(
        _argument(
            [
                "ORAL ARGUMENT OF ANN AY",
                "ON BEHALF OF THE APPELLEES",
                "MS. AY: Affirm.",
                "MR. LEE: If I may.",
            ]
        )
    )
    segment = features.segments[0]
    assert (segment.side, segment.advocate, segment.other_turns) == (
        "respondent",
        _count(1, 1),
        1,
    )


def test_a_recess_line_does_not_end_the_argument() -> None:
    # Only a closing line saying the case was submitted ends the parse, so a
    # head-cut text with a recess in it is still reported as having no close.
    features = parse_argument_features(
        _argument(
            ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
            ["JUSTICE THOMAS: Why?", "(Whereupon, a recess was taken.)"],
            ["JUSTICE THOMAS: And after the recess?"],
            close=False,
        )
    )
    assert not features.coverage.closing_line
    assert features.justices[0].by_side == {"petitioner": _count(2, 5)}


def test_a_label_with_no_space_after_its_colon_still_opens_a_turn() -> None:
    features = parse_argument_features(
        _argument(
            ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY:Reverse."],
            ["JUSTICE KAGAN:Why?"],
        )
    )
    assert features.justices[0].by_side == {"petitioner": _count(1, 1)}
    assert features.segments[0].advocate == _count(1, 1)


def test_a_label_like_line_the_parse_cannot_read_is_counted() -> None:
    features = parse_argument_features(
        _argument(
            ["ORAL ARGUMENT OF ANN AY", "ON BEHALF OF THE PETITIONER", "MS. AY: Reverse."],
            ["THE MARSHAL: Oyez.", "JUSTICE KAGAN: Why?"],
        )
    )
    coverage = features.coverage
    assert (coverage.unrecognized_label_lines, coverage.unrecognized_labels) == (
        1,
        ["THE MARSHAL"],
    )
    # Its words stay with the turn it falls in; nothing is attributed to it.
    assert features.segments[0].advocate == _count(1, 4)


def _transcript_document(text: str) -> CaseDocument:
    return CaseDocument(
        case_id="scotus/9525000466",
        kind=KIND_ARGUMENT_TRANSCRIPT,
        url="https://www.supremecourt.gov/oral_arguments/argument_transcripts/2025/25-100_x.pdf",
        entry_date="2026-04-20",
        fetched_at=date(2026, 4, 21),
        text=text,
    )


def test_a_staged_transcript_yields_the_cells_features() -> None:
    text = clean_transcript_text("\n".join(_RAW))
    staged = [(_transcript_document(text), None)]
    assert staged_argument_features(staged) == _features()


def test_no_staged_transcript_yields_no_features() -> None:
    petition = CaseDocument(
        case_id="scotus/9525000466",
        kind="petition",
        url="https://www.supremecourt.gov/p.pdf",
        entry_date="2025-06-01",
        fetched_at=date(2025, 6, 2),
        text="The petition.",
    )
    assert staged_argument_features([(petition, None)]) is None
