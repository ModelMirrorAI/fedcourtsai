"""Pending registrations and the promotion record a staging→main merge owes ``main``.

The registry side: a label a PR registers is pending until the merge that
carries it stamps it, and every reader treats a pending row in the safe
direction. The git side runs on a synthetic history — a ``main`` holding the
committed registry, a ``staging`` that registers a new label and appends a
freeze-record entry with placeholders, and the ``--no-ff`` merge between them
at a fixed committer time — so the plan, the render, the apply, the jail and
the main check are exercised against git rather than a stand-in.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version
from fedcourtsai.cli import app
from fedcourtsai.process_registration import (
    LiveActor,
    RegistrationError,
    register_boundary,
    register_process,
    set_current_label,
)
from fedcourtsai.process_version import (
    bless_moments,
    counting_instant,
    harness_boundaries,
    load_process_registry,
    registered_windows,
)
from fedcourtsai.promotion_record import (
    FREEZE_RECORD_PATH,
    RECORD_PATHS,
    REGISTRY_PATH,
    PromotionRecordError,
    Stamp,
    apply_promotion_record,
    digest_census,
    dump_registry,
    pending_carried_problems,
    placeholders,
    plan_promotion_record,
    promotion_record_diff_problems,
    render_promotion_record,
)
from fedcourtsai.schemas import FrozenProcessRecord
from fedcourtsai.store import predictor_holds_no_counted_prediction
from tests.conftest import set_windows
from tests.test_counting_windows import CLOSED, SUCCESSOR, T2, _pv, _seed

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = json.loads((ROOT / REGISTRY_PATH).read_text(encoding="utf-8"))
#: The committed registry once the merge-stamping rule is declared.
DECLARED = {**COMMITTED, "merge_stamping_declared": "2026-11-01"}
NEW_CLAUDE = "sha256:" + "a" * 64
NEW_JUDGE = "sha256:" + "d" * 64
NEW_LABEL = "proc-v10"
MERGED_AT = datetime(2026, 10, 13, 15, 4, 5, tzinfo=UTC)
PENDING = {"at": None, "merge": None, "source": "merge"}


def _live_fleet(*, claude: str = NEW_CLAUDE, judge: str | None = None) -> list[LiveActor]:
    """The committed blessings as a live fleet, claude-baseline's (or claude-judge's) moved."""
    moved = {"claude-baseline": claude, "claude-judge": judge}
    return [
        LiveActor(
            blessing["role"],
            blessing["actor_id"],
            moved.get(blessing["actor_id"]) or blessing["digest"],
        )
        for blessing in COMMITTED["blessings"]
    ]


def _registered() -> dict[str, Any]:
    return register_process(DECLARED, NEW_LABEL, _live_fleet())


def _carried_claude() -> str:
    digests = [b["digest"] for b in COMMITTED["blessings"] if b["actor_id"] == "claude-baseline"]
    return str(digests[0])


# --- registration ------------------------------------------------------------


def test_registering_a_moved_process_writes_pending_rows_and_carries_the_rest() -> None:
    document = _registered()
    assert document["labels"][-1] == {"label": NEW_LABEL, "since": PENDING}
    by_digest = {b["digest"]: b for b in document["blessings"]}
    assert by_digest[NEW_CLAUDE]["blessed"] == PENDING
    assert by_digest[NEW_CLAUDE]["label"] == NEW_LABEL
    originals = {b["digest"]: b for b in COMMITTED["blessings"]}
    assert all(
        b == originals[b["digest"]] for b in document["blessings"] if b["digest"] in originals
    )
    closed = [w for w in document["windows"] if w["closes"] == PENDING]
    assert [(w["predictor_id"], w["label"]) for w in closed] == [("claude-baseline", "proc-v9")]
    assert [w for w in document["windows"] if w not in closed and w["label"] != NEW_LABEL] == [
        w for w in COMMITTED["windows"] if w["digest"] != closed[0]["digest"]
    ]
    assert [w for w in document["windows"] if w["label"] == NEW_LABEL] == [
        {
            "label": NEW_LABEL,
            "digest": NEW_CLAUDE,
            "predictor_id": "claude-baseline",
            "opens": PENDING,
            "closes": None,
            "revoked_at": None,
        }
    ]
    for blessing in document["blessings"]:
        if blessing["role"] == "evaluator":
            assert document["evaluate_blessing_labels"][blessing["digest"]][-1] == NEW_LABEL


def test_an_evaluator_only_label_holds_the_instant_and_opens_no_window() -> None:
    document = register_process(
        DECLARED, NEW_LABEL, _live_fleet(claude=_carried_claude(), judge=NEW_JUDGE)
    )
    assert document["labels"][-1]["since"] == COMMITTED["labels"][-1]["since"]
    assert document["windows"] == COMMITTED["windows"]
    judge = next(b for b in document["blessings"] if b["digest"] == NEW_JUDGE)
    assert judge["blessed"] == PENDING and judge["label"] == NEW_LABEL
    assert document["evaluate_blessing_labels"][NEW_JUDGE] == [NEW_LABEL]
    registry = load_process_registry(dump_registry(document), current_label=NEW_LABEL)
    assert counting_instant(registry) == counting_instant(load_process_registry())


def test_a_pending_registration_loads_under_its_own_label_only() -> None:
    text = dump_registry(_registered())
    registry = load_process_registry(text, current_label=NEW_LABEL)
    assert registry.labels[-1].since.pending
    with pytest.raises(ValueError, match="may be pending"):
        load_process_registry(text)


def test_pending_rows_read_in_the_safe_direction() -> None:
    """Nothing pending counts, opens, closes or splits until its merge stamps it."""
    registry = load_process_registry(dump_registry(_registered()), current_label=NEW_LABEL)
    committed = load_process_registry()
    assert counting_instant(registry) == counting_instant(committed)
    moments = bless_moments(registry)
    assert NEW_CLAUDE not in moments
    assert all(moments[d] == m for d, m in bless_moments(committed).items() if d in moments)
    assert registered_windows(registry) == registered_windows(committed)


def test_a_pending_boundary_is_registered_but_splits_nothing() -> None:
    document = register_boundary(
        COMMITTED, "test-change", predictors=None, reach="all", gradual=False
    )
    registry = load_process_registry(dump_registry(document))
    assert registry.harness_boundaries[-1].pending
    assert harness_boundaries(registry) == harness_boundaries(load_process_registry())


def test_a_pending_boundary_does_not_block_a_label() -> None:
    document = register_boundary(
        DECLARED, "test-change", predictors=None, reach="all", gradual=False
    )
    registered = register_process(document, NEW_LABEL, _live_fleet())
    assert registered["labels"][-1]["label"] == NEW_LABEL


def test_no_label_is_registered_before_the_rule_is_declared() -> None:
    with pytest.raises(RegistrationError, match="merge_stamping_declared"):
        register_process(COMMITTED, NEW_LABEL, _live_fleet())


@pytest.mark.parametrize(
    ("label", "fleet", "match"),
    [
        ("proc-v9", _live_fleet(), "already registered"),
        ("proc-v8b", _live_fleet(), "proc-vN"),
        ("proc-v7", _live_fleet(), "already registered|does not follow"),
        (NEW_LABEL, _live_fleet(claude=COMMITTED["blessings"][0]["digest"]), "no digest moved"),
    ],
)
def test_a_registration_the_registry_cannot_take_is_refused(
    label: str, fleet: list[LiveActor], match: str
) -> None:
    with pytest.raises(RegistrationError, match=match):
        register_process(DECLARED, label, fleet)


def test_a_second_registration_waits_for_the_first_merge() -> None:
    with pytest.raises(RegistrationError, match="already waiting"):
        register_process(_registered(), "proc-v11", _live_fleet(claude="sha256:" + "b" * 64))


def test_a_reused_boundary_name_is_refused() -> None:
    name = COMMITTED["harness_boundaries"][0]["name"]
    with pytest.raises(RegistrationError, match="already registered"):
        register_boundary(COMMITTED, name, predictors=None, reach="all", gradual=False)


def test_the_label_line_is_set_once() -> None:
    source = 'X = 1\nCURRENT_PROCESS_LABEL = "proc-v9"\n'
    assert set_current_label(source, NEW_LABEL) == 'X = 1\nCURRENT_PROCESS_LABEL = "proc-v10"\n'
    with pytest.raises(RegistrationError, match="other than once"):
        set_current_label(source + source, NEW_LABEL)


def test_a_pending_blessing_under_a_carried_label_is_refused() -> None:
    raw = json.loads(json.dumps(COMMITTED))
    carried = next(b for b in raw["blessings"] if b["label"] != raw["labels"][-1]["label"])
    carried["blessed"] = dict(PENDING)
    with pytest.raises(ValueError, match="not the label being registered"):
        load_process_registry(json.dumps(raw))


def test_a_stamped_blessing_under_a_pending_label_is_refused() -> None:
    document = _registered()
    blessing = next(b for b in document["blessings"] if b["digest"] == NEW_CLAUDE)
    blessing["blessed"] = {"at": "2026-11-01T00:00:00Z", "merge": "f" * 40, "source": "merge"}
    with pytest.raises(ValueError, match="still pending"):
        load_process_registry(dump_registry(document), current_label=NEW_LABEL)


def test_a_pending_close_with_no_label_pending_is_refused() -> None:
    raw = json.loads(json.dumps(COMMITTED))
    raw["windows"][1]["closes"] = dict(PENDING)
    with pytest.raises(ValueError, match="no label pending"):
        load_process_registry(json.dumps(raw))


def test_the_board_record_lists_pending_rows_and_omits_an_empty_list() -> None:
    assert "pending" not in process_version.frozen_process_record().model_dump(mode="json")
    record = FrozenProcessRecord(digests=[], since=None, pending=[f"label {NEW_LABEL}"])
    assert record.model_dump(mode="json")["pending"] == [f"label {NEW_LABEL}"]


def test_a_pending_cell_is_not_re_owed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A cell whose digest is registered but not yet stamped is pending, not de-counted."""
    pending = "sha256:" + "e" * 64
    data = tmp_path / "data"
    _seed(data, run_id="p1", stamp=_pv(pending, T2 + timedelta(days=1)))
    args = (data, "scotus", 1, "evt-petition-disposition", "alpha")
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    assert predictor_holds_no_counted_prediction(*args)  # an unregistered digest: de-counted
    monkeypatch.setattr(
        process_version,
        "REGISTERED_PROCESS_DIGESTS",
        frozenset(process_version.FROZEN_PROCESS_DIGESTS) | {pending},
    )
    assert not predictor_holds_no_counted_prediction(*args)


# --- placeholders ------------------------------------------------------------


def test_a_mention_and_an_unclosed_marker_are_not_placeholders() -> None:
    text = (
        "The `<FILL:>` placeholders and `<FILL: …>` are prose.\n"
        "Owes <FILL: apply run\n  id> here.\n"
        "An unclosed <FILL: merged-at\n\nNext paragraph> is not one.\n"
        "Nor is <FILL: `promotion tag`>.\n"
    )
    assert [key for key, *_ in placeholders(text)] == ["apply run id"]


# --- the synthetic promotion -------------------------------------------------

_ENTRY_BEFORE = (
    "# Freeze record\n\n- **An earlier entry.** Owes `<FILL: promotion tag>` still.\n"
    "  Its census, `<FILL: merge hash>`, was landed before.\n"
)
_ENTRY_ADDED = (
    "\n- **A new entry, 2026-11-01.** Carried to `main` by `<FILL: promotion tag>` (merge\n"
    "  commit `<FILL: merge hash>`, merged `<FILL: merged-at>`). Predictions under the new\n"
    "  digest at the merge: `<FILL:census predictions\n  digest=aaaaaaaa>`. Applied by run\n"
    "  `<FILL: apply run id>`.\n"
)


def _git(repo: Path, *args: str, when: datetime | None = None) -> str:
    env = dict(os.environ)
    if when is not None:
        stamp = when.strftime("%Y-%m-%dT%H:%M:%SZ")
        env["GIT_COMMITTER_DATE"] = stamp
        env["GIT_AUTHOR_DATE"] = stamp
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=True, text=True, env=env
    ).stdout.strip()


def _write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _read(repo: Path, path: str) -> str:
    return (repo / path).read_text(encoding="utf-8")


def _artifact(repo: Path, kind: str, docket: int, digest: str) -> None:
    name = "prediction.json" if kind == "predictions" else "evaluation.json"
    folder = (
        "predictions/claude-baseline" if kind == "predictions" else "evaluations/j/claude-baseline"
    )
    _write(
        repo,
        f"data/cases/scotus/{docket}/events/evt-x/{folder}/20261101T000000Z/{name}",
        json.dumps({"process_version": {"digest": digest}}),
    )


def _commit(repo: Path, message: str, when: datetime) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message, when=when)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def promotion(tmp_path: Path) -> tuple[Path, str]:
    """``main`` with the committed registry, ``staging`` registering proc-v10, merged."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE)
    _artifact(repo, "predictions", 1, "sha256:" + "c" * 64)
    _commit(repo, "main", datetime(2026, 10, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE + _ENTRY_ADDED)
    _artifact(repo, "predictions", 2, NEW_CLAUDE)
    _artifact(repo, "predictions", 3, NEW_CLAUDE)
    _artifact(repo, "evaluations", 2, NEW_CLAUDE)
    _commit(repo, "register proc-v10", datetime(2026, 10, 12, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    return repo, _git(repo, "rev-parse", "HEAD")


def _old_claude_window() -> str:
    return next(
        f"{w['label']} {w['digest']}"
        for w in COMMITTED["windows"]
        if w["predictor_id"] == "claude-baseline" and w["closes"] is None
    )


def test_the_plan_names_the_tag_the_fills_and_the_stamps(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    plan = plan_promotion_record(repo, merge)
    assert plan.merged_at == "2026-10-13T15:04:05Z"
    assert (plan.promotion_tag.name, plan.promotion_tag.adopt) == ("promotion/2026-10-13", False)
    assert {(fill.key, fill.value) for fill in plan.fills} == {
        ("promotion tag", "promotion/2026-10-13"),
        ("merge hash", merge),
        ("merged-at", "2026-10-13T15:04:05Z"),
        # Wrapped across a line, and counting the two predictions, not the evaluation.
        ("census predictions digest=aaaaaaaa", "2"),
    }
    assert [fill.key for fill in plan.free_text] == ["apply run id"]
    assert sorted(fill.key for fill in plan.stale_placeholders) == ["merge hash", "promotion tag"]
    assert set(plan.stamps) == {
        Stamp("label", NEW_LABEL),
        Stamp("blessing", NEW_CLAUDE),
        Stamp("window-opens", f"{NEW_LABEL} {NEW_CLAUDE}"),
        Stamp("window-closes", _old_claude_window()),
    }
    assert plan.stale_pending == []
    assert plan.prereg_tag is not None and plan.prereg_tag.name == f"prereg/{NEW_LABEL}"
    assert NEW_CLAUDE in plan.prereg_tag.message


def test_a_typo_fix_on_a_landed_placeholder_line_is_stale(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, "- **An entyr.** Owes `<FILL: merge hash>`.\n")
    _commit(repo, "main", datetime(2026, 10, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, FREEZE_RECORD_PATH, "- **An entry.** Owes `<FILL: merge hash>`.\n")
    _commit(repo, "typo", datetime(2026, 10, 12, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    plan = plan_promotion_record(repo, _git(repo, "rev-parse", "HEAD"))
    assert plan.fills == [] and [f.key for f in plan.stale_placeholders] == ["merge hash"]


def test_an_evaluator_only_label_is_tagged_on_its_merge(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, "# Freeze record\n")
    _commit(repo, "main", datetime(2026, 10, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "-c", "staging")
    judge_only = register_process(
        DECLARED, NEW_LABEL, _live_fleet(claude=_carried_claude(), judge=NEW_JUDGE)
    )
    _write(repo, REGISTRY_PATH, dump_registry(judge_only))
    _commit(repo, "register", datetime(2026, 10, 12, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    plan = plan_promotion_record(repo, _git(repo, "rev-parse", "HEAD"))
    assert plan.stamps == [Stamp("blessing", NEW_JUDGE)]
    assert plan.prereg_tag is not None and "holds the counting instant" in plan.prereg_tag.message


def test_a_taken_date_takes_the_next_suffix_and_an_existing_tag_is_adopted(
    promotion: tuple[Path, str],
) -> None:
    repo, merge = promotion
    _git(repo, "tag", "-a", "promotion/2026-10-13", "-m", "another", f"{merge}^1")
    assert plan_promotion_record(repo, merge).promotion_tag.name == "promotion/2026-10-13-2"
    _git(repo, "tag", "-a", "promotion/2026-10-13-2", "-m", "this one", merge)
    tag = plan_promotion_record(repo, merge).promotion_tag
    assert (tag.name, tag.adopt) == ("promotion/2026-10-13-2", True)


def test_apply_fills_and_stamps_once_and_loads(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    plan = plan_promotion_record(repo, merge)
    assert sorted(apply_promotion_record(repo, repo, plan)) == sorted(RECORD_PATHS)
    record = _read(repo, FREEZE_RECORD_PATH)
    assert f"`{merge}`" in record and "`2`" in record and "<FILL: apply run id>" in record
    assert record.count("<FILL: promotion tag>") == 1  # the earlier entry's, untouched
    registry = load_process_registry(_read(repo, REGISTRY_PATH), current_label=NEW_LABEL)
    assert registry.labels[-1].since.at == MERGED_AT
    assert registry.labels[-1].since.merge == merge
    assert bless_moments(registry)[NEW_CLAUDE] == MERGED_AT
    assert any(
        w.digest == NEW_CLAUDE and w.opens == MERGED_AT for w in registered_windows(registry)
    )
    assert apply_promotion_record(repo, repo, plan_promotion_record(repo, merge)) == []


def test_apply_writes_nothing_when_the_registry_is_refused(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    before = {path: _read(repo, path) for path in RECORD_PATHS}

    def refuse(_text: str) -> None:
        raise ValueError("refused")

    with pytest.raises(PromotionRecordError, match="refused"):
        apply_promotion_record(
            repo, repo, plan_promotion_record(repo, merge), check_registry=refuse
        )
    assert {path: _read(repo, path) for path in RECORD_PATHS} == before


def test_apply_carries_onto_a_tip_that_moved_on(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    _write(repo, FREEZE_RECORD_PATH, _read(repo, FREEZE_RECORD_PATH) + "\n- **A later entry.**\n")
    apply_promotion_record(repo, repo, plan_promotion_record(repo, merge))
    record = _read(repo, FREEZE_RECORD_PATH)
    assert "A later entry." in record and f"`{merge}`" in record


def test_a_registration_the_parent_already_held_is_stale_not_stamped(
    promotion: tuple[Path, str],
) -> None:
    repo, _ = promotion
    _git(repo, "switch", "-q", "-c", "late")
    _write(repo, "data/note.txt", "x")
    _commit(repo, "late", MERGED_AT)
    _git(repo, "switch", "-q", "main")
    later = MERGED_AT + timedelta(hours=1)
    _git(repo, "merge", "-q", "--no-ff", "late", "-m", "second promotion", when=later)
    second = _git(repo, "rev-parse", "HEAD")
    plan = plan_promotion_record(repo, second)
    assert plan.stamps == [] and plan.fills == []
    assert Stamp("label", NEW_LABEL) in plan.stale_pending
    # Rendering the second merge's plan stamps nothing, so a stamp of the stale row is refused.
    before = {path: _read(repo, path) for path in RECORD_PATHS}
    forged = json.loads(before[REGISTRY_PATH])
    forged["labels"][-1]["since"] = {
        "at": "2026-10-13T16:04:05Z",
        "merge": second,
        "source": "merge",
    }
    after = {**before, REGISTRY_PATH: dump_registry(forged)}
    expected = render_promotion_record(repo, plan, before)
    problems = promotion_record_diff_problems([REGISTRY_PATH], before, after, expected=expected)
    assert any("differs from the plan" in problem for problem in problems)


def test_a_commit_that_is_not_a_merge_is_refused(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    with pytest.raises(PromotionRecordError, match="two-parent"):
        plan_promotion_record(repo, f"{merge}^1")


def test_a_merge_committed_before_its_parent_is_refused(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _write(repo, "a.txt", "a")
    _commit(repo, "main", MERGED_AT)
    _git(repo, "switch", "-q", "-c", "side")
    _write(repo, "b.txt", "b")
    _commit(repo, "side", MERGED_AT)
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "side", "-m", "m", when=MERGED_AT - timedelta(days=1))
    with pytest.raises(PromotionRecordError, match="before its first parent"):
        plan_promotion_record(repo, _git(repo, "rev-parse", "HEAD"))


def test_a_merge_before_a_registered_instant_is_refused(tmp_path: Path) -> None:
    """Stamping with a time before the instants already registered would close a window early."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _commit(repo, "main", datetime(2026, 10, 1, tzinfo=UTC))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _commit(repo, "register", datetime(2026, 10, 1, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "main")
    _git(
        repo, "merge", "-q", "--no-ff", "staging", "-m", "m", when=datetime(2026, 10, 2, tzinfo=UTC)
    )
    with pytest.raises(PromotionRecordError, match="before the registered instant"):
        plan_promotion_record(repo, _git(repo, "rev-parse", "HEAD"))


def test_the_census_reads_stamps_on_the_merge_tree(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    assert digest_census(repo, merge, "predictions", ["aaaaaaaa"]) == 2
    assert digest_census(repo, merge, "evaluations", ["sha256:aaaaaaaa"]) == 1
    assert digest_census(repo, merge, "predictions", ["aaaaaaaa", "cccccccc"]) == 3
    assert digest_census(repo, f"{merge}^1", "predictions", ["aaaaaaaa"]) == 0


# --- main must hold nothing pending ------------------------------------------


def test_main_holding_a_carried_pending_row_is_named_until_stamped(
    promotion: tuple[Path, str],
) -> None:
    repo, merge = promotion
    problems = pending_carried_problems(repo, "HEAD")
    assert any(f"label {NEW_LABEL}: carried by {merge}" in problem for problem in problems)
    apply_promotion_record(repo, repo, plan_promotion_record(repo, merge))
    _commit(repo, "promotion record", MERGED_AT + timedelta(minutes=1))
    assert pending_carried_problems(repo, "HEAD") == []


# --- the jail ----------------------------------------------------------------


def _texts(repo: Path, rev: str) -> dict[str, str | None]:
    return {
        path: subprocess.run(
            ["git", "-C", str(repo), "show", f"{rev}:{path}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        for path in RECORD_PATHS
    }


def _jail(repo: Path, merge: str, after: dict[str, str | None], changed: list[str]) -> list[str]:
    before = _texts(repo, merge)
    expected = render_promotion_record(repo, plan_promotion_record(repo, merge), before)
    return promotion_record_diff_problems(changed, before, after, expected=expected)


def _applied(repo: Path, merge: str) -> dict[str, str | None]:
    apply_promotion_record(repo, repo, plan_promotion_record(repo, merge))
    return {path: _read(repo, path) for path in RECORD_PATHS}


def test_the_jail_passes_exactly_the_plan(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    assert _jail(repo, merge, _applied(repo, merge), list(RECORD_PATHS)) == []


def test_the_jail_refuses_a_forged_stamp(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    after = _applied(repo, merge)
    text = after[REGISTRY_PATH]
    assert text is not None
    forged = text.replace("2026-10-13T15:04:05Z", "2026-10-13T15:04:06Z", 1)
    problems = _jail(repo, merge, {**after, REGISTRY_PATH: forged}, [REGISTRY_PATH])
    assert any("differs from the plan" in problem for problem in problems)


def test_the_jail_refuses_markdown_in_a_stale_placeholder(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    after = _applied(repo, merge)
    text = after[FREEZE_RECORD_PATH]
    assert text is not None
    injected = text.replace("<FILL: promotion tag>", "**retracted**", 1)
    problems = _jail(repo, merge, {**after, FREEZE_RECORD_PATH: injected}, [FREEZE_RECORD_PATH])
    assert any("differs from the plan" in problem for problem in problems)


def test_the_jail_refuses_an_unclosed_marker_swallowing_an_entry(
    promotion: tuple[Path, str],
) -> None:
    repo, merge = promotion
    before = _texts(repo, merge)
    record = before[FREEZE_RECORD_PATH]
    assert record is not None
    unclosed = record.replace("Owes `<FILL: promotion tag>` still.", "Owes <FILL: still.")
    deleted = unclosed.split("\n- **A new entry")[0] + ">\n"
    problems = promotion_record_diff_problems(
        [FREEZE_RECORD_PATH],
        {**before, FREEZE_RECORD_PATH: unclosed},
        {**before, FREEZE_RECORD_PATH: deleted},
    )
    assert problems


def test_the_jail_refuses_a_registry_edit_beyond_stamps(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    after = _applied(repo, merge)
    document = json.loads(after[REGISTRY_PATH] or "{}")
    document["blessings"][0]["actor_id"] = "someone-else"
    problems = _jail(
        repo, merge, {**after, REGISTRY_PATH: dump_registry(document)}, [REGISTRY_PATH]
    )
    assert any("other than pending stamps" in problem for problem in problems)


def test_the_jail_reports_a_registry_that_is_not_json(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    after = {**_applied(repo, merge), REGISTRY_PATH: "{not json"}
    problems = _jail(repo, merge, after, [REGISTRY_PATH])
    assert any("not JSON" in problem or "invalid" in problem for problem in problems)


def test_the_jail_refuses_any_other_path(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    texts = _texts(repo, merge)
    problems = promotion_record_diff_problems(["src/fedcourtsai/cli.py"], texts, texts)
    assert problems and "writes only" in problems[0]


# --- the commands ------------------------------------------------------------


def test_the_commands_plan_apply_and_check(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    monkeypatch.chdir(repo)
    runner = CliRunner()
    planned = runner.invoke(app, ["promotion-record", "--merge", merge, "--check"])
    assert planned.exit_code == 0, planned.output
    assert json.loads(planned.stdout)["promotion_tag"]["name"] == "promotion/2026-10-13"
    assert runner.invoke(app, ["promotion-record", "--check-main", "HEAD"]).exit_code == 1
    applied = runner.invoke(app, ["promotion-record", "--merge", merge, "--apply"])
    assert applied.exit_code == 0, applied.output
    jail = runner.invoke(app, ["assert-promotion-record-diff", "--merge", merge, "--base", merge])
    assert jail.exit_code == 0, jail.output
    census = runner.invoke(
        app, ["digest-census", "--at", merge, "--kind", "predictions", "--digest", "aaaaaaaa"]
    )
    assert census.exit_code == 0 and census.stdout.strip() == "2"
    _write(repo, "data/a b.txt", "x")
    refused = runner.invoke(
        app, ["assert-promotion-record-diff", "--merge", merge, "--base", merge]
    )
    assert refused.exit_code == 1
    assert "data/a b.txt: a promotion record writes only" in refused.output


def test_the_live_registry_has_no_pending_row() -> None:
    """The committed registry carries nothing pending: every registration was stamped."""
    carried = frozenset(process_version.FROZEN_PROCESS_DIGESTS)
    assert carried == process_version.REGISTERED_PROCESS_DIGESTS
    assert process_version.PENDING_REGISTRATIONS == ()
