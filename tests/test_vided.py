"""The VIDED amicus keys: how a companion the Court never linked as ``Vide`` is found.

One amicus brief supporting two petitions is entered on each docket and marked
``VIDED``. :mod:`fedcourtsai.pipeline.vided` reads each such entry as a
``<date>|<filer>`` key, the live poll writes a docket's keys to the corpus, and
:func:`fedcourtsai.corpus.vided_companions` finds the dockets sharing one.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row
from fedcourtsai.pipeline.vided import vided_amicus_keys, vided_key

_SAMARITAN = ("Sep 14 2026", "Brief amici curiae of Samaritan\u2019s Purse, et al. filed.  VIDED.")
_ACLJ = ("Sep 14 2026", "Brief amicus curiae of American Center for Law and Justice filed. VIDED")
_PLAIN = ("Sep 15 2026", "Brief amicus curiae of Cato Institute filed.")


def _payload(*entries: tuple[str, str], number: str = "26-193") -> dict[str, object]:
    return {
        "CaseNumber": f"{number} ",
        "ProceedingsandOrder": [{"Date": d, "Text": t, "Links": []} for d, t in entries],
    }


def test_a_vided_amicus_entry_reads_as_its_day_and_filer() -> None:
    assert vided_key(_SAMARITAN[1], _SAMARITAN[0]) == (
        "2026-09-14|brief amici curiae of samaritan s purse et al filed"
    )
    # The mark with or without its period, and the spacing around it, read alike.
    assert vided_key("Brief amici curiae of X filed. VIDED", "Sep 14 2026") == vided_key(
        "Brief amici curiae of X filed.  VIDED.", "Sep 14 2026"
    )
    # A brief filed after distribution carries the Clerk's note after the mark,
    # and keys the same as on a docket it reached before distribution.
    assert vided_key("Brief amici curiae of X filed.  VIDED. (Distributed)", "Sep 14 2026") == (
        vided_key("Brief amici curiae of X filed.  VIDED.", "Sep 14 2026")
    )


def test_only_a_dated_amicus_entry_marked_vided_is_a_key() -> None:
    assert vided_key(_PLAIN[1], _PLAIN[0]) is None
    # A VIDED entry that is not an amicus filing: a party's own brief.
    assert vided_key("Brief of respondent in opposition filed. VIDED.", "Sep 14 2026") is None
    # No day to bound it, so the same filer's brief in another case would match.
    assert vided_key(_SAMARITAN[1], None) is None
    assert vided_key(_SAMARITAN[1], "Sep 2026") is None


def test_a_dockets_keys_are_sorted_and_unrepeated() -> None:
    keys = vided_amicus_keys(_payload(_SAMARITAN, _PLAIN, _ACLJ, _SAMARITAN))
    assert keys is not None
    assert keys == sorted(keys)
    assert len(keys) == 2


def test_no_vided_entry_and_no_proceedings_both_read_none() -> None:
    assert vided_amicus_keys(_payload(_PLAIN)) is None
    assert vided_amicus_keys({"CaseNumber": "26-193 "}) is None


def test_the_live_cert_branch_writes_the_keys_at_ingest() -> None:
    payload = _payload(_SAMARITAN, _PLAIN)
    row = to_corpus_row(from_live_record(map_live_docket(payload, 9026000193, form="cert")))
    assert row.vided_amicus == vided_amicus_keys(payload)
    application = _payload(_SAMARITAN, number="26A193")
    row = to_corpus_row(
        from_live_record(map_live_docket(application, 9026000194, form="application"))
    )
    assert row.vided_amicus is None


def _row(case_id: str, number: str, keys: list[str] | None) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id, court="scotus", docket_number=number, vided_amicus=keys
    )


def test_the_column_migrates_and_fills_in(tmp_path: Path) -> None:
    pre = tmp_path / "pre-change.db"
    legacy = sqlite3.connect(pre)
    columns = ",\n".join(
        f"{name} {ddl}" for name, ddl in corpus._CASES_COLUMN_DDL.items() if name != "vided_amicus"
    )
    legacy.executescript(
        f"CREATE TABLE cases ({columns});\n"
        "INSERT INTO cases (case_id, court, docket_number) VALUES "
        "('scotus/1', 'scotus', '26-1');"
    )
    legacy.commit()
    legacy.close()
    with corpus.connect(pre) as conn:
        migrated = corpus.get_row(conn, "scotus/1")
        assert migrated is not None and migrated.vided_amicus is None
        corpus.upsert_rows(conn, [_row("scotus/1", "26-1", ["2026-09-14|a"])])
        # A poll that discloses no proceedings carries no keys and keeps them.
        corpus.upsert_rows(conn, [_row("scotus/1", "26-1", None)])
        kept = corpus.get_row(conn, "scotus/1")
        assert kept is not None and kept.vided_amicus == ["2026-09-14|a"]
        corpus.upsert_rows(conn, [_row("scotus/1", "26-1", ["2026-09-14|a", "2026-09-15|b"])])
        grown = corpus.get_row(conn, "scotus/1")
    assert grown is not None and grown.vided_amicus == ["2026-09-14|a", "2026-09-15|b"]


def test_companions_are_the_dockets_sharing_a_key_most_shared_first(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/193", "26-193", ["d|a", "d|b", "d|c"]),
                _row("scotus/240", "26-240", ["d|a", "d|b", "d|c"]),
                _row("scotus/300", "26-300", ["d|c"]),
                _row("scotus/400", "26-400", ["d|z"]),
                _row("scotus/500", "26-500", None),
            ],
        )
        conn.commit()
    with corpus.connect_readonly(db) as conn:
        found = corpus.vided_companions(conn, ["d|a", "d|b", "d|c"], own_case="scotus/193")
        assert found is not None
        assert [(c.case_id, c.docket_number, c.shared) for c in found] == [
            ("scotus/240", "26-240", ("d|a", "d|b", "d|c")),
            ("scotus/300", "26-300", ("d|c",)),
        ]
        # A cell placed before the third brief asks about the first two only.
        early = corpus.vided_companions(conn, ["d|a"], own_case="scotus/193")
        assert [c.case_id for c in early or []] == ["scotus/240"]
        assert corpus.vided_companions(conn, [], own_case="scotus/500") == []


def test_the_column_is_withheld_from_the_retrieval_surface() -> None:
    assert "vided_amicus" in corpus.RETRIEVAL_WITHHELD_COLUMNS
    assert "vided_amicus" not in corpus.prior_payload(_row("scotus/1", "26-1", ["d|a"]))


def test_companions_are_scotus_dockets_only_and_need_the_index(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/193", "26-193", ["d|a"]),
                corpus.CorpusRow(
                    case_id="ca4/1", court="ca4", docket_number="25-1574", vided_amicus=["d|a"]
                ),
            ],
        )
        conn.commit()
    with corpus.connect_readonly(db) as conn:
        assert corpus.vided_companions(conn, ["d|a"], own_case="scotus/193") == []
        plan = " ".join(
            str(row[3])
            for row in conn.execute(
                "EXPLAIN QUERY PLAN SELECT case_id, docket_number, vided_amicus FROM cases "
                "WHERE court = 'scotus' AND vided_amicus IS NOT NULL"
            )
        )
        assert corpus.VIDED_AMICUS_INDEX in plan
    with corpus.connect(db) as conn:
        conn.execute(f"DROP INDEX {corpus.VIDED_AMICUS_INDEX}")
        # A blob without the index answers "not looked up", never "none".
        assert corpus.vided_companions(conn, ["d|a"], own_case="scotus/193") is None
