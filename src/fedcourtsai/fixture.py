"""Synthetic fixture corpus for offline local runs and tests.

Provisioning a snapshot, retrieving priors, or listing a case's open events all
read from the packed corpus (:mod:`fedcourtsai.corpus`), which in production is a
``dvc pull`` of the S3-backed remote behind OIDC — infra a laptop (or a unit
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
from .schemas import Disposition, EventKind

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

    @property
    def case_id(self) -> str:
        return ids.case_id(self.court, self.docket)

    @property
    def kind(self) -> EventKind:
        """SCOTUS dockets predict a petition; every other court an appeal."""
        return EventKind.petition if self.court == "scotus" else EventKind.appeal

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
            # SCOTUS dockets are in prediction scope by the ingestion rule; the
            # originating-court latch (run during the build) extends it to a
            # linked court-of-appeals docket.
            predict_eligible=self.court == "scotus",
            originating_court=self.originating_court,
            originating_docket_number=self.originating_docket_number,
        )

    def event(self) -> corpus.CorpusEvent:
        return corpus.CorpusEvent(
            event_id=ids.event_id(self.kind.value, "disposition"),
            case_id=self.case_id,
            court=self.court,
            kind=self.kind,
            title=self.case_name,
            decision_target="disposition",
            opened_at=self.date_filed,
            resolved=self.resolved,
        )

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
# scotus/305 links to ca9/102, so the originating-court latch pulls that
# court-of-appeals docket into prediction scope during the build.
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
        entries=(
            ("2025-01-15", "Petition for writ of certiorari filed."),
            ("2025-03-03", "Brief in opposition requested."),
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
    events = [case.event() for case in FIXTURE_CASES]
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_events(conn, events)
        for case in FIXTURE_CASES:
            corpus.upsert_snapshot(conn, case.case_id, case.snapshot_date, case.snapshot_payload())
    return db_path
