"""The VIDED keys: how a companion the Court never linked as ``Vide`` is found.

One filing serving two petitions is entered on each docket and marked
``VIDED``. :mod:`fedcourtsai.pipeline.vided` reads each such entry as a key (an
amicus brief by its day and filer, a party filing by its day and the case
below), the live poll writes a docket's keys to the corpus, and
:func:`fedcourtsai.corpus.vided_companions` finds the dockets sharing one.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row
from fedcourtsai.pipeline.vided import (
    VIDED_AMICUS_RELATION,
    VIDED_PARTY_RELATION,
    companion_relation,
    is_party_key,
    lower_cases,
    vided_key,
    vided_keys,
    vided_party_keys,
)

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


#: One consolidated opposition as the Clerk words it on each of two dockets.
_OPPOSITION_ONE = ("Oct 30 2026", "Brief of respondent Jane Roe in opposition filed.  VIDED.")
_OPPOSITION_TWO = (
    "Oct 30 2026",
    "Brief of respondents Jane Roe, et al. in opposition filed.  VIDED.",
)
_BELOW = {
    "LowerCourt": "United States Court of Appeals for the Second Circuit",
    "LowerCourtCaseNumbers": "(24-644)",
}


def test_the_case_below_reads_one_entry_per_number_and_none_without_a_court() -> None:
    assert lower_cases(_BELOW) == ["united states court of appeals for the second circuit|24 644"]
    several = {**_BELOW, "LowerCourtCaseNumbers": "(24-644, 24-701; 24-644)"}
    assert [case.rsplit("|", 1)[1] for case in lower_cases(several)] == ["24 644", "24 701"]
    assert lower_cases({"LowerCourtCaseNumbers": "(24-644)"}) == []
    assert lower_cases({"LowerCourt": "A Court", "LowerCourtCaseNumbers": None}) == []


def test_a_vided_party_filing_keys_on_its_day_and_the_case_below() -> None:
    below = lower_cases(_BELOW)
    # The two wordings of one opposition read as the same key.
    one = vided_party_keys(_OPPOSITION_ONE[1], _OPPOSITION_ONE[0], below)
    two = vided_party_keys(_OPPOSITION_TWO[1], _OPPOSITION_TWO[0], below)
    assert one == two == ["2026-10-30|united states court of appeals for the second circuit|24 644"]
    assert all(is_party_key(key) for key in one)
    # The same number in another court, and the same case on another day, do not match.
    elsewhere = lower_cases({**_BELOW, "LowerCourt": "Supreme Court of Ohio"})
    assert not set(vided_party_keys(_OPPOSITION_ONE[1], _OPPOSITION_ONE[0], elsewhere)) & set(one)
    assert not set(vided_party_keys(_OPPOSITION_ONE[1], "Oct 31 2026", below)) & set(one)


def test_only_a_dated_vided_filing_that_is_not_an_amicus_one_is_a_party_key() -> None:
    below = lower_cases(_BELOW)
    assert vided_party_keys("Brief of respondent in opposition filed.", "Oct 30 2026", below) == []
    # An amicus filing has its own key and the Court's own action is not a filing.
    assert vided_party_keys(_SAMARITAN[1], _SAMARITAN[0], below) == []
    assert vided_party_keys("SET FOR ARGUMENT on Monday. VIDED.", "Oct 30 2026", below) == []
    # The Court's action on a filed motion says "filed" and keys as the motion does.
    granted = "Motion to dispense with printing filed by petitioner GRANTED. VIDED."
    assert len(vided_party_keys(granted, "Oct 30 2026", below)) == 1
    assert vided_party_keys(_OPPOSITION_ONE[1], None, below) == []
    assert vided_party_keys(_OPPOSITION_ONE[1], "Oct 2026", below) == []
    # No case below, no key: the text alone is not one.
    assert vided_party_keys(_OPPOSITION_ONE[1], _OPPOSITION_ONE[0], []) == []


def test_a_companions_relation_and_strength_count_filings() -> None:
    amicus = vided_key(_SAMARITAN[1], _SAMARITAN[0])
    assert amicus is not None and not is_party_key(amicus)
    assert companion_relation([amicus]) == (VIDED_AMICUS_RELATION, 1)
    # One opposition on a consolidated appeal shares two keys and is one filing.
    several = lower_cases({**_BELOW, "LowerCourtCaseNumbers": "(24-644, 24-701)"})
    party = vided_party_keys(_OPPOSITION_ONE[1], _OPPOSITION_ONE[0], several)
    assert len(party) == 2
    assert companion_relation(party) == (VIDED_PARTY_RELATION, 1)
    assert companion_relation([*party, amicus]) == (VIDED_PARTY_RELATION, 2)


def test_a_dockets_keys_carry_both_kinds() -> None:
    keys = vided_keys({**_payload(_SAMARITAN, _OPPOSITION_ONE, _PLAIN), **_BELOW})
    assert keys is not None
    assert [is_party_key(key) for key in keys] == [False, True]
    # Without a case below the opposition keys nothing.
    assert vided_keys(_payload(_OPPOSITION_ONE)) is None
    other = vided_keys({**_payload(_OPPOSITION_TWO, number="26-142"), **_BELOW})
    assert other is not None and set(other) & set(keys)


def test_a_dockets_keys_are_sorted_and_unrepeated() -> None:
    keys = vided_keys(_payload(_SAMARITAN, _PLAIN, _ACLJ, _SAMARITAN))
    assert keys is not None
    assert keys == sorted(keys)
    assert len(keys) == 2


def test_no_vided_entry_and_no_proceedings_both_read_none() -> None:
    assert vided_keys(_payload(_PLAIN)) is None
    assert vided_keys({"CaseNumber": "26-193 "}) is None


def test_the_live_cert_branch_writes_the_keys_at_ingest() -> None:
    payload = _payload(_SAMARITAN, _PLAIN)
    row = to_corpus_row(from_live_record(map_live_docket(payload, 9026000193, form="cert")))
    assert row.vided_amicus == vided_keys(payload)
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


def test_the_party_census_counts_the_pairs_only_the_party_key_finds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = Path(__file__).resolve().parents[1] / "scripts" / "checks" / "vided_party_census.py"
    spec = importlib.util.spec_from_file_location("_census_check_vided_party", path)
    assert spec is not None and spec.loader is not None
    census = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, census)
    spec.loader.exec_module(census)

    linked = {"RelatedCaseNumber": [{"DisplayCaseNumber": "26-4", "RelatedType": "Vide"}]}
    dockets = {
        # One opposition worded for each docket, no link: the pair to find.
        "scotus/1": ("26-1", "24-644", _payload(_OPPOSITION_ONE, number="26-1"), None),
        "scotus/2": ("26-2", "24-644, 24-701", _payload(_OPPOSITION_TWO, number="26-2"), None),
        # The same shape, linked by the Court on one of the two dockets.
        "scotus/3": ("26-3", "24-900", {**_payload(_OPPOSITION_ONE, number="26-3"), **linked}, 1),
        "scotus/4": ("26-4", "24-900", _payload(_OPPOSITION_ONE, number="26-4"), 1),
        # Shares a number with no other docket, so it is never read.
        "scotus/5": ("26-5", "24-555", _payload(_OPPOSITION_ONE, number="26-5"), None),
    }
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=number,
                    originating_docket_number=lower,
                    last_live_polled=date(2026, 11, 18),
                    date_cert_denied=date(2026, 11, 2) if decided else None,
                    disposition="denied" if decided else None,
                )
                for case_id, (number, lower, _, decided) in dockets.items()
            ],
        )
        for case_id, (_, lower, payload, _) in dockets.items():
            below = {**_BELOW, "LowerCourtCaseNumbers": f"({lower})"}
            corpus.upsert_snapshot(conn, case_id, date(2026, 11, 18), {**payload, **below})
    with corpus.connect_readonly(db) as conn:
        counted = census.run_census(conn, 23, 26)
    assert (counted.read, counted.no_snapshot, counted.keyed) == (4, 0, 4)
    assert sorted(counted.pairs) == [("26-1", "26-2"), ("26-3", "26-4")]
    assert (counted.vide, counted.amicus) == (1, 0)
    assert counted.only == [("26-1", "26-2")]
    assert sorted(counted.undecided) == ["26-1", "26-2"]
    text = census.render(counted, 23, 26)
    assert "pairs only the party key finds: 1" in text and "Jane Roe" not in text
