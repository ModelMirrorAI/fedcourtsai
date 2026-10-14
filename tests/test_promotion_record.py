"""Pending registrations and the promotion record a staging→main merge owes ``main``.

The registry side: a label a PR registers is pending until the merge that
carries it stamps it, and every reader treats a pending row in the safe
direction. The git side runs on a synthetic history — a ``main`` holding the
committed registry, a ``staging`` that registers a new label and appends a
freeze-record entry with placeholders, and the ``--no-ff`` merge between them
at a fixed committer time — so the plan, the apply and the jail are checked
against git rather than a stand-in.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
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
    REGISTRY_PATH,
    Stamp,
    apply_promotion_record,
    digest_census,
    dump_registry,
    plan_promotion_record,
    promotion_record_diff_problems,
)

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = json.loads((ROOT / REGISTRY_PATH).read_text(encoding="utf-8"))
NEW_CLAUDE = "sha256:" + "a" * 64
NEW_LABEL = "proc-v10"
MERGED_AT = datetime(2026, 11, 2, 15, 4, 5, tzinfo=UTC)
PENDING = {"at": None, "merge": None, "source": "merge"}


def _live_fleet(*, claude: str = NEW_CLAUDE) -> list[LiveActor]:
    """The committed blessings as a live fleet, claude-baseline's digest moved."""
    return [
        LiveActor(
            blessing["role"],
            blessing["actor_id"],
            claude if blessing["actor_id"] == "claude-baseline" else blessing["digest"],
        )
        for blessing in COMMITTED["blessings"]
    ]


def _registered() -> dict[str, Any]:
    return register_process(COMMITTED, NEW_LABEL, _live_fleet())


# --- registration ------------------------------------------------------------


def test_registering_a_moved_process_writes_pending_rows_and_carries_the_rest() -> None:
    document = _registered()
    assert document["labels"][-1] == {"label": NEW_LABEL, "since": PENDING}
    by_digest = {b["digest"]: b for b in document["blessings"]}
    assert by_digest[NEW_CLAUDE]["blessed"] == PENDING
    assert by_digest[NEW_CLAUDE]["label"] == NEW_LABEL
    carried = [b for b in document["blessings"] if b["digest"] != NEW_CLAUDE]
    originals = {b["digest"]: b for b in COMMITTED["blessings"]}
    assert all(b == originals[b["digest"]] for b in carried)
    closed = [w for w in document["windows"] if w["closes"] == PENDING]
    assert [(w["predictor_id"], w["label"]) for w in closed] == [("claude-baseline", "proc-v9")]
    # Windows already closed, and the carried predictors' open ones, are untouched.
    assert [w for w in document["windows"] if w not in closed and w["label"] != NEW_LABEL] == [
        w for w in COMMITTED["windows"] if w["digest"] != closed[0]["digest"]
    ]
    opened = [w for w in document["windows"] if w["label"] == NEW_LABEL]
    assert opened == [
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
    # The instant in force stays the last carried label's.
    assert counting_instant(registry) == counting_instant(committed)
    # The pending blessing has no bless moment; the carried ones keep theirs.
    moments = bless_moments(registry)
    assert NEW_CLAUDE not in moments
    assert all(moments[d] == m for d, m in bless_moments(committed).items() if d in moments)
    # The pending window is not a window; the pending close leaves the old one open.
    assert registered_windows(registry) == registered_windows(committed)


def test_a_pending_boundary_is_registered_but_splits_nothing() -> None:
    document = register_boundary(
        COMMITTED, "test-change", predictors=None, reach="all", gradual=False
    )
    registry = load_process_registry(dump_registry(document))
    assert registry.harness_boundaries[-1].pending
    assert harness_boundaries(registry) == harness_boundaries(load_process_registry())


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
        register_process(COMMITTED, label, fleet)


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
    raw["blessings"][0]["blessed"] = dict(PENDING)
    with pytest.raises(ValueError, match="already carried"):
        load_process_registry(json.dumps(raw))


def test_a_pending_close_with_no_label_pending_is_refused() -> None:
    raw = json.loads(json.dumps(COMMITTED))
    raw["windows"][1]["closes"] = dict(PENDING)
    with pytest.raises(ValueError, match="no label pending"):
        load_process_registry(json.dumps(raw))


# --- the synthetic promotion -------------------------------------------------

_ENTRY_BEFORE = "# Freeze record\n\n- **An earlier entry.** Owes `<FILL: promotion tag>` still.\n"
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


@pytest.fixture
def promotion(tmp_path: Path) -> tuple[Path, str]:
    """``main`` with the committed registry, ``staging`` registering proc-v10, merged."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _write(repo, REGISTRY_PATH, dump_registry(COMMITTED))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE)
    _artifact(repo, "predictions", 1, "sha256:" + "c" * 64)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "main", when=datetime(2026, 11, 1, tzinfo=UTC))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE + _ENTRY_ADDED)
    _artifact(repo, "predictions", 2, NEW_CLAUDE)
    _artifact(repo, "predictions", 3, NEW_CLAUDE)
    _artifact(repo, "evaluations", 2, NEW_CLAUDE)
    _git(repo, "add", "-A")
    _git(
        repo, "commit", "-q", "-m", "register proc-v10", when=datetime(2026, 11, 1, 12, tzinfo=UTC)
    )
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    return repo, _git(repo, "rev-parse", "HEAD")


def test_the_plan_names_the_tag_the_fills_and_the_stamps(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    plan = plan_promotion_record(repo, merge)
    assert plan.merged_at == "2026-11-02T15:04:05Z"
    assert (plan.promotion_tag.name, plan.promotion_tag.adopt) == ("promotion/2026-11-02", False)
    filled = {(fill.key, fill.value) for fill in plan.fills}
    assert filled == {
        ("promotion tag", "promotion/2026-11-02"),
        ("merge hash", merge),
        ("merged-at", "2026-11-02T15:04:05Z"),
        # Wrapped across a line, and counting the two predictions, not the evaluation.
        ("census predictions digest=aaaaaaaa", "2"),
    }
    assert [fill.key for fill in plan.free_text] == ["apply run id"]
    # The earlier entry's placeholder was not added by this merge: never filled.
    assert [fill.key for fill in plan.stale_placeholders] == ["promotion tag"]
    assert set(plan.stamps) == {
        Stamp("label", NEW_LABEL),
        Stamp("blessing", NEW_CLAUDE),
        Stamp("window-opens", f"{NEW_LABEL} {NEW_CLAUDE}"),
        Stamp(
            "window-closes",
            next(
                f"{w['label']} {w['digest']}"
                for w in COMMITTED["windows"]
                if w["predictor_id"] == "claude-baseline" and w["closes"] is None
            ),
        ),
    }
    assert plan.stale_pending == []
    assert plan.prereg_tag is not None and plan.prereg_tag.name == f"prereg/{NEW_LABEL}"
    assert NEW_CLAUDE in plan.prereg_tag.message


def test_a_taken_date_takes_the_next_suffix_and_an_existing_tag_is_adopted(
    promotion: tuple[Path, str],
) -> None:
    repo, merge = promotion
    _git(repo, "tag", "-a", "promotion/2026-11-02", "-m", "another", f"{merge}^1")
    assert plan_promotion_record(repo, merge).promotion_tag.name == "promotion/2026-11-02-2"
    _git(repo, "tag", "-a", "promotion/2026-11-02-2", "-m", "this one", merge)
    tag = plan_promotion_record(repo, merge).promotion_tag
    assert (tag.name, tag.adopt) == ("promotion/2026-11-02-2", True)


def test_apply_fills_and_stamps_once_and_loads(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    plan = plan_promotion_record(repo, merge)
    assert sorted(apply_promotion_record(repo, repo, plan)) == sorted(
        [FREEZE_RECORD_PATH, REGISTRY_PATH]
    )
    record = (repo / FREEZE_RECORD_PATH).read_text(encoding="utf-8")
    assert f"`{merge}`" in record and "`2`" in record and "<FILL: apply run id>" in record
    assert record.count("<FILL: promotion tag>") == 1  # the earlier entry's, untouched
    registry = load_process_registry(
        (repo / REGISTRY_PATH).read_text(encoding="utf-8"), current_label=NEW_LABEL
    )
    assert registry.labels[-1].since.at == MERGED_AT
    assert registry.labels[-1].since.merge == merge
    assert bless_moments(registry)[NEW_CLAUDE] == MERGED_AT
    windows = registered_windows(registry)
    assert any(w.digest == NEW_CLAUDE and w.opens == MERGED_AT for w in windows)
    # A re-run on the stamped tree changes nothing.
    assert apply_promotion_record(repo, repo, plan_promotion_record(repo, merge)) == []


def test_apply_carries_onto_a_tip_that_moved_on(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    _write(
        repo,
        FREEZE_RECORD_PATH,
        (repo / FREEZE_RECORD_PATH).read_text(encoding="utf-8") + "\n- **A later entry.**\n",
    )
    apply_promotion_record(repo, repo, plan_promotion_record(repo, merge))
    record = (repo / FREEZE_RECORD_PATH).read_text(encoding="utf-8")
    assert "A later entry." in record and f"`{merge}`" in record


def test_a_registration_the_parent_already_held_is_stale_not_stamped(
    promotion: tuple[Path, str],
) -> None:
    repo, _ = promotion
    _git(repo, "switch", "-q", "-c", "late")
    _write(repo, "data/note.txt", "x")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "late")
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "late", "-m", "second promotion", when=MERGED_AT)
    plan = plan_promotion_record(repo, _git(repo, "rev-parse", "HEAD"))
    assert plan.stamps == [] and plan.fills == []
    assert Stamp("label", NEW_LABEL) in plan.stale_pending


def test_a_commit_that_is_not_a_merge_is_refused(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    with pytest.raises(RuntimeError, match="two-parent"):
        plan_promotion_record(repo, f"{merge}^1")


def test_the_census_reads_stamps_on_the_merge_tree(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    assert digest_census(repo, merge, "predictions", ["aaaaaaaa"]) == 2
    assert digest_census(repo, merge, "evaluations", ["sha256:aaaaaaaa"]) == 1
    assert digest_census(repo, merge, "predictions", ["aaaaaaaa", "cccccccc"]) == 3
    assert digest_census(repo, f"{merge}^1", "predictions", ["aaaaaaaa"]) == 0


# --- the jail ----------------------------------------------------------------


def _texts(repo: Path, rev: str) -> dict[str, str | None]:
    return {
        path: subprocess.run(
            ["git", "-C", str(repo), "show", f"{rev}:{path}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        for path in (REGISTRY_PATH, FREEZE_RECORD_PATH)
    }


def _after(repo: Path) -> dict[str, str | None]:
    return {
        path: (repo / path).read_text(encoding="utf-8")
        for path in (REGISTRY_PATH, FREEZE_RECORD_PATH)
    }


def test_the_jail_passes_exactly_fills_and_stamps(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    apply_promotion_record(repo, repo, plan_promotion_record(repo, merge))
    changed = [FREEZE_RECORD_PATH, REGISTRY_PATH]
    assert promotion_record_diff_problems(changed, _texts(repo, merge), _after(repo)) == []


@pytest.mark.parametrize(
    ("edit", "match"),
    [
        (lambda t: t.replace("A new entry", "A rewritten entry"), "freeze-record"),
        (lambda t: t.replace("<FILL: apply run id>", "one\ntwo"), "freeze-record"),
    ],
)
def test_the_jail_refuses_a_freeze_record_edit_beyond_placeholders(
    promotion: tuple[Path, str], edit: Any, match: str
) -> None:
    repo, merge = promotion
    after = _after(repo)
    after[FREEZE_RECORD_PATH] = edit(after[FREEZE_RECORD_PATH])
    problems = promotion_record_diff_problems([FREEZE_RECORD_PATH], _texts(repo, merge), after)
    assert problems and match in problems[0]


def test_the_jail_refuses_a_registry_edit_beyond_stamps(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    apply_promotion_record(repo, repo, plan_promotion_record(repo, merge))
    document = json.loads((repo / REGISTRY_PATH).read_text(encoding="utf-8"))
    document["blessings"][0]["actor_id"] = "someone-else"
    after = _after(repo)
    after[REGISTRY_PATH] = dump_registry(document)
    problems = promotion_record_diff_problems([REGISTRY_PATH], _texts(repo, merge), after)
    assert any("other than pending stamps" in problem for problem in problems)


def test_the_jail_refuses_any_other_path(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    problems = promotion_record_diff_problems(
        ["src/fedcourtsai/cli.py"], _texts(repo, merge), _texts(repo, merge)
    )
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
    assert json.loads(planned.stdout)["promotion_tag"]["name"] == "promotion/2026-11-02"
    applied = runner.invoke(app, ["promotion-record", "--merge", merge, "--apply"])
    assert applied.exit_code == 0, applied.output
    jail = runner.invoke(app, ["assert-promotion-record-diff", "--base", merge])
    assert jail.exit_code == 0, jail.output
    census = runner.invoke(
        app, ["digest-census", "--at", merge, "--kind", "predictions", "--digest", "aaaaaaaa"]
    )
    assert census.exit_code == 0 and census.stdout.strip() == "2"
    _write(repo, "data/stray.txt", "x")
    refused = runner.invoke(app, ["assert-promotion-record-diff", "--base", merge])
    assert refused.exit_code == 1


def test_the_live_registry_has_no_pending_row() -> None:
    """The committed registry carries nothing pending: every registration was stamped."""
    carried = frozenset(process_version.FROZEN_PROCESS_DIGESTS)
    assert carried == process_version.REGISTERED_PROCESS_DIGESTS
