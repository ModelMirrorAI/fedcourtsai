"""Audit a predict cell's logged tool calls for reads and writes outside its lane.

``run-predict`` takes two surfaces out of the agent's working tree before it
starts: ``data/qp-topics/``, whose membership encodes cert outcomes, and the
committed ``predictions/`` and ``evaluations/`` trees, which carry every other
predictor's forecasts and their gradings. Both stay reachable on purpose
through git history, and a cell's own writes are confined by its prompt rather
than by the tree. So the witness to a cell that went looking — or wrote
beside its own output — is its ``retrieval_log.json``, read twice: by this
check, which leaves a harness note in the cell's ``flags.json``, and by the
judges who grade the cell.

:func:`audit_cell_access` is that check. It reads the captured query slice of
each call the cell could have touched its tree with (a shell, a file tool, or a
call the capture could not classify) and reports three kinds of hit:

* **oracle** — the call names ``qp-topics``;
* **cell record** — the call names an ``evaluations/`` tree, or a
  ``predictions/<id>/`` path that is not this cell's own run directory (another
  predictor's, this predictor's earlier run, or a glob over them);
* **write** — a file tool's target, or a shell redirection's, names ``data/`` or
  a case ``record/`` outside this cell's own run directory.

A path named only to exclude it — ``find … -not -path 'data/qp-topics/*'``,
``--exclude``, a ``!`` glob, a ``:(exclude)`` pathspec, a ``-prune`` — is no
access, and is stripped before matching. An inverted ``grep -v`` is not an
exclusion: it filters output a command already opened, which is the evaluate
prompt's reading too.

What it cannot see bounds what a clean audit means. The query slice is cut at
capture, so a path past the cut is missed — and capture serializes a file
tool's params in sorted key order, so a long ``content`` pushes a write
tool's target past the cut on most such calls, leaving those writes seen
only where the path survives; a relative path is matched as
written, so a write after a ``cd`` into the case directory names no ``data/``;
a call that reads through an indirection (a variable, a script file) or a
glob over the hidden name itself (``qp-top*``) names nothing the patterns
match; a write is seen only through a file tool or a shell redirection or
``tee`` — ``cp``, ``mv``, ``sed -i`` or an interpreter's own writes are not;
and a write is matched to the cell's own run directory by its
``predictions/<id>/<run>`` segment and, where the path names one, its case and
event, so a write into another case of the same run is caught only when its
path is written out in full. A hit is evidence that a call *named* the path, not that it
read anything — a ``git status`` that lists the deletion names it too, which
is why the hidden paths are marked skip-worktree before the agent runs.
"""

from __future__ import annotations

import json
import posixpath
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum

from .blinding import neutral_tool_class
from .retrieval import QUERY_CAP
from .schemas import RetrievalCall


class AccessKind(StrEnum):
    """Which line a call crossed."""

    oracle = "oracle"
    cell_record = "cell-record"
    write = "write"


@dataclass(frozen=True)
class AccessHit:
    """One call that crossed a line, with the path text that crossed it."""

    kind: AccessKind
    tool: str
    path: str


# The calls that never touch the cell's tree: a hosted search or fetch, and an
# MCP tool, whose arguments are a query against someone else's server.
_REMOTE_CLASSES = frozenset({"web-search", "web-fetch"})
# A subagent's prompt is instructions, not access — and names a hidden path
# chiefly to forbid it; the subagent's own calls are logged as calls.
_PROMPT_TOOLS = frozenset({"agent", "task"})

# One shell argument, quoted or bare.
_ARG = r"""(?:'[^']*'|"[^"]*"|[^\s'"]+)"""
# A path named only to leave it out. Each is stripped from the slice before the
# hidden paths are matched, so an exclusion predicate reads as no access.
_EXCLUSIONS = tuple(
    re.compile(pattern)
    for pattern in (
        # find's negated tests: `-not -path X`, `! -path X`, `-not -name X`, …
        rf"(?:-not|!)\s+-i?(?:path|name|wholename|regex)\s+{_ARG}",
        # find's prune idiom: `-path X -prune`
        rf"-i?(?:path|name|wholename)\s+{_ARG}\s+-prune",
        # grep/rsync/tar-style exclusions: `--exclude=X`, `--exclude-dir X`
        rf"--exclude(?:-dir|-from)?(?:=|\s+){_ARG}",
        # git's excluding pathspec magic: `':!X'`, `':^X'`, `':(exclude)X'`
        r"""['"]?:(?:\(exclude\)|!|\^)[^\s'"]+['"]?""",
        # a negated glob opening its own argument: `-g '!X'`, `--glob=!X`; never
        # a `^` or `!` inside a revision such as `HEAD^:path`
        r"""(?:(?<=\s)|(?<==)|^)['"]?![^\s'"]+['"]?""",
    )
)

# The characters a path token runs over: anything but a quote, a space or a
# shell delimiter.
_TOKEN = r"[^\s'\"`;|&<>()\\]*"
_ORACLE = re.compile(rf"{_TOKEN}qp-topics\b{_TOKEN}")
_EVALUATIONS = re.compile(rf"{_TOKEN}(?<![\w-])evaluations\b{_TOKEN}")
# A git command that reads the committed tree rather than the working one.
_HISTORY = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:log|show|diff|grep|ls-tree|cat-file|archive)\b")
# `predictions/<id>[/<run>]`, where either segment may be a glob.
_PREDICTIONS = re.compile(r"(?:^|[^\w-])predictions/([^/\s'\"`;|&)\\]*)(?:/([^/\s'\"`;|&)\\]*))?")
_GLOB = re.compile(r"[*?\[{]")

# Where a file tool's target sits in its captured slice, when the slice is JSON.
_PATH_KEYS = ("file_path", "path", "absolute_path", "notebook_path")
# The slice may be cut mid-object, so a target key is also looked for as text.
_PATH_FIELD = re.compile(rf'"(?:{"|".join(_PATH_KEYS)})"\s*:\s*"([^"]+)"')
# codex's apply_patch names each file it touches on a header line.
_PATCH_TARGET = re.compile(r"\*\*\* (?:Add|Update|Delete) File: (\S+)")
# A shell redirection's or tee's target. `2>&1` and `>&2` are not files.
_REDIRECT = re.compile(r"(?<![0-9&<>])>>?\s*(?!&)([^\s;&|<>)]+)")
_TEE = re.compile(r"\btee\s+(?:-a\s+)?([^\s;&|<>)]+)")
# The paths a write may not reach outside the cell's own run directory.
_GUARDED_WRITE = re.compile(r"(?:^|/)(?:data|record)/")


def _strip_exclusions(text: str) -> str:
    for pattern in _EXCLUSIONS:
        text = pattern.sub(" ", text)
    return text


def _touches_tree(call: RetrievalCall) -> bool:
    """Whether the call could have read or written the cell's working tree."""
    tool_class = neutral_tool_class(call.tool)
    return (
        not tool_class.startswith("mcp:")
        and tool_class not in _REMOTE_CLASSES
        and call.tool.lower() not in _PROMPT_TOOLS
    )


@dataclass(frozen=True)
class _OwnRun:
    case_id: str
    event_id: str
    actor_id: str
    run_id: str


def _is_own_run(path: str, own: _OwnRun) -> bool:
    marker = f"predictions/{own.actor_id}/{own.run_id}"
    if marker not in path:
        return False
    prefix = path.split(marker, 1)[0]
    # A path that names its event says whose it is: it must be this cell's.
    return "events/" not in prefix or prefix.endswith(f"{own.case_id}/events/{own.event_id}/")


def _record_reads(text: str, own: _OwnRun, *, cut: bool) -> Iterable[str]:
    """The ``predictions/`` and ``evaluations/`` paths ``text`` names that are not this cell's."""
    yield from _EVALUATIONS.findall(text)
    for match in _PREDICTIONS.finditer(text):
        if cut and match.end() == len(text):
            # The capture cut this slice: a segment that runs to its end may be
            # a prefix of this cell's own run directory.
            continue
        predictor, run = match.group(1), match.group(2)
        named = match.group(0).lstrip("/ \t'\"=")
        if not predictor:
            # The bare directory: in the working tree, the parent of this
            # cell's own, which the hidden tree leaves holding only that; in
            # history, every predictor's committed output.
            if _HISTORY.search(text):
                yield named
            continue
        other_predictor = _GLOB.search(predictor) is not None or predictor != own.actor_id
        other_run = bool(run) and (_GLOB.search(run) is not None or run != own.run_id)
        if other_predictor or other_run:
            yield named


def _write_targets(call: RetrievalCall) -> list[str]:
    """The paths a call wrote to, as far as its slice shows them."""
    text = call.query or ""
    tool_class = neutral_tool_class(call.tool)
    if tool_class == "file-write":
        targets = _PATCH_TARGET.findall(text)
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            targets += [str(parsed[key]) for key in _PATH_KEYS if isinstance(parsed.get(key), str)]
        elif not targets:
            targets += _PATH_FIELD.findall(text)
        return targets
    return [*_REDIRECT.findall(text), *_TEE.findall(text)]


def _guarded_write(path: str, own: _OwnRun) -> bool:
    path = posixpath.normpath(path)
    if path.startswith(("/dev/", "/tmp/")):
        return False
    return _GUARDED_WRITE.search(path) is not None and not _is_own_run(path, own)


def audit_cell_access(
    calls: Sequence[RetrievalCall], *, case_id: str, event_id: str, actor_id: str, run_id: str
) -> list[AccessHit]:
    """Every call in a predict cell's log that named a hidden path or wrote outside its run.

    One hit per (call, kind, path), in call order. The four coordinates name
    the cell's own run directory, the one place under ``predictions/`` it may
    name and the one place under ``data/`` it may write.
    """
    own = _OwnRun(case_id=case_id, event_id=event_id, actor_id=actor_id, run_id=run_id)
    hits: list[AccessHit] = []
    for call in calls:
        if not call.query or not _touches_tree(call):
            continue
        text = _strip_exclusions(call.query)
        found: list[tuple[AccessKind, str]] = [
            (AccessKind.oracle, path) for path in _ORACLE.findall(text)
        ]
        cut = len(call.query) >= QUERY_CAP
        found += [(AccessKind.cell_record, path) for path in _record_reads(text, own, cut=cut)]
        targets = [path.strip("'\"`") for path in _write_targets(call)]
        found += [(AccessKind.write, path) for path in targets if _guarded_write(path, own)]
        hits += [
            AccessHit(kind=kind, tool=call.tool, path=path) for kind, path in dict.fromkeys(found)
        ]
    return hits
