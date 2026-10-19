"""The promotion gate's Step 0: what a batch's process registry may carry to ``main``.

A promotion that moves the process carries **pending** registrations
(:mod:`fedcourtsai.process_registration`): a label, the digests it blesses, the
windows it opens and closes, a harness boundary. The carrying merge stamps them
(:mod:`fedcourtsai.promotion_record`); this module refuses a batch whose
registrations could not be stamped honestly. Each check reads git alone — the
batch's head, ``main``'s ref and the repository's tags — so the required check
on the promotion PR and the maintainer's pre-flight read the same facts:

1. **Main declares merge-stamped instants.** A batch carrying any pending
   registration needs ``main``'s registry and freeze record to declare the
   rule its stamps apply (``merge_stamping_declared`` and the declaring entry):
   the merge refuses to stamp otherwise, and a pending row nothing will stamp
   leaves its cells uncounted.
2. **No pending digest is already in the ledger.** A digest the batch newly
   blesses must not stamp any committed prediction or evaluation on ``main``:
   a cell carrying it ran before the blessing it would count under, which is
   retroactive blessing — the check the cutover's hand-run Step 0 made.
3. **Every enabled actor is registered.** The digest each enabled actor
   computes on the batch's tree must be in the batch's registry, stamped or
   pending; a moved process with no registration would run unblessed from the
   merge on.
4. **One open window per predictor.** At most one of a predictor's windows is
   unrevoked with no close, a pending close counting as a close:
   ``register-process`` closes the predecessor pending, and a hand edit that
   forgot to would count two digests of one predictor at once.
5. **One new label, untagged.** A batch carries at most one label ``main``
   does not hold — the carrying merge mints ``prereg/<label>`` for that one
   label, an evaluator-only label included — and its tag must not exist yet.
6. **No boundary name repeats.** Boundaries are named once.
7. **Nothing pending already sits on ``main``.** A row a merge carried and no
   writer stamped leaves its cells uncounted indefinitely
   (:func:`fedcourtsai.promotion_record.pending_carried_problems`).
8. **What ``main`` stamped stays as it is.** Every label, blessing, window and
   boundary stamped on ``main`` reaches the merge field for field and in
   ``main``'s order (labels, windows and boundaries, whose order a reader
   takes as meaning), ``merge_stamping_declared`` stays as ``main`` set it,
   and each evaluator digest's blessing labels keep ``main``'s as a prefix,
   growing only by a label new to ``main``: a batch fills pending rows and
   appends new ones. An un-stamped row would be stamped again at the next
   merge's instant, and an edited one would move cells across a published
   line. The comparison is three-way, against every merge base, so a field
   the batch left as a base had it passes — the merge keeps ``main``'s stamp
   there whether or not a sync has carried it back; where a criss-cross
   history leaves several bases, the batch must match all of them. Rows new
   to ``main`` follow every row it stamped. Three changes pass:
   ``register-process``'s own two, a pending close on a window no live
   predictor computes and a blessing dropped once its digest left the fleet
   (a predictor's with its window closed); and a revocation, on a window
   already closed, at or after the batch head's commit. A revocation's
   dated freeze-record entry is the maintainer's to read; this check does
   not look for it.

The batch must hold a registry that loads under its own last label, refusing
what :func:`fedcourtsai.process_version.load_process_registry` refuses; where
it does not, that refusal and check 7 are all Step 0 reports, since the other
checks read the document's fields.
"""

from __future__ import annotations

import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import process_version
from .process_registration import LiveActor
from .promotion_record import (
    FREEZE_RECORD_PATH,
    REGISTRY_PATH,
    PromotionRecordError,
    _declared,
    _registry,
    _tags,
    committer_time,
    digest_census,
    git,
    labels_new_to,
    pending_carried_problems,
    pending_registrations,
    show_at,
)
from .registry import enabled_evaluators, enabled_predictors

#: The config files and the root they sit under, as repository paths.
_CONFIG_ROOT = "config"
_CONFIG_FILES = ("predictors.yaml", "evaluators.yaml")
_CENSUS_KIND = {"predictor": "predictions", "evaluator": "evaluations"}


@dataclass(frozen=True)
class RegistryGateResult:
    """What Step 0 found: the batch's pending rows and every refusal."""

    pending: int
    problems: list[str]


def live_actors_at(repo: Path, rev: str) -> list[LiveActor]:
    """Every enabled actor's process digest on ``rev``'s tree, as ``process-digest --all`` reads it.

    Writes ``rev``'s two actor registries and each enabled actor's prompt file
    into a scratch root and digests them there, so the answer is ``rev``'s
    whatever tree the caller has checked out.
    """
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        config_root = root / _CONFIG_ROOT
        for name in _CONFIG_FILES:
            _write_at(repo, rev, f"{_CONFIG_ROOT}/{name}", root)
        rows = [
            ("predictor", p.id, p.prompt)
            for p in enabled_predictors(config_root / _CONFIG_FILES[0])
        ]
        rows += [
            ("evaluator", e.id, e.prompt)
            for e in enabled_evaluators(config_root / _CONFIG_FILES[1])
        ]
        for _role, _actor, prompt in rows:
            _write_at(repo, rev, str(prompt), root)
        return [
            LiveActor(role, actor, process_version.digest_for_actor(root, config_root, role, actor))
            for role, actor, _prompt in rows
        ]


def _write_at(repo: Path, rev: str, path: str, root: Path) -> None:
    text = show_at(repo, rev, path)
    if text is None:
        raise PromotionRecordError(f"{path} is missing at {rev}")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise PromotionRecordError(f"{path} at {rev} resolves outside the scratch root")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def registry_gate(
    repo: Path, at: str, main_ref: str, actors: Sequence[LiveActor]
) -> RegistryGateResult:
    """Step 0 on the batch at ``at``, against ``main_ref``: its pending rows and every refusal."""
    text = show_at(repo, at, REGISTRY_PATH)
    if text is None:
        return RegistryGateResult(pending=0, problems=[f"no {REGISTRY_PATH} at {at}"])
    try:
        registry = _registry(text, at)
        labels = registry.get("labels") or [{}]
        process_version.load_process_registry(
            text,
            current_label=labels[-1].get("label") or process_version.CURRENT_PROCESS_LABEL,
        )
    except (ValueError, PromotionRecordError) as exc:
        # The other checks read the document's fields; on a document the
        # loader refuses they would misread it, so only main's own check runs.
        return RegistryGateResult(
            pending=0,
            problems=[
                f"the registry at {at} does not load: {exc}",
                *pending_carried_problems(repo, main_ref),
            ],
        )
    pending = pending_registrations(registry)
    main_text = show_at(repo, main_ref, REGISTRY_PATH)
    main_registry = _registry(main_text, main_ref)
    problems: list[str] = []
    if pending:
        refusal = _declared(main_registry, show_at(repo, main_ref, FREEZE_RECORD_PATH) or "")
        if refusal is not None:
            problems.append(
                f"the batch carries {len(pending)} pending registration(s), but {refusal}: "
                "no merge would stamp them, so the declaration lands on main first"
            )
    problems += _ledger_problems(repo, registry, main_ref)
    problems += _unregistered_problems(registry, actors)
    problems += _window_problems(registry)
    problems += _label_problems(repo, registry, main_registry if main_text is not None else None)
    problems += _boundary_problems(registry)
    problems += pending_carried_problems(repo, main_ref)
    if main_text is not None:
        bases = git(repo, "merge-base", "--all", main_ref, at).split()
        problems += _Stamped(
            main=main_registry,
            bases=[_registry(show_at(repo, base, REGISTRY_PATH), base) for base in bases],
            batch=registry,
            live=frozenset(actor.digest for actor in actors),
            live_predictors=frozenset(a.digest for a in actors if a.role == "predictor"),
            head_time=committer_time(repo, at),
        ).problems()
    return RegistryGateResult(pending=len(pending), problems=problems)


def _ledger_problems(repo: Path, registry: Mapping[str, Any], main_ref: str) -> list[str]:
    """Each pending digest that already stamps a committed cell on ``main_ref``."""
    problems: list[str] = []
    for blessing in registry.get("blessings", []):
        if blessing["blessed"]["merge"] is not None:
            continue
        kind = _CENSUS_KIND[blessing["role"]]
        found = digest_census(repo, main_ref, kind, [blessing["digest"]])
        if found:
            problems.append(
                f"{blessing['role']} {blessing['actor_id']} digest {blessing['digest']} is pending "
                f"but already stamps {found} committed {kind} on {main_ref}: those cells ran "
                "before the blessing they would count under"
            )
    return problems


def _unregistered_problems(registry: Mapping[str, Any], actors: Sequence[LiveActor]) -> list[str]:
    """Each enabled actor whose live digest the registry neither blesses nor holds pending."""
    registered = {blessing["digest"] for blessing in registry.get("blessings", [])}
    return [
        f"{actor.role} {actor.actor_id} computes {actor.digest}, which the registry does not "
        "register; run `fedcourts register-process` in the PR that moved it"
        for actor in actors
        if actor.digest not in registered
    ]


def _window_problems(registry: Mapping[str, Any]) -> list[str]:
    """Each predictor with more than one window still open.

    The invariant: per predictor, at most one window that is not revoked and
    has no close — a pending close counts as a close, since the carrying merge
    stamps it. A batch that opens a window without closing its predecessor, or
    opens two, breaks it.
    """
    open_windows: dict[str, list[Mapping[str, Any]]] = {}
    for window in registry.get("windows", []):
        if window["revoked_at"] is None and window["closes"] is None:
            open_windows.setdefault(window["predictor_id"], []).append(window)
    return [
        f"{predictor} has {len(windows)} open windows ("
        + ", ".join(f"{w['label']} {w['digest']}" for w in windows)
        + "): close each predecessor pending in the registration that opens its successor"
        for predictor, windows in sorted(open_windows.items())
        if len(windows) > 1
    ]


def _label_problems(
    repo: Path, registry: Mapping[str, Any], main_registry: Mapping[str, Any] | None
) -> list[str]:
    """More than one label new to ``main``, or a new label whose ``prereg/`` tag exists.

    The carrying merge mints ``prereg/<label>`` for the batch's one new label
    (:func:`fedcourtsai.promotion_record.plan_promotion_record`), an
    evaluator-only label (whose counting instant is carried, not pending)
    included, so a batch carries one label at most, and a tag already present
    is one nothing but that merge should have written. ``main_registry`` is
    ``None`` where ``main`` holds no registry file yet: it holds every label
    the record moved in from code (:func:`fedcourtsai.promotion_record.labels_new_to`).
    """
    new = labels_new_to(registry, main_registry)
    problems: list[str] = []
    if len(new) > 1:
        problems.append(
            f"the batch carries {len(new)} labels new to main ({', '.join(new)}): one label "
            "per promotion"
        )
    tags = _tags(repo, "prereg/")
    problems += [
        f"prereg/{label} already exists ({tags[f'prereg/{label}']}) for a label main does not "
        "hold yet: the carrying merge mints it"
        for label in new
        if f"prereg/{label}" in tags
    ]
    return problems


def _boundary_problems(registry: Mapping[str, Any]) -> list[str]:
    """Each boundary name registered more than once."""
    counts = Counter(boundary["name"] for boundary in registry.get("harness_boundaries", []))
    return [
        f"harness boundary {name!r} is registered {count} times"
        for name, count in sorted(counts.items())
        if count > 1
    ]


#: Each kind of row: its section, how it is named, and whether ``main`` stamped it.
_ROWS: tuple[
    tuple[str, str, Callable[[Mapping[str, Any]], str], Callable[[Mapping[str, Any]], bool]], ...
] = (
    (
        "labels",
        "label",
        lambda row: str(row["label"]),
        lambda row: row["since"]["merge"] is not None,
    ),
    (
        "blessings",
        "blessing",
        lambda row: str(row["digest"]),
        lambda row: row["blessed"]["merge"] is not None,
    ),
    (
        "windows",
        "window",
        lambda row: f"{row['label']} {row['digest']}",
        lambda row: row["opens"]["merge"] is not None,
    ),
    (
        "harness_boundaries",
        "boundary",
        lambda row: str(row["name"]),
        lambda row: row["merge"] is not None,
    ),
)
#: The sections whose order a reader takes as meaning: the last label row is
#: the counting instant, and windows and boundaries publish in registry order.
_ORDERED = frozenset({"labels", "windows", "harness_boundaries"})
_PENDING = {"at": None, "merge": None, "source": "merge"}
_MISSING = object()


@dataclass(frozen=True)
class _Stamped:
    """What check 8 compares: ``main``, its merge bases with the batch, and the batch.

    ``live`` and ``live_predictors`` are the digests the head's enabled actors
    compute; ``head_time`` is the head's committer time, which the carrying
    merge follows.
    """

    main: Mapping[str, Any]
    bases: Sequence[Mapping[str, Any]]
    batch: Mapping[str, Any]
    live: frozenset[str]
    live_predictors: frozenset[str]
    head_time: datetime

    def problems(self) -> list[str]:
        problems: list[str] = []
        declared = self.main.get("merge_stamping_declared")
        if declared is not None and not self._kept(
            self.batch.get("merge_stamping_declared"),
            declared,
            [base.get("merge_stamping_declared") for base in self.bases],
        ):
            problems.append(
                f"main declares merge-stamped instants on {declared} and the batch makes it "
                f"{self.batch.get('merge_stamping_declared')}"
            )
        for section, kind, name, stamped in _ROWS:
            problems += self._section_problems(section, kind, name, stamped)
        return problems + self._blessing_label_problems()

    @staticmethod
    def _kept(value: Any, main_value: Any, base_values: Sequence[Any]) -> bool:
        # Every base, not any: on a criss-cross history the bases disagree on a
        # field main stamped after one of them, and the merge keeps main's
        # stamp only where the batch holds what every base held.
        return bool(value == main_value) or (
            bool(base_values) and all(value == was for was in base_values)
        )

    def _section_problems(
        self,
        section: str,
        kind: str,
        name: Callable[[Mapping[str, Any]], str],
        stamped: Callable[[Mapping[str, Any]], bool],
    ) -> list[str]:
        base_rows = [{name(row): row for row in base.get(section, [])} for base in self.bases]
        batch_rows = {name(row): row for row in self.batch.get(section, [])}
        held = [name(row) for row in self.main.get(section, []) if stamped(row)]
        problems: list[str] = []
        for row in self.main.get(section, []):
            if not stamped(row):
                continue
            ident = name(row)
            was = [rows[ident] for rows in base_rows if ident in rows]
            now = batch_rows.get(ident)
            if now is None:
                if was and not self._may_leave(section, row):
                    problems.append(f"{kind} {ident} is stamped on main and the batch drops it")
                continue
            changed = sorted(
                key for key in set(row) | set(now) if not self._field_kept(key, row, now, was)
            )
            if changed:
                problems.append(
                    f"{kind} {ident} is stamped on main and the batch changes its "
                    f"{', '.join(changed)}: a stamped row reaches main as main holds it"
                )
        if section in _ORDERED:
            order = [ident for ident in batch_rows if ident in set(held)]
            expected = [ident for ident in held if ident in batch_rows]
            if order != expected and not (
                base_rows
                and all(
                    order == [ident for ident in rows if ident in set(order)] for rows in base_rows
                )
            ):
                problems.append(
                    f"the batch reorders the {section} main has stamped: "
                    f"{', '.join(order)} where main holds {', '.join(expected)}"
                )
            on_main = {name(row) for row in self.main.get(section, [])}
            idents = list(batch_rows)
            first_new = next((n for n, i in enumerate(idents) if i not in on_main), len(idents))
            early = [i for i in order if idents.index(i) > first_new]
            if early:
                problems.append(
                    f"the batch places {idents[first_new]} ahead of {', '.join(early)} in "
                    f"{section}: rows new to main follow every row main has stamped"
                )
        return problems

    def _may_leave(self, section: str, row: Mapping[str, Any]) -> bool:
        """A blessing whose digest left the fleet, its predictor window closed, may go."""
        if section != "blessings" or row["digest"] in self.live:
            return False
        if row["role"] != "predictor":
            return True
        return all(
            window["closes"] is not None or window["revoked_at"] is not None
            for window in self.batch.get("windows", [])
            if window["digest"] == row["digest"]
        )

    def _field_kept(
        self,
        key: str,
        row: Mapping[str, Any],
        now: Mapping[str, Any],
        was: Sequence[Mapping[str, Any]],
    ) -> bool:
        value = now.get(key, _MISSING)
        main_value = row.get(key, _MISSING)
        if self._kept(value, main_value, [base.get(key, _MISSING) for base in was]):
            return True
        if key == "closes" and main_value is None:
            # register-process closes, pending, the window no live predictor computes.
            return value == _PENDING and row["digest"] not in self.live_predictors
        if key == "revoked_at" and main_value is None and isinstance(value, str):
            # A revocation: only on a closed window, at or after the carrying merge.
            return now.get("closes") is not None and _instant(value) >= self.head_time
        return False

    def _blessing_label_problems(self) -> list[str]:
        """Each evaluator digest whose labels on ``main`` the batch does not keep as a prefix.

        What the batch appends is a label new to ``main``: the one it registers.
        """
        known = {entry["label"] for entry in self.main.get("labels", [])}
        batch_labels = self.batch.get("evaluate_blessing_labels", {})
        problems: list[str] = []
        for digest, labels in self.main.get("evaluate_blessing_labels", {}).items():
            now = batch_labels.get(digest)
            if self.bases and all(
                now == base.get("evaluate_blessing_labels", {}).get(digest) for base in self.bases
            ):
                continue
            if (
                now is not None
                and now[: len(labels)] == labels
                and not known & set(now[len(labels) :])
            ):
                continue
            problems.append(
                f"evaluator digest {digest} blesses {labels} on main and the batch makes it "
                f"{now}: blessing labels are append-only, and only a label new to main is appended"
            )
        return problems


def _instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
