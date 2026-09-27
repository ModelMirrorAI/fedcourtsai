#!/usr/bin/env python3
"""Classify a CI run's change into the lane that decides which gate stages run.

The `gate` job in ci.yml runs this right after checkout and skips the stages a
change cannot affect. Three lanes:

- ``data`` — every changed path is committed data (``data/``) or the corpus
  pointer. Lint and types are skipped and the test stage narrows to the tests
  that open those files (``scripts/gate.sh data-tests``); ``validate data`` and
  the schema check, which are what cover data, still run.
- ``docs`` — every changed path is prose: Markdown or an image under
  ``docs/``, a top-level Markdown file, one of the two directory READMEs outside
  ``docs/``, or ``CITATION.cff``. Lint and types are skipped and the test stage
  narrows to the tests that open those files (``scripts/gate.sh docs-tests``).
  The top-level files agents read as instructions or policy (``AGENTS.md``,
  ``CLAUDE.md``, ``SECURITY.md``, and the context-file names ``GEMINI.md`` and
  ``MEMORY.md``) are not prose here.
- ``code`` — everything else, and the answer to every doubt: an empty diff, a
  mixed diff, a path this module does not recognise, or a diff it could not
  compute. The full gate runs.

A wrong ``data`` or ``docs`` answer passes silently — a skipped step reports
success and `gate` is a required check — so the lanes are allow-lists and every
failure path lands on ``code``. Prompts, configs, schemas, workflows, scripts,
tests and source are never prose or data here, whatever their extension, and
neither is a symlink or a submodule entry anywhere.

ci.yml runs the *base's* copy of this file (``HEAD^1``), never the change's
own, so a change cannot pick its own lane; a change to this file is itself
``code``, and so gets the full gate under the trusted version.

Which diff: on ``pull_request`` the checkout is GitHub's merge ref, whose first
parent is the base tip it was computed against, so ``HEAD^1..HEAD`` is exactly
what the PR changes in the tree the gate tests — the same set the ``paths`` job
reaches through the three-dot form. On ``push`` the diff is ``before..after``,
which a depth-2 checkout can compute only when ``before`` is ``HEAD``'s first
parent: a single commit, or a merge landed through a PR. A multi-commit push,
a branch creation, or a force push is not that, and is ``code``.

Standard library only, so it needs no environment. Usage::

    python3 scripts/ci_lane.py --event pull_request
    python3 scripts/ci_lane.py --event push --before <sha>

prints ``lane=<lane>`` (append it to ``$GITHUB_OUTPUT``) and writes the
reason to stderr.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import PurePosixPath

DATA = "data"
DOCS = "docs"
CODE = "code"

# The corpus pointer is data in every sense the gate cares about: the writer
# lanes commit it beside data/, and `scripts/gate.sh data` (corpus-status) is
# the stage that reads it.
DATA_FILES = frozenset({"corpus/corpus.db.ref"})
DOCS_FILES = frozenset({"CITATION.cff", "corpus/README.md", "metrics/README.md"})
# Top-level Markdown that is operative rather than prose: agent instructions,
# the security policy, and the names a gemini cell loads as context.
NOT_DOCS = frozenset({"AGENTS.md", "CLAUDE.md", "GEMINI.md", "MEMORY.md", "SECURITY.md"})
# What may live under docs/ and still be prose. Anything else there (a script,
# a config a docs tool reads) is code until someone decides otherwise.
DOCS_SUFFIXES = frozenset({".md", ".png", ".svg"})
# git's modes for a symlink and a submodule (gitlink): neither is a file whose
# content the lanes can reason about.
OPAQUE_MODES = frozenset({"120000", "160000"})


def _is_data(path: str) -> bool:
    return path.startswith("data/") or path in DATA_FILES


def _is_docs(path: str) -> bool:
    pure = PurePosixPath(path)
    if path in DOCS_FILES:
        return True
    if path.startswith("docs/"):
        return pure.suffix.lower() in DOCS_SUFFIXES
    # Top-level Markdown only: a README.md or prompt deeper in the tree may be
    # read by code (.github/prompts/ is the cell contract) and is not prose here.
    return len(pure.parts) == 1 and pure.suffix == ".md" and path not in NOT_DOCS


def classify(paths: Iterable[str]) -> tuple[str, str]:
    """Return ``(lane, reason)`` for a set of changed repository paths."""
    changed = sorted({p.strip() for p in paths if p.strip()})
    if not changed:
        return CODE, "no changed paths; running the full gate"
    for path in changed:
        # A path that tries to climb out of the tree, or an absolute one, is
        # not a path git would print; refuse to reason about it.
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts:
            return CODE, f"unexpected path {path!r}; running the full gate"
    if all(_is_data(p) for p in changed):
        return DATA, f"{len(changed)} path(s), all data"
    if all(_is_docs(p) for p in changed):
        return DOCS, f"{len(changed)} path(s), all prose"
    other = [p for p in changed if not _is_data(p) and not _is_docs(p)]
    if other:
        return CODE, f"{other[0]} is neither data nor prose; running the full gate"
    return CODE, "data and prose together; running the full gate"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def changed_paths(event: str, before: str | None) -> list[str]:
    """The paths the run's change touches, per the module docstring.

    Raises ``ValueError`` whenever the diff is not the one the lane may trust.
    """
    parents = _git("rev-list", "--parents", "-n", "1", "HEAD").split()
    if event == "pull_request":
        if len(parents) != 3:
            raise ValueError("HEAD is not a two-parent merge ref")
    elif event == "push":
        if not before or set(before) == {"0"}:
            raise ValueError("push has no prior tip (branch creation)")
        if len(parents) < 2 or parents[1] != before:
            raise ValueError("push's prior tip is not HEAD's first parent")
    else:
        raise ValueError(f"event {event!r} has no lane")
    return parse_raw(_git("diff", "--no-renames", "--raw", "-z", "HEAD^1", "HEAD"))


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--event", required=True)
    parser.add_argument("--before", default=None)
    args = parser.parse_args(argv)
    try:
        paths = changed_paths(args.event, args.before)
    except (ValueError, subprocess.CalledProcessError, OSError) as exc:
        lane, reason = CODE, f"diff not computable ({exc}); running the full gate"
    else:
        lane, reason = classify(paths)
    print(f"lane={lane}")
    print(f"ci-lane: {lane} — {reason}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
