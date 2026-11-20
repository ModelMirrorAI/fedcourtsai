"""A prediction slice's process label: its own rows, instant and windows in the registry.

A label belongs to one population. Registering a slice's label leaves every
SCOTUS row as it was, a SCOTUS registration leaves the slice's, and the gate
refuses an actor whose digest sits under another population's label.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import process_version
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.process_registration import LiveActor, RegistrationError, register_process
from fedcourtsai.process_version import (
    asked_authorship_claims,
    bless_moments,
    counting_instant,
    label_ordinal,
    load_process_registry,
    registered_windows,
    scotus_label_of,
)
from fedcourtsai.promotion_record import (
    _prereg_message,
    dump_registry,
    pending_registrations,
    stamp_registry,
)
from fedcourtsai.registry_gate import registry_gate
from tests.conftest import seed_prediction
from tests.test_promotion_record import (
    COMMITTED,
    DECLARED,
    LAST_LABEL,
    MERGED_AT,
    NEW_CLAUDE,
    NEW_LABEL,
    PENDING,
    _iso,
    _live_fleet,
)
from tests.test_registry_gate import _history

SLICE = "ai-watchlist"
SLICE_LABEL = f"{SLICE}-v1"
SLICE_PREDICTOR = "sha256:" + "1" * 64
SLICE_JUDGE = "sha256:" + "2" * 64
MOVED_SLICE_PREDICTOR = "sha256:" + "3" * 64
MOVED_SLICE_JUDGE = "sha256:" + "4" * 64
MERGE = "f" * 40


def _slice_actors(*, predictor: str = SLICE_PREDICTOR, judge: str = SLICE_JUDGE) -> list[LiveActor]:
    return [
        LiveActor("predictor", "claude-trial", predictor, SLICE),
        LiveActor("evaluator", "claude-trial-judge", judge, SLICE),
    ]


def _fleet(**moved: str) -> list[LiveActor]:
    """Every enabled actor: the SCOTUS fleet as committed, and the slice's two."""
    return [*_live_fleet(claude=_carried("claude-baseline")), *_slice_actors(**moved)]


def _carried(actor_id: str) -> str:
    return next(str(b["digest"]) for b in COMMITTED["blessings"] if b["actor_id"] == actor_id)


def _slice_registered() -> dict[str, Any]:
    return register_process(DECLARED, SLICE_LABEL, _fleet(), SLICE)


def _carried_to_main(document: dict[str, Any]) -> dict[str, Any]:
    """``document`` as ``main`` holds it once a merge has stamped its pending rows."""
    return stamp_registry(document, pending_registrations(document), MERGE, MERGED_AT)


def _load(document: dict[str, Any], current_label: str = LAST_LABEL) -> Any:
    return load_process_registry(dump_registry(document), current_label=current_label)


# --- registration ------------------------------------------------------------


def test_a_slice_label_adds_its_own_rows_and_leaves_every_scotus_row() -> None:
    document = _slice_registered()
    assert document["labels"][:-1] == COMMITTED["labels"]
    assert document["labels"][-1] == {
        "label": SLICE_LABEL,
        "since": PENDING,
        "population": SLICE,
    }
    assert document["blessings"][: len(COMMITTED["blessings"])] == COMMITTED["blessings"]
    assert document["blessings"][len(COMMITTED["blessings"]) :] == [
        {
            "digest": SLICE_PREDICTOR,
            "role": "predictor",
            "actor_id": "claude-trial",
            "label": SLICE_LABEL,
            "blessed": PENDING,
        },
        {
            "digest": SLICE_JUDGE,
            "role": "evaluator",
            "actor_id": "claude-trial-judge",
            "label": SLICE_LABEL,
            "blessed": PENDING,
        },
    ]
    assert document["windows"][:-1] == COMMITTED["windows"]
    assert document["windows"][-1] == {
        "label": SLICE_LABEL,
        "digest": SLICE_PREDICTOR,
        "predictor_id": "claude-trial",
        "opens": PENDING,
        "closes": None,
        "revoked_at": None,
    }
    labels = document["evaluate_blessing_labels"]
    assert labels[SLICE_JUDGE] == [SLICE_LABEL]
    assert {d: named for d, named in labels.items() if d != SLICE_JUDGE} == (
        COMMITTED["evaluate_blessing_labels"]
    )


def test_a_slice_label_never_moves_the_scotus_counting_instant() -> None:
    committed = _load(COMMITTED)
    pending = _load(_slice_registered())
    carried = _load(_carried_to_main(_slice_registered()))
    for registry in (pending, carried):
        assert counting_instant(registry) == counting_instant(committed)
        scotus_moments = {
            digest: moment
            for digest, moment in bless_moments(registry).items()
            if digest not in (SLICE_PREDICTOR, SLICE_JUDGE)
        }
        assert scotus_moments == bless_moments(committed)
    assert counting_instant(pending, SLICE) is None
    assert registered_windows(pending) == registered_windows(committed)
    assert counting_instant(carried, SLICE) == MERGED_AT
    (opened,) = [w for w in registered_windows(carried) if w.label == SLICE_LABEL]
    assert (opened.predictor_id, opened.opens, opened.closes) == ("claude-trial", MERGED_AT, None)


def test_a_pending_slice_label_loads_under_the_scotus_label_the_code_stamps() -> None:
    document = _slice_registered()
    assert scotus_label_of(document) == LAST_LABEL
    assert _load(document).labels[-1].since.pending


def test_a_scotus_registration_after_a_slice_label_leaves_the_slice_s_rows() -> None:
    main = _carried_to_main(_slice_registered())
    document = register_process(main, NEW_LABEL, [*_live_fleet(), *_slice_actors()])
    assert document["labels"][-1] == {"label": NEW_LABEL, "since": PENDING}
    assert scotus_label_of(document) == NEW_LABEL
    slice_rows = [b for b in main["blessings"] if b["label"] == SLICE_LABEL]
    assert [b for b in document["blessings"] if b["label"] == SLICE_LABEL] == slice_rows
    (slice_window,) = [w for w in document["windows"] if w["label"] == SLICE_LABEL]
    assert slice_window["closes"] is None
    assert document["evaluate_blessing_labels"][SLICE_JUDGE] == [SLICE_LABEL]
    closed = [w["predictor_id"] for w in document["windows"] if w["closes"] == PENDING]
    assert closed == ["claude-baseline"]
    by_digest = {b["digest"]: b for b in document["blessings"]}
    assert by_digest[NEW_CLAUDE]["label"] == NEW_LABEL
    registry = _load(document, NEW_LABEL)
    assert counting_instant(registry, SLICE) == MERGED_AT


def test_a_slice_s_second_label_closes_the_slice_s_window_alone() -> None:
    main = _carried_to_main(_slice_registered())
    document = register_process(main, f"{SLICE}-v2", _fleet(predictor=MOVED_SLICE_PREDICTOR), SLICE)
    assert document["labels"][-1] == {
        "label": f"{SLICE}-v2",
        "since": PENDING,
        "population": SLICE,
    }
    closed = [w for w in document["windows"] if w["closes"] == PENDING]
    assert [(w["predictor_id"], w["label"]) for w in closed] == [("claude-trial", SLICE_LABEL)]
    assert document["windows"][-1]["digest"] == MOVED_SLICE_PREDICTOR
    assert document["evaluate_blessing_labels"][SLICE_JUDGE] == [SLICE_LABEL, f"{SLICE}-v2"]
    scotus = [b for b in document["blessings"] if b["label"].startswith("proc-")]
    assert scotus == COMMITTED["blessings"]
    _load(document)


def test_a_slice_s_evaluator_only_label_holds_the_slice_s_instant() -> None:
    main = _carried_to_main(_slice_registered())
    document = register_process(main, f"{SLICE}-v2", _fleet(judge=MOVED_SLICE_JUDGE), SLICE)
    held = next(row for row in main["labels"] if row["label"] == SLICE_LABEL)["since"]
    assert document["labels"][-1]["since"] == held
    assert held["at"] == _iso(MERGED_AT)
    assert document["windows"] == main["windows"]
    assert document["evaluate_blessing_labels"][MOVED_SLICE_JUDGE] == [f"{SLICE}-v2"]
    _load(document)


def test_a_scotus_evaluator_only_label_after_a_slice_label_holds_the_scotus_instant() -> None:
    main = _carried_to_main(_slice_registered())
    moved_judge = "sha256:" + "5" * 64
    fleet = [*_live_fleet(claude=_carried("claude-baseline"), judge=moved_judge), *_slice_actors()]
    document = register_process(main, NEW_LABEL, fleet)
    assert document["labels"][-1] == {
        "label": NEW_LABEL,
        "since": _label_row(main, LAST_LABEL)["since"],
    }
    assert document["labels"][-1]["since"] != _label_row(main, SLICE_LABEL)["since"]
    assert document["windows"] == main["windows"]
    registry = _load(document, NEW_LABEL)
    assert counting_instant(registry) == counting_instant(_load(COMMITTED))
    assert counting_instant(registry, SLICE) == MERGED_AT


@pytest.mark.parametrize(
    ("label", "population", "fleet", "match"),
    [
        ("proc-v99", SLICE, _fleet(), f"{SLICE}-vN"),
        (SLICE_LABEL, "scotus", _fleet(), "proc-vN"),
        (
            SLICE_LABEL,
            SLICE,
            _fleet(predictor=_carried("codex-baseline")),
            "never share a process",
        ),
        (
            SLICE_LABEL,
            SLICE,
            [*_live_fleet(), LiveActor("evaluator", "claude-trial-judge", SLICE_JUDGE, SLICE)],
            "no enabled predictor",
        ),
        (SLICE_LABEL, SLICE, _live_fleet(), "no digest moved"),
    ],
)
def test_a_slice_registration_the_registry_cannot_take_is_refused(
    label: str, population: str, fleet: list[LiveActor], match: str
) -> None:
    with pytest.raises(RegistrationError, match=match):
        register_process(DECLARED, label, fleet, population)


def test_a_slice_label_waits_behind_a_pending_scotus_label_and_the_reverse() -> None:
    scotus_pending = register_process(DECLARED, NEW_LABEL, _live_fleet())
    with pytest.raises(RegistrationError, match="already waiting"):
        register_process(scotus_pending, SLICE_LABEL, [*_live_fleet(), *_slice_actors()], SLICE)
    with pytest.raises(RegistrationError, match="already waiting"):
        register_process(_slice_registered(), NEW_LABEL, [*_live_fleet(), *_slice_actors()])


# --- the loader --------------------------------------------------------------


def _label_row(document: dict[str, Any], label: str) -> dict[str, Any]:
    row: dict[str, Any] = next(row for row in document["labels"] if row["label"] == label)
    return row


def _mutated(mutate: Any) -> dict[str, Any]:
    document = copy.deepcopy(_carried_to_main(_slice_registered()))
    mutate(document)
    return document


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda d: d["labels"][-1].pop("population"), "not a label of population 'scotus'"),
        (lambda d: d["labels"][-1].update(population="no-such-slice"), "names population"),
        (lambda d: d["labels"][-1].update(label="proc-v99"), "not a label of population"),
        (lambda d: d["labels"][0].update(population=SLICE), "not a label of population"),
        (
            lambda d: d["windows"][-1].update(closes=d["labels"][0]["since"]),
            "closes off every counting instant of its population",
        ),
        (
            lambda d: d["windows"][-1].update(
                label=LAST_LABEL, opens=dict(_label_row(d, LAST_LABEL)["since"])
            ),
            "its digest is blessed for 'ai-watchlist'",
        ),
        (
            lambda d: d["windows"].append(
                dict(d["windows"][-1], predictor_id="claude-baseline", digest="sha256:" + "9" * 64)
            ),
            "claude-baseline has windows in two populations",
        ),
        (
            lambda d: d["evaluate_blessing_labels"][_carried("claude-judge")].append(SLICE_LABEL),
            "blessed by labels of two populations",
        ),
        (
            lambda d: d["evaluate_blessing_labels"][SLICE_JUDGE].append(LAST_LABEL),
            "blessed by labels of two populations",
        ),
    ],
    ids=[
        "slice-row-without-its-population",
        "undeclared-population",
        "slice-row-named-like-scotus",
        "scotus-row-moved-to-a-slice",
        "slice-window-closing-at-a-scotus-instant",
        "slice-digest-window-under-a-scotus-label",
        "scotus-predictor-window-under-a-slice-label",
        "slice-label-on-a-scotus-judge-digest",
        "scotus-label-on-a-slice-judge-digest",
    ],
)
def test_a_registry_that_mixes_populations_is_refused(mutate: Any, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        _load(_mutated(mutate))


def test_the_code_s_label_must_be_a_scotus_row() -> None:
    with pytest.raises(ValueError, match=f"no label row for {SLICE_LABEL}"):
        _load(_carried_to_main(_slice_registered()), SLICE_LABEL)


# --- what a cell is stamped with, and what a board records ---------------------


def test_a_slice_label_takes_no_scotus_threshold() -> None:
    assert label_ordinal(SLICE_LABEL) is None
    assert not asked_authorship_claims(SLICE_LABEL, states_distributions=True)
    assert not process_version.harness_stamps_cert_anchor(SLICE_LABEL)
    assert not process_version.scores_finer_interim_reading(SLICE_LABEL)


def test_each_population_s_cells_are_stamped_with_its_own_label(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert process_version.current_label() == process_version.CURRENT_PROCESS_LABEL
    if not any(e.population == SLICE for e in process_version._REGISTRY.labels):
        with pytest.raises(KeyError, match=SLICE):
            process_version.current_label(SLICE)
    monkeypatch.setattr(process_version, "_REGISTRY", _load(_slice_registered()))
    assert process_version.current_label(SLICE) == SLICE_LABEL
    assert process_version.current_label() == process_version.CURRENT_PROCESS_LABEL

    root = Path(__file__).resolve().parents[1] / "config"
    for name, section in (("predictors.yaml", "predictors"), ("evaluators.yaml", "evaluators")):
        data = yaml.safe_load((root / name).read_text(encoding="utf-8"))
        data[section].append(dict(data[section][0], id="slice-actor", population=SLICE))
        (tmp_path / name).write_text(yaml.safe_dump(data), encoding="utf-8")
    for role in ("predictor", "evaluator"):
        assert process_version.label_for_actor(tmp_path, role, "slice-actor") == SLICE_LABEL
    assert (
        process_version.label_for_actor(tmp_path, "predictor", "claude-baseline")
        == process_version.CURRENT_PROCESS_LABEL
    )


def test_stamp_cell_writes_the_slice_s_label_on_a_slice_actor_s_cell(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = tmp_path / "config"
    config.mkdir()
    root = Path(__file__).resolve().parents[1] / "config"
    for name, section in (("predictors.yaml", "predictors"), ("evaluators.yaml", "evaluators")):
        data = yaml.safe_load((root / name).read_text(encoding="utf-8"))
        data[section].append(dict(data[section][0], id="slice-actor", population=SLICE))
        (config / name).write_text(yaml.safe_dump(data), encoding="utf-8")
    data_root = tmp_path / "data"
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    seed_prediction(data_root, "scotus", 1, "evt-x", predictor_id="slice-actor")
    seed_prediction(data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    event = CasePaths(data_root, "scotus", 1).event("evt-x")

    def stamp(actor: str) -> Any:
        return CliRunner().invoke(
            app,
            [
                "stamp-cell",
                *("--court", "scotus", "--docket", "1", "--event", "evt-x"),
                *("--run-id", "20260101T000000Z", "--role", "predictor", "--actor", actor),
                *("--stamped-at", "2026-01-01T00:00:00Z", "--pipeline-sha", "sha-abc"),
            ],
        )

    def label(actor: str) -> Any:
        stamped = json.loads(event.prediction(actor, "20260101T000000Z").read_text())
        return (stamped["process_version"] or {}).get("label")

    if not any(e.population == SLICE for e in process_version._REGISTRY.labels):
        # No label registered for the slice: its cell is refused, unstamped.
        assert stamp("slice-actor").exit_code != 0
        assert label("slice-actor") is None
    monkeypatch.setattr(process_version, "_REGISTRY", _load(_slice_registered()))
    assert stamp("slice-actor").exit_code == 0
    assert label("slice-actor") == SLICE_LABEL
    assert stamp("claude-baseline").exit_code == 0
    assert label("claude-baseline") == process_version.CURRENT_PROCESS_LABEL


def _install(monkeypatch: pytest.MonkeyPatch, document: dict[str, Any]) -> None:
    """Build the module's freeze constants from ``document``, as an import would."""
    registry = _load(document)
    monkeypatch.setattr(process_version, "_REGISTRY", registry)
    monkeypatch.setattr(process_version, "FROZEN_PROCESS_DIGESTS", bless_moments(registry))
    monkeypatch.setattr(process_version, "FROZEN_SINCE", counting_instant(registry))
    monkeypatch.setattr(process_version, "COUNTING_WINDOWS", registered_windows(registry))


def test_a_scotus_board_s_record_holds_no_slice_row(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, COMMITTED)
    before = process_version.frozen_process_record()
    assert before.windows == list(process_version.COUNTING_WINDOWS)
    assert before.digests == sorted(process_version.FROZEN_PROCESS_DIGESTS)
    _install(monkeypatch, _carried_to_main(_slice_registered()))
    assert process_version.frozen_process_record() == before
    assert len(process_version.COUNTING_WINDOWS) == len(before.windows) + 1
    own = process_version.frozen_process_record(SLICE)
    assert own.digests == sorted([SLICE_PREDICTOR, SLICE_JUDGE])
    assert own.since == MERGED_AT
    assert [w.label for w in own.windows] == [SLICE_LABEL]

    _install(monkeypatch, _slice_registered())
    assert process_version.frozen_process_record() == before
    pending = process_version.frozen_process_record(SLICE)
    assert (pending.digests, pending.since, pending.windows) == ([], None, [])
    assert f"label {SLICE_LABEL}" in pending.pending


def test_a_slice_s_prereg_tag_lists_the_slice_s_digests_alone() -> None:
    message = _prereg_message(_slice_registered(), SLICE_LABEL, MERGE, _iso(MERGED_AT))
    assert SLICE_PREDICTOR in message and SLICE_JUDGE in message
    assert not any(str(b["digest"]) in message for b in COMMITTED["blessings"])
    scotus = _prereg_message(
        register_process(
            _carried_to_main(_slice_registered()), NEW_LABEL, [*_live_fleet(), *_slice_actors()]
        ),
        NEW_LABEL,
        MERGE,
        _iso(MERGED_AT),
    )
    assert NEW_CLAUDE in scotus and SLICE_PREDICTOR not in scotus


# --- the gate ----------------------------------------------------------------


def test_a_slice_registration_passes_the_gate(tmp_path: Path) -> None:
    repo, at = _history(tmp_path, staging_registry=_slice_registered())
    result = registry_gate(repo, at, "main", _fleet())
    assert result.problems == []
    # The slice label's counting instant, its two blessings and the window it opens.
    assert result.pending == 4


def test_a_slice_actor_under_a_scotus_label_is_refused(tmp_path: Path) -> None:
    registry = _slice_registered()
    for blessing in registry["blessings"]:
        if blessing["digest"] == SLICE_PREDICTOR:
            blessing["label"] = LAST_LABEL
            blessing["blessed"] = dict(COMMITTED["labels"][-1]["since"])
    registry["windows"] = [w for w in registry["windows"] if w["label"] != SLICE_LABEL]
    repo, at = _history(tmp_path, staging_registry=registry)
    problems = registry_gate(repo, at, "main", _fleet()).problems
    assert any(
        "claude-trial" in p and "a label blesses its own population's actors" in p for p in problems
    )


def test_a_scotus_actor_under_a_slice_label_is_refused(tmp_path: Path) -> None:
    repo, at = _history(tmp_path, staging_registry=_slice_registered())
    fleet = [
        *_live_fleet(claude=_carried("claude-baseline")),
        LiveActor("predictor", "claude-trial", SLICE_PREDICTOR),
        LiveActor("evaluator", "claude-trial-judge", SLICE_JUDGE, SLICE),
    ]
    problems = registry_gate(repo, at, "main", fleet).problems
    assert any("'scotus'" in p and SLICE_LABEL in p for p in problems)


def test_a_scotus_label_after_a_carried_slice_label_passes_the_gate(tmp_path: Path) -> None:
    """The SCOTUS label follows the slice row main stamped, and loads under its own name."""
    main = _carried_to_main(_slice_registered())
    fleet = [*_live_fleet(), *_slice_actors()]
    staging = register_process(main, NEW_LABEL, fleet)
    assert [row["label"] for row in staging["labels"][-2:]] == [SLICE_LABEL, NEW_LABEL]
    repo, at = _history(tmp_path, main_registry=main, staging_registry=staging)
    result = registry_gate(repo, at, "main", fleet)
    assert result.problems == []
    # The label's counting instant, its one new blessing, the window it opens and
    # the claude-baseline window it closes.
    assert result.pending == 4
