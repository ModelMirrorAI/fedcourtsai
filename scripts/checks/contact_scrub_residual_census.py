"""Census the contact-detail residuals the staged-text scrub leaves, before and after a change.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/contact_scrub_residual_census.py --base <sha>
    ```

it walks every live-slice SCOTUS row, reads the row's stored documents and its
latest live snapshot (from the content store under the corpus split), and runs
the staged-text contact scrub on the snapshot's reading as provisioning does
(`provision.staged_scrub`): once with the scrub as it stands at ``--base``
(loaded with `git show <base>:src/fedcourtsai/pipeline/documents.py`), once
with the checkout's. Over each scrubbed text it runs the checkout's residual
detector (`pipeline.documents.residual_shape_matches`) on four regions: the
document's opening (`OPENING_WINDOW_CHARS`), its closing (the same number of
characters at the end, not overlapping the opening), `flagged` (either of the
two, which is what the manifest's `contact_scrubbed` reads) and the whole
text. As a
comparison population it runs the checkout's shape pass and the detector over
the documents of rows read as represented, where no scrub runs: a flag there
is either a represented filer's professional detail the shape pass misses or
a detector false positive, so it bounds both together.

It writes nothing, and reports to the file named by `CHECK_SUMMARY` counts and
case identifiers only, never stored text or a contact value: the summary is
posted publicly (docs/corpus-check.md). Without ``--base`` (or where git cannot
read the base, as in a shallow checkout) it reports the checkout's scrub alone.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus and the content store addressed.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline import documents as current
from fedcourtsai.pipeline.prefetch import prefetch_by_case

_BASE_MODULE = "fedcourtsai.pipeline._census_base_documents"


def _base_module(sha: str) -> ModuleType | None:
    """The scrub module as it stood at ``sha``, or None where git cannot read it."""
    shown = subprocess.run(
        ["git", "show", f"{sha}:src/fedcourtsai/pipeline/documents.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    if shown.returncode != 0:
        return None
    path = Path(tempfile.mkdtemp()) / "documents.py"
    path.write_text(shown.stdout, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(_BASE_MODULE, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[_BASE_MODULE] = module
    spec.loader.exec_module(module)
    return module


def _staged(module: Any, text: str, values: tuple[str, ...], sides: tuple[str, ...]) -> Any:
    """The scrub provisioning stages a document through (`provision.staged_scrub`)."""
    if not sides:
        return None
    done = module.scrub_contact_details(
        text, values, shape=any(side != module.OTHER_LIST for side in sides)
    )
    return done if done.passes else None


def _regions(text: str) -> dict[str, set[str]]:
    """The residual shapes found in each region of ``text``."""
    window = current.OPENING_WINDOW_CHARS
    closing_start = max(window, len(text) - window)
    return {
        "opening": {name for name, _ in current.residual_shape_matches(text, 0, window)},
        "closing": {name for name, _ in current.residual_shape_matches(text, closing_start)},
        "flagged": {name for name, _ in current.contact_residual_matches(text)},
        "whole": {name for name, _ in current.residual_shape_matches(text)},
    }


class _Tally:
    """Documents, cases and shapes flagged per region."""

    def __init__(self) -> None:
        self.docs: Counter[str] = Counter()
        self.cases: dict[str, set[str]] = {}
        self.shapes: dict[str, Counter[str]] = {}
        self.kinds: dict[str, Counter[str]] = {}

    def add(self, case_id: str, kind: str, regions: dict[str, set[str]]) -> None:
        for region, shapes in regions.items():
            if not shapes:
                continue
            self.docs[region] += 1
            self.cases.setdefault(region, set()).add(case_id)
            self.shapes.setdefault(region, Counter()).update(shapes)
            self.kinds.setdefault(region, Counter())[kind] += 1

    def lines(self, label: str, of: int) -> list[str]:
        out = []
        for region in ("opening", "closing", "flagged", "whole"):
            out.append(
                f"- {label}, {region}: {self.docs[region]} of {of} documents on "
                f"{len(self.cases.get(region, ()))} cases; by shape "
                f"{dict(sorted(self.shapes.get(region, Counter()).items()))}; by kind "
                f"{dict(sorted(self.kinds.get(region, Counter()).items()))}"
            )
        return out


def main() -> int:  # noqa: PLR0912, PLR0915 - one linear census
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", help="the commit whose scrub to compare against")
    parser.add_argument(
        "--list-cases", action="store_true", help="name the cases flagged on the opening"
    )
    args = parser.parse_args()
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    base = _base_module(args.base) if args.base else None
    settings = get_settings()
    counts: Counter[str] = Counter()
    before, after, represented = _Tally(), _Tally(), _Tally()
    spans_more = spans_fewer = docs_more = docs_fewer = 0
    db_path = corpus.corpus_db_path(settings.corpus_root)
    with corpus.connect_readonly(db_path, backend=settings.corpus_backend) as conn:
        rows = [r for r in corpus.iter_rows(conn, court="scotus") if corpus.is_live_slice(r)]
        counts["live-slice rows"] = len(rows)

        def fetch(case_id: str) -> tuple[list[corpus.CaseDocument], Any]:
            docs = corpus.documents_for_case(conn, case_id)
            return docs, corpus.latest_live_snapshot(conn, case_id) if docs else None

        ids = [r.case_id for r in rows]
        with prefetch_by_case(ids, fetch, thread_name_prefix="scrub-census") as fetched:
            for case_id, (docs, snapshot) in fetched:
                if not docs:
                    continue
                counts["cases with documents"] += 1
                counts["documents"] += len(docs)
                if snapshot is None:
                    counts["cases with documents and no live snapshot"] += 1
                    counts["documents with no live snapshot"] += len(docs)
                    continue
                payload = snapshot[1]
                sides = current.unrepresented_sides(payload)
                if not sides:
                    counts["represented cases"] += 1
                    for doc in docs:
                        counts["represented documents"] += 1
                        done = current.scrub_contact_details(doc.text)
                        represented.add(case_id, doc.kind, _regions(done.text))
                    continue
                counts["cases read as self-represented"] += 1
                party = any(side != current.OTHER_LIST for side in sides)
                counts["  on a party side" if party else "  on the Other list alone"] += 1
                values = current.party_contact_values(payload, sides)
                for doc in docs:
                    now = _staged(current, doc.text, values, sides)
                    if now is None:
                        counts["documents the scrub does not run over"] += 1
                        continue
                    counts["documents scrubbed"] += 1
                    if current.SCRUB_PASS_SHAPE not in now.passes:
                        counts["documents scrubbed by the value pass alone"] += 1
                        continue
                    counts["documents shape-scrubbed"] += 1
                    if not now.clean:
                        counts["documents now recorded contact_scrubbed: false"] += 1
                    after.add(case_id, doc.kind, _regions(now.text))
                    if base is None:
                        continue
                    old_sides = base.unrepresented_sides(payload)
                    old_values = base.party_contact_values(payload, old_sides)
                    then = _staged(base, doc.text, old_values, old_sides)
                    if then is None or base.SCRUB_PASS_SHAPE not in then.passes:
                        counts["shape-scrubbed now, not at base"] += 1
                        continue
                    before.add(case_id, doc.kind, _regions(then.text))
                    if now.replacements > then.replacements:
                        docs_more += 1
                        spans_more += now.replacements - then.replacements
                    elif now.replacements < then.replacements:
                        docs_fewer += 1
                        spans_fewer += then.replacements - now.replacements
    shaped = counts["documents shape-scrubbed"]
    lines = ["Contact-scrub residual census (counts and case identifiers only).", ""]
    lines += [f"- {key}: {value}" for key, value in counts.items()]
    lines.append("")
    if base is not None:
        lines += before.lines(f"residual after the scrub at {args.base}", shaped)
        lines.append(
            f"- the checkout's scrub withholds {spans_more} more span(s) across "
            f"{docs_more} document(s) and {spans_fewer} fewer across {docs_fewer} "
            f"(a wider span merging two), net {spans_more - spans_fewer:+d}"
        )
    else:
        lines.append("- no base scrub read; the checkout's scrub alone")
    lines += after.lines("residual after the checkout's scrub", shaped)
    lines += represented.lines(
        "represented dockets after the shape pass (miss or false positive)",
        counts["represented documents"],
    )
    if args.list_cases:
        for region in ("opening", "closing", "flagged"):
            ids_found = " ".join(sorted(after.cases.get(region, ())))
            lines.append(
                f"- cases with a residual after the checkout's scrub, {region}: {ids_found}"
            )
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
