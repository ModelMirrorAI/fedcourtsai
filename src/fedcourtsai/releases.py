"""The results release manifest, ``docs/releases.json``, and its checks against the tags.

The manifest lists every results release, newest first. fedcourts.ai reads it
from ``main`` at build time and reads each release's public summary from that
release's own tag, so tagging a release is all it takes for the site to publish
it, and an entry whose tag does not exist yet is shown there as upcoming. The
entry is added in the release's own pull request and promoted with its
documents, before the tag is pushed (docs/pipeline.md, *Tags*).

:class:`~fedcourtsai.schemas.ReleaseManifest` holds the per-entry and
cross-entry rules (URL-safe and unique slugs, unique tags, newest first);
:func:`document_problems` adds the one rule that needs git: each entry's
summary and audit write-up exist where the site will read them.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .schemas import ReleaseEntry, ReleaseManifest

#: Where the manifest lives, relative to the repository root.
RELEASE_MANIFEST_PATH = Path("docs/releases.json")


def load_release_manifest(path: Path) -> ReleaseManifest:
    """The manifest at ``path``, validated."""
    return ReleaseManifest.model_validate_json(path.read_text(encoding="utf-8"))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def tag_commit(root: Path, tag: str) -> str | None:
    """The commit ``tag`` names in the checkout at ``root``, or None where it is absent there."""
    out = _git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}")
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def document_problems(manifest: ReleaseManifest, root: Path) -> list[str]:
    """Each named document that is missing where the site will read it.

    For an entry whose tag is present in the checkout, the summary and the
    audit write-up must exist in the tagged commit's tree, since the site reads
    them there and nowhere else. For an entry whose tag is not present — not
    yet pushed, or not fetched (CI's shallow checkout fetches no tags) — they
    must exist in the working tree, which is where a release's pull request
    adds them before the tag exists.
    """
    problems: list[str] = []
    for entry in manifest.releases:
        problems.extend(_entry_problems(entry, root))
    return problems


def _entry_problems(entry: ReleaseEntry, root: Path) -> list[str]:
    commit = tag_commit(root, entry.tag)
    problems = []
    for role, doc in (("summary", entry.summary), ("audit", entry.audit)):
        if commit is not None:
            if _git(root, "cat-file", "-e", f"{commit}:{doc}").returncode != 0:
                problems.append(f"{entry.slug}: {role} {doc} does not exist at {entry.tag}")
        elif not (root / doc).is_file():
            problems.append(
                f"{entry.slug}: {role} {doc} does not exist in the working tree "
                f"({entry.tag} is not present here)"
            )
    return problems
