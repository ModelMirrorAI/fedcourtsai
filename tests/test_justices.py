"""The roster module: the SCDB spelling map and the shared surname vocabulary."""

from fedcourtsai.pipeline.justices import (
    COMPOUND_SURNAMES,
    ENTRY_SURNAMES,
    KNOWN_SURNAMES,
    SCDB_JUSTICE_SURNAMES,
    normalize_scdb_justice,
    resolve_surname,
)


def test_the_map_covers_the_modern_span_and_only_it() -> None:
    """Forty Justices sat from the Vinson court through the present bench.

    The count is the cheap tripwire for a dropped or duplicated row: eight
    holdover appointees plus thirty-two from Vinson onward. A new appointment
    moves it by exactly one.
    """
    assert len(SCDB_JUSTICE_SURNAMES) == 40
    # The bookends of the span, by SCDB spelling.
    assert SCDB_JUSTICE_SURNAMES["FMVinson"] == "Vinson"
    assert SCDB_JUSTICE_SURNAMES["KBJackson"] == "Jackson"


def test_the_map_is_many_to_one_where_surnames_repeat() -> None:
    """Two Jacksons print one surname; the Term, not the map, tells them apart.

    A reverse map would have to invent a disambiguator no docket entry prints,
    which is why the module exposes a membership set instead and leaves the
    reverse direction to the import's docket-number-plus-Term join.
    """
    assert normalize_scdb_justice("RHJackson") == "Jackson"
    assert normalize_scdb_justice("KBJackson") == "Jackson"
    # Harlan II carries SCDB's disambiguating digit; the printed surname does not.
    assert normalize_scdb_justice("JHarlan2") == "Harlan"


def test_spellings_that_diverge_between_the_two_vocabularies() -> None:
    """SCDB strips the apostrophe the docket prints; the map restores it."""
    assert normalize_scdb_justice("SDOConnor") == "O'Connor"
    assert "O'Connor" in ENTRY_SURNAMES


def test_an_unknown_spelling_is_refused_rather_than_guessed() -> None:
    assert normalize_scdb_justice("JMarshall") is None
    assert normalize_scdb_justice("") is None
    # Surnames are not SCDB spellings: the map's direction is one-way.
    assert normalize_scdb_justice("Gorsuch") is None


def test_every_modern_surname_is_a_single_token() -> None:
    """The single-token recital parse is exact over the modern span.

    This is the fact that makes the fallback parse safe: only a historical
    compound surname needs the roster-resolved window, and the one that exists
    is carried explicitly.
    """
    assert all(" " not in surname for surname in ENTRY_SURNAMES)
    assert {"Van Devanter"} == COMPOUND_SURNAMES
    assert KNOWN_SURNAMES == ENTRY_SURNAMES | COMPOUND_SURNAMES
    # The value side's tripwire: exactly one surname collision (the Jacksons),
    # so a typo'd surname would add a distinct 40th value and fail here.
    assert len(ENTRY_SURNAMES) == 39
    # No two roster surnames differ only in case, so the case-blind index
    # cannot silently collapse two Justices into one row.
    assert len({surname.casefold() for surname in KNOWN_SURNAMES}) == len(KNOWN_SURNAMES)


def test_resolve_surname_is_case_blind_and_returns_the_roster_spelling() -> None:
    """Docket entries print in whatever case the order list used."""
    assert resolve_surname("GORSUCH") == "Gorsuch"
    assert resolve_surname("gorsuch") == "Gorsuch"
    assert resolve_surname("O'CONNOR") == "O'Connor"
    assert resolve_surname("VAN DEVANTER") == "Van Devanter"
    assert resolve_surname("Stranger") is None
    assert resolve_surname("") is None
