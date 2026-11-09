"""The AI watchlist rulings' summaries: selection, staging, the model call, the file, the update."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
from tenacity import wait_none
from typer.testing import CliRunner

from fedcourtsai import ai_rulings, corpus, summaries
from fedcourtsai.ai_cases_update import build_ai_cases_update, render_ai_cases_update
from fedcourtsai.claude_auth import ApiKey
from fedcourtsai.cli import app
from fedcourtsai.config import SummariesConfig
from fedcourtsai.pipeline.documents import scrub_contact_details
from fedcourtsai.schemas import (
    AiCaseActivity,
    AiCaseActivityEntry,
    AiRulingPlanItem,
    SummaryPlan,
)
from fedcourtsai.serialize import write_json
from fedcourtsai.validate import validate_ledger
from tests.conftest import FixtureCorpus

runner = CliRunner()

CONFIG = SummariesConfig()
FAKE_KEY = "test-summaries-key-0123456789abcdef"
TODAY = date(2026, 11, 4)
COURT, DOCKET_ID = "cand", 67569326

RULING_TEXT = (
    "ORDER GRANTING IN PART AND DENYING IN PART MOTION TO DISMISS\n"
    + "The motion to dismiss is granted as to the unjust enrichment claim and "
    + "denied as to the copyright infringement claim. Leave to amend within 21 days.\n"
)
ENTRY_DESCRIPTION = "ORDER by Judge Somebody re 100 MOTION to Dismiss. (clerk's words)"

PAYLOAD: dict[str, Any] = {
    "id": DOCKET_ID,
    "court_id": COURT,
    "docket_number": "3:23-cv-03417",
    "case_name": "Kadrey v. Meta Platforms, Inc.",
    "nature_of_suit": "820 Copyright",
    "docket_entries": [
        {
            "id": 501,
            "entry_number": 512,
            "date_filed": "2026-11-02",
            "description": ENTRY_DESCRIPTION,
            "recap_documents": [
                {"attachment_number": 1, "plain_text": "Exhibit A text."},
                {"attachment_number": None, "plain_text": RULING_TEXT},
            ],
        },
        {
            "id": 502,
            "entry_number": 513,
            "date_filed": "2026-11-03",
            "description": "ORDER granting 101 Motion for Summary Judgment",
            "recap_documents": [{"attachment_number": None, "plain_text": ""}],
        },
    ],
}

HEADLINE = "The court dismissed one claim against the developer and let the copyright claim go on."
GOOD_BODY = (
    "## In brief\n\n"
    + HEADLINE
    + "\n\n## What the court decided\n\n"
    + " ".join(["The developer asked the court to dismiss the authors' claims."] * 5)
    + "\n\nThe authors may amend the dismissed claim within 21 days."
)


def _activity(
    case: str = "Kadrey v. Meta Platforms",
    *,
    entry_id: int = 501,
    kind: str = "ruling",
    filed: date = date(2026, 11, 2),
    number: int | None = 512,
) -> AiCaseActivityEntry:
    return AiCaseActivityEntry(
        case=case,
        category="copyright",
        court=COURT,
        docket_id=DOCKET_ID,
        docket_number="3:23-cv-03417",
        entry_id=entry_id,
        entry_number=number,
        date_filed=filed,
        kind=kind,
        url=f"https://www.courtlistener.com/docket/{DOCKET_ID}/kadrey/#entry-{number}",
    )


def _record_day(data_root: Path, day: date, entries: list[AiCaseActivityEntry]) -> None:
    write_json(
        data_root / "ai-cases/activity" / f"{day.isoformat()}.json",
        AiCaseActivity(day=day, rule="ai-activity-v1", entries=entries),
    )


def _plan(rulings: list[AiRulingPlanItem]) -> SummaryPlan:
    return SummaryPlan(
        model=CONFIG.model,
        eligible=0,
        up_to_date=0,
        deferred=0,
        cases=[],
        rulings=rulings,
        estimated_cost_usd_low=0.0,
        estimated_cost_usd_high=0.0,
    )


def _planned(data_root: Path) -> SummaryPlan:
    _record_day(data_root, date(2026, 11, 3), [_activity(), _activity(entry_id=502, number=513)])
    owed = ai_rulings.owed_rulings(data_root, TODAY)
    rulings, without, cost = ai_rulings.plan_rulings(owed, lambda c, d: PAYLOAD, CONFIG)
    return ai_rulings.with_rulings(_plan([]), rulings, without, cost)


def _response(text: str, stop: str = "end_turn") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [{"type": "text", "text": text}],
            "stop_reason": stop,
            "usage": {"input_tokens": 2_000, "output_tokens": 300},
        },
    )


def _summarize(
    tmp_path: Path, handler: Callable[[httpx.Request], httpx.Response]
) -> tuple[summaries.SummarizeOutcome, SummaryPlan]:
    data, stage = tmp_path / "data", tmp_path / "stage"
    plan = _planned(data)
    assert ai_rulings.stage_rulings(plan, lambda c, d: PAYLOAD, stage) == []
    outcome = summaries.SummarizeOutcome()
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        ai_rulings.summarize_rulings(
            plan,
            outcome,
            stage_root=stage,
            data_root=data,
            config=CONFIG,
            prompt_bytes=b"the ruling prompt",
            client=client,
            credential=ApiKey(FAKE_KEY),
            now=lambda: datetime(2026, 11, 4, 4, 0, 1, 5, tzinfo=UTC),
            wait=wait_none(),
        )
    return outcome, plan


# --- selection ----------------------------------------------------------------------


def test_ruling_text_is_the_main_documents_text_alone() -> None:
    assert ai_rulings.ruling_text(PAYLOAD, 501) == RULING_TEXT
    assert ai_rulings.ruling_text(PAYLOAD, 502) == ""
    assert ai_rulings.ruling_text(PAYLOAD, 999) == ""


def test_owed_rulings_are_recent_court_written_and_unsummarized(tmp_path: Path) -> None:
    _record_day(
        tmp_path,
        date(2026, 11, 3),
        [
            _activity(),
            _activity(entry_id=503, kind="motion", number=514),
            _activity(entry_id=504, kind="opinion", filed=date(2026, 10, 30), number=515),
        ],
    )
    # The same entry on a second day counts once; a record past the window not at all.
    _record_day(tmp_path, date(2026, 11, 4), [_activity()])
    _record_day(tmp_path, TODAY - timedelta(days=31), [_activity(entry_id=505, number=516)])

    owed = ai_rulings.owed_rulings(tmp_path, TODAY)
    assert [e.entry_id for e in owed] == [504, 501]

    ai_rulings.summary_path(tmp_path, 504).parent.mkdir(parents=True)
    ai_rulings.summary_path(tmp_path, 504).write_text("x")
    assert [e.entry_id for e in ai_rulings.owed_rulings(tmp_path, TODAY)] == [501]


def test_plan_lists_text_less_rulings_apart_and_prices_the_rest(tmp_path: Path) -> None:
    plan = _planned(tmp_path)
    assert [r.entry_id for r in plan.rulings] == [501]
    assert plan.rulings[0].text_digest == ai_rulings.text_digest(RULING_TEXT)
    assert plan.rulings[0].input_chars == len(RULING_TEXT)
    assert plan.rulings_without_text == [502]
    assert 0 < plan.estimated_cost_usd_low <= plan.estimated_cost_usd_high
    report = summaries.render_plan_report(plan)
    assert "AI watchlist rulings owed a summary: **1** planned, 1 whose text" in report
    assert "| `cand/67569326` entry `501` | Kadrey v. Meta Platforms |" in report


def test_plan_reads_each_docket_once(tmp_path: Path) -> None:
    _record_day(tmp_path, TODAY, [_activity(), _activity(entry_id=502, number=513)])
    reads: list[tuple[str, int]] = []

    def read(court: str, docket: int) -> dict[str, Any]:
        reads.append((court, docket))
        return PAYLOAD

    ai_rulings.plan_rulings(ai_rulings.owed_rulings(tmp_path, TODAY), read, CONFIG)
    assert reads == [(COURT, DOCKET_ID)]


# --- staging ------------------------------------------------------------------------


def test_stage_writes_the_scrubbed_text_and_the_stage_check_keeps_it(tmp_path: Path) -> None:
    plan = _planned(tmp_path / "data")
    stage = tmp_path / "stage"
    assert ai_rulings.stage_rulings(plan, lambda c, d: PAYLOAD, stage) == []
    staged = json.loads((stage / "ai-rulings/501.json").read_text())
    assert set(staged) == {"entry_id", "text_digest", "text"}
    assert staged["text"] == RULING_TEXT
    assert ENTRY_DESCRIPTION not in (stage / "ai-rulings/501.json").read_text()
    assert summaries.prune_stage(plan, stage) == []
    assert (stage / "ai-rulings/501.json").is_file()


def test_stage_skips_a_ruling_whose_text_changed_or_went(tmp_path: Path) -> None:
    plan = _planned(tmp_path / "data")
    changed = json.loads(json.dumps(PAYLOAD))
    changed["docket_entries"][0]["recap_documents"][1]["plain_text"] = "Another text."
    assert ai_rulings.stage_rulings(plan, lambda c, d: changed, tmp_path / "s1") == [
        (501, "its text changed since the plan")
    ]
    assert ai_rulings.stage_rulings(plan, lambda c, d: None, tmp_path / "s2") == [
        (501, "the corpus no longer holds its text")
    ]
    assert not (tmp_path / "s1/ai-rulings/501.json").exists()


def test_stage_withholds_a_ruling_with_a_contact_residual(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = _planned(tmp_path / "data")
    real = scrub_contact_details

    def residual(text: str) -> Any:
        scrubbed = real(text)
        return type(scrubbed)(text=scrubbed.text, replacements=0, residuals=1)

    monkeypatch.setattr(ai_rulings, "scrub_contact_details", residual)
    skipped = ai_rulings.stage_rulings(plan, lambda c, d: PAYLOAD, tmp_path / "stage")
    assert skipped == [(501, "1 contact residual(s) after the scrub")]


@pytest.mark.parametrize(
    ("name", "content", "reason"),
    [
        ("777.json", None, "not a planned ruling"),
        ("notes.txt", None, "not a planned ruling"),
        (
            "501.json",
            {"entry_id": 501, "text_digest": "sha256:" + "0" * 64, "text": "x"},
            "staged ruling text is not the text the plan priced",
        ),
        (
            "501.json",
            {"entry_id": 501, "text_digest": None, "text": "x", "docket": {}},
            "staged ruling does not hold exactly entry_id, text, text_digest",
        ),
        ("501.json", "not json", "staged ruling is unreadable"),
    ],
)
def test_stage_check_removes_a_ruling_file_off_the_allowlist(
    tmp_path: Path, name: str, content: object, reason: str
) -> None:
    plan = _planned(tmp_path / "data")
    stage = tmp_path / "stage"
    ai_rulings.stage_rulings(plan, lambda c, d: PAYLOAD, stage)
    path = stage / "ai-rulings" / name
    if isinstance(content, dict):
        path.write_text(json.dumps(content))
    elif isinstance(content, str):
        path.write_text(content)
    elif not path.exists():
        path.write_text("{}")
    removed = summaries.prune_stage(plan, stage)
    assert removed == [(f"ai-rulings/{name}", reason)]
    assert not path.exists()


def test_stage_check_removes_a_ruling_with_a_contact_residual(tmp_path: Path) -> None:
    plan = _planned(tmp_path / "data")
    stage = tmp_path / "stage"
    ai_rulings.stage_rulings(plan, lambda c, d: PAYLOAD, stage)
    path = stage / "ai-rulings/501.json"
    staged = json.loads(path.read_text())
    staged["text"] += "\nCall me at (415) 555-0134 or write to someone@example.com.\n"
    path.write_text(json.dumps(staged))
    assert summaries.prune_stage(plan, stage) == [
        ("ai-rulings/501.json", "staged ruling text carries a contact-shaped residual")
    ]


# --- the call and the file -----------------------------------------------------------


def test_summarize_writes_the_file_from_the_ruling_text_alone(tmp_path: Path) -> None:
    seen: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return _response(GOOD_BODY)

    outcome, _ = _summarize(tmp_path, handler)
    assert [label for label, _, _ in outcome.written] == ["ruling cand/67569326 entry 501"]
    (body,) = seen
    assert "tools" not in body
    assert body["thinking"] == {"type": "disabled"}
    message = body["messages"][0]["content"]
    assert RULING_TEXT.strip() in message
    assert 'case="Kadrey v. Meta Platforms"' in message
    assert 'entry_number="512"' in message
    for curated in (ENTRY_DESCRIPTION, "820 Copyright", "Kadrey v. Meta Platforms, Inc."):
        assert curated not in message

    path = ai_rulings.summary_path(tmp_path / "data", 501)
    front, text = ai_rulings.parse_summary(path.read_text())
    assert (front.entry_id, front.kind, front.model) == (501, "ruling", CONFIG.model)
    assert front.text_digest == ai_rulings.text_digest(RULING_TEXT)
    assert front.prompt_digest == summaries.prompt_digest(b"the ruling prompt")
    assert front.usage is not None and front.usage.input_tokens == 2_000
    assert text.strip() == GOOD_BODY
    assert validate_ledger(tmp_path / "data").ok


def test_summarize_retries_a_mechanical_rejection_once(tmp_path: Path) -> None:
    bodies = iter([GOOD_BODY.replace("## What the court decided", "## Decision"), GOOD_BODY])
    seen: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return _response(next(bodies))

    outcome, _ = _summarize(tmp_path, handler)
    assert len(outcome.written) == 1
    assert outcome.retried and "sections must be exactly" in outcome.retried[0][1]
    assert len(seen[1]["messages"]) == 3


def test_summarize_skips_markup_on_retry_and_writes_nothing(tmp_path: Path) -> None:
    bad = GOOD_BODY + "\n\nSee https://example.com for more."
    outcome, _ = _summarize(tmp_path, lambda r: _response(bad))
    assert outcome.written == []
    ((_label, reason, cost),) = outcome.skipped
    assert reason.startswith("rejected on retry: carries a URL")
    assert cost > 0
    assert not ai_rulings.summary_path(tmp_path / "data", 501).exists()


def test_summarize_does_not_rewrite_a_summarized_ruling(tmp_path: Path) -> None:
    _summarize(tmp_path, lambda r: _response(GOOD_BODY))
    outcome, _ = _summarize(tmp_path, lambda r: _response(GOOD_BODY))
    assert outcome.written == []


@pytest.mark.parametrize(
    ("body", "problem"),
    [
        (GOOD_BODY.replace(HEADLINE, " ".join(["word"] * 31)), "headline runs 31 words"),
        ("Preamble.\n\n" + GOOD_BODY, "text before the first section heading"),
        (GOOD_BODY.replace("The authors may", "Whether the authors may"), "opens with 'Whether'"),
        (GOOD_BODY + "\n\n- a list item", "carries a list item"),
        ("## In brief\n\nShort.\n\n## What the court decided\n\nToo short.", "outside the 60-350"),
    ],
)
def test_body_contract(body: str, problem: str) -> None:
    assert any(problem in p for p in ai_rulings.body_problems(body))
    assert ai_rulings.body_problems(GOOD_BODY) == []


def test_validate_refuses_a_summary_named_for_another_entry(tmp_path: Path) -> None:
    _summarize(tmp_path, lambda r: _response(GOOD_BODY))
    path = ai_rulings.summary_path(tmp_path / "data", 501)
    path.rename(path.with_name("777.md"))
    report = validate_ledger(tmp_path / "data")
    assert not report.ok and "named for entry 777 but records entry 501" in report.problems[0]


def test_the_jail_admits_a_ruling_summary_and_nothing_else_under_ai_cases() -> None:
    writes, violations = summaries.summary_changes(
        [
            ("A", "data/ai-cases/summaries/501.md"),
            ("A", "data/ai-cases/activity/2026-11-04.json"),
            ("A", "data/ai-cases/summaries/../activity/x.md"),
            ("D", "data/ai-cases/summaries/501.md"),
        ],
        withdrawn={"data/ai-cases/summaries/501.md"},
    )
    assert writes == ["data/ai-cases/summaries/501.md"]
    assert violations == [
        "A data/ai-cases/activity/2026-11-04.json",
        "A data/ai-cases/summaries/../activity/x.md",
        "D data/ai-cases/summaries/501.md",
    ]


# --- the update ---------------------------------------------------------------------


def test_the_update_quotes_a_rulings_summary_under_its_item(tmp_path: Path) -> None:
    _summarize(tmp_path, lambda r: _response(GOOD_BODY))
    data = tmp_path / "data"
    text = render_ai_cases_update(build_ai_cases_update(data, date(2026, 11, 2), date(2026, 11, 8)))
    item = "- Nov 2: Ruling on a motion (N.D. Cal. 3:23-cv-03417, entry 512)."
    assert item in text
    after = text.split(item, 1)[1]
    assert f"  > {HEADLINE}" in after
    assert "  > *Summary written by claude-sonnet-5 from the ruling's own text." in after
    # The entry without a summary renders as an item alone.
    assert after.count("> *Summary written by") == 1


def test_the_update_renders_without_any_summary(tmp_path: Path) -> None:
    _record_day(tmp_path, date(2026, 11, 3), [_activity()])
    text = render_ai_cases_update(
        build_ai_cases_update(tmp_path, date(2026, 11, 2), date(2026, 11, 8))
    )
    assert ">" not in text.split("## Kadrey v. Meta Platforms", 1)[1].split("---")[0]


# --- the commands -------------------------------------------------------------------


def test_plan_stage_check_and_summarize_commands_end_to_end(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    today = datetime.now(UTC).date()
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, f"{COURT}/{DOCKET_ID}", today, PAYLOAD)
    _record_day(fixture_corpus.data_root, today, [_activity()])

    plain = runner.invoke(app, ["summarize-plan", "--corpus-backend", "local"])
    assert plain.exit_code == 0, plain.output
    assert SummaryPlan.model_validate_json(plain.stdout).rulings == []

    plan_file = tmp_path / "plan.json"
    planned = runner.invoke(
        app,
        ["summarize-plan", "--rulings", "--corpus-backend", "local", "--out", str(plan_file)],
    )
    assert planned.exit_code == 0, planned.output
    plan = SummaryPlan.model_validate_json(plan_file.read_text())
    assert [r.entry_id for r in plan.rulings] == [501]

    stage = tmp_path / "stage"
    staged = runner.invoke(
        app,
        [
            "ai-ruling-stage",
            "--plan",
            str(plan_file),
            "--staged",
            str(stage),
            "--corpus-backend",
            "local",
        ],
    )
    assert staged.exit_code == 0, staged.output
    assert "1 ruling(s) staged, 0 skipped" in staged.output
    checked = runner.invoke(
        app, ["summary-stage-check", "--plan", str(plan_file), "--staged", str(stage)]
    )
    assert checked.exit_code == 0, checked.output
    assert (stage / "ai-rulings/501.json").is_file()

    real_client = httpx.Client

    def client(**kwargs: Any) -> httpx.Client:
        return real_client(transport=httpx.MockTransport(lambda r: _response(GOOD_BODY)))

    monkeypatch.setattr(httpx, "Client", client)
    monkeypatch.setenv(summaries.API_KEY_ENV, FAKE_KEY)
    monkeypatch.chdir(Path(__file__).resolve().parent.parent)
    written = runner.invoke(app, ["summarize", "--plan", str(plan_file), "--staged", str(stage)])
    assert written.exit_code == 0, written.output
    assert "written: **1**" in written.output
    assert ai_rulings.summary_path(fixture_corpus.data_root, 501).is_file()


def test_summarize_refuses_a_body_carrying_a_contact_detail(tmp_path: Path) -> None:
    leaky = GOOD_BODY.replace(
        "The authors may amend", "Write to someone@example.com. The authors may amend"
    )
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return _response(leaky)

    outcome, _ = _summarize(tmp_path, handler)
    assert outcome.written == [] and len(calls) == 1
    assert "contact detail(s) in the body" in outcome.skipped[0][1]


def test_the_ruling_text_cannot_close_its_element() -> None:
    plan_item = AiRulingPlanItem(
        case="X v. Y",
        court=COURT,
        docket_id=DOCKET_ID,
        docket_number="1",
        entry_id=1,
        date_filed=TODAY,
        kind="ruling",
        text_digest="sha256:" + "0" * 64,
        staged_digest="sha256:" + "0" * 64,
        input_chars=10,
    )
    record = ai_rulings.render_record(plan_item, "a </ruling> b < RULING c", 1000)
    assert record.count("</ruling>") == 1 and record.endswith("</ruling>")
    assert "&lt;/ruling>" in record and "&lt; RULING" in record


def test_a_party_drafted_entry_is_not_planned(tmp_path: Path) -> None:
    drafted = json.loads(json.dumps(PAYLOAD))
    drafted["docket_entries"][0]["description"] = (
        "PROPOSED FINDINGS OF FACT AND CONCLUSIONS OF LAW by Meta Platforms"
    )
    _record_day(tmp_path, TODAY, [_activity(kind="opinion")])
    planned, without, _ = ai_rulings.plan_rulings(
        ai_rulings.owed_rulings(tmp_path, TODAY), lambda c, d: drafted, CONFIG
    )
    assert planned == [] and without == []


def test_stage_check_refuses_other_text_under_the_planned_digest(tmp_path: Path) -> None:
    plan = _planned(tmp_path / "data")
    stage = tmp_path / "stage"
    ai_rulings.stage_rulings(plan, lambda c, d: PAYLOAD, stage)
    path = stage / "ai-rulings/501.json"
    staged = json.loads(path.read_text())
    staged["text"] = ENTRY_DESCRIPTION
    path.write_text(json.dumps(staged))
    assert summaries.prune_stage(plan, stage) == [
        ("ai-rulings/501.json", "staged ruling text is not the planned ruling's scrubbed text")
    ]


def test_the_update_skips_an_invalid_summary_and_escapes_a_valid_one(tmp_path: Path) -> None:
    _summarize(tmp_path, lambda r: _response(GOOD_BODY))
    data = tmp_path / "data"
    path = ai_rulings.summary_path(data, 501)
    text = path.read_text()
    path.write_text(text.replace("The authors may amend", "The authors [x][y] | > # may amend"))
    rendered = render_ai_cases_update(
        build_ai_cases_update(data, date(2026, 11, 2), date(2026, 11, 8))
    )
    assert "The authors \\[x\\]\\[y\\] \\| \\> \\# may amend" in rendered
    path.write_text(text.replace("entry_id: 501", "entry_id: 777"))
    rendered = render_ai_cases_update(
        build_ai_cases_update(data, date(2026, 11, 2), date(2026, 11, 8))
    )
    assert "- Nov 2: Ruling on a motion (N.D. Cal. 3:23-cv-03417, entry 512)." in rendered
    assert "Summary written by" not in rendered


def test_stage_check_removes_an_ai_rulings_path_that_is_not_a_directory(tmp_path: Path) -> None:
    plan = _planned(tmp_path / "data")
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "ai-rulings").write_text("x")
    assert summaries.prune_stage(plan, stage) == [("ai-rulings", "not a case tree")]
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (stage / "ai-rulings").unlink(missing_ok=True)
    (stage / "ai-rulings").symlink_to(elsewhere)
    assert summaries.prune_stage(plan, stage) == [("ai-rulings", "not a case tree")]
