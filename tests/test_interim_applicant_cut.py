"""The interim statpack's applicant-class cut: who applies, and whether the case is capital.

What the cut owes and these pin:

- **It partitions the finer pool.** Each Term's cells sum to that Term's
  ``finer_*`` and ``wide_finer_*`` counts, so a moot dismissal and an unread
  row stay out of the cut exactly as they stay out of the pool.
- **The class is the caption rule's and the marking the capital cut's**: a
  State officer's caption reads ``state``, a federal officer's ``federal``, and
  a row no live poll stamped reads ``unknown`` rather than ``unmarked``.
- **The pool reads the scored pool's Terms and vocabulary** and refuses where
  that pool would.
- **The published table applies the floor**: a thin cell shows its count, not
  its rate, and the scored yardstick is unchanged.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fedcourtsai import analytics, corpus
from fedcourtsai.pipeline.base_rates import (
    INTERIM_APPLICANT_CUT_MIN_RESOLVED,
    INTERIM_WINDOW_FROM_TERM,
    interim_applicant_cut_pool,
)
from fedcourtsai.schemas import (
    Disposition,
    StatPack,
    StatPackInterim,
    StatPackInterimApplicantCut,
    StatPackInterimTerm,
)


def _application(case_id: str, docket: str, title: str, **kwargs: object) -> corpus.CorpusRow:
    fields: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket,
        "petitioner_title": title,
        "case_name": f"{title} v. Respondent",
        "application_kind": "substantive",
        "application_kind_wide": "substantive",
        "disposition": Disposition.granted,
        "interim_reading": "granted",
        "last_live_polled": date(2026, 7, 1),
        "sample_weight": 1,
    }
    fields.update(kwargs)
    return corpus.CorpusRow.model_validate(fields)


_DENIED = {"disposition": Disposition.denied, "interim_reading": "denied"}
_STATE = "John Q. Hamm, Commissioner, Alabama Department of Corrections"
_FEDERAL = "Department of Homeland Security, et al."


def _seed(db: Path) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # A State asking to vacate a stay of execution: state x capital.
                _application("scotus/1", "24A1", _STATE, capital_case=True),
                _application("scotus/2", "24A2", _STATE, capital_case=True, **_DENIED),
                _application("scotus/3", "24A3", _FEDERAL),
                _application("scotus/4", "24A4", "Jane Doe", **_DENIED),
                # A moot dismissal and an unread row leave the finer pool, and so the cut.
                _application(
                    "scotus/5",
                    "24A5",
                    "John Roe",
                    disposition=Disposition.dismissed,
                    interim_reading="dismissed-moot",
                ),
                _application("scotus/6", "24A6", "Richard Roe", interim_reading=None),
                # No live poll stamped it: its marking is unknown, not unmarked.
                _application("scotus/7", "23A1", "Mary Major", last_live_polled=None),
            ],
        )


def test_the_registered_floor() -> None:
    assert INTERIM_APPLICANT_CUT_MIN_RESOLVED == 30


def test_the_cut_partitions_each_terms_finer_counts(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db)
    interim = analytics.build_statpack(corpus_db_path=db).interim
    assert interim is not None
    assert interim.applicant_class_rule == "caption-v2"
    ot24, ot23 = interim.terms
    assert ot24.applicant_cuts is not None
    cells = {
        (c.applicant_class, c.capital_marking): (c.finer_granted, c.finer_resolved)
        for c in ot24.applicant_cuts
    }
    assert cells == {
        ("federal", "unmarked"): (1, 1),
        ("state", "capital"): (1, 2),
        ("private", "unmarked"): (0, 1),
    }
    assert sum(c.finer_resolved for c in ot24.applicant_cuts) == ot24.finer_resolved == 4
    assert sum(c.finer_granted for c in ot24.applicant_cuts) == ot24.finer_granted == 2
    assert sum(c.wide_finer_resolved for c in ot24.applicant_cuts) == ot24.wide_finer_resolved
    assert ot23.applicant_cuts == [
        StatPackInterimApplicantCut(
            applicant_class="private",
            capital_marking="unknown",
            finer_resolved=1,
            finer_granted=1,
            wide_finer_resolved=1,
            wide_finer_granted=1,
        )
    ]


def test_a_pack_without_the_cut_serializes_without_it() -> None:
    pack = StatPack(corpus_rows=1, interim=StatPackInterim(terms=[StatPackInterimTerm(term=2024)]))
    payload = pack.model_dump(mode="json")
    assert "applicant_class_rule" not in payload["interim"]
    assert "applicant_cuts" not in payload["interim"]["terms"][0]
    assert "Substantive applications by applicant class" not in (
        analytics.render_statpack_markdown(pack)
    )


def _cell(applicant: str, marking: str, granted: int, resolved: int) -> StatPackInterimApplicantCut:
    return StatPackInterimApplicantCut.model_validate(
        {
            "applicant_class": applicant,
            "capital_marking": marking,
            "finer_resolved": resolved,
            "finer_granted": granted,
            # The widened twins differ, so a pool reading the wrong pair shows.
            "wide_finer_resolved": resolved + 1,
            "wide_finer_granted": granted,
        }
    )


def _term(year: int, *, unread: int = 0, cuts: bool = True) -> StatPackInterimTerm:
    cells = [_cell("state", "capital", 7, 10), _cell("private", "unmarked", 4, 40)]
    return StatPackInterimTerm(
        term=year,
        finer_resolved=50,
        finer_granted=11,
        finer_moot=0,
        finer_unread=unread,
        wide_resolved=52,
        wide_granted=11,
        wide_finer_resolved=52,
        wide_finer_granted=11,
        wide_finer_unread=0,
        wide_unread=0,
        applicant_cuts=cells if cuts else None,
    )


def _pack(*terms: StatPackInterimTerm) -> StatPack:
    ordered = sorted(terms, key=lambda t: t.term, reverse=True)
    return StatPack(
        corpus_rows=1, interim=StatPackInterim(terms=ordered, applicant_class_rule="caption-v2")
    )


def test_the_pool_reads_strictly_prior_terms_within_the_lookback() -> None:
    pack = _pack(_term(2026), _term(2025), _term(2024), _term(2023))
    pooled = interim_applicant_cut_pool(2026, pack, lookback_terms=2)
    # OT2026 is the cell's own Term and OT2023 is outside the window.
    assert pooled == {("state", "capital"): (14, 20), ("private", "unmarked"): (8, 80)}


def test_the_pool_refuses_where_the_scored_pool_would() -> None:
    assert interim_applicant_cut_pool(2026, _pack(_term(2025, unread=1))) is None
    assert interim_applicant_cut_pool(2026, _pack(_term(2025, cuts=False))) is None
    assert interim_applicant_cut_pool(2026, StatPack(corpus_rows=1)) is None


def test_the_interim_window_pools_the_widened_counts() -> None:
    term = INTERIM_WINDOW_FROM_TERM
    pack = _pack(*(_term(year) for year in range(term - 4, term)))
    pooled = interim_applicant_cut_pool(term, pack, lookback_terms=10)
    # Three Terms, whatever the caller's lookback, on the `wide_finer_*` pair.
    assert pooled == {("state", "capital"): (21, 33), ("private", "unmarked"): (12, 123)}


def test_the_table_shows_a_thin_cell_without_its_rate() -> None:
    pack = _pack(_term(2026), _term(2025), _term(2024))
    md = analytics.render_statpack_markdown(pack, interim_lookback_terms=10)
    section = md.split("### Substantive applications by applicant class")[1]
    assert "the 10 application-Term(s) before OT2026" in section
    assert "Descriptive context, not a yardstick" in section
    # 20 resolved is under the floor; 80 and the margins clear it.
    assert "| state | n=20, below floor | — | n=20, below floor |" in section
    assert "| private | — | 10.0% (8/80) | 10.0% (8/80) |" in section
    assert "| all | n=20, below floor | 10.0% (8/80) | 22.0% (22/100) |" in section
