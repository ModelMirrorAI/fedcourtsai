"""The staged snapshot's contact scrub removes values nothing scored or analytic reads.

Two halves, because "nothing reads it" is two claims. The **source** half scans
the package for any code naming a withheld key, so a reader added later fails
here rather than silently scoring a placeholder. The **behavioural** half runs
every function that turns a snapshot payload into something scored, banded,
counted or read by a cell — the corpus row every analytic reads (the statpack,
salience and its bands, the party census and the metrics all sit on it), the
cell context, the forward-leakage gate, the live probe, the backtest redaction
and the scrub trigger itself — on the payload and on its scrubbed copy, and
asserts the outputs are identical. Provisioning itself hands every one of
those the payload as served and writes only the scrubbed copy, so the
behavioural half guards the day one of them is pointed at the staged copy; the
source half guards the day a new reader names a withheld key.
"""

from __future__ import annotations

import ast
import copy
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from fedcourtsai import cert_backtest
from fedcourtsai.pipeline import cell_context, ingest, liveprobe, outcome, salience
from fedcourtsai.pipeline.documents import (
    CONTACT_PLACEHOLDER,
    REGISTER_NUMBER_WITHHELD,
    SNAPSHOT_CONTACT_FIELDS,
    scrub_snapshot_contacts,
    unrepresented_sides,
)

WITHHELD_KEYS = (*SNAPSHOT_CONTACT_FIELDS, "PrisonerId")


def _payload() -> dict[str, Any]:
    """A self-represented, incarcerated petitioner's docket as the Court serves it."""
    return {
        "CaseNumber": "25-5123 ",
        "bCapitalCase": False,
        "sJsonCaseType": "IFP",
        "sJsonTerm": "2025",
        "sJsonCreationDate": "07/10/2026",
        "DocketedDate": "June 2, 2026",
        "PetitionerTitle": "John Q. Doe, Petitioner",
        "RespondentTitle": "Warden Roe, Respondent",
        "LowerCourt": "United States Court of Appeals for the Fifth Circuit",
        "LowerCourtCaseNumbers": "(24-10001)",
        "Petitioner": [
            {
                "Attorney": "John Doe",
                "IsCounselofRecord": True,
                "Title": None,
                "PrisonerId": "#01234567",
                "Phone": "(936) 555-0147",
                "Address": "Coffield Unit, 2661 FM 2054",
                "City": "Tennessee Colony",
                "State": "TX",
                "Zip": "75884",
                "Email": "jdoe.petitioner@example.com",
                "PartyName": "John Q. Doe",
            }
        ],
        "Respondent": [
            {
                "Attorney": "Ann Counsel",
                "IsCounselofRecord": True,
                "Title": "Solicitor General",
                "PrisonerId": None,
                "Phone": "(512) 555-0100",
                "Address": "P.O. Box 12548",
                "City": "Austin",
                "State": "TX",
                "Zip": "78711",
                "Email": "counsel@example.gov",
                "PartyName": "Warden Roe",
            }
        ],
        "ProceedingsandOrder": [
            {
                "Date": "Jun 01 2026",
                "Text": "Petition for a writ of certiorari and motion for leave to proceed "
                + "in forma pauperis filed.",
                "Links": [
                    {"Description": "Petition", "DocumentUrl": "https://www.supremecourt.gov/p.pdf"}
                ],
            },
            {"Date": "Jul 01 2026", "Text": "DISTRIBUTED for Conference of 9/28/2026."},
        ],
    }


def test_the_scrub_withholds_every_contact_value_and_keeps_what_is_read() -> None:
    payload = _payload()

    scrubbed = scrub_snapshot_contacts(payload)

    block = scrubbed.payload["Petitioner"][0]
    for key in ("Address", "City", "Zip", "Phone", "Email"):
        assert block[key] == CONTACT_PLACEHOLDER
    assert block["Title"] is None  # empty as served, so empty as staged
    # The register number's presence survives as a fixed marker; the number goes.
    assert block["PrisonerId"] == REGISTER_NUMBER_WITHHELD
    assert block["PartyName"] == "John Q. Doe"
    assert block["Attorney"] == "John Doe"
    assert block["State"] == "TX"
    assert scrubbed.blocks == 1
    assert scrubbed.fields == 6
    # The represented side's block is the payload's own object, untouched.
    assert scrubbed.payload["Respondent"] == payload["Respondent"]
    assert scrubbed.payload["Respondent"][0] is payload["Respondent"][0]
    # The caller's payload is never mutated.
    assert payload == _payload()


def test_no_withheld_value_survives_anywhere_in_the_staged_payload() -> None:
    payload = _payload()
    personal = [payload["Petitioner"][0][key] for key in WITHHELD_KEYS]
    personal = [value for value in personal if value]

    staged = repr(scrub_snapshot_contacts(payload).payload)

    for value in personal:
        assert value not in staged


def test_a_represented_petitioner_block_is_left_as_served() -> None:
    payload = _payload()
    payload["Petitioner"][0]["Attorney"] = "Kannon K. Shanmugam"
    payload["Petitioner"][0]["PrisonerId"] = None

    scrubbed = scrub_snapshot_contacts(payload)

    assert scrubbed.payload == payload
    assert scrubbed.blocks == 0
    assert scrubbed.fields == 0


def test_only_the_self_represented_block_of_several_is_scrubbed() -> None:
    payload = _payload()
    counsel = {
        "Attorney": "Kannon K. Shanmugam",
        "PartyName": "Richard Doe",
        "Email": "ks@firm.example.com",
        "Phone": "(202) 555-0199",
    }
    payload["Petitioner"].append(counsel)

    scrubbed = scrub_snapshot_contacts(payload)

    assert scrubbed.payload["Petitioner"][1] == counsel
    assert scrubbed.payload["Petitioner"][0]["Email"] == CONTACT_PLACEHOLDER


@pytest.mark.parametrize("empty", [None, "", "  "])
def test_an_empty_key_stays_empty(empty: str | None) -> None:
    payload = _payload()
    for key in WITHHELD_KEYS:
        payload["Petitioner"][0][key] = empty

    scrubbed = scrub_snapshot_contacts(payload)

    block = scrubbed.payload["Petitioner"][0]
    assert all(block[key] == empty for key in WITHHELD_KEYS)
    assert scrubbed.fields == 0


def test_a_free_text_title_is_withheld_with_the_contact_keys() -> None:
    # Upstream sometimes files an inmate number under `Title` rather than
    # `PrisonerId`; nothing reads the key, so a populated one is withheld.
    payload = _payload()
    payload["Petitioner"][0]["Title"] = "195949"

    scrubbed = scrub_snapshot_contacts(payload)

    assert scrubbed.payload["Petitioner"][0]["Title"] == CONTACT_PLACEHOLDER
    assert scrubbed.fields == 7


def _pro_se_respondent() -> dict[str, Any]:
    """A self-represented respondent's block, as the Court serves one."""
    return {
        "Attorney": "Richard Roe",
        "IsCounselofRecord": True,
        "Title": None,
        "PrisonerId": None,
        "Phone": "(936) 555-0199",
        "Address": "Route 2, 4417 County Road 12",
        "City": "Tennessee Colony",
        "State": "TX",
        "Zip": "75884",
        "Email": "rroe.respondent@example.com",
        "PartyName": "Richard Roe",
    }


def test_a_self_represented_respondent_block_is_scrubbed_like_a_petitioners() -> None:
    payload = _payload()
    payload["Petitioner"][0]["Attorney"] = "Kannon K. Shanmugam"
    payload["Petitioner"][0]["PrisonerId"] = None
    payload["Respondent"].append(_pro_se_respondent())

    scrubbed = scrub_snapshot_contacts(payload)

    block = scrubbed.payload["Respondent"][1]
    for key in ("Address", "City", "Zip", "Phone", "Email"):
        assert block[key] == CONTACT_PLACEHOLDER
    assert block["Title"] is None
    assert block["PrisonerId"] is None
    assert block["PartyName"] == block["Attorney"] == "Richard Roe"
    assert block["State"] == "TX"
    assert scrubbed.blocks == 1
    assert scrubbed.fields == 5
    # The respondent's represented co-party and the counselled petitioner are
    # the payload's own objects, untouched.
    assert scrubbed.payload["Respondent"][0] is payload["Respondent"][0]
    assert scrubbed.payload["Petitioner"][0] is payload["Petitioner"][0]
    assert payload["Respondent"][1] == _pro_se_respondent()


def test_a_represented_respondent_block_is_left_as_served() -> None:
    payload = _payload()

    scrubbed = scrub_snapshot_contacts(payload)

    assert scrubbed.payload["Respondent"] == payload["Respondent"]
    assert scrubbed.payload["Respondent"][0] is payload["Respondent"][0]
    assert scrubbed.payload["Respondent"][0]["Email"] == "counsel@example.gov"


def test_both_sides_self_represented_are_both_scrubbed() -> None:
    payload = _payload()
    payload["Respondent"] = [_pro_se_respondent()]

    scrubbed = scrub_snapshot_contacts(payload)

    assert scrubbed.blocks == 2
    assert scrubbed.fields == 6 + 5
    staged = repr(scrubbed.payload)
    for value in (*_pro_se_respondent().values(), *payload["Petitioner"][0].values()):
        if isinstance(value, str) and value not in {"Richard Roe", "John Doe", "John Q. Doe", "TX"}:
            assert value not in staged


def test_the_staged_snapshot_is_a_fixed_point() -> None:
    # Scrubbing the staged copy again changes nothing: the placeholders and the
    # register number's marker keep each block qualifying and are themselves
    # what a second pass would write.
    payload = _payload()
    payload["Respondent"].append(_pro_se_respondent())

    once = scrub_snapshot_contacts(payload).payload
    twice = scrub_snapshot_contacts(once).payload

    assert twice == once
    assert unrepresented_sides(once) == ("Petitioner", "Respondent")


def test_a_payload_serving_no_petitioner_block_is_an_equal_copy() -> None:
    payload = {"docket_entries": [{"description": "Petition filed."}]}

    scrubbed = scrub_snapshot_contacts(payload)

    assert scrubbed.payload == payload
    assert scrubbed.fields == 0


# --- nothing scored or analytic reads what was withheld ---------------------


def test_every_scored_and_analytic_reading_of_the_payload_is_unchanged() -> None:
    payload = _payload()
    staged = scrub_snapshot_contacts(copy.deepcopy(payload)).payload
    assert staged != payload  # the scrub did withhold something

    # The corpus row every analytic reads: the statpack, salience and its bands,
    # the party census and the metrics all sit on it, not on the payload.
    row = ingest.from_live_docket(payload, 9_025_005_123)
    staged_row = ingest.from_live_docket(staged, 9_025_005_123)
    assert staged_row.model_dump() == row.model_dump()
    stored = ingest.to_corpus_row(row, last_pulled=date(2026, 7, 10))
    staged_stored = ingest.to_corpus_row(staged_row, last_pulled=date(2026, 7, 10))
    assert staged_stored.model_dump() == stored.model_dump()
    assert salience.salience_band(staged_stored) == salience.salience_band(stored)

    # What the cell reads beside the snapshot, and the gates provisioning runs.
    for mode in ("forward", "replay"):
        assert cell_context.build(
            "scotus/9025005123", date(2026, 7, 10), staged, mode
        ) == cell_context.build("scotus/9025005123", date(2026, 7, 10), payload, mode)
    assert outcome.forward_leakage(staged, "scotus", "evt-cert-petition") == (
        outcome.forward_leakage(payload, "scotus", "evt-cert-petition")
    )
    assert liveprobe.classify_record(25, 5123, staged) == liveprobe.classify_record(
        25, 5123, payload
    )
    # The backtest's redaction drops the counsel blocks wholesale.
    assert cert_backtest.redact_snapshot(copy.deepcopy(staged)) == (
        cert_backtest.redact_snapshot(copy.deepcopy(payload))
    )
    # And the scrub trigger reads the same docket either way: the register
    # number's marker keeps the block reading as self-represented.
    assert unrepresented_sides(staged) == unrepresented_sides(payload) == ("Petitioner",)


def _key_literals(tree: ast.AST) -> set[str]:
    """Every string constant in a module, docstrings excluded."""
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                docstrings.add(id(body[0].value))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    }


def _imported_names(tree: ast.AST) -> set[str]:
    """Every name a module imports from anywhere."""
    return {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }


def test_no_code_outside_the_scrub_names_a_withheld_key() -> None:
    # The source half, over every module of the package. A module that names a
    # withheld key as a string literal could read it — upstream spells the keys
    # in one casing, so an exact match is the one a reader would use — and so could
    # one that imports the scrub's key list. Only `pipeline/documents.py` — the
    # scrub, and the trigger that reads the register number's presence — may.
    # `City` is also an institution word in the short caption's word list, which
    # names no payload key; that module is allowed that one word and nothing
    # else. What this cannot see is a reader that walks a block generically; the
    # one such reader of the staged file is the case-summary prompt renderer,
    # whose recipient is meant to read the scrubbed copy.
    keys = set(WITHHELD_KEYS)
    exports = {"SNAPSHOT_CONTACT_FIELDS", "REGISTER_NUMBER_WITHHELD", "scrub_snapshot_contacts"}
    allowed = {"short_caption.py": {"City"}}
    package = Path(cert_backtest.__file__).parent
    offenders: dict[str, set[str]] = {}
    for path in sorted(package.rglob("*.py")):
        rel = path.relative_to(package).as_posix()
        if rel == "pipeline/documents.py":
            continue
        tree = ast.parse(path.read_text())
        named = (_key_literals(tree) & keys) - allowed.get(rel, set())
        named |= _imported_names(tree) & exports - (
            {"scrub_snapshot_contacts"} if rel == "cli.py" else set()
        )
        if named:
            offenders[rel] = named
    assert offenders == {}
