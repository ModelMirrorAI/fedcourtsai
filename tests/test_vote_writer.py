"""The vote writer: order and opinion readings stamped onto committed outcomes.

Offline throughout: the Court's pages are served by an ``httpx.MockTransport``
and PDF extraction is stubbed to decode the bytes, so each document is the
fixture text the reader tests already pin (``tests/test_order_lineups.py``,
``tests/test_opinion_lineups.py``). The corpus is a one-table SQLite file
holding only what the writer reads from it: each case's docket number.
"""

from __future__ import annotations

import dataclasses
import json
import sqlite3
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, get_args

import httpx
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture, vote_writer
from fedcourtsai.cli import app
from fedcourtsai.handoff import HandoffRefused, read_handoff, write_handoff
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import opinion_lineups, order_lineups, vote_sources
from fedcourtsai.pipeline.base_rates import PER_CURIAM_LABEL
from fedcourtsai.pipeline.documents import ExtractedText
from fedcourtsai.pipeline.opinion_lineups import OpinionFetcher
from fedcourtsai.pipeline.order_lineups import OrderDocketReading, OrderFetcher, OrderPartReading
from fedcourtsai.pipeline.vote_sources import is_opinion_pdf
from fedcourtsai.schemas import (
    Disposition,
    EventKind,
    GrammarStamp,
    Judgment,
    JusticeVote,
    JusticeWriting,
    Outcome,
    PredictableEvent,
    Stage,
    VoteProvenance,
    VoteValue,
    WritingRole,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.supremecourt import SupremeCourtClient
from fedcourtsai.validate import CHECK_OUTCOME_VOTES_HELD, run_ledger_referential_checks
from fedcourtsai.vote_writer import (
    SETTLING_DAYS,
    VoteWriteResult,
    order_record,
    stamp_opinion_votes,
    stamp_order_votes,
)
from tests.test_opinion_lineups import LISTING, SLIP
from tests.test_order_lineups import ORDER_LIST, ORDERS_PAGE, RELATING, RELATING_PAGE

DAY = date(2026, 6, 22)
LATER = date(2026, 9, 30)

#: Ledger docket ids and the Court's docket numbers they stand for.
CERT = {
    1: "25-885",  # Carter: Thomas and Alito would grant; Alito dissents in writing
    2: "25-1309",  # Carr: Alito took no part
    3: "25-7457",  # denied, nothing noted: roles only
    4: "25-9999",  # named in no document for the date
}


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> SupremeCourtClient:
    return SupremeCourtClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)), sleep=lambda _s: None
    )


def _stub_extraction(monkeypatch: pytest.MonkeyPatch, module: object) -> None:
    def extract(data: bytes, *, char_cap: int) -> ExtractedText:
        text = data.decode()
        return ExtractedText(text=text[:char_cap], pages=1, truncated=len(text) > char_cap)

    monkeypatch.setattr(module, "extract_pdf_text", extract)


def _corpus(tmp_path: Path, numbers: dict[int, str]) -> sqlite3.Connection:
    conn = sqlite3.connect(tmp_path / "corpus.db")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE cases (case_id TEXT PRIMARY KEY, docket_number TEXT)")
    conn.executemany(
        "INSERT INTO cases VALUES (?, ?)",
        [(f"scotus/{docket}", number) for docket, number in numbers.items()],
    )
    return conn


def _outcome(
    data_root: Path,
    docket: int,
    *,
    event_id: str = "evt-petition-disposition",
    stage: Stage | None = Stage.cert,
    resolved_at: date = DAY,
) -> Path:
    ep = CasePaths(data_root, "scotus", docket).event(event_id)
    merits = stage is Stage.merits
    write_yaml(
        ep.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=f"scotus/{docket}",
            kind=EventKind.order if merits else EventKind.petition,
            stage=stage,
            title="Doe v. Roe",
            decision_target="judgment" if merits else "disposition",
        ),
    )
    write_json(
        ep.outcome,
        Outcome(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            resolved_at=resolved_at,
            actual_disposition=Disposition.other if merits else Disposition.denied,
            actual_granted=1 if merits else 0,
            judgment=Judgment.reversed if merits else None,
        ),
    )
    return ep.outcome


def _orders_handler(requested: list[str]) -> Callable[[httpx.Request], httpx.Response]:
    def handle(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path == "/orders/ordersofthecourt/25":
            return httpx.Response(200, text=ORDERS_PAGE)
        if request.url.path == "/opinions/relatingtoorders/25":
            return httpx.Response(200, text=RELATING_PAGE)
        if request.url.path.endswith("062226zor_g314.pdf"):
            return httpx.Response(200, content=ORDER_LIST.encode())
        if request.url.path.endswith("25-885_5h26.pdf"):
            return httpx.Response(200, content=RELATING.encode())
        return httpx.Response(404)

    return handle


def _cert_ledger(tmp_path: Path) -> tuple[Path, sqlite3.Connection]:
    data_root = tmp_path / "data"
    for docket in CERT:
        _outcome(data_root, docket)
    return data_root, _corpus(tmp_path, CERT)


def _stamp_orders(
    data_root: Path,
    conn: sqlite3.Connection,
    requested: list[str],
    *,
    today: date = LATER,
    apply: bool,
    max_stamps: int | None = None,
    replace_differing: bool = False,
) -> VoteWriteResult:
    with _client(_orders_handler(requested)) as client:
        return stamp_order_votes(
            conn,
            data_root,
            OrderFetcher(client),
            today=today,
            terms=(2025,),
            apply=apply,
            max_stamps=max_stamps,
            replace_differing=replace_differing,
        )


def _votes_hold(data_root: Path) -> list[str]:
    check = next(
        c for c in run_ledger_referential_checks(data_root) if c.name == CHECK_OUTCOME_VOTES_HELD
    )
    return list(check.problems)


# --- the orders pass -------------------------------------------------------------


def test_the_orders_dry_run_plans_each_outcome_and_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    before = {p: p.read_text() for p in data_root.rglob("outcome.json")}
    requested: list[str] = []
    result = _stamp_orders(data_root, conn, requested, apply=False)
    assert {p: p.read_text() for p in data_root.rglob("outcome.json")} == before
    stamps = {s.target.case_id: s.record for s in result.stamps}
    assert set(stamps) == {"scotus/1", "scotus/2", "scotus/3"}

    carter = stamps["scotus/1"]
    assert [(v.justice, v.vote, v.writing) for v in carter.votes] == [
        ("Thomas", VoteValue.grant, WritingRole.none),
        ("Alito", VoteValue.grant, WritingRole.dissent),
    ]
    assert carter.provenance is not None and carter.provenance.complete is False
    assert carter.provenance.participating == 9
    assert sorted(g.grammar for g in carter.provenance.grammars) == [
        "scotus-order-notations",
        "scotus-writing-headers",
    ]
    assert len(carter.provenance.documents) == 2
    assert carter.writing_roles is not None and len(carter.writing_roles) == 9

    carr = stamps["scotus/2"]
    assert [(v.justice, v.vote) for v in carr.votes] == [("Alito", VoteValue.did_not_participate)]
    assert carr.provenance is not None and carr.provenance.participating == 8
    assert carr.writing_roles is not None
    assert "Alito" not in {r.justice for r in carr.writing_roles}

    roles_only = stamps["scotus/3"]
    assert roles_only.votes == ()
    assert roles_only.writing_roles is not None
    assert {r.writing for r in roles_only.writing_roles} == {WritingRole.none}
    assert result.skipped == [
        (
            "scotus/4/evt-petition-disposition",
            "not named in the date's documents: 25-9999 on 2026-06-22",
        )
    ]


def test_an_applied_orders_stamp_validates_and_a_rerun_is_a_no_op(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    applied = _stamp_orders(data_root, conn, [], apply=True, max_stamps=3)
    assert applied.applied and len(applied.stamps) == 3
    carter = read_model(
        CasePaths(data_root, "scotus", 1).event("evt-petition-disposition").outcome, Outcome
    )
    assert carter.vote_provenance is not None and carter.writing_roles is not None
    assert carter.actual_disposition == Disposition.denied  # nothing else moved
    assert _votes_hold(data_root) == []

    again = _stamp_orders(data_root, conn, [], apply=False)
    assert again.stamps == []
    assert len(again.unchanged) == 3


def test_an_apply_over_its_bound_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    before = {p: p.read_text() for p in data_root.rglob("outcome.json")}
    result = _stamp_orders(data_root, conn, [], apply=True, max_stamps=2)
    assert result.refused and not result.applied
    assert {p: p.read_text() for p in data_root.rglob("outcome.json")} == before


def test_a_different_record_is_held_back_unless_replacement_is_asked_for(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    path = CasePaths(data_root, "scotus", 1).event("evt-petition-disposition").outcome
    held = read_model(path, Outcome).model_copy(
        update={
            "votes": [JusticeVote(justice="Thomas", vote=VoteValue.grant)],
            "vote_provenance": VoteProvenance(
                source="supremecourt-orders", participating=9, complete=False
            ),
        }
    )
    write_json(path, held)
    result = _stamp_orders(data_root, conn, [], apply=False)
    assert "scotus/1/evt-petition-disposition" in dict(result.held_back)
    replaced = _stamp_orders(data_root, conn, [], apply=True, max_stamps=3, replace_differing=True)
    assert [s.replaces for s in replaced.stamps].count(True) == 1
    assert len(read_model(path, Outcome).votes) == 2


def test_a_date_inside_the_settling_window_is_not_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    requested: list[str] = []
    today = date.fromordinal(DAY.toordinal() + SETTLING_DAYS - 1)
    result = _stamp_orders(data_root, conn, requested, today=today, apply=False)
    assert result.stamps == []
    assert all("settling window" in reason for _, reason in result.skipped)
    assert not any(path.endswith(".pdf") for path in requested)
    settled = date.fromordinal(DAY.toordinal() + SETTLING_DAYS)
    assert _stamp_orders(data_root, conn, [], today=settled, apply=False).stamps


def test_a_stage_less_cert_baseline_takes_its_declared_stage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The cert baselines are written with no stage; the moments table names it."""
    _stub_extraction(monkeypatch, order_lineups)
    data_root = tmp_path / "data"
    _outcome(data_root, 1, stage=None)
    conn = _corpus(tmp_path, {1: "25-885"})
    result = _stamp_orders(data_root, conn, [], apply=True, max_stamps=1)
    assert [s.target.stage for s in result.stamps] == ["cert"]
    assert _votes_hold(data_root) == []


def test_an_empty_population_makes_no_request(tmp_path: Path) -> None:
    requested: list[str] = []
    conn = _corpus(tmp_path, {})
    result = _stamp_orders(tmp_path / "data", conn, requested, apply=False)
    assert result.population == 0 and requested == []


def test_an_unreadable_listing_refuses_the_apply(tmp_path: Path) -> None:
    data_root, conn = _cert_ledger(tmp_path)

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    with _client(handle) as client:
        result = stamp_order_votes(
            conn,
            data_root,
            OrderFetcher(client),
            today=LATER,
            terms=(2025,),
            apply=True,
            max_stamps=10,
        )
    assert result.failures and result.refused and not result.applied


def _part(where: str, text: str) -> OrderPartReading:
    return OrderPartReading(
        document="https://www.supremecourt.gov/orders/courtorders/x.pdf",
        where=where,
        grammar="scotus-order-notations",
        grammar_version=1,
        text=text,
    )


def _reading(parts: list[OrderPartReading], **fields: object) -> OrderDocketReading:
    bench = [
        "Thomas",
        "Roberts",
        "Alito",
        "Sotomayor",
        "Kagan",
        "Gorsuch",
        "Kavanaugh",
        "Barrett",
        "Jackson",
    ]
    return OrderDocketReading.model_validate(
        {
            "docket": "25-1",
            "order_date": DAY,
            "documents": ["https://www.supremecourt.gov/orders/courtorders/x.pdf"],
            "bench": bench,
            "writings_complete": False,
            "votes": [{"justice": "Alito", "vote": "did-not-participate"}],
            "writing_roles": {},
            "writings": [],
            "problems": [],
            "parts": [p.model_dump() for p in parts],
        }
        | fields
    )


def test_an_order_record_is_held_back_off_the_cert_or_application_act() -> None:
    """Non-participation is recorded only where it attaches to the disposing act."""
    rehearing = _reading(
        [_part("list-entry", "The petition for rehearing is denied.  Justice Alito took no part.")]
    )
    assert order_record(rehearing) == (None, "the docket's order text mentions a rehearing")
    header_only = _reading([_part("header", "JUSTICE ALITO, dissenting.")])
    assert order_record(header_only)[1] == "only a writing names the docket on the date"
    troubled = _reading(
        [_part("list-entry", "Denied.")], problems=["x is read both as grant and deny"]
    )
    assert order_record(troubled)[1] == "the reading has problems: x is read both as grant and deny"
    silent = _reading([_part("list-entry", "Denied.")], votes=[])
    assert order_record(silent) == (None, None)
    record, why = order_record(_reading([_part("list-entry", "The petition is denied.")]))
    assert why is None and record is not None
    assert record.provenance is not None and record.provenance.participating == 8
    assert record.writing_roles is None


# --- the opinions pass -----------------------------------------------------------

GRANTED_NOTED = """SUPREME COURT OF THE UNITED STATES
GRANTED & NOTED LIST
24-38)  CFX LITTLE V. HECOX
24-43)  CFX WEST VIRGINIA V. B. P. J.
   Court:  USCA-4     Granted:  7/3/25
   Argument Date:  1/13/26   Decided:  6/30/26
   Author:  J. Kavanaugh    Other:  Thomas (C); Gorsuch (C);
          Sotomayor (C/J, D/P); Jackson (C/J, D/P)
   Result:  REVERSED AND REMANDED
"""


def _opinions_handler(requested: list[str]) -> Callable[[httpx.Request], httpx.Response]:
    def handle(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path == "/opinions/slipopinion/25":
            return httpx.Response(200, text=LISTING)
        if request.url.path.endswith("24-43_2b35.pdf"):
            return httpx.Response(200, content=SLIP.encode())
        return httpx.Response(404)

    return handle


def _stamp_opinions(
    data_root: Path,
    conn: sqlite3.Connection,
    granted_noted: str | None,
    *,
    apply: bool,
    max_stamps: int | None = None,
) -> VoteWriteResult:
    with _client(_opinions_handler([])) as client:
        return stamp_opinion_votes(
            conn,
            data_root,
            OpinionFetcher(client),
            lambda _term: granted_noted,
            apply=apply,
            max_stamps=max_stamps,
        )


def _merits_ledger(tmp_path: Path) -> tuple[Path, sqlite3.Connection]:
    data_root = tmp_path / "data"
    for docket in (43, 38):
        _outcome(
            data_root,
            docket,
            event_id="evt-order-judgment",
            stage=Stage.merits,
            resolved_at=date(2026, 6, 30),
        )
    return data_root, _corpus(tmp_path, {43: "24-43", 38: "24-38"})


def test_an_opinion_stamps_its_docket_and_the_consolidated_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The listing prints 24-43 alone; the Granted & Noted entry joins 24-38 to it."""
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root, conn = _merits_ledger(tmp_path)
    result = _stamp_opinions(data_root, conn, GRANTED_NOTED, apply=True, max_stamps=2)
    assert sorted(s.target.case_id for s in result.stamps) == ["scotus/38", "scotus/43"]
    outcome = read_model(
        CasePaths(data_root, "scotus", 38).event("evt-order-judgment").outcome, Outcome
    )
    assert outcome.vote_provenance is not None and outcome.vote_provenance.complete
    assert outcome.writing_roles is not None and len(outcome.writing_roles) == 9
    assert JusticeWriting(justice="Roberts", writing=WritingRole.none) in outcome.writing_roles
    assert _votes_hold(data_root) == []


def test_a_granted_noted_disagreement_holds_the_record_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root, conn = _merits_ledger(tmp_path)
    wrong = GRANTED_NOTED.replace("Gorsuch (C);", "Gorsuch (D);")
    result = _stamp_opinions(data_root, conn, wrong, apply=False)
    # The listing's author still stamps; no vote record does.
    assert result.stamps and all(s.record.provenance is None for s in result.stamps)
    reasons = [reason for _, reason in result.held_back]
    assert reasons and all(r.startswith("Granted & Noted disagrees") for r in reasons)
    assert any("Gorsuch (dissent)" in r for r in reasons)


def test_an_unreadable_granted_noted_list_refuses_the_apply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root, conn = _merits_ledger(tmp_path)
    result = _stamp_opinions(data_root, conn, None, apply=True, max_stamps=5)
    assert result.refused and result.failures
    assert all(s.record.provenance is None for s in result.stamps)


def test_an_opinion_dated_off_the_outcome_is_held_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root = tmp_path / "data"
    _outcome(
        data_root,
        43,
        event_id="evt-order-judgment",
        stage=Stage.merits,
        resolved_at=date(2026, 7, 1),
    )
    result = _stamp_opinions(
        data_root, _corpus(tmp_path, {43: "24-43"}), GRANTED_NOTED, apply=False
    )
    ((_, reason),) = result.held_back
    assert reason.startswith("the opinion's date is not the outcome's")


# --- the commands ----------------------------------------------------------------


@pytest.mark.parametrize("command", ["stamp-order-votes", "stamp-opinion-votes"])
def test_the_commands_refuse_an_unbounded_apply_or_a_cached_one(
    command: str, tmp_path: Path
) -> None:
    runner = CliRunner()
    unbounded = runner.invoke(app, [command, "--apply"])
    cached = runner.invoke(
        app, [command, "--apply", "--max-stamps", "1", "--cache-dir", str(tmp_path)]
    )
    assert (unbounded.exit_code, cached.exit_code) == (2, 2)
    assert "--max-stamps" in unbounded.output
    assert "--cache-dir" in cached.output


def test_writing_roles_cohere_with_the_record() -> None:
    """The schema half: roles need provenance, cover the sitting bench, match votes."""
    base = Outcome(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        resolved_at=DAY,
        actual_disposition=Disposition.denied,
        actual_granted=0,
    ).model_dump(mode="json")
    provenance = {"source": "supremecourt-orders", "participating": 6, "complete": False}
    roles: list[dict[str, object]] = [
        {"justice": name, "writing": "none"}
        for name in ("Thomas", "Roberts", "Sotomayor", "Kagan", "Gorsuch")
    ]
    roles.append({"justice": "Alito", "writing": "dissent"})
    ok = Outcome.model_validate(base | {"vote_provenance": provenance, "writing_roles": roles})
    assert ok.votes == []
    bad = [
        base | {"writing_roles": roles},
        base | {"vote_provenance": provenance, "writing_roles": roles[:5]},
        base | {"vote_provenance": provenance, "writing_roles": [*roles[:5], roles[0]]},
        base
        | {
            "vote_provenance": provenance,
            "writing_roles": roles,
            "votes": [{"justice": "Alito", "vote": "grant", "writing": "none"}],
        },
        base
        | {
            "vote_provenance": provenance,
            "writing_roles": roles,
            "votes": [{"justice": "Alito", "vote": "did-not-participate"}],
        },
    ]
    for payload in bad:
        with pytest.raises(ValueError):
            Outcome.model_validate(payload)
    assert json.loads(ok.model_dump_json())["writing_roles"] == roles


# --- review follow-ups -------------------------------------------------------------


def test_a_petition_grouped_with_an_application_is_held_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """One order disposes of a stay application and a cert petition together.

    Ramey's entry groups `26-5637` with `(26A380)`; a noted vote on the stay
    would otherwise be read onto the petition. Both outcomes are held back.
    """
    _stub_extraction(monkeypatch, order_lineups)
    data_root = tmp_path / "data"
    _outcome(data_root, 5)
    _outcome(data_root, 6, event_id="evt-motion-disposition", stage=Stage.interim)
    conn = _corpus(tmp_path, {5: "26-5637", 6: "26A380"})
    result = _stamp_orders(data_root, conn, [], apply=False)
    assert result.stamps == []
    reasons = dict(result.held_back)
    assert reasons["scotus/5/evt-petition-disposition"].startswith(
        "the docket shares its order or a writing with a docket of the other stage"
    )
    assert "scotus/6/evt-motion-disposition" in reasons


def test_a_record_the_ledger_check_would_refuse_is_held_back(tmp_path: Path) -> None:
    """The writer runs validate's per-record check before it plans a stamp."""
    data_root = tmp_path / "data"
    path = _outcome(data_root, 1)
    target = vote_writer.OutcomeTarget(
        path, "scotus/1", "evt-petition-disposition", "cert", read_model(path, Outcome)
    )
    record = vote_writer.VoteRecord(
        votes=(JusticeVote(justice="Alito", vote=VoteValue.grant),),
        # Nine sat on the order's date and none is recorded absent.
        provenance=VoteProvenance(
            source="supremecourt-orders",
            documents=["https://www.supremecourt.gov/orders/courtorders/x.pdf"],
            grammars=[GrammarStamp(grammar="scotus-order-notations", version=1)],
            participating=8,
            complete=False,
        ),
        writing_roles=None,
    )
    result = vote_writer.VoteWriteResult(source="supremecourt-orders")
    vote_writer._classify(target, record, result, replace_differing=False)
    assert result.stamps == []
    ((_, reason),) = result.held_back
    assert reason.startswith("the record departs from its source's registration")
    assert "`participating` is 8" in reason


def test_a_dockets_own_listing_row_is_never_replaced_by_a_group_mates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Where the listing prints a row for the docket, only that row is read."""
    _stub_extraction(monkeypatch, opinion_lineups)
    per_curiam = (
        "<tr><td>69</td><td>6/30/26</td><td>24-38</td>"
        + "<td><a href='/opinions/25pdf/24-38_pc.pdf'>Little v. Hecox</a></td>"
        + "<td>PC</td><td><span>609/3</span></td></tr></table>"
    )
    listing = LISTING.replace("</table>", per_curiam)

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/opinions/slipopinion/25":
            return httpx.Response(200, text=listing)
        if request.url.path.endswith("24-43_2b35.pdf"):
            return httpx.Response(200, content=SLIP.encode())
        return httpx.Response(404)

    data_root, conn = _merits_ledger(tmp_path)
    with _client(handle) as client:
        result = stamp_opinion_votes(
            conn, data_root, OpinionFetcher(client), lambda _t: GRANTED_NOTED, apply=False
        )
    voted = [s.target.case_id for s in result.stamps if s.record.provenance is not None]
    assert voted == ["scotus/43"]
    authors = {s.target.case_id: s.record.merits_author for s in result.stamps}
    assert authors["scotus/38"] == "per-curiam"
    assert dict(result.votes_unread)["scotus/38/evt-order-judgment"].startswith(
        "the listing's opinion is not read: per curiam"
    )


def test_an_author_only_stamp_round_trips_through_the_plan(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A per curiam row's author reaches the outcome through the plan, with no votes."""
    _stub_extraction(monkeypatch, opinion_lineups)
    per_curiam = (
        "<tr><td>69</td><td>6/30/26</td><td>24-38</td>"
        + "<td><a href='/opinions/25pdf/24-38_pc.pdf'>Little v. Hecox</a></td>"
        + "<td>PC</td><td><span>609/3</span></td></tr></table>"
    )
    listing = LISTING.replace("</table>", per_curiam)

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/opinions/slipopinion/25":
            return httpx.Response(200, text=listing)
        if request.url.path.endswith("24-43_2b35.pdf"):
            return httpx.Response(200, content=SLIP.encode())
        return httpx.Response(404)

    data_root, conn = _merits_ledger(tmp_path)
    with _client(handle) as client:
        dry = stamp_opinion_votes(
            conn, data_root, OpinionFetcher(client), lambda _t: GRANTED_NOTED, apply=False
        )
    plan_file = tmp_path / "plan.json"
    write_handoff(plan_file, vote_writer.vote_plan(dry))
    split = vote_writer.apply_vote_plan(
        read_handoff(plan_file, vote_writer.VoteStampPlan),
        data_root,
        source="supremecourt-opinions",
        today=LATER,
        apply=True,
        max_stamps=2,
    )
    assert split.applied and len(split.stamps) == 2
    paths = CasePaths(data_root, "scotus", 38).event("evt-order-judgment")
    outcome = read_model(paths.outcome, Outcome)
    assert outcome.merits_author == "per-curiam"
    assert outcome.vote_provenance is None and not outcome.votes
    signed = read_model(
        CasePaths(data_root, "scotus", 43).event("evt-order-judgment").outcome, Outcome
    )
    assert signed.merits_author == "Kavanaugh" and signed.vote_provenance is not None


def test_an_author_only_record_fills_beside_a_vote_record_and_never_clobbers_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root, conn = _merits_ledger(tmp_path)
    _stamp_opinions(data_root, conn, GRANTED_NOTED, apply=True, max_stamps=2)
    path = CasePaths(data_root, "scotus", 43).event("evt-order-judgment").outcome
    carried = read_model(path, Outcome)
    assert carried.merits_author == "Kavanaugh" and carried.vote_provenance is not None
    bare = carried.model_copy(update={"merits_author": None})
    target = vote_writer.OutcomeTarget(path, "scotus/43", "evt-order-judgment", "merits", bare)

    def classify(author: str, *, replace: bool = False) -> vote_writer.VoteWriteResult:
        result = vote_writer.VoteWriteResult(source="supremecourt-opinions")
        record = vote_writer.VoteRecord((), None, None, merits_author=author)
        vote_writer._classify(target, record, result, replace_differing=replace)
        return result

    filled = classify("Kavanaugh")
    ((stamp,),) = (filled.stamps,)
    assert not stamp.replaces
    assert vote_writer.stamped(bare, stamp.record).model_dump() == carried.model_dump()
    target = dataclasses.replace(target, outcome=carried)
    assert classify("Kavanaugh").unchanged == ["scotus/43/evt-order-judgment"]
    ((_, why),) = classify("Thomas").held_back
    assert why.startswith("carries a different merits author;")
    ((swap,),) = (classify("Thomas", replace=True).stamps,)
    assert swap.replaces
    swapped = vote_writer.stamped(carried, swap.record)
    assert swapped.merits_author == "Thomas" and swapped.votes == carried.votes


def test_a_listing_row_dated_off_the_resolution_names_no_author(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root = tmp_path / "data"
    for docket in (43, 38):
        _outcome(
            data_root,
            docket,
            event_id="evt-order-judgment",
            stage=Stage.merits,
            resolved_at=date(2026, 6, 29),
        )
    conn = _corpus(tmp_path, {43: "24-43", 38: "24-38"})
    result = _stamp_opinions(data_root, conn, GRANTED_NOTED, apply=False)
    assert all(s.record.merits_author is None for s in result.stamps)


def test_the_plans_author_vocabulary_is_the_listings() -> None:
    assert set(get_args(vote_writer._Author)) == {
        *opinion_lineups.LISTING_AUTHOR_CODES.values(),
        PER_CURIAM_LABEL,
    }


def test_docket_numbers_read_the_real_corpus_schema(tmp_path: Path) -> None:
    db = fixture.build_fixture_corpus(corpus.corpus_db_path(tmp_path / "corpus"))
    with corpus.connect_readonly(db, backend="local") as conn:
        numbers = vote_writer.docket_numbers(conn, ["scotus/304", "scotus/306", "scotus/999"])
    assert numbers == {"scotus/304": "22-845", "scotus/306": "26A11"}


def test_an_opinion_url_with_a_dot_segment_is_not_the_sources_document() -> None:
    assert is_opinion_pdf("https://www.supremecourt.gov/opinions/25pdf/24-43_2b35.pdf")
    assert not is_opinion_pdf("https://www.supremecourt.gov/opinions/../orders/x.pdf")
    assert not is_opinion_pdf("https://www.supremecourt.gov/opinions/./x.pdf")
    assert not is_opinion_pdf("https://www.supremecourt.gov/opinions/%2e%2e/orders/x.pdf")
    assert not vote_sources.is_order_document_url(
        "https://www.supremecourt.gov/orders/%2E%2E/x.pdf"
    )


# --- the credential split: projection, plan, apply ------------------------------------


def _orders_plan(
    data_root: Path, conn: sqlite3.Connection, tmp_path: Path, *, today: date = LATER
) -> Path:
    """The projection and the corpus-free read, through files as the jobs pass them."""
    projection_file = tmp_path / "handoff" / "projection.json"
    write_handoff(
        projection_file,
        vote_writer.vote_docket_numbers(
            conn, data_root, source="supremecourt-orders", terms=(2025,)
        ),
    )
    projection = read_handoff(projection_file, vote_writer.VoteDocketNumbers)
    numbers = vote_writer.projected_numbers(projection, "supremecourt-orders")
    with _client(_orders_handler([])) as client:
        dry = stamp_order_votes(
            numbers, data_root, OrderFetcher(client), today=today, terms=(2025,), apply=False
        )
    plan_file = tmp_path / "handoff" / "plan.json"
    write_handoff(plan_file, vote_writer.vote_plan(dry))
    return plan_file


def _apply_plan(
    data_root: Path,
    plan_file: Path,
    *,
    max_stamps: int | None = 10,
    replace_differing: bool = False,
    apply: bool = True,
) -> VoteWriteResult:
    return vote_writer.apply_vote_plan(
        read_handoff(plan_file, vote_writer.VoteStampPlan),
        data_root,
        source="supremecourt-orders",
        today=LATER,
        terms=(2025,),
        apply=apply,
        max_stamps=max_stamps,
        replace_differing=replace_differing,
    )


def _outcomes(data_root: Path) -> dict[str, str]:
    return {str(p.relative_to(data_root)): p.read_text() for p in data_root.rglob("outcome.json")}


def test_the_split_stamps_what_the_one_process_apply_stamps(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path / "split")
    plan_file = _orders_plan(data_root, conn, tmp_path / "split")
    projection = json.loads((tmp_path / "split" / "handoff" / "projection.json").read_text())
    # The projection carries the population's case ids and docket numbers, nothing else.
    assert projection["numbers"] == {f"scotus/{k}": v for k, v in CERT.items()}
    assert set(projection) == {"format", "version", "source", "numbers", "unprojected"}

    over = _apply_plan(data_root, plan_file, max_stamps=2)
    assert over.refused and not over.applied
    split = _apply_plan(data_root, plan_file, max_stamps=3)
    assert split.applied and len(split.stamps) == 3
    assert _votes_hold(data_root) == []

    one_root, one_conn = _cert_ledger(tmp_path / "one")
    _stamp_orders(one_root, one_conn, [], apply=True, max_stamps=3)
    assert _outcomes(data_root) == _outcomes(one_root)

    # The same plan again is a no-op: every record is already in place.
    again = _apply_plan(data_root, plan_file, max_stamps=1)
    assert again.stamps == [] and len(again.unchanged) == 3


def test_the_split_apply_holds_back_what_moved_since_the_plan(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    path = CasePaths(data_root, "scotus", 1).event("evt-petition-disposition").outcome
    write_json(
        path,
        read_model(path, Outcome).model_copy(
            update={
                "votes": [JusticeVote(justice="Thomas", vote=VoteValue.grant)],
                "vote_provenance": VoteProvenance(
                    source="supremecourt-orders",
                    documents=["https://www.supremecourt.gov/orders/courtorders/x.pdf"],
                    grammars=[GrammarStamp(grammar="scotus-order-notations", version=1)],
                    participating=9,
                    complete=False,
                ),
            }
        ),
    )
    result = _apply_plan(data_root, plan_file, max_stamps=3)
    assert "scotus/1/evt-petition-disposition" in dict(result.held_back)
    assert len(result.stamps) == 2
    replaced = _apply_plan(data_root, plan_file, max_stamps=3, replace_differing=True)
    assert [s.replaces for s in replaced.stamps] == [True]


def _tamper_votes(plan: dict[str, Any], change: str) -> None:  # noqa: PLR0912
    stamp = plan["stamps"][0]
    if change == "unknown-outcome":
        stamp["case_id"] = "scotus/999"
    elif change == "path-traversal":
        stamp["event_id"] = "../../../../etc"
    elif change == "duplicate":
        plan["stamps"].append(dict(stamp))
    elif change == "other-source":
        stamp["vote_provenance"]["source"] = "supremecourt-opinions"
    elif change == "complete-bench":
        stamp["vote_provenance"]["complete"] = True
    elif change == "foreign-document":
        stamp["vote_provenance"]["documents"] = ["https://example.com/orders/x.pdf"]
    elif change == "unregistered-grammar":
        stamp["vote_provenance"]["grammars"][0]["grammar"] = "made-up"
    elif change == "unsettled":
        stamp["resolved_at"] = LATER.isoformat()
    elif change == "plan-source":
        plan["source"] = "supremecourt-opinions"
    elif change == "extra-field":
        stamp["note"] = "x"
    elif change == "version":
        plan["version"] = 3
    elif change == "bad-vote":
        stamp["votes"] = [{"justice": "Thomas", "vote": "maybe"}]
    elif change == "orders-author":
        stamp["merits_author"] = "Thomas"
    elif change == "off-roster-author":
        stamp["merits_author"] = "Holmes"
    elif change == "no-part":
        stamp["votes"], stamp["vote_provenance"] = [], None
        stamp.pop("writing_roles", None)
    elif change == "unprovenanced-votes":
        stamp["vote_provenance"] = None


@pytest.mark.parametrize(
    "change",
    [
        "unknown-outcome",
        "path-traversal",
        "duplicate",
        "other-source",
        "complete-bench",
        "foreign-document",
        "unregistered-grammar",
        "unsettled",
        "plan-source",
        "extra-field",
        "version",
        "bad-vote",
        "orders-author",
        "off-roster-author",
        "no-part",
        "unprovenanced-votes",
    ],
)
def test_a_tampered_or_malformed_plan_is_refused_whole(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, change: str
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    raw = json.loads(plan_file.read_text())
    # Tamper with the record a one-process run would stamp onto scotus/1.
    raw["stamps"].sort(key=lambda s: s["case_id"])
    _tamper_votes(raw, change)
    plan_file.write_text(json.dumps(raw))
    before = _outcomes(data_root)
    with pytest.raises(HandoffRefused):
        _apply_plan(data_root, plan_file)
    assert _outcomes(data_root) == before


def test_a_plan_read_from_a_partial_fetch_refuses_the_apply(tmp_path: Path) -> None:
    data_root, _ = _cert_ledger(tmp_path)
    plan = vote_writer.VoteStampPlan(
        source="supremecourt-orders",
        population=4,
        failures=["OT25 orders listings: 503"],
        stamps=[],
    )
    plan_file = tmp_path / "plan.json"
    write_handoff(plan_file, plan)
    result = _apply_plan(data_root, plan_file)
    assert result.refused and not result.applied


def test_a_projection_for_the_other_pass_is_refused(tmp_path: Path) -> None:
    projection = vote_writer.VoteDocketNumbers(source="supremecourt-opinions", numbers={})
    with pytest.raises(HandoffRefused):
        vote_writer.projected_numbers(projection, "supremecourt-orders")
    with pytest.raises(ValidationError):
        vote_writer.VoteDocketNumbers.model_validate(
            {"source": "supremecourt-orders", "numbers": {"scotus/1": "25-1; rm -rf"}}
        )


@pytest.mark.parametrize("command", ["stamp-order-votes", "stamp-opinion-votes"])
def test_the_commands_split_modes(command: str, tmp_path: Path) -> None:
    """The projection needs the corpus; the plan's apply needs neither corpus nor network."""
    data_root, _ = _cert_ledger(tmp_path)
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as real:
        real.executemany(
            "INSERT INTO cases (case_id, court, docket_number) VALUES (?, 'scotus', ?)",
            [(f"scotus/{docket}", number) for docket, number in CERT.items()],
        )
        real.commit()
    env = {"FEDCOURTS_CORPUS_ROOT": str(corpus_root), "FEDCOURTS_DATA_ROOT": str(data_root)}
    runner = CliRunner()
    projection = tmp_path / "p.json"
    emitted = runner.invoke(app, [command, "--emit-corpus-projection", str(projection)], env=env)
    assert emitted.exit_code == 0, emitted.output
    source = "supremecourt-orders" if command == "stamp-order-votes" else "supremecourt-opinions"
    assert read_handoff(projection, vote_writer.VoteDocketNumbers).source == source
    plan = tmp_path / "plan.json"
    write_handoff(
        plan, vote_writer.VoteStampPlan(source=source, population=0, failures=[], stamps=[])
    )
    no_corpus = {**env, "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "nowhere")}
    applied = runner.invoke(
        app, [command, "--from-plan", str(plan), "--apply", "--max-stamps", "1"], env=no_corpus
    )
    assert applied.exit_code == 0, applied.output
    plan.write_text("{}")
    refused = runner.invoke(
        app, [command, "--from-plan", str(plan), "--apply", "--max-stamps", "1"], env=no_corpus
    )
    assert refused.exit_code == 1 and "refusing the handoff file" in refused.output
    for args in (
        ["--projection", str(projection), "--apply", "--max-stamps", "1"],
        ["--plan-out", str(plan), "--apply", "--max-stamps", "1"],
        ["--emit-corpus-projection", str(projection), "--from-plan", str(plan)],
        ["--from-plan", str(plan), "--projection", str(projection)],
    ):
        assert runner.invoke(app, [command, *args], env=env).exit_code == 2, args


def test_an_opinions_plan_round_trips_to_the_one_process_apply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The opinions source's honest plan — complete records — passes the writer's checks."""
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root, conn = _merits_ledger(tmp_path / "split")
    numbers = vote_writer.projected_numbers(
        vote_writer.vote_docket_numbers(conn, data_root, source="supremecourt-opinions"),
        "supremecourt-opinions",
    )
    with _client(_opinions_handler([])) as client:
        dry = stamp_opinion_votes(
            numbers, data_root, OpinionFetcher(client), lambda _t: GRANTED_NOTED, apply=False
        )
    plan_file = tmp_path / "plan.json"
    write_handoff(plan_file, vote_writer.vote_plan(dry))
    split = vote_writer.apply_vote_plan(
        read_handoff(plan_file, vote_writer.VoteStampPlan),
        data_root,
        source="supremecourt-opinions",
        today=LATER,
        apply=True,
        max_stamps=2,
    )
    assert split.applied and len(split.stamps) == 2
    one_root, one_conn = _merits_ledger(tmp_path / "one")
    _stamp_opinions(one_root, one_conn, GRANTED_NOTED, apply=True, max_stamps=2)
    assert _outcomes(data_root) == _outcomes(one_root)
    assert _votes_hold(data_root) == []


def test_an_annotated_stored_number_is_left_out_of_the_projection(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _outcome(data_root, 1)
    _outcome(data_root, 2)
    conn = _corpus(tmp_path, {1: "25-885", 2: "11-6029 (11A229)"})
    projection = vote_writer.vote_docket_numbers(
        conn, data_root, source="supremecourt-orders", terms=(2025,)
    )
    assert projection.numbers == {"scotus/1": "25-885"} and projection.unprojected == 1


# --- the standing sweep ------------------------------------------------------------


def test_the_orders_pass_reads_from_its_floor_through_the_current_term() -> None:
    """The current Term is in reach as soon as it opens, so its orders settle into stamps."""
    assert vote_writer.order_vote_terms(date(2026, 9, 30)) == (2024, 2025)
    assert vote_writer.order_vote_terms(date(2026, 10, 1)) == (2024, 2025, 2026)
    assert vote_writer.order_vote_terms(date(2026, 10, 13)) == (2024, 2025, 2026)


def _orders_record() -> vote_writer.VoteRecord:
    return vote_writer.VoteRecord(
        votes=(),
        provenance=VoteProvenance(
            source="supremecourt-orders",
            documents=["https://www.supremecourt.gov/orders/courtorders/x.pdf"],
            grammars=[GrammarStamp(grammar="scotus-order-notations", version=1)],
            participating=9,
            complete=False,
        ),
        writing_roles=None,
    )


def _target(data_root: Path, docket: int, resolved_at: date) -> vote_writer.OutcomeTarget:
    path = _outcome(data_root, docket, resolved_at=resolved_at)
    return vote_writer.OutcomeTarget(
        path=path,
        case_id=f"scotus/{docket}",
        event_id="evt-petition-disposition",
        stage="cert",
        outcome=read_model(path, Outcome),
    )


def test_a_sweep_takes_the_oldest_order_date_first(tmp_path: Path) -> None:
    """The slice is keyed on the order date before the outcome, so an older order is
    never starved behind newer ones that happen to sort first by case id."""
    data_root = tmp_path / "data"
    later = _target(data_root, 1, date(2026, 6, 29))
    earlier = _target(data_root, 2, date(2026, 6, 22))
    result = VoteWriteResult(
        source="supremecourt-orders",
        stamps=[
            vote_writer.VoteStamp(target=later, record=_orders_record()),
            vote_writer.VoteStamp(target=earlier, record=_orders_record()),
        ],
    )
    sliced = vote_writer._finish(
        result, apply=False, max_stamps=None, sweep=vote_writer.SweepSlice(cap=1, ceiling=5)
    )
    assert [s.target.case_id for s in sliced.stamps] == ["scotus/2"]
    assert sliced.deferred == 1


def _sweep_plan(data_root: Path, plan_file: Path, sweep: vote_writer.SweepSlice) -> VoteWriteResult:
    return vote_writer.apply_vote_plan(
        read_handoff(plan_file, vote_writer.VoteStampPlan),
        data_root,
        source="supremecourt-orders",
        today=LATER,
        terms=(2025,),
        apply=True,
        sweep=sweep,
    )


def test_a_sweep_slices_at_its_cap_and_successive_windows_converge(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The cap is a slice, not a refusal: the rest waits for the next window, and a
    window over a converged ledger stamps nothing."""
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    sweep = vote_writer.SweepSlice(cap=2, ceiling=10)

    first = _sweep_plan(data_root, plan_file, sweep)
    assert first.applied and not first.refused
    assert [s.target.case_id for s in first.stamps] == ["scotus/1", "scotus/2"]
    assert first.deferred == 1

    second = _sweep_plan(data_root, plan_file, sweep)
    assert [s.target.case_id for s in second.stamps] == ["scotus/3"]
    assert (second.deferred, len(second.unchanged)) == (0, 2)

    third = _sweep_plan(data_root, plan_file, sweep)
    assert (third.stamps, third.deferred, len(third.unchanged)) == ([], 0, 3)
    assert _votes_hold(data_root) == []

    # The windows together wrote exactly what one bounded apply writes.
    one_root, one_conn = _cert_ledger(tmp_path / "one")
    _stamp_orders(one_root, one_conn, [], apply=True, max_stamps=3)
    assert _outcomes(data_root) == _outcomes(one_root)


def test_a_sweep_above_its_ceiling_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A class past the ceiling is a widened population: refused whole, not drained."""
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    before = _outcomes(data_root)
    result = _sweep_plan(data_root, plan_file, vote_writer.SweepSlice(cap=1, ceiling=2))
    assert result.refused and not result.applied
    assert (result.stamps, result.deferred) == ([], 3)
    assert _outcomes(data_root) == before


def test_a_sweep_never_replaces_a_record(tmp_path: Path) -> None:
    data_root, _ = _cert_ledger(tmp_path)
    path = CasePaths(data_root, "scotus", 1).event("evt-petition-disposition").outcome
    before = path.read_text()
    target = vote_writer.OutcomeTarget(
        path=path,
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        stage="cert",
        outcome=read_model(path, Outcome),
    )
    record = vote_writer.VoteRecord(
        votes=(),
        provenance=VoteProvenance(
            source="supremecourt-orders",
            documents=["https://www.supremecourt.gov/orders/courtorders/x.pdf"],
            grammars=[GrammarStamp(grammar="scotus-order-notations", version=1)],
            participating=9,
            complete=False,
        ),
        writing_roles=None,
    )
    result = VoteWriteResult(
        source="supremecourt-orders",
        stamps=[vote_writer.VoteStamp(target=target, record=record, replaces=True)],
    )
    with pytest.raises(ValueError, match="never replaces"):
        vote_writer._finish(
            result, apply=True, max_stamps=None, sweep=vote_writer.SweepSlice(cap=5, ceiling=5)
        )
    assert path.read_text() == before


def test_a_sweep_slice_needs_a_cap_within_its_ceiling() -> None:
    for cap, ceiling in ((0, 5), (6, 5)):
        with pytest.raises(ValueError, match="cap <= ceiling"):
            vote_writer.SweepSlice(cap=cap, ceiling=ceiling)


def test_the_sweep_command_stamps_the_plan_and_reports_its_ledger_line(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The writer job's argv end to end: no bound, the configured cap, and a re-run
    that finds nothing to fill."""
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    env = {
        "FEDCOURTS_DATA_ROOT": str(data_root),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "nowhere"),
    }
    argv = ["stamp-order-votes", "--from-plan", str(plan_file), "--sweep", "--apply"]
    runner = CliRunner()
    first = runner.invoke(app, argv, env=env)
    assert first.exit_code == 0, first.output
    assert "sweep ledger — stamp-order-votes: would fill 3; filled 3; remaining 0" in first.output
    assert _votes_hold(data_root) == []
    again = runner.invoke(app, argv, env=env)
    assert again.exit_code == 0, again.output
    assert "sweep ledger — stamp-order-votes: would fill 0; filled 0; remaining 0" in again.output
    assert "3 already carry the same record" in again.output


@pytest.mark.parametrize("extra", [["--max-stamps", "5"], ["--replace-differing"]])
def test_the_sweep_refuses_a_bound_or_a_replacement(extra: list[str], tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    write_handoff(
        plan,
        vote_writer.VoteStampPlan(
            source="supremecourt-orders", population=0, failures=[], stamps=[]
        ),
    )
    result = CliRunner().invoke(
        app, ["stamp-order-votes", "--from-plan", str(plan), "--sweep", "--apply", *extra]
    )
    assert result.exit_code == 2, result.output


def test_the_read_only_split_modes_take_no_sweep(tmp_path: Path) -> None:
    runner = CliRunner()
    for args in (
        ["--emit-corpus-projection", str(tmp_path / "p.json")],
        ["--projection", str(tmp_path / "p.json"), "--plan-out", str(tmp_path / "plan.json")],
    ):
        result = runner.invoke(app, ["stamp-order-votes", *args, "--sweep"])
        assert result.exit_code == 2, (args, result.output)
        assert "take no --sweep" in " ".join(result.output.split())


def _tight_caps(tmp_path: Path) -> Path:
    """A config root whose vote sweep takes one record a window and refuses above two."""
    config_root = tmp_path / "config"
    config_root.mkdir()
    (config_root / "tracking.yaml").write_text(
        "historical:\n  sweep_caps:\n    order_votes: 1\n    order_votes_ceiling: 2\n"
    )
    return config_root


def test_the_sweep_command_refuses_a_class_above_its_ceiling(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    before = _outcomes(data_root)
    env = {
        "FEDCOURTS_DATA_ROOT": str(data_root),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "nowhere"),
        "FEDCOURTS_CONFIG_ROOT": str(_tight_caps(tmp_path)),
    }
    result = CliRunner().invoke(
        app, ["stamp-order-votes", "--from-plan", str(plan_file), "--sweep", "--apply"], env=env
    )
    output = " ".join(result.output.split())
    assert result.exit_code == 1, result.output
    assert "::error::stamp-order-votes --sweep: refusing to apply" in output
    assert "sweep ledger — stamp-order-votes: would fill 3; filled 0; remaining 3 (cap 1)" in output
    assert _outcomes(data_root) == before


def test_a_dry_run_sweep_warns_above_its_ceiling_and_exits_clean(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, order_lineups)
    data_root, conn = _cert_ledger(tmp_path)
    plan_file = _orders_plan(data_root, conn, tmp_path)
    env = {
        "FEDCOURTS_DATA_ROOT": str(data_root),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "nowhere"),
        "FEDCOURTS_CONFIG_ROOT": str(_tight_caps(tmp_path)),
    }
    result = CliRunner().invoke(
        app, ["stamp-order-votes", "--from-plan", str(plan_file), "--sweep"], env=env
    )
    output = " ".join(result.output.split())
    assert result.exit_code == 0, result.output
    assert "::warning::stamp-order-votes --sweep: the class holds 3 rows" in output
    assert "would fill 3; filled 0; remaining 3 (cap 1)" in output
