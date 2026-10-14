"""What a staging→main promotion merge owes ``main``, computed from git alone.

A promotion merge carries registrations that are still **pending** — a label,
its blessings and windows, a harness boundary — and freeze-record entries with
``<FILL:>`` placeholders for facts only the merge knows: its tag, its SHA, its
time, and a census of the ledger at that moment. :func:`plan_promotion_record`
reads the merge commit and its first parent and nothing else, and says what
the merge owes: the annotated ``promotion/<UTC date>`` tag, a ``prereg/<label>``
tag where the merge carried a label, each placeholder the merge added that a
closed key set can fill, and each pending registration to stamp with the
merge's SHA and committer time. :func:`apply_promotion_record` writes those
edits into a working tree; :func:`promotion_record_diff_problems` is the jail
that holds such a commit to exactly that.

Only what the merge **added** is filled or stamped. A placeholder or pending
row the first parent already held was carried by an earlier merge, and
stamping it with this one would date it late; it is reported as stale, never
written.
"""

from __future__ import annotations

import copy
import difflib
import json
import re
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from .schemas import ProcessRegistry

#: The registry and the freeze record, as paths in the repository.
REGISTRY_PATH = "src/fedcourtsai/process_registry.json"
FREEZE_RECORD_PATH = "docs/freeze-record.md"

#: A freeze-record placeholder. ``[^<>]`` spans newlines, so a placeholder
#: wrapped across lines is still one placeholder.
FILL_PATTERN = re.compile(r"<FILL:([^<>]*)>")

#: The closed key set a promotion merge can fill: its tag, its SHA, its time.
#: Keys compare case-insensitively after whitespace is collapsed.
TAG_KEYS = frozenset({"promotion tag"})
SHA_KEYS = frozenset({"merge hash", "merge sha"})
TIME_KEYS = frozenset({"merged-at", "merged time utc"})

#: A census placeholder: ``census predictions digest=<hex>[,<hex>…]`` or the
#: ``evaluations`` twin, each digest an 8-to-64-hex prefix of the process
#: digest. Filled with the number of committed artifacts of that kind, on the
#: merge's tree, whose stamp carries any of the digests.
CENSUS_PATTERN = re.compile(
    r"census (predictions|evaluations) digest=([0-9a-f]{8,64}(?:,[0-9a-f]{8,64})*)"
)

type StampKind = Literal["label", "blessing", "window-opens", "window-closes", "boundary"]

#: Reads a census: the artifact kind and the digest prefixes, to a count.
type CensusReader = Callable[[str, list[str]], int]


@dataclass(frozen=True)
class Stamp:
    """One pending registration the merge stamps with its SHA and time."""

    kind: StampKind
    ident: str


@dataclass(frozen=True)
class Fill:
    """One placeholder the merge added: its key, its line, and its value if the key set has one.

    ``value`` is ``None`` for a free-text placeholder, which no merge can fill
    and a maintainer completes by hand.
    """

    key: str
    line: int
    value: str | None
    start: int = field(repr=False)
    end: int = field(repr=False)


@dataclass(frozen=True)
class TagPlan:
    """An annotated tag on the merge; ``adopt`` where one already peels to it."""

    name: str
    adopt: bool
    message: str


@dataclass(frozen=True)
class PromotionPlan:
    """Everything one promotion merge owes ``main``."""

    merge: str
    merged_at: str
    promotion_tag: TagPlan
    prereg_tag: TagPlan | None
    fills: list[Fill]
    free_text: list[Fill]
    stamps: list[Stamp]
    stale_pending: list[Stamp]
    stale_placeholders: list[Fill]

    def to_json(self) -> dict[str, Any]:
        """The plan as JSON-ready data, without the placeholders' byte offsets."""
        payload = asdict(self)
        for group in ("fills", "free_text", "stale_placeholders"):
            for item in payload[group]:
                item.pop("start")
                item.pop("end")
        return payload


class PromotionRecordError(RuntimeError):
    """The merge cannot be planned, or a plan cannot be applied cleanly."""


def git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` and return its stdout; raises on failure."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise PromotionRecordError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def show_at(repo: Path, rev: str, path: str) -> str | None:
    """``path`` at ``rev``, or ``None`` where that tree does not hold it."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def committer_time(repo: Path, sha: str) -> datetime:
    """``sha``'s committer time, on UTC."""
    return datetime.fromisoformat(git(repo, "log", "-1", "--format=%cI", sha).strip()).astimezone(
        UTC
    )


def iso(moment: datetime) -> str:
    """The registry's instant form: UTC, seconds, ``Z``."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize(key: str) -> str:
    return " ".join(key.split()).lower()


# --- tags --------------------------------------------------------------------


def _tags(repo: Path, prefix: str) -> dict[str, str]:
    """Every tag under ``prefix`` mapped to the commit it peels to."""
    out = git(
        repo,
        "for-each-ref",
        "--format=%(refname:strip=2) %(objectname) %(*objectname)",
        f"refs/tags/{prefix}",
    )
    tags: dict[str, str] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            tags[parts[0]] = parts[2] if len(parts) == 3 else parts[1]
    return tags


def promotion_tag_name(repo: Path, merge: str, merged_at: datetime) -> tuple[str, bool]:
    """The merge's ``promotion/<UTC date>`` tag, and whether one already peels to it.

    A tag that already names the merge is adopted, so a re-run never mints a
    second; otherwise the merge's UTC date, suffixed ``-2``, ``-3`` … past
    each name another merge already holds.
    """
    tags = _tags(repo, "promotion/")
    for name, peeled in sorted(tags.items()):
        if peeled == merge:
            return name, True
    base = f"promotion/{merged_at.astimezone(UTC):%Y-%m-%d}"
    if base not in tags:
        return base, False
    suffix = 2
    while f"{base}-{suffix}" in tags:
        suffix += 1
    return f"{base}-{suffix}", False


# --- registry stamps ---------------------------------------------------------


def pending_registrations(registry: Mapping[str, Any]) -> list[Stamp]:
    """Every pending registration in a registry document, in document order."""
    found: list[Stamp] = []
    for entry in registry.get("labels", []):
        if entry["since"]["merge"] is None:
            found.append(Stamp("label", entry["label"]))
    for blessing in registry.get("blessings", []):
        if blessing["blessed"]["merge"] is None:
            found.append(Stamp("blessing", blessing["digest"]))
    for window in registry.get("windows", []):
        ident = f"{window['label']} {window['digest']}"
        if window["opens"]["merge"] is None:
            found.append(Stamp("window-opens", ident))
        if window["closes"] is not None and window["closes"]["merge"] is None:
            found.append(Stamp("window-closes", ident))
    for boundary in registry.get("harness_boundaries", []):
        if boundary["merge"] is None:
            found.append(Stamp("boundary", boundary["name"]))
    return found


def stamp_registry(
    registry: Mapping[str, Any], stamps: list[Stamp], merge: str, merged_at: datetime
) -> dict[str, Any]:
    """A copy of ``registry`` with each of ``stamps`` set to the merge's SHA and time."""
    stamped: dict[str, Any] = copy.deepcopy(dict(registry))
    instant = {"at": iso(merged_at), "merge": merge, "source": "merge"}
    wanted = set(stamps)
    for entry in stamped["labels"]:
        if Stamp("label", entry["label"]) in wanted:
            entry["since"] = dict(instant)
    for blessing in stamped["blessings"]:
        if Stamp("blessing", blessing["digest"]) in wanted:
            blessing["blessed"] = dict(instant)
    for window in stamped["windows"]:
        ident = f"{window['label']} {window['digest']}"
        if Stamp("window-opens", ident) in wanted:
            window["opens"] = dict(instant)
        if Stamp("window-closes", ident) in wanted:
            window["closes"] = dict(instant)
    for boundary in stamped["harness_boundaries"]:
        if Stamp("boundary", boundary["name"]) in wanted:
            boundary["merge"] = merge
            boundary["at"] = iso(merged_at)
    return stamped


def dump_registry(registry: Mapping[str, Any]) -> str:
    """The registry document in its committed form: two-space JSON and a final newline."""
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


def _prereg_message(registry: Mapping[str, Any], label: str, merge: str, at: str) -> str:
    lines = [f"prereg/{label}: {label} counts from {at}, the committer time of merge {merge}."]
    lines.append("")
    lines.append("Blessed digests:")
    for blessing in registry["blessings"]:
        carried = blessing["label"] != label
        how = f"carried from {blessing['label']}" if carried else "new"
        lines.append(f"- {blessing['role']} {blessing['actor_id']} {blessing['digest']} ({how})")
    return "\n".join(lines) + "\n"


# --- placeholders ------------------------------------------------------------


def _added_lines(before: str, after: str) -> set[int]:
    """The 0-based lines of ``after`` that ``before`` does not hold, by line diff."""
    old, new = before.splitlines(), after.splitlines()
    added: set[int] = set()
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag in ("insert", "replace"):
            added.update(range(j1, j2))
    return added


def placeholders(text: str) -> list[tuple[str, int, int, int]]:
    """Each placeholder in ``text``: its normalized key, start line, and byte span."""
    found = []
    for match in FILL_PATTERN.finditer(text):
        line = text.count("\n", 0, match.start())
        found.append((_normalize(match.group(1)), line, match.start(), match.end()))
    return found


def fill_value(
    key: str, *, tag: str, merge: str, merged_at: datetime, census: CensusReader
) -> str | None:
    """The closed key set's value for ``key``, or ``None`` for a free-text placeholder."""
    if key in TAG_KEYS:
        return tag
    if key in SHA_KEYS:
        return merge
    if key in TIME_KEYS:
        return iso(merged_at)
    match = CENSUS_PATTERN.fullmatch(key)
    if match:
        kind = "predictions" if match.group(1) == "predictions" else "evaluations"
        return str(census(kind, match.group(2).split(",")))
    return None


# --- census ------------------------------------------------------------------

_ARTIFACT = {"predictions": "prediction.json", "evaluations": "evaluation.json"}


def digest_census(repo: Path, rev: str, kind: str, digests: list[str]) -> int:
    """How many committed ``kind`` artifacts at ``rev`` carry a stamp naming any of ``digests``.

    Reads every ``data/cases/**/<kind>/**/<artifact>.json`` on ``rev``'s tree
    and counts those whose ``process_version.digest`` starts (after its
    ``sha256:`` prefix) with one of the given hex prefixes. Unstamped
    artifacts count for no digest.
    """
    if kind not in _ARTIFACT:
        raise PromotionRecordError(f"census kind is predictions or evaluations, not {kind!r}")
    prefixes = tuple(digest.removeprefix("sha256:").lower() for digest in digests)
    artifact = _ARTIFACT[kind]
    names = [
        name
        for name in git(repo, "ls-tree", "-r", "--name-only", rev, "--", "data/cases").splitlines()
        if name.endswith(f"/{artifact}") and f"/{kind}/" in name
    ]
    if not names:
        return 0
    batch = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        input="".join(f"{rev}:{name}\n" for name in names).encode(),
        capture_output=True,
        check=True,
    ).stdout
    count = 0
    offset = 0
    for _ in names:
        header_end = batch.index(b"\n", offset)
        header = batch[offset:header_end].split()
        size = int(header[2])
        body = batch[header_end + 1 : header_end + 1 + size]
        offset = header_end + 1 + size + 1
        stamp = json.loads(body).get("process_version") or {}
        digest = str(stamp.get("digest") or "").removeprefix("sha256:")
        if digest and digest.startswith(prefixes):
            count += 1
    return count


# --- the plan ----------------------------------------------------------------


def plan_promotion_record(repo: Path, merge: str) -> PromotionPlan:
    """What ``merge`` owes ``main``: tags, fills and stamps, read from git alone.

    Refuses anything but a two-parent merge. Compares the merge's tree with its
    first parent's — what ``main`` held before — so only what the promotion
    added is filled or stamped.
    """
    merge = git(repo, "rev-parse", "--verify", f"{merge}^{{commit}}").strip()
    parents = git(repo, "rev-list", "--parents", "-n", "1", merge).split()[1:]
    if len(parents) != 2:
        raise PromotionRecordError(f"{merge} is not a two-parent merge")
    parent = parents[0]
    merged_at = committer_time(repo, merge)
    tag, adopt = promotion_tag_name(repo, merge, merged_at)
    promotion = TagPlan(tag, adopt, f"{tag}: the staging→main promotion merged as {merge}.\n")

    def census(kind: str, digests: list[str]) -> int:
        return digest_census(repo, merge, kind, digests)

    record_after = show_at(repo, merge, FREEZE_RECORD_PATH) or ""
    record_before = show_at(repo, parent, FREEZE_RECORD_PATH) or ""
    added = _added_lines(record_before, record_after)
    fills: list[Fill] = []
    free: list[Fill] = []
    stale: list[Fill] = []
    for key, line, start, end in placeholders(record_after):
        value = fill_value(key, tag=tag, merge=merge, merged_at=merged_at, census=census)
        item = Fill(key, line + 1, value, start, end)
        if line not in added:
            stale.append(item)
        elif value is None:
            free.append(item)
        else:
            fills.append(item)

    registry_after = json.loads(show_at(repo, merge, REGISTRY_PATH) or "{}")
    registry_before = json.loads(show_at(repo, parent, REGISTRY_PATH) or "{}")
    pending_after = pending_registrations(registry_after)
    pending_before = set(pending_registrations(registry_before))
    stamps = [stamp for stamp in pending_after if stamp not in pending_before]
    stale_pending = [stamp for stamp in pending_after if stamp in pending_before]

    prereg: TagPlan | None = None
    labels = [stamp.ident for stamp in stamps if stamp.kind == "label"]
    if labels:
        label = labels[0]
        name = f"prereg/{label}"
        existing = _tags(repo, "prereg/").get(name)
        if existing is not None and existing != merge:
            raise PromotionRecordError(f"{name} already names {existing}, not {merge}")
        prereg = TagPlan(
            name,
            existing == merge,
            _prereg_message(registry_after, label, merge, iso(merged_at)),
        )
    return PromotionPlan(
        merge=merge,
        merged_at=iso(merged_at),
        promotion_tag=promotion,
        prereg_tag=prereg,
        fills=fills,
        free_text=free,
        stamps=stamps,
        stale_pending=stale_pending,
        stale_placeholders=stale,
    )


def substitute(text: str, fills: list[Fill]) -> str:
    """``text`` with each fill's placeholder span replaced by its value, back to front."""
    for item in sorted(fills, key=lambda fill: fill.start, reverse=True):
        if item.value is None:
            continue
        text = text[: item.start] + item.value + text[item.end :]
    return text


def _three_way(tip: str, base: str, patched: str) -> str:
    """Carry ``base``→``patched`` onto ``tip``; refuses a conflicting merge."""
    if tip == base:
        return patched
    with tempfile.TemporaryDirectory() as scratch:
        paths = []
        for name, content in (("tip", tip), ("base", base), ("patched", patched)):
            path = Path(scratch) / name
            path.write_text(content, encoding="utf-8")
            paths.append(str(path))
        result = subprocess.run(
            ["git", "merge-file", "-p", *paths], capture_output=True, text=True, check=False
        )
    if result.returncode != 0:
        raise PromotionRecordError("the edit conflicts with the working tree's copy")
    return result.stdout


def apply_promotion_record(repo: Path, worktree: Path, plan: PromotionPlan) -> list[str]:
    """Write the plan's fills and stamps into ``worktree``; returns the paths it changed.

    Each edit is made on the merge's own copy of the file and carried onto the
    working tree's copy by a three-way merge, so later commits that touched
    other lines of the same file keep them.
    """
    changed: list[str] = []
    if plan.fills:
        merged = show_at(repo, plan.merge, FREEZE_RECORD_PATH) or ""
        target = worktree / FREEZE_RECORD_PATH
        tip = target.read_text(encoding="utf-8")
        result = _three_way(tip, merged, substitute(merged, plan.fills))
        if result != tip:
            target.write_text(result, encoding="utf-8")
            changed.append(FREEZE_RECORD_PATH)
    if plan.stamps:
        merged = show_at(repo, plan.merge, REGISTRY_PATH) or ""
        stamped = dump_registry(
            stamp_registry(
                json.loads(merged),
                plan.stamps,
                plan.merge,
                datetime.fromisoformat(plan.merged_at),
            )
        )
        target = worktree / REGISTRY_PATH
        tip = target.read_text(encoding="utf-8")
        result = _three_way(tip, merged, stamped)
        ProcessRegistry.model_validate_json(result)
        if result != tip:
            target.write_text(result, encoding="utf-8")
            changed.append(REGISTRY_PATH)
    return changed


# --- the jail ----------------------------------------------------------------

_SHA40 = re.compile(r"[0-9a-f]{40}")
_INSTANT_KEYS = {"at", "merge", "source"}


def _pending_instant(node: Any) -> bool:
    return (
        isinstance(node, dict)
        and set(node) == _INSTANT_KEYS
        and node["at"] is None
        and node["merge"] is None
    )


def _merge_stamp(node: Any) -> bool:
    return (
        isinstance(node, dict)
        and set(node) == _INSTANT_KEYS
        and isinstance(node["at"], str)
        and isinstance(node["merge"], str)
        and bool(_SHA40.fullmatch(node["merge"]))
        and node["source"] == "merge"
    )


def _stamped_only(before: Any, after: Any) -> bool:
    """Whether ``after`` is ``before`` with only pending instants and boundaries stamped."""
    if _pending_instant(before):
        return _merge_stamp(after)
    if isinstance(before, dict) and isinstance(after, dict):
        if set(before) != set(after):
            return False
        if "reach" in before and before.get("merge") is None and after.get("merge") is not None:
            rest = {key for key in before if key not in ("merge", "at")}
            return (
                before.get("at") is None
                and isinstance(after.get("at"), str)
                and bool(_SHA40.fullmatch(str(after["merge"])))
                and all(_stamped_only(before[key], after[key]) for key in rest)
            )
        return all(_stamped_only(before[key], after[key]) for key in before)
    if isinstance(before, list) and isinstance(after, list):
        return len(before) == len(after) and all(
            _stamped_only(old, new) for old, new in zip(before, after, strict=True)
        )
    return bool(before == after)


def _fills_only(before: str, after: str) -> bool:
    """Whether ``after`` is ``before`` with only placeholders replaced by one-line values."""
    pattern: list[str] = []
    cursor = 0
    for match in FILL_PATTERN.finditer(before):
        pattern.append(re.escape(before[cursor : match.start()]))
        pattern.append(f"(?:{re.escape(match.group(0))}|[^<>\\n]+)")
        cursor = match.end()
    pattern.append(re.escape(before[cursor:]))
    return re.fullmatch("".join(pattern), after) is not None


def promotion_record_diff_problems(
    changed: list[str], before: Mapping[str, str | None], after: Mapping[str, str | None]
) -> list[str]:
    """Why a promotion-record commit exceeds what it may write; empty when it does not.

    It may change only the registry and the freeze record: the registry only by
    stamping pending instants and boundaries, the freeze record only by
    replacing ``<FILL:>`` placeholders with one-line values.
    """
    problems = [
        f"{path}: a promotion record writes only {REGISTRY_PATH} and {FREEZE_RECORD_PATH}"
        for path in changed
        if path not in (REGISTRY_PATH, FREEZE_RECORD_PATH)
    ]
    if REGISTRY_PATH in changed:
        old, new = before.get(REGISTRY_PATH), after.get(REGISTRY_PATH)
        if old is None or new is None:
            problems.append(f"{REGISTRY_PATH}: created or deleted")
        else:
            try:
                ProcessRegistry.model_validate_json(new)
            except ValueError as exc:
                problems.append(f"{REGISTRY_PATH}: invalid ({exc})")
            if not _stamped_only(json.loads(old), json.loads(new)):
                problems.append(f"{REGISTRY_PATH}: changes something other than pending stamps")
    if FREEZE_RECORD_PATH in changed:
        old, new = before.get(FREEZE_RECORD_PATH), after.get(FREEZE_RECORD_PATH)
        if old is None or new is None or not _fills_only(old, new):
            problems.append(
                f"{FREEZE_RECORD_PATH}: changes something other than <FILL:> placeholders"
            )
    return problems
