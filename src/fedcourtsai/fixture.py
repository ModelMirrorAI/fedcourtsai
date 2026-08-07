"""Synthetic fixture corpus for offline local runs and tests.

Provisioning a snapshot, retrieving priors, or listing a case's open events all
read from the packed corpus (:mod:`fedcourtsai.corpus`), which in production is
pulled from the S3-backed remote behind OIDC — infra a laptop (or a unit
test) cannot reach. This module builds a *tiny, deterministic* corpus from
hard-coded facts instead, so the local read loop and the offline tests run with
no remote, no token, and no network.

The fixture is a faithful miniature of a real corpus, not a mock: it populates
the same three stores the ingestion channels write — normalized ``cases`` rows,
predictable ``events``, and dated ``snapshots`` — kept mutually consistent (each
snapshot's docket JSON matches its row), across more than one court, with a mix
of resolved and open cases. It is built directly through the corpus write APIs
rather than the ingestion path, so it deliberately exercises the *read* seams
retrieval and provisioning use without depending on the REST/bulk normalizers.

Determinism is the contract: every field is a literal (no clock, no randomness),
so :func:`build_fixture_corpus` over a fresh path is reproducible run to run.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from . import corpus, ids
from .pipeline import moments
from .schemas import Disposition, EventKind, Judgment, Moment, Stage

_COURT_URL = "https://www.courtlistener.com/api/rest/v4/courts/{court}/"


@dataclass(frozen=True)
class FixtureCase:
    """One synthetic case, the single source for its row, event, and snapshot.

    Holding every fact in one place keeps the three corpus stores consistent the
    way a real corpus is: the dated snapshot's docket JSON describes the same
    docket the normalized ``cases`` row summarizes, and the predictable event's
    resolved flag matches whether the case carries a realized ``disposition``.
    """

    court: str
    docket: int
    docket_number: str
    case_name: str
    date_filed: date
    snapshot_date: date
    # (date, description) docket-entry pairs that populate the snapshot payload.
    entries: tuple[tuple[str, str], ...]
    topic: str | None = None
    judges: tuple[str, ...] = ()
    citations: tuple[str, ...] = ()
    citation_count: int | None = None
    precedential_status: str | None = None
    opinion_text: str | None = None
    disposition: Disposition | None = None
    date_decided: date | None = None
    originating_court: str | None = None
    originating_docket_number: str | None = None
    # Live-channel facts: a case the fixture treats as written by the
    # supremecourt.gov channel carries the poll stamp (live-slice membership),
    # its inclusion weight, and the parsed cert signals — so the statpack's
    # live-slice sections have a population to aggregate.
    last_live_polled: date | None = None
    sample_weight: int | None = None
    distribution_count: int | None = None
    cvsg_date: date | None = None
    originating_court_name: str | None = None
    date_cert_granted: date | None = None
    date_cert_denied: date | None = None
    # Interim-docket facts: an application case carries its parsed ask and the
    # latched escalation-ladder signals, so the corpus columns the interim
    # cohort is assembled from have a population in miniature.
    application_kind: str | None = None
    response_requested: bool | None = None
    referred_to_court: bool | None = None
    amicus_briefs: int | None = None
    # The merits pair a granted docket's judgment entry latches (see
    # pipeline/judgment.py); set only on a granted case whose judgment landed.
    merits_judgment: Judgment | None = None
    merits_decided: date | None = None

    @property
    def case_id(self) -> str:
        return ids.case_id(self.court, self.docket)

    @property
    def kind(self) -> EventKind:
        """Mirrors the baseline-mint rule (:func:`fedcourtsai.pipeline.ingest.default_event`).

        At SCOTUS an application docket predicts its motion and a cert docket
        its petition; every other court predicts the appeal.
        """
        if self.court != "scotus":
            return EventKind.appeal
        if corpus.is_scotus_application_form(self.docket_number):
            return EventKind.motion
        return EventKind.petition

    @property
    def resolved(self) -> bool:
        """A case is resolved once it carries a realized disposition label."""
        return self.disposition is not None

    def row(self) -> corpus.CorpusRow:
        return corpus.CorpusRow(
            case_id=self.case_id,
            court=self.court,
            docket_number=self.docket_number,
            case_name=self.case_name,
            date_filed=self.date_filed,
            date_decided=self.date_decided,
            disposition=self.disposition,
            judges=list(self.judges),
            topic=self.topic,
            citations=list(self.citations),
            citation_count=self.citation_count,
            precedential_status=self.precedential_status,
            opinion_text=self.opinion_text,
            # SCOTUS dockets are in prediction scope by the ingestion rule.
            predict_eligible=self.court == "scotus",
            originating_court=self.originating_court,
            originating_docket_number=self.originating_docket_number,
            last_live_polled=self.last_live_polled,
            sample_weight=self.sample_weight,
            distribution_count=self.distribution_count,
            cvsg_date=self.cvsg_date,
            originating_court_name=self.originating_court_name,
            date_cert_granted=self.date_cert_granted,
            date_cert_denied=self.date_cert_denied,
            application_kind=self.application_kind,
            response_requested=self.response_requested,
            referred_to_court=self.referred_to_court,
            amicus_briefs=self.amicus_briefs,
            merits_judgment=self.merits_judgment.value if self.merits_judgment else None,
            merits_decided=self.merits_decided,
        )

    def event(self) -> corpus.CorpusEvent:
        # The stage mirrors the baseline-mint rule: a SCOTUS motion baseline is
        # the interim decision standard, a SCOTUS petition baseline the cert
        # standard, and a circuit appeal declares none.
        if self.court != "scotus":
            stage = None
        elif self.kind == EventKind.motion:
            stage = Stage.interim
        else:
            stage = Stage.cert
        return corpus.CorpusEvent(
            event_id=ids.event_id(self.kind.value, "disposition"),
            case_id=self.case_id,
            court=self.court,
            kind=self.kind,
            stage=stage,
            moment=moments.first_moment(stage) if stage is not None else None,
            title=self.case_name,
            decision_target="disposition",
            opened_at=self.date_filed,
            resolved=self.resolved,
        )

    def events(self) -> list[corpus.CorpusEvent]:
        """The case's predictable events: the baseline, plus the merits event.

        A SCOTUS docket whose grant opens a merits proceeding carries the open
        merits event the cert grant mints in production
        (`pipeline.outcome.mint_merits_event`) — same id, kind, stage, and
        target — resolved once the fixture states a parsed judgment, so the
        offline cascade exercises the merits cell contract end to end. The
        admission is `corpus.opens_merits_proceeding`, the production
        predicate itself, so a fixture case can never carry an event the
        pipeline would not mint for it.
        """
        events = [self.event()]
        if corpus.opens_merits_proceeding(self.row()):
            events.append(
                corpus.CorpusEvent(
                    event_id=ids.event_id(EventKind.order.value, "judgment"),
                    case_id=self.case_id,
                    court=self.court,
                    kind=EventKind.order,
                    stage=Stage.merits,
                    moment=Moment.grant,
                    title=self.case_name,
                    description="Disposition of the judgment below, following the cert grant.",
                    decision_target="judgment",
                    opened_at=self.date_cert_granted,
                    resolved=self.merits_judgment is not None,
                )
            )
        return events

    def snapshot_payload(self) -> dict[str, Any]:
        """The point-in-time docket JSON ``provision-snapshot`` materializes."""
        return {
            "id": self.docket,
            "court": _COURT_URL.format(court=self.court),
            "case_name": self.case_name,
            "docket_number": self.docket_number,
            "date_filed": self.date_filed.isoformat(),
            "date_terminated": self.date_decided.isoformat() if self.date_decided else None,
            "docket_entries": [
                {"id": i + 1, "date_filed": entry_date, "description": description}
                for i, (entry_date, description) in enumerate(self.entries)
            ],
        }


# A handful of synthetic cases across three courts (ca9, ca1, scotus), a mix of
# resolved and open, populating the fields retrieval (court / topic / judges /
# citations / disposition / recency) and provisioning (the dated snapshot) read.
# The SCOTUS petitions carry lower-court linkage onto the ca9 dockets (304 →
# ca9/102, 305 → ca9/103) and are live-slice rows, so the statpack's
# originating-circuit and weighted cert cuts have material to aggregate. The
# `26A11` application docket (scotus/306) is the interim stage in miniature: a
# resolved substantive stay application whose motion-baseline event carries
# `Stage.interim`, so the offline cascade can prove an interim cell end to end.
FIXTURE_CASES: tuple[FixtureCase, ...] = (
    FixtureCase(
        court="ca9",
        docket=101,
        docket_number="22-15001",
        case_name="Alvarez v. Northwest Logistics",
        topic="civil rights",
        judges=("berzon", "smith"),
        citations=("410 U.S. 113", "347 U.S. 483"),
        citation_count=14,
        precedential_status="Published",
        opinion_text="The panel reverses the summary judgment and remands for trial.",
        disposition=Disposition.granted,
        date_filed=date(2022, 4, 11),
        date_decided=date(2023, 9, 18),
        snapshot_date=date(2023, 9, 18),
        entries=(
            ("2022-04-11", "Notice of appeal filed."),
            ("2023-09-18", "Opinion: reversed and remanded."),
        ),
    ),
    FixtureCase(
        court="ca9",
        docket=102,
        docket_number="22-15044",
        case_name="Cohen v. Pacific Mutual",
        topic="contracts",
        judges=("smith",),
        citations=("5 U.S. 137",),
        citation_count=3,
        precedential_status="Unpublished",
        opinion_text="The district court's judgment is affirmed.",
        disposition=Disposition.denied,
        date_filed=date(2022, 6, 2),
        date_decided=date(2023, 11, 30),
        snapshot_date=date(2023, 11, 30),
        entries=(
            ("2022-06-02", "Notice of appeal filed."),
            ("2023-11-30", "Memorandum: affirmed."),
        ),
    ),
    FixtureCase(
        court="ca9",
        docket=103,
        docket_number="24-15110",
        case_name="Doe v. Cascade School District",
        topic="civil rights",
        judges=("berzon", "watford"),
        date_filed=date(2024, 2, 14),
        snapshot_date=date(2024, 6, 1),
        entries=(
            ("2024-02-14", "Notice of appeal filed."),
            ("2024-05-20", "Opening brief filed."),
        ),
    ),
    FixtureCase(
        court="ca1",
        docket=201,
        docket_number="23-1380",
        case_name="Okafor v. Department of Homeland Security",
        topic="immigration",
        judges=("barron",),
        citations=("533 U.S. 678",),
        citation_count=6,
        precedential_status="Published",
        opinion_text="The petition for review is dismissed for lack of jurisdiction.",
        disposition=Disposition.dismissed,
        date_filed=date(2023, 3, 9),
        date_decided=date(2024, 1, 22),
        snapshot_date=date(2024, 1, 22),
        entries=(
            ("2023-03-09", "Petition for review filed."),
            ("2024-01-22", "Judgment: dismissed."),
        ),
    ),
    FixtureCase(
        court="scotus",
        docket=304,
        docket_number="22-845",
        case_name="In re Pacific Mutual",
        judges=("roberts", "kagan"),
        disposition=Disposition.denied,
        date_filed=date(2024, 1, 8),
        date_decided=date(2024, 6, 24),
        snapshot_date=date(2024, 6, 24),
        originating_court="ca9",
        originating_docket_number="22-15044",
        # Written by the historical walker under an interval-5 denial sample
        # (serial 845 sits on that grid): the fixture's weighted-aggregate case.
        last_live_polled=date(2026, 7, 1),
        sample_weight=5,
        distribution_count=2,
        date_cert_denied=date(2024, 6, 24),
        originating_court_name="United States Court of Appeals for the Ninth Circuit",
        entries=(
            ("2024-01-08", "Petition for writ of certiorari filed."),
            ("2024-06-24", "Petition DENIED."),
        ),
    ),
    FixtureCase(
        court="scotus",
        docket=305,
        docket_number="24-12",
        case_name="Cascade School District v. Doe",
        date_filed=date(2025, 1, 15),
        snapshot_date=date(2025, 3, 3),
        originating_court="ca9",
        originating_docket_number="24-15110",
        # Written by the forward poller (weight 1, pending): distributed once,
        # with a CVSG on file — the fixture's live-signal case.
        last_live_polled=date(2026, 7, 1),
        sample_weight=1,
        distribution_count=1,
        cvsg_date=date(2025, 6, 2),
        originating_court_name="United States Court of Appeals for the Ninth Circuit",
        entries=(
            ("2025-01-15", "Petition for writ of certiorari filed."),
            ("2025-03-03", "Brief in opposition requested."),
        ),
    ),
    FixtureCase(
        court="scotus",
        docket=306,
        docket_number="26A11",
        case_name="Marbury Power Cooperative v. Ellison",
        date_filed=date(2026, 6, 22),
        date_decided=date(2026, 7, 14),
        snapshot_date=date(2026, 7, 14),
        # Written by the live application rotation: a substantive stay
        # application that climbed the whole escalation ladder — a requested
        # response, referral to the full Court, one amicus brief — and was
        # granted, so the fixture exercises the interim (motion-baseline) path:
        # a `Stage.interim` event, application-shaped entry text, and an
        # outcome with no cert `signals` block (no distributions, no CVSG).
        # The snapshot envelope stays the fixture's uniform CourtListener docket
        # shape; only the entry text is application-shaped.
        disposition=Disposition.granted,
        last_live_polled=date(2026, 7, 14),
        sample_weight=1,
        application_kind="substantive",
        response_requested=True,
        referred_to_court=True,
        amicus_briefs=1,
        entries=(
            (
                "2026-06-22",
                "Application (26A11) for a stay of the mandate pending the filing and "
                + "disposition of a petition for a writ of certiorari, submitted to "
                + "The Chief Justice.",
            ),
            ("2026-06-25", "Response to application (26A11) requested, due July 2, 2026."),
            ("2026-07-02", "Response to application filed."),
            ("2026-07-06", "Brief amicus curiae of Grid Reliability Council filed."),
            (
                "2026-07-14",
                "Application (26A11) referred to the Court. Application granted; the "
                + "mandate is stayed pending disposition of the petition.",
            ),
        ),
    ),
)


def build_fixture_corpus(db_path: Path) -> Path:
    """Build the synthetic fixture corpus at ``db_path``, returning the path.

    Overwrites any file already at ``db_path`` so the build starts from an empty
    database and its content is a pure function of :data:`FIXTURE_CASES` — the
    determinism the offline loop and tests rely on. Writes the normalized rows,
    their predictable events, and one dated snapshot per case through the corpus
    write APIs, so the prediction-scope column is set by the real rule.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.unlink(missing_ok=True)
    rows = [case.row() for case in FIXTURE_CASES]
    events = [event for case in FIXTURE_CASES for event in case.events()]
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_events(conn, events)
        for case in FIXTURE_CASES:
            corpus.upsert_snapshot(conn, case.case_id, case.snapshot_date, case.snapshot_payload())
        # The discovery-cursor state a real walked corpus carries, in miniature:
        # OT22's paid stream walked to a confirmed frontier (complete — census
        # 850), its IFP stream mid-walk (partial), and OT24's forward frontier
        # probed without an end observed. Feeds the statpack's census read.
        corpus.set_live_cursor(conn, 22, "historical-paid", 850)
        corpus.set_live_frontier(conn, 22, "historical-paid", 850)
        corpus.set_live_cursor(conn, 22, "historical-ifp", 5460)
        corpus.set_live_cursor(conn, 24, "paid", 12)
    return db_path


# A granted-and-decided SCOTUS merits case, deliberately OUTSIDE `FIXTURE_CASES`:
# the base corpus is a measured statistical surface (the statpack, back-test, and
# retrieval tests assert its exact counts and rates), and folding a granted
# merits row in would silently move every one of those figures. A test that
# wants the merits cell contract opts in with :func:`add_merits_fixture`
# instead. The docket carries the full trajectory in its entries — petition,
# grant, argument, judgment — with the row's cert/merits columns stating the
# same facts the live channel would latch from them.
MERITS_FIXTURE_CASE = FixtureCase(
    court="scotus",
    docket=306,
    docket_number="23-980",
    case_name="Cascade Timber Co. v. United States",
    date_filed=date(2024, 3, 4),
    snapshot_date=date(2025, 6, 20),
    disposition=Disposition.granted,
    date_cert_granted=date(2025, 1, 10),
    merits_judgment=Judgment.reversed,
    merits_decided=date(2025, 6, 20),
    originating_court="ca9",
    originating_docket_number="23-35105",
    last_live_polled=date(2026, 7, 1),
    sample_weight=1,
    distribution_count=2,
    originating_court_name="United States Court of Appeals for the Ninth Circuit",
    entries=(
        ("2024-03-04", "Petition for writ of certiorari filed."),
        ("2025-01-10", "Petition GRANTED."),
        ("2025-04-21", "Argued. For petitioner: counsel of record."),
        ("2025-06-20", "Judgment REVERSED and case REMANDED."),
    ),
)


def add_merits_fixture(db_path: Path) -> FixtureCase:
    """Write :data:`MERITS_FIXTURE_CASE` into an existing fixture corpus.

    The opt-in half of the fixture: the same three stores
    :func:`build_fixture_corpus` populates — the row (merits columns included),
    the two events (the resolved cert baseline and the resolved merits event),
    and the dated snapshot — through the same corpus write APIs, so the
    offline cascade can run a merits cell end to end. Returns the case, so the
    caller can address it without restating literals.
    """
    case = MERITS_FIXTURE_CASE
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(conn, [case.row()])
        corpus.upsert_events(conn, case.events())
        corpus.upsert_snapshot(conn, case.case_id, case.snapshot_date, case.snapshot_payload())
    return case
