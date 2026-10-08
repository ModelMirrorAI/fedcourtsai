"""`fedcourts release-sensitivity`: the release's sensitivity lines, one departure at a time."""

from __future__ import annotations

import json
import math
import subprocess
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.ids import parse_run_id
from fedcourtsai.paths import CasePaths
from fedcourtsai.release_sensitivity import (
    RANKED_ARM,
    GitBuildSource,
    ReleaseSensitivityError,
    StatpackBuild,
    considering_conference,
    opening_petition,
    release_sensitivity,
)
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
)
from fedcourtsai.serialize import write_json, write_yaml
from fedcourtsai.store import stratify
from tests.conftest import bless_process

runner = CliRunner()

BLESSED = "sha256:blessed"
EVENT = "evt-petition-disposition"
VERSION = "sal-v4"
PAYLOAD_DAY = date(2026, 10, 6)


def _pack(rate: float) -> StatPack:
    """A pack whose only prior Term pools ``rate`` for the baseline band."""
    return StatPack(
        corpus_rows=1,
        terms=[
            StatPackTerm(
                term=2024,
                base_rates=BaseRateBucket(),
                salience_version=VERSION,
                segments=[
                    StatPackTermSegment(
                        band="baseline",
                        prefix_est_grant_rate=rate,
                        prefix_weighted_resolved=1000,
                        est_grant_rate=rate,
                        weighted_resolved=1000,
                    )
                ],
            )
        ],
    )


class _Builds:
    """A build source keyed by checkout commit, standing in for the repository."""

    def __init__(self, packs: Mapping[str, float]) -> None:
        self.packs = packs

    def build_at(self, pipeline_sha: str) -> StatpackBuild | None:
        if pipeline_sha not in self.packs:
            return None
        rate = self.packs[pipeline_sha]
        return StatpackBuild(
            build_commit=f"build-{pipeline_sha}",
            blob=f"blob-{rate}",
            lookback=10,
            statpack=_pack(rate),
        )


def _stamp(digest: str, when: datetime, sha: str = "fill") -> ProcessVersion:
    return ProcessVersion(label="proc-v1", digest=digest, stamped_at=when, pipeline_sha=sha)


def _paths(data_root: Path, case_id: str) -> Any:
    court, _, docket = case_id.partition("/")
    return CasePaths(data_root, court, int(docket)).event(EVENT)


def _event(data_root: Path, case_id: str, *, granted: int = 0) -> None:
    paths = _paths(data_root, case_id)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=EVENT, case_id=case_id, kind=EventKind.petition, title=f"P v. R ({case_id})"
        ),
    )
    write_json(
        paths.outcome,
        Outcome(
            case_id=case_id,
            event_id=EVENT,
            resolved_at=date(2026, 10, 15),
            actual_disposition=Disposition.granted if granted else Disposition.denied,
            actual_granted=granted,
        ),
    )


def _prediction(
    data_root: Path, case_id: str, *, predictor_id: str = "alpha", run_id: str, p: float = 0.1
) -> None:
    write_json(
        _paths(data_root, case_id).prediction(predictor_id, run_id),
        Prediction(
            case_id=case_id,
            event_id=EVENT,
            predictor_id=predictor_id,
            engine=Engine.claude_code,
            run_id=run_id,
            created_at=parse_run_id(run_id),
            input_snapshot="corpus",
            granted=0,
            probability=p,
            predicted_disposition=Disposition.denied,
            process_version=_stamp(BLESSED, parse_run_id(run_id)),
            context=PredictionContext(
                mode="forward",
                snapshot_date=parse_run_id(run_id).date(),
                signals_observable=True,
                band="baseline",
                salience_version=VERSION,
                term=2025,
            ),
        ),
    )


def _grade(  # noqa: PLR0913 - one keyword per field a test varies
    data_root: Path,
    case_id: str,
    *,
    judge: str,
    run_id: str,
    sha: str,
    recorded: float,
    predictor_id: str = "alpha",
    p: float = 0.1,
    granted: int = 0,
) -> None:
    brier = (p - granted) ** 2
    write_json(
        _paths(data_root, case_id).evaluation(judge, predictor_id, "e1"),
        Evaluation(
            case_id=case_id,
            event_id=EVENT,
            predictor_id=predictor_id,
            evaluator_id=judge,
            engine=Engine.codex,
            run_id="e1",
            prediction_run_id=run_id,
            created_at=datetime(2026, 10, 16, tzinfo=UTC),
            correct=int(granted == 0),
            brier_score=brier,
            brier_skill_score=1 - brier / (recorded - granted) ** 2,
            segment_base_rate=recorded,
            base_rate_basis="risk_set",
            base_rate_salience_version=VERSION,
            leakage_suspected=False,
            process_version=_stamp("sha256:judge", datetime(2026, 10, 16, tzinfo=UTC), sha),
        ),
    )


def _docket(*entries: tuple[str, str]) -> dict[str, Any]:
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


CERT = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed. (Response due July 1, 2026)"),
    ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
)
MANDAMUS = _docket(
    ("Apr 01 2026", "Application (25A1) to extend the time to file a petition, submitted."),
    ("May 20 2026", "Petition for a writ of mandamus filed. (Response due June 26, 2026)"),
    ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
) | {"CaseNumber": "25-2 *** CAPITAL CASE ***"}
CALLED_FOR_RESPONSE = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed."),
    ("Aug 12 2026", "DISTRIBUTED for Conference of 9/28/2026."),
    ("Aug 12 2026", "Response Requested. (Due September 11, 2026)"),
)
RELISTED = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed."),
    ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
    ("Sep 30 2026", "DISTRIBUTED for Conference of 10/9/2026."),
)


# -- docket readings ----------------------------------------------------------


def test_opening_petition_reads_the_petition_entry_past_an_extension_application() -> None:
    petition = opening_petition(MANDAMUS)
    assert petition is not None
    assert petition.writ == "rule-20"
    assert petition.filed == date(2026, 5, 20)
    certiorari = opening_petition(CERT)
    assert certiorari is not None and certiorari.writ == "certiorari"


@pytest.mark.parametrize(
    ("text", "writ"),
    [
        ("Petition for a writ of habeas corpus filed.", "rule-20"),
        ("Petition for a writ of mandamus and/or prohibition filed.", "rule-20"),
        ("Petition for a writ of certiorari or, alternatively, mandamus filed.", "ambiguous"),
        (
            "Petition for a writ of certiorari and motion for leave to proceed in "
            + "forma pauperis filed.",
            "certiorari",
        ),
    ],
)
def test_opening_petition_classifies_the_writ(text: str, writ: str) -> None:
    petition = opening_petition(_docket(("Jun 01 2026", text)))
    assert petition is not None and petition.writ == writ


def test_opening_petition_is_none_without_a_petition_entry() -> None:
    assert (
        opening_petition(_docket(("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026.")))
        is None
    )


def test_a_conference_that_sat_is_after_on_its_own_day() -> None:
    assert considering_conference(CERT, PAYLOAD_DAY, date(2026, 9, 28)) == (
        date(2026, 9, 28),
        "sat",
    )
    assert considering_conference(CERT, PAYLOAD_DAY, date(2026, 9, 27)) == (
        date(2026, 9, 28),
        "ahead",
    )


def test_a_call_for_response_takes_the_petition_off_its_conference() -> None:
    assert considering_conference(CALLED_FOR_RESPONSE, PAYLOAD_DAY, date(2026, 10, 3)) == (
        date(2026, 9, 28),
        "off",
    )


def test_a_relist_moves_the_reading_to_the_conference_ahead() -> None:
    # Run after the relist entry: forecast against the 10/9 conference, still ahead.
    assert considering_conference(RELISTED, PAYLOAD_DAY, date(2026, 10, 3)) == (
        date(2026, 10, 9),
        "ahead",
    )
    # Run between the sitting and the relist entry: the 9/28 conference had sat.
    assert considering_conference(RELISTED, PAYLOAD_DAY, date(2026, 9, 29)) == (
        date(2026, 9, 28),
        "sat",
    )


def test_a_reschedule_before_the_conference_moves_it() -> None:
    redistributed = _docket(
        ("Jun 01 2026", "Petition for a writ of certiorari filed."),
        ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
        ("Sep 20 2026", "DISTRIBUTED for Conference of 10/9/2026."),
    )
    assert considering_conference(redistributed, PAYLOAD_DAY, date(2026, 10, 3)) == (
        date(2026, 10, 9),
        "ahead",
    )
    bare = _docket(
        ("Jun 01 2026", "Petition for a writ of certiorari filed."),
        ("Aug 26 2026", "DISTRIBUTED for Conference of 9/28/2026."),
        ("Aug 27 2026", "Rescheduled."),
    )
    assert considering_conference(bare, PAYLOAD_DAY, date(2026, 10, 3)) == (
        date(2026, 9, 28),
        "off",
    )


def test_an_undistributed_petition_has_no_conference() -> None:
    assert considering_conference(
        _docket(("Jun 01 2026", "Petition for a writ of certiorari filed.")),
        PAYLOAD_DAY,
        date(2026, 10, 3),
    ) == (None, "undistributed")


def test_a_payload_older_than_the_conference_cannot_say_whether_it_sat() -> None:
    assert considering_conference(CERT, date(2026, 9, 1), date(2026, 10, 3))[1] == "unknown"


# -- the ledger ----------------------------------------------------------------


@pytest.fixture
def ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Four cert distribution events, graded by two judges reading two statpack builds.

    - scotus/1: a certiorari petition first forecast before its conference;
      beta's *scored* run is after the conference, alpha's first is not.
    - scotus/2: a mandamus petition (Rule 20), forecast before its conference.
    - scotus/3: first forecast after its 9/28 conference had sat.
    - scotus/4: first forecast after 9/28, but a call for response took it off.
    """
    bless_process(monkeypatch, BLESSED)
    data_root = tmp_path / "data"
    early, late = "20260917T120000Z", "20261003T120000Z"
    for case_id, run in (
        ("scotus/1", early),
        ("scotus/2", early),
        ("scotus/3", late),
        ("scotus/4", late),
    ):
        _event(data_root, case_id)
        _prediction(data_root, case_id, run_id=run)
        # j1 read build A (exact 0.05) and transcribed it loosely; j2 read
        # build B (exact 0.06) and transcribed it exactly.
        _grade(data_root, case_id, judge="j1", run_id=run, sha="sha-a", recorded=0.0512)
        _grade(data_root, case_id, judge="j2", run_id=run, sha="sha-b", recorded=0.06)
    _prediction(data_root, "scotus/1", predictor_id="beta", run_id=late, p=0.2)
    _grade(
        data_root,
        "scotus/1",
        judge="j1",
        run_id=late,
        sha="sha-a",
        recorded=0.0512,
        predictor_id="beta",
        p=0.2,
    )
    return data_root


PAYLOADS = {
    "scotus/1": CERT,
    "scotus/2": MANDAMUS,
    "scotus/3": CERT,
    "scotus/4": CALLED_FOR_RESPONSE,
}


def _run(data_root: Path, **kwargs: Any) -> dict[str, Any]:
    cells = stratify(data_root, frozen_only=True).cells
    return release_sensitivity(
        cells,
        data_root,
        _pack(0.09),  # the fill-time pack: never the anchor's source
        builds=_Builds({"sha-a": 0.05, "sha-b": 0.06}),
        payloads=lambda case_id: (PAYLOAD_DAY, PAYLOADS[case_id]) if case_id in PAYLOADS else None,
        **kwargs,
    )


def _forward(figures: Mapping[str, Any], predictor: str = "alpha") -> Mapping[str, Any]:
    forward: Mapping[str, Any] = figures[RANKED_ARM]["entries"][predictor]["forward"]
    return forward


def test_the_registered_headline_is_the_board(ledger: Path) -> None:
    result = _run(ledger)
    forward = _forward(result["registered_headline"]["figures"])
    assert forward["accuracy_events_scored"] == 4
    assert forward["skill_scored"] == 8
    expected = 1 - (8 * 0.01) / (4 * 0.0512**2 + 4 * 0.06**2)
    assert math.isclose(forward["population_brier_skill_score"], expected)


def test_the_in_sample_benchmark_rides_beside_the_headline_not_inside_it(ledger: Path) -> None:
    result = _run(ledger)
    headline = _forward(result["registered_headline"]["figures"])
    assert "population_in_sample_skill_score" not in headline
    assert "in_sample_grant_rate" not in headline
    benchmark = _forward(result["post_hoc_in_sample_benchmark"]["figures"])
    assert set(benchmark) == {
        "events_scored",
        "in_sample_events_scored",
        "in_sample_grant_rate",
        "population_in_sample_skill_score",
        "in_sample_skill_scored",
    }
    assert benchmark["events_scored"] == headline["events_scored"]
    assert benchmark["in_sample_events_scored"] == 4


def test_the_anchor_reads_the_build_each_grading_read(ledger: Path) -> None:
    block = _run(ledger)["blocks"]["exact_pool_anchor"]
    forward = _forward(block["figures"])
    # Build A's 0.05 for j1, build B's 0.06 for j2 — never the fill pack's 0.09.
    expected = 1 - (8 * 0.01) / (4 * 0.05**2 + 4 * 0.06**2)
    assert math.isclose(forward["population_brier_skill_score"], expected)
    assert forward["skill_scored"] == 8
    assert block["recorded_retained"] == []
    assert {b["build_commit"] for b in block["statpack_builds"]} == {"build-sha-a", "build-sha-b"}
    by_build = {b["build_commit"]: b["gradings"] for b in block["statpack_builds"]}
    assert by_build == {"build-sha-a": 5, "build-sha-b": 4}


def test_the_spread_is_per_judge_and_docket_term(ledger: Path) -> None:
    spread = _run(ledger)["blocks"]["exact_pool_anchor"]["transcription_spread"]
    cells = spread["skill_scored_cert_cells"]
    j1 = cells["by_judge"]["j1"]
    assert j1["cells"] == 5
    assert j1["exact"] == 0
    assert j1["over_one_percent"] == 5
    assert math.isclose(j1["max_relative_deviation"], 0.0012 / 0.05)
    assert j1["by_docket_term"]["2025"]["cells"] == 5
    j2 = cells["by_judge"]["j2"]
    assert (j2["cells"], j2["exact"], j2["max_relative_deviation"]) == (4, 4, 0.0)
    assert cells["all"]["cells"] == 9
    # No registration day, no cohort spread.
    assert spread["registered_cohort_graded_cert_cells"] is None


def test_an_unreadable_build_keeps_the_recorded_baseline_and_says_so(ledger: Path) -> None:
    cells = stratify(ledger, frozen_only=True).cells
    result = release_sensitivity(
        cells,
        ledger,
        None,
        builds=_Builds({"sha-a": 0.05}),
        payloads=lambda case_id: None,
    )
    block = result["blocks"]["exact_pool_anchor"]
    assert len(block["recorded_retained"]) == 4
    assert {row["reason"] for row in block["recorded_retained"]} == {"build not readable"}
    forward = _forward(block["figures"])
    expected = 1 - (8 * 0.01) / (4 * 0.05**2 + 4 * 0.06**2)
    assert math.isclose(forward["population_brier_skill_score"], expected)


def test_the_registered_cohort_gets_its_own_spread(ledger: Path) -> None:
    result = _run(ledger, registered={("scotus/1", EVENT)})
    cohort = result["blocks"]["exact_pool_anchor"]["transcription_spread"][
        "registered_cohort_graded_cert_cells"
    ]
    assert cohort["all"]["cells"] == 3  # alpha by j1 and j2, beta by j1
    assert cohort["unanchored"] == []


def test_rule_20_petitions_are_found_by_opening_entry_and_removed(ledger: Path) -> None:
    block = _run(ledger)["blocks"]["rule_20_excluded"]
    assert [row["case_id"] for row in block["identified"]] == ["scotus/2"]
    assert block["identified"][0]["opening_entry_filed"] == "2026-05-20"
    # The Court's trailing markers are not part of the docket number.
    assert block["identified"][0]["docket_number"] == "25-2"
    assert block["cases_scanned"] == 4
    assert block["board_cells_removed"] == 2
    forward = _forward(block["figures"])
    assert forward["accuracy_events_scored"] == 3
    assert forward["skill_scored"] == 6
    assert "grants_expected" not in forward


def test_post_conference_first_forecasts_are_listed_and_removed(ledger: Path) -> None:
    block = _run(ledger, registered={("scotus/1", EVENT)}, grant_list=date(2026, 10, 1))["blocks"][
        "post_conference_first_forecasts_excluded"
    ]
    assert [row["case_id"] for row in block["subset"]] == ["scotus/3"]
    row = block["subset"][0]
    assert row["considering_conference"] == "2026-09-28"
    assert row["first_forward_run_id"] == "20261003T120000Z"
    assert row["after_grant_list"] is True
    assert row["registered"] is False
    assert (block["events"], block["resolved"], block["graded"], block["registered"]) == (
        1,
        1,
        1,
        0,
    )
    assert block["by_conference"] == {
        "2026-09-28": {"events": 1, "resolved": 1, "graded": 1, "registered": 0}
    }
    # The called-for-response petition was never considered on 9/28.
    assert all(row["case_id"] != "scotus/4" for row in block["subset"])
    # beta's scored cell on scotus/1 postdates the conference, outside the subset.
    assert block["scored_after_conference_outside_subset"] == [
        {
            "case_id": "scotus/1",
            "event_id": EVENT,
            "predictor_id": "beta",
            "evaluator_id": "j1",
            "scored_run_id": "20261003T120000Z",
            "considering_conference": "2026-09-28",
        }
    ]
    assert block["lines_equal_headline"] is False
    assert block["board_cells_removed"] == 2
    assert _forward(block["figures"])["accuracy_events_scored"] == 3


def test_an_ungraded_subset_leaves_the_lines_equal_to_the_headline(ledger: Path) -> None:
    for path in (ledger / "cases/scotus/3").rglob("evaluation.json"):
        path.unlink()
    result = _run(ledger)
    block = result["blocks"]["post_conference_first_forecasts_excluded"]
    assert block["graded"] == 0
    assert block["lines_equal_headline"] is True
    assert block["figures"] == result["registered_headline"]["figures"]


# -- the repository's builds ----------------------------------------------------


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return done.stdout.strip()


def _commit(repo: Path, rate: float, lookback: int) -> str:
    (repo / "metrics").mkdir(exist_ok=True)
    (repo / "config").mkdir(exist_ok=True)
    (repo / "metrics/statpack.json").write_text(_pack(rate).model_dump_json())
    (repo / "config/tracking.yaml").write_text(
        f"salience:\n  base_rate_lookback_terms: {lookback}\n"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", f"pack {rate}")
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "test")
    _git(root, "config", "user.email", "test@example.invalid")
    return root


def test_git_builds_resolve_each_checkout_to_its_own_pack(repo: Path) -> None:
    first = _commit(repo, 0.05, 3)
    second = _commit(repo, 0.06, 10)
    (repo / "notes.txt").write_text("a later commit that leaves the pack alone")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "notes")
    third = _git(repo, "rev-parse", "HEAD")
    builds = GitBuildSource(repo)
    at_first = builds.build_at(first)
    assert at_first is not None
    assert at_first.statpack == _pack(0.05)
    assert at_first.lookback == 3
    at_third = builds.build_at(third)
    assert at_third is not None
    # The build is the commit that last wrote the pack, not the checkout.
    assert at_third.build_commit == second
    assert at_third.statpack == _pack(0.06)
    assert at_third.lookback == 10
    assert builds.build_at("0" * 40) is None


# -- the command ---------------------------------------------------------------


def test_the_command_prints_json_with_its_provenance(
    repo: Path, ledger: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("FEDCOURTS_CORPUS_SPLIT", raising=False)
    sha = _commit(repo, 0.05, 10)
    data_root = repo / "data"
    ledger.rename(data_root)
    # Point every grading at the repository's one build.
    for path in data_root.rglob("evaluation.json"):
        record = json.loads(path.read_text())
        record["process_version"]["pipeline_sha"] = sha
        path.write_text(json.dumps(record))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "ledger")
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id=case_id, court="scotus", docket_number=f"25-{n}")
                for n, case_id in enumerate(PAYLOADS, start=1)
            ],
        )
        for case_id, payload in PAYLOADS.items():
            corpus.upsert_snapshot(conn, case_id, PAYLOAD_DAY, payload)
        conn.commit()
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(repo / "metrics"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(app, ["release-sensitivity", "--grant-list", "2026-10-01"])
    assert result.exit_code == 0, result.output
    stdout = result.stdout
    output = json.loads(stdout[stdout.index("{") :])
    assert output["ledger"]["commit"] == _git(repo, "rev-parse", "HEAD")
    assert output["ledger"]["dirty"] is False
    assert output["corpus"]["latest_snapshot"] == PAYLOAD_DAY.isoformat()
    assert output["corpus"]["sha256"]
    assert output["fill_statpack"]["build_commit"] == sha
    assert output["registered_headline"]["matches_committed_board"] is None
    blocks = output["blocks"]
    assert [b["build_commit"] for b in blocks["exact_pool_anchor"]["statpack_builds"]] == [sha]
    assert [r["case_id"] for r in blocks["rule_20_excluded"]["identified"]] == ["scotus/2"]
    subset = blocks["post_conference_first_forecasts_excluded"]["subset"]
    assert [r["case_id"] for r in subset] == ["scotus/3"]
    assert "anchor skill" in result.stderr


def test_unreadable_dockets_are_listed_not_placed(ledger: Path) -> None:
    payloads = {
        # scotus/1: no payload at all; scotus/3: stored before its conference sat.
        "scotus/2": MANDAMUS,
        "scotus/3": CERT,
        "scotus/4": _docket(("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026.")),
    }
    cells = stratify(ledger, frozen_only=True).cells
    result = release_sensitivity(
        cells,
        ledger,
        None,
        builds=_Builds({"sha-a": 0.05, "sha-b": 0.06}),
        payloads=lambda case_id: (
            (date(2026, 9, 1) if case_id == "scotus/3" else PAYLOAD_DAY, payloads[case_id])
            if case_id in payloads
            else None
        ),
    )
    rule_20 = result["blocks"]["rule_20_excluded"]
    assert rule_20["unclassified"] == [
        {"case_id": "scotus/1", "reason": "no live payload"},
        {"case_id": "scotus/4", "reason": "no opening petition entry"},
    ]
    post = result["blocks"]["post_conference_first_forecasts_excluded"]
    # scotus/4's payload carries no petition entry but does show its conference sit.
    assert [row["case_id"] for row in post["subset"]] == ["scotus/4"]
    assert sorted((row["case_id"], row["reason"]) for row in post["unreadable"]) == [
        ("scotus/1", "no live payload"),
        ("scotus/3", "payload of 2026-09-01 predates the conference of 2026-09-28"),
    ]


def test_an_ambiguous_writ_is_named_and_not_removed(ledger: Path) -> None:
    ambiguous = _docket(
        ("Jun 01 2026", "Petition for a writ of certiorari or, alternatively, mandamus filed."),
    )
    cells = stratify(ledger, frozen_only=True).cells
    result = release_sensitivity(
        cells,
        ledger,
        None,
        builds=_Builds({}),
        payloads=lambda case_id: (PAYLOAD_DAY, ambiguous if case_id == "scotus/2" else CERT),
    )
    block = result["blocks"]["rule_20_excluded"]
    assert block["identified"] == []
    assert [row["case_id"] for row in block["not_certiorari_not_rule_20"]] == ["scotus/2"]
    assert block["board_cells_removed"] == 0


def test_a_shallow_clone_is_refused(repo: Path, tmp_path: Path) -> None:
    _commit(repo, 0.05, 10)
    _commit(repo, 0.06, 10)
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        check=True,
        capture_output=True,
    )
    with pytest.raises(ReleaseSensitivityError, match="shallow"):
        GitBuildSource(shallow)


def test_the_command_reads_the_committed_board_and_the_registered_cohort(
    repo: Path, ledger: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("FEDCOURTS_CORPUS_SPLIT", raising=False)
    sha = _commit(repo, 0.05, 10)
    data_root = repo / "data"
    ledger.rename(data_root)
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id=case_id, court="scotus", docket_number=f"25-{n}")
                for n, case_id in enumerate(PAYLOADS, start=1)
            ],
        )
        for case_id, payload in PAYLOADS.items():
            corpus.upsert_snapshot(conn, case_id, PAYLOAD_DAY, payload)
        conn.commit()
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(repo / "metrics"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    # The committed board, built by `leaderboard` itself over the same ledger.
    built = runner.invoke(app, ["leaderboard"])
    assert built.exit_code == 0, built.output
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "ledger and board")
    result = runner.invoke(app, ["release-sensitivity", "--registered-at", "2026-09-15"])
    assert result.exit_code == 0, result.output
    stdout = result.stdout
    output = json.loads(stdout[stdout.index("{") :])
    assert output["registered_headline"]["matches_committed_board"] is True
    assert output["registered_at"] == "2026-09-15"
    assert output["conference_fallbacks"] == 0
    # The gradings name checkouts this repository does not hold: kept as recorded.
    anchor = output["blocks"]["exact_pool_anchor"]
    assert len(anchor["recorded_retained"]) == 9
    assert anchor["transcription_spread"]["registered_cohort_graded_cert_cells"] is not None
    assert output["fill_statpack"]["build_commit"] == sha
    # Read-only: the checkout is exactly as committed.
    assert _git(repo, "status", "--porcelain") == ""


def test_the_command_refuses_a_bad_date() -> None:
    result = runner.invoke(app, ["release-sensitivity", "--grant-list", "October"])
    assert result.exit_code == 2


def test_an_ancillary_papers_distribution_is_not_the_petitions_conference() -> None:
    docket = _docket(
        ("Apr 01 2026", "Motion (25M75) DISTRIBUTED for Conference of 5/14/2026."),
        ("Jun 01 2026", "Petition for a writ of certiorari filed."),
        ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
        ("Aug 01 2026", "Motion (25M90) DISTRIBUTED for Conference of 8/20/2026."),
    )
    # Before the petition's own distribution, the motion's conference is not its.
    assert considering_conference(docket, PAYLOAD_DAY, date(2026, 6, 1)) == (
        None,
        "undistributed",
    )
    # After it, a later motion distribution does not win the latest-entry read.
    assert considering_conference(docket, PAYLOAD_DAY, date(2026, 9, 1)) == (
        date(2026, 9, 28),
        "ahead",
    )


def test_a_reschedule_on_the_conference_day_takes_it_off() -> None:
    docket = _docket(
        ("Jun 01 2026", "Petition for a writ of certiorari filed."),
        ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
        ("Sep 28 2026", "Rescheduled."),
    )
    assert considering_conference(docket, PAYLOAD_DAY, date(2026, 10, 3)) == (
        date(2026, 9, 28),
        "off",
    )


def test_the_spread_counts_faithful_roundings_at_the_recorded_precision(ledger: Path) -> None:
    cells = stratify(ledger, frozen_only=True).cells
    result = release_sensitivity(
        cells,
        ledger,
        None,
        # j2 recorded 0.06: a faithful two-decimal rounding of 0.0600004, not exact.
        builds=_Builds({"sha-a": 0.05, "sha-b": 0.0600004}),
        payloads=lambda case_id: None,
    )
    by_judge = result["blocks"]["exact_pool_anchor"]["transcription_spread"][
        "skill_scored_cert_cells"
    ]["by_judge"]
    assert (by_judge["j2"]["exact"], by_judge["j2"]["faithful_rounding"]) == (4, 4)
    # 0.0512 is not 0.05 at four decimals.
    assert by_judge["j1"]["faithful_rounding"] == 0
    assert result["payloads_read"] == {"cases": 4, "missing": 4, "oldest": None, "newest": None}


def test_the_grant_list_is_read_against_one_conference(ledger: Path) -> None:
    block = _run(ledger, grant_list=date(2026, 9, 1))["blocks"][
        "post_conference_first_forecasts_excluded"
    ]
    # No considering conference sits on or before a 9/1 grant list.
    assert block["grant_list_conference"] is None
    assert [row["after_grant_list"] for row in block["subset"]] == [None]
    assert block["not_after_grant_list"] == []
