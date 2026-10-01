"""The per-opinion record: the word-count rule, the two splitters, the writer.

Every fixture is text shaped like what pypdf extracts from the Court's slip
opinions (layout mode) and preliminary prints (plain-mode lines with type
sizes), written out here; nothing in this file touches the network.
"""

from __future__ import annotations

import ast
import json
import sqlite3
from datetime import date
from pathlib import Path

import httpx
import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline import opinion_record
from fedcourtsai.pipeline.lineup import Join, Writing, WritingKind
from fedcourtsai.pipeline.opinion_lineups import OpinionListing
from fedcourtsai.pipeline.opinion_record import (
    OpinionDocumentReading,
    OpinionEntry,
    OpinionJoin,
    PrintLine,
    Section,
    build_opinion_record,
    count_words,
    insert_opinions,
    read_header,
    recorded_documents,
    split_print,
    split_slip,
)

BENCH = (
    "Roberts",
    "Thomas",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
    "Barrett",
    "Jackson",
)

# --- the counting rule --------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "words"),
    [
        ("The Court holds that the order is valid.", 8),
        # A hyphen ending a line closes up: one word, not two.
        ("the juris-\ndiction of the Court", 5),
        # A hyphenated compound and a number range are one word each.
        ("a well-settled rule, Id., at 404\u2013405", 6),
        # The em dash separates words; the en dash does not.
        ("the States—and the Nation", 5),
        # A citation counts token by token; a bare section sign is not a word.
        ("Dred Scott v. Sandford, 19 How. 393 (1857)", 8),
        ("42 U. S. C. §1983 and § 1983", 7),
        # Ellipsis dots and stray punctuation are not words.
        ("born . . . in the United States ” ,", 5),
    ],
)
def test_the_counting_rule(text: str, words: int) -> None:
    assert count_words(text) == words


def test_a_spaced_off_reference_mark_is_not_a_word() -> None:
    section = Section(
        read_header("JUSTICE ALITO, dissenting.", bench=BENCH)  # type: ignore[arg-type]
    )
    section.body = [
        "JUSTICE ALITO, dissenting.",
        "as high as 75. 1 Smith also introduced 2 records.",
    ]
    # "1" follows a period and is the next expected mark; "2" follows a word.
    assert section.words == 3 + 9


# --- headers -----------------------------------------------------------------------


def test_headers_read_lead_per_curiam_and_separate_writings() -> None:
    lead = read_header(
        "CHIEF            JUSTICE   ROBERTS delivered the opinion of the\nCourt.", bench=BENCH
    )
    assert lead is not None and lead.lead and lead.authors == ("Roberts",)
    assert lead.kind is WritingKind.opinion_of_the_court
    plurality = read_header(
        "JUSTICE ALITO announced the judgment of the Court and delivered an opinion.",
        bench=BENCH,
    )
    assert plurality is not None and plurality.kind is WritingKind.plurality
    per_curiam = read_header("Per Curiam.\nThe writ is dismissed.", bench=BENCH)
    assert per_curiam is not None and per_curiam.kind is WritingKind.per_curiam
    separate = read_header(
        "JUSTICE JACKSON, with whom JUSTICE SOTOMAYOR joins\nas to the introduction and "
        "Part I, concurring.\n I join the Court\u2019s opinion in full.",
        bench=BENCH,
    )
    assert separate is not None and not separate.lead
    assert separate.kind is WritingKind.concurrence
    assert separate.authors == ("Jackson",)
    assert separate.joins == (Join("Sotomayor", "as to the introduction and Part I"),)
    mixed = read_header(
        "JUSTICE KAVANAUGH, concurring in the judgment and\ndissenting in part.", bench=BENCH
    )
    assert mixed is not None and mixed.kind is WritingKind.concurrence_in_part_dissent_in_part
    joint = read_header(
        "JUSTICE SOTOMAYOR, JUSTICE KAGAN, and JUSTICE JACKSON, dissenting.", bench=BENCH
    )
    assert joint is not None and joint.authors == ("Sotomayor", "Kagan", "Jackson")
    chief = read_header(
        "THE CHIEF JUSTICE, with whom JUSTICE KAGAN joins, dissenting.", bench=BENCH
    )
    assert chief is not None and chief.authors == ("Roberts",)
    assert chief.joins == (Join("Kagan", None),)
    two = read_header(
        "Justice Alito, with whom Justice Thomas joins as to Part I and with whom Justice "
        "Barrett joins as to Parts II and III, dissenting.",
        bench=BENCH,
    )
    assert two is not None
    assert two.joins == (Join("Thomas", "as to Part I"), Join("Barrett", "as to Parts II and III"))


@pytest.mark.parametrize(
    "prose",
    [
        "Justice Kagan's dissent says otherwise.",
        "Justice Kagan, dissenting, contends that the Court errs.",
        "JUSTICE BRENNAN, dissenting.",  # not on this bench
        "The Court holds that the order is valid.",
    ],
)
def test_prose_is_not_a_header(prose: str) -> None:
    assert read_header(prose, bench=BENCH) is None


# --- the slip opinion ------------------------------------------------------------------

_SYLLABUS = """ 1 (Slip Opinion) OCTOBER TERM, 2025
Syllabus
SUPREME COURT OF THE UNITED STATES
Syllabus
DOE v. ROE
No. 25-1. Argued April 1, 2026—Decided June 30, 2026
KAGAN, J., delivered the opinion of the Court."""


def _caption(head: str, header: str) -> str:
    return f""" Cite as: 609 U. S. ____ (2026)        1

                   {head}
SUPREME COURT OF THE UNITED STATES
                   _________________
                   No. 25\u20131
                   _________________
  JOHN DOE, PETITIONER v. RICHARD ROE
ON WRIT OF CERTIORARI TO THE UNITED STATES COURT OF
       APPEALS FOR THE NINTH CIRCUIT
                   [June 30, 2026]

{header}"""


def test_the_slip_splits_at_each_caption_and_counts_footnotes() -> None:
    pages = [
        _SYLLABUS,
        _caption("Opinion of the Court", "  JUSTICE KAGAN delivered the opinion of the Court.*")
        + "\n  The question is simple.1 We answer it.\n\n——————\n"
        + "  *Together with No. 25\u20132, Roe v. Doe, also on certiorari.\n"
        + "  1 A footnote of six words.",
        " 2 DOE v. ROE\n\n          Opinion of the Court\n  It is so ordered.",
        _caption(
            "ALITO, J., dissenting",
            "  JUSTICE ALITO, with whom JUSTICE THOMAS joins,\n"
            + "dissenting.\n  I would reverse.",
        ),
    ]
    sections, problems = split_slip(pages, bench=BENCH)
    assert problems == []
    assert [s.header.kind for s in sections] == [
        WritingKind.opinion_of_the_court,
        WritingKind.dissent,
    ]
    lead, dissent = sections
    # Header (7) + body (8) + "It is so ordered." (4); the caption, running
    # heads and the "Together with" note are not the opinion's.
    assert lead.footnote_words == 5
    assert lead.words == 7 + 8 + 4 + 5
    assert dissent.words == count_words(
        "JUSTICE ALITO, with whom JUSTICE THOMAS joins, dissenting. I would reverse."
    )


def test_an_unread_slip_header_is_a_problem() -> None:
    pages = [
        _SYLLABUS,
        _caption("Opinion", "  JUSTICE BRENNAN delivered the opinion of the Court."),
    ]
    sections, problems = split_slip(pages, bench=BENCH)
    assert len(sections) == 1 and sections[0].header.kind is None
    assert problems


# --- the preliminary print ---------------------------------------------------------------

BODY, SMALL, MARK = 11.0, 9.0, 5.4
# A page of body type, so the print's body size is the body's, as in a real print.
_FILLER = PrintLine("x " * 400, BODY)


def _page(*lines: tuple[str, float]) -> list[PrintLine]:
    return [PrintLine(text, size) for text, size in lines]


def test_the_print_splits_mid_page_and_drops_the_amicus_note() -> None:
    pages = [
        _page(
            ("278 OCTOBER TERM, 2025", SMALL),
            ("Syllabus", SMALL),
            ("Kagan, J., delivered the opinion of the Court.", SMALL),
            ("Jane Roe argued the cause for petitioner.*", BODY),
            ("*Briefs of amici curiae urging reversal were fled for the", SMALL),
            ("State of Idaho et al. by Raul Labrador;", SMALL),
        ),
        _page(
            ("Cite as: 608 U. S. 278 (2026) 279", SMALL),
            ("Opinion of the Court", SMALL),
            ("Justice Kagan delivered the opinion of the Court.", BODY),
            ("The question is simple. 1 We answer it.", BODY),
            ("It is so ordered.", BODY),
            ("Justice Alito, with whom Justice Thomas joins,", BODY),
            ("dissenting.", BODY),
            ("I would reverse. 1 Respectfully.", BODY),
            ("and for the Cato Institute by Ilya Shapiro.", SMALL),
            ("1 A footnote of six words.", MARK),
            ("1 The dissent's footnote here.", MARK),
        ),
    ]
    sections, problems = split_print([[_FILLER], *pages], bench=BENCH)
    assert problems == []
    lead, dissent = sections
    assert lead.header.kind is WritingKind.opinion_of_the_court
    assert dissent.header.kind is WritingKind.dissent
    assert dissent.header.joins == (Join("Thomas", None),)
    # The amicus note's continuation is dropped; each "1" goes to its opinion.
    assert lead.footnote_words == 5
    assert dissent.footnote_words == 4
    assert lead.words == 7 + 8 + 4 + 5
    assert dissent.words == 9 + 3 + 4


def test_a_print_note_continues_across_pages() -> None:
    pages = [
        _page(
            ("Justice Kagan delivered the opinion of the Court.", BODY),
            ("Text. 1 More text.", BODY),
            ("1 A note that runs", SMALL),
        ),
        _page(
            ("Cite as: 608 U. S. 278 (2026) 279", SMALL),
            ("Opinion of the Court", SMALL),
            ("Closing text.", BODY),
            ("onto the next page.", SMALL),
        ),
    ]
    sections, _ = split_print([[_FILLER], *pages], bench=BENCH)
    assert sections[0].footnote_words == 8


# --- the cross-check --------------------------------------------------------------------


def _section(text: str) -> Section:
    header = read_header(text, bench=BENCH)
    assert header is not None
    return Section(header, body=[text])


def test_the_cross_check_needs_count_authors_and_kinds_to_agree() -> None:
    lead = Writing(WritingKind.opinion_of_the_court, "Kagan")
    dissent = Writing(WritingKind.dissent, "Alito", (Join("Thomas"),))
    sections = [
        _section("JUSTICE KAGAN delivered the opinion of the Court."),
        _section("JUSTICE ALITO, with whom JUSTICE THOMAS joins, dissenting."),
    ]
    assert opinion_record._cross_check([lead, dissent], sections) == []
    assert opinion_record._cross_check([lead], sections)
    other = Writing(WritingKind.dissent, "Gorsuch")
    assert opinion_record._cross_check([lead, other], sections)
    concurrence = Writing(WritingKind.concurrence, "Alito")
    assert opinion_record._cross_check([lead, concurrence], sections)


# --- the writer ----------------------------------------------------------------------------


def _listing(number: str, docket: str) -> OpinionListing:
    return OpinionListing(
        term=25,
        number=number,
        decided=date(2026, 6, 30),
        docket=docket,
        name=f"Case {number}",
        url=f"https://www.supremecourt.gov/opinions/25pdf/{docket}_x.pdf",
        author_code="EK",
    )


class _Fetcher:
    def __init__(self, rows: list[OpinionListing]) -> None:
        self.rows = rows
        self.fetched: list[str] = []

    def listing(self, term: int) -> list[OpinionListing]:
        assert term == 25
        return self.rows

    def opinion(self, url: str) -> bytes | None:
        self.fetched.append(url)
        return b"%PDF"


def _reading(entry: OpinionListing, data: bytes) -> OpinionDocumentReading:
    del data
    opinions = [
        OpinionEntry(
            position=1,
            kind=WritingKind.opinion_of_the_court,
            author="Kagan",
            words=100,
            footnote_words=10,
            header="JUSTICE KAGAN delivered the opinion of the Court.",
        ),
        OpinionEntry(
            position=2,
            kind=WritingKind.dissent,
            author="Alito",
            joins=[OpinionJoin(justice="Thomas", qualifier="as to Part I")],
            words=50,
            footnote_words=0,
            header="JUSTICE ALITO, with whom JUSTICE THOMAS joins as to Part I, dissenting.",
        ),
    ]
    return opinion_record._base(
        entry, status="read", source_format="slip", lineup="scotus-syllabus/2", opinions=opinions
    )


@pytest.fixture
def _corpus(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(opinion_record, "read_document", _reading)
    path = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(path) as conn:
        conn.execute(
            "INSERT INTO cases (case_id, court, docket_number) "
            + "VALUES ('scotus/1', 'scotus', '25-1')"
        )
        conn.commit()
    return path


def test_the_dry_run_writes_nothing_and_reads_a_missing_table_as_empty(tmp_path: Path) -> None:
    path = tmp_path / "legacy.db"
    raw = sqlite3.connect(path)
    raw.execute("CREATE TABLE cases (case_id TEXT, court TEXT, docket_number TEXT)")
    raw.commit()
    raw.close()
    ro = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        assert recorded_documents(ro) == set()
    finally:
        ro.close()


def test_apply_inserts_fill_only_and_a_rerun_fetches_nothing(_corpus: Path) -> None:
    fetcher = _Fetcher([_listing("1", "25-1"), _listing("2", "25-2")])
    with corpus.connect(_corpus) as conn:
        dry = build_opinion_record(conn, fetcher, terms=[2025])
        assert not dry.applied and dry.rows == 4
        assert conn.execute("SELECT COUNT(*) FROM opinions").fetchone()[0] == 0
        assert [r.case_id for r in dry.readings] == ["scotus/1", None]

        refused = build_opinion_record(
            conn,
            fetcher,
            terms=[2025],
            apply=True,
            max_rows=3,
            write=lambda pairs: insert_opinions(conn, pairs),
        )
        assert refused.refused and not refused.applied
        assert conn.execute("SELECT COUNT(*) FROM opinions").fetchone()[0] == 0

        done = build_opinion_record(
            conn,
            fetcher,
            terms=[2025],
            apply=True,
            max_rows=4,
            write=lambda pairs: insert_opinions(conn, pairs),
        )
        assert done.applied and done.rows == 4
        row = conn.execute(
            "SELECT * FROM opinions WHERE listing_number = '1' AND position = 2"
        ).fetchone()
        assert row["author"] == "Alito" and row["kind"] == "dissent"
        assert json.loads(row["joins"]) == [{"justice": "Thomas", "qualifier": "as to Part I"}]
        assert row["word_rule"] == "scotus-opinion-words/1"
        assert row["case_id"] == "scotus/1"

        fetcher.fetched.clear()
        again = build_opinion_record(
            conn,
            fetcher,
            terms=[2025],
            apply=True,
            max_rows=0,
            write=lambda pairs: insert_opinions(conn, pairs),
        )
        assert again.rows == 0 and again.already_recorded == 2 and fetcher.fetched == []
        assert conn.execute("SELECT COUNT(*) FROM opinions").fetchone()[0] == 4


def test_a_volume_linked_row_is_skipped_unfetched(_corpus: Path) -> None:
    entry = OpinionListing(
        term=19,
        number="1",
        decided=date(2019, 11, 1),
        docket="18-1",
        name="Old",
        url="https://www.supremecourt.gov/opinions/preliminaryprint/589US1PP_final.pdf#page=5",
        author_code="EK",
    )
    fetcher = _Fetcher([entry])
    reading = opinion_record.read_listing_entry(entry, fetcher)
    assert reading.status == "skipped" and fetcher.fetched == []


def test_a_listing_failure_is_reported(_corpus: Path) -> None:
    class Down(_Fetcher):
        def listing(self, term: int) -> list[OpinionListing]:
            raise httpx.ConnectError("down")

    with corpus.connect(_corpus) as conn:
        result = build_opinion_record(conn, Down([]), terms=[2025])
    assert result.failures and result.readings == []


# --- withheld from what a cell sees ------------------------------------------------------


def test_the_table_is_created_from_its_ddl_map(tmp_path: Path) -> None:
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(opinions)")]
    assert cols == list(corpus.OPINIONS_COLUMN_DDL)


def test_no_retrieval_row_carries_the_opinion_record() -> None:
    """A ``query`` row is a case row: no field of the per-opinion record is on it."""
    record_only = set(corpus.OPINIONS_COLUMN_DDL) - {"case_id", "docket", "case_name"}
    assert not record_only & set(corpus.CorpusRow.model_fields)


def test_only_the_record_s_own_modules_touch_the_table() -> None:
    """No module but the writer, the schema and the CLI names the ``opinions`` table in SQL.

    So no retrieval, provisioning, outcome or scoring path — nothing a predict
    or evaluate cell is shown — can read it without this test changing.
    """
    root = Path(__file__).resolve().parents[1] / "src" / "fedcourtsai"
    allowed = {"corpus.py", "pipeline/opinion_record.py"}
    touching: set[str] = set()
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                text = " ".join(node.value.split()).lower()
                if any(f"{verb} opinions" in text for verb in ("from", "into", "table", "update")):
                    touching.add(str(path.relative_to(root)))
    assert touching <= allowed, touching - allowed
