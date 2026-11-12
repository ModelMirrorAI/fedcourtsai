"""Unforecast outcomes: the grants and application rulings no forecast preceded.

The selection-recall readout. The missed-forecast monitor
(:mod:`fedcourtsai.pipeline.missed`) asks whether the pipeline delivered what
it *owed*, so a petition the salience gate never selected is declined by
design there and never named. This census asks the other question: of the
outcomes worth having forecast, which did selection leave out? It reads the
outcome first — the Court's order, which is no input to selection — and then
looks for any committed prediction on the case dated on or before the day the
matter resolved.

Two populations, each read off the corpus row:

- **Cert.** Every SCOTUS modern cert docket whose disposition is grant-family
  (:data:`fedcourtsai.schemas.GRANT_FAMILY_DISPOSITIONS`) and whose
  petition-stage resolution (:func:`fedcourtsai.corpus.resolution_date`) falls
  in the window. In-forma-pauperis petitions are counted apart: the scope rule
  excludes them below the merits stage, so they are never part of the recall.
- **Interim.** Every application resolved in the window that the Court
  referred to the full bench, or that the substantive-application test admits
  (:func:`fedcourtsai.pipeline.interim_signals.is_predictable_application`).
  An application referred to the Court that the test read as not substantive
  is flagged, since that is the interim analogue of a mislabeled petitioner.

**The alarms.** An unforecast grant on a paid petition raises one when the row
sits in the ``federal`` band (the carve-in selects that band whole, so the
label arrived too late or the cell never ran), or when it sits outside the
band and a reading looser than any registered caption rule places the federal
government on the petitioner side (:func:`federal_signals`). The signals are
for a person to read, never a selection input: one of them reads counsel
entries a docket can gain after its outcome. The band is the active scorer's
reading of the row as it stands now, not as it stood while the petition was
pending. A petition no scheduled predict round could have reached between its
filing and its outcome is listed and counted in the recall, and raises
neither. The third alarm is the Term-to-date reachable recall under its floor.

**Recall** is grant-family paid petitions with a prior forecast over all
grant-family paid petitions, in the window and over the October Term of
``until`` to date; the *reachable* recall drops from the denominator the
unforecast outcomes selection could never have reached (out of scope, or
resolved before a round), and is the one the alarm reads. The Term opens on
1 October (:func:`fedcourtsai.supremecourt.october_term_year`), so a
late-September long-conference grant counts in the outgoing Term's figure. A
grant-family row with no cert-grant date is left out: its only date is the
docket's termination, months after the grant. Both figures are
outcome-selected by construction and belong on no board: they say whether
selection is finding the grants, and nothing about any predictor.

**What a prior forecast is.** A ``prediction.json`` under any event of the
case whose run id is dated on or before the resolution day. Same-day counts,
because both are dated to the day and a morning round precedes an order list;
that is the under-report direction for the alarm. Reads the corpus index and
the committed ledger; reads no snapshot and writes nothing.
"""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..paths import CasePaths
from ..schemas import GRANT_FAMILY_DISPOSITIONS
from ..supremecourt import october_term_year
from .caption import classify_petitioner_v2, petitioner_caption
from .interim_signals import ApplicationKind
from .missed import had_a_scheduled_round
from .salience import salience_band

#: The band the federal carve-in selects under; a row already in it needs no signal.
FEDERAL_BAND = "federal"

#: Term-to-date reachable recall below this raises the alarm. Set under the
#: salience replay's 0.76-0.81 at the shipped cap (``config/tracking.yaml``), so
#: the cap's own cost does not trip it. The replay's denominator is its own
#: reconstructable pool, so the two figures are neighbours, not the same
#: quantity, and the alarm is a prompt to read the list, not a test.
RECALL_ALARM_BELOW = 0.70

#: The fewest reachable grant-family paid petitions the recall is alarmed over.
#: A share of a few dozen outcomes is noisy and is re-read on every run: at a
#: true recall of 0.78 a reading under the floor is still roughly a one-in-ten
#: event at this size.
RECALL_ALARM_MIN_OUTCOMES = 30


class UnforecastReason(StrEnum):
    """Why no forecast preceded an outcome, first match wins."""

    out_of_scope = "out_of_scope"
    """A predict-scope rule refuses the row (the rule's own reason is in ``detail``)."""
    resolved_before_a_round = "resolved_before_a_round"
    """No scheduled predict round fell certainly between the filing and the outcome."""
    not_scored = "not_scored"
    """In scope, but the salience pass never scored the row."""
    not_selected = "not_selected"
    """Scored and left unselected by the salience pass."""
    selected_unforecast = "selected_unforecast"
    """Selected, and still no prediction was committed before the outcome."""


#: The reasons that put an outcome beyond anything selection could have done.
_UNREACHABLE = frozenset({UnforecastReason.out_of_scope, UnforecastReason.resolved_before_a_round})


class FederalSignal(StrEnum):
    """A loose reading that places the federal government on the petitioner side."""

    sg_office_counsel = "sg_office_counsel"
    """The Solicitor General's office appears for a petitioner, of record or not."""
    federal_petitioner_party = "federal_petitioner_party"
    """A petitioner-side party name reads federal, anywhere in the party block."""


#: A relator's caption ("ex rel."). The sovereign named before the relator is a
#: party on the petitioner side of every such petition and the petitioner in
#: none, so the party reading is not asked of one, whichever sovereign it is.
_EX_REL_RE = re.compile(r"\bex rel\b\.?", re.IGNORECASE)


class UnforecastOutcome(BaseModel):
    """One outcome that no committed forecast preceded."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    disposition: str
    resolved_at: date
    reason: UnforecastReason
    detail: str | None = Field(
        default=None,
        description="The predict-scope rule's reason for `out_of_scope`; the two dates "
        "for `resolved_before_a_round`",
    )
    selected: bool = Field(description="The row's salience selection latch as it stands now")
    salience_version: str | None
    salience_score: float | None
    band: str | None = Field(
        default=None, description="The active scorer's band for the row; cert rows only"
    )
    federal_signals: list[FederalSignal] = Field(
        default_factory=list,
        description="Loose federal-petitioner readings on a paid petition outside the "
        "`federal` band; empty on every other row",
    )
    application_kind: str | None = Field(
        default=None, description="The stored reading of the ask; applications only"
    )
    referred_to_court: bool | None = Field(
        default=None, description="Whether the application was referred to the full Court"
    )
    referred_not_substantive: bool = Field(
        default=False,
        description="An application the Court referred to the full bench that the "
        "substantive-application test does not admit",
    )


class Recall(BaseModel):
    """Grant-family paid petitions with a prior forecast, over all of them."""

    model_config = ConfigDict(extra="forbid")

    since: date
    until: date
    outcomes: int = Field(ge=0, description="Grant-family paid petitions resolved in the span")
    forecast: int = Field(ge=0, description="Those a committed forecast preceded")
    recall: float | None = Field(description="`forecast / outcomes`; null on an empty span")
    reachable_outcomes: int = Field(
        ge=0,
        description="`outcomes` less the unforecast ones selection could never have "
        "reached: `out_of_scope` and `resolved_before_a_round`",
    )
    reachable_recall: float | None = Field(
        description="`forecast / reachable_outcomes`, the figure the recall alarm reads; "
        "null on an empty span"
    )


class UnforecastReport(BaseModel):
    """The unforecast-outcomes census over one resolution window."""

    model_config = ConfigDict(extra="forbid")

    since: date
    until: date
    window: Recall
    term_to_date: Recall = Field(
        description="The same recall from the opening of `until`'s October Term through `until`"
    )
    cert_unforecast: list[UnforecastOutcome] = Field(
        description="Grant-family paid petitions in the window with no prior forecast"
    )
    ifp_grants_unforecast: list[UnforecastOutcome] = Field(
        description="Grant-family in-forma-pauperis petitions in the window with no prior "
        "forecast; excluded from the recall, since the scope rule excludes them"
    )
    interim_outcomes: int = Field(
        ge=0, description="Referred or substantive applications resolved in the window"
    )
    interim_unforecast: list[UnforecastOutcome] = Field(description="Those with no prior forecast")
    alarms: list[str] = Field(
        description="Each alarm condition that holds, in words; empty = quiet"
    )


def federal_signals(row: corpus.CorpusRow) -> list[FederalSignal]:
    """The loose federal-petitioner readings that fire on ``row``.

    Deliberately wider than a registered caption rule, because a false positive
    here costs a minute of reading: the office anywhere on the petitioner side
    (the reading ``caption-v3`` was set aside for, since a docket can gain it
    after the outcome), and the federal caption grammar run over every
    petitioner-side party name rather than the lead caption alone — except on
    a relator's caption, where the United States is always such a party.
    """
    from .counsel import sg_office_annotations  # noqa: PLC0415 - counsel<-party<-caption cycle

    signals: list[FederalSignal] = []
    if sg_office_annotations(row, None).petitioner == "yes":
        signals.append(FederalSignal.sg_office_counsel)
    if not _EX_REL_RE.search(petitioner_caption(row)) and any(
        entry.role == corpus.CounselRole.petitioner
        and classify_petitioner_v2(entry.party) == "federal"
        for entry in row.counsel
    ):
        signals.append(FederalSignal.federal_petitioner_party)
    return signals


def forecast_preceded(data_root: Path, case_id: str, resolved_at: date) -> bool:
    """Whether the ledger holds a prediction on the case dated on or before ``resolved_at``."""
    court, docket = case_id.split("/", 1)
    events_dir = CasePaths(data_root, court, int(docket)).events_dir
    for path in events_dir.glob("*/predictions/*/*/prediction.json"):
        try:
            run_day = ids.parse_run_id(path.parent.name).date()
        except ValueError:
            continue
        if run_day <= resolved_at:
            return True
    return False


def _reason(
    conn: corpus.ReadConnection, row: corpus.CorpusRow, resolved_at: date
) -> tuple[UnforecastReason, str | None]:
    if row.predict_excluded:
        return UnforecastReason.out_of_scope, "the case row is latched out of scope"
    scope = corpus.out_of_scope_reason_full(conn, row)
    if scope is not None:
        return UnforecastReason.out_of_scope, scope
    if row.date_filed is not None and not had_a_scheduled_round(row.date_filed, resolved_at):
        return (
            UnforecastReason.resolved_before_a_round,
            f"filed {row.date_filed.isoformat()}, resolved {resolved_at.isoformat()}",
        )
    if row.salience_selected:
        return UnforecastReason.selected_unforecast, None
    if row.salience_version is None:
        return UnforecastReason.not_scored, None
    return UnforecastReason.not_selected, None


def _entry(
    conn: corpus.ReadConnection, row: corpus.CorpusRow, resolved_at: date, *, application: bool
) -> UnforecastOutcome:
    reason, detail = _reason(conn, row, resolved_at)
    if application:
        kind = row.application_kind
        admitted = _admitted(kind)
        return UnforecastOutcome(
            case_id=row.case_id,
            docket_number=row.docket_number,
            disposition=str(row.disposition),
            resolved_at=resolved_at,
            reason=reason,
            detail=detail,
            selected=row.salience_selected,
            salience_version=row.salience_version,
            salience_score=row.salience_score,
            application_kind=kind,
            referred_to_court=row.referred_to_court,
            referred_not_substantive=bool(row.referred_to_court) and not admitted,
        )
    band = salience_band(row)
    paid = not corpus.is_ifp_petition(row)
    return UnforecastOutcome(
        case_id=row.case_id,
        docket_number=row.docket_number,
        disposition=str(row.disposition),
        resolved_at=resolved_at,
        reason=reason,
        detail=detail,
        selected=row.salience_selected,
        salience_version=row.salience_version,
        salience_score=row.salience_score,
        band=band,
        federal_signals=federal_signals(row) if paid and band != FEDERAL_BAND else [],
    )


_GRANT_FAMILY_SQL = ", ".join(f"'{d.value}'" for d in sorted(GRANT_FAMILY_DISPOSITIONS))


def _resolved_rows(
    conn: corpus.ReadConnection, *, since: date, until: date
) -> list[corpus.CorpusRow]:
    """The SCOTUS rows a census can count, decided in ``[since, until]``, by case id.

    Grant-family rows and anything shaped like an application number; the
    callers' own tests decide membership.

    The window is pushed into SQL over the three date columns a SCOTUS
    resolution can be read from, so the census hydrates a window's rows rather
    than the corpus; :func:`fedcourtsai.corpus.resolution_date` then says which
    of the three is the row's own.
    """
    lo, hi = since.isoformat(), until.isoformat()
    cur = conn.execute(
        "SELECT case_id FROM cases WHERE court = 'scotus' AND disposition IS NOT NULL "
        "AND (docket_number LIKE '%A%' OR disposition IN (" + _GRANT_FAMILY_SQL + ")) AND ("
        "date_cert_granted BETWEEN ? AND ? OR date_cert_denied BETWEEN ? AND ? "
        "OR date_decided BETWEEN ? AND ?) ORDER BY case_id",
        (lo, hi, lo, hi, lo, hi),
    )
    case_ids = [str(record[0]) for record in cur]
    rows = (corpus.get_row(conn, case_id) for case_id in case_ids)
    return [row for row in rows if row is not None]


def _recall(since: date, until: date, tally: list[int]) -> Recall:
    outcomes, forecast, unreachable = tally
    reachable = outcomes - unreachable
    return Recall(
        since=since,
        until=until,
        outcomes=outcomes,
        forecast=forecast,
        recall=forecast / outcomes if outcomes else None,
        reachable_outcomes=reachable,
        reachable_recall=forecast / reachable if reachable else None,
    )


def _is_grant_family_cert(row: corpus.CorpusRow) -> bool:
    return (
        corpus.is_modern_cert(row)
        and row.date_cert_granted is not None
        and row.disposition is not None
        and row.disposition in GRANT_FAMILY_DISPOSITIONS
    )


def _admitted(kind: str | None) -> bool:
    """Whether the stored reading is the one the substantive-application test admits.

    Compared as text: the column is blob-tolerant, and a value outside the
    vocabulary is a row the test does not admit, never a reason to stop.
    """
    return kind == ApplicationKind.substantive.value


def _is_watched_application(row: corpus.CorpusRow) -> bool:
    if not corpus.is_scotus_application_form(row.docket_number):
        return False
    return _admitted(row.application_kind) or bool(row.referred_to_court)


def unforecast_outcomes(
    conn: corpus.ReadConnection, data_root: Path, *, since: date, until: date
) -> UnforecastReport:
    """Census the outcomes resolved in ``[since, until]`` that no forecast preceded."""
    term_open = date(october_term_year(until), 10, 1)
    span_open = min(since, term_open)
    cert: list[UnforecastOutcome] = []
    ifp: list[UnforecastOutcome] = []
    interim: list[UnforecastOutcome] = []
    window = [0, 0, 0]
    term = [0, 0, 0]
    interim_outcomes = 0
    for row in _resolved_rows(conn, since=span_open, until=until):
        resolved_at = corpus.resolution_date(row)
        if resolved_at is None or not span_open <= resolved_at <= until:
            continue
        in_window = since <= resolved_at <= until
        if _is_grant_family_cert(row):
            covered = forecast_preceded(data_root, row.case_id, resolved_at)
            if corpus.is_ifp_petition(row):
                if in_window and not covered:
                    ifp.append(_entry(conn, row, resolved_at, application=False))
                continue
            entry = None if covered else _entry(conn, row, resolved_at, application=False)
            unreachable = entry is not None and entry.reason in _UNREACHABLE
            for tally, counted in ((window, in_window), (term, resolved_at >= term_open)):
                if counted:
                    tally[0] += 1
                    tally[1] += covered
                    tally[2] += unreachable
            if in_window and entry is not None:
                cert.append(entry)
        elif in_window and _is_watched_application(row):
            interim_outcomes += 1
            if not forecast_preceded(data_root, row.case_id, resolved_at):
                interim.append(_entry(conn, row, resolved_at, application=True))
    for entries in (cert, ifp, interim):
        entries.sort(key=lambda e: (e.resolved_at, e.docket_number))
    term_to_date = _recall(term_open, until, term)
    reachable = [e for e in cert if e.reason != UnforecastReason.resolved_before_a_round]
    floor_read = term_to_date.reachable_recall
    alarms = [
        f"{e.docket_number}: {e.disposition} with no forecast, in the federal band"
        for e in reachable
        if e.band == FEDERAL_BAND
    ]
    alarms += [
        f"{e.docket_number}: {e.disposition} with no forecast, outside the federal band, "
        f"and reads federal by {', '.join(s.value for s in e.federal_signals)}"
        for e in reachable
        if e.federal_signals
    ]
    if (
        floor_read is not None
        and term_to_date.reachable_outcomes >= RECALL_ALARM_MIN_OUTCOMES
        and floor_read < RECALL_ALARM_BELOW
    ):
        alarms.append(
            f"Term-to-date reachable grant recall {floor_read:.3f} "
            f"({term_to_date.forecast}/{term_to_date.reachable_outcomes}) "
            f"is below {RECALL_ALARM_BELOW:.2f}"
        )
    return UnforecastReport(
        since=since,
        until=until,
        window=_recall(since, until, window),
        term_to_date=term_to_date,
        cert_unforecast=cert,
        ifp_grants_unforecast=ifp,
        interim_outcomes=interim_outcomes,
        interim_unforecast=interim,
        alarms=alarms,
    )
