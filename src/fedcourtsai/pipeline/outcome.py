"""Outcome detection: turn a resolved docket into ``outcome.json`` (or surface it).

This is ``pull``'s third job (see ``docs/data-pipeline.md``): once a refresh
re-ingests a docket through the shared core, decide whether any of the case's
**open** predictable events have now been decided, and record the ground truth
that ``run-evaluate`` scores against.

The corpus row carries only **case-level** facts — the docket's resolution
date (:func:`fedcourtsai.corpus.resolution_date`: the petition-stage cert date
on a SCOTUS docket, ``date_decided`` elsewhere) and a normalized
``disposition`` — so detection reasons at the case level and is deliberately
conservative:

- **Deterministic write.** When the docket appears decided, the disposition is
  *machine-readable* (a concrete :class:`Disposition`, not the ``other`` catch-all
  or ``None``), there is a decision date to stamp as ``resolved_at``, and the case
  has exactly **one** open event, the event's outcome is unambiguous: write
  ``outcome.json`` and mark the event resolved.
- **Surface otherwise.** Anything ambiguous — an unreadable/absent disposition,
  no decision date, or open events the case-level disposition cannot be
  attributed to one of — produces an :class:`UnrecordedOutcome`, surfaced on the
  pipeline-runs dashboard for maintainer triage. Nothing is written on a guess.

Attribution is **stage-routed**, with the docket's form selecting the
disposition's source and therefore its stage: on a cert docket the case-level
disposition is the *cert*-stage decision, so it belongs to the open event whose
``stage`` is ``cert`` — even when other events (an interim motion) are open
beside it, which then simply stay open — with stage-less events falling back to
the case-baseline id-prefix rule (:func:`_cert_disposition_target`); on an
application docket it is the *interim* disposition the interim vocabulary
matched at ingest, so it belongs to the lone open ``interim``-stage event
(:func:`_interim_disposition_target`). Anything the stage does not disambiguate
is refused.

A recorded cert **grant** is also a birth: it opens the merits proceeding, so
:func:`resolve_case` mints the case's open merits event
(:func:`mint_merits_event` — after the attribution completes, so the detection
pass that resolves the petition never sees it), and the live rotation keeps
polling the granted docket toward its judgment on that event's account. Once
the petition event has closed, a re-poll's decided-looking row is recognized
as the record of that resolution (:func:`_cert_already_attributed`) and
resolves to a clean no-op rather than triage — until the judgment lands: the
live channel latches the parsed merits pair onto the row at ingest
(``merits_judgment`` / ``merits_decided``, via the shared
:mod:`fedcourtsai.pipeline.judgment` parser), and detection resolves the open
merits-stage event from those columns (:func:`build_merits_outcome` — the
judgment axis on the outcome, the disturbed projection as its declared
binary), at which point the case's last open event closes and the docket
exits the rotation.

The pure decision (:func:`detect_resolution`) is separated from the ledger write
(:func:`record_outcomes`) so the logic is testable without a filesystem.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from .. import corpus, ids
from ..paths import CasePaths
from ..schemas import (
    GRANTED_DISPOSITIONS,
    MERITS_PROCEEDING_DISPOSITIONS,
    Disposition,
    EventKind,
    Judgment,
    Outcome,
    PredictableEvent,
    ResolutionSignals,
    Stage,
)
from ..serialize import write_json, write_yaml
from ..store import open_events
from .cert_signals import match_disposition_signal, mootness_disposition
from .ingest import CorpusRow
from .judgment import judgment_disturbed

# Which grants open a merits proceeding is one definition, shared with the
# judgment backfill and the statpack's merits section so the population that is
# predicted is the population the base rate is measured over.
_MERITS_PROCEEDING = MERITS_PROCEEDING_DISPOSITIONS


def _known_judgment(value: str) -> Judgment | None:
    """The stored merits judgment as a :class:`Judgment`, or ``None`` if unknown.

    ``merits_judgment`` is a blob-tolerant TEXT column whose readers re-validate
    against the vocabulary rather than failing the row, so an out-of-vocabulary
    value degrades to the unrecorded path everywhere it is read.
    """
    try:
        return Judgment(value)
    except ValueError:
        return None


#: The id of the merits event a cert grant mints: the grant order is the filing
#: that opened it (kind names the filing, stage names the standard — the
#: ``Stage`` docstring), and the thing to predict is the judgment.
MERITS_EVENT_ID = ids.event_id("order", "judgment")


def granted_flag(disposition: Disposition) -> int:
    """Project a disposition onto the binary ``actual_granted`` target (1=granted)."""
    return int(disposition in GRANTED_DISPOSITIONS)


def is_machine_readable(disposition: Disposition | None) -> bool:
    """Whether a disposition is a concrete label we can record without a human.

    ``None`` (no disposition) and :attr:`Disposition.other` (the normalizer's
    catch-all for text it could not classify) are *not* machine-readable — they
    mean "decided, but we do not know how", which is the unrecorded path.
    """
    return disposition is not None and disposition != Disposition.other


def appears_decided(row: CorpusRow) -> bool:
    """Whether the refreshed docket now looks resolved.

    A resolution date — the petition-stage cert grant/denial date on a SCOTUS
    docket, or the docket-level decision date (``date_terminated``/``date_decided``
    upstream) — or any disposition at all is the signal that the matter is no
    longer pending.
    """
    return corpus.resolution_date(row) is not None or row.disposition is not None


# Docket-entry descriptions that state the matter is over even when the docket
# row carries no decision date or disposition. Four families:
#   - appellate dockets CourtListener stopped indexing years ago
#     (``date_terminated`` stays null): the clerk's termination entry and the
#     published-opinion entry;
#   - SCOTUS terminal orders the cert-disposition resolver deliberately does not
#     match — an IFP denial that dismisses under Rule 39.8, an original/habeas
#     petition dismissal (many words separate "petition" from "dismissed"), and a
#     fee-default closure;
#   - SCOTUS decided-merits orders the resolver's grant-anchored patterns miss:
#     a vacate-and-remand disposition with no "grant" word ("Judgment VACATED
#     and case REMANDED for further consideration in light of ..."), the
#     "Judgment Issued" entry that follows it (the mandate analog — on a SCOTUS
#     docket the matter is over once judgment issues), and the merits judgment
#     itself ("Adjudged to be AFFIRMED", "Judgment REVERSED") — its latest entry
#     leaked a granted-argued-and-decided cert-before-judgment docket forward;
#   - the cert-before-judgment disposition — grant, denial, and dismissal — whose
#     "before judgment" gap separates the noun from the verb, so the resolver
#     misses all three (a CBJ grant decides the petition-disposition event just
#     as a denial does).
# The new shapes are anchored against pending-shaped near-misses: "judgment
# issued" and the merits and CBJ branches are start-anchored (like "opinion
# issued") so a docketing recital ("NOTICE OF APPEAL filed from the judgment
# issued/affirmed on ...", the expedite *motion* reciting the CBJ petition) stays
# pending, and the vacate pair requires the disposition order's noun-verb shape —
# "judgment ... vacated ... remand" — so the SG's confession-of-error *motion*
# ("Motion of respondent to vacate the judgment and remand ... filed", verb
# before noun) and an en banc panel-opinion vacatur ("panel opinion is VACATED
# and the case is REMANDED to the panel", no judgment) stay pending too.
# This is a high-recall *routing* backstop that also feeds the forward-cell
# provisioning refusal (``provision-snapshot --refuse-terminal``): a match
# diverts a decided-looking case out of the forward-predict queue for triage
# (``predict_skipped_decided``), or leaves a fanned-out cell snapshot-less.
# Routing (``termination_signal``) reads only the latest entry (pendency, so a
# reactivation reopens the docket); the provisioning leakage guard
# (``snapshot_shows_disposition``) scans every entry with no reactivation
# exception (the outcome must not be legible anywhere in the cell's snapshot). It
# never records an ``outcome.json``, so — unlike broadening the resolving
# instrument (:func:`fedcourtsai.pipeline.cert_signals.match_disposition_signal`) —
# a false positive is cheap (a case parked for triage or one degraded cell, its
# events left open), not a fabricated ground truth. The initial IFP denial that
# only sets a fee deadline ("...is denied. Petitioner allowed until ... to pay")
# is deliberately *not* matched: that petition may still proceed on payment, so
# the later closure / dismissal entry — not the denial — is the terminal signal.
_TERMINAL_ENTRY_RE = re.compile(
    r"^opinion issued\b"
    r"|\bcase termination\b"
    r"|\bconsidered closed\b"
    r"|\brule\s*39\.8\b"
    r"|\bpetition\b.{0,80}?\bdismissed\b"
    r"|^judgment issued\b"
    r"|\bjudgment\b.{0,40}?\bvacated\b.{0,80}?\bremand\w*"
    # The SCOTUS merits judgment: once the Court enters judgment the case is
    # over, so nothing about the petition is pending. Start-anchored to the
    # disposition entry's own noun ("Adjudged to be AFFIRMED", "Judgment
    # REVERSED") — a lower-court-history recital opens with "Notice of appeal
    # ..." / "Motion ..." and stays clear. This is the shape that leaked a
    # granted-argued-and-decided cert-before-judgment docket into a forward
    # cell: its latest entry is the merits ruling, which no other branch read.
    r"|^(?:adjudged|judgment)\b.{0,40}?\b(?:affirmed|reversed)\b"
    # The cert-before-judgment disposition — grant as well as denial/dismissal.
    # Denial and dismissal are deliberate resolver misses (the multi-word
    # noun-verb gap would also admit the expedite-motion recital), so routing is
    # their only net. The *grant* the resolver now reads at ingest (a decided
    # grant otherwise wastes forward-predict cells), but the branch stays here as
    # defense in depth: once cert-before-judgment is granted the petition event
    # is decided, so a snapshot still carrying it must route out of the forward
    # queue / refuse provisioning even if ingest resolution did not fire (a
    # pre-resolution snapshot, a replay, a multi-event docket the resolver
    # declined). Start-anchored — the disposition entry opens with the noun,
    # while the expedite order opens with "Motion ..." and must stay pending.
    r"|^(?:the\s+)?petitions? for (?:a )?writs? of certiorari before judgment "
    r"(?:are |is )?(?:denied|dismiss|granted)",
    re.IGNORECASE,
)


def entry_descriptions(docket: Mapping[str, Any]) -> list[str]:
    """Every non-empty entry description in a docket payload, in docket order.

    Reads both payload shapes a stored snapshot can carry: the REST/mapped
    ``docket_entries`` list (``description`` / ``short_description``) and the
    raw supremecourt.gov ``ProceedingsandOrder`` list (``Text``) that the live
    channel stores verbatim as the point-in-time raw fact. The shapes are
    mutually exclusive per stored payload (each channel stores its own payload
    whole), so the concatenation order is immaterial in practice. Tolerates
    malformed entries (skipped, never raised) — the raw payload is unvalidated.
    """
    descriptions: list[str] = []
    for entry in docket.get("docket_entries") or []:
        if not isinstance(entry, Mapping):
            continue
        for key in ("description", "short_description"):
            description = str(entry.get(key) or "").strip()
            if description:
                descriptions.append(description)
                break
    for entry in docket.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        description = str(entry.get("Text") or "").strip()
        if description:
            descriptions.append(description)
    return descriptions


def termination_signal(docket: Mapping[str, Any]) -> str | None:
    """A human-readable reason the fresh docket looks already decided, or ``None``.

    Complements :func:`appears_decided`, which keys on the normalized row's
    resolution date / disposition: a stale appellate docket often carries
    neither, yet its **latest** entry ("Case termination for order and
    judgment", "Opinion Issued") shows the matter is over. Only the last
    described entry counts — pendency is event-level, and a filing *after* a
    terminal entry (a stay-the-mandate motion, a rehearing petition) means the
    docket is active again, so an earlier terminal entry must not starve the
    later event. (A linked opinion cluster alone is deliberately not a signal
    here, matching :func:`fedcourtsai.corpus.snapshot_links_opinion_cluster`'s
    callers: a motions-panel opinion can publish on a still-pending appeal.)
    Pure, over the fresh full-docket payload in either shape
    (:func:`entry_descriptions`). Used to keep decided-looking cases out of
    the forward-prediction queue — a forward cell on a decided case is a
    mislabeled back-test with unrestricted retrieval, so any predictor could
    trivially read the outcome.
    """
    descriptions = entry_descriptions(docket)
    last_description = descriptions[-1] if descriptions else ""
    if last_description and _TERMINAL_ENTRY_RE.search(last_description):
        return f"latest docket entry reads as terminal: {last_description!r}"
    return None


def snapshot_shows_disposition(docket: Mapping[str, Any]) -> str | None:
    """A terminal disposition visible **anywhere** in the snapshot, or ``None``.

    The whole-snapshot counterpart of :func:`termination_signal` for the
    forward-cell provisioning leakage guard. The question here is not docket
    *pendency* (:func:`termination_signal`'s latest-entry, reactivation-aware
    rule) but whether the outcome is *visible in the snapshot a forward cell
    would read* — so it deliberately scans every entry and takes no reactivation
    exception: once a disposition order sits in the snapshot, a predictor can
    read it even if a later filing reopened the docket. Uses the same high-recall
    :data:`_TERMINAL_ENTRY_RE` as the routing backstop (a false positive only
    parks a cell snapshot-less), which catches the shapes the resolver
    deliberately omits — the cert-before-judgment grant, the merits judgment,
    "Judgment Issued" — that trailing administrative notations ("Application ...
    denied as moot") hide from the latest-entry rule. Pure, over either payload
    shape (:func:`entry_descriptions`).
    """
    for description in entry_descriptions(docket):
        if _TERMINAL_ENTRY_RE.search(description):
            return f"snapshot entry reads as terminal: {description!r}"
    return None


# The one :data:`_TERMINAL_ENTRY_RE` shape that is a merits cell's own opening
# rather than its outcome: a cert-before-judgment GRANT opens a merits
# proceeding exactly as an ordinary grant does, so a merits cell's snapshot
# necessarily carries it. Its denial/dismissal siblings stay terminal for the
# merits scan, since neither leaves anything to argue.
_CBJ_GRANT_RE = re.compile(
    r"^(?:the\s+)?petitions? for (?:a )?writs? of certiorari before judgment "
    r"(?:are |is )?granted",
    re.IGNORECASE,
)


def snapshot_shows_judgment(docket: Mapping[str, Any]) -> str | None:
    """A **merits** outcome visible anywhere in the snapshot, or ``None``.

    The merits-event counterpart of :func:`snapshot_shows_disposition` for the
    forward-cell provisioning guard, which is keyed on the event because one
    docket carries several events' outcomes at once. It keeps that function's
    high-recall :data:`_TERMINAL_ENTRY_RE` rather than narrowing to the
    deterministic merits parser: the parser is deliberately conservative (a
    miss there costs one unparsed row in a descriptive count), while a miss
    *here* hands a forward cell its answer, so the two failure costs point in
    opposite directions and the guard must take the wider net. Every terminal
    shape the cert scan catches — "Opinion Issued", "Judgment Issued", a case
    termination, a dismissal — is a decided merits docket too.

    One branch is dropped: the **cert-before-judgment grant**, which is the
    order that mints the merits event rather than a disclosure of its outcome.
    The plain cert grant needs no exclusion because it matches no branch of the
    regex at all — only the resolver sees it, and the merits scan does not run
    the resolver.
    """
    for description in entry_descriptions(docket):
        if _CBJ_GRANT_RE.search(description):
            continue
        if _TERMINAL_ENTRY_RE.search(description):
            return f"snapshot entry reads as terminal: {description!r}"
    return None


# High-recall interim disposal shapes, for the routing and provisioning
# backstops on APPLICATION-FORM dockets only. Deliberately wider than the
# resolving vocabulary (`interim_signals.match_interim_disposition`), which
# anchors on the word "application": a disposing order can name the relief
# instead ("Stay granted pending disposition", "The motion for an injunction
# ... is denied"), leaving the row unresolved while the outcome sits legible in
# the snapshot — on the cert side that single point of failure is covered by
# `_TERMINAL_ENTRY_RE`, which matches no application phrasing. A match here
# never records an outcome; it only diverts the forward queue
# (`predict_skipped_decided`) or refuses provisioning, so a false positive (a
# recital of a lower court's stay denial) parks a cell — the cheap failure the
# `_TERMINAL_ENTRY_RE` doctrine already endorses. Form-keyed by the callers, so
# a cert docket's stay-order recital can never refuse a legitimate cert cell.
_INTERIM_DISPOSAL_RE = re.compile(
    r"\b(?:applications?|stays?|injunctions?|vacaturs?|motions?)\b[^.]{0,200}?"
    r"\b(?:granted|denied|dismissed|withdrawn)\b",
    re.IGNORECASE,
)


def interim_disposal_signal(docket: Mapping[str, Any]) -> str | None:
    """An interim disposal legible **anywhere** in an application docket's payload.

    The application-form counterpart of :func:`snapshot_shows_disposition` —
    leakage semantics, so it scans every entry and takes no reactivation
    exception — used by the live routing's decided-guard and the forward-cell
    provisioning refusal on application dockets only (the caller keys on
    :func:`fedcourtsai.corpus.is_scotus_application_form`). Pure, over either
    payload shape (:func:`entry_descriptions`).
    """
    for description in entry_descriptions(docket):
        if _INTERIM_DISPOSAL_RE.search(description):
            return f"snapshot entry reads as an interim disposal: {description!r}"
    return None


@dataclass(frozen=True)
class UnrecordedOutcome:
    """An open event that appears decided but cannot be recorded deterministically.

    Carried out of the library so the workflow can surface it on the
    pipeline-runs dashboard; ``reason`` explains why automatic recording was
    declined. ``reason`` must stay a fixed-vocabulary string (the literals in
    :func:`detect_resolution`, interpolating only closed-enum values and
    event ids — slugified ``[a-z0-9._-]`` strings minted by
    :func:`fedcourtsai.ids.event_id`, never raw text): it is
    rendered into a GitHub issue body, so raw docket text — e.g.
    :func:`termination_signal` output — must never route here.
    """

    case_id: str
    court_id: str
    docket_id: int
    event_id: str
    disposition: Disposition | None
    date_decided: date | None
    reason: str


@dataclass(frozen=True)
class Resolution:
    """The outcome of detection for one case in one refresh.

    ``outcomes`` maps each deterministically-resolved event id to the
    :class:`Outcome` to write; ``unrecorded`` lists the events left for triage.
    """

    outcomes: dict[str, Outcome] = field(default_factory=dict)
    unrecorded: tuple[UnrecordedOutcome, ...] = ()


def disposition_basis(docket: Mapping[str, Any]) -> Literal["standard", "mootness"]:
    """What drove the payload's disposition wording — the ``Outcome`` basis marker.

    Pure over the fresh full-docket payload (either shape, via
    :func:`entry_descriptions`), so the refresh channels compute it from the
    payload they already hold and pass it into :func:`resolve_case`. "mootness"
    when the first disposition-bearing entry is mootness practice
    (:func:`fedcourtsai.pipeline.cert_signals.mootness_disposition` — a
    Munsingwear vacatur or a dismissal as moot): the label then tracks vacatur
    practice rather than cert-worthiness, and scoring segments the cell into
    the leaderboard's procedural stratum. On the REST shape the recorded
    disposition can come from upstream fields or cert dates rather than entry
    text, so the basis attaches to the first disposition-bearing *entry* — the
    same first-entry rule the live resolver applies.
    """
    for text in entry_descriptions(docket):
        if match_disposition_signal(text) is not None:
            return "mootness" if mootness_disposition(text) else "standard"
    return "standard"


def resolution_signals(
    distribution_count: int | None, cvsg_date: date | None
) -> ResolutionSignals | None:
    """The live-parsed docket signals to freeze onto a resolving event's outcome.

    Takes the two values rather than a row: the ingest-stage and the persisted row
    are different models and both reach this, so passing the fields keeps one rule
    in one place without coupling it to either.

    ``None`` when the proceedings were never live-parsed, which is exactly what an
    absent ``distribution_count`` means — the corpus treats it as the coverage
    sentinel for the whole live-signal family, so emitting a block there would
    assert an observation nobody made.
    """
    if distribution_count is None:
        return None
    return ResolutionSignals(distribution_count=distribution_count, cvsg_date=cvsg_date)


def _build_outcome(
    row: CorpusRow,
    event_id: str,
    basis: Literal["standard", "mootness"],
    *,
    interim: bool = False,
) -> Outcome:
    """Construct the ground-truth ``Outcome`` from a decided, machine-readable row.

    ``resolved_at`` is the :func:`corpus.resolution_date` — for a SCOTUS petition
    the cert-stage decision date, so a granted petition's outcome is stamped when
    cert was granted, not at the merits termination; for an application docket
    the cert dates are empty by construction, so it is the disposing entry's
    date the interim resolver latched at ingest. ``interim`` marks an
    interim-stage recording, whose outcome never carries the ``signals`` block:
    those are the cert docket's resolution signals (distribution count, CVSG),
    observations nobody makes on an application.
    """
    resolved_at = corpus.resolution_date(row)
    assert row.disposition is not None and resolved_at is not None
    return Outcome(
        case_id=row.case_id,
        event_id=event_id,
        resolved_at=resolved_at,
        actual_disposition=row.disposition,
        actual_granted=granted_flag(row.disposition),
        signals=None if interim else resolution_signals(row.distribution_count, row.cvsg_date),
        source=row.citations[0] if row.citations else None,
        disposition_basis=basis,
    )


def build_merits_outcome(
    case_id: str,
    event_id: str,
    judgment: Judgment,
    decided: date,
    *,
    distribution_count: int | None,
    cvsg_date: date | None,
    source: str | None,
) -> Outcome:
    """Construct the merits ground truth from a parsed judgment and its date.

    Takes the values rather than a row for the same reason
    :func:`resolution_signals` does: the ingest-stage row (live detection) and
    the persisted corpus row (the cascade's replay of an already-resolved
    event) are different models and both reach this, so passing the fields
    keeps one mapping in one place.

    The mapping is the least-corrupting one the vocabularies allow, and each
    choice is deliberate:

    - ``actual_disposition`` is :attr:`Disposition.other` — the Judgment values
      are deliberately not Dispositions (forcing one onto the cert binary would
      corrupt the comparability anchor, per the ``Judgment`` docstring), so the
      cert vocabulary's catch-all records that no cert label applies and
      ``judgment`` carries the result. The stage axis keeps such outcomes out
      of every cert-vocabulary figure.
    - ``actual_granted`` is the **declared merits binary** — the judgment
      disturbed the decision below (:func:`~fedcourtsai.pipeline.judgment.judgment_disturbed`) —
      matching ``Prediction.probability``'s merits meaning, P(disturbed), so
      the Brier formula scores every stage unchanged. A DIG and an equally
      divided affirmance record 0: both leave the judgment below standing.
    - ``votes`` stays empty and ``vote_provenance`` absent ("nobody looked"),
      deliberately: the terminal entry's authorship recital names at most the
      opinion's author and never the participating count that
      ``VoteProvenance`` requires as the aggregation denominator, so an honest
      provenance block cannot be built from docket text — and a vote list
      without one would be illegible. A real vote source (an order list, the
      opinion) is the seam that populates these, not this writer;
      :func:`~fedcourtsai.pipeline.judgment.opinion_author` stays advisory.
    - ``resolved_at`` is ``decided`` — the judgment entry's own docket date
      (``merits_decided``); detection refuses to resolve on an undated parse
      rather than stamping a guess.
    """
    return Outcome(
        case_id=case_id,
        event_id=event_id,
        resolved_at=decided,
        actual_disposition=Disposition.other,
        actual_granted=int(judgment_disturbed(judgment)),
        judgment=judgment,
        signals=resolution_signals(distribution_count, cvsg_date),
        source=source,
    )


# The event kinds the case-level disposition may resolve: the case-baseline
# petition/appeal events (`evt-<kind>-<slug>`, so the kind is the id's first
# segment). An entry-pinned event of another kind (a stay motion on a cert
# docket) resolves on its own filing's terms, and letting it inherit the
# docket's cert disposition writes the petition's outcome onto a motion — the
# resolved-sequentially shape of exactly that failure sits in the committed
# ledger. An application docket's motion/interim baseline is likewise
# deliberately outside this tuple: its disposition resolves under the interim
# standard, routed by the explicit interim stage (`_interim_disposition_target`)
# rather than by any id-prefix fallback, so it can never inherit the cert rule.
CASE_BASELINE_ID_PREFIXES = tuple(
    f"evt-{kind.value}-" for kind in (EventKind.petition, EventKind.appeal)
)


def _cert_disposition_target(
    open_event_ids: list[str], stages: Mapping[str, Stage | None]
) -> str | None:
    """The one open event the case-level disposition attributes to, or ``None``.

    The corpus row carries exactly one case-level disposition, and on a cert
    docket it is the **cert**-stage decision
    (:func:`fedcourtsai.corpus.resolution_date` is the petition-stage cert date
    on a SCOTUS docket), so cert is the only stage routed here; an interim
    disposition has a different case-level source (the application's own
    resolving entry, matched by the interim vocabulary at ingest), and the
    sibling stage → disposition-source branch that routes it is
    :func:`_interim_disposition_target`.

    Stage first: the open event tagged ``cert`` claims the disposition outright,
    even with other (non-cert) events open beside it — those resolve on their
    own filings' terms and simply stay open. Two events sharing the cert stage
    is ambiguous, so nothing is attributed. Where no event carries the cert
    stage, the stage-less fallback is the case-baseline id-prefix rule: a
    *lone* open event with no recorded stage and a petition/appeal id prefix.
    An event carrying an explicit non-cert stage never inherits the cert
    disposition, whatever its id.
    """
    cert_staged = [eid for eid in open_event_ids if stages.get(eid) == Stage.cert]
    if len(cert_staged) == 1:
        return cert_staged[0]
    if cert_staged:
        return None  # two events share the cert stage: no unambiguous target
    if (
        len(open_event_ids) == 1
        and stages.get(open_event_ids[0]) is None
        and open_event_ids[0].startswith(CASE_BASELINE_ID_PREFIXES)
    ):
        return open_event_ids[0]
    return None


def _cert_already_attributed(
    resolved_event_ids: list[str], stages: Mapping[str, Stage | None]
) -> bool:
    """Whether a **resolved** event already carries the case-level cert disposition.

    The same event shapes :func:`_cert_disposition_target` routes the
    disposition to — a cert-staged event, or a stage-less case-baseline one —
    but over the resolved set: once such an event has closed, the row-level
    decided signals (the cert date, the latched disposition) are the record of
    *that* resolution, not news about any event still open.
    """
    return any(
        stages.get(event_id) == Stage.cert
        or (stages.get(event_id) is None and event_id.startswith(CASE_BASELINE_ID_PREFIXES))
        for event_id in resolved_event_ids
    )


def _interim_disposition_target(
    open_event_ids: list[str], stages: Mapping[str, Stage | None]
) -> str | None:
    """The one open event an application's interim disposition attributes to, or ``None``.

    The interim sibling of :func:`_cert_disposition_target`: on an application
    docket the row's case-level disposition comes from the application's own
    disposing entry (the interim vocabulary,
    :func:`fedcourtsai.pipeline.interim_signals.match_interim_disposition`), so
    it belongs to the open event whose ``stage`` is ``interim`` — the
    motion-kind baseline the discovery mint stamps. Two events sharing the
    stage is ambiguous, so nothing is attributed. There is deliberately **no
    stage-less fallback** here: the only stage-less baseline an application
    docket carries is a historical spelling's petition-kind event, whose
    cert-shaped id must never receive an interim disposition.
    """
    interim_staged = [eid for eid in open_event_ids if stages.get(eid) == Stage.interim]
    if len(interim_staged) == 1:
        return interim_staged[0]
    return None


def detect_resolution(
    row: CorpusRow,
    court_id: str,
    docket_id: int,
    open_event_ids: list[str],
    disposition_basis: Literal["standard", "mootness"] = "standard",
    *,
    stages: Mapping[str, Stage | None] | None = None,
    resolved_event_ids: list[str] | None = None,
) -> Resolution:
    """Decide how each open event resolves, given the refreshed corpus row.

    Pure: no I/O. Returns deterministic outcomes to write and unrecorded
    outcomes for the rest. An undecided docket, or one with no open events, resolves to an
    empty :class:`Resolution` (nothing to do). ``stages`` maps each event id
    to its recorded decision stage (from the corpus event rows) and drives the
    stage-routed attribution — :func:`_cert_disposition_target` on a cert
    docket, :func:`_interim_disposition_target` on an application docket;
    omitted, every event reads as stage-less, so on a cert docket only the
    case-baseline prefix fallback applies and on an application docket nothing
    is ever attributed.
    When the stage identifies the target unambiguously *and* the disposition is
    recordable, the other open events are neither resolved nor surfaced for
    triage — they stay open on their own filings' terms, still tracked by the
    corpus open-event reads rather than silently dropped. An unreadable or
    undated disposition still surfaces **every** open event: with nothing
    recordable, whole-docket triage is the conservative call.

    A row carrying a parsed merits judgment (``merits_judgment`` /
    ``merits_decided``, latched at ingest by the shared parser) resolves the
    case's lone open **merits-stage** event instead
    (:func:`build_merits_outcome`); an undated parse surfaces that event for
    triage, since ``resolved_at`` is never guessed.

    ``resolved_event_ids`` lists the case's already-closed events and gates the
    one clean no-op: when no open event can claim the disposition, a resolved
    event already carries it (:func:`_cert_already_attributed`), and the row
    still tells that resolution's story — a granted-set disposition with no
    docket-level decision date — the decided-looking row is the record of the
    earlier grant: the shape every re-poll of a retained granted docket
    presents, its petition event closed and the minted merits event open (and
    no judgment parsed yet), so
    nothing is recorded and nothing is surfaced. Without it a retained granted
    docket would re-surface an unrecorded outcome on every poll until
    judgment. The no-op is deliberately that narrow: a latched ``date_decided``
    (a termination arriving upstream without a judgment-shaped entry) or a
    disposition outside the
    granted set (a DIG relabeled ``dismissed``, an upstream correction) is news
    no detection rule reads, so those shapes fall through to the
    conservative triage surface instead of being absorbed.
    """
    if not open_event_ids or not appears_decided(row):
        return Resolution()

    readable = is_machine_readable(row.disposition) and corpus.resolution_date(row) is not None
    # An application docket never takes the cert rule, whatever its baseline's
    # current shape: its disposition resolves under the interim standard, routed
    # to the interim-stage baseline by the sibling target rule. Keyed on the
    # tolerant docket-form recognizer so every recorded application spelling is
    # covered, not just the strict `YYAnnn` the baseline mint and the relabel
    # migration key on.
    application = row.court == "scotus" and corpus.is_scotus_application_form(row.docket_number)
    target = (
        _interim_disposition_target(open_event_ids, stages or {})
        if application
        else _cert_disposition_target(open_event_ids, stages or {})
    )
    if readable and target is not None:
        return Resolution(
            outcomes={target: _build_outcome(row, target, disposition_basis, interim=application)}
        )

    # The merits branch: a retained granted docket whose refreshed row carries
    # a parsed judgment (latched at ingest via the shared parser) resolves its
    # lone open merits-stage event from the columns — the row-level facts, the
    # same discipline as the cert branch, so detection stays pure and
    # deterministic. Other open events (an entry-pinned motion) stay open on
    # their own filings' terms, exactly as under the cert stage routing. A
    # judgment parsed from an undated entry has no `resolved_at` to stamp, so
    # it surfaces for triage rather than being recorded on a guessed date.
    merits_staged = [eid for eid in open_event_ids if stages and stages.get(eid) == Stage.merits]
    if not application and row.merits_judgment is not None and len(merits_staged) == 1:
        merits_event = merits_staged[0]
        # The column is blob-tolerant TEXT whose readers re-validate against the
        # vocabulary rather than failing the row (the field's own contract, and
        # the same guard the cascade's replay applies): an out-of-vocabulary
        # value surfaces for triage, never a crash in the poll.
        parsed = _known_judgment(row.merits_judgment)
        if parsed is not None and row.merits_decided is not None:
            outcome = build_merits_outcome(
                row.case_id,
                merits_event,
                parsed,
                row.merits_decided,
                distribution_count=row.distribution_count,
                cvsg_date=row.cvsg_date,
                source=row.citations[0] if row.citations else None,
            )
            return Resolution(outcomes={merits_event: outcome})
        return Resolution(
            unrecorded=(
                UnrecordedOutcome(
                    case_id=row.case_id,
                    court_id=court_id,
                    docket_id=docket_id,
                    event_id=merits_event,
                    disposition=row.disposition,
                    date_decided=row.date_decided,
                    reason=(
                        f"merits judgment {row.merits_judgment!r} is out of vocabulary"
                        if parsed is None
                        else (
                            f"merits judgment parsed ({row.merits_judgment}) but its docket "
                            "entry is undated; no resolved_at can be stamped"
                        )
                    ),
                ),
            )
        )

    # A retained granted docket re-polls with its cert disposition already
    # attributed to the (resolved) cert event and only the merits event open:
    # a clean no-op, not a triage case. Narrow by design — a latched
    # date_decided or a mutated disposition falls through to triage.
    if (
        not application
        and target is None
        and row.date_decided is None
        and row.disposition in GRANTED_DISPOSITIONS
        and _cert_already_attributed(resolved_event_ids or [], stages or {})
    ):
        return Resolution()

    if application and readable:
        reason = (
            f"decided application docket ({row.disposition}) but no lone open "
            "interim-stage event to attribute the interim disposition to; an "
            "application's disposition belongs to its interim baseline only"
        )
    elif not is_machine_readable(row.disposition):
        reason = "docket appears decided but its disposition is not machine-readable"
    elif corpus.resolution_date(row) is None:
        reason = "disposition is machine-readable but the docket carries no decision date"
    elif len(open_event_ids) == 1:
        reason = (
            f"docket decided ({row.disposition}) but the one open event "
            f"({open_event_ids[0]}) forecasts a different filing; the case-level "
            "disposition belongs to the case-baseline event only"
        )
    else:
        reason = (
            f"docket decided ({row.disposition}) but {len(open_event_ids)} events are open; "
            "the case-level disposition cannot be attributed to one event"
        )
    unrecorded = tuple(
        UnrecordedOutcome(
            case_id=row.case_id,
            court_id=court_id,
            docket_id=docket_id,
            event_id=event_id,
            disposition=row.disposition,
            date_decided=row.date_decided,
            reason=reason,
        )
        for event_id in open_event_ids
    )
    return Resolution(unrecorded=unrecorded)


def record_outcomes(
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
    resolution: Resolution,
) -> list[str]:
    """Write each deterministic ``outcome.json`` and close its event in the corpus.

    The derived judgment (``outcome.json``) lands in the git ledger; the event's
    open/resolved state is a raw fact, so the matching ``CorpusEvent`` is flipped
    ``resolved`` in the packed corpus. The event's ``event.yaml`` is materialized
    beside the outcome from the same corpus row: an outcome committed without its
    event definition is a referential orphan the offline ``validate`` gate
    rejects, and unlike the agent cells (whose workflows run ``materialize-event``
    first) the deterministic writers commit straight from this working tree, so
    this is the only place that can guarantee the pair. Returns the event ids
    written, sorted. Idempotent: a resolved event is filtered out upstream by
    :func:`open_events` (which reads the same corpus flag), so a re-run never
    duplicates or overwrites a recorded outcome.
    """
    case = CasePaths(data_root, court_id, docket_id)
    case_id = ids.case_id(court_id, docket_id)
    written: list[str] = []
    with corpus.connect(corpus_db_path) as conn:
        events_by_id = {e.event_id: e for e in corpus.events_for_case(conn, case_id)}
        for event_id, outcome in sorted(resolution.outcomes.items()):
            event = events_by_id.get(event_id)
            if event is None:
                # Fail loud, before the outcome is written: an outcome without
                # its event definition is exactly the orphan the gate rejects,
                # and a resolution for an event the corpus does not hold is an
                # internal inconsistency (the open-events read and this write
                # use the same table), not upstream degradation.
                raise RuntimeError(
                    f"corpus holds no event {event_id!r} for {case_id}; "
                    "refusing to write an orphaned outcome"
                )
            write_json(case.event(event_id).outcome, outcome)
            write_yaml(
                case.event(event_id).event_file,
                PredictableEvent(
                    event_id=event.event_id,
                    case_id=event.case_id,
                    kind=event.kind,
                    stage=event.stage,
                    title=event.title,
                    description=event.description,
                    docket_entry_id=event.docket_entry_id,
                    opened_at=event.opened_at,
                    decision_target=event.decision_target,
                    resolved=True,  # the outcome beside it is the resolution
                ),
            )
            # An event with a realized outcome is, by definition, resolved: close
            # it in the corpus so the next open_events read stops queuing it.
            corpus.set_event_resolved(conn, case_id, event_id)
            written.append(event_id)
    return written


def merits_event_for(row: CorpusRow, resolution: Resolution) -> corpus.CorpusEvent | None:
    """The open merits event a freshly-recorded cert grant implies, or ``None``.

    Pure. A grant in the merits-proceeding subset (:data:`_MERITS_PROCEEDING` —
    ``gvr`` and ``summary-reversal`` terminate at the cert order and mint
    nothing) puts the case on the merits docket, so the grant that closes the
    petition event is also the birth of the next predictable thing: the
    judgment. The grant order is the filing that opened it (``kind=order``),
    the merits standard governs it (``stage=merits``), and it opens on the
    grant date the outcome was stamped with. Keyed on the outcomes recorded in
    *this* resolution — not the row's latched disposition — so it fires exactly
    once, at cert-grant detection, and a later re-poll of the granted docket
    (whose resolution is an empty no-op) never re-mints.
    """
    if row.court != "scotus":
        # The merits-event contract is SCOTUS-only: a cert grant is the only
        # grant that opens a merits proceeding before this Court, but the
        # shared resolution seam also records granted dispositions on circuit
        # dockets (pull refreshes any court), and those must not receive a
        # cert-vocabulary merits event.
        return None
    grant = next(
        (
            outcome
            for outcome in resolution.outcomes.values()
            if outcome.actual_disposition in _MERITS_PROCEEDING
        ),
        None,
    )
    if grant is None:
        return None
    return corpus.CorpusEvent(
        event_id=MERITS_EVENT_ID,
        case_id=row.case_id,
        court=row.court,
        kind=EventKind.order,
        stage=Stage.merits,
        # The same fallback chain the baseline event uses, so a payload with no
        # petitioner title never yields an empty-titled event definition.
        title=row.case_name or row.docket_number or row.case_id,
        description="Disposition of the judgment below, following the cert grant.",
        opened_at=grant.resolved_at,
        decision_target="judgment",
        resolved=False,
    )


def mint_merits_event(
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
    row: CorpusRow,
    resolution: Resolution,
) -> str | None:
    """Record the merits event a just-recorded cert grant opens; return its id.

    The write half of :func:`merits_event_for`: upsert the corpus event row —
    idempotent by ``(case_id, event_id)``, and ``resolved`` MAX-latches, so a
    re-detection can neither duplicate the event nor reopen a merits event a
    later judgment has closed — and materialize its ``event.yaml`` in the
    ledger, stamped with the **post-upsert** resolved state so the ledger file
    honours the same latch (a re-mint after the merits event has closed must
    not regress the committed definition to open). ``record_outcomes``
    materializes ``event.yaml`` only beside a
    written outcome, but the ledger's event definitions are
    materialized-on-touch and the merits event is *born at* an outcome write:
    the deterministic writers commit straight from this working tree, so this
    is the only seam that can put the open event definition in the git tree it
    ships with (an open ``event.yaml`` with ``resolved=False`` is the same
    shape ``materialize-event`` provisions for the agent cells).
    """
    event = merits_event_for(row, resolution)
    if event is None:
        return None
    with corpus.connect(corpus_db_path) as conn:
        corpus.upsert_events(conn, [event])
        stored = {e.event_id: e for e in corpus.events_for_case(conn, event.case_id)}[
            event.event_id
        ]
    write_yaml(
        CasePaths(data_root, court_id, docket_id).event(event.event_id).event_file,
        PredictableEvent(
            event_id=stored.event_id,
            case_id=stored.case_id,
            kind=stored.kind,
            stage=stored.stage,
            title=stored.title,
            description=stored.description,
            docket_entry_id=stored.docket_entry_id,
            opened_at=stored.opened_at,
            decision_target=stored.decision_target,
            resolved=stored.resolved,
        ),
    )
    return event.event_id


def resolve_case(
    corpus_db_path: Path,
    data_root: Path,
    row: CorpusRow,
    court_id: str,
    docket_id: int,
    disposition_basis: Literal["standard", "mootness"] = "standard",
) -> Resolution:
    """Detect and record resolution for one freshly-refreshed case.

    Reads the case's open events from the corpus (:func:`open_events`) along with
    every event's recorded decision stage and resolved flag (which route the
    case-level disposition — see :func:`_cert_disposition_target` — and gate the
    already-attributed no-op), decides
    each (:func:`detect_resolution`), writes the deterministic outcomes and closes
    their corpus events (:func:`record_outcomes`), and returns the full
    :class:`Resolution` so the caller can surface the unrecorded rest.

    A recorded cert grant then mints the case's open merits event
    (:func:`mint_merits_event`) — strictly *after* the outcome attribution, so
    the detection pass that resolves the petition never sees the merits event
    among the open set (the single-open-event and stage-routing logic judge the
    docket as it stood when the grant was detected).
    """
    open_event_ids = open_events(corpus_db_path, court_id, docket_id)
    stages: dict[str, Stage | None] = {}
    resolved_event_ids: list[str] = []
    if open_event_ids:  # the corpus exists — open_events read from it
        with corpus.connect(corpus_db_path) as conn:
            for event in corpus.events_for_case(conn, ids.case_id(court_id, docket_id)):
                stages[event.event_id] = event.stage
                if event.resolved:
                    resolved_event_ids.append(event.event_id)
    resolution = detect_resolution(
        row,
        court_id,
        docket_id,
        open_event_ids,
        disposition_basis,
        stages=stages,
        resolved_event_ids=resolved_event_ids,
    )
    record_outcomes(corpus_db_path, data_root, court_id, docket_id, resolution)
    mint_merits_event(corpus_db_path, data_root, court_id, docket_id, row, resolution)
    return resolution
