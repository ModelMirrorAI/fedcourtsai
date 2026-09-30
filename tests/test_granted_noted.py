"""The Granted & Noted list parser and its comparison with a lineup reading.

The fixture text is shaped the way the lists' text layers extract, one quirk
per Term: letter-spaced labels and names, ``&``-separated codes, jointly
written opinions, docket markers run into the number, and a consolidated case
printed as two entries joined by "(with No. …)".
"""

from __future__ import annotations

from datetime import date

from fedcourtsai.pipeline.granted_noted import (
    CHIEF,
    by_docket,
    disagreements,
    parse_granted_noted,
    summarize,
)
from fedcourtsai.pipeline.justices import bench_on
from fedcourtsai.pipeline.lineup import WritingKind

LIST = """SUPREME COURT OF THE UNITED STATES
GRANTED & NOTED LIST
OCTOBER TERM 2025 CASES FOR ARGUMENT
- 1 -
24-38  CFX LITTLE V. HECOX
   Court:  USCA-9     Granted:  7/3/25
   Argument Date:  1/13/26     Decided:  6/30/26 (with No. 24-43)
   Result:  REVERSED AND REMANDED—see opinion West Virginia v. B. P. J.,
      No. 24-43
24-43  CFX WEST VIRGINIA V. B. P. J.
   Court:  USCA-4     Granted:  7/3/25
   Argument Date:  1/13/26   Decided:  6/30/26 (with No. 24-38)
   Author:  J. Kavanaugh    Other:  Thomas (C); Gorsuch (C);
          Sotomayor (C/J/P, D/P);
          Jackson (C/J/P, D/P)
   Result:  REVERSED AND REMANDED
24-171#       CFX COX COMMUNICATIONS, INC. V. SONY MUSIC ENTERTAINMENT
   Court:  USCA-4     Granted:  6/30/25
   Argument Date:  12/1/25   Decided:  3/25/26
   Author:  J. Thomas    Other:  Sotomayor (C/J)
   Result:  REVERSED AND REMANDED
20-512)*
20-520)*
CFX
CFX
NCAA V. ALSTON
   A u t h o r : C h i e f J u s t i c e
   R e s u l t : AFFIRMED
  Decided: 6/21/21
Other: Breyer (C/P & C/J); Sotomayor & Kagan (D)
19-199 CFX TORRES V. MADRID
   Argument Date: 10/14/20   Decided: 3/25/21
 Author: J. Sotomayo r Other: Gorsuch (D - as to Part II)
   R e s u l t : VACATED
"""


def test_entries_groups_dates_and_authors_are_read() -> None:
    index = by_docket(parse_granted_noted(LIST))
    cox = index["24-171"]
    assert (cox.decided, cox.author) == (date(2026, 3, 25), "Thomas")
    assert cox.others == (("Sotomayor", WritingKind.concurrence_in_judgment),)

    alston = index["20-520"]
    assert alston.dockets == ("20-512", "20-520")
    assert alston.author == CHIEF
    assert set(alston.others) == {
        ("Breyer", WritingKind.concurrence_in_part),
        ("Sotomayor", WritingKind.dissent),
        ("Kagan", WritingKind.dissent),
    }


def test_a_case_decided_with_another_takes_that_entry() -> None:
    """The listing prints 24-43 alone; the list joins 24-38 to its opinion."""
    index = by_docket(parse_granted_noted(LIST))
    hecox = index["24-38"]
    assert hecox is index["24-43"]
    assert set(hecox.dockets) == {"24-38", "24-43"}
    assert hecox.author == "Kavanaugh"
    assert ("Jackson", WritingKind.concurrence_in_part_dissent_in_part) in hecox.others


def test_a_letter_spaced_name_resolves_and_a_qualified_code_is_a_problem() -> None:
    torres = by_docket(parse_granted_noted(LIST))["19-199"]
    assert torres.author == "Sotomayor"
    assert torres.others == ()
    assert torres.problems == ("Gorsuch's codes ['D-astoPartII'] name no known writing kind",)


def test_a_matching_reading_agrees_and_each_difference_is_named() -> None:
    entry = by_docket(parse_granted_noted(LIST))["24-43"]
    bench = bench_on(date(2026, 6, 30))
    reading = summarize(
        [
            (WritingKind.opinion_of_the_court, ("Kavanaugh",)),
            (WritingKind.concurrence, ("Thomas",)),
            (WritingKind.concurrence, ("Gorsuch",)),
            (WritingKind.concurrence_in_part_dissent_in_part, ("Sotomayor",)),
            (WritingKind.concurrence_in_part_dissent_in_part, ("Jackson",)),
        ]
    )
    assert disagreements(entry, reading, bench=bench, decided=date(2026, 6, 30)) == []
    wrong = summarize(
        [
            (WritingKind.opinion_of_the_court, ("Barrett",)),
            (WritingKind.dissent, ("Thomas",)),
        ]
    )
    found = disagreements(entry, wrong, bench=bench, decided=date(2026, 7, 1))
    assert "the list dates the decision 2026-06-30, the opinion 2026-07-01" in found
    assert "the list's author is Kavanaugh, the lineup's Barrett" in found
    assert "the lineup reads Thomas (dissent), the list does not" in found
    assert "the list prints Gorsuch (concurrence), the lineup does not" in found


def test_the_chief_justice_is_seated_at_comparison() -> None:
    entry = by_docket(parse_granted_noted(LIST))["20-512"]
    bench = bench_on(date(2021, 6, 21))
    reading = summarize(
        [
            (WritingKind.opinion_of_the_court, ("Roberts",)),
            (WritingKind.concurrence_in_part, ("Breyer",)),
            (WritingKind.dissent, ("Sotomayor", "Kagan")),
        ]
    )
    assert disagreements(entry, reading, bench=bench, decided=date(2021, 6, 21)) == []


def test_a_letter_spaced_decided_and_a_wrapped_with_are_read() -> None:
    text = (
        "19-1\n   D e c i d e d : 3 / 25 / 21 (with\n"
        + "   No.\n19-2)\n   A u t h o r : J. Thomas\n19-2 CFX X V. Y\n"
        + "   Decided: 3/25/21\n   Author: J. Thomas\n"
    )
    entries = parse_granted_noted(text)
    assert [e.dockets for e in entries] == [("19-1",), ("19-2",)]
    assert entries[0].decided == date(2021, 3, 25)
    assert entries[0].author == "Thomas"


def test_an_entry_with_no_decision_date_never_agrees() -> None:
    (entry,) = parse_granted_noted("20-1 CFX X V. Y\n   Author: J. Thomas\n")
    reading = summarize([(WritingKind.opinion_of_the_court, ("Thomas",))])
    found = disagreements(entry, reading, bench=bench_on(date(2021, 3, 1)), decided=None)
    assert "the list prints no decision date that could be read" in found
    assert "the opinion prints no decision date that could be read" in found
