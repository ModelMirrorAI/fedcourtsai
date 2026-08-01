"""Addressing and identity for the interim docket.

The Court's applications — stays, injunctions, vacaturs pending certiorari — are
a separate numbering sequence served at the same endpoint as the cert docket,
with the same payload shape. What follows is the first of the three things
integrating them needs: the pipeline can *name* one, *fetch* one, and give it an
identity that cannot be confused with a petition's.

Scope and events are the other two, and neither is here: nothing polls an
application, nothing takes one into predict scope, and no event models one.
"""

from __future__ import annotations

import pytest

from fedcourtsai.supremecourt import (
    LIVE_APPLICATION_ID_BASE,
    LIVE_DOCKET_ID_BASE,
    is_application_docket_id,
    is_live_docket_id,
    live_application_id,
    live_docket_id,
    parse_scotus_application_number,
    parse_scotus_docket_number,
    scotus_docket_slug,
)


def test_an_application_number_parses_to_term_and_serial() -> None:
    assert parse_scotus_application_number("24A1099") == (24, 1099)
    # The upstream JSON carries a trailing space, as it does on the cert docket.
    assert parse_scotus_application_number("25A123 ") == (25, 123)
    assert parse_scotus_application_number("25a1") == (25, 1)


def test_the_two_sequences_do_not_parse_each_other() -> None:
    """A petition and an application are different matters, so a parser that
    accepted both would silently address the wrong docket."""
    assert parse_scotus_application_number("25-5184") is None
    assert parse_scotus_docket_number("24A1099") is None


def test_a_non_addressable_application_spelling_is_rejected() -> None:
    """Deliberately stricter than the scope rule, which must recognize every
    spelling so none reaches cert scope. This one only has to address the
    ``YYAnnn`` form the endpoint actually serves — a number it rejects is still
    an application, just not one the live channel can fetch."""
    for raw in ("A-706", "A14-662", "18A142T", "22O141", "", None):
        assert parse_scotus_application_number(raw) is None, raw


def test_the_two_id_ranges_are_disjoint() -> None:
    """`24A1` and `24-1` are different matters. Packing both on `(term, serial)`
    into one range would collide them onto a single row — and `case_id` is
    immutable, so that is not a mistake a later pass could undo."""
    assert live_docket_id(24, 1) != live_application_id(24, 1)
    assert live_application_id(24, 1) > live_docket_id(99, 999_999)
    # Both stay inside the live channel's reserved space, above every
    # CourtListener id, so neither can collide with an ingested row.
    assert is_live_docket_id(live_application_id(24, 1))
    assert live_docket_id(0, 1) > LIVE_DOCKET_ID_BASE


def test_an_application_id_is_recognizable_as_one() -> None:
    """Downstream has to be able to tell what a reserved-range id refers to
    without re-parsing a docket number it may not have."""
    assert is_application_docket_id(live_application_id(25, 123))
    assert not is_application_docket_id(live_docket_id(25, 123))
    assert LIVE_APPLICATION_ID_BASE > LIVE_DOCKET_ID_BASE


def test_ids_are_deterministic_and_permanent() -> None:
    """Re-discovery of the same application must mint the same id: the ledger and
    the snapshots key on it, so a second id is a second case."""
    assert live_application_id(24, 1099) == live_application_id(24, 1099)


def test_an_out_of_range_serial_is_refused_rather_than_folded() -> None:
    """Silently wrapping would mint one id for two matters."""
    for term, serial in ((100, 1), (-1, 1), (24, 0), (24, 1_000_000)):
        with pytest.raises(ValueError):
            live_application_id(term, serial)


def test_the_slug_addresses_the_right_sequence() -> None:
    """Upstream serves both forms at one endpoint, so the slug is the only thing
    that distinguishes which docket is fetched."""
    assert scotus_docket_slug(24, 1099, form="application") == "24A1099"
    assert scotus_docket_slug(24, 1099) == "24-1099"
    assert scotus_docket_slug(4, 12, form="application") == "04A12"
