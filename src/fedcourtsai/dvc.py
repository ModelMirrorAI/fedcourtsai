"""Offline consistency checks for the repository's DVC metadata.

CI runs without the DVC remote or its credentials — the gate stays offline and
fast (see ``docs/data-pipeline.md``) — so it cannot fetch the corpus blob to
diff it against the remote. What it *can* verify, deterministically and offline,
is that the committed DVC bookkeeping is internally coherent:

* every DVC-tracked data output (a ``*.dvc`` pointer such as
  ``corpus/corpus.db.dvc``, or a cached ``dvc.yaml`` stage output) is a
  well-formed pointer that is **gitignored and absent from git**, so the
  multi-hundred-megabyte corpus blob can never slip into the repo; and
* every pipeline output the ``dvc.yaml`` declares as git-tracked (``cache:
  false`` — the ``metrics/`` roll-ups) is actually committed.

``fedcourts dvc-status`` runs these checks. The online side — ``dvc status``
against the remote, ``dvc pull``/``push`` — belongs to the data workflows
(``run-pull``'s writer jobs), which hold the remote credentials.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DVC_POINTER_SUFFIX = ".dvc"
# Directories never worth scanning for pointer files.
_SKIP_DIRS = frozenset({".git", ".venv", ".dvc", "node_modules", "__pycache__"})


@dataclass(frozen=True)
class DvcOut:
    """One output DVC tracks, resolved to a repo-relative path.

    ``cached`` is True for blobs DVC stores in its cache/remote (the corpus, any
    cached stage output) — these must stay out of git — and False for outputs
    DVC leaves in the working tree for git to version (``cache: false`` metrics
    and plots).
    """

    path: Path
    cached: bool
    source: Path


def _as_entries(spec: Any) -> list[Any]:
    """Normalize a DVC ``outs``/``metrics``/``plots`` block to a list of entries."""
    if spec is None:
        return []
    if isinstance(spec, list):
        return spec
    return [spec]


def _entry_path_and_cache(entry: Any) -> tuple[str | None, bool]:
    """Pull the path and cache flag from one out entry (string or ``{path: opts}``)."""
    if isinstance(entry, str):
        return entry, True
    if isinstance(entry, dict) and len(entry) == 1:
        ((path, opts),) = entry.items()
        cache = True
        if isinstance(opts, dict):
            cache = bool(opts.get("cache", True))
        return str(path), cache
    return None, True


def _parse_pointer(pointer: Path, repo_root: Path) -> tuple[list[DvcOut], list[str]]:
    """Read a ``*.dvc`` pointer file into its outputs, collecting any defects."""
    outs: list[DvcOut] = []
    errors: list[str] = []
    rel_source = pointer.relative_to(repo_root)
    try:
        doc = yaml.safe_load(pointer.read_text())
    except (OSError, yaml.YAMLError) as exc:
        return [], [f"{rel_source}: unreadable DVC pointer ({exc})"]
    entries = _as_entries((doc or {}).get("outs"))
    if not entries:
        return [], [f"{rel_source}: DVC pointer declares no outs"]
    for entry in entries:
        if not isinstance(entry, dict) or "path" not in entry:
            errors.append(f"{rel_source}: malformed out entry (missing path)")
            continue
        if "md5" not in entry and "hash" not in entry:
            errors.append(f"{rel_source}: out '{entry['path']}' has no checksum (md5/hash)")
        # Pointer paths are relative to the pointer file's directory.
        resolved = (pointer.parent / str(entry["path"])).resolve().relative_to(repo_root.resolve())
        outs.append(DvcOut(path=resolved, cached=bool(entry.get("cache", True)), source=rel_source))
    return outs, errors


def _parse_pipeline(dvc_yaml: Path, repo_root: Path) -> tuple[list[DvcOut], list[str]]:
    """Read ``dvc.yaml`` stage outputs (paths are relative to the file's directory)."""
    outs: list[DvcOut] = []
    errors: list[str] = []
    rel_source = dvc_yaml.relative_to(repo_root)
    try:
        doc = yaml.safe_load(dvc_yaml.read_text())
    except (OSError, yaml.YAMLError) as exc:
        return [], [f"{rel_source}: unreadable pipeline file ({exc})"]
    stages = (doc or {}).get("stages") or {}
    if not isinstance(stages, dict):
        return [], [f"{rel_source}: 'stages' must be a mapping"]
    for name, stage in stages.items():
        if not isinstance(stage, dict) or not stage.get("cmd"):
            errors.append(f"{rel_source}: stage '{name}' has no cmd")
            continue
        for block in ("outs", "metrics", "plots"):
            for entry in _as_entries(stage.get(block)):
                path, cached = _entry_path_and_cache(entry)
                if path is None:
                    errors.append(f"{rel_source}: stage '{name}' has a malformed {block} entry")
                    continue
                resolved = (dvc_yaml.parent / path).resolve().relative_to(repo_root.resolve())
                outs.append(DvcOut(path=resolved, cached=cached, source=rel_source))
    return outs, errors


def collect_outs(repo_root: Path) -> tuple[list[DvcOut], list[str]]:
    """Gather every DVC-declared output in the repo plus any malformed-metadata errors."""
    outs: list[DvcOut] = []
    errors: list[str] = []
    for pointer in sorted(repo_root.rglob(f"*{DVC_POINTER_SUFFIX}")):
        if not pointer.is_file() or _SKIP_DIRS.intersection(pointer.parts):
            continue
        p_outs, p_errors = _parse_pointer(pointer, repo_root)
        outs.extend(p_outs)
        errors.extend(p_errors)
    dvc_yaml = repo_root / "dvc.yaml"
    if dvc_yaml.is_file():
        y_outs, y_errors = _parse_pipeline(dvc_yaml, repo_root)
        outs.extend(y_outs)
        errors.extend(y_errors)
    return outs, errors


def check_state(
    repo_root: Path,
    *,
    is_tracked: Callable[[Path], bool],
    is_ignored: Callable[[Path], bool],
) -> list[str]:
    """Return human-readable problems with the repo's DVC metadata (empty = clean).

    ``is_tracked`` / ``is_ignored`` answer git questions about a repo-relative
    path; the CLI wires them to git, and tests inject fakes so the core logic
    stays pure and offline.
    """
    outs, errors = collect_outs(repo_root)
    for out in sorted(outs, key=lambda o: str(o.path)):
        problem = (
            _cached_problem(out, is_tracked, is_ignored)
            if out.cached
            else _git_tracked_problem(out, repo_root, is_tracked)
        )
        if problem is not None:
            errors.append(problem)
    return errors


def _cached_problem(
    out: DvcOut,
    is_tracked: Callable[[Path], bool],
    is_ignored: Callable[[Path], bool],
) -> str | None:
    """Defect for a cached blob: it lives in the DVC remote only, never in git."""
    if is_tracked(out.path):
        return (
            f"{out.path}: DVC-tracked blob is also committed to git "
            f"(declared in {out.source}); it must live only in the DVC remote"
        )
    if not is_ignored(out.path):
        return (
            f"{out.path}: DVC-tracked output is not gitignored "
            f"(declared in {out.source}); it could be committed by accident"
        )
    return None


def _git_tracked_problem(
    out: DvcOut,
    repo_root: Path,
    is_tracked: Callable[[Path], bool],
) -> str | None:
    """Defect for a cache:false output (the metrics roll-ups): git must version it."""
    if not (repo_root / out.path).is_file():
        return (
            f"{out.path}: pipeline output is missing "
            f"(declared cache:false in {out.source}); run its stage and commit it"
        )
    if not is_tracked(out.path):
        return (
            f"{out.path}: pipeline output is not committed to git "
            f"(declared cache:false in {out.source})"
        )
    return None


def _git_tracked_files(repo_root: Path) -> set[Path]:
    """Repo-relative paths git currently tracks."""
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {Path(name) for name in proc.stdout.split("\0") if name}


def _git_is_ignored(repo_root: Path, path: Path) -> bool:
    """Whether git would ignore ``path`` (works even if the file is absent)."""
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-q", "--", str(path)],
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def git_checkers(repo_root: Path) -> tuple[Callable[[Path], bool], Callable[[Path], bool]]:
    """Build ``(is_tracked, is_ignored)`` backed by git for ``check_state``."""
    tracked = _git_tracked_files(repo_root)

    def is_tracked(path: Path) -> bool:
        return path in tracked

    def is_ignored(path: Path) -> bool:
        return _git_is_ignored(repo_root, path)

    return is_tracked, is_ignored


def tracked_paths(outs: Iterable[DvcOut]) -> list[Path]:
    """The data outputs DVC keeps out of git, for a one-line status summary."""
    return sorted({o.path for o in outs if o.cached})
