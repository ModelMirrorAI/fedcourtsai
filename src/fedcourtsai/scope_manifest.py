"""Build the published prediction-scope manifest for the already-public case set.

``data/scope/scope.json`` records, for every docket that already has a committed
directory under ``data/cases``, the pipeline's prediction-scope decision:
whether it is in the gate (``predict_eligible``), whether the reconcile latched
it out (``predict_excluded``), the shared exclusion reason, and the sampling
weight. It is the transparency counterpart of the scope reconcile — the reconcile
*decides* scope in the corpus; this *publishes* that decision for the cases the
repository already discloses.

The one load-bearing invariant: the manifest is enumerated from the committed
``data/cases`` directory tree **alone** (:func:`_public_case_ids`), never from a
corpus scan (``iter_rows`` / ``iter_tracked_cases``). The corpus is consulted
only by exact ``case_id`` lookup for cases already on that public list. So the
manifest cannot enumerate the broader ingested corpus — the compilation-extent
boundary the project holds deliberately. Adding a corpus-driven enumeration here
would breach that boundary; do not.
"""

from __future__ import annotations

from pathlib import Path

from . import corpus
from .schemas import ScopeManifest, ScopeManifestEntry


def _public_case_ids(data_root: Path) -> list[str]:
    """The ``<court>/<docket>`` ids that already have a committed case directory.

    Enumerates the git-visible public set only: the numeric docket directories
    under ``data/cases/<court>/``. This is the sole enumeration source for the
    manifest — it never reads the corpus, so it cannot disclose ingested-but-
    unpublished dockets (see the module docstring).
    """
    cases_root = data_root / "cases"
    if not cases_root.is_dir():
        return []
    case_ids: list[str] = []
    for court_dir in sorted(p for p in cases_root.iterdir() if p.is_dir()):
        for docket_dir in sorted(p for p in court_dir.iterdir() if p.is_dir()):
            if docket_dir.name.isdigit():
                case_ids.append(f"{court_dir.name}/{docket_dir.name}")
    return case_ids


def build_scope_manifest(*, data_root: Path, corpus_db_path: Path) -> ScopeManifest:
    """Roll the public case set's prediction-scope decision into a manifest.

    Deterministic and offline: enumerates the committed public cases, then looks
    each one up in the corpus for its scope columns. Returns a ``skipped``
    manifest (empty entries) when the corpus is absent, so it is safe to
    regenerate before a corpus pull. Cases on the public list but missing from
    the corpus are omitted rather than guessed at.
    """
    case_ids = _public_case_ids(data_root)
    if not corpus_db_path.exists():
        return ScopeManifest(skipped=True)

    entries: list[ScopeManifestEntry] = []
    # Pinned to the local pulled file: like the statpack/leaderboard generators
    # this is a pure function of the corpus, run after a full pull — never the
    # ranged/casestore read seams the predict/evaluate plan jobs use.
    with corpus.connect_readonly(corpus_db_path, backend="local") as conn:
        for case_id in case_ids:
            row = corpus.get_row(conn, case_id)
            if row is None:
                continue
            reason = corpus.out_of_scope_reason_full(conn, row)
            entries.append(
                ScopeManifestEntry(
                    case_id=case_id,
                    predict_eligible=row.predict_eligible,
                    predict_excluded=row.predict_excluded,
                    out_of_scope_reason=reason,
                    sample_weight=row.sample_weight,
                )
            )
    entries.sort(key=lambda e: e.case_id)
    return ScopeManifest(
        cases=len(entries),
        eligible=sum(1 for e in entries if e.predict_eligible),
        excluded=sum(1 for e in entries if e.predict_excluded),
        entries=entries,
    )
