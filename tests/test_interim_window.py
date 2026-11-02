"""The interim pool from OT2027: a 3-Term window over the widened ask vocabulary.

What the registration owes and these pin:

- **Before `INTERIM_WINDOW_FROM_TERM` nothing moves**: the caller's lookback
  and the registered substantive slice, whatever the pack's widened counts say.
- **From that Term the pool is the interim window**: the three application
  Terms strictly before the cell's own, whatever lookback the caller passes,
  counted on `wide_granted` / `wide_resolved` (or their finer twins), and
  refusing while a pooled Term is unread on the widened ask or predates the
  counts.
- **The widened ask is a superset** of the registered one: only an `unknown`
  can move, bail and release asks stay `unknown`, and extensions stay
  extensions.
- **The statpack counts the widened slice** beside the registered one.
"""

from __future__ import annotations

import pytest

from fedcourtsai import corpus
from fedcourtsai.analytics import _InterimAcc
from fedcourtsai.pipeline.base_rates import (
    INTERIM_LOOKBACK_TERMS,
    INTERIM_WINDOW_FROM_TERM,
    interim_base_rate,
)
from fedcourtsai.pipeline.interim_signals import (
    WIDE_APPLICATION_KIND_FROM_TERM,
    ApplicationKind,
    application_kind,
    application_kind_wide,
)
from fedcourtsai.schemas import StatPack, StatPackInterim, StatPackInterimTerm

_Counts = tuple[int, int, int, int, int, int]


def _pack(terms: dict[int, _Counts | None]) -> StatPack:
    """``term -> (granted, resolved, wide_granted, wide_resolved, wide_unread, wide_finer_unread)``.

    The finer twins are the widened counts less one resolved row, so the two
    readings are told apart; ``None`` is a Term built before the widened counts.
    """
    entries = []
    for year, counts in sorted(terms.items(), reverse=True):
        if counts is None:
            entries.append(
                StatPackInterimTerm(term=year, substantive_resolved=100, substantive_granted=10)
            )
            continue
        granted, resolved, wg, wr, unread, finer_unread = counts
        entries.append(
            StatPackInterimTerm(
                term=year,
                substantive_resolved=resolved,
                substantive_granted=granted,
                finer_resolved=resolved,
                finer_granted=granted,
                finer_moot=0,
                finer_unread=0,
                wide_resolved=wr,
                wide_granted=wg,
                wide_finer_resolved=wr - 1,
                wide_finer_granted=wg,
                wide_finer_unread=finer_unread,
                wide_unread=unread,
            )
        )
    return StatPack(corpus_rows=1, interim=StatPackInterim(terms=entries))


def test_the_registered_constants() -> None:
    assert INTERIM_WINDOW_FROM_TERM == WIDE_APPLICATION_KIND_FROM_TERM == 2027
    assert INTERIM_LOOKBACK_TERMS == 3


_TERMS: dict[int, _Counts | None] = {
    2020: (50, 100, 60, 120, 0, 0),  # outside the window: never pooled from OT2027
    2023: (10, 100, 12, 120, 0, 0),
    2024: (10, 100, 12, 120, 0, 0),
    2025: (10, 100, 12, 120, 0, 0),
    2026: (10, 100, 12, 120, 0, 0),
}


def test_before_the_window_term_the_registered_pool_stands() -> None:
    pack = _pack(_TERMS)
    assert interim_base_rate(2026, pack, lookback_terms=10) == pytest.approx(80 / 400)
    assert interim_base_rate(2026, pack, lookback_terms=10, reading="finer") == pytest.approx(
        80 / 400
    )


@pytest.mark.parametrize("lookback", [0, 3, 10])
def test_from_the_window_term_the_pool_is_three_terms_of_the_widened_slice(
    lookback: int,
) -> None:
    pack = _pack(_TERMS)
    assert interim_base_rate(2027, pack, lookback_terms=lookback) == pytest.approx(36 / 360)
    assert interim_base_rate(2027, pack, lookback_terms=lookback, reading="finer") == pytest.approx(
        36 / 357
    )


@pytest.mark.parametrize(
    ("older", "registered_refuses", "finer_refuses"),
    [
        (None, True, True),
        ((10, 100, 12, 120, 1, 0), True, True),
        ((10, 100, 12, 120, 0, 1), False, True),
    ],
    ids=["predates", "ask-unread", "reading-unread"],
)
def test_the_window_refuses_a_term_it_does_not_cover(
    older: _Counts | None, registered_refuses: bool, finer_refuses: bool
) -> None:
    pack = _pack({**_TERMS, 2024: older})
    registered = interim_base_rate(2027, pack, lookback_terms=10)
    finer = interim_base_rate(2027, pack, lookback_terms=10, reading="finer")
    assert (registered is None) is registered_refuses
    assert (finer is None) is finer_refuses
    # A Term outside the window never refuses it.
    assert interim_base_rate(2027, _pack({**_TERMS, 2020: older}), lookback_terms=10) is not None


def test_the_window_keeps_the_floor() -> None:
    thin: dict[int, _Counts | None] = {
        2024: (1, 10, 1, 15, 0, 0),
        2025: (1, 10, 1, 15, 0, 0),
        2026: (1, 10, 1, 15, 0, 0),
    }
    assert interim_base_rate(2027, _pack(thin)) is None  # 45 < 50


@pytest.mark.parametrize(
    "ask",
    [
        "for a partial stay",
        "for stay of removal",
        "for stays of execution of sentences of death",
        "for a stayor vacatur",
        "to recall and stay the mandate",
        "to recall the mandate",
        "for writ of injunction",
        "for injunction pending appeal",
        "Injunction",
        "to suspend the effect of the denial of the petition for a writ of certiorari",
        "for temporary restraining order",
        "for interim relief",
        "vacate lower court orders",
    ],
)
def test_the_widened_vocabulary_reads_what_the_registered_one_misses(ask: str) -> None:
    text = [f"Application (25A9) {ask}, submitted to The Chief Justice."]
    assert application_kind(text) is ApplicationKind.unknown
    assert application_kind_wide(text) is ApplicationKind.substantive


@pytest.mark.parametrize(
    ("ask", "expected"),
    [
        ("for bail pending appeal", ApplicationKind.unknown),
        ("for release pending appeal", ApplicationKind.unknown),
        ("for a certificate of appealability", ApplicationKind.unknown),
        ("for leave to file a reply to the brief in opposition", ApplicationKind.unknown),
        ("to file petition for rehearing in excess of the word limits", ApplicationKind.unknown),
        (
            "to extend the time to file a petition for a writ of certiorari",
            ApplicationKind.extension,
        ),
        ("for a stay", ApplicationKind.substantive),
    ],
)
def test_the_widened_vocabulary_moves_only_unreadable_asks(
    ask: str, expected: ApplicationKind
) -> None:
    text = [f"Application (25A9) {ask}, submitted to The Chief Justice."]
    assert application_kind_wide(text) is expected
    assert application_kind(text) in (expected, ApplicationKind.unknown)


def _row(kind: str, wide: str | None, disposition: str, reading: str | None) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        docket_number="25A1",
        case_name="In re Application",
        application_kind=kind,
        application_kind_wide=wide,
        disposition=disposition,
        interim_reading=reading,
    )


def test_the_statpack_counts_the_widened_slice_beside_the_registered_one() -> None:
    acc = _InterimAcc()
    for row in (
        _row("substantive", "substantive", "granted", "granted"),
        _row("unknown", "substantive", "denied", "granted-in-part"),
        _row("unknown", "substantive", "granted", "dismissed-moot"),
        _row("unknown", "substantive", "denied", None),
        _row("unknown", "unknown", "denied", "denied"),
        _row("extension", "extension", "granted", "granted"),
        _row("unknown", None, "denied", "denied"),
    ):
        acc.add(row)
    assert (acc.substantive_resolved, acc.substantive_granted) == (1, 1)
    assert (acc.wide_resolved, acc.wide_granted) == (4, 2)
    assert (acc.wide_finer_resolved, acc.wide_finer_granted, acc.wide_finer_unread) == (2, 2, 1)
    assert acc.wide_unread == 1


def test_a_twin_number_joins_no_widened_count() -> None:
    """A second row for a counted number is tallied a duplicate before any count reads it."""
    acc = _InterimAcc()
    acc.add(_row("unknown", "substantive", "granted", "granted"))
    acc.skip_duplicate()
    assert (acc.wide_resolved, acc.duplicate_rows) == (1, 1)
