"""Blind grading: the staged copy carries no identity, and the round trip restores it.

Two failures matter more than the rest and both are silent, so both are pinned
here. A leaked identifier in the staging area defeats the whole barrier without
anything erroring; and an alias that survives to the ledger keys an evaluation on
a name no predictor answers to — which ``stamp-cell`` absorbs quietly (its
prediction join simply misses and writes no claim block) and only ``validate``
reports.

The leak test deliberately does **not** reuse the module's own scrub pattern to
decide what counts as a leak: a test that grades an implementation with the
implementation's own ruler cannot see a boundary bug. It reads the forbidden
terms off the live registries and pricing tables and searches for them as plain
case-insensitive substrings, in file bodies *and* in filenames.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import blinding, tool_usage
from fedcourtsai.blinding import (
    ALIAS_PREFIX,
    ENGINE_TERMS,
    BlindingError,
    assign_aliases,
    provision_blinded_predictions,
    unblind_evaluations,
)
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pricing import DEFAULT_MODELS, MODEL_RATES
from fedcourtsai.registry import load_evaluators, load_predictors
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    Disposition,
    Evaluation,
    EvaluatorConfig,
    EventKind,
    ModelUsage,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    PredictorConfig,
    RetrievalCall,
    RetrievalLog,
    Stage,
)
from fedcourtsai.serialize import write_json, write_text, write_yaml
from fedcourtsai.validate import (
    check_evaluation_targets,
    run_ledger_referential_checks,
    validate_ledger,
)

runner = CliRunner()

CONFIG_ROOT = Path("config")
COURT = "scotus"
DOCKET = 73369987
EVENT = "evt-petition-disposition"
PREDICT_RUN = "20260718T000130Z"
EVALUATE_RUN = "20260801T090000Z"
EVALUATOR = "claude-judge"

# The three registry predictors, so the fixture ledger is the shape a real cell
# blinds — one candidate per engine, ids that embed the engine name.
CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("claude-baseline", "claude-code", "claude-fable-5"),
    ("codex-baseline", "codex", "gpt-5.6-sol"),
    ("gemini-baseline", "gemini", "gemini-3.1-pro-preview"),
)


# --- fixtures -----------------------------------------------------------------


def _seed_event(data_root: Path) -> None:
    event_paths = CasePaths(data_root, COURT, DOCKET).event(EVENT)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=EVENT,
            case_id=f"{COURT}/{DOCKET}",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for a writ of certiorari",
            resolved=True,
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id=f"{COURT}/{DOCKET}",
            event_id=EVENT,
            resolved_at=date(2026, 7, 20),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )


def _seed_prediction(
    data_root: Path,
    predictor_id: str,
    engine: str,
    model: str,
    *,
    run_id: str = PREDICT_RUN,
    created_at: datetime = datetime(2026, 7, 18, tzinfo=UTC),
    reasoning_doc: str = "reasoning.md",
) -> Path:
    """One predictor's full cell, in the shape the committed ledger actually holds."""
    event_paths = CasePaths(data_root, COURT, DOCKET).event(EVENT)
    directory = event_paths.prediction_dir(predictor_id, run_id)
    write_json(
        event_paths.prediction(predictor_id, run_id),
        Prediction(
            case_id=f"{COURT}/{DOCKET}",
            event_id=EVENT,
            predictor_id=predictor_id,
            engine=engine,
            model=model,
            run_id=run_id,
            created_at=created_at,
            input_snapshot=f"data/cases/{COURT}/{DOCKET}/record/snapshots/2026-07-17.json",
            granted=0,
            probability=0.04,
            predicted_disposition=Disposition.denied,
            reasoning_doc=reasoning_doc,
            predicted_reasoning_doc="predicted_reasoning.md",
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 7, 17),
                signals_observable=True,
                distribution_count=1,
                band="baseline",
                salience_version="sal-v1",
                term=2025,
            ),
        ),
    )
    write_text(
        directory / reasoning_doc,
        f"# Reasoning — {predictor_id}\n\nOne distribution; the band rate governs.\n",
    )
    write_text(
        directory / "predicted_reasoning.md",
        f"# Forecast — {predictor_id}\n\nDenial without comment at the next conference.\n",
    )
    # The self-identifying title line 125 committed retrieval.md files carry, plus
    # the digit-suffixed self-reference a model writes in prose.
    write_text(
        directory / "retrieval.md",
        f"# Retrieval log — {COURT}/{DOCKET} / {predictor_id} / {run_id}\n\n"
        f"Ran as {model} on {engine}. I am GPT5. Consulted `metrics/statpack.md` only.\n",
    )
    write_json(
        event_paths.prediction_retrieval_log(predictor_id, run_id),
        RetrievalLog(
            case_id=f"{COURT}/{DOCKET}",
            run_id=run_id,
            role="predictor",
            actor_id=predictor_id,
            engine=engine,
            mode="forward",
            mcp_servers=["courtlistener==1.1.0"],
            mcp_tools=["search"],
            calls=[
                RetrievalCall(
                    tool="read_file",
                    # A query slice quoting the cell's own output path — the leak
                    # a field-only mask would sail straight past.
                    query=f'{{"file_path": "…/predictions/{predictor_id}/{run_id}/"}}',
                    params_digest="7b04ede542faba4e",
                ),
            ],
        ),
    )
    # Deliberately not staged: dropping beats masking on the free-text files.
    write_json(
        event_paths.prediction_flags(predictor_id, run_id),
        AgentFlags(
            case_id=f"{COURT}/{DOCKET}",
            run_id=run_id,
            role="predictor",
            actor_id=predictor_id,
            flags=[AgentFlag(category="data-quality", severity="info", message="snapshot thin")],
        ),
    )
    write_json(
        event_paths.prediction_usage(predictor_id, run_id),
        ModelUsage(
            case_id=f"{COURT}/{DOCKET}",
            event_id=EVENT,
            run_id=run_id,
            role="predictor",
            actor_id=predictor_id,
            engine=engine,
            model=model,
            created_at=created_at,
            input_tokens=1000,
            output_tokens=200,
            estimated_cost_usd=0.02,
        ),
    )
    return directory


@pytest.fixture
def ledger(tmp_path: Path) -> Path:
    """A resolved event with all three registry predictors' full cells committed."""
    data_root = tmp_path / "data"
    _seed_event(data_root)
    for predictor_id, engine, model in CANDIDATES:
        _seed_prediction(data_root, predictor_id, engine, model)
    return data_root


def _map_dir(data_root: Path) -> Path:
    """Runner-local, outside the case tree — where the real cell keeps the key."""
    return data_root.parent / ".blinding"


def _map_path(data_root: Path) -> Path:
    return blinding.map_path_for(
        _map_dir(data_root), court=COURT, docket=DOCKET, event_id=EVENT, run_id=EVALUATE_RUN
    )


def _blind(data_root: Path, *, run_id: str = EVALUATE_RUN) -> blinding.BlindingResult:
    return provision_blinded_predictions(
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court=COURT,
        docket=DOCKET,
        event_id=EVENT,
        run_id=run_id,
        map_dir=_map_dir(data_root),
    )


def _unblind(data_root: Path) -> tuple[tuple[str, str], ...]:
    return unblind_evaluations(
        data_root=data_root,
        court=COURT,
        docket=DOCKET,
        event_id=EVENT,
        evaluator_id=EVALUATOR,
        run_id=EVALUATE_RUN,
        map_dir=_map_dir(data_root),
    )


def _staged_files(data_root: Path) -> list[Path]:
    root = CasePaths(data_root, COURT, DOCKET).blinded_predictions
    return sorted(p for p in root.rglob("*") if p.is_file())


def _forbidden_terms() -> list[str]:
    """Every identifier the staged copy must not contain, read off the live sources.

    Built from the registries, the pricing tables, and the module's family list
    rather than from a constant in this file, so adding a fourth engine to
    ``config/predictors.yaml`` — or re-pricing a model — fails here rather than
    leaking silently.
    """
    terms: set[str] = {*ENGINE_TERMS, *DEFAULT_MODELS.values(), *MODEL_RATES}
    actors: list[PredictorConfig | EvaluatorConfig] = [
        *load_predictors(CONFIG_ROOT / "predictors.yaml"),
        *load_evaluators(CONFIG_ROOT / "evaluators.yaml"),
    ]
    for entry in actors:
        terms.update({entry.id, str(entry.engine), entry.model or ""})
    for predictor_id, engine, model in CANDIDATES:
        terms.update({predictor_id, engine, model})
    return sorted(term for term in terms if term)


# --- what the grader may see --------------------------------------------------


def test_no_identifier_survives_anywhere_in_the_staged_copy(ledger: Path) -> None:
    """Every staged byte and every staged filename is free of predictor/engine/model names."""
    _blind(ledger)
    forbidden = _forbidden_terms()
    files = _staged_files(ledger)
    assert files, "blinding staged nothing"
    for path in files:
        haystack = f"{path.name}\n{path.read_text()}".lower()
        for term in forbidden:
            assert term.lower() not in haystack, f"{term!r} survives in {path}"
    # The digit-suffixed self-reference a letter-and-digit trailing boundary lets through.
    assert not any("gpt5" in path.read_text().lower() for path in files)


def test_the_alias_map_is_not_in_the_tree_the_grader_is_sent_into(ledger: Path) -> None:
    """The key does not sit beside the lock: an `ls record/` must not disclose it."""
    result = _blind(ledger)
    assert result.map_path.is_file()
    assert not result.map_path.is_relative_to(ledger)
    forbidden = _forbidden_terms()
    record = CasePaths(ledger, COURT, DOCKET).record
    for path in sorted(p for p in record.rglob("*") if p.is_file()):
        body = f"{path.name}\n{path.read_text()}".lower()
        assert not any(term.lower() in body for term in forbidden), path


def test_an_agent_chosen_prose_filename_is_staged_under_the_harness_name(tmp_path: Path) -> None:
    """A pointer is the agent's word, and a filename is as identifying as its contents."""
    data_root = tmp_path / "data"
    _seed_event(data_root)
    _seed_prediction(
        data_root,
        "claude-baseline",
        "claude-code",
        "claude-fable-5",
        reasoning_doc="claude-notes.md",
    )
    result = _blind(data_root)
    alias_dir = CasePaths(data_root, COURT, DOCKET).blinded_prediction_dir(
        result.candidates[0].alias
    )
    assert (alias_dir / "reasoning.md").is_file()
    assert not (alias_dir / "claude-notes.md").exists()
    # The masked pointer names the staged file, so "follow the pointer" resolves.
    payload = json.loads((alias_dir / "prediction.json").read_text())
    assert payload["reasoning_doc"] == "reasoning.md"
    assert (alias_dir / payload["reasoning_doc"]).is_file()


def test_retrieval_md_self_identification_is_scrubbed(ledger: Path) -> None:
    """The title line the committed logs carry names the predictor; the staged one does not."""
    result = _blind(ledger)
    alias_dir = CasePaths(ledger, COURT, DOCKET).blinded_prediction_dir(result.candidates[0].alias)
    staged = (alias_dir / "retrieval.md").read_text()
    assert blinding.IDENTITY_REDACTION in staged
    assert "Retrieval log" in staged, "the scrub replaces identity, not the document"


def test_prediction_identity_fields_are_masked(ledger: Path) -> None:
    result = _blind(ledger)
    for candidate in result.candidates:
        path = (
            CasePaths(ledger, COURT, DOCKET).blinded_prediction_dir(candidate.alias)
            / "prediction.json"
        )
        payload = json.loads(path.read_text())
        assert payload["predictor_id"] == candidate.alias
        assert payload["engine"] is None
        assert payload["model"] is None
        assert "process_version" not in payload
        # Relativized: the repo-rooted spelling is an engine fingerprint, and the
        # leading path only restates the case the grader already knows.
        assert payload["input_snapshot"] == "2026-07-17.json"
        # What the grade actually reads is carried through untouched.
        assert payload["probability"] == pytest.approx(0.04)
        assert payload["context"]["band"] == "baseline"


def test_retrieval_log_keeps_what_the_leakage_grading_reads(ledger: Path) -> None:
    result = _blind(ledger)
    path = (
        CasePaths(ledger, COURT, DOCKET).blinded_prediction_dir(result.candidates[0].alias)
        / "retrieval_log.json"
    )
    payload = json.loads(path.read_text())
    assert payload["actor_id"] == result.candidates[0].alias
    assert payload["engine"] is None
    assert payload["mode"] == "forward", "the leakage grading is keyed on the mode"
    assert payload["calls"], "the call list is the leakage evidence and must survive"
    assert blinding.IDENTITY_REDACTION in payload["calls"][0]["query"]
    # The fixture's engine-flavored "read_file" is respelled: raw vocabularies
    # are disjoint per engine, so a raw name would name the candidate.
    assert payload["calls"][0]["tool"] == "file-read"


def test_staged_tool_names_are_engine_neutral() -> None:
    """The three engines' disjoint tool vocabularies collapse to one spelling.

    The registry holds one predictor per engine, so a raw tool name on the
    grader's required reading path names the candidate. The classes keep what
    the leakage grading distinguishes — shell/file/web/MCP — and an MCP name
    keeps its server and method, spelled identically whichever engine logged
    it.
    """
    assert blinding.neutral_tool_class("Bash") == "shell"
    assert blinding.neutral_tool_class("exec") == "shell"
    assert blinding.neutral_tool_class("run_shell_command") == "shell"
    assert (
        blinding.neutral_tool_class("mcp__courtlistener__search")
        == blinding.neutral_tool_class("mcp_courtlistener_search")
        == "mcp:courtlistener:search"
    )
    assert (
        blinding.neutral_tool_class("mcp_courtlistener_get_endpoint_item")
        == "mcp:courtlistener:get_endpoint_item"
    )
    assert blinding.neutral_tool_class("google_web_search") == "web-search"
    assert blinding.neutral_tool_class("WebFetch") == "web-fetch"
    # The payload-TYPE fallbacks a provider-side call is captured under: the
    # hosted web search is the row the leakage doctrine singles out, so it
    # must stage as web-search — and "web-search" appearing on every engine
    # is also what stops the class reading as "not codex".
    assert blinding.neutral_tool_class("web_search_call") == "web-search"
    assert blinding.neutral_tool_class("local_shell_call") == "shell"
    assert blinding.neutral_tool_class("apply_patch") == "file-write"
    assert blinding.neutral_tool_class("search_file_content") == "file-search"
    assert blinding.neutral_tool_class("read_many_files") == "file-read"
    # An unmapped name collapses rather than passing through — pass-through
    # would leak any engine-specific name the map has not met.
    assert blinding.neutral_tool_class("update_topic") == "other"
    assert blinding.neutral_tool_class("ToolSearch") == "other"


def test_every_known_web_tool_stages_as_a_web_class() -> None:
    """The web-tool inventory and the neutral classes cannot drift apart.

    ``tool_usage`` owns the canonical set of names the engines' web calls are
    logged under; a member missing from the blinding map would stage as
    "other", making the web class an inverse engine fingerprint and the
    hosted-search leakage instruction unexecutable on the staged copy.
    """
    for name in tool_usage._WEB_TOOLS:
        assert blinding.neutral_tool_class(name).startswith("web-"), name


def test_free_text_cell_files_are_not_staged_at_all(ledger: Path) -> None:
    """`usage.json` / `tooling.json` / `flags.json` are dropped rather than masked."""
    _blind(ledger)
    staged = {path.name for path in _staged_files(ledger)}
    assert staged == {
        "prediction.json",
        "reasoning.md",
        "predicted_reasoning.md",
        "retrieval.md",
        "retrieval_log.json",
    }


def test_the_staging_area_does_not_break_the_gate(ledger: Path) -> None:
    """A masked prediction is not a `Prediction`, and `validate` knows record/ is not ledger."""
    _blind(ledger)
    verdict = validate_ledger(ledger)
    assert verdict.ok, verdict.problems
    assert verdict.checked, "the scan skipped record/, not the whole ledger"


def test_the_provisioning_skip_is_anchored_on_the_case_layout(tmp_path: Path) -> None:
    """An unanchored `record` match would validate nothing under a root named `record`."""
    data_root = tmp_path / "record" / "data"
    _seed_event(data_root)
    _seed_prediction(data_root, "claude-baseline", "claude-code", "claude-fable-5")
    CasePaths(data_root, COURT, DOCKET).event(EVENT).prediction(
        "claude-baseline", PREDICT_RUN
    ).write_text('{"nonsense": true}')
    verdict = validate_ledger(data_root)
    assert not verdict.ok, "a malformed prediction under a `record`-named root must still fail"


def test_the_latest_prediction_is_the_one_downstream_scores(ledger: Path) -> None:
    """The harness clock decides (created_at here — the runs are unstamped),
    matching every join the harness makes on the same cell."""
    _seed_prediction(
        ledger,
        "claude-baseline",
        "claude-code",
        "claude-fable-5",
        run_id="20260101T000000Z",  # sorts first by name, latest by created_at
        created_at=datetime(2026, 12, 1, tzinfo=UTC),
    )
    latest = blinding.latest_prediction_dirs(CasePaths(ledger, COURT, DOCKET).event(EVENT))
    assert latest["claude-baseline"].name == "20260101T000000Z"


def test_a_created_at_tie_breaks_the_way_the_stamp_breaks_it(ledger: Path) -> None:
    """`max` over path-sorted runs takes the FIRST maximum — the lowest run name.

    The stamp and the stratifier both do exactly that, so the grader and the
    harness must not read different runs when two carry the same `created_at`.
    """
    _seed_prediction(
        ledger,
        "claude-baseline",
        "claude-code",
        "claude-fable-5",
        run_id="20260101T000000Z",  # same created_at as the fixture's run
    )
    latest = blinding.latest_prediction_dirs(CasePaths(ledger, COURT, DOCKET).event(EVENT))
    assert latest["claude-baseline"].name == "20260101T000000Z"

    event_dir = CasePaths(ledger, COURT, DOCKET).event(EVENT).base
    files = sorted(event_dir.glob("predictions/claude-baseline/*/prediction.json"))
    downstream = max(files, key=lambda p: blinding._cell_clock(p.parent))
    assert downstream.parent == latest["claude-baseline"]


# --- the alias is not a lookup ------------------------------------------------


def test_alias_order_is_not_predictor_id_sort_order(ledger: Path) -> None:
    """At least one seed permutes the candidates away from their sorted order.

    Sorted order would make the alias a lookup: read the registry, sort, read off
    the mapping. The seeded shuffle sometimes *coincides* with sorted order — one
    permutation in six for three candidates — so this asserts over a set of run
    ids rather than one.
    """
    predictor_ids = [predictor_id for predictor_id, _, _ in CANDIDATES]
    ordered = sorted(predictor_ids)
    permuted = [
        list(
            assign_aliases(
                predictor_ids, case_id=f"{COURT}/{DOCKET}", event_id=EVENT, run_id=run
            ).values()
        )
        for run in (f"2026080{n}T000000Z" for n in range(1, 8))
    ]
    assert any(order != ordered for order in permuted), "the alias order is predictor-id sort order"


def test_alias_assignment_is_deterministic(ledger: Path) -> None:
    first = _blind(ledger)
    second = _blind(ledger)
    assert [(c.alias, c.predictor_id) for c in first.candidates] == [
        (c.alias, c.predictor_id) for c in second.candidates
    ]


def test_the_seed_carries_the_case_not_just_the_run(ledger: Path) -> None:
    """Two cases in one run must not share a permutation, or one leak unlocks the fan-out."""
    predictor_ids = [predictor_id for predictor_id, _, _ in CANDIDATES]
    here = assign_aliases(predictor_ids, case_id="scotus/1", event_id=EVENT, run_id=EVALUATE_RUN)
    there = assign_aliases(predictor_ids, case_id="scotus/2", event_id=EVENT, run_id=EVALUATE_RUN)
    assert here != there


def test_blinding_refuses_an_event_with_nothing_to_score(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _seed_event(data_root)
    with pytest.raises(BlindingError, match="nothing to score"):
        _blind(data_root)


def test_restaging_clears_a_stale_candidate(ledger: Path) -> None:
    """A re-run must not leave a previous run's alias behind for the grader to score."""
    _blind(ledger, run_id="20260801T000000Z")
    stale = CasePaths(ledger, COURT, DOCKET).blinded_prediction_dir("candidate-z")
    write_text(stale / "reasoning.md", "left over\n")
    _blind(ledger, run_id=EVALUATE_RUN)
    assert not stale.exists()


# --- the round trip -----------------------------------------------------------


def _seed_evaluations(data_root: Path, result: blinding.BlindingResult) -> None:
    """The grader's output, keyed on the aliases it was given — prose and flags included."""
    event_paths = CasePaths(data_root, COURT, DOCKET).event(EVENT)
    for candidate in result.candidates:
        write_json(
            event_paths.evaluation(EVALUATOR, candidate.alias, EVALUATE_RUN),
            Evaluation(
                case_id=f"{COURT}/{DOCKET}",
                event_id=EVENT,
                predictor_id=candidate.alias,
                evaluator_id=EVALUATOR,
                engine="claude-code",
                run_id=EVALUATE_RUN,
                created_at=datetime(2026, 8, 1, tzinfo=UTC),
                correct=1,
                brier_score=0.0016,
                reasoning_quality=0.7,
            ),
        )
        write_text(
            event_paths.evaluation_dir(EVALUATOR, candidate.alias, EVALUATE_RUN) / "evaluation.md",
            f"{candidate.alias} was sound on the band base rate.\n",
        )
    # The durable channel: a leakage note keyed on an alias the maintainer who
    # reads the run PR has no way to resolve.
    write_json(
        event_paths.evaluation_flags(EVALUATOR, EVALUATE_RUN),
        AgentFlags(
            case_id=f"{COURT}/{DOCKET}",
            run_id=EVALUATE_RUN,
            role="evaluator",
            actor_id=EVALUATOR,
            flags=[
                AgentFlag(
                    category="data-quality",
                    severity="warning",
                    message=f"{result.candidates[0].alias} cited a post-decision order",
                )
            ],
        ),
    )


def test_round_trip_restores_every_predictor_id_exactly(ledger: Path) -> None:
    result = _blind(ledger)
    _seed_evaluations(ledger, result)

    moved = _unblind(ledger)
    assert dict(moved) == {c.alias: c.predictor_id for c in result.candidates}

    event_paths = CasePaths(ledger, COURT, DOCKET).event(EVENT)
    for candidate in result.candidates:
        path = event_paths.evaluation(EVALUATOR, candidate.predictor_id, EVALUATE_RUN)
        assert json.loads(path.read_text())["predictor_id"] == candidate.predictor_id
        prose = (path.parent / "evaluation.md").read_text()
        assert candidate.predictor_id in prose and candidate.alias not in prose
        assert not event_paths.evaluation_dir(EVALUATOR, candidate.alias, EVALUATE_RUN).exists()

    verdict = validate_ledger(ledger)
    assert verdict.ok, verdict.problems
    for check in run_ledger_referential_checks(ledger):
        assert check.passed, (check.name, check.problems)


def test_the_evaluators_flags_are_resolved_too(ledger: Path) -> None:
    """A leakage note reaches a maintainer through the run PR; it must name a predictor."""
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    _unblind(ledger)
    flags = json.loads(
        CasePaths(ledger, COURT, DOCKET)
        .event(EVENT)
        .evaluation_flags(EVALUATOR, EVALUATE_RUN)
        .read_text()
    )
    message = flags["flags"][0]["message"]
    assert result.candidates[0].predictor_id in message
    assert ALIAS_PREFIX not in message


def test_an_earlier_committed_run_is_left_byte_identical(ledger: Path) -> None:
    """Un-aliasing rewrites what this cell wrote and nothing else.

    The evaluator directory also holds every earlier committed run for the event.
    Those were written by an agent, so they do not match the repo's canonical JSON
    formatting — a touch-everything pass would reformat them, they would land in
    the collect job's diff as **modifications**, and the append-only path jail
    would silently cost the whole run its auto-merge.
    """
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    event_paths = CasePaths(ledger, COURT, DOCKET).event(EVENT)
    earlier = event_paths.evaluation(
        EVALUATOR, result.candidates[0].predictor_id, "20260101T000000Z"
    )
    earlier.parent.mkdir(parents=True, exist_ok=True)
    # Agent-written spelling: four-space indent, unsorted keys, no trailing newline.
    real = result.candidates[0].predictor_id
    body = f'{{\n    "predictor_id": "{real}",\n    "case_id": "{COURT}/{DOCKET}"\n}}'
    earlier.write_text(body)
    (earlier.parent / "evaluation.md").write_text("no trailing newline")

    _unblind(ledger)

    assert earlier.read_text() == body
    assert (earlier.parent / "evaluation.md").read_text() == "no trailing newline"


def test_an_alias_that_survives_fails_the_gate_loudly(ledger: Path) -> None:
    """The self-check on the ordering rule: `check_evaluation_targets` reports the orphan."""
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    check = check_evaluation_targets(ledger)
    assert not check.passed
    assert any(ALIAS_PREFIX in problem for problem in check.problems)


def test_unblinding_is_idempotent(ledger: Path) -> None:
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    assert _unblind(ledger)
    assert _unblind(ledger) == ()
    verdict = validate_ledger(ledger)
    assert verdict.ok, verdict.problems


def test_unblinding_hard_fails_without_a_map(ledger: Path) -> None:
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    _map_path(ledger).unlink()
    with pytest.raises(BlindingError, match="never blinded"):
        _unblind(ledger)


@pytest.mark.parametrize(
    ("aliases", "match"),
    [
        pytest.param({}, "no usable `aliases` block", id="empty"),
        pytest.param({"candidate-a": "../../escaped"}, "single path component", id="traversal"),
        pytest.param({"../evil": "claude-baseline"}, "is not an alias", id="alias-traversal"),
    ],
)
def test_unblinding_hard_fails_on_a_hostile_map(
    ledger: Path, aliases: dict[str, str], match: str
) -> None:
    """The map is a file on a runner an agent has a shell on, so it is untrusted input."""
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    payload = json.loads(_map_path(ledger).read_text())
    payload["aliases"] = aliases
    _map_path(ledger).write_text(json.dumps(payload))
    with pytest.raises(BlindingError, match=match):
        _unblind(ledger)


def test_unblinding_hard_fails_on_an_unreadable_map(ledger: Path) -> None:
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    _map_path(ledger).write_text("{not json")
    with pytest.raises(BlindingError, match="not readable JSON"):
        _unblind(ledger)


def test_unblinding_hard_fails_on_a_map_for_another_cell(ledger: Path) -> None:
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    payload = json.loads(_map_path(ledger).read_text())
    payload["case_id"] = "scotus/999"
    _map_path(ledger).write_text(json.dumps(payload))
    with pytest.raises(BlindingError, match="is for case_id"):
        _unblind(ledger)


def test_unblinding_hard_fails_on_an_invented_alias(ledger: Path) -> None:
    """A grader that wrote under an alias it was never given must not ship it."""
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    event_paths = CasePaths(ledger, COURT, DOCKET).event(EVENT)
    write_text(
        event_paths.evaluation_dir(EVALUATOR, f"{ALIAS_PREFIX}zz", EVALUATE_RUN) / "evaluation.md",
        "invented\n",
    )
    with pytest.raises(BlindingError, match="alias directories survive"):
        _unblind(ledger)


def test_a_partial_cell_fails_before_anything_moves(ledger: Path) -> None:
    """Mutate-then-check would let a retry sweep the wreckage clean and call it a success."""
    result = _blind(ledger)
    _seed_evaluations(ledger, result)
    event_paths = CasePaths(ledger, COURT, DOCKET).event(EVENT)
    event_paths.evaluation(EVALUATOR, result.candidates[0].alias, EVALUATE_RUN).unlink()
    with pytest.raises(BlindingError, match=r"no evaluation\.json"):
        _unblind(ledger)
    # Nothing moved, so a maintainer sees the same tree the failure described.
    for candidate in result.candidates:
        assert event_paths.evaluation_dir(EVALUATOR, candidate.alias, EVALUATE_RUN).is_dir()
        assert not event_paths.evaluation_dir(
            EVALUATOR, candidate.predictor_id, EVALUATE_RUN
        ).exists()


# --- the commands the workflow calls ------------------------------------------


def test_the_two_commands_drive_the_whole_round_trip(
    ledger: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(ledger))
    common = ["--court", COURT, "--docket", str(DOCKET), "--event", EVENT]
    map_args = ["--map-dir", str(_map_dir(ledger)), "--run-id", EVALUATE_RUN]
    blind = runner.invoke(app, ["provision-blinded-predictions", *common, *map_args])
    assert blind.exit_code == 0, blind.output
    assert "blinded 3 candidate(s)" in blind.output

    aliases = json.loads(_map_path(ledger).read_text())["aliases"]
    event_paths = CasePaths(ledger, COURT, DOCKET).event(EVENT)
    for alias in aliases:
        write_json(
            event_paths.evaluation(EVALUATOR, alias, EVALUATE_RUN),
            Evaluation(
                case_id=f"{COURT}/{DOCKET}",
                event_id=EVENT,
                predictor_id=alias,
                evaluator_id=EVALUATOR,
                engine="claude-code",
                run_id=EVALUATE_RUN,
                created_at=datetime(2026, 8, 1, tzinfo=UTC),
                correct=1,
            ),
        )

    unblind = runner.invoke(
        app, ["unblind-evaluations", *common, "--evaluator", EVALUATOR, *map_args]
    )
    assert unblind.exit_code == 0, unblind.output
    assert "un-aliased 3 evaluation(s)" in unblind.output
    assert check_evaluation_targets(ledger).passed


def test_the_command_exits_non_zero_when_it_cannot_un_alias(
    ledger: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(ledger))
    result = runner.invoke(
        app,
        [
            "unblind-evaluations",
            *["--court", COURT, "--docket", str(DOCKET), "--event", EVENT],
            *["--evaluator", EVALUATOR, "--run-id", EVALUATE_RUN],
            *["--map-dir", str(_map_dir(ledger))],
        ],
    )
    assert result.exit_code == 1
    assert "un-aliasing failed" in result.output


def test_a_harness_stamp_outranks_an_agent_backdate_in_latest_selection(ledger: Path) -> None:
    """The harness clock decides, matching the stratified join's rule.

    A run whose agent-written `created_at` is later must not outrank a run
    whose harness stamp is later still — both the grader's staging and the
    stratifier read the same clock, or the two halves of a cell would describe
    different predictions.
    """
    # The fixture run carries created_at 2026-07-18 and no stamp. Add an
    # earlier-created run whose harness stamp postdates everything.
    stamped_dir = _seed_prediction(
        ledger,
        "claude-baseline",
        "claude-code",
        "claude-fable-5",
        run_id="20260101T000000Z",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    payload = json.loads((stamped_dir / "prediction.json").read_text())
    payload["process_version"] = {
        "label": "proc-v2",
        "digest": "sha256:any",
        "stamped_at": "2026-12-31T00:00:00+00:00",
    }
    (stamped_dir / "prediction.json").write_text(json.dumps(payload))

    latest = blinding.latest_prediction_dirs(CasePaths(ledger, COURT, DOCKET).event(EVENT))

    assert latest["claude-baseline"].name == "20260101T000000Z"


@pytest.mark.parametrize(
    "payload",
    [
        "not json at all",
        json.dumps({"created_at": 12345}),
        json.dumps({"created_at": "not-a-timestamp"}),
        json.dumps({"process_version": {"stamped_at": "also-not"}, "created_at": None}),
    ],
)
def test_cell_clock_degrades_to_the_epoch_on_unreadable_bytes(tmp_path: Path, payload: str) -> None:
    # This runs pre-agent over committed bytes; a malformed prediction must
    # sort first (the epoch), never crash the staging step.
    directory = tmp_path / "run"
    directory.mkdir()
    (directory / "prediction.json").write_text(payload)

    clock = blinding._cell_clock(directory)

    assert clock == blinding._EPOCH


def test_unaliasing_resolves_a_sentence_initial_capitalized_alias(tmp_path: Path) -> None:
    # Aliases are handed out lowercase, but a judge's prose capitalizes at
    # sentence start — "Candidate-a explicitly repeated ..." — and an alias
    # that survives un-aliasing ships unresolvable in the run PR's flag
    # roll-up. The resolver matches case-insensitively and looks the match up
    # lowered, exactly like the blinding-direction resolver.
    root = tmp_path / "out"
    root.mkdir()
    (root / "flags.json").write_text(
        json.dumps({"note": "Candidate-a repeated the outcome. candidate-b did not."})
    )

    blinding._resolve_aliases_in_tree(
        root, {"candidate-a": "gemini-baseline", "candidate-b": "claude-baseline"}
    )

    resolved = json.loads((root / "flags.json").read_text())
    assert resolved["note"] == "gemini-baseline repeated the outcome. claude-baseline did not."


def test_the_resolver_bounds_every_alternative(tmp_path: Path) -> None:
    # `|` binds loosest: without the non-capturing group the lookbehind
    # anchored only the first alternative and the lookahead only the last, so
    # a middle alias resolved inside larger tokens. Three aliases, middle one
    # embedded — none may resolve.
    root = tmp_path / "out"
    root.mkdir()
    (root / "note.md").write_text("xcandidate-b y precandidate-a candidate-c1\n")

    blinding._resolve_aliases_in_tree(
        root,
        {
            "candidate-a": "gemini-baseline",
            "candidate-b": "claude-baseline",
            "candidate-c": "codex-baseline",
        },
    )

    assert (root / "note.md").read_text() == "xcandidate-b y precandidate-a candidate-c1\n"
