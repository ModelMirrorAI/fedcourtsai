"""Confine a predict cell's writes under ``data/`` to its own run directory.

A predict cell may write one place in the data tree:
``data/cases/<court>/<docket>/events/<event>/predictions/<predictor_id>/<run_id>/``.
Its prompt says so, and the logged-tool-call audit
(:mod:`fedcourtsai.cell_access`) flags a write it can see elsewhere. Neither
stops the write. The cell's artifact uploads its whole event directory, and the
collect job's add-only union adds any file ``main`` lacks, so a stray file one
level above the run directory, or an edited ``event.yaml`` for an event first
materialized this run, would otherwise reach the ledger; and the steps after the
agent read the case ``record/`` and the committed trees, so an edit there would
change what the stamp and ``validate`` see.

So the data tree is held to a recorded baseline instead. Before the agent
starts, :func:`record_baseline` notes every entry under the data root (after
the hidden trees have been moved out, so they are not in it) and keeps a copy
of each file. After the agent stops, and before anything else reads the tree,
:func:`confine_writes` compares the tree with that baseline and puts back every
difference outside the run directory: an entry the baseline did not hold is
removed (a symlink unlinked, never followed), an entry it held that changed or
went missing is restored from the copy, and a directory the agent created is
removed once it is empty. The run directory itself, and the directories leading
to it, are the cell's own and are left as the agent wrote them.

What this contains is a careless write, not a hostile one. A claude or gemini
agent runs as the runner's own user, so the baseline under the runner temp
directory, the git objects and the project code that runs this check are all
within its reach, as ``SECURITY.md`` records; codex runs as a separate account
that cannot write any of them. The scope is the data tree alone: the engine
state, sidecar logs and watchdog bundle the harness writes at the workspace root
during the run are outside it, and so is the project code.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_MANIFEST = "manifest.json"
_FILES = "files"
_SCHEMA = 1

EntryKind = Literal["file", "link", "other"]


class ConfinementError(Exception):
    """The baseline cannot be recorded or read, so nothing was compared."""


@dataclass(frozen=True)
class Entry:
    """One non-directory entry under the data root, as the baseline saw it."""

    kind: EntryKind
    # A file's content digest, a symlink's target text, or nothing for a
    # socket or FIFO, which the baseline records but cannot copy.
    value: str | None


@dataclass(frozen=True)
class Baseline:
    """What the data root held before the agent started."""

    root: Path
    entries: dict[str, Entry]
    directories: frozenset[str]


@dataclass
class ConfinementReport:
    """What :func:`confine_writes` put back, as data-root-relative POSIX paths."""

    removed: list[str] = field(default_factory=list)
    restored: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.removed or self.restored or self.failed)


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _scan(root: Path) -> tuple[dict[str, Entry], set[str]]:
    """Every entry under ``root``, never following a symlink, split into leaves and directories."""
    entries: dict[str, Entry] = {}
    directories: set[str] = set()
    stack = [root]
    while stack:
        current = stack.pop()
        with os.scandir(current) as listing:
            for item in listing:
                path = Path(item.path)
                relative = path.relative_to(root).as_posix()
                mode = item.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    entries[relative] = Entry("link", os.readlink(path))
                elif stat.S_ISDIR(mode):
                    directories.add(relative)
                    stack.append(path)
                elif stat.S_ISREG(mode):
                    entries[relative] = Entry("file", _digest(path))
                else:
                    entries[relative] = Entry("other", None)
    return entries, directories


def _check_root(root: Path) -> Path:
    absolute = Path(os.path.abspath(root))
    if absolute.is_symlink() or not absolute.is_dir() or absolute.resolve() != absolute:
        raise ConfinementError(f"{root} is not a plain directory reached without a symlink")
    return absolute


def record_baseline(data_root: Path, stash_dir: Path) -> Baseline:
    """Record what ``data_root`` holds and copy its files into ``stash_dir``.

    Refuses a stash that already holds a manifest, so a second call cannot
    overwrite the baseline the first one took.
    """
    root = _check_root(data_root)
    manifest = stash_dir / _MANIFEST
    if manifest.exists():
        raise ConfinementError(f"{manifest} already exists; a baseline is recorded once")
    entries, directories = _scan(root)
    files = stash_dir / _FILES
    for relative, entry in entries.items():
        if entry.kind == "file":
            target = files / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, target)
    payload = {
        "schema": _SCHEMA,
        "root": str(root),
        "entries": {
            relative: {"kind": entry.kind, "value": entry.value}
            for relative, entry in sorted(entries.items())
        },
        "directories": sorted(directories),
    }
    stash_dir.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    return Baseline(root=root, entries=entries, directories=frozenset(directories))


def load_baseline(stash_dir: Path) -> Baseline:
    """Read the baseline :func:`record_baseline` wrote, refusing a malformed one."""
    try:
        raw = json.loads((stash_dir / _MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfinementError(f"no readable baseline under {stash_dir}: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema") != _SCHEMA:
        raise ConfinementError("the baseline manifest is not one this version reads")
    root, entries, directories = raw.get("root"), raw.get("entries"), raw.get("directories")
    if not isinstance(root, str) or not os.path.isabs(root):
        raise ConfinementError("the baseline names its root as an absolute path")
    if not isinstance(entries, dict) or not isinstance(directories, list):
        raise ConfinementError("the baseline lists its entries and directories")
    parsed: dict[str, Entry] = {}
    for relative, item in entries.items():
        kind = item.get("kind") if isinstance(item, dict) else None
        value = item.get("value") if isinstance(item, dict) else None
        if kind not in ("file", "link", "other") or not (value is None or isinstance(value, str)):
            raise ConfinementError(f"the baseline entry {relative!r} is malformed")
        parsed[relative] = Entry(kind, value)
    if not all(isinstance(item, str) for item in directories):
        raise ConfinementError("the baseline lists its directories as strings")
    return Baseline(root=Path(root), entries=parsed, directories=frozenset(directories))


def _within(relative: str, own: str) -> bool:
    return relative == own or relative.startswith(own + "/")


def _leads_to(relative: str, own: str) -> bool:
    return own.startswith(relative + "/")


def _remove(path: Path) -> None:
    if path.is_symlink() or not path.is_dir():
        path.unlink()
    else:
        shutil.rmtree(path)


def _restore(baseline: Baseline, stash_dir: Path, relative: str, entry: Entry) -> None:
    target = baseline.root / relative
    # Whatever stands at the path now — a rewritten file, a directory, a link —
    # goes first, so the copy below writes a fresh entry rather than through it.
    if target.is_symlink() or target.exists():
        _remove(target)
    parent = target.parent
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        _remove(parent)
    parent.mkdir(parents=True, exist_ok=True)
    if parent.resolve() != Path(os.path.abspath(parent)):
        raise OSError(f"{parent} is reached through a symlink")
    if entry.kind == "link" and entry.value is not None:
        os.symlink(entry.value, target)
    elif entry.kind == "file":
        shutil.copy2(stash_dir / _FILES / relative, target)
    else:
        raise OSError("the baseline kept no copy of this entry")


def _remove_added(
    root: Path, entries: dict[str, Entry], baseline: Baseline, own: str, report: ConfinementReport
) -> None:
    # Shallowest first, so a link standing where a directory was is unlinked
    # before anything is restored beneath it. The run directory itself counts
    # as outside when it is not a directory: a link there would carry the
    # cell's later writes, and its upload, somewhere else.
    added = sorted(
        (
            relative
            for relative in entries
            if (relative == own or not _within(relative, own)) and relative not in baseline.entries
        ),
        key=lambda relative: (relative.count("/"), relative),
    )
    for relative in added:
        path = root / relative
        if not (path.is_symlink() or path.exists()):
            continue
        try:
            _remove(path)
        except OSError:
            report.failed.append(relative)
        else:
            report.removed.append(relative)


def _restore_changed(
    entries: dict[str, Entry],
    baseline: Baseline,
    stash_dir: Path,
    own: str,
    report: ConfinementReport,
) -> None:
    for relative, entry in sorted(baseline.entries.items()):
        if _within(relative, own):
            continue
        path = baseline.root / relative
        # Unchanged as scanned, unless a removal above took it with it.
        if entries.get(relative) == entry and (path.is_symlink() or path.exists()):
            continue
        try:
            _restore(baseline, stash_dir, relative, entry)
        except OSError:
            report.failed.append(relative)
        else:
            report.restored.append(relative)


def _remove_created(
    root: Path, directories: set[str], baseline: Baseline, own: str, report: ConfinementReport
) -> None:
    # Deepest first, once whatever was in them is gone. One still holding
    # something the removals could not take is reported with them.
    created = sorted(
        (
            relative
            for relative in directories
            if relative not in baseline.directories
            and not _within(relative, own)
            and not _leads_to(relative, own)
        ),
        key=lambda relative: (-relative.count("/"), relative),
    )
    for relative in created:
        path = root / relative
        if path.is_symlink() or not path.is_dir():
            continue
        try:
            path.rmdir()
        except OSError:
            report.failed.append(relative + "/")
        else:
            report.removed.append(relative + "/")


def confine_writes(data_root: Path, stash_dir: Path, own_run_dir: Path) -> ConfinementReport:
    """Put back every change under ``data_root`` outside ``own_run_dir``.

    ``own_run_dir`` is the cell's ``predictions/<predictor_id>/<run_id>/``
    directory; everything under it is the cell's and is left as written. An
    entry that cannot be put back is listed in ``failed`` and the rest are
    still handled, so the caller can refuse the cell with the full account.
    """
    baseline = load_baseline(stash_dir)
    root = _check_root(data_root)
    if root != baseline.root:
        raise ConfinementError(f"the baseline was recorded for {baseline.root}, not {root}")
    try:
        own = Path(os.path.abspath(own_run_dir)).relative_to(root).as_posix()
    except ValueError as exc:
        raise ConfinementError(f"{own_run_dir} is not under {root}") from exc
    entries, directories = _scan(root)
    report = ConfinementReport()
    _remove_added(root, entries, baseline, own, report)
    _restore_changed(entries, baseline, stash_dir, own, report)
    _remove_created(root, directories, baseline, own, report)
    report.removed.sort()
    report.restored.sort()
    report.failed.sort()
    return report
