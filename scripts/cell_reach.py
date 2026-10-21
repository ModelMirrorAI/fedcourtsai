#!/usr/bin/env python3
"""Classify a promotion batch by whether it can reach a cell.

The promotion gate's evidence is an integration suite at the batch's head. The
paid ``gate`` suite runs real engines — an ``engine-smoke`` cell and an
``engine-actions-smoke`` boot probe per engine; ``offline-gate`` is the same
suite without those six legs. The engine legs are the only evidence that a real
cell still runs in the production posture at the head, so they are owed by any
batch that could change what a cell runs or how, and by no other. Two verdicts:

- ``inert`` — every changed path is on the allow-list below: prose, data,
  tests, and the gate, promotion, reporting and spend machinery no cell runs.
  The promotion train dispatches ``offline-gate`` for such a batch and the
  promotion gate accepts it (``PROMOTION_SKIP_SMOKE``).
- ``engine`` — everything else, and the answer to every doubt: an empty diff,
  a path this module does not recognise, a symlink or submodule, any file or
  directory name an agent reads as instructions or config (``CLAUDE.md``,
  ``AGENTS.md``, ``.claude/``, ``.github/`` and the rest of the path jail's set,
  at any depth), or a diff it could not compute. The full ``gate`` suite is
  owed.

A wrong ``inert`` answer merges a batch with no real-engine evidence, so the
verdict is an allow-list and every failure path lands on ``engine``. Engine
relevance is what is left off it: the cell workflows and their composites, the
pinned engine CLIs (all under ``.github/``), the prompts, the predictor and
evaluator configs, ``pyproject.toml`` and ``uv.lock``, the schemas, every
``src/`` module not named in :data:`INERT_SOURCE` — ``pricing.py``'s default
models, the provisioning, retrieval and MCP code, and ``cli.py`` itself among
them — and every script not named in :data:`INERT_FILES`. A path new to the
tree is ``engine`` until someone lists it here.

An inert ``src/`` module is one no module but ``cli.py`` and the other listed
modules imports, and that no script or workflow names: ``tests/test_cell_reach.py``
pins both. ``cli.py`` is engine-relevant, and none of the commands a cell
workflow runs reaches a listed module; the round planners' spend arithmetic
(``spend``, ``planning_rates``, ``review_hold``) is left off for that reason,
since ``predict-matrix`` and ``evaluate-matrix`` decide with it which cells
exist. ``cli.py`` imports every module at load, so a module that
fails to import breaks every command, cells included; the offline suite runs
those commands and catches that without an engine.

Which diff: the batch is the three-dot diff ``<base>...<head>``, what the head
changed since its merge-base with ``main``, so the writer lanes' commits to
``main`` are never read as the batch's. The promotion train and ci.yml's
``promotion-gate`` job both extract ``main``'s copy of this file from
``origin/main`` and run that, never the candidate's, so a batch cannot grade
itself inert; a ``main`` that has no copy yet leaves the gate strict.

Standard library only, so it needs no environment. Usage::

    python3 -I -S scripts/cell_reach.py --base origin/main --head <sha>

prints ``reach=<verdict>`` and writes the reason to stderr. Exit 0 whatever
the verdict.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import PurePosixPath

INERT = "inert"
ENGINE = "engine"

# Prose, on scripts/ci_lane.py's docs lane: Markdown or an image under docs/,
# a top-level Markdown file (never an agent instruction file — those are
# refused first), the two directory READMEs outside docs/, and CITATION.cff.
# A cell may read this prose, as the prompts point it to docs/; what it cannot
# do is change whether an engine runs in the production posture, which is the
# only thing the engine legs test.
DOCS_FILES = frozenset({"CITATION.cff", "corpus/README.md", "metrics/README.md"})
NOT_DOCS = frozenset({"SECURITY.md"})
DOCS_SUFFIXES = frozenset({".md", ".png", ".svg"})

# Whole trees no cell runs: committed data and derived metrics (the writer
# lanes' paths), the test suite, and the corpus-check lane's scripts. The
# corpus pointer is not among them: the engine legs read the corpus it names.
INERT_PREFIXES = ("data/", "metrics/", "tests/", "scripts/checks/")

# Single files no cell runs: the gate and lane machinery, and the configs of
# the promotion train and the corpus-check lane.
INERT_FILES = frozenset(
    {
        "scripts/cell_reach.py",
        "scripts/ci_lane.py",
        "scripts/gate.sh",
        "scripts/merge-when-green.sh",
        "scripts/promotion-gate.sh",
        "config/corpus-check.yaml",
        "config/promotion-train.yaml",
    }
)

# src/fedcourtsai/ modules no cell path imports: the promotion gate and train
# with the predict chain's dispatch decision, the settings checks, and the
# metrics, reporting and public-update writers. Every other module is
# engine-relevant.
INERT_SOURCE = frozenset(
    {
        "buttondown",
        "claim_metrics",
        "contexts_due",
        "corpus_check",
        "dataset_export",
        "dispatch_chain",
        "environment_checks",
        "metrics_refresh",
        "ops",
        "promotion_body",
        "promotion_train",
        "public_update",
        "registry_gate",
        "release_sensitivity",
        "required_checks",
        "ruleset_checks",
    }
)
SOURCE_DIR = "src/fedcourtsai/"

# File and directory names an agent reads as instructions, context or config,
# lower-cased and matched at any depth: the path jail's own sets
# (fedcourtsai.collect.AGENT_CONTEXT_FILENAMES / AGENT_CONFIG_DIRS), copied
# because this script runs with no environment; a test pins them equal. An
# engine running in a cell may load one, so a path that names one can reach a
# cell wherever it sits.
AGENT_CONTEXT_FILENAMES = frozenset(
    {
        "claude.md",
        "claude.local.md",
        "agents.md",
        "agents.override.md",
        "agent.md",
        "codex.md",
        ".mcp.json",
        "gemini.md",
        "memory.md",
        ".cursorrules",
        ".clinerules",
        ".windsurfrules",
        "copilot-instructions.md",
    }
)
AGENT_CONFIG_DIRS = frozenset(
    {
        ".claude",
        ".codex",
        ".gemini",
        ".agents",
        ".cursor",
        ".clinerules",
        ".windsurf",
        ".roo",
        ".kiro",
        ".continue",
        ".junie",
        ".github",
    }
)
# git's modes for a symlink and a submodule (gitlink): neither is a file whose
# content the verdict can reason about.
OPAQUE_MODES = frozenset({"120000", "160000"})
# What --base and --head may be: a ref name or a SHA, never an option.
_REVISION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")


def _is_agent_context(path: str) -> bool:
    parts = [part.lower() for part in path.split("/") if part]
    return bool(parts) and (
        parts[-1] in AGENT_CONTEXT_FILENAMES or any(p in AGENT_CONFIG_DIRS for p in parts[:-1])
    )


def _is_docs(path: str) -> bool:
    pure = PurePosixPath(path)
    if path in DOCS_FILES:
        return True
    if path.startswith("docs/"):
        return pure.suffix.lower() in DOCS_SUFFIXES
    return len(pure.parts) == 1 and pure.suffix == ".md" and path not in NOT_DOCS


def _is_inert_source(path: str) -> bool:
    if not path.startswith(SOURCE_DIR):
        return False
    pure = PurePosixPath(path[len(SOURCE_DIR) :])
    return len(pure.parts) == 1 and pure.suffix == ".py" and pure.stem in INERT_SOURCE


def is_inert(path: str) -> bool:
    """Whether ``path`` alone is on the allow-list (agent context is refused first)."""
    return (
        path in INERT_FILES
        or path.startswith(INERT_PREFIXES)
        or _is_docs(path)
        or _is_inert_source(path)
    )


def classify(paths: Iterable[str]) -> tuple[str, str]:
    """Return ``(verdict, reason)`` for a batch's changed repository paths."""
    changed = sorted({p for p in paths if p})
    if not changed:
        return ENGINE, "no changed paths; the engine legs are owed"
    for path in changed:
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts or path != path.strip():
            return ENGINE, f"unexpected path {path!r}; the engine legs are owed"
        if _is_agent_context(path):
            return ENGINE, f"{path!r} names an agent instruction or config path"
    reaching = [p for p in changed if not is_inert(p)]
    if reaching:
        more = f" and {len(reaching) - 1} more" if len(reaching) > 1 else ""
        # repr, never the raw name: the reason reaches a workflow log, where a
        # name carrying a newline could start a line the runner reads as a
        # workflow command.
        return ENGINE, f"{reaching[0]!r}{more} can reach a cell"
    return INERT, f"{len(changed)} path(s), none of which a cell runs"


def parse_raw(out: str) -> list[str]:
    """Paths from ``git diff --raw -z`` output, refusing opaque entries.

    Each record is ``:<old mode> <new mode> <old sha> <new sha> <status>``,
    NUL, then the one path (renames are off). Raises ``ValueError`` on a
    symlink or submodule on either side, or on anything unparseable.
    """
    fields = out.split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    if len(fields) % 2:
        raise ValueError("unparseable diff")
    paths = []
    for meta, path in zip(fields[::2], fields[1::2], strict=True):
        parts = meta[1:].split()
        if not meta.startswith(":") or len(parts) != 5:
            raise ValueError(f"unparseable diff record {meta!r}")
        if OPAQUE_MODES & {parts[0], parts[1]}:
            raise ValueError(f"{path} is a symlink or submodule")
        paths.append(path)
    return paths


def changed_paths(base: str, head: str) -> list[str]:
    """The paths ``head`` changed since its merge-base with ``base``.

    Raises ``ValueError`` on a revision that is not a plain ref or SHA, and
    ``subprocess.CalledProcessError`` when git cannot compute the diff.
    """
    for revision in (base, head):
        if not _REVISION.fullmatch(revision) or ".." in revision:
            raise ValueError(f"{revision!r} is not a ref or SHA")
    out = subprocess.run(
        ["git", "diff", "--no-renames", "--raw", "-z", f"{base}...{head}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return parse_raw(out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args(argv)
    try:
        paths = changed_paths(args.base, args.head)
    except (ValueError, subprocess.CalledProcessError, OSError) as exc:
        verdict, reason = ENGINE, f"diff not computable ({exc}); the engine legs are owed"
    else:
        verdict, reason = classify(paths)
    print(f"reach={verdict}")
    print(f"cell-reach: {verdict} — {reason}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
