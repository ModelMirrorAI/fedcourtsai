"""Every live-channel write stores its row at weight 1.

The corpus holds each decided petition as its own row, so a row stands for
itself and nothing about its serial, its disposition or the rows around it
changes the weight it lands at. These pin that at the one seam every
live-channel SCOTUS payload is written through, and at the back-fill that
weights a row no channel ever did.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.ingest import UNSAMPLED_WEIGHT, backfill_live_signals
from fedcourtsai.pipeline.live import ingest_live_payload
from tests.test_live import _DENIED_ENTRY, _GRANTED_ENTRY, _payload

_POLLED = date(2026, 7, 1)


def _corpus_with_cursors(tmp_path: Path, *, cursor: int) -> Path:
    """An empty corpus whose OT2019 walk cursors sit at ``cursor``."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        for stream in ("historical-paid", "historical-ifp"):
            corpus.set_live_cursor(conn, 19, stream, cursor)
        conn.commit()
    return db


def _serve(
    db: Path,
    tmp_path: Path,
    number: str,
    docket_id: int,
    *,
    denied: bool = True,
    form: Literal["cert", "application"] = "cert",
) -> int | None:
    """Serve one docket through the live-ingest seam; read back its stored weight."""
    entry = _DENIED_ENTRY if denied else _GRANTED_ENTRY
    payload = _payload(number, proceedings=[entry])
    result = ingest_live_payload(
        db, tmp_path / "data", payload, docket_id, today=_POLLED, form=form
    )
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, result.case_id)
    assert stored is not None
    return stored.sample_weight


@pytest.mark.parametrize(
    ("number", "docket_id", "denied", "form"),
    [
        # A denial under the walk's cursor with nothing stored around it.
        ("19-1000", 190001000, True, "cert"),
        ("19-1001", 190001001, True, "cert"),
        ("19-5010", 190005010, True, "cert"),
        ("19-1000", 190001000, False, "cert"),
        # A Term the walk never reached.
        ("21-1000", 210001000, True, "cert"),
        ("19A11", 190009911, True, "application"),
    ],
)
def test_a_served_docket_lands_at_weight_one(
    tmp_path: Path,
    number: str,
    docket_id: int,
    denied: bool,
    form: Literal["cert", "application"],
) -> None:
    db = _corpus_with_cursors(tmp_path, cursor=9000)
    assert _serve(db, tmp_path, number, docket_id, denied=denied, form=form) == UNSAMPLED_WEIGHT


def test_a_re_serve_keeps_weight_one(tmp_path: Path) -> None:
    db = _corpus_with_cursors(tmp_path, cursor=9000)
    assert _serve(db, tmp_path, "19-1000", 190001000) == UNSAMPLED_WEIGHT
    assert _serve(db, tmp_path, "19-1000", 190001000) == UNSAMPLED_WEIGHT


def test_a_re_serve_takes_a_stored_weight_above_one_down_to_one(tmp_path: Path) -> None:
    """The upsert keeps the smaller of the stored and the incoming weight.

    No writer lands a weight above 1 and ``validate-corpus`` fails on a stored
    one, so this is not a state the corpus holds. If one arrived by another
    route, serving the docket again stores it as the one petition it is.
    """
    db = _corpus_with_cursors(tmp_path, cursor=9000)
    _serve(db, tmp_path, "19-1000", 190001000)
    with corpus.connect(db) as conn, conn:
        conn.execute("UPDATE cases SET sample_weight = 10 WHERE case_id = 'scotus/190001000'")
    assert _serve(db, tmp_path, "19-1000", 190001000) == UNSAMPLED_WEIGHT


def test_backfill_weights_an_unweighted_live_row_at_one(tmp_path: Path) -> None:
    """A live-slice row no channel weighted takes 1, once, wherever it sits."""
    db = _corpus_with_cursors(tmp_path, cursor=9000)
    for serial in (1000, 1001, 5010):
        _serve(db, tmp_path, f"19-{serial}", 190000000 + serial)
    with corpus.connect(db) as conn, conn:
        conn.execute("UPDATE cases SET sample_weight = NULL")

    assert backfill_live_signals(db) == (0, 3)
    with corpus.connect(db) as conn:
        weights = {row["sample_weight"] for row in conn.execute("SELECT sample_weight FROM cases")}
    assert weights == {UNSAMPLED_WEIGHT}
    assert backfill_live_signals(db) == (0, 0)


def test_backfill_leaves_a_row_outside_the_live_slice_unweighted(tmp_path: Path) -> None:
    """The fill is the live channel's: a row it never polled asserts nothing."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [corpus.CorpusRow(case_id="scotus/7", court="scotus")])
        conn.commit()
    assert backfill_live_signals(db) == (0, 0)
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, "scotus/7")
    assert stored is not None and stored.sample_weight is None
