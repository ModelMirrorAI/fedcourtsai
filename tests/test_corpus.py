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
