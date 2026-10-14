"""What a staging→main promotion merge owes ``main``, computed from git alone.

A promotion merge carries registrations that are still **pending** — a label,
its blessings and windows, a harness boundary — and freeze-record entries with
``<FILL:>`` placeholders for facts only the merge knows: its tag, its SHA, its
time, and a census of the ledger at that moment. :func:`plan_promotion_record`
reads the merge commit, its first parent and the repository's tags, and says
what the merge owes: the annotated ``promotion/<UTC date>`` tag, a
``prereg/<label>`` tag on the merge where it added a label, each placeholder
the merge added that a closed key set can fill, and each pending registration
to stamp with the merge's SHA and committer time.
:func:`render_promotion_record` makes those edits on given copies of the two
files, :func:`apply_promotion_record` writes them into a working tree, and
:func:`promotion_record_diff_problems` is the jail: a promotion-record change
must be **byte-identical** to the plan rendered on its base, and is checked
structurally besides.

Only what the merge **added** is filled or stamped. A placeholder or pending
row the first parent already held — or a placeholder on a line the merge only
edited — was carried by an earlier merge, and stamping it with this one would
date it late; it is reported as stale, never written. Nothing here runs on a
merge by itself: a writer job that invokes it lands separately.
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
RECORD_PATHS = (REGISTRY_PATH, FREEZE_RECORD_PATH)

#: A candidate placeholder: ``<FILL:`` to the next ``>``, with no ``<``,
#: ``>`` or backtick inside. :func:`placeholders` also refuses a span that
#: crosses a blank line or names no word, so an unclosed marker cannot swallow
#: the paragraphs after it and a prose mention (``<FILL:>``, ``<FILL: …>``) is
#: not a placeholder. A placeholder wrapped across one line break is still one.
FILL_PATTERN = re.compile(r"<FILL:([^<>`]*)>")
_BLANK_LINE = re.compile(r"\n[ \t]*\n")
_WORD = re.compile(r"[A-Za-z]")

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
    """The merge cannot be planned, or a plan cannot be rendered or applied cleanly."""


def _git_argv(repo: Path, args: tuple[str, ...]) -> list[str]:
    # A configured signature check would print into %cI and show's output.
    return ["git", "-C", str(repo), "-c", "log.showSignature=false", *args]


def git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` and return its stdout; raises on failure."""
    result = subprocess.run(_git_argv(repo, args), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PromotionRecordError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def show_at(repo: Path, rev: str, path: str) -> str | None:
    """``path`` at ``rev``, or ``None`` where that tree does not hold it."""
    result = subprocess.run(
        _git_argv(repo, ("show", f"{rev}:{path}")), capture_output=True, text=True, check=False
    )
    return result.stdout if result.returncode == 0 else None


def committer_time(repo: Path, sha: str) -> datetime:
    """``sha``'s committer time, on UTC."""
    stamp = git(repo, "log", "-1", "--format=%cI", sha).strip()
    return datetime.fromisoformat(stamp).astimezone(UTC)


def iso(moment: datetime) -> str:
    """The registry's instant form: UTC, seconds, ``Z``."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize(key: str) -> str:
    return " ".join(key.split()).lower()


def _registry(text: str | None, where: str) -> dict[str, Any]:
    """A registry document, or a refusal naming where it would not parse."""
    try:
        document = json.loads(text or "{}")
    except json.JSONDecodeError as exc:
        raise PromotionRecordError(f"{where}: the registry is not JSON ({exc})") from exc
    if not isinstance(document, dict):
        raise PromotionRecordError(f"{where}: the registry is not a JSON object")
    return document


# --- tags --------------------------------------------------------------------


def _tags(repo: Path, prefix: str) -> dict[str, str]:
    """Every tag under ``prefix`` mapped to the commit it peels to.

    Reads the local tag refs, so a caller planning a merge fetches tags first;
    a missed tag would read as a free name.
    """
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
    """A copy of ``registry`` with each of ``stamps`` set to the merge's SHA and time.

    Only a row still pending is stamped; a row already stamped is left as it
    is, so a stamp can never overwrite a landed instant.
    """
    stamped: dict[str, Any] = copy.deepcopy(dict(registry))
    instant = {"at": iso(merged_at), "merge": merge, "source": "merge"}
    wanted = set(stamps)

    def due(kind: StampKind, ident: str, node: Any) -> bool:
        return Stamp(kind, ident) in wanted and isinstance(node, dict) and node["merge"] is None

    for entry in stamped.get("labels", []):
        if due("label", entry["label"], entry["since"]):
            entry["since"] = dict(instant)
    for blessing in stamped.get("blessings", []):
        if due("blessing", blessing["digest"], blessing["blessed"]):
            blessing["blessed"] = dict(instant)
    for window in stamped.get("windows", []):
        ident = f"{window['label']} {window['digest']}"
        if due("window-opens", ident, window["opens"]):
            window["opens"] = dict(instant)
        if due("window-closes", ident, window["closes"]):
            window["closes"] = dict(instant)
    for boundary in stamped.get("harness_boundaries", []):
        if due("boundary", boundary["name"], boundary):
            boundary["merge"] = merge
            boundary["at"] = iso(merged_at)
    return stamped


def _stamped_instants(registry: Mapping[str, Any]) -> list[datetime]:
    """Every instant a merge has already stamped or a hand has set, on UTC."""
    raw = [entry["since"]["at"] for entry in registry.get("labels", [])]
    raw += [blessing["blessed"]["at"] for blessing in registry.get("blessings", [])]
    for window in registry.get("windows", []):
        raw.append(window["opens"]["at"])
        if window["closes"] is not None:
            raw.append(window["closes"]["at"])
    return [
        datetime.fromisoformat(str(at).replace("Z", "+00:00")).astimezone(UTC)
        for at in raw
        if at is not None
    ]


def dump_registry(registry: Mapping[str, Any]) -> str:
    """The registry document in its committed form: two-space JSON and a final newline."""
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


def _prereg_message(registry: Mapping[str, Any], label: str, merge: str, at: str) -> str:
    entry = next(row for row in registry["labels"] if row["label"] == label)
    since = entry["since"]
    if since["merge"] is None:
        counts = f"counts from {at}, the committer time of merge {merge}."
    else:
        counts = f"holds the counting instant {since['at']}; merged as {merge} at {at}."
    lines = [f"prereg/{label}: {label} {counts}", "", "Blessed digests:"]
    for blessing in registry["blessings"]:
        carried = blessing["label"] != label
        how = f"carried from {blessing['label']}" if carried else "new"
        lines.append(f"- {blessing['role']} {blessing['actor_id']} {blessing['digest']} ({how})")
    return "\n".join(lines) + "\n"


# --- placeholders ------------------------------------------------------------


def placeholders(text: str) -> list[tuple[str, int, int, int]]:
    """Each placeholder in ``text``: its normalized key, start line, and byte span.

    A span that crosses a blank line, or whose key names no word, is not a
    placeholder: an unclosed ``<FILL:`` stays prose, and a mention of the
    marker itself is never filled.
    """
    found = []
    for match in FILL_PATTERN.finditer(text):
        inner = match.group(1)
        if _BLANK_LINE.search(inner) or not _WORD.search(inner):
            continue
        line = text.count("\n", 0, match.start())
        found.append((_normalize(inner), line, match.start(), match.end()))
    return found


def _added_placeholder_lines(before: str, after: str) -> set[int]:
    """The 0-based lines of ``after`` whose placeholders the change added.

    A line inserted, or edited from lines that held no placeholder of the same
    key, adds its placeholders. A placeholder on a line edited from one that
    already held that key — a typo fixed on a landed entry — was carried by an
    earlier merge, so the edit does not make it this merge's.
    """
    old_lines, new_lines = before.splitlines(keepends=True), after.splitlines(keepends=True)
    old_keys_by_line: dict[int, set[str]] = {}
    for key, line, _start, _end in placeholders(before):
        old_keys_by_line.setdefault(line, set()).add(key)
    new_keys_by_line: dict[int, set[str]] = {}
    for key, line, _start, _end in placeholders(after):
        new_keys_by_line.setdefault(line, set()).add(key)
    added: set[int] = set()
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            added.update(range(j1, j2))
        elif tag == "replace":
            held = set().union(*(old_keys_by_line.get(i, set()) for i in range(i1, i2)))
            for j in range(j1, j2):
                if not new_keys_by_line.get(j, set()) & held:
                    added.add(j)
    return added


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
    artifacts count for no digest; an artifact that is not JSON is refused.
    """
    if kind not in _ARTIFACT:
        raise PromotionRecordError(f"census kind is predictions or evaluations, not {kind!r}")
    prefixes = tuple(digest.removeprefix("sha256:").lower() for digest in digests)
    if not prefixes:
        raise PromotionRecordError("a census names at least one digest prefix")
    artifact = _ARTIFACT[kind]
    listed = git(repo, "ls-tree", "-r", "-z", "--name-only", rev, "--", "data/cases")
    names = [
        name for name in listed.split("\0") if name.endswith(f"/{artifact}") and f"/{kind}/" in name
    ]
    if not names:
        return 0
    batch = subprocess.run(
        _git_argv(repo, ("cat-file", "--batch")),
        input="".join(f"{rev}:{name}\n" for name in names).encode(),
        capture_output=True,
        check=True,
    ).stdout
    count = 0
    offset = 0
    for name in names:
        header_end = batch.index(b"\n", offset)
        header = batch[offset:header_end].split()
        size = int(header[2])
        body = batch[header_end + 1 : header_end + 1 + size]
        offset = header_end + 1 + size + 1
        try:
            document = json.loads(body)
        except json.JSONDecodeError as exc:
            raise PromotionRecordError(f"{name} at {rev} is not JSON") from exc
        stamp = (document.get("process_version") if isinstance(document, dict) else None) or {}
        digest = str(stamp.get("digest") or "").removeprefix("sha256:")
        if digest and digest.startswith(prefixes):
            count += 1
    return count


# --- the plan ----------------------------------------------------------------


def _merge_and_parent(repo: Path, merge: str) -> tuple[str, str, datetime]:
    """The merge's full SHA, its first parent and its committer time; refuses a non-merge.

    The committer time must not precede the first parent's, nor lie in the
    future: either would date every stamp wrong.
    """
    merge = git(repo, "rev-parse", "--verify", f"{merge}^{{commit}}").strip()
    parents = git(repo, "rev-list", "--parents", "-n", "1", merge).split()[1:]
    if len(parents) != 2:
        raise PromotionRecordError(f"{merge} is not a two-parent merge")
    merged_at = committer_time(repo, merge)
    if merged_at < committer_time(repo, parents[0]):
        raise PromotionRecordError(f"{merge} is committed before its first parent")
    if merged_at > datetime.now(UTC):
        raise PromotionRecordError(f"{merge} is committed in the future")
    return merge, parents[0], merged_at


def plan_promotion_record(repo: Path, merge: str) -> PromotionPlan:
    """What ``merge`` owes ``main``: tags, fills and stamps, read from git alone.

    Refuses anything but a two-parent merge. Compares the merge's tree with its
    first parent's — what ``main`` held before — so only what the promotion
    added is filled or stamped.
    """
    merge, parent, merged_at = _merge_and_parent(repo, merge)
    tag, adopt = promotion_tag_name(repo, merge, merged_at)
    promotion = TagPlan(tag, adopt, f"{tag}: the staging→main promotion merged as {merge}.\n")

    def census(kind: str, digests: list[str]) -> int:
        return digest_census(repo, merge, kind, digests)

    record_after = show_at(repo, merge, FREEZE_RECORD_PATH) or ""
    record_before = show_at(repo, parent, FREEZE_RECORD_PATH) or ""
    added = _added_placeholder_lines(record_before, record_after)
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

    registry_after = _registry(show_at(repo, merge, REGISTRY_PATH), merge)
    registry_before = _registry(show_at(repo, parent, REGISTRY_PATH), parent)
    latest = max(_stamped_instants(registry_after), default=None)
    if latest is not None and merged_at < latest:
        raise PromotionRecordError(
            f"{merge} is committed at {iso(merged_at)}, before the registered instant "
            f"{iso(latest)}: its stamps would close a window before it opened"
        )
    pending_after = pending_registrations(registry_after)
    pending_before = set(pending_registrations(registry_before))
    stamps = [stamp for stamp in pending_after if stamp not in pending_before]
    stale_pending = [stamp for stamp in pending_after if stamp in pending_before]

    prereg: TagPlan | None = None
    known = {entry["label"] for entry in registry_before.get("labels", [])}
    new_labels = [
        entry["label"] for entry in registry_after.get("labels", []) if entry["label"] not in known
    ]
    if new_labels:
        label = new_labels[-1]
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
        raise PromotionRecordError("the edit conflicts with the copy it is carried onto")
    return result.stdout


#: Checks a rendered registry's semantics (the loader's rules) beyond its schema.
type RegistryCheck = Callable[[str], object]


def render_promotion_record(
    repo: Path,
    plan: PromotionPlan,
    onto: Mapping[str, str | None],
    *,
    check_registry: RegistryCheck | None = None,
) -> dict[str, str | None]:
    """The two files as ``plan`` leaves them, rendered onto the copies in ``onto``.

    Each edit is made on the merge's own copy and carried onto ``onto``'s by a
    three-way merge, so later commits that touched other lines keep them. A
    path the plan does not edit comes back as given. Raises
    :class:`PromotionRecordError` — before anything is written anywhere —
    where an edit conflicts, or where the rendered registry fails its schema
    or ``check_registry``.
    """
    rendered: dict[str, str | None] = dict(onto)
    if plan.fills:
        merged = show_at(repo, plan.merge, FREEZE_RECORD_PATH) or ""
        tip = onto.get(FREEZE_RECORD_PATH)
        if tip is None:
            raise PromotionRecordError(f"{FREEZE_RECORD_PATH} is missing")
        rendered[FREEZE_RECORD_PATH] = _three_way(tip, merged, substitute(merged, plan.fills))
    if plan.stamps:
        merged = show_at(repo, plan.merge, REGISTRY_PATH) or ""
        stamped = dump_registry(
            stamp_registry(
                _registry(merged, plan.merge),
                plan.stamps,
                plan.merge,
                datetime.fromisoformat(plan.merged_at),
            )
        )
        tip = onto.get(REGISTRY_PATH)
        if tip is None:
            raise PromotionRecordError(f"{REGISTRY_PATH} is missing")
        result = _three_way(tip, merged, stamped)
        try:
            ProcessRegistry.model_validate_json(result)
            if check_registry is not None:
                check_registry(result)
        except ValueError as exc:
            raise PromotionRecordError(f"the stamped registry is refused: {exc}") from exc
        rendered[REGISTRY_PATH] = result
    return rendered


def apply_promotion_record(
    repo: Path,
    worktree: Path,
    plan: PromotionPlan,
    *,
    check_registry: RegistryCheck | None = None,
) -> list[str]:
    """Write the plan's fills and stamps into ``worktree``; returns the paths it changed.

    Renders both files first (:func:`render_promotion_record`), so a conflict
    or a refused registry writes nothing at all.
    """
    current = {
        path: (worktree / path).read_text(encoding="utf-8") if (worktree / path).exists() else None
        for path in RECORD_PATHS
    }
    rendered = render_promotion_record(repo, plan, current, check_registry=check_registry)
    changed = []
    for path in RECORD_PATHS:
        new = rendered.get(path)
        if new is not None and new != current[path]:
            changed.append(path)
    for path in changed:
        text = rendered[path]
        if text is not None:
            (worktree / path).write_text(text, encoding="utf-8")
    return changed


# --- main must hold nothing pending --------------------------------------------


def pending_carried_problems(repo: Path, ref: str, *, depth: int = 200) -> list[str]:
    """Each pending row on ``ref`` that a merge on its first-parent chain already carried.

    A pending row belongs on ``staging`` only: once a promotion merge carries
    it to ``main``, that merge is due to stamp it. Walks ``ref``'s first-parent
    merges, newest first, up to ``depth``, and names the merge that introduced
    each row still pending at ``ref``. Empty when ``ref`` holds nothing pending.
    """
    pending = set(pending_registrations(_registry(show_at(repo, ref, REGISTRY_PATH), ref)))
    if not pending:
        return []
    problems: list[str] = []
    merges = git(
        repo, "rev-list", "--first-parent", "--merges", f"--max-count={depth}", ref
    ).split()
    for merge in merges:
        parent = git(repo, "rev-parse", f"{merge}^1").strip()
        after = set(pending_registrations(_registry(show_at(repo, merge, REGISTRY_PATH), merge)))
        before = set(pending_registrations(_registry(show_at(repo, parent, REGISTRY_PATH), parent)))
        for stamp in sorted((after - before) & pending, key=lambda s: (s.kind, s.ident)):
            problems.append(f"{stamp.kind} {stamp.ident}: carried by {merge}, still pending")
        pending -= after - before
        if not pending:
            break
    return problems


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
    """Whether ``after`` is ``before`` with only placeholders replaced by one-line values.

    Walks ``before``'s literal text in order: each placeholder may stay as it
    is or become one line holding no ``<``, ``>`` or backtick, and every
    literal stretch must follow unchanged.
    """
    cursor = 0
    position = 0
    spans = [(start, end) for _key, _line, start, end in placeholders(before)]
    for index, (start, end) in enumerate(spans):
        literal = before[position:start]
        if not after.startswith(literal, cursor):
            return False
        cursor += len(literal)
        next_literal = before[end : spans[index + 1][0] if index + 1 < len(spans) else None]
        original = before[start:end]
        if after.startswith(original + next_literal, cursor):
            cursor += len(original)
        elif not next_literal and index + 1 < len(spans):
            return False  # two abutting placeholders: no literal marks where a value ends
        else:
            stop = after.find(next_literal, cursor) if next_literal else len(after)
            value = after[cursor:stop] if stop >= 0 else ""
            if stop < 0 or not value or re.search(r"[\n<>`]", value):
                return False
            cursor = stop
        position = end
    return after[cursor:] == before[position:]


def promotion_record_diff_problems(
    changed: list[str],
    before: Mapping[str, str | None],
    after: Mapping[str, str | None],
    *,
    expected: Mapping[str, str | None] | None = None,
) -> list[str]:
    """Why a promotion-record change exceeds what it may write; empty when it does not.

    It may change only the registry and the freeze record. Where ``expected``
    is given — the plan rendered on the same base
    (:func:`render_promotion_record`) — each must equal it byte for byte, so
    the stamps carry the merge's own SHA and committer time and no free-text
    or stale placeholder moves. Structurally besides: the registry only by
    stamping pending instants and boundaries, the freeze record only by
    replacing placeholders with one-line values.
    """
    problems = [
        f"{path}: a promotion record writes only {REGISTRY_PATH} and {FREEZE_RECORD_PATH}"
        for path in changed
        if path not in RECORD_PATHS
    ]
    if expected is not None:
        for path in RECORD_PATHS:
            if after.get(path) != expected.get(path):
                problems.append(f"{path}: differs from the plan rendered on its base")
    if REGISTRY_PATH in changed:
        problems += _registry_problems(before.get(REGISTRY_PATH), after.get(REGISTRY_PATH))
    if FREEZE_RECORD_PATH in changed:
        old, new = before.get(FREEZE_RECORD_PATH), after.get(FREEZE_RECORD_PATH)
        if old is None or new is None or not _fills_only(old, new):
            problems.append(
                f"{FREEZE_RECORD_PATH}: changes something other than <FILL:> placeholders"
            )
    return problems


def _registry_problems(old: str | None, new: str | None) -> list[str]:
    if old is None or new is None:
        return [f"{REGISTRY_PATH}: created or deleted"]
    problems = []
    try:
        ProcessRegistry.model_validate_json(new)
    except ValueError as exc:
        problems.append(f"{REGISTRY_PATH}: invalid ({exc})")
    try:
        if not _stamped_only(json.loads(old), json.loads(new)):
            problems.append(f"{REGISTRY_PATH}: changes something other than pending stamps")
    except json.JSONDecodeError as exc:
        problems.append(f"{REGISTRY_PATH}: not JSON ({exc})")
    return problems
