import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai import corpus, corpus_ranged
from fedcourtsai.schemas import (
    Disposition,
    EventKind,
    Judgment,
    MeritsTermination,
    Moment,
    Stage,
)


def _row(case_id: str = "ca9/123", **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "docket_number": "23-1234",
        "case_name": "Doe v. Roe",
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
        assert legacy_row.counsel == []
        assert legacy_row.date_cert_granted is None and legacy_row.date_cert_denied is None
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


def test_iter_rows_pushes_the_live_slice_filter_into_sql(tmp_path: Path) -> None:
    # The SQL form has to agree with `is_live_slice` in both directions: a pass
    # that only wants the slice must not hydrate the bulk-import rows to discard
    # them, and the complement must be the exact remainder.
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="scotus/1", court="scotus", last_live_polled=date(2026, 8, 27)),
        _row(case_id="scotus/2", court="scotus", last_live_polled=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        live = list(corpus.iter_rows(conn, live_slice=True))
        frozen = [r.case_id for r in corpus.iter_rows(conn, live_slice=False)]
    assert [r.case_id for r in live] == ["scotus/1"]
    assert all(corpus.is_live_slice(row) for row in live)
    assert frozen == ["scotus/2"]


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


def test_predict_eligible_self_heals_on_reingest(tmp_path: Path) -> None:
    # The column is a derived mirror of the court predicate, not a latch: a
    # re-ingest carrying the correctly-computed value overwrites a stale one.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", predict_eligible=True)])  # stale
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", topic="refreshed", predict_eligible=False)])
        fetched = corpus.get_row(conn, "ca9/9")
    assert fetched is not None
    assert fetched.topic == "refreshed"
    assert fetched.predict_eligible is False  # the mirror self-heals


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


def test_cert_stage_date_columns_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="22-451",
                    date_cert_granted=date(2022, 10, 3),
                    date_cert_denied=None,
                )
            ],
        )
        corpus.upsert_rows(conn, [_row(case_id="ca9/1")])  # default: no cert dates
        fetched = corpus.get_row(conn, "scotus/1")
        default = corpus.get_row(conn, "ca9/1")
    assert fetched is not None
    assert fetched.date_cert_granted == date(2022, 10, 3)
    assert fetched.date_cert_denied is None
    assert default is not None
    assert default.date_cert_granted is None and default.date_cert_denied is None


def test_from_record_tolerates_record_without_cert_date_columns() -> None:
    """A ranged read of a remote blob packed before the cert-date columns existed."""
    record = corpus._to_record(_row())
    del record["date_cert_granted"]
    del record["date_cert_denied"]
    row = corpus._from_record(record)  # a plain dict raises KeyError like the ranged Row
    assert row.date_cert_granted is None and row.date_cert_denied is None
    assert row == _row()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("21-35466", "21-35466"),
        ("  21-35466 ", "21-35466"),
        ("No. 21-35466", "21-35466"),
        ("no. 21-35466", "21-35466"),
        ("21-35466, 21-35467", "21-35466,21-35467"),  # consolidated: kept distinct
        ("01" + chr(0x2013) + "7700", "01-7700"),  # en-dash folded to a hyphen
        ("No. 01" + chr(0x2013) + "7700.", "01-7700."),  # dominant historical form + label
        ("01" + chr(0x2014) + "7700", "01-7700"),  # em-dash folded too
        ("", None),
        ("   ", None),
        (None, None),
    ],
)
def test_normalize_docket_number(raw: str | None, expected: str | None) -> None:
    assert corpus.normalize_docket_number(raw) == expected


def test_normalize_predict_eligible_converges_to_the_court_predicate(tmp_path: Path) -> None:
    # Rows latched under an earlier, broader rule (a CoA docket flagged eligible)
    # converge to the scope predicate; a mislabeled SCOTUS row converges too.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(case_id="ca9/55", court="ca9", predict_eligible=True),  # stale broad latch
                _row(case_id="scotus/1", court="scotus", predict_eligible=True),  # already right
                _row(case_id="ca1/2", court="ca1"),  # already right
            ],
        )
        # A raw column write simulating a pre-predicate row the upsert latch kept.
        conn.execute("UPDATE cases SET predict_eligible = 0 WHERE case_id = 'scotus/1'")
        changed = corpus.normalize_predict_eligible(conn)
        assert changed == 2  # the stale CoA latch cleared, the SCOTUS row set
        assert corpus.normalize_predict_eligible(conn) == 0  # idempotent
        coa = corpus.get_row(conn, "ca9/55")
        scotus = corpus.get_row(conn, "scotus/1")
    assert coa is not None and coa.predict_eligible is False
    assert scotus is not None and scotus.predict_eligible is True


def test_is_historical_mandatory_detects_bare_scotus_docket() -> None:
    # A pre-1925 mandatory-jurisdiction matter: the snapshot is sparse
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


def test_is_historical_mandatory_detects_labeled_bare_docket() -> None:
    # "No. 123" is a bare sequential number behind a label; normalization
    # strips the label so it reads as historical-mandatory like a raw "123" would.
    row = corpus.CorpusRow(case_id="scotus/12", court="scotus", docket_number="No. 123")
    assert corpus.is_historical_mandatory(row) is True


def test_is_historical_mandatory_only_applies_to_scotus() -> None:
    # The regime is a Supreme Court concept; a bare-numbered lower-court docket is
    # not swept up (and the scope gate only weighs SCOTUS dockets anyway).
    row = corpus.CorpusRow(case_id="ca9/801", court="ca9", docket_number="801")
    assert corpus.is_historical_mandatory(row) is False


def test_is_stale_unresolvable_detects_old_open_scotus_petition() -> None:
    # A modern-format docket from an old Term ("93-7515" -> OT1993),
    # still open in the corpus (no disposition, no decision date), is unresolvable.
    row = corpus.CorpusRow(case_id="scotus/1004289", court="scotus", docket_number="93-7515")
    assert corpus.is_stale_unresolvable(row) is True


def test_is_stale_unresolvable_detects_labeled_old_petition() -> None:
    # The dominant historical format carries a `No.` label that the raw
    # parser missed; normalization makes "No. 01-7700" read as OT2001 -> stale.
    row = corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="No. 01-7700")
    assert corpus.is_stale_unresolvable(row) is True


def test_is_stale_unresolvable_detects_en_dash_old_petition() -> None:
    # The same old cert docket behind a typographic en-dash now folds to a
    # hyphen and reads as OT1993 -> stale, instead of falling through unparsed.
    docket = "No. 93" + chr(0x2013) + "7515."
    row = corpus.CorpusRow(case_id="scotus/1004289", court="scotus", docket_number=docket)
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


def test_is_published_opinion_unresolvable_detects_opinion_only_disposition() -> None:
    # The observed upstream shape — a still-open SCOTUS docket
    # (no disposition, no decision date) whose only outcome signal is a linked published
    # opinion (a reporter citation). The disposition lives in the opinion text, not a
    # structured field, so the cert model cannot score it. Each recoverable signal
    # (citation, citation_count, opinion_text) is sufficient on its own.
    by_citation = corpus.CorpusRow(
        case_id="scotus/1000512", court="scotus", docket_number="", citations=["121 U.S. 183"]
    )
    by_count = corpus.CorpusRow(case_id="scotus/1002339", court="scotus", citation_count=3)
    by_text = corpus.CorpusRow(case_id="scotus/1003943", court="scotus", opinion_text="Affirmed.")
    assert corpus.is_published_opinion_unresolvable(by_citation) is True
    assert corpus.is_published_opinion_unresolvable(by_count) is True
    assert corpus.is_published_opinion_unresolvable(by_text) is True


def test_is_published_opinion_unresolvable_keeps_live_pending_petition() -> None:
    # Safe by construction: a pending cert petition has no published opinion yet (no
    # citation, no opinion text), so it is never dropped — even from an old-looking Term.
    pending = corpus.CorpusRow(case_id="scotus/9", court="scotus", docket_number="24-101")
    assert corpus.is_published_opinion_unresolvable(pending) is False


def test_is_published_opinion_unresolvable_keeps_resolved_or_dated_or_non_scotus() -> None:
    # Only while still open (no disposition and no decision date), and SCOTUS-only. A
    # resolved case carries ground truth to score; a dated one is the reconcile path.
    resolved = corpus.CorpusRow(
        case_id="scotus/10", court="scotus", disposition=Disposition.denied, citations=["1 U.S. 1"]
    )
    dated = corpus.CorpusRow(
        case_id="scotus/11", court="scotus", date_decided=date(2002, 1, 7), citation_count=2
    )
    lower = corpus.CorpusRow(case_id="ca9/12", court="ca9", citations=["1 F.3d 1"])
    assert corpus.is_published_opinion_unresolvable(resolved) is False
    assert corpus.is_published_opinion_unresolvable(dated) is False
    assert corpus.is_published_opinion_unresolvable(lower) is False


def test_is_non_cert_scotus_form_detects_applications_and_original_jurisdiction() -> None:
    # A stay/emergency application ("22A123", older "A-9999") and an
    # original-jurisdiction case — numeric "22O141" or the spelled-out "No. 155, Orig."
    # / "155, Original." text form — are not discretionary cert, so the
    # evt-petition-disposition model does not fit them; excluded by docket format.
    non_cert = (
        "22A123",
        "24A99",
        "A-9999",
        "No. A-999",
        "No. 22A99.",
        "22O141",
        "No. 155, Orig.",
        "155, Original.",
        "Orig. 155",
        # Miscellaneous forms: the modern motions docket ("22M75", "No. 03M77."),
        # its hyphenated spelling ("No. M-62", en-dash variant), and the pre-1971
        # separate docket's text label ("No. 33, Misc.").
        "22M75",
        "No. 03M77.",
        "No. M-62",
        "M" + chr(0x2013) + "371",
        "No. 33, Misc.",
        "33, Misc",
        # Trailing-letter historical spellings: a bare number followed by the
        # term letter, the pre-unification way the separate dockets were written
        # ("515 M" normalizes to "515M"). The parenthetical-companion tolerance
        # the sibling forms share applies here too.
        "515 M",
        "133M",
        "No. 979 A.",
        "515A",
        "141 O",
        "515O",
        "No. 515 M.",
        "515M (98-1368)",
        # A trailing parenthetical companion — a related docket or a Term
        # annotation — does not defeat the format match.
        "No. A-706 (98-1368)",
        "No. A-241 (O. T. 1995)",
        "01A753 (01-1632)",
    )
    for number in non_cert:
        row = corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number=number)
        assert corpus.is_non_cert_scotus_form(row) is True, number


def test_substantive_application_is_in_predict_scope() -> None:
    # The interim predict scope: an application whose latched ask reads
    # substantive (a stay, an injunction, a vacatur) is spared by the form
    # rule and by the whole row-rule chain — the one letter-form slice any
    # predict path targets.
    substantive = corpus.CorpusRow(
        case_id="scotus/9525000001",
        court="scotus",
        docket_number="25A1",
        application_kind="substantive",
    )
    assert corpus.is_non_cert_scotus_form(substantive) is False
    assert corpus.out_of_scope_reason(substantive) is None


def test_non_substantive_applications_stay_out_of_scope() -> None:
    # An extension is single-Justice routine, an unknown ask is a parser gap,
    # and a never-parsed row (a historical spelling the live channel cannot
    # address, or a REST-ingested application) carries no reading at all —
    # every one of them stays excluded; only the substantive reading spares.
    for kind in ("extension", "unknown", None):
        row = corpus.CorpusRow(
            case_id="scotus/9525000002",
            court="scotus",
            docket_number="25A2",
            application_kind=kind,
        )
        assert corpus.is_non_cert_scotus_form(row) is True, kind
        assert corpus.out_of_scope_reason(row) is not None, kind
    # The spare is application-only: a substantive-looking kind on an
    # original-jurisdiction or miscellaneous docket changes nothing.
    for number in ("22O141", "22M75"):
        other_form = corpus.CorpusRow(
            case_id="scotus/10",
            court="scotus",
            docket_number=number,
            application_kind="substantive",
        )
        assert corpus.is_non_cert_scotus_form(other_form) is True, number


def test_is_non_cert_scotus_form_keeps_cert_dockets_and_non_scotus() -> None:
    # A modern cert docket carries a hyphen, not a term letter, so it is never caught;
    # a bare or blank number falls to the other predicates; the rule is SCOTUS-only.
    cert = corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-101")
    labeled_cert = corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="No. 93-7515")
    bare = corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="801")
    blank = corpus.CorpusRow(case_id="scotus/5", court="scotus", docket_number="")
    lower = corpus.CorpusRow(case_id="ca9/6", court="ca9", docket_number="22A123")
    # A cert docket noting an application *companion* in the parenthetical is
    # still the cert docket — the letter form must match before the parenthetical.
    cert_with_companion = corpus.CorpusRow(
        case_id="scotus/7", court="scotus", docket_number="No. 09-9000 (09A743)"
    )
    # A hyphenated number ending in a letter is not the trailing-letter misc
    # form (the alternative requires a bare number with no hyphen).
    hyphenated_letter = corpus.CorpusRow(
        case_id="scotus/8", court="scotus", docket_number="22-451A"
    )
    # A consolidated trailing-letter string keeps its comma, so the single-docket
    # predicate refuses it (the end anchor never reaches a lone trailing letter);
    # is_consolidated_out_of_scope owns it by splitting the members.
    consolidated = corpus.CorpusRow(case_id="scotus/9", court="scotus", docket_number="515M, 516M")
    assert corpus.is_non_cert_scotus_form(cert) is False
    assert corpus.is_non_cert_scotus_form(labeled_cert) is False
    assert corpus.is_non_cert_scotus_form(bare) is False
    assert corpus.is_non_cert_scotus_form(blank) is False
    assert corpus.is_non_cert_scotus_form(lower) is False
    assert corpus.is_non_cert_scotus_form(cert_with_companion) is False
    assert corpus.is_non_cert_scotus_form(hyphenated_letter) is False
    assert corpus.is_non_cert_scotus_form(consolidated) is False
    assert corpus.is_consolidated_out_of_scope(consolidated) is True


def test_is_disbarment_docket_matches_both_spellings_while_open() -> None:
    # The disbarment (attorney-discipline) docket: the plain "D-####" form (label,
    # dash-variant, and trailing-period tolerant) and the Term-prefixed "##D####"
    # spelling, whose sequence numbers continue the same D series.
    disbarment = (
        "No. D-2464",
        "D-2464",
        "D2464",
        "D" + chr(0x2013) + "2464",  # en-dash variant folds to a hyphen
        "No. D-100.",
        "16D2924",
        "16D02977",
        "25D03158",
        "2464 D",  # trailing-letter historical spelling, like the sibling forms
    )
    for number in disbarment:
        row = corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number=number)
        assert corpus.is_disbarment_docket(row) is True, number


def test_is_disbarment_docket_keeps_cert_resolved_and_non_scotus() -> None:
    # Never a cert form, a bare/blank number, or another court's docket.
    cert = corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-101")
    labeled_cert = corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="No. 93-7515")
    bare = corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="801")
    blank = corpus.CorpusRow(case_id="scotus/5", court="scotus", docket_number="")
    lower = corpus.CorpusRow(case_id="ca9/6", court="ca9", docket_number="D-2464")
    assert corpus.is_disbarment_docket(cert) is False
    assert corpus.is_disbarment_docket(labeled_cert) is False
    assert corpus.is_disbarment_docket(bare) is False
    assert corpus.is_disbarment_docket(blank) is False
    assert corpus.is_disbarment_docket(lower) is False
    # Only while still open: a resolved or dated row is never this rule's business.
    resolved = corpus.CorpusRow(
        case_id="scotus/7",
        court="scotus",
        docket_number="No. D-2464",
        disposition=Disposition.denied,
    )
    dated = corpus.CorpusRow(
        case_id="scotus/8",
        court="scotus",
        docket_number="16D2924",
        date_decided=date(2017, 6, 1),
    )
    assert corpus.is_disbarment_docket(resolved) is False
    assert corpus.is_disbarment_docket(dated) is False


def test_is_disbarment_docket_carries_its_own_reason() -> None:
    row = corpus.CorpusRow(case_id="scotus/9", court="scotus", docket_number="No. D-2464")
    assert corpus.out_of_scope_reason(row) == (
        "SCOTUS disbarment docket — attorney discipline, not discretionary cert"
    )


def test_scotus_term_year_parses_two_digit_term_with_pivot() -> None:
    assert corpus.scotus_term_year("01-7700") == 2001
    assert corpus.scotus_term_year("93-7515") == 1993
    assert corpus.scotus_term_year("24-101") == 2024
    # Mid-century year-prefixed dockets are 19xx, never impossible future Terms.
    assert corpus.scotus_term_year("68-123") == 1968
    assert corpus.scotus_term_year("42-15") == 1942
    # The pivot's boundary: 29 is the last 20xx prefix, 30 the first 19xx.
    assert corpus.scotus_term_year("29-100") == 2029
    assert corpus.scotus_term_year("30-100") == 1930
    assert corpus.scotus_term_year("801") is None
    assert corpus.scotus_term_year("22A123") is None
    # The `No.` label (the dominant historical format) is normalized away.
    assert corpus.scotus_term_year("No. 01-7700") == 2001
    assert corpus.scotus_term_year("No. 93-7515") == 1993
    # A typographic en-dash is folded, so the Term parses like a hyphen.
    assert corpus.scotus_term_year("01" + chr(0x2013) + "7700") == 2001
    assert corpus.scotus_term_year("No. 93" + chr(0x2013) + "7515.") == 1993


def test_scotus_application_term_year_parses_the_strict_a_form_only() -> None:
    # The interim docket's Term key, under the same century pivot as
    # `scotus_term_year`; only the live channel's addressable `YYAnnn` form
    # parses — historical spellings and cert-form numbers fall through.
    assert corpus.scotus_application_term_year("24A1099") == 2024
    assert corpus.scotus_application_term_year("29A1") == 2029
    assert corpus.scotus_application_term_year("30A1") == 1930
    assert corpus.scotus_application_term_year("A-363") is None
    assert corpus.scotus_application_term_year("22-451") is None
    assert corpus.scotus_application_term_year("22O141") is None


def test_is_date_inconsistent_flags_decided_before_filed() -> None:
    # Decided before filed — court-agnostic, excluded from prediction.
    bad = corpus.CorpusRow(
        case_id="ca1/4490126",
        court="ca1",
        date_filed=date(2016, 6, 17),
        date_decided=date(2014, 1, 29),
    )
    ok = corpus.CorpusRow(
        case_id="ca1/2", court="ca1", date_filed=date(2014, 1, 1), date_decided=date(2016, 1, 1)
    )
    open_case = corpus.CorpusRow(case_id="ca1/3", court="ca1", date_filed=date(2016, 6, 17))
    assert corpus.is_date_inconsistent(bad) is True
    assert corpus.is_date_inconsistent(ok) is False  # normal ordering
    assert corpus.is_date_inconsistent(open_case) is False  # undecided -> not inconsistent
    assert corpus.out_of_scope_reason(bad) == (
        "internally inconsistent dates — decided before filed"
    )


def test_consolidated_docket_members_splits_and_normalizes() -> None:
    # Per-member labels ("No." / the plural "Nos.") are stripped after the split.
    assert corpus.consolidated_docket_members("No. 155; No. 156") == ["155", "156"]
    assert corpus.consolidated_docket_members("Nos. 522, 523, 524") == ["522", "523", "524"]
    assert corpus.consolidated_docket_members("Nos. 155 and 156") == ["155", "156"]
    assert corpus.consolidated_docket_members("93-7515 & 94-100") == ["93-7515", "94-100"]
    # Not consolidated: no separator, or fewer than two members survive.
    assert corpus.consolidated_docket_members("22-451") is None
    assert corpus.consolidated_docket_members("No. 155, ") is None
    assert corpus.consolidated_docket_members("") is None


def _consolidated(number: str, **kw: object) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {"case_id": "scotus/9", "court": "scotus", "docket_number": number, **kw}
    )


def test_consolidated_out_of_scope_needs_every_member_to_agree() -> None:
    # All bare-sequential members -> the pre-1925 mandatory regime.
    assert corpus.is_consolidated_out_of_scope(_consolidated("No. 155; No. 156")) is True
    assert corpus.is_consolidated_out_of_scope(_consolidated("Nos. 522, 523, 524")) is True
    # All stale Term years on a still-open row.
    assert corpus.is_consolidated_out_of_scope(_consolidated("93-7515; 94-100")) is True
    # All non-cert letter forms: consolidated miscellaneous and application pairs,
    # including a member carrying a parenthetical companion.
    assert corpus.is_consolidated_out_of_scope(_consolidated("No. 99M81; No. 99M82")) is True
    assert corpus.is_consolidated_out_of_scope(_consolidated("A-363; A-366")) is True
    assert corpus.is_consolidated_out_of_scope(_consolidated("A-174 (97-369); A-175")) is True
    # Disagreement (bare + Term-form, or non-cert + live cert) stays in scope,
    # visible in the audit.
    assert corpus.is_consolidated_out_of_scope(_consolidated("801; 93-7515")) is False
    assert corpus.is_consolidated_out_of_scope(_consolidated("22A123; 24-101")) is False
    # Recent consolidated Terms are live petitions: neither branch matches.
    assert corpus.is_consolidated_out_of_scope(_consolidated("24-101; 24-102")) is False
    # A resolved row cannot be stale-unresolvable, whatever its members' Terms.
    resolved = _consolidated(
        "93-7515; 94-100", disposition=Disposition.denied, date_decided=date(1994, 6, 1)
    )
    assert corpus.is_consolidated_out_of_scope(resolved) is False
    # Single-docket rows and other courts are never this rule's business.
    assert corpus.is_consolidated_out_of_scope(_consolidated("801")) is False
    ca9 = corpus.CorpusRow(case_id="ca9/9", court="ca9", docket_number="155; 156")
    assert corpus.is_consolidated_out_of_scope(ca9) is False


def test_consolidated_out_of_scope_carries_its_own_reason() -> None:
    assert corpus.out_of_scope_reason(_consolidated("No. 155; No. 156")) == (
        "consolidated docket whose members all classify out of scope"
    )


def test_case_era_prefers_term_year_then_dates() -> None:
    # SCOTUS: the parsed October-Term year wins over any date.
    scotus = corpus.CorpusRow(
        case_id="scotus/1", court="scotus", docket_number="93-7515", date_filed=date(2001, 1, 1)
    )
    assert corpus.case_era(scotus) == "1990s"
    # Non-SCOTUS (and unparseable SCOTUS): date_filed, then date_decided.
    filed = corpus.CorpusRow(case_id="ca9/1", court="ca9", date_filed=date(2022, 4, 11))
    decided = corpus.CorpusRow(case_id="scotus/2", court="scotus", date_decided=date(1873, 3, 1))
    bare = corpus.CorpusRow(case_id="scotus/3", court="scotus")
    assert corpus.case_era(filed) == "2020s"
    assert corpus.case_era(decided) == "1870s"
    assert corpus.case_era(bare) is None


def test_era_tokens_span_the_judiciary_and_hold_what_case_era_mints() -> None:
    # The `--era` vocabulary the CLI offers a caller that guessed one. It is
    # derived from case_era's own arithmetic rather than typed out again, so
    # the tokens offered are the ones rows can actually carry: a decade the
    # corpus could never hold must not be offered, and one it can must not be
    # refused.
    tokens = corpus.era_tokens(date(2026, 8, 26))
    assert tokens[0] == "1780s" and tokens[-1] == "2020s"
    old = corpus.CorpusRow(case_id="scotus/2", court="scotus", date_decided=date(1873, 3, 1))
    assert corpus.case_era(old) in tokens
    # It follows the clock, so the decade a cell is predicting in is offered.
    assert corpus.era_tokens(date(2031, 1, 1))[-1] == "2030s"


def test_case_year_prefers_term_year_then_dates() -> None:
    # The year behind case_era and the decided_before cutoff, same signal order.
    scotus = corpus.CorpusRow(
        case_id="scotus/1", court="scotus", docket_number="93-7515", date_filed=date(2001, 1, 1)
    )
    filed = corpus.CorpusRow(case_id="ca9/1", court="ca9", date_filed=date(2022, 4, 11))
    decided = corpus.CorpusRow(case_id="scotus/2", court="scotus", date_decided=date(1873, 3, 1))
    bare = corpus.CorpusRow(case_id="scotus/3", court="scotus")
    assert corpus.case_year(scotus) == 1993
    assert corpus.case_year(filed) == 2022
    assert corpus.case_year(decided) == 1873
    assert corpus.case_year(bare) is None
    # A cert-dated SCOTUS row without a parseable Term or filing date anchors to
    # the petition-stage decision year, ahead of the merits termination.
    cert_dated = corpus.CorpusRow(
        case_id="scotus/4",
        court="scotus",
        date_cert_granted=date(2022, 10, 3),
        date_decided=date(2023, 6, 30),
    )
    assert corpus.case_year(cert_dated) == 2022


def test_resolution_date_prefers_cert_stage_for_scotus() -> None:
    granted = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        date_cert_granted=date(2022, 10, 3),
        date_decided=date(2023, 6, 30),  # merits termination, months after the grant
    )
    denied = corpus.CorpusRow(case_id="scotus/2", court="scotus", date_cert_denied=date(2023, 1, 9))
    terminated = corpus.CorpusRow(
        case_id="scotus/3", court="scotus", date_decided=date(2023, 6, 30)
    )
    circuit = corpus.CorpusRow(
        case_id="ca9/1",
        court="ca9",
        date_cert_granted=date(2022, 10, 3),  # defensive: never read off SCOTUS
        date_decided=date(2022, 6, 15),
    )
    assert corpus.resolution_date(granted) == date(2022, 10, 3)
    assert corpus.resolution_date(denied) == date(2023, 1, 9)
    assert corpus.resolution_date(terminated) == date(2023, 6, 30)
    assert corpus.resolution_date(circuit) == date(2022, 6, 15)
    assert corpus.resolution_date(corpus.CorpusRow(case_id="scotus/5", court="scotus")) is None


def test_recency_key_orders_by_petition_stage_resolution() -> None:
    # A granted petition ranks by when cert was granted, not the later merits
    # termination — so it sorts between two denials dated around the grant.
    granted = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        date_cert_granted=date(2022, 10, 3),
        date_decided=date(2023, 6, 30),
    )
    newer_denial = corpus.CorpusRow(
        case_id="scotus/2", court="scotus", date_cert_denied=date(2023, 1, 9)
    )
    older_denial = corpus.CorpusRow(
        case_id="scotus/3", court="scotus", date_cert_denied=date(2022, 6, 27)
    )
    undated = corpus.CorpusRow(case_id="scotus/4", court="scotus")
    ordered = sorted([granted, older_denial, undated, newer_denial], key=corpus.recency_key)
    assert [r.case_id for r in ordered] == ["scotus/2", "scotus/1", "scotus/3", "scotus/4"]


def test_cert_dates_never_trip_date_inconsistency() -> None:
    # The date-order exclusion reads only filing vs decision; a petition-stage
    # cert date out of order with the filing date is kept as faithful upstream data.
    row = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        date_filed=date(2022, 5, 1),
        date_cert_denied=date(2021, 1, 1),
    )
    assert corpus.is_date_inconsistent(row) is False


def test_is_modern_cert_matches_term_prefixed_scotus_only() -> None:
    modern = corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="22-451")
    labeled = corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="No. 01-7700")
    application = corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="22A123")
    bare = corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="801")
    coa = corpus.CorpusRow(case_id="ca9/5", court="ca9", docket_number="22-15001")
    assert corpus.is_modern_cert(modern) is True
    assert corpus.is_modern_cert(labeled) is True
    assert corpus.is_modern_cert(application) is False
    assert corpus.is_modern_cert(bare) is False
    assert corpus.is_modern_cert(coa) is False


def test_retrieve_priors_era_filter(tmp_path: Path) -> None:
    # Era is derived (Term year / dates), so the filter applies in Python over
    # the SQL-narrowed candidates — historical cases retrieve their own period.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(case_id="scotus/1", court="scotus", docket_number="93-7515"),
                _row(case_id="scotus/2", court="scotus", docket_number="22-451"),
            ],
        )
        priors = corpus.retrieve_priors(
            conn, corpus.PriorQuery(court="scotus", era="1990s"), limit=10
        )
    assert [r.case_id for r in priors] == ["scotus/1"]


def test_retrieve_priors_decided_before_is_exclusive_and_conservative(tmp_path: Path) -> None:
    # The back-test replay clock: only priors that provably precede the cutoff
    # qualify — the cutoff year itself and rows with no derivable year never do.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(case_id="scotus/1", court="scotus", docket_number="93-7515"),  # 1993
                _row(case_id="scotus/2", court="scotus", docket_number="98-100"),  # the cutoff year
                _row(case_id="scotus/3", court="scotus", docket_number="22-451"),  # later
                _row(  # no Term, no dates: year underivable -> excluded under a cutoff
                    case_id="scotus/4",
                    court="scotus",
                    docket_number="801",
                    date_filed=None,
                    date_decided=None,
                ),
            ],
        )
        masked = corpus.retrieve_priors(
            conn, corpus.PriorQuery(court="scotus", decided_before=1998), limit=10
        )
        unmasked = corpus.retrieve_priors(conn, corpus.PriorQuery(court="scotus"), limit=10)
    assert [r.case_id for r in masked] == ["scotus/1"]
    assert len(unmasked) == 4


def test_retrieve_priors_decided_before_strips_post_clock_merits(tmp_path: Path) -> None:
    # The merits judgment on an admitted row is a later fact than the row's own
    # year: a Term-1993 petition qualifies under a 1998 clock while its
    # judgment may have issued afterwards. The pair survives the mask only when
    # `merits_decided` provably precedes the cutoff too; an undated judgment
    # fails closed. Unmasked (forward) retrieval keeps the columns whole.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(  # judgment provably pre-clock: survives the mask
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="93-7515",
                    merits_judgment="reversed",
                    merits_decided=date(1994, 6, 1),
                ),
                _row(  # judgment postdates the clock: stripped
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="93-7516",
                    merits_judgment="affirmed",
                    merits_decided=date(1999, 6, 1),
                ),
                _row(  # undated judgment cannot prove precedence: stripped
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="93-7517",
                    merits_judgment="vacated",
                    merits_decided=None,
                ),
            ],
        )
        masked = {
            r.case_id: r
            for r in corpus.retrieve_priors(
                conn, corpus.PriorQuery(court="scotus", decided_before=1998), limit=10
            )
        }
        unmasked = {
            r.case_id: r
            for r in corpus.retrieve_priors(conn, corpus.PriorQuery(court="scotus"), limit=10)
        }
    assert set(masked) == {"scotus/1", "scotus/2", "scotus/3"}
    assert masked["scotus/1"].merits_judgment == "reversed"
    assert masked["scotus/1"].merits_decided == date(1994, 6, 1)
    assert masked["scotus/2"].merits_judgment is None
    assert masked["scotus/2"].merits_decided is None
    assert masked["scotus/3"].merits_judgment is None
    assert unmasked["scotus/2"].merits_judgment == "affirmed"
    assert unmasked["scotus/3"].merits_judgment == "vacated"


def test_retrieve_priors_decided_before_always_strips_a_termination(tmp_path: Path) -> None:
    # `merits_terminated` carries no date, so nothing in it can prove it came
    # before the clock — and what it records (the proceeding ended) is exactly
    # the post-clock fact the mask exists to hide. Fail closed: strip it
    # whenever the mask is active, keep it on unmasked retrieval.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(  # a pre-clock judgment beside it: the pair still survives
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="93-7515",
                    merits_judgment="reversed",
                    merits_decided=date(1994, 6, 1),
                ),
                _row(case_id="scotus/2", court="scotus", docket_number="93-7516"),
            ],
        )
        for case_id in ("scotus/1", "scotus/2"):
            corpus.set_merits_termination(conn, case_id, MeritsTermination.judgment_issued)
        masked = {
            r.case_id: r
            for r in corpus.retrieve_priors(
                conn, corpus.PriorQuery(court="scotus", decided_before=1998), limit=10
            )
        }
        unmasked = {
            r.case_id: r
            for r in corpus.retrieve_priors(conn, corpus.PriorQuery(court="scotus"), limit=10)
        }
    assert masked["scotus/1"].merits_terminated is None
    assert masked["scotus/1"].merits_judgment == "reversed"  # dated, provably pre-clock
    assert masked["scotus/2"].merits_terminated is None
    assert unmasked["scotus/2"].merits_terminated == MeritsTermination.judgment_issued.value


def _application_slice() -> list[corpus.CorpusRow]:
    """The pollution in miniature: two non-cert applications above two cert-surface rows.

    The extension and the unread-ask application resolve within days of filing,
    so the recency ranking puts them first — which is exactly why they have to
    be screened rather than merely deprioritized.
    """
    return [
        _row(  # a time extension: `granted` by one Justice, not a cert vote
            case_id="scotus/1",
            court="scotus",
            docket_number="25A123",
            application_kind="extension",
            date_decided=date(2026, 7, 1),
        ),
        _row(  # ask never read: a coverage gap, never a prior
            case_id="scotus/2",
            court="scotus",
            docket_number="25A150",
            application_kind=None,
            date_decided=date(2026, 6, 15),
        ),
        _row(  # a stay: the interim predict scope, a real prior for a real event
            case_id="scotus/3",
            court="scotus",
            docket_number="25A99",
            application_kind="substantive",
            date_decided=date(2026, 6, 1),
        ),
        _row(case_id="scotus/4", court="scotus", docket_number="24-451"),
    ]


def test_retrieve_priors_screens_non_cert_applications(tmp_path: Path) -> None:
    # The cert surface is the default population: an extension grant and an
    # unread-ask application are dropped, the substantive stay and the cert
    # petition stay. `exclude_non_cert=False` retrieves the whole letter-form
    # docket back. Asserted on both retrieval paths — the overlap-free fast path
    # and (via a judge filter) the scored path — since each screens separately.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _application_slice())
        screened = corpus.retrieve_priors(conn, corpus.PriorQuery(court="scotus"), limit=10)
        overlap = corpus.retrieve_priors(
            conn, corpus.PriorQuery(court="scotus", judges=["smith"]), limit=10
        )
        included = corpus.retrieve_priors(
            conn, corpus.PriorQuery(court="scotus", exclude_non_cert=False), limit=10
        )
    assert [r.case_id for r in screened] == ["scotus/3", "scotus/4"]
    assert [r.case_id for r in overlap] == ["scotus/3", "scotus/4"]
    assert [r.case_id for r in included] == ["scotus/1", "scotus/2", "scotus/3", "scotus/4"]


def test_retrieve_priors_screen_does_not_spend_result_slots(tmp_path: Path) -> None:
    # The screen runs after the SQL, so the LIMIT applies to what survives it: a
    # page of 2 comes back full even though the two highest-ranked rows are
    # screened out. (A pushed-down LIMIT would have returned nothing.)
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _application_slice())
        page = corpus.retrieve_priors(conn, corpus.PriorQuery(court="scotus"), limit=2)
        # Court-less too: that shape has no index-served ordering, so it ranks in
        # Python — the other place the limit is applied.
        anywhere = corpus.retrieve_priors(conn, corpus.PriorQuery(), limit=2)
    assert [r.case_id for r in page] == ["scotus/3", "scotus/4"]
    assert [r.case_id for r in anywhere] == ["scotus/3", "scotus/4"]


def test_retrieve_priors_screen_is_scotus_only(tmp_path: Path) -> None:
    # The letter forms are a SCOTUS spelling; a circuit docket that happens to
    # look like one is never screened.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/1", docket_number="25A123")])
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(court="ca9"), limit=10)
    assert [r.case_id for r in priors] == ["ca9/1"]


def _bare_row(case_id: str = "scotus/1038466", **kw: object) -> corpus.CorpusRow:
    """A bulk-import shell: SCOTUS with every predicate-keyed row field empty."""
    return corpus.CorpusRow.model_validate({"case_id": case_id, "court": "scotus", **kw})


def test_is_bare_import_profile_matches_only_empty_scotus_rows() -> None:
    # The profile is every field the sibling predicates key on, empty.
    assert corpus.is_bare_import_profile(_bare_row()) is True
    # A whitespace-only docket number normalizes to empty and still counts.
    assert corpus.is_bare_import_profile(_bare_row(docket_number="  ")) is True
    # Any real field breaks the profile: it is no longer a bare shell.
    assert corpus.is_bare_import_profile(_bare_row(docket_number="24-101")) is False
    assert corpus.is_bare_import_profile(_bare_row(date_filed=date(1946, 1, 2))) is False
    assert corpus.is_bare_import_profile(_bare_row(citation_count=3)) is False
    assert corpus.is_bare_import_profile(_bare_row(opinion_text="held...")) is False
    assert corpus.is_bare_import_profile(_bare_row(disposition=Disposition.denied)) is False
    # Non-SCOTUS rows never match; the class is a SCOTUS bulk-import artifact.
    assert corpus.is_bare_import_profile(_bare_row(court="ca9")) is False


def test_is_bare_opinion_import_needs_the_cluster_link() -> None:
    # The bare profile alone is not an exclusion signal — the linked opinion
    # cluster is what marks the docket as a decided historical matter.
    row = _bare_row()
    linked = {"id": 1038466, "clusters": ["https://example/clusters/88494/"]}
    unlinked = {"id": 1038466, "clusters": []}
    assert corpus.is_bare_opinion_import(row, linked) is True
    assert corpus.is_bare_opinion_import(row, unlinked) is False
    assert corpus.is_bare_opinion_import(row, None) is False
    assert corpus.is_bare_opinion_import(_bare_row(docket_number="24-101"), linked) is False


def test_out_of_scope_reason_full_adds_the_snapshot_aware_rule(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_bare_row(), _bare_row(case_id="scotus/2")])
        corpus.upsert_snapshot(
            conn,
            "scotus/1038466",
            date(2026, 7, 2),
            {"id": 1038466, "clusters": ["https://example/clusters/88494/"]},
        )
        # scotus/2 has no snapshot at all — the bare profile alone must not exclude.
        linked = corpus.get_row(conn, "scotus/1038466")
        bare_only = corpus.get_row(conn, "scotus/2")
        assert linked is not None and bare_only is not None
        assert corpus.out_of_scope_reason_full(conn, linked) == (corpus.BARE_OPINION_IMPORT_REASON)
        assert corpus.out_of_scope_reason_full(conn, bare_only) is None
        # Row rules still come first and short-circuit the snapshot fetch.
        historical = corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="801")
        assert corpus.out_of_scope_reason_full(conn, historical) == (
            "pre-1925 mandatory-jurisdiction matter"
        )


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


def _recency_fixture_rows() -> list[corpus.CorpusRow]:
    """Rows exercising every branch of the recency ordering.

    SCOTUS rows keyed on the cert date over the merits termination, a
    denied-date fallback, a decided-only fallback, an exact date tie broken by
    case_id, an undated row (sorts last), and a non-SCOTUS court keyed on
    date_decided.
    """
    return [
        _row(  # cert granted 2024 — the cert date must outrank the 2026 termination
            case_id="scotus/b-grant",
            court="scotus",
            docket_number="23-100",
            date_cert_granted=date(2024, 3, 1),
            date_decided=date(2026, 1, 2),
        ),
        _row(  # denied 2025 — newest resolution, ranks first
            case_id="scotus/a-deny",
            court="scotus",
            docket_number="24-200",
            date_cert_granted=None,
            date_cert_denied=date(2025, 6, 1),
            date_decided=None,
            disposition=Disposition.denied,
        ),
        _row(  # decided-only fallback, ties scotus/b-grant on the date -> case_id order
            case_id="scotus/c-tie",
            court="scotus",
            docket_number="23-300",
            date_cert_granted=None,
            date_decided=date(2024, 3, 1),
            # A merits pair the decided_before screen must mask: the row's
            # Term qualifies under a 2024 clock, the judgment postdates it.
            merits_judgment="affirmed",
            merits_decided=date(2025, 5, 1),
        ),
        _row(  # undated but disposition-resolved: sorts after every dated row
            case_id="scotus/d-undated",
            court="scotus",
            docket_number="23-400",
            date_cert_granted=None,
            date_decided=None,
            date_filed=None,
            disposition=Disposition.denied,
        ),
        _row(case_id="ca9/x", date_decided=date(2025, 12, 31)),
    ]


def test_retrieve_priors_sql_ranking_matches_the_python_ranking(tmp_path: Path) -> None:
    """The overlap-free fast path is byte-identical to the Python ranking.

    The retrieval surface is measured, so the SQL ordering must reproduce the
    Python key exactly — cert-date precedence, the decided fallback, undated
    rows last, case_id tie-breaks — pinned two ways: against a reference sort
    on `recency_key`, and against the overlap path itself (a judges filter
    every row satisfies keeps relevance uniform, so the two paths must agree
    on bytes).
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _recency_fixture_rows())
        for query, expect in [
            (
                corpus.PriorQuery(court="scotus"),
                ["scotus/a-deny", "scotus/b-grant", "scotus/c-tie", "scotus/d-undated"],
            ),
            # Court-less: the fast path serves this shape only unscreened, so
            # the cert-surface screen comes off to keep it pinned here.
            (corpus.PriorQuery(exclude_non_cert=False), None),
            # The screened shapes take the fast path only beside a court
            # filter (the index serves the ordering there), and decided_before
            # exercises the masking branch on the stream.
            (corpus.PriorQuery(court="scotus", era="2020s"), None),
            (corpus.PriorQuery(court="scotus", decided_before=2024), None),
        ]:
            fast = corpus.retrieve_priors(conn, query, limit=10)
            if expect is not None:
                assert [r.case_id for r in fast] == expect
            # Order claim: the fast path emits the documented key's order.
            # (Membership rides the overlap cross-check below, which re-runs
            # the same query through the Python path.)
            reference = sorted(fast, key=lambda r: (corpus.recency_key(r), r.case_id))
            assert [r.model_dump(mode="json") for r in fast] == [
                r.model_dump(mode="json") for r in reference
            ]
            # The overlap path, made relevance-uniform (every fixture row
            # carries the shared default judge): identical bytes, so a row the
            # fast path wrongly dropped or mismasked cannot pass.
            overlap_query = query.model_copy(update={"judges": ["smith"]})
            slow = corpus.retrieve_priors(conn, overlap_query, limit=10)
            fast_with_judges = [r for r in fast if "smith" in r.judges]
            assert [r.model_dump(mode="json") for r in slow] == [
                r.model_dump(mode="json") for r in fast_with_judges
            ]
        # The masking branch genuinely ran: the qualifying row's post-clock
        # merits pair is stripped on the clocked query, present otherwise.
        clocked = corpus.retrieve_priors(
            conn, corpus.PriorQuery(court="scotus", decided_before=2024), limit=10
        )
        by_id = {r.case_id: r for r in clocked}
        assert "scotus/c-tie" in by_id and by_id["scotus/c-tie"].merits_judgment is None
        # The limit truncates the same ranking, not a different one — applied
        # as the screened stream is consumed rather than pushed into the SQL.
        top_two = corpus.retrieve_priors(conn, corpus.PriorQuery(court="scotus"), limit=2)
        assert [r.case_id for r in top_two] == ["scotus/a-deny", "scotus/b-grant"]


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


def test_rename_event_moves_the_row_to_the_new_identity(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    new = _event(
        event_id="evt-motion-disposition",
        kind=EventKind.motion,
        description="carried over",
        docket_entry_id=42,
    )
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(description="carried over", docket_entry_id=42)])
        corpus.rename_event(conn, "ca9/123", "evt-appeal-disposition", new)
        (event,) = corpus.events_for_case(conn, "ca9/123")
    assert event == new  # exactly one row, under the new identity


def test_rename_event_never_regresses_the_resolved_latch(tmp_path: Path) -> None:
    # The rename carries resolution as MAX(old, new): renaming a closed event
    # with a freshly-minted (resolved=False) replacement must not reopen it.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(resolved=True)])
        corpus.rename_event(
            conn,
            "ca9/123",
            "evt-appeal-disposition",
            _event(event_id="evt-motion-disposition", kind=EventKind.motion, resolved=False),
        )
        (event,) = corpus.events_for_case(conn, "ca9/123")
    assert event.event_id == "evt-motion-disposition"
    assert event.resolved is True


def test_rename_event_folds_onto_an_existing_new_row(tmp_path: Path) -> None:
    # Where the new identity already exists (a re-extraction minted it before
    # the rename ran), the rename folds onto that row instead of duplicating,
    # and the latch still takes the MAX across all three.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                _event(resolved=False),
                _event(event_id="evt-motion-disposition", kind=EventKind.motion, resolved=True),
            ],
        )
        corpus.rename_event(
            conn,
            "ca9/123",
            "evt-appeal-disposition",
            _event(event_id="evt-motion-disposition", kind=EventKind.motion, resolved=False),
        )
        (event,) = corpus.events_for_case(conn, "ca9/123")
    assert event.resolved is True


def test_rename_event_requires_the_old_row_and_a_matching_case(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event()])
        with pytest.raises(ValueError, match="no event"):
            corpus.rename_event(
                conn, "ca9/123", "evt-nonexistent", _event(event_id="evt-motion-disposition")
            )
        with pytest.raises(ValueError, match="names case"):
            corpus.rename_event(
                conn,
                "ca9/999",
                "evt-appeal-disposition",
                _event(event_id="evt-motion-disposition"),
            )
        # A same-identity call would upsert-then-delete the row — a silent
        # event delete, which the corpus deliberately has no API for.
        with pytest.raises(ValueError, match="same-identity"):
            corpus.rename_event(conn, "ca9/123", "evt-appeal-disposition", _event())
        # No failed call disturbed the stored row.
        (event,) = corpus.events_for_case(conn, "ca9/123")
    assert event.event_id == "evt-appeal-disposition"


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


# --- live-parsed signal columns and the sample-weight min-latch --------------------


def test_live_signal_columns_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    row = _row(
        case_id="scotus/1",
        court="scotus",
        docket_number="25-100",
        distribution_count=2,
        cvsg_date=date(2026, 1, 12),
        originating_court_name="Supreme Court of Nevada",
        sample_weight=10,
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        fetched = corpus.get_row(conn, "scotus/1")
    assert fetched == row


def test_live_signal_columns_survive_a_courtlistener_write(tmp_path: Path) -> None:
    # A REST enrichment carries none of the live-parsed signals; the COALESCE
    # latch must keep what the live channel stamped (same rule as the
    # conference date), while a fresh live parse still overwrites.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-100",
                    distribution_count=1,
                    cvsg_date=date(2026, 1, 12),
                    originating_court_name="Supreme Court of Nevada",
                )
            ],
        )
        corpus.upsert_rows(
            conn,
            [_row(case_id="scotus/1", court="scotus", docket_number="25-100")],
        )
        after_rest = corpus.get_row(conn, "scotus/1")
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-100",
                    distribution_count=3,
                )
            ],
        )
        after_relist = corpus.get_row(conn, "scotus/1")
    assert after_rest is not None and after_relist is not None
    assert after_rest.distribution_count == 1
    assert after_rest.cvsg_date == date(2026, 1, 12)
    assert after_rest.originating_court_name == "Supreme Court of Nevada"
    assert after_relist.distribution_count == 3  # a fresh parse still advances


def test_interim_and_merits_dates_survive_a_courtlistener_write(tmp_path: Path) -> None:
    # The dated interim/merits signals are live-parse-only, so the REST pull that
    # next rotates onto the case carries None for all three. Without the fill-in
    # latch it blanks them, leaving the max-latched `response_requested` flag
    # standing beside a NULL date — the shape an undated request takes, asserted
    # about a request that was in fact dated.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-100",
                    response_requested=True,
                    response_requested_at=date(2026, 3, 2),
                    response_filed_at=date(2026, 3, 20),
                    merits_brief_filed=date(2026, 5, 11),
                )
            ],
        )
        corpus.upsert_rows(
            conn,
            [_row(case_id="scotus/1", court="scotus", docket_number="25-100")],
        )
        after_rest = corpus.get_row(conn, "scotus/1")
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-100",
                    response_filed_at=date(2026, 3, 21),
                )
            ],
        )
        after_reparse = corpus.get_row(conn, "scotus/1")
    assert after_rest is not None and after_reparse is not None
    assert after_rest.response_requested is True
    assert after_rest.response_requested_at == date(2026, 3, 2)
    assert after_rest.response_filed_at == date(2026, 3, 20)
    assert after_rest.merits_brief_filed == date(2026, 5, 11)
    # A fresh parse still overwrites, so a corrected date reaches the store.
    assert after_reparse.response_filed_at == date(2026, 3, 21)
    assert after_reparse.response_requested_at == date(2026, 3, 2)


def test_distribution_count_never_regresses_on_a_degraded_parse(tmp_path: Path) -> None:
    # A degraded live parse (proceedings missing from the served payload) yields
    # a confident 0 — asserting "parsed, never distributed" — not NULL, so a
    # fill-in latch would let it wipe a stored count. Proceedings are
    # append-only upstream: the max-latch rejects the regression.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="scotus/1", court="scotus", distribution_count=3)])
        corpus.upsert_rows(conn, [_row(case_id="scotus/1", court="scotus", distribution_count=0)])
        stored = corpus.get_row(conn, "scotus/1")
    assert stored is not None and stored.distribution_count == 3


def test_has_opinion_survives_a_reingest_without_the_body(tmp_path: Path) -> None:
    # The presence bit is monotone (an opinion once linked is never unlinked)
    # and every writer asserts it (NOT NULL, default False), so a channel that
    # does not carry the body — a docket-only re-ingest — must not flip a
    # stored True back to False; a genuine first link still lands.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/77")])  # opinion_text set → bit True
        corpus.upsert_rows(conn, [_row(case_id="ca9/77", opinion_text=None, summary=None)])
        survived = corpus.get_row(conn, "ca9/77")
        corpus.upsert_rows(conn, [_row(case_id="ca9/78", opinion_text=None, summary=None)])
        corpus.upsert_rows(conn, [_row(case_id="ca9/78")])  # the first link still lands
        linked = corpus.get_row(conn, "ca9/78")
    assert survived is not None and survived.has_opinion is True
    assert linked is not None and linked.has_opinion is True


def test_sample_weight_min_latches_toward_certainty(tmp_path: Path) -> None:
    # Weight 1 means "included with certainty"; once known, a walker re-serve
    # of the sampled serial (weight N) must not regress it — and the other
    # order converges to the same value, so write order is immaterial.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="scotus/a", sample_weight=10)])
        corpus.upsert_rows(conn, [_row(case_id="scotus/a", sample_weight=1)])
        corpus.upsert_rows(conn, [_row(case_id="scotus/a", sample_weight=10)])
        a = corpus.get_row(conn, "scotus/a")
        corpus.upsert_rows(conn, [_row(case_id="scotus/b", sample_weight=1)])
        corpus.upsert_rows(conn, [_row(case_id="scotus/b", sample_weight=10)])
        b = corpus.get_row(conn, "scotus/b")
        # A writer with nothing to assert (None) preserves the stored weight.
        corpus.upsert_rows(conn, [_row(case_id="scotus/a", sample_weight=None)])
        a_after_none = corpus.get_row(conn, "scotus/a")
    assert a is not None and a.sample_weight == 1
    assert b is not None and b.sample_weight == 1
    assert a_after_none is not None and a_after_none.sample_weight == 1


# --- interim-application signal columns and rotation --------------------------------


def test_merits_judgment_columns_roundtrip_and_migrate(tmp_path: Path) -> None:
    # Round-trip through the normal API, and a DB created before the columns
    # existed gains them on connect with the never-parsed NULL sentinel intact.
    db = tmp_path / "corpus.db"
    row = _row(
        case_id="scotus/24001",
        court="scotus",
        docket_number="23-101",
        date_cert_granted=date(2024, 1, 12),
        merits_judgment="reversed",
        merits_decided=date(2024, 6, 27),
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        fetched = corpus.get_row(conn, "scotus/24001")
    assert fetched == row

    # A pre-change DB: the current schema minus the two merits columns.
    pre = tmp_path / "pre-change.db"
    legacy = sqlite3.connect(pre)
    merits = ("merits_judgment", "merits_decided")
    columns = ",\n".join(
        f"{name} {ddl}" for name, ddl in corpus._CASES_COLUMN_DDL.items() if name not in merits
    )
    legacy.executescript(
        f"CREATE TABLE cases ({columns});\n"
        "INSERT INTO cases (case_id, court, docket_number) VALUES "
        "('scotus/24001', 'scotus', '23-101');"
    )
    legacy.commit()
    legacy.close()
    with corpus.connect(pre) as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(cases)")}
        assert set(merits) <= cols
        migrated = corpus.get_row(conn, "scotus/24001")
    assert migrated is not None
    assert migrated.merits_judgment is None  # never parsed, not an observed absence
    assert migrated.merits_decided is None


def test_from_record_tolerates_record_without_merits_columns() -> None:
    """A ranged read of a remote blob packed before the merits columns existed."""
    record = corpus._to_record(_row())
    del record["merits_judgment"]
    del record["merits_decided"]
    del record["merits_terminated"]
    row = corpus._from_record(record)  # a plain dict raises KeyError like the ranged Row
    assert row.merits_judgment is None and row.merits_decided is None
    assert row.merits_terminated is None
    assert row == _row()


def test_merits_terminated_migrates_and_survives_ingestion(tmp_path: Path) -> None:
    # A DB written before the column gains it on connect, and the sweep's
    # finding is not a channel fact — no ingestion writer ever has one to
    # assert, so a re-ingest must keep the stored value rather than clear it.
    pre = tmp_path / "pre-change.db"
    legacy = sqlite3.connect(pre)
    columns = ",\n".join(
        f"{name} {ddl}"
        for name, ddl in corpus._CASES_COLUMN_DDL.items()
        if name != "merits_terminated"
    )
    legacy.executescript(
        f"CREATE TABLE cases ({columns});\n"
        "INSERT INTO cases (case_id, court, docket_number) VALUES "
        "('scotus/24001', 'scotus', '23-101');"
    )
    legacy.commit()
    legacy.close()
    with corpus.connect(pre) as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(cases)")}
        assert "merits_terminated" in cols
        migrated = corpus.get_row(conn, "scotus/24001")
        assert migrated is not None and migrated.merits_terminated is None
        corpus.set_merits_termination(conn, "scotus/24001", MeritsTermination.voluntary_dismissal)
        corpus.upsert_rows(conn, [_row(case_id="scotus/24001", court="scotus")])
        kept = corpus.get_row(conn, "scotus/24001")
    assert kept is not None
    assert kept.merits_terminated == MeritsTermination.voluntary_dismissal.value


def test_set_merits_judgment_stamps_and_overwrites_forward(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/24001", court="scotus")])
        corpus.set_merits_judgment(conn, "scotus/24001", Judgment.vacated, date(2024, 6, 20))
        first = corpus.get_row(conn, "scotus/24001")
        # A corrected parse self-heals forward, an undated entry stores NULL.
        corpus.set_merits_judgment(conn, "scotus/24001", Judgment.reversed, None)
        second = corpus.get_row(conn, "scotus/24001")
    assert first is not None
    assert first.merits_judgment == "vacated" and first.merits_decided == date(2024, 6, 20)
    assert second is not None
    assert second.merits_judgment == "reversed" and second.merits_decided is None


def test_interim_signal_columns_roundtrip_and_migrate(tmp_path: Path) -> None:
    # Round-trip through the normal API, and a DB created before the columns
    # existed gains them on connect with the never-parsed NULL sentinel intact.
    db = tmp_path / "corpus.db"
    row = _row(
        case_id="scotus/9500024001",
        court="scotus",
        docket_number="24A1099",
        application_kind="substantive",
        response_requested=True,
        referred_to_court=True,
        amicus_briefs=2,
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        fetched = corpus.get_row(conn, "scotus/9500024001")
    assert fetched == row

    # A pre-change DB: the current schema minus the four interim columns.
    pre = tmp_path / "pre-change.db"
    legacy = sqlite3.connect(pre)
    interim = ("application_kind", "response_requested", "referred_to_court", "amicus_briefs")
    columns = ",\n".join(
        f"{name} {ddl}" for name, ddl in corpus._CASES_COLUMN_DDL.items() if name not in interim
    )
    legacy.executescript(
        f"CREATE TABLE cases ({columns});\n"
        "INSERT INTO cases (case_id, court, docket_number) VALUES "
        "('scotus/9500024001', 'scotus', '24A1099');"
    )
    legacy.commit()
    legacy.close()
    with corpus.connect(pre) as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(cases)")}
        assert set(interim) <= cols
        migrated = corpus.get_row(conn, "scotus/9500024001")
    assert migrated is not None
    assert migrated.application_kind is None  # never parsed, not 'unknown'
    assert migrated.response_requested is None
    assert migrated.referred_to_court is None
    assert migrated.amicus_briefs is None


def test_interim_escalation_signals_max_latch_and_never_regress(tmp_path: Path) -> None:
    # The three ladder signals are monotone over an application's life (the
    # Court does not un-request a response, un-refer an application, or un-file
    # an amicus brief), so a degraded parse's confident False/0 — or a writer
    # with nothing to assert (None) — must never regress a stored value, while a
    # real advance still lands.
    db = tmp_path / "corpus.db"
    base = {"case_id": "scotus/9500024001", "court": "scotus", "docket_number": "24A1099"}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [_row(**base, response_requested=True, referred_to_court=True, amicus_briefs=2)],
        )
        # A degraded parse: confidently absent signals.
        corpus.upsert_rows(
            conn,
            [_row(**base, response_requested=False, referred_to_court=False, amicus_briefs=0)],
        )
        after_degraded = corpus.get_row(conn, "scotus/9500024001")
        # A cert-form / CourtListener write: nothing to assert.
        corpus.upsert_rows(conn, [_row(**base)])
        after_none = corpus.get_row(conn, "scotus/9500024001")
        # A fresh parse with a real advance still lands.
        corpus.upsert_rows(conn, [_row(**base, amicus_briefs=5)])
        after_advance = corpus.get_row(conn, "scotus/9500024001")
    assert after_degraded is not None and after_none is not None and after_advance is not None
    assert after_degraded.response_requested is True
    assert after_degraded.referred_to_court is True
    assert after_degraded.amicus_briefs == 2
    assert after_none.response_requested is True
    assert after_none.referred_to_court is True
    assert after_none.amicus_briefs == 2
    assert after_advance.amicus_briefs == 5


def test_application_kind_keeps_a_real_reading_over_unknown(tmp_path: Path) -> None:
    # A degraded application parse reads a confident 'unknown' — not NULL — so
    # the latch must keep a real reading over it, let 'unknown' fill a genuine
    # gap, and let a real reading land over anything.
    db = tmp_path / "corpus.db"
    base = {"case_id": "scotus/9500024001", "court": "scotus", "docket_number": "24A1099"}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(**base, application_kind="substantive")])
        corpus.upsert_rows(conn, [_row(**base, application_kind="unknown")])
        after_unknown = corpus.get_row(conn, "scotus/9500024001")
        corpus.upsert_rows(conn, [_row(**base)])  # nothing to assert (a cert write)
        after_none = corpus.get_row(conn, "scotus/9500024001")
        corpus.upsert_rows(conn, [_row(case_id="scotus/9500024002", court="scotus")])
        corpus.upsert_rows(
            conn, [_row(case_id="scotus/9500024002", court="scotus", application_kind="unknown")]
        )
        filled = corpus.get_row(conn, "scotus/9500024002")
    assert after_unknown is not None and after_unknown.application_kind == "substantive"
    assert after_none is not None and after_none.application_kind == "substantive"
    assert filled is not None and filled.application_kind == "unknown"  # fills a real gap


def test_application_rotation_selects_unresolved_applications_in_order(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # OT25 never-polled lead (case_id breaking the tie between the
                # two); the OT25 polled row follows them.
                corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="25A2"),
                corpus.CorpusRow(case_id="scotus/20", court="scotus", docket_number="25A20"),
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25A1",
                    last_live_polled=date(2026, 7, 1),
                ),
                # Older Term follows the current one.
                corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24A3"),
                # Below the Term floor -> excluded (unfetchable upstream).
                corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="16A4"),
                # Resolved application -> excluded.
                corpus.CorpusRow(
                    case_id="scotus/5",
                    court="scotus",
                    docket_number="25A5",
                    disposition="denied",
                ),
                # Terminated without a disposition label -> excluded.
                corpus.CorpusRow(
                    case_id="scotus/6",
                    court="scotus",
                    docket_number="25A6",
                    date_decided=date(2026, 7, 1),
                ),
                # Cert form -> excluded (the cert rotation's population).
                corpus.CorpusRow(case_id="scotus/7", court="scotus", docket_number="25-7"),
                # A spelling the GLOB admits but the strict addressable-form
                # parser rejects -> dropped by the Python re-verification.
                corpus.CorpusRow(case_id="scotus/8", court="scotus", docket_number="25A8 (X)"),
            ],
        )
        picked = [r.case_id for r in corpus.application_rotation(conn, limit=10)]
        assert picked == ["scotus/2", "scotus/20", "scotus/1", "scotus/3"]
        # The cap is a cap.
        assert [r.case_id for r in corpus.application_rotation(conn, limit=1)] == ["scotus/2"]


def test_salience_columns_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    row = _row(
        case_id="scotus/1",
        court="scotus",
        docket_number="25-100",
        salience_score=0.37,
        salience_version="sal-v1",
        salience_selected=True,
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        fetched = corpus.get_row(conn, "scotus/1")
    assert fetched == row


def test_salience_score_zero_survives_roundtrip(tmp_path: Path) -> None:
    # A real score of 0.0 (a genuinely low-salience petition) must read back as
    # 0.0, not collapse to None — `_optional_float` guards this with `is not None`,
    # distinguishing a scored-zero row from an unscored one (score None).
    db = tmp_path / "corpus.db"
    row = _row(case_id="scotus/1", court="scotus", salience_score=0.0, salience_version="sal-v1")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        fetched = corpus.get_row(conn, "scotus/1")
    assert fetched is not None and fetched.salience_score == 0.0


def test_salience_columns_are_pass_owned_not_clobbered_by_ingest(tmp_path: Path) -> None:
    # The salience selection pass owns score/version/selected; an ingestion write
    # (which never carries a salience opinion — the model defaults apply) must
    # keep the stored values, the same rule predict_excluded uses.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="scotus/1", court="scotus", docket_number="25-100")])
        # Simulate the selection pass stamping its columns directly.
        conn.execute(
            "UPDATE cases SET salience_score = 0.9, salience_version = 'sal-v1', "
            "salience_selected = 1 WHERE case_id = 'scotus/1'"
        )
        # A later re-ingest carries no salience opinion (defaults: None/None/0).
        corpus.upsert_rows(conn, [_row(case_id="scotus/1", court="scotus", docket_number="25-100")])
        after = corpus.get_row(conn, "scotus/1")
    assert after is not None
    assert after.salience_score == 0.9
    assert after.salience_version == "sal-v1"
    assert after.salience_selected is True


def test_from_record_tolerates_record_without_salience_columns() -> None:
    """A ranged read of a remote blob packed before the salience columns existed."""
    record = corpus._to_record(_row())
    del record["salience_score"]
    del record["salience_version"]
    del record["salience_selected"]
    row = corpus._from_record(record)  # a plain dict raises KeyError like the ranged Row
    assert row.salience_score is None
    assert row.salience_version is None
    assert row.salience_selected is False
    assert row == _row()


def test_existing_db_with_retired_cell_attempts_column_still_reads(tmp_path: Path) -> None:
    """Forward-compat: a live DB physically carrying the retired `cell_attempts`
    column round-trips through the normal corpus API.

    The column and its model were dropped, but a corpus DB created under the old
    schema still has the physical column. The model/DDL no longer name it and the
    INSERT/UPSERT/SELECT use explicit column lists (SELECT * simply ignores the
    extra column in `_from_record`), so the residual column is harmless — no
    destructive migration needed. Simulate that DB by adding the column back after
    the schema is created, then write and read a row through the public API,
    including a populated legacy value to prove `SELECT *` tolerates it."""
    db = tmp_path / "corpus.db"
    row = _row(case_id="scotus/1", court="scotus", docket_number="25-100")
    with corpus.connect(db) as conn:
        # An older schema physically had this column; re-add it to mimic a live DB.
        conn.execute("ALTER TABLE cases ADD COLUMN cell_attempts TEXT NOT NULL DEFAULT '{}'")
        corpus.upsert_rows(conn, [row])
        # Populate the residual column directly, as an existing DB would carry it.
        conn.execute(
            "UPDATE cases SET cell_attempts = ? WHERE case_id = ?",
            (json.dumps({"evaluate:claude-judge:evt-x": {"attempts": 2}}), "scotus/1"),
        )
        fetched = corpus.get_row(conn, "scotus/1")
        # A re-ingest through the explicit-column upsert must not choke on the extra
        # physical column either.
        corpus.upsert_rows(conn, [row])
        refetched = corpus.get_row(conn, "scotus/1")
    assert fetched == row
    assert refetched == row


def test_ifp_petition_is_out_of_predict_scope() -> None:
    # The IFP docket serial starts at 5001; a paid cert docket stays in scope.
    ifp = _row(case_id="scotus/1", court="scotus", docket_number="25-5005")
    paid = _row(case_id="scotus/2", court="scotus", docket_number="25-100")
    assert corpus.is_ifp_petition(ifp) is True
    assert corpus.out_of_scope_reason(ifp) == (
        "in-forma-pauperis petition — a documented predict-scope exclusion"
    )
    assert corpus.is_ifp_petition(paid) is False
    assert corpus.out_of_scope_reason(paid) is None
    # A non-cert form (an application) does not parse, so it is not an IFP match.
    assert corpus.is_ifp_petition(_row(court="scotus", docket_number="25A100")) is False
    # Non-SCOTUS never matches.
    assert corpus.is_ifp_petition(_row(court="ca9", docket_number="5005")) is False


def test_is_salience_deferred_is_fail_open() -> None:
    # Unscored (no version) → treated as selected (fail-open), never deferred.
    assert corpus.is_salience_deferred(_row(salience_version=None)) is False
    # Scored and selected → in the slice, not deferred.
    assert (
        corpus.is_salience_deferred(_row(salience_version="sal-v1", salience_selected=True))
        is False
    )
    # Scored but not selected → deferred (dropped from the tournament this round).
    assert (
        corpus.is_salience_deferred(_row(salience_version="sal-v1", salience_selected=False))
        is True
    )


def test_is_live_slice_reads_the_poll_stamp() -> None:
    assert corpus.is_live_slice(_row(last_live_polled=date(2026, 7, 10))) is True
    assert corpus.is_live_slice(_row(last_live_polled=None)) is False


# --- the persisted frontier on live-discovery cursors ------------------------------


def test_live_frontier_roundtrip_and_no_op_without_cursor(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        # No cursor row yet: nothing to stamp onto, silently a no-op.
        corpus.set_live_frontier(conn, 25, "historical-paid", 100)
        assert corpus.get_live_frontier(conn, 25, "historical-paid") is None
        corpus.set_live_cursor(conn, 25, "historical-paid", 120)
        assert corpus.get_live_frontier(conn, 25, "historical-paid") is None
        corpus.set_live_frontier(conn, 25, "historical-paid", 120)
        assert corpus.get_live_frontier(conn, 25, "historical-paid") == 120
        # The frontier of a live Term moves: a later observation overwrites.
        corpus.set_live_cursor(conn, 25, "historical-paid", 140)
        corpus.set_live_frontier(conn, 25, "historical-paid", 140)
        assert corpus.get_live_frontier(conn, 25, "historical-paid") == 140


def test_connect_migrates_a_frontierless_cursor_table(tmp_path: Path) -> None:
    # A corpus written before `frontier_serial` existed gains the column on
    # open, with its cursor rows intact and readable.
    db = tmp_path / "corpus.db"
    legacy = sqlite3.connect(db)
    legacy.execute(
        "CREATE TABLE live_discovery_cursors ("
        "term INTEGER NOT NULL, stream TEXT NOT NULL, last_serial INTEGER NOT NULL, "
        "PRIMARY KEY (term, stream))"
    )
    legacy.execute("INSERT INTO live_discovery_cursors VALUES (25, 'paid', 42)")
    legacy.commit()
    legacy.close()
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 25, "paid") == 42
        assert corpus.get_live_frontier(conn, 25, "paid") is None
        corpus.set_live_frontier(conn, 25, "paid", 42)
        assert corpus.get_live_frontier(conn, 25, "paid") == 42


def test_rename_live_streams_carries_the_frontier_stamp(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 22, "seed-paid", 300)
        corpus.set_live_frontier(conn, 22, "seed-paid", 300)
        corpus.rename_live_streams(conn, {"seed-paid": "historical-paid"})
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 300
        assert corpus.get_live_frontier(conn, 22, "historical-paid") == 300
        assert corpus.get_live_cursor(conn, 22, "seed-paid") is None


# --- the live-shaped snapshot reader ------------------------------------------------


def test_latest_live_snapshot_skips_a_newer_rest_snapshot(tmp_path: Path) -> None:
    # The snapshots table holds both channels' payloads; the signal backfill
    # needs the newest *live-shaped* one even when a later pull stored a
    # CourtListener-shaped snapshot on top.
    db = tmp_path / "corpus.db"
    live_payload = {"CaseNumber": "25-100 ", "ProceedingsandOrder": []}
    rest_payload = {"id": 1, "court": "https://example/courts/scotus/"}
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "scotus/1", date(2026, 6, 10), live_payload)
        corpus.upsert_snapshot(conn, "scotus/1", date(2026, 6, 20), rest_payload)
        assert corpus.latest_snapshot(conn, "scotus/1") == (date(2026, 6, 20), rest_payload)
        assert corpus.latest_live_snapshot(conn, "scotus/1") == (date(2026, 6, 10), live_payload)
        assert corpus.latest_live_snapshot(conn, "scotus/none") is None


def test_connect_readonly_rejects_service_backend(tmp_path: Path) -> None:
    # "service" has no client-side connection: query/open-events forward whole
    # requests to the corpus query service, so any other consumer inheriting
    # the setting must fail loudly here rather than silently read local.
    with (
        pytest.raises(ValueError, match="service backend has no client-side connection"),
        corpus.connect_readonly(tmp_path / "corpus.db", backend="service"),
    ):
        pass


def test_prior_payload_shapes_the_query_row() -> None:
    row = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        docket_number="24-1",
        date_filed=date(2024, 10, 7),
        opinion_text="per curiam",
    )
    bare = corpus.prior_payload(row)
    assert bare["era"] == "2020s"
    assert "opinion_text" not in bare
    full = corpus.prior_payload(row, full=True)
    assert full["opinion_text"] == "per curiam"


def test_resolved_only_counts_a_decision_date_as_decided(tmp_path: Path) -> None:
    # The rotation's closed-case reading: a decision date closes a case even
    # when no disposition label was machine-derived — such rows must retrieve
    # as precedent rather than being invisibly excluded.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(case_id="ca9/1"),  # labeled + dated
                _row(case_id="ca9/2", disposition=None),  # dated, never labeled
                _row(case_id="ca9/3", disposition=None, date_decided=None),  # open
            ],
        )
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(court="ca9"), limit=10)
    assert [r.case_id for r in priors] == ["ca9/1", "ca9/2"]


def test_sparse_filter_coverage_names_the_data_gap(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(case_id="ca9/1", citations=["597 U.S. 1"]),
                _row(case_id="ca9/2", citations=[], topic=None),
            ],
        )
        none = corpus.sparse_filter_coverage(conn, corpus.PriorQuery(court="ca9"))
        cites = corpus.sparse_filter_coverage(
            conn, corpus.PriorQuery(court="ca9", citations=["1 U.S. 1"])
        )
        topic = corpus.sparse_filter_coverage(conn, corpus.PriorQuery(court="ca9", topic="tribe"))
    assert none == []
    assert len(cites) == 1 and "1 of 2 rows in scope (ca9)" in cites[0]
    assert "OWN reporter cites" in cites[0]
    assert len(topic) == 1 and "1 of 2 rows in scope (ca9)" in topic[0]
    assert "exact" in topic[0]


def test_a_docket_annotation_does_not_change_a_docket_number() -> None:
    """The bug this prevents: two channels spelling one docket differently.

    CourtListener discovers the plain number while supremecourt.gov serves it with
    a `*** CAPITAL CASE ***` flag appended. Left in, the two normalize differently,
    the identity join misses, and both channels mint a row for the same petition —
    which is how 22 duplicate SCOTUS rows reached the corpus.
    """
    assert corpus.normalize_docket_number("25-5184 *** CAPITAL CASE ***") == "25-5184"
    assert corpus.normalize_docket_number("25-5184 *** CAPITAL CASE ***") == (
        corpus.normalize_docket_number("25-5184")
    )
    # Whichever end it is appended to.
    assert corpus.normalize_docket_number("*** CAPITAL CASE *** 25-5184") == "25-5184"


def test_stripping_an_annotation_still_yields_no_false_matches() -> None:
    """The normalization's standing promise: a miss, never a wrong link. Removing
    a flag must not make two genuinely different dockets compare equal, and must
    not turn a consolidated multi-number string into a single tracked docket."""
    assert corpus.normalize_docket_number("21-1, 21-2") == "21-1,21-2"
    assert corpus.normalize_docket_number("25-5184 *** CAPITAL CASE ***") != (
        corpus.normalize_docket_number("25-5185")
    )
    # An annotation is not a docket number, so a string that is only one is empty.
    assert corpus.normalize_docket_number("*** CAPITAL CASE ***") is None


def test_the_bare_number_test_is_unaffected_by_stripping() -> None:
    """`is_historical_mandatory` keys on `.isdigit()` of the normalized value, so a
    change here could silently reclassify rows into the out-of-scope regime.
    Verified against the live corpus: 318 rows normalize differently and zero flip
    this test."""
    assert corpus.normalize_docket_number("No. 123") == "123"
    assert (corpus.normalize_docket_number("No. 123") or "").isdigit()
    assert not (corpus.normalize_docket_number("25-5184 *** CAPITAL CASE ***") or "").isdigit()


def _scotus(docket_number: str) -> corpus.CorpusRow:
    return corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number=docket_number)


def test_an_application_serial_may_carry_hyphens_or_a_trailing_letter() -> None:
    """Real spellings on the application docket that an end-anchored `\\d+` missed,
    which let five rows past the scope rule and into predict scope. An
    application's disposition is a stay grant/deny, so one reaching a cert cell
    would be scored against a target the model is not calibrated for."""
    for dn in ("A14-662", "A-13-717", "A-0245-12", "A04-1646", "18A142T"):
        assert corpus.is_non_cert_scotus_form(_scotus(dn)), dn


def test_the_widened_serial_still_cannot_reach_a_cert_number() -> None:
    """The letter is the whole discriminator: a modern cert number is `YY-NNNN`
    with no letter anywhere, so widening what counts as a serial cannot catch one.
    Verified over the corpus too — the widening excludes nine more rows and zero
    of them is a modern cert petition."""
    for dn in ("25-5184", "25-1", "24-12", "22-451"):
        assert not corpus.is_non_cert_scotus_form(_scotus(dn)), dn


def test_a_dangling_hyphen_is_not_a_serial() -> None:
    """The serial has to end in a digit, or a bare letter-and-dash would read as
    an application docket."""
    assert not corpus.is_non_cert_scotus_form(_scotus("A-"))


def test_the_sibling_letter_forms_take_the_same_tolerances() -> None:
    """Original, miscellaneous and disbarment dockets carry the same spellings for
    the same reason; the rule treats all of them as non-cert forms, so a tolerance
    added to one belongs on the others."""
    assert corpus.is_non_cert_scotus_form(_scotus("22O14-1"))
    assert corpus.is_non_cert_scotus_form(_scotus("M-62-3"))
    assert corpus.is_disbarment_docket(_scotus("16D02977"))


def test_counsel_reads_empty_from_a_blob_that_predates_the_column(tmp_path: Path) -> None:
    """The ranged and service backends read the published blob as-is — no
    ``connect`` migration runs — so a column the blob predates must read as its
    default through ``_from_record``, the same contract every ``_optional_*``
    column honors."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/886")])

    raw = sqlite3.connect(db)
    try:
        raw.execute("ALTER TABLE cases DROP COLUMN counsel")
        raw.commit()
        raw.row_factory = sqlite3.Row
        record = raw.execute("SELECT * FROM cases WHERE case_id = 'scotus/886'").fetchone()
        row = corpus._from_record(record)
    finally:
        raw.close()
    assert row.counsel == []


def test_counsel_round_trips_with_its_side(tmp_path: Path) -> None:
    """The side is the reason the column exists, so it is the thing that must
    survive storage — a round trip that kept only the names would be the flat
    `attorneys` list again, spelled more expensively."""
    db = tmp_path / "corpus.db"
    entries = [
        corpus.CounselEntry(
            party="United States",
            attorney="D. John Sauer",
            role=corpus.CounselRole.petitioner,
            counsel_of_record=True,
        ),
        corpus.CounselEntry(
            party="Donte J. Carter",
            attorney="Shay Dvoretzky",
            role=corpus.CounselRole.respondent,
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/885", counsel=entries)])
        stored = corpus.get_row(conn, "scotus/885")
    assert stored is not None
    assert stored.counsel == entries
    assert stored.counsel[0].counsel_of_record is True
    assert stored.counsel[1].counsel_of_record is False


def test_event_stage_round_trips_and_null_stays_null(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/1",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                ),
                corpus.CorpusEvent(
                    event_id="evt-appeal-disposition",
                    case_id="ca9/2",
                    court="ca9",
                    kind=EventKind.appeal,
                ),
            ],
        )
        staged = corpus.events_for_case(conn, "scotus/1")
        unstaged = corpus.events_for_case(conn, "ca9/2")
    assert staged[0].stage == "cert"
    assert unstaged[0].stage is None


def test_migrate_events_adds_the_stage_column(tmp_path: Path) -> None:
    """A corpus written before the column existed opens cleanly and reads
    its pre-existing events with no stage, rather than failing the SELECT."""
    db = tmp_path / "corpus.db"
    raw = sqlite3.connect(db)
    raw.executescript(
        """
        CREATE TABLE events (
            case_id         TEXT NOT NULL,
            event_id        TEXT NOT NULL,
            court           TEXT NOT NULL,
            kind            TEXT NOT NULL,
            title           TEXT NOT NULL DEFAULT '',
            description     TEXT,
            docket_entry_id INTEGER,
            decision_target TEXT NOT NULL DEFAULT 'disposition',
            opened_at       TEXT,
            resolved        INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (case_id, event_id)
        );
        INSERT INTO events (case_id, event_id, court, kind)
        VALUES ('scotus/7', 'evt-petition-disposition', 'scotus', 'petition');
        """
    )
    raw.commit()
    raw.close()
    with corpus.connect(db) as conn:
        events = corpus.events_for_case(conn, "scotus/7")
    assert len(events) == 1
    assert events[0].stage is None
    assert events[0].moment is None


def test_events_schema_and_migration_ddl_agree(tmp_path: Path) -> None:
    """A fresh `events` table has exactly the columns the writers bind.

    The events counterpart of the `cases` guard above: the bound list and
    the migration are built from one DDL map, and this pins the map against
    the live CREATE TABLE — so the next added column cannot reach the
    writers without reaching the migration.
    """
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(events)")}
    assert cols == set(corpus._EVENT_COLUMNS) == set(corpus._EVENTS_COLUMN_DDL)


def test_migrate_events_backfills_every_written_column(tmp_path: Path) -> None:
    """The original events table accepts an event write after migration.

    The failure shape this pins: `_event_upsert_sql` binds the full column
    list, so a blob whose `events` table predates any written column fails
    the first upsert with "no column named ..." — the corpus writers' whole
    lane, not one row. Build the table's original creation-time schema (no
    stage, no moment, no docket_entry_id), then prove connect() migrates it
    far enough that a current-code upsert round-trips.
    """
    db = tmp_path / "corpus.db"
    raw = sqlite3.connect(db)
    raw.executescript(
        """
        CREATE TABLE events (
            case_id         TEXT NOT NULL,
            event_id        TEXT NOT NULL,
            court           TEXT NOT NULL,
            kind            TEXT NOT NULL,
            title           TEXT NOT NULL DEFAULT '',
            description     TEXT,
            decision_target TEXT NOT NULL DEFAULT 'disposition',
            opened_at       TEXT,
            resolved        INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (case_id, event_id)
        );
        """
    )
    raw.commit()
    raw.close()
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-order-judgment",
                    case_id="scotus/7",
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                    moment=Moment.grant,
                    title="Cascade Timber Co. v. United States",
                    docket_entry_id=24,
                    decision_target="judgment",
                    resolved=False,
                )
            ],
        )
        (event,) = corpus.events_for_case(conn, "scotus/7")
    assert event.stage == Stage.merits
    assert event.moment == Moment.grant
    assert event.docket_entry_id == 24


def test_event_from_pre_stage_ranged_row_reads_stage_as_unset() -> None:
    """The ranged backend serves the remote blob as-is, so an events row from a
    blob written before the column existed must read with no stage rather than
    failing the SELECT wholesale."""
    columns = [
        "case_id",
        "event_id",
        "court",
        "kind",
        "title",
        "description",
        "docket_entry_id",
        "decision_target",
        "opened_at",
        "resolved",
    ]
    names = {name: i for i, name in enumerate(columns)}
    record = corpus_ranged.Row(
        names,
        (
            "scotus/7",
            "evt-petition-disposition",
            "scotus",
            "petition",
            "t",
            None,
            None,
            "disposition",
            None,
            0,
        ),
    )
    event = corpus._event_from_record(record)
    assert event.stage is None
    assert event.event_id == "evt-petition-disposition"


# --- the merits pair latch ---------------------------------------------------------


def test_merits_pair_survives_a_writer_with_no_parse(tmp_path: Path) -> None:
    # A writer carrying no judgment (a REST enrichment, a bulk row, a degraded
    # live payload) keeps BOTH stored values: the pair latch keys on the
    # incoming judgment, so the backfill's stamp and the live channel's
    # ingest-time parse cannot wipe each other.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="22-451",
                    merits_judgment="reversed",
                    merits_decided=date(2023, 6, 27),
                )
            ],
        )
        corpus.upsert_rows(conn, [_row(case_id="scotus/1", court="scotus", docket_number="22-451")])
        stored = corpus.get_row(conn, "scotus/1")
    assert stored is not None
    assert stored.merits_judgment == "reversed"
    assert stored.merits_decided == date(2023, 6, 27)


def test_merits_pair_moves_as_a_pair_on_a_fresh_parse(tmp_path: Path) -> None:
    # A fresh parse takes both halves — its date included even when that is
    # NULL (an undated entry): keeping the old date beside the new judgment
    # would fabricate a mismatched pair.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="22-451",
                    merits_judgment="reversed",
                    merits_decided=date(2023, 6, 27),
                )
            ],
        )
        corpus.upsert_rows(
            conn,
            [
                _row(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="22-451",
                    merits_judgment="vacated",
                    merits_decided=None,
                )
            ],
        )
        stored = corpus.get_row(conn, "scotus/1")
    assert stored is not None
    assert stored.merits_judgment == "vacated"
    assert stored.merits_decided is None
