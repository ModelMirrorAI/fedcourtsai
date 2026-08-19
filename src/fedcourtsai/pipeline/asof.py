"""Point-in-time projection of a corpus row from a payload: the as-of layer.

The corpus row holds a case's *current* values — outcome labels, latched
signals, selection state — while a truncated or dated snapshot payload holds
what was observable at some earlier moment. Replaying any current-state code
(the salience gate, a backtest selector) over past moments therefore needs an
honest synthesis: a row whose time-invariant identity comes from the corpus but
whose docket-acquired signals are re-derived from the payload as at a cutoff,
and whose outcome and latch fields are nulled outright.

:func:`project_row` is that synthesis, shared by the predict cell's
conditioning context (:mod:`.cell_context`) and the salience-gate replay
(:mod:`fedcourtsai.salience_replay`), so the two cannot drift on what "the row
as the cell saw it" means. :class:`CutoffPolicy` names the reconstruction
moments a replay may place a petition at.

A leaf over the schema and the signal parsers, like :mod:`.cert_signals`: it
imports no provisioner, so every provisioner can import it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Any, Literal

from .. import corpus
from . import cert_signals, interim_signals


@dataclass(frozen=True)
class AsOfRow:
    """A corpus row projected to what a payload disclosed as at ``cutoff``.

    ``row`` carries the time-invariant identity copied from the current row and
    the docket-acquired signals re-derived from the payload; every outcome and
    latch field is nulled, so downstream code sees the petition as still open.
    ``observable`` is False when the payload discloses no proceedings list at
    all — the signals are then *unknown*, not zero, and the row must never be
    banded (a band derived from silence would assert ``baseline`` about a
    petition whose posture is simply not disclosed). ``provenance`` records how
    the payload was obtained (see ``PredictionContext.snapshot_provenance``);
    ``cutoff`` is ``None`` only on a blind projection, where no moment could be
    identified and the proceedings were removed outright.
    """

    row: corpus.CorpusRow
    cutoff: date | None
    observable: bool
    provenance: Literal["dated", "truncated", "blind"]


def project_row(
    base: corpus.CorpusRow,
    payload: Mapping[str, Any],
    *,
    cutoff: date | None,
    provenance: Literal["dated", "truncated", "blind"],
    parse: str = cert_signals.DEFAULT_DISTRIBUTION_PARSE,
) -> AsOfRow:
    """Project ``base`` to what ``payload`` disclosed, as an :class:`AsOfRow`.

    Three field families, three rules:

    - **Time-invariant identity is copied** from the current row: the docket
      number (which fixes the Term and the paid/IFP fee class — assigned at
      filing, never changed), caption and structured petitioner title, filing
      date, originating-court linkage, and the sampling ``sample_weight`` (a
      property of how the corpus was built, not of the docket's progress).
      The caption invariance is measured, not assumed, at the *class* grain
      (the two measurements and their vintages: ``pipeline.caption``'s module
      docstring) — the residual concentrates in officer-title renderings,
      which is why the structured ``petitioner_title`` exists and why
      arrival-vs-terminal caption drift (unmeasurable until dated arrival
      snapshots resolve) stays a declared gap for any caption-keyed scorer
      rather than a replay-validated claim.
    - **Docket-acquired signals are re-derived from the payload** via the same
      parsers the cell-context builder uses — the cert pair
      (``distribution_count``, ``cvsg_date``) and the interim escalation trio
      (``response_requested``, ``referred_to_court``, ``amicus_briefs``) — so
      they reflect the moment the payload represents rather than where the case
      ended up. Both families are monotone, which is exactly why re-deriving
      matters: the latched columns hold the *ending* state. The interim trio is
      nulled outright where the payload discloses no proceedings, for the same
      reason the cert pair is: silence is unknown, not zero, and the corpus
      itself distinguishes a confident ``False``/``0`` from a never-parsed
      ``None``. Both families are derived unconditionally rather than switching
      on the docket form: the projection's job is to report what the payload
      says, and which of the two a consumer may read is a question about the
      *stage*, settled by each consumer. So a cert docket carries the trio too —
      its entries name no response request and no referral, while its amicus
      entries do count. This row is internal (the gate replay's interim ladder
      reads it as-of here); the *cell-visible* freeze narrows it, and
      :func:`fedcourtsai.pipeline.cell_context.build` states why.
      ``distributed_for_conference`` is left
      ``None`` — a caller that wants the as-of conference derives it with
      :func:`asof_conference` and sets it on the row, keeping the derivation
      moment explicit.
    - **Everything else is nulled** — disposition, decision and cert dates,
      the ``salience_*`` columns, the ``predict_*``/queue latches, tracking
      stamps, opinion linkage. The projected row therefore reads as an open,
      never-scored petition, which is what it was at the cutoff.

    ``parse`` names the registered DISTRIBUTED reading
    (:data:`~fedcourtsai.pipeline.cert_signals.DISTRIBUTION_PARSES`) the
    ``distribution_count`` is derived under. A caller that goes on to band the
    projected row passes the parse its scorer pins
    (:attr:`~fedcourtsai.pipeline.salience.SalienceScorer.distribution_parse`),
    or the band it reads back is one that scoring function was never fitted on.
    :func:`asof_conference` takes no parse for the reason ingest's conference
    key takes none: the cohort a petition is scored in is one value per case,
    not one per registered parse.
    """
    observable = cert_signals.snapshot_carries_proceedings(payload)
    texts = [text for text, _ in cert_signals.proceedings_entries(payload)]
    requested, referred, amicus = (
        interim_signals.escalation_signals(texts) if observable else (None, None, None)
    )
    return AsOfRow(
        row=corpus.CorpusRow(
            case_id=base.case_id,
            court=base.court,
            docket_number=base.docket_number,
            case_name=base.case_name,
            petitioner_title=base.petitioner_title,
            date_filed=base.date_filed,
            originating_court=base.originating_court,
            originating_court_name=base.originating_court_name,
            originating_docket_number=base.originating_docket_number,
            sample_weight=base.sample_weight,
            distribution_count=cert_signals.snapshot_distribution_count(payload, parse=parse),
            cvsg_date=cert_signals.entry_date(cert_signals.snapshot_cvsg_date(payload)),
            response_requested=requested,
            referred_to_court=referred,
            amicus_briefs=amicus,
        ),
        cutoff=cutoff,
        observable=observable,
        provenance=provenance,
    )


def asof_conference(payload: Mapping[str, Any], cutoff: date) -> date | None:
    """The conference the payload showed this petition distributed for, as at ``cutoff``.

    The live channel's latest-entry-wins rule, reproduced as-of: scan the
    proceedings in docket order, keep the conference date named by each
    DISTRIBUTED entry whose *own filing date* is strictly before ``cutoff``, and
    return the last one — an unparseable conference date degrades to the
    previous match, exactly as ingestion's parse does, so with a cutoff past
    every entry this equals the live ``distributed_for_conference`` value.
    ``None`` when no distribution was disclosed before the cutoff (or the
    payload discloses no proceedings at all). An undated entry is skipped —
    fail closed, the same posture replay truncation takes.
    """
    conference: date | None = None
    for text, raw in cert_signals.proceedings_entries(payload):
        match = cert_signals.DISTRIBUTED_RE.search(text)
        if match is None:
            continue
        filed = cert_signals.entry_date(raw)
        if filed is None or filed >= cutoff:
            continue
        parsed = cert_signals.conference_date(match.group(1))
        if parsed is not None:
            conference = parsed
    return conference


class CutoffPolicy(StrEnum):
    """The reconstruction moments a gate replay may place a petition at.

    Each names the day *after* an observable docket event, so a truncation at
    the policy's cutoff keeps that event and everything before it — mirroring
    how a forward cell runs after the transition that queued it.
    """

    #: The day after the docket's earliest dated entry (the petition's arrival;
    #: falls back to the filing date + 1 day when no entry carries a date).
    arrival = "arrival"
    #: The day after the first DISTRIBUTED entry — the moment the forward
    #: trigger most often fires at.
    distribution_1 = "distribution-1"
    #: The last distribution before resolution — the latest posture a forward
    #: cell would have seen (:func:`replay_cutoff`).
    resolution = "resolution"


def replay_cutoff(payload: Mapping[str, Any], resolved_at: date) -> date | None:
    """The day after the last distribution entry that predates ``resolved_at``.

    A forward cell is queued by a **distribution transition**, so that is the
    moment a replay has to reproduce if the two channels are to be comparable.
    Taking the last such entry before resolution puts the replay at the latest
    posture a forward cell would have seen — the hardest and most realistic one,
    and exactly one cell per petition.

    ``None`` when the payload shows no dated distribution before resolution, in
    which case there is no forward moment to reproduce and the caller drops the
    entries wholesale rather than guessing a cutoff.

    Reading entry dates rather than the conference dates they name is deliberate:
    the entry "DISTRIBUTED for Conference of March 7" is *filed* in late February,
    and February is when a forward cell would have run.

    The moment reads ``DISTRIBUTED_RE`` unversioned on purpose: the cutoff is
    the reconstruction *moment* and must be parse-invariant so cells stay
    comparable across salience versions — only the projected *count*
    (:func:`project_row`) follows a version's declared parse.
    """
    latest: date | None = None
    for text, raw in cert_signals.proceedings_entries(payload):
        if not cert_signals.DISTRIBUTED_RE.search(text):
            continue
        filed = cert_signals.entry_date(raw)
        if filed is not None and filed < resolved_at and (latest is None or filed > latest):
            latest = filed
    return latest + timedelta(days=1) if latest is not None else None


def policy_cutoff(
    policy: CutoffPolicy, row: corpus.CorpusRow, payload: Mapping[str, Any]
) -> date | None:
    """The ``policy``'s cutoff for this petition, or ``None`` if no moment exists.

    ``None`` means the payload (plus the row's dates) identifies no such moment
    — an undated docket under ``arrival``, a never-distributed petition under
    ``distribution-1``, or no pre-resolution distribution under ``resolution``
    — and the caller degrades to a blind projection rather than guessing.

    Like :func:`replay_cutoff`, the ``distribution-1`` branch reads
    ``DISTRIBUTED_RE`` unversioned on purpose: the moment is parse-invariant so
    cells stay comparable across versions; only the count follows the parse.
    """
    if policy is CutoffPolicy.arrival:
        dates = [
            filed
            for _, raw in cert_signals.proceedings_entries(payload)
            if (filed := cert_signals.entry_date(raw)) is not None
        ]
        if dates:
            return min(dates) + timedelta(days=1)
        return row.date_filed + timedelta(days=1) if row.date_filed is not None else None
    if policy is CutoffPolicy.distribution_1:
        for text, raw in cert_signals.proceedings_entries(payload):
            if cert_signals.DISTRIBUTED_RE.search(text):
                filed = cert_signals.entry_date(raw)
                return filed + timedelta(days=1) if filed is not None else None
        return None
    resolved_at = corpus.resolution_date(row)
    if resolved_at is None:
        return None
    return replay_cutoff(payload, resolved_at)
