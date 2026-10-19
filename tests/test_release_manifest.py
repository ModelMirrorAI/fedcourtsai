"""The results release manifest (``docs/releases.json``): its rules and the committed file."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from fedcourtsai.releases import (
    RELEASE_MANIFEST_PATH,
    document_problems,
    load_release_manifest,
    tag_commit,
)
from fedcourtsai.schemas import ReleaseManifest

ROOT = Path(__file__).resolve().parents[1]


def _entry(**overrides: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "slug": "ot2026-longconf",
        "label": "Release 1",
        "tag": "results/ot2026-longconf",
        "published": "2026-10-09",
        "covers": "The first conference of the term",
        "summary": "docs/summary.md",
        "audit": "docs/audit.md",
        "data_doi": "10.5281/zenodo.1",
        "code_doi": None,
    }
    entry.update(overrides)
    return entry


def _manifest(*entries: dict[str, Any]) -> ReleaseManifest:
    return ReleaseManifest.model_validate({"schema_version": "1.0", "releases": list(entries)})


@pytest.mark.reads_docs
def test_committed_manifest_is_valid_and_its_documents_exist() -> None:
    manifest = load_release_manifest(ROOT / RELEASE_MANIFEST_PATH)
    assert manifest.releases, "the manifest lists at least the first release"
    assert document_problems(manifest, ROOT) == []


@pytest.mark.parametrize(
    "slug", ["OT2026", "ot2026_longconf", "ot2026/longconf", "-ot2026", "ot2026--x", ""]
)
def test_slug_must_be_url_safe(slug: str) -> None:
    with pytest.raises(ValidationError, match="slug"):
        _manifest(_entry(slug=slug))


@pytest.mark.parametrize("field", ["slug", "tag"])
def test_slug_and_tag_are_unique(field: str) -> None:
    first = _entry(published="2027-01-10", slug="b", tag="results/b")
    second = _entry(slug="a", tag="results/a")
    second[field] = first[field]
    with pytest.raises(ValidationError, match=f"release {field} listed more than once"):
        _manifest(first, second)


def test_releases_are_newest_first() -> None:
    older = _entry()
    newer = _entry(slug="ot2026-merits", tag="results/ot2026-merits", published="2027-07-01")
    assert [r.slug for r in _manifest(newer, older).releases] == ["ot2026-merits", older["slug"]]
    with pytest.raises(ValidationError, match="newest first"):
        _manifest(older, newer)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tag", "prereg/proc-v8"),
        ("summary", "../outside.md"),
        ("summary", "/docs/summary.md"),
        ("audit", "docs/audit.txt"),
        ("data_doi", "https://doi.org/10.5281/zenodo.1"),
        ("code_doi", "zenodo.1"),
    ],
)
def test_entry_fields_are_constrained(field: str, value: str) -> None:
    with pytest.raises(ValidationError, match=field):
        _manifest(_entry(**{field: value}))


def test_unknown_field_is_refused() -> None:
    with pytest.raises(ValidationError, match="extra"):
        _manifest(_entry(doi="10.5281/zenodo.1"))


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "summary.md").write_text("summary\n")
    (tmp_path / "docs" / "audit.md").write_text("audit\n")
    _git(tmp_path, "add", "docs")
    _git(tmp_path, "commit", "-q", "-m", "release documents")
    _git(tmp_path, "tag", "-a", "results/ot2026-longconf", "-m", "release")
    return tmp_path


def test_tagged_entry_is_checked_at_its_tag(repo: Path) -> None:
    assert tag_commit(repo, "results/ot2026-longconf") is not None
    # Gone from the working tree, still at the tag: the site reads the tag.
    (repo / "docs" / "audit.md").unlink()
    assert document_problems(_manifest(_entry()), repo) == []
    missing = _manifest(_entry(summary="docs/elsewhere.md"))
    assert document_problems(missing, repo) == [
        "ot2026-longconf: summary docs/elsewhere.md does not exist at results/ot2026-longconf"
    ]


def test_untagged_entry_is_checked_in_the_working_tree(repo: Path) -> None:
    pending = _entry(slug="ot2026-merits", tag="results/ot2026-merits", published="2027-07-01")
    assert tag_commit(repo, pending["tag"]) is None
    assert document_problems(_manifest(pending), repo) == []
    (repo / "docs" / "audit.md").unlink()
    assert document_problems(_manifest(pending), repo) == [
        "ot2026-merits: audit docs/audit.md does not exist in the working tree "
        "(results/ot2026-merits is not present here)"
    ]
