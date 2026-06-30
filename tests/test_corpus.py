import sqlite3
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition, EventKind


def _row(case_id: str = "ca9/123", **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "docket_number": "23-1234",
        "date_filed": date(2025, 1, 2),
        "date_decided": date(2026, 1, 2),
        "disposition": Disposition.granted,
        "judges": ["smith", "jones"],
        "topic": "civil rights",
        "citations": ["410 U.S. 113"],
        "opinion_text": "full text",
        "summary": "short",
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def test_db_path_under_corpus_root() -> None:
    assert corpus.corpus_db_path(Path("corpus")) == Path("corpus/corpus.db")


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        corpus.CorpusRow.model_validate({"case_id": "ca9/1", "court": "ca9", "surprise": "no"})


def test_roundtrip_preserves_all_fields(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    row = _row()
    with corpus.connect(db) as conn:
        assert corpus.upsert_rows(conn, [row]) == 1
        fetched = corpus.get_row(conn, "ca9/123")
    assert fetched == row


def test_connect_creates_parent_dir(tmp_path: Path) -> None:
    db = tmp_path / "nested" / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 0
    assert db.exists()


def test_schema_and_migration_ddl_agree(tmp_path: Path) -> None:
    """A fresh `cases` table has exactly the columns the migration map declares."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(cases)")}
    assert cols == set(corpus._COLUMNS) == set(corpus._CASES_COLUMN_DDL)


def test_connect_migrates_legacy_cases_table(tmp_path: Path) -> None:
    """A corpus written before the enriched columns is migrated on open, not broken."""
    db = tmp_path / "corpus.db"
    # The pre-enrichment schema: no panel / parties / attorneys / citation_count /
    # precedential_status columns.
    legacy = sqlite3.connect(db)
    legacy.executescript(
        """
        CREATE TABLE cases (
            case_id       TEXT PRIMARY KEY,
            court         TEXT NOT NULL,
            docket_number TEXT NOT NULL DEFAULT '',
            date_filed    TEXT,
            date_decided  TEXT,
            disposition   TEXT,
            judges        TEXT NOT NULL DEFAULT '[]',
            topic         TEXT,
            citations     TEXT NOT NULL DEFAULT '[]',
            opinion_text  TEXT,
            summary       TEXT,
            last_pulled   TEXT
        );
        INSERT INTO cases (case_id, court) VALUES ('ca9/1', 'ca9');
        """
    )
    legacy.commit()
    legacy.close()

    with corpus.connect(db) as conn:
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(cases)")}
        assert cols == set(corpus._COLUMNS)
        # The pre-existing row reads back with the new columns at their defaults,
        # and the pull governor can scan it without raising.
        legacy_row = corpus.get_row(conn, "ca9/1")
        assert legacy_row is not None
        assert legacy_row.panel == []
        assert legacy_row.parties == []
        assert corpus.rotation_for_pull(conn, limit=10) == [legacy_row]
        # And the enriched columns are now writable.
        assert corpus.upsert_rows(conn, [_row()]) == 1
        assert corpus.get_row(conn, "ca9/123") == _row()


def test_upsert_is_idempotent_by_case_id(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(topic="old")])
        corpus.upsert_rows(conn, [_row(topic="new")])
        assert corpus.count(conn) == 1
        fetched = corpus.get_row(conn, "ca9/123")
        assert fetched is not None
        assert fetched.topic == "new"


def test_unresolved_row_has_null_disposition(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca1/9", disposition=None)])
        fetched = corpus.get_row(conn, "ca1/9")
    assert fetched is not None
    assert fetched.disposition is None


def test_iter_rows_filters_by_court_and_disposition(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/1", court="ca9", disposition=Disposition.granted),
        _row(case_id="ca9/2", court="ca9", disposition=Disposition.denied),
        _row(case_id="ca1/3", court="ca1", disposition=Disposition.granted),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        by_court = [r.case_id for r in corpus.iter_rows(conn, court="ca9")]
        granted = [r.case_id for r in corpus.iter_rows(conn, disposition=Disposition.granted)]
        both = [
            r.case_id for r in corpus.iter_rows(conn, court="ca9", disposition=Disposition.granted)
        ]
    assert by_court == ["ca9/1", "ca9/2"]
    assert granted == ["ca1/3", "ca9/1"]
    assert both == ["ca9/1"]


def test_get_row_missing_returns_none(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "nope/0") is None


def test_last_pulled_roundtrips(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/7", last_pulled=date(2026, 6, 20))])
        fetched = corpus.get_row(conn, "ca9/7")
    assert fetched is not None
    assert fetched.last_pulled == date(2026, 6, 20)


def test_last_pulled_defaults_to_none(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/8")])
        fetched = corpus.get_row(conn, "ca9/8")
    assert fetched is not None
    assert fetched.last_pulled is None


def test_predict_eligible_roundtrips_and_defaults_false(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="scotus/1", court="scotus", predict_eligible=True)])
        corpus.upsert_rows(conn, [_row(case_id="ca9/1")])  # default
        eligible = corpus.get_row(conn, "scotus/1")
        default = corpus.get_row(conn, "ca9/1")
    assert eligible is not None and eligible.predict_eligible is True
    assert default is not None and default.predict_eligible is False


def test_predict_eligible_latches_on_and_never_clears(tmp_path: Path) -> None:
    # Once a case is in prediction scope, a later re-ingest (even one that would
    # compute the flag False under a narrower rule) must not drop it back out.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", predict_eligible=True)])
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", topic="refreshed", predict_eligible=False)])
        fetched = corpus.get_row(conn, "ca9/9")
    assert fetched is not None
    assert fetched.topic == "refreshed"  # other columns still overwrite
    assert fetched.predict_eligible is True  # but the latch holds


def test_originating_link_columns_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    originating_court="ca9",
                    originating_docket_number="21-35466",
                )
            ],
        )
        corpus.upsert_rows(conn, [_row(case_id="ca9/1")])  # default: no link
        fetched = corpus.get_row(conn, "scotus/1")
        default = corpus.get_row(conn, "ca9/1")
    assert fetched is not None
    assert fetched.originating_court == "ca9"
    assert fetched.originating_docket_number == "21-35466"
    assert default is not None
    assert default.originating_court is None and default.originating_docket_number is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("21-35466", "21-35466"),
        ("  21-35466 ", "21-35466"),
        ("No. 21-35466", "21-35466"),
        ("no. 21-35466", "21-35466"),
        ("21-35466, 21-35467", "21-35466,21-35467"),  # consolidated: kept distinct
        ("", None),
        ("   ", None),
        (None, None),
    ],
)
def test_normalize_docket_number(raw: str | None, expected: str | None) -> None:
    assert corpus.normalize_docket_number(raw) == expected


def test_latch_originating_flips_tracked_coa_docket_eligible(tmp_path: Path) -> None:
    # A SCOTUS docket linked to a *tracked* ca9 docket flips that docket eligible,
    # joining on court id + normalized docket number (here a "No." label differs).
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/55", court="ca9", docket_number="21-35466")])
        scotus = _row(
            case_id="scotus/1",
            court="scotus",
            originating_court="ca9",
            originating_docket_number="No. 21-35466",
        )
        assert corpus.latch_originating_eligible(conn, [scotus]) == 1
        coa = corpus.get_row(conn, "ca9/55")
    assert coa is not None and coa.predict_eligible is True


def test_latch_originating_is_noop_for_unlinked_or_untracked(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/55", court="ca9", docket_number="21-35466")])
        # Unlinked SCOTUS row, a non-SCOTUS row, and a link to an untracked docket
        # (wrong number) all leave the tracked CoA docket alone.
        rows = [
            _row(case_id="scotus/1", court="scotus"),
            _row(
                case_id="ca1/2",
                court="ca1",
                originating_court="ca9",
                originating_docket_number="21-35466",
            ),
            _row(
                case_id="scotus/3",
                court="scotus",
                originating_court="ca9",
                originating_docket_number="99-00000",
            ),
        ]
        assert corpus.latch_originating_eligible(conn, rows) == 0
        coa = corpus.get_row(conn, "ca9/55")
    assert coa is not None and coa.predict_eligible is False


def test_latch_originating_is_idempotent_and_never_clears(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    scotus = _row(
        case_id="scotus/1",
        court="scotus",
        originating_court="ca9",
        originating_docket_number="21-35466",
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/55", court="ca9", docket_number="21-35466")])
        assert corpus.latch_originating_eligible(conn, [scotus]) == 1
        # Second pass: already latched, so nothing is newly flipped, but it holds.
        assert corpus.latch_originating_eligible(conn, [scotus]) == 0
        coa = corpus.get_row(conn, "ca9/55")
    assert coa is not None and coa.predict_eligible is True


def test_is_historical_mandatory_detects_bare_scotus_docket() -> None:
    # A pre-1925 mandatory-jurisdiction matter (issue #309): the snapshot is sparse
    # and every activity date is null, but the bare sequential docket number ("801",
    # no Term-year prefix) gives it away.
    row = corpus.CorpusRow(case_id="scotus/1001931", court="scotus", docket_number="801")
    assert corpus.is_historical_mandatory(row) is True


def test_is_historical_mandatory_keeps_modern_scotus_docket() -> None:
    # A modern discretionary-cert docket carries a Term-year prefix, so it is in
    # scope; an undated / unnumbered SCOTUS row is not assumed historical either.
    modern = corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="01-7700")
    bare_application = corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="22A123")
    unknown = corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="")
    assert corpus.is_historical_mandatory(modern) is False
    assert corpus.is_historical_mandatory(bare_application) is False
    assert corpus.is_historical_mandatory(unknown) is False


def test_is_historical_mandatory_uses_pre_1925_filing_date() -> None:
    # A filing date before the Judiciary Act of 1925 corroborates the era on the
    # rare row that carries one, even if the docket number looks modern.
    pre = corpus.CorpusRow(
        case_id="scotus/5", court="scotus", docket_number="No. 5", date_filed=date(1897, 4, 1)
    )
    post = corpus.CorpusRow(
        case_id="scotus/6", court="scotus", docket_number="01-7700", date_filed=date(1999, 1, 1)
    )
    assert corpus.is_historical_mandatory(pre) is True
    assert corpus.is_historical_mandatory(post) is False


def test_is_historical_mandatory_only_applies_to_scotus() -> None:
    # The regime is a Supreme Court concept; a bare-numbered lower-court docket is
    # not swept up (and the gate only sees a case once it is SCOTUS-eligible anyway).
    row = corpus.CorpusRow(case_id="ca9/801", court="ca9", docket_number="801")
    assert corpus.is_historical_mandatory(row) is False


def test_is_stale_unresolvable_detects_old_open_scotus_petition() -> None:
    # Issue #333: a modern-format docket from an old Term ("93-7515" -> OT1993),
    # still open in the corpus (no disposition, no decision date), is unresolvable.
    row = corpus.CorpusRow(case_id="scotus/1004289", court="scotus", docket_number="93-7515")
    assert corpus.is_stale_unresolvable(row) is True


def test_is_stale_unresolvable_keeps_recent_open_petition() -> None:
    # A recent Term's petition may legitimately be open and pending — never drop it.
    row = corpus.CorpusRow(case_id="scotus/9", court="scotus", docket_number="24-101")
    assert corpus.is_stale_unresolvable(row) is False


def test_is_stale_unresolvable_keeps_resolved_old_petition() -> None:
    # An old docket the corpus *did* resolve carries ground truth to score against,
    # so it stays in scope; only the unresolvable stubs are dropped.
    decided = corpus.CorpusRow(
        case_id="scotus/10",
        court="scotus",
        docket_number="01-7700",
        disposition=Disposition.denied,
        date_decided=date(2002, 1, 7),
    )
    assert corpus.is_stale_unresolvable(decided) is False


def test_is_stale_unresolvable_ignores_unparseable_and_non_scotus() -> None:
    # Conservative: a docket whose Term year can't be parsed (bare/original/blank) is
    # left in scope rather than guessed, and the predicate is SCOTUS-only.
    bare = corpus.CorpusRow(case_id="scotus/801", court="scotus", docket_number="801")
    original = corpus.CorpusRow(case_id="scotus/11", court="scotus", docket_number="22O141")
    blank = corpus.CorpusRow(case_id="scotus/12", court="scotus", docket_number="")
    lower = corpus.CorpusRow(case_id="ca9/13", court="ca9", docket_number="01-7700")
    assert corpus.is_stale_unresolvable(bare) is False
    assert corpus.is_stale_unresolvable(original) is False
    assert corpus.is_stale_unresolvable(blank) is False
    assert corpus.is_stale_unresolvable(lower) is False


def test_scotus_term_year_parses_two_digit_term_with_pivot() -> None:
    assert corpus._scotus_term_year("01-7700") == 2001
    assert corpus._scotus_term_year("93-7515") == 1993
    assert corpus._scotus_term_year("24-101") == 2024
    assert corpus._scotus_term_year("801") is None
    assert corpus._scotus_term_year("22A123") is None


def test_upsert_without_stamp_preserves_prior_last_pulled(tmp_path: Path) -> None:
    # A bulk re-ingest (no stamp) must not reset a timestamp a prior pull recorded,
    # else the governor would treat a freshly-refreshed case as never-pulled.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", last_pulled=date(2026, 6, 1))])
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", topic="refreshed", last_pulled=None)])
        fetched = corpus.get_row(conn, "ca9/9")
    assert fetched is not None
    assert fetched.topic == "refreshed"  # other columns still overwrite
    assert fetched.last_pulled == date(2026, 6, 1)  # but the stamp is preserved


def test_retrieve_priors_defaults_to_resolved_only(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/decided", disposition=Disposition.granted),
        _row(case_id="ca9/open", disposition=None, date_decided=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery())
    assert [r.case_id for r in priors] == ["ca9/decided"]


def test_retrieve_priors_include_open(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/decided", disposition=Disposition.granted),
        _row(case_id="ca9/open", disposition=None, date_decided=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(resolved_only=False))
    assert {r.case_id for r in priors} == {"ca9/decided", "ca9/open"}


def test_retrieve_priors_exact_filters(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/1", court="ca9", topic="civil rights", disposition=Disposition.granted),
        _row(case_id="ca9/2", court="ca9", topic="contracts", disposition=Disposition.granted),
        _row(case_id="ca1/3", court="ca1", topic="civil rights", disposition=Disposition.denied),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        by_court = corpus.retrieve_priors(conn, corpus.PriorQuery(court="ca9"))
        by_topic = corpus.retrieve_priors(conn, corpus.PriorQuery(topic="civil rights"))
        by_disp = corpus.retrieve_priors(conn, corpus.PriorQuery(disposition=Disposition.denied))
    assert {r.case_id for r in by_court} == {"ca9/1", "ca9/2"}
    assert {r.case_id for r in by_topic} == {"ca9/1", "ca1/3"}
    assert [r.case_id for r in by_disp] == ["ca1/3"]


def test_retrieve_priors_judge_overlap_required_and_ranked(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/both", judges=["smith", "jones"], date_decided=date(2025, 1, 1)),
        _row(case_id="ca9/one", judges=["smith", "lee"], date_decided=date(2025, 1, 1)),
        _row(case_id="ca9/none", judges=["doe"], date_decided=date(2025, 1, 1)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(judges=["smith", "jones"]))
    # Only cases sharing a judge survive; sharing more ranks higher.
    assert [r.case_id for r in priors] == ["ca9/both", "ca9/one"]


def test_retrieve_priors_citation_overlap_required(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/cited", citations=["410 U.S. 113"]),
        _row(case_id="ca9/other", citations=["347 U.S. 483"]),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(citations=["410 U.S. 113"]))
    assert [r.case_id for r in priors] == ["ca9/cited"]


def test_retrieve_priors_ranks_by_total_overlap(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/more", judges=["smith", "jones"], citations=["410 U.S. 113"]),
        _row(case_id="ca9/less", judges=["smith"], citations=["410 U.S. 113"]),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(
            conn, corpus.PriorQuery(judges=["smith", "jones"], citations=["410 U.S. 113"])
        )
    # Both satisfy every filter; the one sharing more judges has higher overlap.
    assert [r.case_id for r in priors] == ["ca9/more", "ca9/less"]


def test_retrieve_priors_requires_all_given_filters(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    # Shares the judge but cites a different authority — excluded, since each
    # given list filter must overlap (the filters AND together).
    rows = [
        _row(case_id="ca9/judge-only", judges=["smith"], citations=["999 U.S. 1"]),
        _row(case_id="ca9/both", judges=["smith"], citations=["410 U.S. 113"]),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(
            conn, corpus.PriorQuery(judges=["smith"], citations=["410 U.S. 113"])
        )
    assert [r.case_id for r in priors] == ["ca9/both"]


def test_retrieve_priors_ties_break_by_recency_then_case_id(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/old", judges=["smith"], date_decided=date(2020, 1, 1)),
        _row(case_id="ca9/new", judges=["smith"], date_decided=date(2025, 1, 1)),
        _row(case_id="ca9/undated", judges=["smith"], date_decided=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(judges=["smith"]))
    # Equal overlap: newest decision first, undated last.
    assert [r.case_id for r in priors] == ["ca9/new", "ca9/old", "ca9/undated"]


def test_retrieve_priors_respects_limit(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [_row(case_id=f"ca9/{i}", disposition=Disposition.granted) for i in range(5)]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(), limit=2)
    assert len(priors) == 2


def test_retrieve_priors_zero_limit_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
        assert corpus.retrieve_priors(conn, corpus.PriorQuery(), limit=0) == []


def test_prior_query_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        corpus.PriorQuery.model_validate({"surprise": "no"})


def _active(case_id: str, **kw: object) -> corpus.CorpusRow:
    """An unresolved (open) corpus row, eligible for rotation."""
    return _row(case_id=case_id, disposition=None, date_decided=None, **kw)


def test_rotation_orders_never_pulled_first_then_oldest(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _active("ca9/1", last_pulled=date(2026, 6, 20)),
        _active("ca9/2", last_pulled=None),  # never pulled — stalest
        _active("ca9/3", last_pulled=date(2026, 6, 10)),  # oldest dated
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        order = [r.case_id for r in corpus.rotation_for_pull(conn, limit=10)]
    assert order == ["ca9/2", "ca9/3", "ca9/1"]


def test_rotation_respects_limit(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [_active(f"ca9/{i}", last_pulled=None) for i in range(5)]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        picked = corpus.rotation_for_pull(conn, limit=2)
    assert len(picked) == 2


def test_rotation_zero_limit_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_active("ca9/1")])
        assert corpus.rotation_for_pull(conn, limit=0) == []


def test_rotation_skips_closed_and_resolved(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _active("ca9/open"),
        _row(case_id="ca9/resolved", disposition=Disposition.granted, date_decided=None),
        _row(case_id="ca9/closed", disposition=None, date_decided=date(2026, 1, 1)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        kept = [r.case_id for r in corpus.rotation_for_pull(conn, limit=10)]
    assert kept == ["ca9/open"]


def test_rotation_without_skip_closed_includes_all(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _active("ca9/open", last_pulled=None),
        _row(case_id="ca9/resolved", disposition=Disposition.granted, last_pulled=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        kept = {r.case_id for r in corpus.rotation_for_pull(conn, limit=10, skip_closed=False)}
    assert kept == {"ca9/open", "ca9/resolved"}


def _event(
    case_id: str = "ca9/123", event_id: str = "evt-appeal-disposition", **kw: object
) -> corpus.CorpusEvent:
    base: dict[str, object] = {
        "case_id": case_id,
        "event_id": event_id,
        "court": "ca9",
        "kind": EventKind.appeal,
        "title": "Doe v. Roe",
        "opened_at": date(2026, 6, 1),
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


def test_event_roundtrips(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    event = _event(description="appeal outcome", resolved=True)
    with corpus.connect(db) as conn:
        assert corpus.upsert_events(conn, [event]) == 1
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched == [event]


def test_event_docket_entry_id_roundtrips(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    event = _event(event_id="evt-motion-stay", kind=EventKind.motion, docket_entry_id=987)
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [event])
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched[0].docket_entry_id == 987


def test_event_docket_entry_id_defaults_to_none(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event()])
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched[0].docket_entry_id is None


def test_events_upsert_is_idempotent_by_case_and_event(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(title="old")])
        corpus.upsert_events(conn, [_event(title="new")])
        fetched = corpus.events_for_case(conn, "ca9/123")
        assert corpus.event_count(conn) == 1
    assert fetched[0].title == "new"


def test_events_upsert_never_reopens_a_resolved_event(tmp_path: Path) -> None:
    # Resolution latches on: re-ingesting a docket (re-discovery, or a quarterly
    # seed reconcile) carries freshly-extracted events with resolved=False, which
    # must not reopen an event a prior outcome detection already closed.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(resolved=False)])
        corpus.set_event_resolved(conn, "ca9/123", "evt-appeal-disposition")
        # A later re-ingest re-asserts the event as open — it must stay resolved.
        corpus.upsert_events(conn, [_event(title="re-ingested", resolved=False)])
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched[0].resolved is True  # resolution preserved
    assert fetched[0].title == "re-ingested"  # other fields still refresh


def test_multiple_events_per_case(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [_event(event_id="evt-appeal-disposition"), _event(event_id="evt-motion-stay")],
        )
        ids = [e.event_id for e in corpus.events_for_case(conn, "ca9/123")]
    assert ids == ["evt-appeal-disposition", "evt-motion-stay"]


def test_events_for_missing_case_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.events_for_case(conn, "nope/0") == []


def test_set_event_resolved_flips_the_flag(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(resolved=False)])
        corpus.set_event_resolved(conn, "ca9/123", "evt-appeal-disposition")
        (event,) = corpus.events_for_case(conn, "ca9/123")
    assert event.resolved is True


def test_set_event_resolved_unknown_event_is_a_noop(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(resolved=False)])
        corpus.set_event_resolved(conn, "ca9/123", "evt-nonexistent")
        (event,) = corpus.events_for_case(conn, "ca9/123")
    assert event.resolved is False


def test_watermark_set_and_get(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") is None
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 10))
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 10)


def test_watermark_only_moves_forward(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 10))
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 1))  # older — ignored
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 10)
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 20))  # newer — applied
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 20)


def test_watermark_is_per_court(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 10))
        corpus.set_discovery_watermark(conn, "ca1", date(2026, 5, 1))
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 10)
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 5, 1)


def test_snapshot_upsert_and_latest_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    payload = {"id": 123, "docket_entries": [{"id": 1, "description": "Filed"}]}
    with corpus.connect(db) as conn:
        assert corpus.latest_snapshot(conn, "ca9/123") is None
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 10), payload)
        found = corpus.latest_snapshot(conn, "ca9/123")
    assert found is not None
    snap_date, stored = found
    assert snap_date == date(2026, 6, 10)
    assert stored == payload


def test_snapshot_latest_returns_newest_date(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 10), {"v": 1})
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 20), {"v": 2})
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 15), {"v": 3})
        found = corpus.latest_snapshot(conn, "ca9/123")
    assert found is not None
    assert found == (date(2026, 6, 20), {"v": 2})


def test_snapshot_upsert_same_day_overwrites(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 10), {"v": 1})
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 10), {"v": 2})
        assert corpus.snapshot_count(conn) == 1
        found = corpus.latest_snapshot(conn, "ca9/123")
    assert found == (date(2026, 6, 10), {"v": 2})


def test_snapshot_is_per_case(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 10), {"case": "a"})
        corpus.upsert_snapshot(conn, "ca1/9", date(2026, 6, 10), {"case": "b"})
        assert corpus.latest_snapshot(conn, "ca9/123") == (date(2026, 6, 10), {"case": "a"})
        assert corpus.latest_snapshot(conn, "ca1/9") == (date(2026, 6, 10), {"case": "b"})
        assert corpus.snapshot_count(conn) == 2
