"""The federal-label cross-check: pending petitions a looser reading places federal.

The federal carve-in selects on the petitioner class a registered caption rule
reads. A federal petitioner the rule reads ``private`` or ``state`` is scored
with everyone else and, most often, never selected, and nothing downstream
says so until the grant. This census looks ahead of the outcome: over every
**pending** paid cert petition in predict scope whose band is not ``federal``,
it lists the ones a deliberately looser reading
(:func:`fedcourtsai.pipeline.unforecast.federal_signals`) places federal, while
there is still a conference to forecast. Pending means no stored resolution on
a docket of the current October Term or the two before it; an older open row
is a stale record, not a petition awaiting a conference.

Pending rows only, on purpose. One signal reads counsel entries a docket can
gain after its outcome, which is why no registered rule may use it; on a
petition not yet decided there is no outcome for it to carry. The check
selects nothing and moves no band: a confirmed miss is evidence for the next
registered caption version.

**The alarm** is a flagged petition the Solicitor General's office appears for
that is **not selected**: no forecast is coming for it. A flagged petition
that is selected will be forecast, under a band and base rate that may be the
wrong ones, and is a list for a person to read, as is every party-only flag.
The conference date printed beside an entry is the latest one the docket was
distributed for, which may already have passed.

**The outside list** (:func:`read_sg_petition_listing`) is a second reading
that shares nothing with the caption grammar or the stored docket: the Office
of the Solicitor General posts its own cert petitions on its briefs listing,
and every petition there is the government's. A pending petition on that
listing whose band is not ``federal`` is an alarm whatever its selection or
conference, because the band prices its forecast. The listing is read one way
only: it is what the Office has posted, newest Term first and one page deep,
so a petition absent from it is not thereby private. A listing that cannot be
read is an alarm of its own, since a check that stopped reading its source
would otherwise look like a quiet one. The census reads the listing only when
handed one; the fetch is the caller's choice.

``salience_version`` re-reads the bands under another registered scorer, to
ask what the check lists under a different caption rule; the selection latch
it prints stays the stored one, set by the active scorer.
Reads the corpus index; reads no snapshot and writes nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import october_term_year
from .documents import KIND_PETITION
from .salience import scorer
from .sg_briefs import OsgClient, parse_listing
from .unforecast import FEDERAL_BAND, FederalSignal, federal_signals

#: How many October Terms before the current one a pending docket may belong to.
PENDING_TERMS_BACK = 2


#: What an alarm about the listing itself, not a docket on it, is named by.
SG_LISTING_SUBJECT = "sg-petition-listing"


@dataclass(frozen=True)
class SgPetitionListing:
    """The Office of the Solicitor General's posted cert petitions, as one read found them."""

    docket_numbers: frozenset[str]
    newest_filed: date | None = None
    oldest_filed: date | None = None
    #: Why the listing could not be read, in words that carry no page text;
    #: ``None`` when it was.
    error: str | None = None


def read_sg_petition_listing(client: OsgClient) -> SgPetitionListing:
    """Read the Office's cert petitions off the first page of its briefs listing.

    One request (:meth:`OsgClient.cert_petitions`). Only rows whose type is the
    Office's own petition are kept, so a page served without the type filter
    applied cannot put an opposition's docket on the list. A request that
    fails, a page that cannot be parsed, and a page with no such row come back
    as an unread listing naming the failure by its kind, never by anything the
    page said. The page is outside text, so nothing it holds may raise out of
    here: the caller's other checks report whatever this one met.
    """
    try:
        served = client.cert_petitions()
    except (httpx.HTTPError, ValueError) as exc:
        return SgPetitionListing(frozenset(), error=f"the request failed ({type(exc).__name__})")
    if served is None:
        return SgPetitionListing(frozenset(), error="the listing was not found")
    page, page_url = served
    try:
        rows = [row for row in parse_listing(page, page_url=page_url) if row.kind == KIND_PETITION]
    except Exception as exc:  # any shape a served page can take
        return SgPetitionListing(
            frozenset(), error=f"the page could not be parsed ({type(exc).__name__})"
        )
    if not rows:
        return SgPetitionListing(frozenset(), error="the page held no petition row")
    filed = [row.filed for row in rows if row.filed is not None]
    return SgPetitionListing(
        docket_numbers=frozenset(number for row in rows for number in row.docket_numbers),
        newest_filed=max(filed, default=None),
        oldest_filed=min(filed, default=None),
    )


class SgListedPetition(BaseModel):
    """One pending petition on the Solicitor General's listing outside the ``federal`` band."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    band: str
    selected: bool = Field(
        description="The row's stored salience selection latch, set by the active scorer"
    )
    distributed_for_conference: date | None = Field(
        description="The latest conference the docket was distributed for"
    )


class SgPetitionCheck(BaseModel):
    """The pending docket read against the Solicitor General's posted cert petitions."""

    model_config = ConfigDict(extra="forbid")

    read: bool = Field(description="Whether the listing was read")
    error: str | None = Field(description="Why it was not, by kind of failure")
    listed: int = Field(ge=0, description="Docket numbers on the listing's first page")
    newest_filed: date | None = Field(description="The newest filing date among them")
    oldest_filed: date | None = Field(
        description="The oldest filing date among them: how far back the page reaches"
    )
    pending: int = Field(ge=0, description="Those that are pending petitions in this census")
    not_federal: list[SgListedPetition] = Field(
        description="Those pending outside the `federal` band, by docket"
    )
    alarms: list[str] = Field(
        description="The alarms this reading raises, which the report's own list also carries"
    )


class FlaggedPetition(BaseModel):
    """One pending petition outside the ``federal`` band that a loose reading places federal."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    band: str
    signals: list[FederalSignal]
    selected: bool = Field(
        description="The row's stored salience selection latch, set by the active scorer"
    )
    distributed_for_conference: date | None = Field(
        description="The latest conference the docket was distributed for"
    )
    days_to_conference: int | None = Field(
        description="Days from the census day to the conference; negative once it has passed"
    )


class FederalLabelReport(BaseModel):
    """The federal-label cross-check over the pending paid docket."""

    model_config = ConfigDict(extra="forbid")

    as_of: date
    salience_version: str = Field(description="The scorer whose bands the census read")
    pending: int = Field(
        ge=0,
        description="Paid cert petitions in predict scope with no stored resolution, "
        "from the current October Term or the two before it",
    )
    federal: int = Field(ge=0, description="Those the scorer bands `federal`")
    flagged: list[FlaggedPetition] = Field(
        description="Those outside the band that a loose reading places federal, by docket"
    )
    sg_petition_list: SgPetitionCheck | None = Field(
        default=None,
        description="The pending docket against the Solicitor General's posted cert "
        "petitions; null when the census was not handed the listing",
    )
    alarms: list[str] = Field(
        description="Each alarm condition that holds, in words; empty when the census is quiet"
    )


def _pending_rows(conn: corpus.ReadConnection, *, today: date) -> list[corpus.CorpusRow]:
    oldest_term = october_term_year(today) - PENDING_TERMS_BACK
    cur = conn.execute(
        "SELECT case_id FROM cases WHERE court = 'scotus' AND disposition IS NULL "
        "AND date_cert_granted IS NULL AND date_cert_denied IS NULL "
        "AND predict_excluded = 0 AND docket_number GLOB '[0-9][0-9]-*' ORDER BY case_id"
    )
    case_ids = [str(record[0]) for record in cur]
    rows = (corpus.get_row(conn, case_id) for case_id in case_ids)
    return [
        row
        for row in rows
        if row is not None
        and corpus.is_modern_cert(row)
        and not corpus.is_ifp_petition(row)
        and corpus.out_of_scope_reason(row) is None
        and (corpus.scotus_term_year(row.docket_number) or 0) >= oldest_term
    ]


def federal_label_check(
    conn: corpus.ReadConnection,
    *,
    today: date,
    salience_version: str | None = None,
    sg_listing: SgPetitionListing | None = None,
) -> FederalLabelReport:
    """Cross-check the ``federal`` band on every pending paid petition in scope.

    ``sg_listing`` adds the outside list: each pending petition on it is
    counted, and one outside the band is reported and alarmed.
    """
    active = scorer(salience_version)
    version, band_of = active.version, active.band
    pending = federal = listed_pending = 0
    flagged: list[FlaggedPetition] = []
    listed_not_federal: list[SgListedPetition] = []
    listed = sg_listing.docket_numbers if sg_listing is not None else frozenset()
    for row in _pending_rows(conn, today=today):
        pending += 1
        band = band_of(row)
        if corpus.strip_docket_annotation(row.docket_number).strip().upper() in listed:
            listed_pending += 1
            if band != FEDERAL_BAND:
                listed_not_federal.append(
                    SgListedPetition(
                        case_id=row.case_id,
                        docket_number=row.docket_number,
                        band=band,
                        selected=row.salience_selected,
                        distributed_for_conference=row.distributed_for_conference,
                    )
                )
        if band == FEDERAL_BAND:
            federal += 1
            continue
        signals = federal_signals(row)
        if not signals:
            continue
        conference = row.distributed_for_conference
        flagged.append(
            FlaggedPetition(
                case_id=row.case_id,
                docket_number=row.docket_number,
                band=band,
                signals=signals,
                selected=row.salience_selected,
                distributed_for_conference=conference,
                days_to_conference=(conference - today).days if conference else None,
            )
        )
    flagged.sort(key=lambda f: f.docket_number)
    alarms = [
        f"{f.docket_number}: the Solicitor General's office appears for the petitioner, "
        f"band {f.band}, not selected, conference {f.distributed_for_conference}"
        for f in flagged
        if FederalSignal.sg_office_counsel in f.signals and not f.selected
    ]
    sg_check: SgPetitionCheck | None = None
    if sg_listing is not None:
        listed_not_federal.sort(key=lambda p: p.docket_number)
        sg_check = SgPetitionCheck(
            read=sg_listing.error is None,
            error=sg_listing.error,
            listed=len(sg_listing.docket_numbers),
            newest_filed=sg_listing.newest_filed,
            oldest_filed=sg_listing.oldest_filed,
            pending=listed_pending,
            not_federal=listed_not_federal,
            alarms=(
                [
                    f"{SG_LISTING_SUBJECT}: the Solicitor General's listing of its cert "
                    f"petitions could not be read, {sg_listing.error}"
                ]
                if sg_listing.error is not None
                else []
            )
            + [
                f"{p.docket_number}: on the Solicitor General's listing of its own cert "
                f"petitions, band {p.band}, {'selected' if p.selected else 'not selected'}"
                + (
                    f", conference {p.distributed_for_conference}"
                    if p.distributed_for_conference
                    else ""
                )
                for p in listed_not_federal
            ],
        )
        alarms += sg_check.alarms
    return FederalLabelReport(
        as_of=today,
        salience_version=version,
        pending=pending,
        federal=federal,
        flagged=flagged,
        sg_petition_list=sg_check,
        alarms=alarms,
    )
