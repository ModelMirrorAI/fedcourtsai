"""The score baselines' frozen per-Term fits, for scoring beside the models.

``docs/merits-alignment-baseline.md`` (*The frozen fits*) specifies them. The
leaderboard reads only committed records, so baselines 3 and 4 reach it
through a committed artifact, ``data/merits-alignment/alignment-fits.json``:
one entry per October Term, holding everything the two baselines need to
call that Term's decisions, fitted on what was decided before the Term opened.

- **The transform** is the isotonic outcome transform (:func:`.alignment_score.fit_calibration`)
  over every decided code of an earlier Term.
- **The spread** ``k`` is fitted (:func:`.alignment_score.fit_spread`) on every
  earlier Term's coded complete lineups, each at its own Term's prior-bench
  positions and at the transform, so the Term is scored exactly as the
  readout's out-of-sample reading scores it.
- **The positions** are the prior Term's from the release published before
  the Term opened (:meth:`.alignment_score.JusticePositions.prior_bench`).

Each entry is made once and never revised (:func:`publish_fit`), so a code or
a lineup added later for an earlier Term moves no figure already scored. A
fit reads nothing decided in its Term, but it may be made after some of the
Term's decisions, so a reading under it is pre-registered only for a decision
dated after its ``frozen_on`` whose own code was made before that decision;
the rest are backtests.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

from ..schemas import AlignmentFits, AlignmentSideCode, AlignmentTermFit, Judgment
from .alignment_score import (
    K_GRID,
    Calibration,
    JusticePositions,
    OutcomeCase,
    _fit_rows,
    consolidated_duplicates,
    fit_calibration,
    fit_spread,
    outcome_cases,
    vote_cases,
)
from .merits_lineups import MeritsLineup


class AlignmentFitError(ValueError):
    """A fit that cannot be published as asked."""


def fits_path(data_root: Path) -> Path:
    """The committed frozen-fits artifact."""
    return data_root / "merits-alignment" / "alignment-fits.json"


def codes_digest(cases: Sequence[OutcomeCase]) -> str:
    """sha256 of the compact JSON list of [case_id, conservative_side, score], by case_id."""
    rows = sorted([c.case_id, str(c.conservative_side), c.score] for c in cases)
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def frozen_fit(
    codes: Sequence[AlignmentSideCode],
    judgments: Mapping[str, tuple[Judgment, date]],
    lineups: Sequence[MeritsLineup],
    positions: JusticePositions,
    *,
    term: int,
    frozen_on: date,
) -> AlignmentTermFit:
    """Term ``term``'s fit, reading only decisions made before 1 October of ``term``.

    The caller hands in every lineup from the first coded decision Term, as
    for :func:`.alignment_score.score_readout`; judgments, codes and lineups
    of ``term`` itself or later are handed in harmlessly and never read.
    """
    opened = date(term, 10, 1)
    before = {cid: jd for cid, jd in judgments.items() if jd[1] < opened}
    early = [lu for lu in lineups if lu.decided < opened]
    dropped = consolidated_duplicates(early, codes, before)
    outcomes = [c for c in outcome_cases(codes, before) if c.case_id not in dropped]
    earlier = [c for c in outcomes if c.term < term]
    calibration = fit_calibration([(c.score, c.conservative_prevailed) for c in earlier])
    bench = positions.prior_bench(term)
    k: float | None = None
    k_decisions = 0
    if calibration is not None and bench is not None:
        votes = [v for v in vote_cases(early, outcomes, codes) if v.term < term]
        rows, _used = _fit_rows(votes, positions.prior_bench, calibration)
        k = fit_spread(rows)
        k_decisions = len(rows)
    read = [before[c.case_id][1] for c in earlier]
    return AlignmentTermFit(
        term=term,
        opened=opened,
        frozen_on=frozen_on,
        codes_digest=codes_digest(earlier),
        latest_decision_read=max(read) if read else None,
        transform=None if calibration is None else list(calibration.knots),
        transform_decisions=len(earlier),
        k=k,
        k_decisions=k_decisions,
        k_at_grid_edge=k == K_GRID[-1],
        consolidated=len(dropped),
        positions=bench,
        positions_source=positions.source,
        contamination_risk=sum(c.contamination_risk for c in earlier),
    )


def calibration_of(fit: AlignmentTermFit) -> Calibration | None:
    """The fit's outcome transform, as :func:`.alignment_score.fit_calibration` returns one."""
    if fit.transform is None:
        return None
    return Calibration(
        knots=tuple((start, rate) for start, rate in fit.transform),
        decisions=fit.transform_decisions,
    )


def publish_fit(prior: AlignmentFits | None, fit: AlignmentTermFit) -> AlignmentFits:
    """Add one Term's fit to the committed fits, append-only.

    A Term already fitted is refused: its fit may already have scored a
    decision, and a refit would re-score it.
    """
    held = {e.term: e for e in (prior.entries if prior is not None else [])}
    if fit.term in held:
        raise AlignmentFitError(f"OT{fit.term} is already fitted: a fit is never revised")
    held[fit.term] = fit
    return AlignmentFits(entries=[held[t] for t in sorted(held)])


def assert_appended(before: AlignmentFits | None, after: AlignmentFits) -> int:
    """The one Term ``after`` adds to ``before``, refusing any other change.

    The writer's check on its own output: every entry ``before`` holds is in
    ``after`` byte for byte, and ``after`` holds exactly one entry more.
    """
    held = [] if before is None else before.entries
    added = [e for e in after.entries if e.term not in {h.term for h in held}]
    kept = {e.term: e for e in after.entries}
    for entry in held:
        if kept.get(entry.term) != entry:
            raise AlignmentFitError(f"OT{entry.term}'s fit changed: a fit is never revised")
    if len(added) != 1 or len(after.entries) != len(held) + 1:
        raise AlignmentFitError(
            f"expected exactly one new Term's fit, found {len(added)} new of "
            f"{len(after.entries)} entries over {len(held)}"
        )
    return added[0].term
