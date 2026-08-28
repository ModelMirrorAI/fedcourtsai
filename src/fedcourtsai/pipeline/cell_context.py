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
from .asof import project_row
from .salience import SALIENCE_VERSION, salience_band, scorer


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
    against an invented conditioning. The one flag governs **both** signal
    families: the cert pair and the interim escalation trio come off the same
    proceedings list, so a payload that discloses none discloses neither.

    The interim trio is frozen only on an **application** docket, even though the
    projection derives it for anything. This object is read by the cell
    (``record/context.json``), so what it carries is part of the cell's
    information set: handing a cert cell a pre-computed amicus count would widen
    that set for every cert cell without a prompt edit to bound it, which is
    exactly the silent move ``docs/process-version.md`` exists to prevent. An
    application cell needs the trio because its declared claims resolve against
    it; a cert cell has no claim that reads it.
    """
    # Both payload shapes: the REST record carries `docket_number`, the live
    # supremecourt.gov JSON carries `CaseNumber`. Only the live shape carries
    # proceedings, so reading just the first leaves every live cell without a Term
    # and silently disables the whole frozen path.
    docket_number = str(payload.get("docket_number") or payload.get("CaseNumber") or "").strip()
    # The caption in both payload shapes: the live JSON's structured
    # `PetitionerTitle` (preferred, exactly as ingest prefers the structured
    # column) and the REST record's joined `case_name`. It must come from the
    # payload, not the corpus row, because the band below turns on the caption
    # class under sal-v2 — a `federal` band frozen from a caption the cell
    # cannot read would break this module's reproducibility rule. Caption is
    # time-invariant identity (`asof.project_row`), so a dated or truncated
    # payload's caption is as leakage-safe as its docket number.
    petitioner_title = str(payload.get("PetitionerTitle") or "").strip() or None
    case_name = str(payload.get("case_name") or "").strip()
    # The shared as-of projection derives the signals and their observability;
    # the base row carries only the identity a payload discloses (a forward
    # cell's snapshot need not disclose its originating court, and the nudge is
    # bounded below every band cutpoint anyway, so a band never turns on it).
    projected = project_row(
        corpus.CorpusRow(
            case_id=case_id,
            court=case_id.split("/", 1)[0],
            docket_number=docket_number,
            case_name=case_name,
            petitioner_title=petitioner_title,
        ),
        payload,
        cutoff=cutoff if cutoff is not None else snapshot_date,
        provenance="dated" if provenance == "as-stored" else provenance,
        # The ACTIVE scorer's parse, read here rather than defaulted, so this
        # cell's count follows the reading its banding version declares. That is
        # all this line buys, and the limit is worth stating: the live gate bands
        # the corpus's max-latched `distribution_count`, written under
        # `cert_signals.DEFAULT_DISTRIBUTION_PARSE`, and this projection is
        # deliberately behind that column anyway (it reads one snapshot, as-of).
        # So the two agree on the reading only while the ACTIVE version pins the
        # default — which the active-scorer parse test enforces, and which
        # activating a version pinning another parse must revisit together with
        # the column's own re-derivation. A registered-but-inactive version
        # pinning a second parse reaches no cell through here, which is what
        # makes registration safe ahead of that re-derivation.
        parse=scorer().distribution_parse,
    )
    observable = projected.observable
    count = projected.row.distribution_count
    cvsg = projected.row.cvsg_date
    # An application docket takes no salience band, by rule rather than by
    # parse accident: the trajectory features (distribution count, CVSG) are
    # cert observations that do not exist on the interim docket, so a band
    # derived from their absence would assert `baseline` — and hand the
    # evaluator a cert-population base rate — for a cell that resolves on the
    # interim standard. The caption class *does* exist on an application, but
    # every band's base rate is a cert-petition population, so banding on
    # caption alone would mislabel the population just the same. With no band
    # frozen, the base-rate guards downstream refuse by design (the interim
    # segment rate publishes on its own pre-registered terms; see
    # docs/salience.md).
    application = corpus.is_scotus_application_form(docket_number)
    band = salience_band(projected.row) if observable and not application else None
    # The Term axis follows the docket form, because the two stages' baselines
    # pool different sections keyed on different Terms: a cert petition's
    # `YY-NNNN` number gives the cert Term the band table is keyed on, an
    # application's `YYAnnn` number the application Term the interim section is
    # keyed on. Both are read from the number alone, so both are as
    # leakage-safe as the number is; which pool a cell's Term addresses is
    # decided by the claim it is scoring, never by this field.
    term = corpus.scotus_term_year(docket_number) if docket_number else None
    if term is None and application:
        term = corpus.scotus_application_term_year(docket_number)
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
        response_requested=projected.row.response_requested if application else None,
        referred_to_court=projected.row.referred_to_court if application else None,
        amicus_briefs=projected.row.amicus_briefs if application else None,
        term=term,
    )
