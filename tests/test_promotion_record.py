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
    DECLARATION_HEADING,
    FREEZE_RECORD_PATH,
    RECORD_PATHS,
    REGISTRY_PATH,
    PromotionRecordError,
    Stamp,
    _declared,
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
PENDING = {"at": None, "merge": None, "source": "merge"}
#: The fixture ``main``'s last counting instant. The committed registry is
#: shifted so its newest label lands here, and every fixture commit and merge
#: time is an offset from it: the fixtures stay consistent with each other and
#: in the past, however many labels the real registry gains or when they merge.
ANCHOR = datetime(2026, 10, 11, 12, tzinfo=UTC)


def _iso(at: datetime) -> str:
    return at.strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_pending(node: Any, at: str) -> Any:
    """``node`` with every pending instant stamped ``at``, as a carrying merge would."""
    if isinstance(node, dict):
        if node == PENDING:
            return {"at": at, "merge": "f" * 40, "source": "merge"}
        return {key: _stamp_pending(value, at) for key, value in node.items()}
    if isinstance(node, list):
        return [_stamp_pending(value, at) for value in node]
    return node


def _shifted(node: Any, delta: timedelta) -> Any:
    """``node`` with every registered instant moved by ``delta``."""
    if isinstance(node, dict):
        return {
            key: _iso(datetime.fromisoformat(value) + delta)
            if key in ("at", "revoked_at") and isinstance(value, str)
            else _shifted(value, delta)
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [_shifted(value, delta) for value in node]
    return node


def _label_instants(document: dict[str, Any]) -> list[datetime]:
    return [
        datetime.fromisoformat(entry["since"]["at"])
        for entry in document["labels"]
        if entry["since"]["at"] is not None
    ]


def _fixture_main(live: dict[str, Any]) -> dict[str, Any]:
    """The committed registry as a ``main`` that holds it fully stamped, at ``ANCHOR``.

    A pending boundary is left out, since these fixtures build their own
    pending rows on top and a carried one would be a second batch's. A pending
    label cannot be left out (its registration replaced the blessings it
    moved), so it is stamped an hour after the last carried label's instant,
    as the merge that carries it would. Then every instant moves together so
    the newest label's lands on ``ANCHOR``.
    """
    stamped = _stamp_pending(
        {
            **live,
            "harness_boundaries": [b for b in live["harness_boundaries"] if b["merge"] is not None],
        },
        _iso(max(_label_instants(live)) + timedelta(hours=1)),
    )
    shifted: dict[str, Any] = _shifted(stamped, ANCHOR - max(_label_instants(stamped)))
    return shifted


_LIVE = json.loads((ROOT / REGISTRY_PATH).read_text(encoding="utf-8"))
COMMITTED = _fixture_main(_LIVE)
#: The last label the fixture ``main`` holds.
LAST_LABEL = str(COMMITTED["labels"][-1]["label"])


def _at(hours: float) -> datetime:
    return ANCHOR + timedelta(hours=hours)


def _next_label(steps: int = 1) -> str:
    return f"proc-v{int(LAST_LABEL.removeprefix('proc-v')) + steps}"


#: The committed registry once the merge-stamping rule is declared.
DECLARED_ON = "2026-10-12"
DECLARED = {**COMMITTED, "merge_stamping_declared": DECLARED_ON}
#: The committed registry with the declaration removed: a ``main`` from before it.
UNDECLARED = {key: value for key, value in COMMITTED.items() if key != "merge_stamping_declared"}
NEW_CLAUDE = "sha256:" + "a" * 64
NEW_JUDGE = "sha256:" + "d" * 64
NEW_LABEL = _next_label()
MERGED_AT = _at(51) + timedelta(minutes=4, seconds=5)
MERGED_DAY = MERGED_AT.strftime("%Y-%m-%d")


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
    (claude_window,) = [
        w
        for w in COMMITTED["windows"]
        if w["predictor_id"] == "claude-baseline" and not w["closes"]
    ]
    assert [(w["predictor_id"], w["label"]) for w in closed] == [
        ("claude-baseline", claude_window["label"])
    ]
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
    assert counting_instant(registry) == counting_instant(
        load_process_registry(dump_registry(COMMITTED))
    )


def test_a_pending_registration_loads_under_its_own_label_only() -> None:
    text = dump_registry(_registered())
    registry = load_process_registry(text, current_label=NEW_LABEL)
    assert registry.labels[-1].since.pending
    with pytest.raises(ValueError, match="may be pending"):
        load_process_registry(text)


def test_pending_rows_read_in_the_safe_direction() -> None:
    """Nothing pending counts, opens, closes or splits until its merge stamps it."""
    registry = load_process_registry(dump_registry(_registered()), current_label=NEW_LABEL)
    committed = load_process_registry(dump_registry(COMMITTED))
    assert counting_instant(registry) == counting_instant(committed)
    moments = bless_moments(registry)
    assert NEW_CLAUDE not in moments
    assert all(moments[d] == m for d, m in bless_moments(committed).items() if d in moments)
    assert registered_windows(registry) == registered_windows(committed)


def test_a_pending_boundary_is_registered_but_splits_nothing() -> None:
    document = register_boundary(
        DECLARED, "test-change", predictors=None, reach="all", gradual=False
    )
    registry = load_process_registry(dump_registry(document))
    assert registry.harness_boundaries[-1].pending
    assert harness_boundaries(registry) == harness_boundaries(
        load_process_registry(dump_registry(COMMITTED))
    )


def test_a_pending_boundary_does_not_block_a_label() -> None:
    document = register_boundary(
        DECLARED, "test-change", predictors=None, reach="all", gradual=False
    )
    registered = register_process(document, NEW_LABEL, _live_fleet())
    assert registered["labels"][-1]["label"] == NEW_LABEL


def test_no_label_is_registered_before_the_rule_is_declared() -> None:
    with pytest.raises(RegistrationError, match="merge_stamping_declared"):
        register_process(UNDECLARED, NEW_LABEL, _live_fleet())


def test_no_boundary_is_registered_before_the_rule_is_declared() -> None:
    with pytest.raises(RegistrationError, match="merge_stamping_declared"):
        register_boundary(UNDECLARED, "early", predictors=None, reach="all", gradual=False)


@pytest.mark.parametrize(
    ("label", "fleet", "match"),
    [
        (LAST_LABEL, _live_fleet(), "already registered"),
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
        register_process(_registered(), _next_label(2), _live_fleet(claude="sha256:" + "b" * 64))


def test_a_reused_boundary_name_is_refused() -> None:
    name = COMMITTED["harness_boundaries"][0]["name"]
    with pytest.raises(RegistrationError, match="already registered"):
        register_boundary(DECLARED, name, predictors=None, reach="all", gradual=False)


def test_the_label_line_is_set_once() -> None:
    source = 'X = 1\nCURRENT_PROCESS_LABEL = "proc-v9"\n'
    assert set_current_label(source, NEW_LABEL) == f'X = 1\nCURRENT_PROCESS_LABEL = "{NEW_LABEL}"\n'
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
    live = process_version.frozen_process_record().model_dump(mode="json")
    # The live board names exactly the rows the committed registry holds pending.
    assert live.get("pending", []) == list(process_version.PENDING_REGISTRATIONS)
    assert "pending" not in FrozenProcessRecord(digests=[], since=None).model_dump(mode="json")
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


def test_an_evaluator_digest_leaving_with_nothing_new_registers_a_holding_label() -> None:
    """Retiring a judge moves the fleet with no new digest: a label that holds the instant."""
    judge = next(b for b in COMMITTED["blessings"] if b["role"] == "evaluator")
    fleet = [
        actor for actor in _live_fleet(claude=_carried_claude()) if actor.digest != judge["digest"]
    ]
    document = register_process(DECLARED, NEW_LABEL, fleet)
    assert judge["digest"] not in {b["digest"] for b in document["blessings"]}
    assert document["labels"][-1]["since"] == COMMITTED["labels"][-1]["since"]
    assert document["windows"] == COMMITTED["windows"]
    load_process_registry(dump_registry(document), current_label=NEW_LABEL)


# --- the synthetic promotion -------------------------------------------------

#: The declaring entry the merge-stamping rule needs on the merge's first parent.
_DECLARATION = f"- **{DECLARATION_HEADING}, {DECLARED_ON}.** The rule.\n"
_ENTRY_BEFORE = (
    "# Freeze record\n\n"
    + _DECLARATION
    + "\n- **An earlier entry.** Owes `<FILL: promotion tag>` still.\n"
    + "  Its census, `<FILL: merge hash>`, was landed before.\n"
)
_ENTRY_ADDED = (
    "\n- **A new entry, 2026-10-12.** Carried to `main` by `<FILL: promotion tag>` (merge\n"
    "  commit `<FILL: merge hash>`, merged `<FILL: merged-at>`). Predictions under the new\n"
    "  digest at the merge: `<FILL:census predictions\n  digest=aaaaaaaa>`. Applied by run\n"
    "  `<FILL: apply run id>`.\n"
)
REFS = {"main_ref": "main", "staging_ref": "staging"}


def _git(repo: Path, *args: str, when: datetime | None = None, stdin: str | None = None) -> str:
    env = dict(os.environ)
    if when is not None:
        stamp = when.strftime("%Y-%m-%dT%H:%M:%SZ")
        env["GIT_COMMITTER_DATE"] = stamp
        env["GIT_AUTHOR_DATE"] = stamp
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=True,
        text=True,
        env=env,
        input=stdin,
    ).stdout.strip()


def _write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(text.encode("utf-8"))


def _read(repo: Path, path: str) -> str:
    return (repo / path).read_bytes().decode("utf-8")


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


def _init(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    return repo


def _promote(
    tmp_path: Path,
    *,
    before: str = _ENTRY_BEFORE,
    staging_record: str | None = None,
    main_registry: dict[str, Any] = DECLARED,
    staging_registry: dict[str, Any] | None = None,
) -> tuple[Path, str]:
    """``main`` at ``before``; ``staging`` registering (by default) ``NEW_LABEL``; the merge."""
    repo = _init(tmp_path)
    _write(repo, REGISTRY_PATH, dump_registry(main_registry))
    _write(repo, FREEZE_RECORD_PATH, before)
    _artifact(repo, "predictions", 1, "sha256:" + "c" * 64)
    _commit(repo, "main", _at(12))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(staging_registry or _registered()))
    _write(
        repo,
        FREEZE_RECORD_PATH,
        staging_record if staging_record is not None else before + _ENTRY_ADDED,
    )
    _artifact(repo, "predictions", 2, NEW_CLAUDE)
    _artifact(repo, "predictions", 3, NEW_CLAUDE)
    _artifact(repo, "evaluations", 2, NEW_CLAUDE)
    _commit(repo, f"register {NEW_LABEL}", _at(24))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    return repo, _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def promotion(tmp_path: Path) -> tuple[Path, str]:
    return _promote(tmp_path)


def _plan(repo: Path, merge: str) -> Any:
    return plan_promotion_record(repo, merge, **REFS)


def _old_claude_window() -> str:
    return next(
        f"{w['label']} {w['digest']}"
        for w in COMMITTED["windows"]
        if w["predictor_id"] == "claude-baseline" and w["closes"] is None
    )


def test_the_first_promotion_carrying_the_record_mints_no_prereg_tag(tmp_path: Path) -> None:
    """``main`` before the record holds no registry file; its labels were frozen
    by hand and their prereg/ tags made then. The promotion that carries the
    record in adds no label, so it mints no tag and refuses none."""
    repo = _init(tmp_path)
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE)
    _commit(repo, "main", _at(12))
    for entry in COMMITTED["labels"]:
        _git(repo, "tag", "-a", f"prereg/{entry['label']}", "-m", "hand freeze", "main")
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(COMMITTED))
    _commit(repo, "the record", _at(24))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    plan = _plan(repo, _git(repo, "rev-parse", "HEAD"))
    assert plan.prereg_tag is None
    assert plan.stamps == []


def test_the_plan_names_the_tag_the_fills_and_the_stamps(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    plan = _plan(repo, merge)
    assert plan.merged_at == _iso(MERGED_AT)
    assert (plan.promotion_tag.name, plan.promotion_tag.adopt) == (f"promotion/{MERGED_DAY}", False)
    assert {(fill.key, fill.value) for fill in plan.fills} == {
        ("promotion tag", f"promotion/{MERGED_DAY}"),
        ("merge hash", merge),
        ("merged-at", _iso(MERGED_AT)),
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


@pytest.mark.parametrize(
    ("before", "after"),
    [
        # A landed entry moved below another.
        (
            "# R\n\n- **A (2026-09-01).** Merge `<FILL: merge hash>`.\n\n- **B.** Prose.\n",
            "# R\n\n- **B.** Prose.\n\n- **A (2026-09-01).** Merge `<FILL: merge hash>`.\n",
        ),
        # The same move, past a longer entry.
        (
            "# R\n\n- **A.** Merge `<FILL: merge hash>`.\n\n- **B.** l1\n  l2\n  l3\n  l4\n",
            "# R\n\n- **B.** l1\n  l2\n  l3\n  l4\n\n- **A.** Merge `<FILL: merge hash>`.\n",
        ),
    ],
    ids=["moved", "moved-far"],
)
def test_a_moved_landed_placeholder_is_stale(tmp_path: Path, before: str, after: str) -> None:
    repo, merge = _promote(tmp_path, before=before, staging_record=after, staging_registry=DECLARED)
    plan = _plan(repo, merge)
    assert plan.fills == [] and len(plan.stale_placeholders) == 1


_LANDED = (
    "# Freeze record\n\n- **Landed entry (2026-09-01).** Text.\n"
    "  Merge `<FILL: merge hash>` owed by an earlier merge.\n"
)


@pytest.mark.parametrize(
    "after",
    [
        # A typo fixed on a landed line.
        _LANDED.replace("owed by", "owed bye"),
        # A placeholder renamed in place.
        _LANDED.replace("merge hash", "merge sha"),
        # H8: the placeholder line joined onto its heading.
        _LANDED.replace("Text.\n  Merge", "Text. Merge"),
        # H3: the heading's date edited and the placeholder line reworded.
        _LANDED.replace("2026-09-01", "2026-09-02").replace(
            "Merge `<FILL: merge hash>` owed by an earlier merge.",
            "Carried as `<FILL: merge hash>`.",
        ),
        # H4: a heading inserted and the placeholder line reworded under it.
        _LANDED.replace(
            "  Merge `<FILL: merge hash>` owed by an earlier merge.",
            "- **Brand new.**\n  Carried as `<FILL: merge hash>`.",
        ),
        # The placeholder deleted.
        _LANDED.replace("Merge `<FILL: merge hash>` owed", "Merge owed"),
    ],
    ids=["typo", "rename", "H8-join", "H3-reword", "H4-heading-reword", "deleted"],
)
def test_a_rewritten_landed_placeholder_refuses_the_plan(tmp_path: Path, after: str) -> None:
    """A landed placeholder survives verbatim or filled, on its own line; else the plan refuses."""
    before = _LANDED.replace("# Freeze record\n\n", "# Freeze record\n\n" + _DECLARATION + "\n")
    after = after.replace("# Freeze record\n\n", "# Freeze record\n\n" + _DECLARATION + "\n")
    repo, merge = _promote(tmp_path, before=before, staging_record=after)
    with pytest.raises(PromotionRecordError, match="rewrites landed placeholders"):
        _plan(repo, merge)


_WRAPPED = (
    "# Freeze record\n\n- **Landed entry (2026-09-01).** Text.\n"
    "  The replay census is `<FILL: replay census line from the check\n"
    "  below>`, and the forward census is `<FILL: forward census line from the\n"
    "  check below>`, both read from the blob whose freshness\n"
    "  line is `<FILL: corpus-info freshness line>`.\n"
)


@pytest.mark.parametrize(
    "after",
    [
        # Every wrapped placeholder filled: their line breaks go with them.
        "# Freeze record\n\n- **Landed entry (2026-09-01).** Text.\n"
        + "  The replay census is `695 priors`, and the forward census is `727 priors`,"
        + " both read from the blob whose freshness\n"
        + "  line is `latest pull 2026-10-16`.\n",
        # Only the first filled: the second still wraps.
        "# Freeze record\n\n- **Landed entry (2026-09-01).** Text.\n"
        + "  The replay census is `695 priors`, and the forward census is"
        + " `<FILL: forward census line from the\n"
        + "  check below>`, both read from the blob whose freshness\n"
        + "  line is `<FILL: corpus-info freshness line>`.\n",
        # Left verbatim.
        _WRAPPED,
    ],
    ids=["all-filled", "first-filled", "verbatim"],
)
def test_a_wrapped_landed_placeholder_may_be_filled(tmp_path: Path, after: str) -> None:
    """A placeholder wrapped across a line break, filled by hand, is not a rewrite."""
    before = _WRAPPED.replace("# Freeze record\n\n", "# Freeze record\n\n" + _DECLARATION + "\n")
    after = after.replace("# Freeze record\n\n", "# Freeze record\n\n" + _DECLARATION + "\n")
    repo, merge = _promote(tmp_path, before=before, staging_record=after)
    _plan(repo, merge)


def test_a_wrapped_landed_placeholder_reworded_still_refuses(tmp_path: Path) -> None:
    """Joining a wrapped unit does not loosen the check on the prose around it."""
    after = (
        "# Freeze record\n\n- **Landed entry (2026-09-01).** Text.\n"
        "  The replay census reads `695 priors`, and the forward census is `727 priors`,"
        " both read from the blob whose freshness\n"
        "  line is `latest pull 2026-10-16`.\n"
    )
    before = _WRAPPED.replace("# Freeze record\n\n", "# Freeze record\n\n" + _DECLARATION + "\n")
    after = after.replace("# Freeze record\n\n", "# Freeze record\n\n" + _DECLARATION + "\n")
    repo, merge = _promote(tmp_path, before=before, staging_record=after)
    with pytest.raises(PromotionRecordError, match="rewrites landed placeholders"):
        _plan(repo, merge)


def test_a_new_entry_copying_a_filled_entrys_lines_is_still_added(tmp_path: Path) -> None:
    """The batch fills an old entry and appends a new one built from the same template."""
    template = "  Carried by `<FILL: promotion tag>` (merge `<FILL: merge hash>`).\n"
    middle = "\n- **Middle, 2026-10-05.** Prose.\n  More prose.\n  And more.\n"
    before = "# R\n\n- **Old, 2026-10-01.** Applied.\n" + template + middle
    after = (
        "# R\n\n- **Old, 2026-10-01.** Applied.\n  Carried by `promotion/x` (merge `abc`).\n"
        + middle
        + "\n- **New, 2026-10-12.** Applied.\n"
        + template
    )
    repo, merge = _promote(tmp_path, before=before, staging_record=after, staging_registry=DECLARED)
    plan = _plan(repo, merge)
    assert sorted(fill.key for fill in plan.fills) == ["merge hash", "promotion tag"]
    assert plan.stale_placeholders == []


@pytest.mark.parametrize("inserted", ["# note\n", "- **x**\n", "#\n"])
def test_a_heading_inserted_above_a_landed_placeholder_does_not_add_it(
    tmp_path: Path, inserted: str
) -> None:
    """Inserting a heading line above a landed placeholder never makes the placeholder new."""
    landed = (
        "# Freeze record\n\n" + _DECLARATION + "\n- **Landed entry (2026-09-01).** Text.\n"
        "  Merge `<FILL: merge hash>` owed by an earlier merge.\n"
    )
    edited = landed.replace("  Merge `<FILL", inserted + "  Merge `<FILL")
    repo, merge = _promote(tmp_path, before=landed, staging_record=edited)
    plan = _plan(repo, merge)
    assert [fill.key for fill in plan.fills] == []
    assert [fill.key for fill in plan.stale_placeholders] == ["merge hash"]


def test_a_heading_edit_does_not_add_the_entrys_placeholder(tmp_path: Path) -> None:
    landed = (
        "# Freeze record\n\n" + _DECLARATION + "\n- **Landed entry (2026-09-01).** Text.\n"
        "  Merge `<FILL: merge hash>` owed by an earlier merge.\n"
    )
    edited = landed.replace("Landed entry", "Landed  entry")
    repo, merge = _promote(tmp_path, before=landed, staging_record=edited)
    assert _plan(repo, merge).fills == []


def test_an_evaluator_only_label_is_tagged_on_its_merge(tmp_path: Path) -> None:
    judge_only = register_process(
        DECLARED, NEW_LABEL, _live_fleet(claude=_carried_claude(), judge=NEW_JUDGE)
    )
    repo, merge = _promote(tmp_path, staging_record=_ENTRY_BEFORE, staging_registry=judge_only)
    plan = _plan(repo, merge)
    assert plan.stamps == [Stamp("blessing", NEW_JUDGE)]
    assert plan.prereg_tag is not None and "holds the counting instant" in plan.prereg_tag.message


def test_stamps_need_the_declaration_on_the_first_parent(tmp_path: Path) -> None:
    repo, merge = _promote(tmp_path, main_registry=UNDECLARED)
    with pytest.raises(PromotionRecordError, match="declares no merge-stamped"):
        _plan(repo, merge)
    repo2, merge2 = _promote(tmp_path / "b", before="# Freeze record\n")
    with pytest.raises(PromotionRecordError, match="no entry headed"):
        _plan(repo2, merge2)


def test_only_a_promotion_merge_is_planned(tmp_path: Path) -> None:
    """A merge into staging, and a data branch merged into main, are not promotions."""
    repo = _init(tmp_path)
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE)
    _commit(repo, "main", _at(12))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, "x", "1")
    _commit(repo, "s", _at(13))
    _git(repo, "switch", "-q", "-c", "feature")
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _commit(repo, "reg", _at(14))
    _git(repo, "switch", "-q", "staging")
    _git(
        repo,
        "merge",
        "-q",
        "--no-ff",
        "feature",
        "-m",
        "f",
        when=_at(15),
    )
    with pytest.raises(PromotionRecordError, match="first-parent chain"):
        _plan(repo, _git(repo, "rev-parse", "HEAD"))
    _git(repo, "switch", "-q", "main")
    _git(repo, "switch", "-q", "-c", "data")
    _write(repo, "data/cases/note.txt", "x")
    _commit(repo, "data", _at(16))
    _git(repo, "switch", "-q", "main")
    _git(
        repo,
        "merge",
        "-q",
        "--no-ff",
        "data",
        "-m",
        "d",
        when=_at(17),
    )
    with pytest.raises(PromotionRecordError, match="not a promotion merge"):
        _plan(repo, _git(repo, "rev-parse", "HEAD"))


def test_a_taken_date_takes_the_next_suffix_and_an_existing_tag_is_adopted(
    promotion: tuple[Path, str],
) -> None:
    repo, merge = promotion
    _git(repo, "tag", "-a", f"promotion/{MERGED_DAY}", "-m", "another", f"{merge}^1")
    assert _plan(repo, merge).promotion_tag.name == f"promotion/{MERGED_DAY}-2"
    _git(repo, "tag", "-a", f"promotion/{MERGED_DAY}-2", "-m", "this one", merge)
    tag = _plan(repo, merge).promotion_tag
    assert (tag.name, tag.adopt) == (f"promotion/{MERGED_DAY}-2", True)


def test_a_tag_of_a_tag_is_not_adopted(tmp_path: Path) -> None:
    """b1d: a tag that only peels to the merge through another tag object is refused."""
    repo, merge = _promote(tmp_path)
    _git(repo, "tag", "-a", "inner", "-m", "inner", merge)
    _git(repo, "tag", "-a", f"promotion/{MERGED_DAY}", "-m", "outer", "inner")
    with pytest.raises(PromotionRecordError, match="does not tag the merge commit directly"):
        _plan(repo, merge)


def test_a_stray_or_lightweight_tag_on_the_merge_is_refused(tmp_path: Path) -> None:
    repo, merge = _promote(tmp_path)
    _git(repo, "tag", "promotion/0-attacker)](x.example)", merge)
    with pytest.raises(PromotionRecordError, match="not its canonical"):
        _plan(repo, merge)
    repo2, merge2 = _promote(tmp_path / "b")
    _git(repo2, "tag", f"promotion/{MERGED_DAY}", merge2)
    with pytest.raises(PromotionRecordError, match="lightweight"):
        _plan(repo2, merge2)
    repo3, merge3 = _promote(tmp_path / "c")
    _git(repo3, "tag", f"prereg/{NEW_LABEL}", merge3)
    with pytest.raises(PromotionRecordError, match="lightweight"):
        _plan(repo3, merge3)


def test_a_train_candidate_merged_after_staging_moved_on_is_a_promotion(tmp_path: Path) -> None:
    """The promotion train merges a frozen `promote/<date>` branch cut at a staging
    tip, often after staging has taken more merges. The cut stays on staging's
    first-parent chain, so the record plans the merge as for a staging head."""
    repo = _init(tmp_path)
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE)
    _artifact(repo, "predictions", 1, "sha256:" + "c" * 64)
    _commit(repo, "main", _at(12))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE + _ENTRY_ADDED)
    _artifact(repo, "predictions", 2, NEW_CLAUDE)
    _artifact(repo, "predictions", 3, NEW_CLAUDE)
    _artifact(repo, "evaluations", 2, NEW_CLAUDE)
    cut = _commit(repo, f"register {NEW_LABEL}", _at(24))
    _git(repo, "branch", "promote/2026-10-12", cut)
    # Staging moves on: a feature merged after the cut, which the candidate
    # does not carry.
    _git(repo, "switch", "-q", "-c", "feature")
    _write(repo, "later.txt", "x")
    _commit(repo, "later feature", _at(25))
    _git(repo, "switch", "-q", "staging")
    _git(
        repo,
        "merge",
        "-q",
        "--no-ff",
        "feature",
        "-m",
        "feature PR",
        when=_at(26),
    )
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "promote/2026-10-12", "-m", "promote", when=MERGED_AT)
    merge = _git(repo, "rev-parse", "HEAD")
    plan = _plan(repo, merge)
    assert plan.promotion_tag.name.startswith("promotion/")
    assert not (repo / "later.txt").exists()
    # A branch at a commit that reached staging only as a merge's second parent
    # was never a staging tip, so a candidate there is refused.
    _git(repo, "switch", "-q", "-c", "fake", f"{merge}^1")
    _git(
        repo,
        "merge",
        "-q",
        "--no-ff",
        _git(repo, "rev-parse", "feature"),
        "-m",
        "promote side",
        when=MERGED_AT + timedelta(minutes=5),
    )
    with pytest.raises(PromotionRecordError, match="first-parent chain"):
        plan_promotion_record(
            repo, _git(repo, "rev-parse", "HEAD"), main_ref="fake", staging_ref="staging"
        )


def test_a_data_merge_stays_refused_after_a_sync(tmp_path: Path) -> None:
    """A sync makes a data head reachable from staging, but not on its first-parent chain."""
    repo, _ = _promote(tmp_path)
    _git(repo, "switch", "-q", "-c", "data", "main")
    _write(repo, "data/x.json", "{}\n")
    _commit(repo, "data", MERGED_AT + timedelta(minutes=1))
    _git(repo, "switch", "-q", "main")
    _git(
        repo,
        "merge",
        "-q",
        "--no-ff",
        "data",
        "-m",
        "data PR",
        when=MERGED_AT + timedelta(minutes=2),
    )
    data_merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "-q", "staging")
    _git(
        repo, "merge", "-q", "--no-ff", "main", "-m", "sync", when=MERGED_AT + timedelta(minutes=3)
    )
    _git(repo, "switch", "-q", "main")
    with pytest.raises(PromotionRecordError, match="first-parent chain"):
        _plan(repo, data_merge)


def test_the_census_refuses_a_path_with_a_newline(tmp_path: Path) -> None:
    repo, _ = _promote(tmp_path)
    path = (
        "data/cases/scotus/2/events/evt-x/predictions/claude-baseline/20261101T000000Z/"
        "prediction.json"
    )
    _git(repo, "switch", "-q", "staging")
    _write(repo, path + "\nHEAD:" + path, "{}\n")
    _commit(repo, "weird", _at(25))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "p2", when=MERGED_AT + timedelta(hours=1))
    with pytest.raises(PromotionRecordError, match="newline"):
        digest_census(repo, _git(repo, "rev-parse", "HEAD"), "predictions", ["aaaaaaaa"])


def test_apply_fills_and_stamps_once_and_loads(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    plan = _plan(repo, merge)
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
    assert apply_promotion_record(repo, repo, _plan(repo, merge)) == []


def test_apply_writes_nothing_when_the_registry_is_refused(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    before = {path: _read(repo, path) for path in RECORD_PATHS}

    def refuse(_text: str) -> None:
        raise ValueError("refused")

    with pytest.raises(PromotionRecordError, match="refused"):
        apply_promotion_record(repo, repo, _plan(repo, merge), check_registry=refuse)
    assert {path: _read(repo, path) for path in RECORD_PATHS} == before


def test_apply_carries_onto_a_tip_that_moved_on(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    _write(repo, FREEZE_RECORD_PATH, _read(repo, FREEZE_RECORD_PATH) + "\n- **A later entry.**\n")
    apply_promotion_record(repo, repo, _plan(repo, merge))
    record = _read(repo, FREEZE_RECORD_PATH)
    assert "A later entry." in record and f"`{merge}`" in record


def test_a_registration_the_parent_already_held_is_stale_not_stamped(
    promotion: tuple[Path, str],
) -> None:
    repo, _ = promotion
    _git(repo, "switch", "-q", "staging")
    _write(repo, "data/note.txt", "x")
    _commit(repo, "late", MERGED_AT)
    _git(repo, "switch", "-q", "main")
    later = MERGED_AT + timedelta(hours=1)
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "second promotion", when=later)
    second = _git(repo, "rev-parse", "HEAD")
    plan = _plan(repo, second)
    assert plan.stamps == [] and plan.fills == []
    assert Stamp("label", NEW_LABEL) in plan.stale_pending
    before = {path: _read(repo, path) for path in RECORD_PATHS}
    forged = json.loads(before[REGISTRY_PATH])
    forged["labels"][-1]["since"] = {
        "at": _iso(MERGED_AT + timedelta(hours=1)),
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
        _plan(repo, f"{merge}^1")


def test_a_merge_committed_before_a_parent_is_refused(tmp_path: Path) -> None:
    repo = _init(tmp_path)
    _write(repo, "a.txt", "a")
    _commit(repo, "main", MERGED_AT)
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, "b.txt", "b")
    _commit(repo, "side", MERGED_AT + timedelta(hours=1))
    _git(repo, "switch", "-q", "main")
    _git(
        repo, "merge", "-q", "--no-ff", "staging", "-m", "m", when=MERGED_AT + timedelta(minutes=1)
    )
    with pytest.raises(PromotionRecordError, match="before one of its parents"):
        _plan(repo, _git(repo, "rev-parse", "HEAD"))


def test_a_merge_before_a_registered_instant_is_refused(tmp_path: Path) -> None:
    """Stamping with a time before the instants already registered would close a window early."""
    repo = _init(tmp_path)
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, _ENTRY_BEFORE)
    _commit(repo, "main", datetime(2026, 10, 1, tzinfo=UTC))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _commit(repo, "register", datetime(2026, 10, 1, 12, tzinfo=UTC))
    _git(repo, "switch", "-q", "main")
    _git(
        repo, "merge", "-q", "--no-ff", "staging", "-m", "m", when=datetime(2026, 10, 2, tzinfo=UTC)
    )
    with pytest.raises(PromotionRecordError, match="before the registered instant"):
        _plan(repo, _git(repo, "rev-parse", "HEAD"))


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
    apply_promotion_record(repo, repo, _plan(repo, merge))
    _commit(repo, "promotion record", MERGED_AT + timedelta(minutes=1))
    assert pending_carried_problems(repo, "HEAD") == []


def test_a_pending_row_on_main_without_a_carrying_merge_is_named(tmp_path: Path) -> None:
    repo = _init(tmp_path)
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _commit(repo, "main", _at(12))
    _write(repo, REGISTRY_PATH, dump_registry(_registered()))
    _commit(repo, "a direct commit", _at(13))
    problems = pending_carried_problems(repo, "HEAD")
    assert any("no carrying merge found" in problem for problem in problems)


def test_a_carrying_merge_past_the_walk_is_still_named(promotion: tuple[Path, str]) -> None:
    repo, _ = promotion
    for index in range(3):
        _git(repo, "switch", "-q", "-c", f"b{index}")
        _write(repo, f"f{index}", "x")
        _commit(repo, "c", MERGED_AT + timedelta(minutes=index))
        _git(repo, "switch", "-q", "main")
        _git(
            repo,
            "merge",
            "-q",
            "--no-ff",
            f"b{index}",
            "-m",
            "m",
            when=MERGED_AT + timedelta(minutes=index, seconds=30),
        )
    problems = pending_carried_problems(repo, "HEAD", depth=2)
    assert problems and all("within 2" in problem for problem in problems)


# --- the jail ----------------------------------------------------------------


def _texts(repo: Path, rev: str) -> dict[str, str | None]:
    return {
        path: subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", f"{rev}:{path}"],
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8")
        for path in RECORD_PATHS
    }


def _record_commit(repo: Path, merge: str, mutate: Any = None, *, tag: bool = True) -> str:
    """The writer's sequence: tag the merge, apply, (tamper,) commit; returns the record commit.

    The record is committed on a side branch, so ``main`` stays at the merge it
    was planned against — the writer pushes the jailed commit after the jail.
    """
    plan = _plan(repo, merge)
    if tag:
        _tag(repo, plan)
    _git(repo, "switch", "-q", "-c", "record")
    apply_promotion_record(repo, repo, plan)
    if mutate is not None:
        mutate(repo)
    return _commit(repo, "promotion record", MERGED_AT + timedelta(minutes=5))


def _tag(repo: Path, plan: Any) -> None:
    for tag in [plan.promotion_tag] + ([plan.prereg_tag] if plan.prereg_tag else []):
        _git(
            repo,
            "tag",
            "-a",
            "--cleanup=verbatim",
            tag.name,
            "-F",
            "-",
            plan.merge,
            stdin=tag.message,
        )


def _cli_jail(repo: Path, merge: str, head: str, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.chdir(repo)
    return CliRunner().invoke(
        app,
        [
            "assert-promotion-record-diff",
            "--merge",
            merge,
            "--base",
            merge,
            "--head",
            head,
            "--main-ref",
            "main",
            "--staging-ref",
            "staging",
        ],
    )


def test_the_jail_passes_exactly_the_plan(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    result = _cli_jail(repo, merge, _record_commit(repo, merge), monkeypatch)
    assert result.exit_code == 0, result.output


def test_the_jail_needs_the_tags_first(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    result = _cli_jail(repo, merge, _record_commit(repo, merge, tag=False), monkeypatch)
    assert result.exit_code == 1 and "does not yet name" in result.output


def _swap(path: str, old: bytes, new: bytes) -> Any:
    def mutate(repo: Path) -> None:
        target = repo / path
        target.write_bytes(target.read_bytes().replace(old, new))

    return mutate


def _chmod(path: str) -> Any:
    def mutate(repo: Path) -> None:
        os.chmod(repo / path, 0o700)  # the owner execute bit is all git records

    return mutate


def _symlink(path: str) -> Any:
    def mutate(repo: Path) -> None:
        outside = repo.parent / "outside.md"
        outside.write_bytes((repo / path).read_bytes())
        (repo / path).unlink()
        (repo / path).symlink_to(outside)

    return mutate


@pytest.mark.parametrize(
    "mutate",
    [
        _swap(FREEZE_RECORD_PATH, b"\n", b"\r\n"),
        _swap(FREEZE_RECORD_PATH, b"\n", b"\r"),
        _swap(REGISTRY_PATH, b"\n", b"\r\n"),
        _swap(FREEZE_RECORD_PATH, b"# Freeze", "﻿# Freeze".encode()),
        _swap(
            REGISTRY_PATH,
            _iso(MERGED_AT).encode(),
            _iso(MERGED_AT + timedelta(seconds=1)).encode(),
        ),
        _swap(FREEZE_RECORD_PATH, b"<FILL: promotion tag>", b"**retracted**"),
        _chmod(FREEZE_RECORD_PATH),
        _symlink(FREEZE_RECORD_PATH),
    ],
    ids=["crlf", "cr", "crlf-registry", "bom", "forged-time", "stale-injected", "mode", "symlink"],
)
def test_the_jail_refuses_a_tampered_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutate: Any
) -> None:
    repo, merge = _promote(tmp_path)
    result = _cli_jail(repo, merge, _record_commit(repo, merge, mutate), monkeypatch)
    assert result.exit_code == 1, result.output


def _jail_at(repo: Path, merge: str, base: str, head: str, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.chdir(repo)
    args = ["--merge", merge, "--base", base, "--head", head]
    refs = ["--main-ref", "main", "--staging-ref", "staging"]
    return CliRunner().invoke(app, ["assert-promotion-record-diff", *args, *refs])


def test_the_jail_refuses_a_base_that_is_not_main(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    _tag(repo, _plan(repo, merge))
    _git(repo, "switch", "-q", "-c", "side", merge)
    _write(repo, ".github/workflows/evil.yml", "on: push\n")
    base = _commit(repo, "evil", MERGED_AT + timedelta(minutes=1))
    apply_promotion_record(repo, repo, _plan(repo, merge))
    head = _commit(repo, "record", MERGED_AT + timedelta(minutes=5))
    result = _jail_at(repo, merge, base, head, monkeypatch)
    assert result.exit_code == 1 and "is not main's tip" in result.output


@pytest.mark.parametrize("shape", ["extra-parent", "unrelated"])
def test_the_jail_refuses_a_head_that_is_not_one_step_on_base(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch, shape: str
) -> None:
    repo, merge = promotion
    plan = _plan(repo, merge)
    _tag(repo, plan)
    _git(repo, "switch", "-q", "--orphan", "junk")
    _write(repo, "x.txt", "junk\n")
    junk = _commit(repo, "junk", MERGED_AT)
    _git(repo, "switch", "-q", "-f", "-c", "record", merge)
    apply_promotion_record(repo, repo, plan)
    _git(repo, "add", "-A")
    tree = _git(repo, "write-tree")
    parents = ["-p", merge, "-p", junk] if shape == "extra-parent" else ["-p", junk]
    head = _git(repo, "commit-tree", tree, *parents, "-m", "record")
    result = _jail_at(repo, merge, merge, head, monkeypatch)
    assert result.exit_code == 1 and "exactly one parent" in result.output


def test_the_jail_refuses_a_submodule(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    plan = _plan(repo, merge)
    _tag(repo, plan)
    _git(repo, "switch", "-q", "-c", "record")
    apply_promotion_record(repo, repo, plan)
    _git(repo, "add", "-A")
    _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{merge},vendor")
    tree = _git(repo, "write-tree")
    head = _git(repo, "commit-tree", tree, "-p", merge, "-m", "record and a gitlink")
    result = _jail_at(repo, merge, merge, head, monkeypatch)
    assert result.exit_code == 1 and "submodule" in result.output


def test_the_jail_refuses_a_tag_whose_message_is_not_the_plans(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    plan = _plan(repo, merge)
    _git(repo, "tag", "-a", plan.promotion_tag.name, "-m", "another message", merge)
    if plan.prereg_tag is not None:
        _git(
            repo,
            "tag",
            "-a",
            "--cleanup=verbatim",
            plan.prereg_tag.name,
            "-F",
            "-",
            merge,
            stdin=plan.prereg_tag.message,
        )
    _git(repo, "switch", "-q", "-c", "record")
    apply_promotion_record(repo, repo, plan)
    head = _commit(repo, "record", MERGED_AT + timedelta(minutes=5))
    result = _jail_at(repo, merge, merge, head, monkeypatch)
    assert result.exit_code == 1 and "not the annotated tag the plan writes" in result.output


def test_the_jail_refuses_any_other_path_even_with_a_space(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion

    def stray(repo: Path) -> None:
        _write(repo, "data/a b.txt", "x")

    result = _cli_jail(repo, merge, _record_commit(repo, merge, stray), monkeypatch)
    assert result.exit_code == 1
    assert "data/a b.txt: a promotion record writes only" in result.output


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
    before = _texts(repo, merge)
    plan = _plan(repo, merge)
    expected = render_promotion_record(repo, plan, before)
    document = json.loads(expected[REGISTRY_PATH] or "{}")
    document["blessings"][0]["actor_id"] = "someone-else"
    after = {**expected, REGISTRY_PATH: dump_registry(document)}
    problems = promotion_record_diff_problems([REGISTRY_PATH], before, after, expected=expected)
    assert any("other than pending stamps" in problem for problem in problems)


def test_the_jail_reports_a_registry_that_is_not_json(promotion: tuple[Path, str]) -> None:
    repo, merge = promotion
    before = _texts(repo, merge)
    after = {**before, REGISTRY_PATH: "{not json"}
    problems = promotion_record_diff_problems([REGISTRY_PATH], before, after)
    assert any("not JSON" in problem or "invalid" in problem for problem in problems)


# --- the commands ------------------------------------------------------------


def test_the_commands_plan_apply_and_check(
    promotion: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, merge = promotion
    monkeypatch.chdir(repo)
    runner = CliRunner()
    refs = ["--main-ref", "main", "--staging-ref", "staging"]
    planned = runner.invoke(app, ["promotion-record", "--merge", merge, "--check", *refs])
    assert planned.exit_code == 0, planned.output
    assert json.loads(planned.stdout)["promotion_tag"]["name"] == f"promotion/{MERGED_DAY}"
    assert runner.invoke(app, ["promotion-record", "--merge", merge]).exit_code == 2
    assert runner.invoke(app, ["promotion-record", "--check-main", "HEAD"]).exit_code == 1
    applied = runner.invoke(app, ["promotion-record", "--merge", merge, "--apply", *refs])
    assert applied.exit_code == 0, applied.output
    census = runner.invoke(
        app, ["digest-census", "--at", merge, "--kind", "predictions", "--digest", "aaaaaaaa"]
    )
    assert census.exit_code == 0 and census.stdout.strip() == "2"


@pytest.mark.reads_docs
def test_the_committed_declaration_resolves_on_main() -> None:
    """The committed registry names its declaring entry, and the record holds it.

    Once both are on ``main``, a later promotion's first parent satisfies
    :func:`_declared`; the promotion that carries them cannot stamp, since its
    own first parent predates both (``test_stamps_need_the_declaration_on_the_first_parent``).
    """
    record = (ROOT / FREEZE_RECORD_PATH).read_text(encoding="utf-8")
    assert COMMITTED["merge_stamping_declared"]
    assert _declared(COMMITTED, record) is None


def test_the_declaring_promotion_fills_its_entry_and_stamps_nothing(tmp_path: Path) -> None:
    """The real declaring shape: ``main`` holds no registry file, and the batch
    brings the registry with the declaration set and nothing pending.

    The merge's first parent holds no declaration, so no stamp is planned and no
    ``prereg/`` tag is minted; the declaring entry's closed-key placeholders are
    still filled — the promotion tag, the merge, its time and the census.
    """
    repo = _init(tmp_path)
    _write(repo, FREEZE_RECORD_PATH, "# Freeze record\n")
    _artifact(repo, "predictions", 1, NEW_CLAUDE)
    _commit(repo, "main", _at(12))
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(
        repo,
        FREEZE_RECORD_PATH,
        "# Freeze record\n\n"
        + _DECLARATION
        + "  Carried to `main` by `<FILL: promotion tag>` (merge commit\n"
        + "  `<FILL: merge hash>`, merged `<FILL: merged-at>`). Predictions carrying\n"
        + "  the digest: `<FILL: census predictions digest=aaaaaaaa>`.\n",
    )
    _commit(repo, "declare", _at(24))
    _git(repo, "switch", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "staging", "-m", "promote", when=MERGED_AT)
    merge = _git(repo, "rev-parse", "HEAD")

    plan = _plan(repo, merge)

    assert plan.stamps == []
    assert plan.prereg_tag is None
    filled = {fill.key: fill.value for fill in plan.fills}
    assert filled["promotion tag"] == plan.promotion_tag.name
    assert filled["merge hash"] == merge
    assert filled["census predictions digest=aaaaaaaa"] == "1"
    assert plan.free_text == []
