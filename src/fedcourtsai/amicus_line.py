"""The amicus-adjusted cert reference line: the band rate, split on a cert-stage amicus brief.

A cert cell's salience band is its relist, CVSG and caption tier, so the
risk-set band rate (``StatPackTermSegment.prefix_est_grant_rate``) already is
the no-model forecast those docket facts give. One docket fact the band does
not read is whether an amicus brief reached the docket at the cert stage. This
module owns the registered rule that turns it into a second no-model forecast
(``docs/freeze-record.md`` dates the registration, and ``metrics/README.md``
carries the reading rule):

- **The fit** (:func:`fit_rows`) is the band's risk set, the same rows on the
  same weights the statpack's per-Term segments pool, cut in two **arms** on
  the corpus ``cert_amicus_briefs`` column: ``none`` (a stored 0) and ``some``
  (1 or more). A row whose count is NULL, a docket the live channel has not
  read since the column existed, joins neither arm and is counted beside them
  as ``unread``, so every rate is over read rows only.
- **The forecast** (:func:`forecast`) for a cell that froze a band, a salience
  version, a Term and a cert-stage amicus count is its arm's pooled rate over
  the Terms strictly before its own, inside the same lookback window the band
  anchor is pooled under. Where that arm's pool holds fewer than
  :data:`AMICUS_LINE_MIN_RESOLVED` observed resolved rows the forecast falls
  back to the band rate the cell froze, and says so.

Two approximations the rule states rather than hides. The fit conditions on
the count **at disposition** (what the column stores), while a forecast reads
the count **at the cell's snapshot** (``PredictionContext.cert_amicus_briefs``),
and the corpus stores only the final count, so neither side of the gap can be
sized. The ``none`` pool holds only petitions that never drew a brief, while a
``none`` cell may yet draw one: its rate is a floor for such a cell. The
``some`` pool also holds petitions whose first brief arrived after they had
climbed to a stronger band, so in a weak band its rate is probably a ceiling
for a cell that already holds a brief. And the two arms nest by band exactly
as the anchor's risk sets do, so a relisted petition is in the weaker bands'
arms too.

The fit is a committed artifact, ``metrics/amicus-line.json``
(:class:`AmicusLineFit`), written by ``fedcourts statpack`` beside the statpack
from the same corpus read, so a cell and every later reader pool one dated
build. Provisioning freezes a cert cell's forecast from the build checked out
when the cell is placed (:func:`freeze`), into ``record/context.json`` beside
the cert anchor, where the cell reads it. The evaluator stamp re-pools the
frozen forecast from the fit committed on ``main`` at the cell's run id
(:func:`verify`) and copies the rate onto the grading only where it
reproduces; the board's reference line reads that stamped rate.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from . import corpus
from .analytics import _GRANT_LABELS, _is_scored_segment_row
from .pipeline.salience import registered_versions, scorer
from .schemas import (
    AmicusLineCell,
    AmicusLineFit,
    CertAmicusLine,
    CertAnchor,
    PredictionContext,
)

#: The registered rule's name. A change to the split, the pool or the fallback
#: is a new name, never an edit to this one.
AMICUS_LINE_RULE: Final = "amicus-line-v2"

#: Observed (unweighted) resolved rows an arm's pool must hold before its rate
#: is used. Below it the forecast is the band rate.
AMICUS_LINE_MIN_RESOLVED: Final = 30

AmicusArm = Literal["none", "some"]
AmicusLineBasis = Literal["arm", "band-fallback"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AmicusLineForecast(_Model):
    """The line's forecast for one cell, with what it was pooled from."""

    rate: float | None = Field(
        ge=0.0,
        le=1.0,
        description="The reference probability of a grant; null only on the fallback "
        "where no band rate was passed in",
    )
    basis: AmicusLineBasis = Field(
        description="'arm' where the cell's arm pool met the minimum; 'band-fallback' "
        "where it did not and the rate is the band rate passed in"
    )
    arm: AmicusArm = Field(description="The arm the cell's frozen count put it in")
    arm_resolved: int = Field(
        ge=0, description="Observed resolved rows in that arm's pool, whichever basis was used"
    )


def arm_of(cert_amicus_briefs: int) -> AmicusArm:
    """The arm a cert-stage amicus count falls in: none against one or more."""
    return "some" if cert_amicus_briefs >= 1 else "none"


def fit_rows(rows: Iterable[corpus.CorpusRow]) -> list[AmicusLineCell]:
    """Every (Term, version, band) risk set over ``rows``, cut on the amicus count.

    The population, the weights and the risk-set walk are the statpack's own
    (``analytics._TermAcc.add``): a live-slice paid modern-cert row inside a
    version's segment joins its own band's risk set and every weaker band on
    its reachable ladder, weighted by ``sample_weight`` floored at 1. Only
    resolved rows are counted, since a pending row is in no rate. Sorted by
    Term (recent first), version and the scorer's own band order.
    """
    scorers = tuple((version, scorer(version)) for version in registered_versions())
    counts: dict[tuple[int, str, str], list[int]] = defaultdict(lambda: [0] * 7)
    for row in rows:
        if row.disposition is None or not corpus.is_live_slice(row):
            continue
        if not _is_scored_segment_row(row):
            continue
        term = corpus.scotus_term_year(row.docket_number)
        if term is None:
            continue
        weight = max(1, row.sample_weight if row.sample_weight is not None else 1)
        granted = row.disposition in _GRANT_LABELS
        amicus = row.cert_amicus_briefs
        for version, banding in scorers:
            if not banding.in_segment(row):
                continue
            ladder = banding.reachable_bands(row)
            own = banding.band(row)
            if own not in ladder:  # a registration whose ladder and band rule disagree
                raise ValueError(f"{version} banded {row.case_id} `{own}`, off its ladder {ladder}")
            for band in ladder[ladder.index(own) :]:
                cell = counts[(term, version, band)]
                if amicus is None:
                    cell[6] += 1
                    continue
                offset = 3 if amicus >= 1 else 0
                cell[offset] += 1
                cell[offset + 1] += weight
                cell[offset + 2] += weight if granted else 0
    order = {
        version: {band: index for index, band in enumerate(banding.bands)}
        for version, banding in scorers
    }
    return [
        AmicusLineCell(
            term=term,
            salience_version=version,
            band=band,
            none_resolved=cell[0],
            none_weighted_resolved=cell[1],
            none_weighted_grants=cell[2],
            some_resolved=cell[3],
            some_weighted_resolved=cell[4],
            some_weighted_grants=cell[5],
            unread_resolved=cell[6],
        )
        for (term, version, band), cell in sorted(
            counts.items(),
            key=lambda item: (-item[0][0], item[0][1], order[item[0][1]][item[0][2]]),
        )
    ]


class AmicusLineArmPool(_Model):
    """One arm's pool for one band: what a cell in that arm would be forecast from."""

    band: str = Field(description="The band whose risk set was pooled")
    arm: AmicusArm = Field(description="The arm pooled")
    terms: list[int] = Field(description="The Terms that contributed rows, recent first")
    resolved: int = Field(ge=0, description="Observed resolved rows in the pool (raw count)")
    weighted_resolved: int = Field(ge=0, description="The pool's weighted resolved estimate")
    rate: float | None = Field(
        ge=0.0,
        le=1.0,
        description="Weighted grant-family share of the pool; null where it is empty. "
        "Printed whatever the count: `meets_minimum` says whether the line would use it",
    )
    meets_minimum: bool = Field(
        description="Whether `resolved` reaches `AMICUS_LINE_MIN_RESOLVED`; where it does "
        "not, the line forecasts the band rate"
    )
    unsplit_rate: float | None = Field(
        ge=0.0,
        le=1.0,
        description="Both arms of this band pooled over the same Terms: the band rate from "
        "the same fit, over read rows only. The comparator that isolates the split from "
        "the fit's vintage; null where both arms are empty",
    )
    unread_resolved: int = Field(
        ge=0,
        description="Resolved rows in this band's risk set over the same Terms whose stored "
        "count is NULL: in neither arm and in no rate here",
    )


def _pool(
    fit: Iterable[AmicusLineCell],
    *,
    band: str,
    salience_version: str,
    term: int,
    arm: AmicusArm,
    lookback_terms: int,
) -> AmicusLineArmPool:
    """One arm of one band, pooled over the Terms strictly before ``term`` in the window."""
    oldest = term - lookback_terms if lookback_terms > 0 else None
    terms: list[int] = []
    resolved = weighted_resolved = weighted_grants = 0
    both_resolved = both_grants = unread = 0
    for cell in fit:
        if cell.salience_version != salience_version or cell.band != band:
            continue
        if cell.term >= term or (oldest is not None and cell.term < oldest):
            continue
        counts = (
            (cell.some_resolved, cell.some_weighted_resolved, cell.some_weighted_grants)
            if arm == "some"
            else (cell.none_resolved, cell.none_weighted_resolved, cell.none_weighted_grants)
        )
        both_resolved += cell.none_weighted_resolved + cell.some_weighted_resolved
        both_grants += cell.none_weighted_grants + cell.some_weighted_grants
        unread += cell.unread_resolved
        if counts[0]:
            terms.append(cell.term)
        resolved += counts[0]
        weighted_resolved += counts[1]
        weighted_grants += counts[2]
    return AmicusLineArmPool(
        band=band,
        arm=arm,
        terms=sorted(terms, reverse=True),
        resolved=resolved,
        weighted_resolved=weighted_resolved,
        rate=weighted_grants / weighted_resolved if weighted_resolved else None,
        meets_minimum=resolved >= AMICUS_LINE_MIN_RESOLVED,
        unsplit_rate=both_grants / both_resolved if both_resolved else None,
        unread_resolved=unread,
    )


def pools(
    fit: Iterable[AmicusLineCell], *, salience_version: str, term: int, lookback_terms: int
) -> list[AmicusLineArmPool]:
    """Both arms of every band under ``salience_version``, as a cell of ``term`` would pool them."""
    cells = list(fit)
    return [
        _pool(
            cells,
            band=band,
            salience_version=salience_version,
            term=term,
            arm=arm,
            lookback_terms=lookback_terms,
        )
        for band in scorer(salience_version).bands
        for arm in ("none", "some")
    ]


def forecast(
    fit: Iterable[AmicusLineCell],
    *,
    band: str,
    salience_version: str,
    term: int,
    cert_amicus_briefs: int,
    band_rate: float | None,
    lookback_terms: int,
) -> AmicusLineForecast:
    """The line's forecast for a cell that froze this band, version, Term and count.

    The arm's rate is pooled as the band anchor is
    (``base_rates._pooled_band_rate``): aggregate weighted grants over aggregate
    weighted resolved, across the Terms strictly before ``term`` that carry the
    band under ``salience_version``, no older than ``term - lookback_terms``
    (``0`` is no window). The minimum is read on the pool's observed rows, not
    its weighted estimate, so a heavily weighted handful cannot clear it.
    ``band_rate`` is the fallback, the risk-set rate the cell itself froze
    (``CertAnchor.rate``), and ``lookback_terms`` the window that anchor froze
    (``CertAnchor.lookback_terms``), so a later change to the configured window
    does not move the line for a cell already placed. A null ``band_rate``, an
    anchor whose own pool was empty, leaves the fallback with no rate.
    """
    arm = arm_of(cert_amicus_briefs)
    pool = _pool(
        fit,
        band=band,
        salience_version=salience_version,
        term=term,
        arm=arm,
        lookback_terms=lookback_terms,
    )
    if pool.rate is None or not pool.meets_minimum:
        return AmicusLineForecast(
            rate=band_rate, basis="band-fallback", arm=arm, arm_resolved=pool.resolved
        )
    return AmicusLineForecast(rate=pool.rate, basis="arm", arm=arm, arm_resolved=pool.resolved)


#: How far a frozen rate may sit from its re-pool over the same fit. Float noise
#: only: both sides run one pooler over one build and one window.
FROZEN_LINE_TOLERANCE: Final = 1e-9


def build_fit(rows: Iterable[corpus.CorpusRow]) -> AmicusLineFit:
    """The fit over ``rows``, as ``fedcourts statpack`` commits it."""
    return AmicusLineFit(
        rule=AMICUS_LINE_RULE, min_resolved=AMICUS_LINE_MIN_RESOLVED, cells=fit_rows(rows)
    )


def fit_digest(fit: AmicusLineFit) -> str:
    """A content digest naming one fit build, as ``sha256:<hex>``.

    Over the parsed model's canonical JSON (sorted keys, no whitespace), as
    :func:`fedcourtsai.pipeline.base_rates.statpack_digest` names a statpack
    build, so a re-serialisation that changes no count names the same build.
    """
    canonical = json.dumps(fit.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def freeze(
    context: PredictionContext, fit: AmicusLineFit, anchor: CertAnchor | None
) -> CertAmicusLine | None:
    """The forecast a cert cell faces as placed, pinned to the fit it was pooled from.

    :func:`forecast` over the band, version, Term and cert-stage amicus count
    ``context`` froze, with ``anchor``'s rate as the fallback and its window as
    the pool's. ``None`` where any of those is missing or the fit was written
    under another rule: the cell then carries no line, which no later pool can
    stand in for.
    """
    if (
        anchor is None
        or context.band is None
        or context.salience_version is None
        or context.term is None
        or context.cert_amicus_briefs is None
        or fit.rule != AMICUS_LINE_RULE
        or fit.min_resolved != AMICUS_LINE_MIN_RESOLVED
    ):
        return None
    pooled = forecast(
        fit.cells,
        band=context.band,
        salience_version=context.salience_version,
        term=context.term,
        cert_amicus_briefs=context.cert_amicus_briefs,
        band_rate=anchor.rate,
        lookback_terms=anchor.lookback_terms,
    )
    return CertAmicusLine(
        rule=AMICUS_LINE_RULE,
        rate=pooled.rate,
        basis=pooled.basis,
        arm=pooled.arm,
        arm_resolved=pooled.arm_resolved,
        fit_digest=fit_digest(fit),
    )


def parse_fit(text: str) -> AmicusLineFit | None:
    """``text`` as a fit file, or ``None`` where it does not parse as one."""
    try:
        return AmicusLineFit.model_validate_json(text)
    except ValueError:
        return None


def verify(
    line: CertAmicusLine,
    context: PredictionContext,
    anchor: CertAnchor,
    committed: Sequence[str],
) -> str | None:
    """Why ``line`` is not the forecast a committed fit yields, or ``None`` where it is.

    ``committed`` is the text of each fit build the cell could have been placed
    against, read harness-side: the revision of ``metrics/amicus-line.json`` in
    force on ``main`` at the predict cell's run id, and the one it replaced
    where that landed within the checkout slack
    (:meth:`fedcourtsai.statpack_history.GitStatpackHistory.amicus_fits_in_force`).
    ``anchor`` is the cell's cert anchor, already verified by the caller, whose
    rate and window the line was frozen under. The line verifies where one of
    those builds carries its ``fit_digest`` and :func:`freeze` over ``context``
    reproduces its rule, arm, basis, pool size and rate. The file sits in the
    cell's workspace like the anchor, so the record is never checked against
    itself.
    """
    if not committed:
        return "no committed amicus-line fit at or before the cell's run id"
    named = False
    for text in committed:
        fit = parse_fit(text)
        if fit is None or fit_digest(fit) != line.fit_digest:
            continue
        named = True
        expected = freeze(context, fit, anchor)
        if expected is None:
            continue
        same_rate = (
            expected.rate is None and line.rate is None
            if expected.rate is None or line.rate is None
            else math.isclose(expected.rate, line.rate, rel_tol=0.0, abs_tol=FROZEN_LINE_TOLERANCE)
        )
        if same_rate and expected.model_copy(update={"rate": line.rate}) == line:
            return None
    if not named:
        return f"it names {line.fit_digest}, not a fit build in force when the cell was placed"
    return "the frozen forecast does not re-pool from the fit build it names"
