"""The conditioning a predict cell runs against, derived from what it can read.

One builder, two provisioners. A forward cell and a replay cell reach this from
different directions — the first gets the corpus's latest payload, the second a
point-in-time one — but both must have their band derived by the *same* rule from
the *same* kind of input, or the two strata stop being comparable at exactly the
seam that matters.

Derived from the snapshot **payload**, never the corpus row. The row holds current
values; the payload is what the cell could read, and a baseline has to be
conditioned on the latter. It also makes the record reproducible from the
artifact the cell was handed: an auditor re-parses the *provisioned* snapshot and
recovers the same band. That file, not the corpus's latest — for a truncated
replay cell the two are different documents, and only the first is what the cell
actually saw.

A leaf over the schema and the signal parsers, so neither provisioner has to know
how a band is computed and the two cannot drift apart.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any, Literal

from .. import corpus
from ..schemas import PredictionContext
from . import cert_signals
from .salience import SALIENCE_VERSION, salience_band


def build(
    case_id: str,
    snapshot_date: date,
    payload: Mapping[str, Any],
    mode: str,
    *,
    provenance: Literal["as-stored", "dated", "truncated", "blind"] = "as-stored",
    cutoff: date | None = None,
    decided_before: str | None = None,
) -> PredictionContext:
    """The conditioning state ``payload`` discloses, as at ``snapshot_date``.

    Deliberately carries no count of what truncation removed. That count separates
    a grant from a denial about as cleanly as the disposing order does — a denied
    docket stops within days of its cutoff, a granted one runs for another eight
    months of briefing — and this object is read by the cell. It belongs in the
    harness's own record, not here.

    Absence of a proceedings list is recorded as ``signals_observable=False``
    rather than as zero distributions. A snapshot that carries no entries — one
    truncated to before this petition's first distribution, or a payload shape
    that never had them — says nothing about the docket's posture, and a band
    derived from that silence would assert ``baseline`` about a petition whose
    position is simply unknown. The evaluator then falls back rather than scoring
    against an invented conditioning.
    """
    observable = cert_signals.snapshot_carries_proceedings(payload)
    count = cert_signals.snapshot_distribution_count(payload)
    cvsg = cert_signals.entry_date(cert_signals.snapshot_cvsg_date(payload))
    # Both payload shapes: the REST record carries `docket_number`, the live
    # supremecourt.gov JSON carries `CaseNumber`. Only the live shape carries
    # proceedings, so reading just the first leaves every live cell without a Term
    # and silently disables the whole frozen path.
    docket_number = str(payload.get("docket_number") or payload.get("CaseNumber") or "").strip()
    band: str | None = None
    if observable:
        # Scored from a row carrying only the two signals the band turns on: the
        # originating-court nudge is bounded below every cutpoint, so it cannot
        # move a band, and a snapshot need not disclose it.
        band = salience_band(
            corpus.CorpusRow(
                case_id=case_id,
                court=case_id.split("/", 1)[0],
                docket_number=docket_number,
                distribution_count=count,
                cvsg_date=cvsg,
            )
        )
    return PredictionContext(
        mode=mode,
        snapshot_date=snapshot_date,
        snapshot_provenance=provenance,
        cutoff=cutoff,
        decided_before=decided_before,
        signals_observable=observable,
        distribution_count=count,
        cvsg_date=cvsg,
        band=band,
        salience_version=SALIENCE_VERSION if band else None,
        term=corpus.scotus_term_year(docket_number) if docket_number else None,
    )
