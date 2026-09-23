"""The case-summary lane: selection, the model call, the file contract, validation."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml
from tenacity import wait_none
from typer.testing import CliRunner

from fedcourtsai import summaries
from fedcourtsai.cli import app
from fedcourtsai.config import SummariesConfig, load_summaries_config
from fedcourtsai.paths import CasePaths
from fedcourtsai.pricing import MODEL_RATES, ModelRate
from fedcourtsai.schemas import CaseSummaryFrontMatter, SummaryPlan
from fedcourtsai.validate import validate_ledger
from tests.conftest import FixtureCorpus

runner = CliRunner()

CONFIG = SummariesConfig()
FAKE_KEY = "test-summaries-key-0123456789abcdef"

PAYLOAD: dict[str, Any] = {
    "CaseNumber": "25-100",
    "PetitionerTitle": "Doe, Petitioner",
    "ProceedingsandOrder": [{"Date": "Jan 02 2026", "Text": "Petition filed."}],
    "sJsonCreationDate": "09/22/2026",
}
DOCS = [("petition", "The petition text."), ("questions-presented", "Whether X.")]

GOOD_BODY = (
    "## What happened\n\n"
    + " ".join(["The parties disagreed about a contract and the lower courts ruled."] * 8)
    + "\n\n## What the Court is being asked\n\n"
    + " ".join(["The Court is asked if the contract binds the buyer."] * 6)
    + "\n\n## Where it stands\n\n"
    + "The petition is waiting to be considered at a conference. "
    + "No response has been filed yet."
)


def _record(
    payload: dict[str, Any] | None = None, docs: list[tuple[str, str]] | None = None
) -> summaries.CaseRecord:
    return summaries.CaseRecord(
        snapshot=date(2026, 9, 22),
        payload=payload if payload is not None else PAYLOAD,
        documents=docs if docs is not None else DOCS,
    )


def _commit_summary(data_root: Path, case_id: str, day: str, digest: str) -> Path:
    court, docket = case_id.split("/")
    front = CaseSummaryFrontMatter(
        case_id=case_id,
        snapshot=date.fromisoformat(day),
        record_digest=digest,
        model="claude-sonnet-5",
        prompt_digest="sha256:" + "0" * 64,
        generated_at=datetime(2026, 9, 22, 4, 0, tzinfo=UTC),
    )
    path = CasePaths(data_root, court, int(docket)).summary(day)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(summaries.render_summary(front, GOOD_BODY))
    return path


# --- selection ----------------------------------------------------------------


def test_record_digest_ignores_the_generation_stamp_only() -> None:
    base = summaries.record_digest(PAYLOAD, DOCS)
    restamped = {**PAYLOAD, "sJsonCreationDate": "09/23/2026"}
    assert summaries.record_digest(restamped, DOCS) == base
    changed = {**PAYLOAD, "ProceedingsandOrder": [*PAYLOAD["ProceedingsandOrder"], {"Text": "x"}]}
    assert summaries.record_digest(changed, DOCS) != base
    # Document order is not content; a document's text is.
    assert summaries.record_digest(PAYLOAD, list(reversed(DOCS))) == base
    assert summaries.record_digest(PAYLOAD, [*DOCS, ("brief-in-opposition", "BIO")]) != base


def _plan(
    data_root: Path,
    records: dict[str, summaries.CaseRecord | None],
    *,
    limit: int = 0,
) -> SummaryPlan:
    return summaries.plan_summaries(data_root, records, records.__getitem__, CONFIG, limit=limit)


def test_plan_owes_a_case_with_no_summary(tmp_path: Path) -> None:
    plan = _plan(tmp_path, {"scotus/1": _record()})
    assert [c.case_id for c in plan.cases] == ["scotus/1"]
    assert plan.cases[0].reason == "new"
    assert plan.cases[0].snapshot == date(2026, 9, 22)
    assert plan.cases[0].record_digest == summaries.record_digest(PAYLOAD, DOCS)
    assert plan.estimated_cost_usd_high > plan.estimated_cost_usd_low > 0


def test_plan_skips_a_case_whose_summary_matches_its_record(tmp_path: Path) -> None:
    _commit_summary(tmp_path, "scotus/1", "2026-09-20", summaries.record_digest(PAYLOAD, DOCS))
    # A newer snapshot day that only re-stamped the pull is the same record.
    restamped = {**PAYLOAD, "sJsonCreationDate": "09/23/2026"}
    plan = _plan(tmp_path, {"scotus/1": _record(restamped)})
    assert plan.cases == []
    assert plan.up_to_date == 1


def test_plan_owes_a_case_whose_docket_changed(tmp_path: Path) -> None:
    _commit_summary(tmp_path, "scotus/1", "2026-09-20", summaries.record_digest(PAYLOAD, DOCS))
    changed = {**PAYLOAD, "ProceedingsandOrder": [{"Text": "DISTRIBUTED for Conference."}]}
    plan = _plan(tmp_path, {"scotus/1": _record(changed)})
    assert [(c.case_id, c.reason) for c in plan.cases] == [("scotus/1", "record-changed")]


def test_plan_owes_a_case_whose_documents_alone_changed(tmp_path: Path) -> None:
    _commit_summary(tmp_path, "scotus/1", "2026-09-20", summaries.record_digest(PAYLOAD, DOCS))
    plan = _plan(tmp_path, {"scotus/1": _record(docs=[*DOCS, ("brief-in-opposition", "BIO")])})
    assert [c.reason for c in plan.cases] == ["record-changed"]


def test_plan_reads_the_newest_summary_only(tmp_path: Path) -> None:
    digest = summaries.record_digest(PAYLOAD, DOCS)
    _commit_summary(tmp_path, "scotus/1", "2026-09-01", "sha256:" + "1" * 64)
    _commit_summary(tmp_path, "scotus/1", "2026-09-20", digest)
    assert _plan(tmp_path, {"scotus/1": _record()}).cases == []


def test_plan_limit_prefers_cases_without_a_summary(tmp_path: Path) -> None:
    _commit_summary(tmp_path, "scotus/1", "2026-09-20", "sha256:" + "1" * 64)
    plan = _plan(
        tmp_path,
        {"scotus/1": _record(), "scotus/2": _record(), "scotus/3": None},
        limit=1,
    )
    assert [c.case_id for c in plan.cases] == ["scotus/2"]
    assert plan.deferred == 1
    assert plan.no_snapshot == ["scotus/3"]
    assert plan.eligible == 3


def test_summarize_plan_cli_reads_only_predicted_cases(fixture_corpus: FixtureCorpus) -> None:
    # Eligibility is a committed prediction; scotus/305 has one, nothing else does.
    marker = (
        CasePaths(fixture_corpus.data_root, "scotus", 305).event("evt-petition-cert").base
        / "predictions/claude-baseline/20260901T000000Z/prediction.json"
    )
    marker.parent.mkdir(parents=True)
    marker.write_text("{}")

    result = runner.invoke(app, ["summarize-plan", "--corpus-backend", "local"])

    assert result.exit_code == 0, result.output
    plan = SummaryPlan.model_validate_json(result.stdout)
    assert plan.eligible == 1
    assert [c.case_id for c in plan.cases] == ["scotus/305"]
    assert plan.cases[0].snapshot == date(2025, 3, 3)


# --- the model call -------------------------------------------------------------


def _stage(stage_root: Path, court: str = "scotus", docket: int = 1) -> None:
    paths = CasePaths(stage_root, court, docket)
    paths.snapshot("2026-09-22").parent.mkdir(parents=True)
    paths.snapshot("2026-09-22").write_text(json.dumps(PAYLOAD))
    paths.documents_dir.mkdir(parents=True)
    paths.document("petition").write_text("P" * 150_000)
    paths.documents_manifest.write_text(
        json.dumps([{"kind": "petition", "entry_date": "Jan 02 2026", "truncated": False}])
    )


def _response(text: str, stop: str = "end_turn") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [{"type": "text", "text": text}],
            "stop_reason": stop,
            "usage": {"input_tokens": 50_000, "output_tokens": 400},
        },
    )


def _run(
    tmp_path: Path, handler: Callable[[httpx.Request], httpx.Response]
) -> tuple[summaries.SummarizeOutcome, SummaryPlan]:
    stage = tmp_path / "stage"
    data = tmp_path / "data"
    _stage(stage)
    plan = _plan(data, {"scotus/1": _record()})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        outcome = summaries.summarize_plan(
            plan,
            stage_root=stage,
            data_root=data,
            config=CONFIG,
            prompt_bytes=b"the prompt",
            client=client,
            api_key=FAKE_KEY,
            now=lambda: datetime(2026, 9, 23, 4, 0, 1, 5, tzinfo=UTC),
            wait=wait_none(),
        )
    return outcome, plan


def test_summarize_writes_the_file_with_harness_front_matter(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _response(GOOD_BODY)

    outcome, plan = _run(tmp_path, handler)

    assert outcome.skipped == []
    [(_, path, cost)] = outcome.written
    assert path == CasePaths(tmp_path / "data", "scotus", 1).summary("2026-09-22")
    front, body = summaries.parse_summary(path.read_text())
    assert front.case_id == "scotus/1"
    assert front.snapshot == date(2026, 9, 22)
    assert front.record_digest == plan.cases[0].record_digest
    assert front.model == "claude-sonnet-5"
    assert front.prompt_digest == summaries.prompt_digest(b"the prompt")
    assert front.generated_at == datetime(2026, 9, 23, 4, 0, 1, tzinfo=UTC)
    assert front.usage is not None and front.usage.input_tokens == 50_000
    assert cost == pytest.approx(50_000 * 2 / 1e6 + 400 * 10 / 1e6)
    assert body.strip() == GOOD_BODY.strip()
    # The request carries the prompt and the record, and nothing that retrieves.
    [request] = requests
    sent = json.loads(request.content)
    assert "tools" not in sent
    assert sent["model"] == "claude-sonnet-5"
    assert sent["system"] == "the prompt"
    assert sent["thinking"] == {"type": "disabled"}
    assert sent["max_tokens"] == CONFIG.max_output_tokens
    assert request.headers["x-api-key"] == FAKE_KEY
    assert request.headers["anthropic-version"] == summaries.ANTHROPIC_VERSION
    record = sent["messages"][0]["content"]
    assert "[truncated: 100000 of 150000 characters shown]" in record
    assert "P" * 100_001 not in record
    # A rerun over the now up-to-date ledger owes nothing.
    assert _plan(tmp_path / "data", {"scotus/1": _record()}).cases == []


@pytest.mark.parametrize(
    "body",
    [
        "Just a paragraph with no sections at all. " * 20,
        GOOD_BODY.replace("## Where it stands", "## Status"),
        GOOD_BODY.replace(
            "## What the Court is being asked\n\n",
            "## What the Court is being asked\n\nWhether the contract binds. ",
        ),
        "## What happened\n\nShort.\n\n## What the Court is being asked\n\nShort."
        + "\n\n## Where it stands\n\nShort.",
        GOOD_BODY + "\n\nThe key is " + FAKE_KEY,
    ],
    ids=["no-sections", "wrong-heading", "whether", "too-short", "secret"],
)
def test_summarize_rejects_a_body_off_the_contract(tmp_path: Path, body: str) -> None:
    outcome, _ = _run(tmp_path, lambda request: _response(body))
    assert outcome.written == []
    [(_, reason, cost)] = outcome.skipped
    assert reason.startswith("rejected:")
    assert cost > 0  # a rejected response still cost its tokens
    assert not (tmp_path / "data" / "cases").exists()


def test_summarize_rejects_a_truncated_response(tmp_path: Path) -> None:
    outcome, _ = _run(tmp_path, lambda request: _response(GOOD_BODY, stop="max_tokens"))
    assert outcome.written == []
    assert "max_tokens" in outcome.skipped[0][1]


def test_summarize_retries_a_throttle_then_succeeds(tmp_path: Path) -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(429, json={"type": "error"})
        if len(calls) == 2:
            return httpx.Response(529, json={"type": "error"})
        return _response(GOOD_BODY)

    outcome, _ = _run(tmp_path, handler)
    assert len(calls) == 3
    assert len(outcome.written) == 1


def test_summarize_skips_a_case_that_keeps_failing(tmp_path: Path) -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(500, json={"type": "error"})

    outcome, _ = _run(tmp_path, handler)
    assert outcome.written == []
    assert outcome.skipped == [("scotus/1", "HTTP 500", 0.0)]
    assert len(calls) == 5


def test_summarize_does_not_retry_a_client_error(tmp_path: Path) -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(400, json={"type": "error"})

    outcome, _ = _run(tmp_path, handler)
    assert outcome.skipped[0][1] == "HTTP 400"
    assert len(calls) == 1


def test_summarize_skips_a_case_whose_staged_snapshot_moved(tmp_path: Path) -> None:
    stage = tmp_path / "stage"
    _stage(stage)
    plan = _plan(tmp_path / "data", {"scotus/1": _record()})
    moved = plan.model_copy(
        update={"cases": [plan.cases[0].model_copy(update={"snapshot": date(2026, 9, 23)})]}
    )
    with httpx.Client(transport=httpx.MockTransport(lambda r: _response(GOOD_BODY))) as client:
        outcome = summaries.summarize_plan(
            moved,
            stage_root=stage,
            data_root=tmp_path / "data",
            config=CONFIG,
            prompt_bytes=b"p",
            client=client,
            api_key=FAKE_KEY,
        )
    assert outcome.written == []
    assert "no staged snapshot" in outcome.skipped[0][1]


def test_summarize_refuses_a_plan_for_another_model(tmp_path: Path) -> None:
    plan = _plan(tmp_path, {"scotus/1": _record()}).model_copy(update={"model": "other"})
    with (
        httpx.Client(transport=httpx.MockTransport(lambda r: _response(GOOD_BODY))) as client,
        pytest.raises(ValueError, match="plan was made for model"),
    ):
        summaries.summarize_plan(
            plan,
            stage_root=tmp_path,
            data_root=tmp_path,
            config=CONFIG,
            prompt_bytes=b"p",
            client=client,
            api_key=FAKE_KEY,
        )


def test_summarize_cli_refuses_without_a_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(summaries.API_KEY_ENV, raising=False)
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    result = runner.invoke(app, ["summarize", "--plan", str(plan), "--staged", str(tmp_path)])
    assert result.exit_code == 2


# --- validation -------------------------------------------------------------------


def test_validate_accepts_a_committed_summary(tmp_path: Path) -> None:
    _commit_summary(tmp_path, "scotus/1", "2026-09-20", "sha256:" + "a" * 64)
    result = validate_ledger(tmp_path)
    assert result.ok, result.problems
    assert result.checked == 1


def test_validate_rejects_summaries_off_the_contract(tmp_path: Path) -> None:
    good = _commit_summary(tmp_path, "scotus/1", "2026-09-20", "sha256:" + "a" * 64)
    # Named for another day than its front matter's snapshot.
    good.rename(good.with_name("2026-09-21.md"))
    # Front matter naming another case than its path.
    other = _commit_summary(tmp_path, "scotus/2", "2026-09-20", "sha256:" + "a" * 64)
    other.write_text(other.read_text().replace("case_id: scotus/2", "case_id: scotus/9"))
    # Body missing a section.
    third = _commit_summary(tmp_path, "scotus/3", "2026-09-20", "sha256:" + "a" * 64)
    third.write_text(third.read_text().replace("## Where it stands", "## Status"))
    # No front matter; and a stray non-summary file.
    bare = CasePaths(tmp_path, "scotus", 4).summary("2026-09-20")
    bare.parent.mkdir(parents=True)
    bare.write_text(GOOD_BODY)
    (bare.parent / "notes.txt").write_text("x")

    result = validate_ledger(tmp_path)

    assert not result.ok
    joined = "\n".join(result.problems)
    assert "does not match the file name" in joined
    assert "does not match the path" in joined
    assert "sections must be exactly" in joined
    assert "no YAML front matter" in joined
    assert "not a summary file" in joined


def test_validate_front_matter_rejects_a_bad_digest(tmp_path: Path) -> None:
    path = _commit_summary(tmp_path, "scotus/1", "2026-09-20", "sha256:" + "a" * 64)
    path.write_text(path.read_text().replace("sha256:" + "a" * 64, "not-a-digest"))
    assert not validate_ledger(tmp_path).ok


# --- config and pricing -------------------------------------------------------------


def test_repo_config_pins_the_summary_model_and_caps() -> None:
    cfg = load_summaries_config(Path("config"))
    assert cfg.model == "claude-sonnet-5"
    assert cfg.max_output_tokens == 2000
    assert cfg.max_document_chars == 100_000
    tracking = yaml.safe_load((Path("config") / "tracking.yaml").read_text())
    assert "model" in tracking["summaries"]


def test_summaries_config_defaults_when_the_section_is_absent(tmp_path: Path) -> None:
    assert load_summaries_config(tmp_path) == SummariesConfig()


def test_the_summary_model_is_priced() -> None:
    assert MODEL_RATES["claude-sonnet-5"] == ModelRate(2.0, 10.0)


# --- the publish jail -------------------------------------------------------------


def test_summary_paths_admits_only_summary_writes(tmp_path: Path) -> None:
    good = "data/cases/scotus/9026000239/summaries/2026-09-20.md"
    changes = tmp_path / "changes.txt"
    changes.write_text(
        f"A\t{good}\n"
        + "M\tdata/cases/scotus/1/summaries/2026-09-21.md\n"
        + "D\tdata/cases/scotus/2/summaries/2026-09-20.md\n"
        + "A\tdata/cases/scotus/3/events/evt-x/event.yaml\n"
        + "A\tdata/cases/scotus/../4/summaries/2026-09-20.md\n"
        + "A\tdata/cases/scotus/abc/summaries/2026-09-20.md\n"
    )

    lenient = runner.invoke(app, ["summary-paths", "--name-status-file", str(changes)])
    assert lenient.exit_code == 0
    assert lenient.stdout.split() == ["data/cases/scotus/1/summaries/2026-09-21.md", good]

    strict = runner.invoke(app, ["summary-paths", "--name-status-file", str(changes), "--strict"])
    assert strict.exit_code == 1
    assert strict.output.count("not a case summary write") == 4


def test_the_paths_helper_and_the_jail_agree() -> None:
    path = CasePaths(Path("data"), "scotus", 9026000239).summary("2026-09-20")
    assert summaries.is_summary_path(path.as_posix())
