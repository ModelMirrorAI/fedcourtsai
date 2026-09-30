"""The vote writer: order and opinion readings stamped onto committed outcomes.

Offline throughout: the Court's pages are served by an ``httpx.MockTransport``
and PDF extraction is stubbed to decode the bytes, so each document is the
fixture text the reader tests already pin (``tests/test_order_lineups.py``,
``tests/test_opinion_lineups.py``). The corpus is a one-table SQLite file
holding only what the writer reads from it: each case's docket number.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from datetime import date
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import opinion_lineups, order_lineups
from fedcourtsai.pipeline.documents import ExtractedText
from fedcourtsai.pipeline.opinion_lineups import OpinionFetcher
from fedcourtsai.pipeline.order_lineups import OrderDocketReading, OrderFetcher, OrderPartReading
from fedcourtsai.schemas import (
    Disposition,
    EventKind,
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
    assert carter.provenance.complete is False
    assert carter.provenance.participating == 9
    assert sorted(g.grammar for g in carter.provenance.grammars) == [
        "scotus-order-notations",
        "scotus-writing-headers",
    ]
    assert len(carter.provenance.documents) == 2
    assert carter.writing_roles is not None and len(carter.writing_roles) == 9

    carr = stamps["scotus/2"]
    assert [(v.justice, v.vote) for v in carr.votes] == [("Alito", VoteValue.did_not_participate)]
    assert carr.provenance.participating == 8
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
    assert record.provenance.participating == 8 and record.writing_roles is None


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
    assert result.stamps == []
    reasons = [reason for _, reason in result.held_back]
    assert reasons and all(r.startswith("Granted & Noted disagrees") for r in reasons)
    assert any("Gorsuch (dissent)" in r for r in reasons)


def test_an_unreadable_granted_noted_list_refuses_the_apply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch, opinion_lineups)
    data_root, conn = _merits_ledger(tmp_path)
    result = _stamp_opinions(data_root, conn, None, apply=True, max_stamps=5)
    assert result.refused and result.failures and result.stamps == []


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
