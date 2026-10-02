"""Back-fill a closed Term's interim applications through the live channel's own seam.

The live channel captures an application when frontier discovery onboards it
(:func:`~fedcourtsai.pipeline.live.discover_live`'s ``application`` stream) and
re-polls it on the application rotation until it resolves. A serial the
discovery cursor had already passed before the stream existed was never polled,
so a Term whose capture started mid-stream holds only what the older channels
left for those serials: CourtListener stubs with a filing date and a court
below, and no ask, no capital marking, no referral, no disposition and no
counsel. OT2024 is that Term — complete capture starts at ``24A1000`` — and
every earlier Term is the same shape with no live row at all.

This pass enumerates one Term's application serials and lands each one the live
channel does not already own **through the live channel's own write path**:
:func:`~fedcourtsai.pipeline.live._resolve_identity` for the case id (the stub's
row when one exists, else the reserved-range mint) and
:func:`~fedcourtsai.pipeline.live.ingest_live_payload` with
``form="application"`` for the row, the dated snapshot, resolution and events.
Nothing here maps a field. ``application_kind``, ``capital_case``,
``referred_to_court``, the dates, ``counsel`` and the stored snapshot come out
of the shared mapping exactly as a live poll's would, and every write stamps
``last_live_polled``, so a back-filled row joins the live slice on the same
terms as a discovered one.

**Ownership.** A serial whose stored row already carries ``last_live_polled`` is
the live channel's: it is counted and never fetched, so this pass can never
overwrite a live-polled row. Because the ingest stamps that marker, a row this
pass writes becomes live-owned too, which is what makes a re-run a no-op: the
control dry run after an apply reads zero candidates.

**Enumeration.** Serials run from 1 upward. Upstream withholds the occasional
number mid-stream, so a miss (a 404 or a non-JSON body) is an end signal only
past the highest serial the corpus already stores for the Term: from there,
``end_misses`` consecutive misses mark the Term's last application. Below that
point a miss is a withheld serial, recorded and walked past. A Term the corpus
holds no row for is armed from serial 1. An upstream error, a fetch limit or
the run deadline stops the Term's walk where it stands; the apply refuses any
reading that did not reach every Term's end rather than land half a Term. One
mis-keyed stub far past a Term's real end would arm the end late and turn the
tail into withheld serials; the deadline bounds that walk, and the ledger prints
the stored maximum and every withheld serial so the outlier is visible.

**Two guards beside ownership.** A served record whose own docket number is not
the serial it was fetched as is held back, since identity keys on that number.
A row whose open event carries a committed prediction is held back too and left
to the live rotation, for the historical walker's reason: this pass writes no
evaluate queue, so an ingest that resolved it would strand the prediction
unscored.

Read-only by default: fetch, map, and report what an apply would write. The
apply refuses above ``max_rows`` before its first write. It is a corpus write,
so it runs on run-repair's ``application-backfill`` pass, which holds the
writer credentials; a dev checkout over a pulled corpus produces the dry run.

**Split across a credential boundary.** On run-repair the walk — about a
thousand fetches of upstream JSON — runs in a job holding no credential. A
read-only job writes each Term's stored serials (:class:`ApplicationProjection`);
the credential-free job walks against it, checks each served record's own
docket number, and writes every served record it would land, verbatim, with a
mapped preview (:class:`ApplicationPlan`) — a file that carries the served
dockets' party contact blocks, which crosses only under the narrow carve-out
``docs/data-sources.md`` (*PII stance*) records; and the writer job,
holding the corpus lock and the read-write role over a freshly pulled corpus,
re-checks the plan whole and lands it through the shared seam
(:func:`apply_application_plan`) — re-reading ownership, resolving identity and
applying the prediction guard against the corpus it writes, so a row the live
channel took over in the meantime is never overwritten. Without a corpus the
plan cannot tell an onboard from an enrich or see a committed prediction, so
its ledger says ``unresolved`` and an apply can land fewer rows than it lists,
never more.
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclasses_field
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Final, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .. import corpus, ids
from ..handoff import HandoffRefused
from ..matrix import event_has_predictions
from ..supremecourt import (
    SupremeCourtClient,
    parse_scotus_application_number,
    scotus_docket_slug,
)
from .ingest import from_live_record, map_live_docket
from .live import _resolve_identity, ingest_live_payload

#: The Term this pass exists for: OT2024's applications below ``24A1000`` were
#: never polled, because application capture started mid-Term.
DEFAULT_TERMS: tuple[int, ...] = (24,)

#: The Terms whose apply is pre-registered in ``docs/freeze-record.md``. Each
#: Term's apply moves the pooled interim base rate by its own amount, so each is
#: its own scoring-baseline move: a Term joins this set in the same change that
#: appends its freeze-record entry, and an apply for any other Term is refused.
#: A dry run reads any reachable Term, since reading moves nothing.
REGISTERED_APPLY_TERMS: frozenset[int] = frozenset({24})

#: Consecutive misses past the highest stored serial that mark a Term's last
#: application. Far above the live frontier's tolerance, because a closed Term's
#: end is read once rather than re-confirmed every cycle, so a short withheld run
#: mistaken for the end would leave the tail unread until someone noticed. Ten
#: fetches of slack cost ten seconds.
DEFAULT_END_MISSES = 10


#: One ledger note's text: bounded, one line, no control character, so a note
#: carried through a plan can neither forge a ledger line nor run long.
_NoteText = Annotated[str, StringConstraints(max_length=300, pattern=r"^[^\x00-\x1f]*$")]


class PlannedRow(BaseModel):
    """One application an apply would land, read through the live mapping."""

    model_config = ConfigDict(extra="forbid")

    docket_number: str
    serial: int
    case_id: str | None = Field(
        description="The row the record lands on; None where identity is not yet resolved"
    )
    action: Literal["onboard", "enrich", "unresolved"] = Field(
        description="`onboard` mints a row the corpus does not hold; `enrich` lands the "
        "live reading on the stored stub row; `unresolved` is a plan read without the "
        "corpus, whose writer resolves it."
    )
    application_kind: str | None
    capital_case: bool
    referred_to_court: bool | None
    disposition: str | None
    date_filed: date | None
    date_decided: date | None
    counsel: int = Field(description="Counsel entries the live mapping reads.")


class TermLedger(BaseModel):
    """One Term's enumeration: what was read, what is owned, what would land."""

    model_config = ConfigDict(extra="forbid")

    term: int
    end_misses: int
    stored_max_serial: int | None = Field(
        description="Highest serial the corpus stores for this Term before the pass; "
        "end detection arms past it."
    )
    stopped: Literal["end", "limit", "deadline", "upstream-error"] | None = None
    last_served: int | None = None
    fetched: int = 0
    served: int = 0
    live_owned: int = Field(
        default=0, description="Serials whose stored row the live channel owns; never fetched."
    )
    withheld: list[int] = Field(
        default_factory=list, description="Serials upstream did not serve below the end."
    )
    candidates: list[PlannedRow] = Field(default_factory=list)
    held: list[dict[Literal["docket", "reason"], _NoteText]] = Field(default_factory=list)
    failures: list[dict[Literal["docket", "reason"], _NoteText]] = Field(default_factory=list)


class ApplicationBackfillResult(BaseModel):
    """The pass's ledger across every Term it read, and what the apply wrote."""

    terms: list[TermLedger] = Field(default_factory=list)
    applied: bool = False
    refused: str | None = None
    written: list[str] = Field(default_factory=list)

    @property
    def candidates(self) -> list[PlannedRow]:
        return [row for ledger in self.terms for row in ledger.candidates]

    @property
    def failures(self) -> list[dict[Literal["docket", "reason"], str]]:
        return [failure for ledger in self.terms for failure in ledger.failures]


class DocketCache:
    """A dev-side read-through cache of the docket JSON this pass fetches.

    A dry run over a whole Term is a quarter of an hour of paced fetches, and a
    developer iterating on the ledger should not pay it twice. A cached record is
    a local file, not a host-scoped fetch, so the command refuses it on an apply.
    A miss is cached as a marker so a re-read does not re-probe the end either.
    """

    def __init__(self, root: Path) -> None:
        self.root = root

    def _paths(self, term: int, serial: int) -> tuple[Path, Path]:
        slug = scotus_docket_slug(term, serial, form="application")
        return self.root / f"{slug}.json", self.root / f"{slug}.missing"

    def read(self, term: int, serial: int) -> tuple[bool, dict[str, Any] | None]:
        served, missing = self._paths(term, serial)
        if served.exists():
            payload = json.loads(served.read_text())
            return True, payload if isinstance(payload, dict) else None
        if missing.exists():
            return True, None
        return False, None

    def write(self, term: int, serial: int, payload: dict[str, Any] | None) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        served, missing = self._paths(term, serial)
        if payload is None:
            missing.touch()
        else:
            served.write_text(json.dumps(payload, sort_keys=True))


def _stored_serials(conn: sqlite3.Connection, term: int) -> tuple[set[int], set[int]]:
    """Every serial the corpus stores for the Term, and the live-owned subset.

    Read over the identity join's own normalization (``norm_dn``), so a stored
    spelling the join would match is counted here too. Ownership is any row's:
    where a twin pair exists and either half is live-polled, the serial is the
    live channel's.
    """
    stored: set[int] = set()
    owned: set[int] = set()
    cur = conn.execute(
        "SELECT norm_dn(docket_number) AS norm, last_live_polled FROM cases "
        "WHERE court = 'scotus' AND norm_dn(docket_number) GLOB ?",
        (f"{term:02d}A*",),
    )
    for record in cur:
        parsed = parse_scotus_application_number(str(record["norm"]))
        if parsed is None or parsed[0] != term:
            continue
        stored.add(parsed[1])
        if record["last_live_polled"] is not None:
            owned.add(parsed[1])
    return stored, owned


def _plan(
    conn: sqlite3.Connection,
    data_root: Path,
    payload: dict[str, Any],
    term: int,
    serial: int,
    ledger: TermLedger,
    matches: Mapping[str, str],
) -> tuple[PlannedRow, int] | None:
    """Classify one served record: a planned row and its docket id, or held back."""
    number = scotus_docket_slug(term, serial, form="application")
    if (why := _served_as_problem(payload, term, serial)) is not None:
        ledger.held.append({"docket": number, "reason": why})
        return None
    docket_id = _resolve_identity(conn, payload, term, serial, form="application", matches=matches)
    case_id = ids.case_id("scotus", docket_id)
    stored = corpus.get_row(conn, case_id)
    if stored is not None and stored.last_live_polled is not None:
        # The serial check above missed it only if the stored spelling parses
        # differently from the served one; the identity join says it is owned.
        ledger.live_owned += 1
        return None
    open_events = [e.event_id for e in corpus.events_for_case(conn, case_id) if not e.resolved]
    if any(event_has_predictions(data_root, "scotus", docket_id, e) for e in open_events):
        ledger.held.append(
            {"docket": number, "reason": "an open event carries a committed prediction"}
        )
        return None
    row = from_live_record(map_live_docket(payload, docket_id, form="application"))
    planned = PlannedRow(
        docket_number=number,
        serial=serial,
        case_id=case_id,
        action="onboard" if stored is None else "enrich",
        application_kind=None if row.application_kind is None else str(row.application_kind),
        capital_case=bool(row.capital_case),
        referred_to_court=row.referred_to_court,
        disposition=None if row.disposition is None else str(row.disposition),
        date_filed=row.date_filed,
        date_decided=row.date_decided,
        counsel=len(row.counsel),
    )
    return planned, docket_id


@dataclass
class _Walk:
    """One invocation's enumeration state: the shared handles and fetch budget."""

    client: SupremeCourtClient
    end_misses: int
    limit: int | None
    cache: DocketCache | None
    deadline: float | None = None
    time_fn: Callable[[], float] = time.monotonic
    fetched: int = 0
    payloads: dict[str, tuple[dict[str, Any], int]] = dataclasses_field(default_factory=dict)

    def fetch(self, term: int, serial: int) -> dict[str, Any] | None:
        """One docket read, through the dev cache when one is set; raises on upstream error."""
        cached, payload = (False, None) if self.cache is None else self.cache.read(term, serial)
        if not cached:
            payload = self.client.get_docket(term, serial, form="application")
            if self.cache is not None:
                self.cache.write(term, serial, payload)
        self.fetched += 1
        return payload

    def walk_term(
        self,
        term: int,
        stored_max_serial: int | None,
        owned: set[int],
        classify: Callable[[dict[str, Any], int, TermLedger], tuple[PlannedRow, int] | None],
    ) -> TermLedger:
        """Enumerate one Term from serial 1 to its end, a fetch limit, the deadline, or an error.

        ``stored_max_serial`` and ``owned`` are the corpus's reading of the Term
        (:func:`_stored_serials`, directly or through the projection);
        ``classify`` files one served record as a planned row and its docket id,
        or records why not on the ledger.
        """
        ledger = TermLedger(
            term=term,
            end_misses=self.end_misses,
            stored_max_serial=stored_max_serial,
        )
        arm_after = ledger.stored_max_serial or 0
        serial, misses = 1, 0
        while True:
            if serial in owned:
                # Owned serials are stored ones, so they sit at or below
                # `arm_after`, where no miss is ever counted toward the end.
                ledger.live_owned += 1
                serial += 1
                continue
            if self.limit is not None and self.fetched >= self.limit:
                ledger.stopped = "limit"
                return ledger
            if self.deadline is not None and self.time_fn() >= self.deadline:
                ledger.stopped = "deadline"
                return ledger
            try:
                payload = self.fetch(term, serial)
            except httpx.HTTPError as exc:
                ledger.failures.append(
                    {
                        "docket": scotus_docket_slug(term, serial, form="application"),
                        "reason": " ".join(f"{type(exc).__name__}: {exc}".split())[:300],
                    }
                )
                ledger.stopped = "upstream-error"
                return ledger
            ledger.fetched += 1
            if payload is None:
                if serial <= arm_after:
                    ledger.withheld.append(serial)
                else:
                    misses += 1
                    if misses >= self.end_misses:
                        ledger.stopped = "end"
                        return ledger
                serial += 1
                continue
            # Misses a later record proves were mid-stream gaps are withheld.
            ledger.withheld.extend(range(serial - misses, serial))
            misses = 0
            ledger.served += 1
            ledger.last_served = serial
            planned = classify(payload, serial, ledger)
            if planned is not None:
                row, docket_id = planned
                ledger.candidates.append(row)
                self.payloads[_payload_key(term, serial)] = (payload, docket_id)
            serial += 1


def _payload_key(term: int, serial: int) -> str:
    return scotus_docket_slug(term, serial, form="application")


def _corpus_classifier(
    conn: sqlite3.Connection, data_root: Path, term: int
) -> Callable[[dict[str, Any], int, TermLedger], tuple[PlannedRow, int] | None]:
    """The one-process classifier: identity, ownership and the prediction guard."""
    # The identity join, read once for the Term rather than once per serial:
    # the per-number join walks every SCOTUS row.
    matches = corpus.scotus_case_ids_by_docket_number_prefix(conn, f"{term:02d}A")

    def classify(
        payload: dict[str, Any], serial: int, ledger: TermLedger
    ) -> tuple[PlannedRow, int] | None:
        return _plan(conn, data_root, payload, term, serial, ledger, matches)

    return classify


def _served_as_problem(payload: dict[str, Any], term: int, serial: int) -> str | None:
    """Why a served record is not the serial it was fetched as, or ``None``."""
    number = scotus_docket_slug(term, serial, form="application")
    served = str(payload.get("CaseNumber"))
    served_as = parse_scotus_application_number(
        corpus.strip_docket_annotation(str(payload.get("CaseNumber") or "").strip())
    )
    if served_as != (term, serial):
        # Upstream text in a run summary: truncated, and repr-escaped.
        return f"served docket number {served[:32]!r} is not {number}"
    return None


def _preview(
    payload: dict[str, Any], serial: int, ledger: TermLedger
) -> tuple[PlannedRow, int] | None:
    """The corpus-free classifier: the served-number check and a mapped preview.

    The record is mapped through the shared live mapping with no docket id yet
    (identity is the writer's, against the corpus it writes), so the ledger
    can count kinds and dispositions; the case id and the onboard/enrich split
    stay unresolved.
    """
    number = scotus_docket_slug(ledger.term, serial, form="application")
    if (why := _served_as_problem(payload, ledger.term, serial)) is not None:
        ledger.held.append({"docket": number, "reason": why})
        return None
    row = from_live_record(map_live_docket(payload, 0, form="application"))
    return (
        PlannedRow(
            docket_number=number,
            serial=serial,
            case_id=None,
            action="unresolved",
            application_kind=None if row.application_kind is None else str(row.application_kind),
            capital_case=bool(row.capital_case),
            referred_to_court=row.referred_to_court,
            disposition=None if row.disposition is None else str(row.disposition),
            date_filed=row.date_filed,
            date_decided=row.date_decided,
            counsel=len(row.counsel),
        ),
        0,
    )


def backfill_applications(  # noqa: PLR0913 - the pass's knobs, each a documented CLI flag
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    terms: Sequence[int] = DEFAULT_TERMS,
    *,
    today: date,
    apply: bool = False,
    max_rows: int | None = None,
    end_misses: int = DEFAULT_END_MISSES,
    limit: int | None = None,
    cache: DocketCache | None = None,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> ApplicationBackfillResult:
    """Enumerate each Term's applications; on ``apply``, land the unowned ones.

    ``limit`` caps fetches across the whole invocation (a sampled dry run), and
    ``deadline`` (a ``time_fn`` reading) stops the walk before the caller's own
    clock does, so a slow upstream still leaves a printed ledger. ``max_rows``
    is the apply's refusal threshold. The apply lands only a reading in which
    every Term was walked to its end: a walk stopped by the limit, the deadline
    or an upstream error is refused whole before the first write, so no half
    Term lands. Terms are two-digit October Terms, walked in the order given.
    """
    if apply and max_rows is None:
        raise ValueError("an apply needs max_rows, the count read off a dry run")
    if apply and cache is not None:
        raise ValueError("a cached record is not a host-scoped fetch; an apply reads upstream")
    result = ApplicationBackfillResult()
    walk = _Walk(client, end_misses, limit, cache, deadline, time_fn)
    with corpus.connect(corpus_db_path) as conn:
        for term in dict.fromkeys(terms):
            stored, owned = _stored_serials(conn, term)
            result.terms.append(
                walk.walk_term(
                    term,
                    max(stored) if stored else None,
                    owned,
                    _corpus_classifier(conn, data_root, term),
                )
            )
    if not apply:
        return result
    assert max_rows is not None  # checked on entry
    return _land(result, walk.payloads, corpus_db_path, data_root, today=today, max_rows=max_rows)


def _land(
    result: ApplicationBackfillResult,
    payloads: Mapping[str, tuple[dict[str, Any], int]],
    corpus_db_path: Path,
    data_root: Path,
    *,
    today: date,
    max_rows: int,
) -> ApplicationBackfillResult:
    """The apply's refusals, then each candidate through the live channel's ingest."""
    short = {f"OT20{t.term:02d}": t.stopped for t in result.terms if t.stopped != "end"}
    if short:
        result.refused = (
            f"the reading did not reach every Term's end ({short}), so no half Term is "
            "landed; re-dispatch once upstream serves"
        )
        return result
    if len(result.candidates) > max_rows:
        result.refused = (
            f"{len(result.candidates)} row(s) to land, above the bound of {max_rows}; "
            "read the dry run again before raising it"
        )
        return result
    for row in result.candidates:
        assert row.case_id is not None  # a landed candidate is always resolved
        payload, docket_id = payloads[row.docket_number]
        ingest_live_payload(
            corpus_db_path, data_root, payload, docket_id, today=today, form="application"
        )
        result.written.append(row.case_id)
    result.applied = True
    return result


# --- the handoff --------------------------------------------------------------------

#: The highest serial a plan or projection may name: no Term has reached a
#: tenth of it.
_MAX_SERIAL: Final = 20_000


class TermSerials(BaseModel):
    """One Term's stored application serials, as the walk reads them."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    term: int = Field(ge=0, le=99)
    stored_max_serial: int | None = Field(ge=1, le=_MAX_SERIAL)
    owned: list[int] = Field(max_length=_MAX_SERIAL)


class ApplicationProjection(BaseModel):
    """The corpus facts the walk needs: each Term's highest stored serial and the live-owned ones.

    Public: an application serial is the Court's own docket number (``24A123``
    is Term 24, serial 123), and the two facts say only how far the corpus's
    rows for the Term reach and which of them the live channel polls — no row
    content, snapshot or CourtListener field.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/application-projection"] = "fedcourts/application-projection"
    version: Literal[1] = 1
    terms: list[TermSerials] = Field(max_length=100)


class ServedDocket(BaseModel):
    """One served record the walk would land, verbatim as upstream served it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    term: int = Field(ge=0, le=99)
    serial: int = Field(ge=1, le=_MAX_SERIAL)
    payload: dict[str, Any]


class ApplicationPlan(BaseModel):
    """What the credential-free walk read: the file the writer job lands.

    Each served record is the supremecourt.gov docket JSON verbatim, party
    contact blocks included; the rest is the structured fields the walk parsed
    from those records. That is the whole of what the PII carve-out in
    ``docs/data-sources.md`` (*PII stance*) lets cross as run-repair's one-day
    ``repair-plan-<run_id>`` artifact, so the writer refuses a plan carrying
    anything else (:func:`_plan_shape_problem`): a record that is not shaped as
    a served docket, or a structured field its record does not map to.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/application-plan"] = "fedcourts/application-plan"
    version: Literal[1] = 1
    terms: list[TermLedger] = Field(max_length=100)
    served: list[ServedDocket] = Field(max_length=_MAX_SERIAL)


def application_projection(conn: sqlite3.Connection, terms: Sequence[int]) -> ApplicationProjection:
    """Each Term's stored-serial reading, for the walk that cannot open the corpus."""
    out: list[TermSerials] = []
    for term in dict.fromkeys(terms):
        stored, owned = _stored_serials(conn, term)
        out.append(
            TermSerials(
                term=term,
                stored_max_serial=max(stored) if stored else None,
                owned=sorted(owned),
            )
        )
    return ApplicationProjection(terms=out)


def plan_applications(
    client: SupremeCourtClient,
    projection: ApplicationProjection,
    terms: Sequence[int],
    *,
    end_misses: int = DEFAULT_END_MISSES,
    limit: int | None = None,
    cache: DocketCache | None = None,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> tuple[ApplicationBackfillResult, ApplicationPlan]:
    """Walk each Term against the projection, with no corpus: the dry-run ledger and its plan."""
    by_term = {t.term: t for t in projection.terms}
    wanted = list(dict.fromkeys(terms))
    if sorted(by_term) != sorted(wanted):
        raise HandoffRefused(
            f"the projection was read for Terms {sorted(by_term)}, not {sorted(wanted)}"
        )
    result = ApplicationBackfillResult()
    walk = _Walk(client, end_misses, limit, cache, deadline, time_fn)
    for term in wanted:
        state = by_term[term]
        result.terms.append(
            walk.walk_term(term, state.stored_max_serial, set(state.owned), _preview)
        )
    served = [
        ServedDocket(
            term=ledger.term, serial=row.serial, payload=walk.payloads[row.docket_number][0]
        )
        for ledger in result.terms
        for row in ledger.candidates
    ]
    return result, ApplicationPlan(terms=result.terms, served=served)


#: The top-level keys a supremecourt.gov docket JSON carries, read off the
#: served application and cert dockets. The plan may carry the Court's served
#: record and nothing else, so a record with any other key is refused with the
#: whole plan; a key upstream adds later surfaces as that refusal, naming it.
SERVED_DOCKET_KEYS: Final = frozenset(
    {
        "AttorneyHeaderOther",
        "AttorneyHeaderPetitioner",
        "AttorneyHeaderRespondent",
        "CaseNumber",
        "DocketedDate",
        "Links",
        "LowerCourt",
        "LowerCourtCaseNumbers",
        "LowerCourtDecision",
        "Other",
        "Petitioner",
        "PetitionerTitle",
        "ProceedingsandOrder",
        "QPLink",
        "RelatedCaseNumber",
        "Respondent",
        "RespondentTitle",
        "bCapitalCase",
        "sJsonCaseNumber",
        "sJsonCaseType",
        "sJsonCreationDate",
        "sJsonTerm",
    }
)

#: The one note an honest corpus-free walk files as held: the served-number
#: check's (:func:`_served_as_problem`).
_HELD_REASON_PREFIX: Final = "served docket number "


def _served_docket_problem(payload: Mapping[str, Any]) -> str | None:
    """Why ``payload`` is not shaped as a supremecourt.gov docket JSON, or ``None``."""
    unknown = sorted(set(payload) - SERVED_DOCKET_KEYS)
    if unknown:
        # Upstream (or forged) text in a run summary: truncated, and repr-escaped.
        return (
            f"carries {len(unknown)} key(s) a served docket does not, the first {unknown[0][:32]!r}"
        )
    if not isinstance(payload.get("CaseNumber"), str) or not isinstance(
        payload.get("ProceedingsandOrder"), list
    ):
        return "lacks a served docket's CaseNumber string or ProceedingsandOrder list"
    return None


def _plan_shape_problem(plan: ApplicationPlan, terms: Sequence[int]) -> str | None:  # noqa: PLR0911, PLR0912 - one return per check
    """Why a plan cannot have come from an honest walk of ``terms``.

    The plan crosses a public artifact under the PII carve-out, which admits
    served docket JSON and the structured fields parsed from it, nothing more.
    So beyond the walk's own consistency, every served record must be shaped as
    a supremecourt.gov docket, every planned row must be exactly the preview its
    record maps to, and every held note must be the served-number check's.
    """
    read = [ledger.term for ledger in plan.terms]
    if read != list(dict.fromkeys(terms)):
        return f"was read for Terms {read}, not {list(dict.fromkeys(terms))}"
    previews = {(ledger.term, row.serial) for ledger in plan.terms for row in ledger.candidates}
    rows = [row for ledger in plan.terms for row in ledger.candidates]
    if any(row.case_id is not None or row.action != "unresolved" for row in rows):
        return "resolves a case id or an action, which only the writer does"
    notes = [note for ledger in plan.terms for note in (*ledger.held, *ledger.failures)]
    if any(set(note) != {"docket", "reason"} for note in notes):
        return "carries a ledger note without its docket and reason"
    for ledger in plan.terms:
        for note in (*ledger.held, *ledger.failures):
            parsed = parse_scotus_application_number(note["docket"])
            if parsed is None or parsed[0] != ledger.term:
                return "carries a ledger note on a docket outside its Term"
        if any(not note["reason"].startswith(_HELD_REASON_PREFIX) for note in ledger.held):
            return "holds a record back for a reason a corpus-free walk never gives"
    seen: set[tuple[int, int]] = set()
    for docket in plan.served:
        key = (docket.term, docket.serial)
        if key in seen:
            return f"serves {_payload_key(*key)} twice"
        seen.add(key)
        if key not in previews:
            return f"serves {_payload_key(*key)}, which its ledger does not list"
        if (why := _served_docket_problem(docket.payload)) is not None:
            return f"serves {_payload_key(*key)} as something other than a docket JSON: {why}"
        if (why := _served_as_problem(docket.payload, docket.term, docket.serial)) is not None:
            return f"serves a record under the wrong number: {why}"
    if seen != previews:
        return "lists a record its served set does not carry"
    payloads = {(docket.term, docket.serial): docket.payload for docket in plan.served}
    for ledger in plan.terms:
        scratch = TermLedger(term=ledger.term, end_misses=ledger.end_misses, stored_max_serial=None)
        for row in ledger.candidates:
            try:
                derived = _preview(payloads[(ledger.term, row.serial)], row.serial, scratch)
            except (TypeError, ValueError, KeyError, AttributeError):
                return f"serves {row.docket_number} as a record the live mapping cannot read"
            if derived is None or derived[0] != row:
                return f"lists {row.docket_number} with fields its served record does not map to"
    return None


def apply_application_plan(
    plan: ApplicationPlan,
    corpus_db_path: Path,
    data_root: Path,
    terms: Sequence[int],
    *,
    today: date,
    apply: bool,
    max_rows: int | None = None,
) -> ApplicationBackfillResult:
    """Re-check a plan whole, then classify and land it against the corpus at ``corpus_db_path``.

    The plan is untrusted input — written by the job that fetched upstream —
    so it must be for exactly ``terms``, carry each served record once, list
    each in its ledger, and serve each under the number it was fetched as; any
    departure refuses the whole plan with :class:`HandoffRefused` before
    anything is written. Each record is then classified as a one-process run
    classifies it, against the corpus about to be written: a serial the live
    channel owns now is counted live-owned and never touched, identity is the
    shared join, and an open event carrying a committed prediction holds the
    row back. The apply's own refusals follow — a walk that stopped short of a
    Term's end, a count above ``max_rows`` — and then the shared ingest.
    Fetches nothing.
    """
    if apply and max_rows is None:
        raise ValueError("an apply needs max_rows, the count read off a dry run")
    if (why := _plan_shape_problem(plan, terms)) is not None:
        raise HandoffRefused(f"the plan {why}")
    served: dict[int, list[ServedDocket]] = {}
    for docket in plan.served:
        served.setdefault(docket.term, []).append(docket)
    result = ApplicationBackfillResult()
    payloads: dict[str, tuple[dict[str, Any], int]] = {}
    with corpus.connect(corpus_db_path) as conn:
        for read in plan.terms:
            _, owned = _stored_serials(conn, read.term)
            ledger = read.model_copy(update={"candidates": [], "held": list(read.held)}, deep=True)
            classify = _corpus_classifier(conn, data_root, read.term)
            for docket in served.get(read.term, []):
                if docket.serial in owned:
                    ledger.live_owned += 1
                    continue
                planned = classify(docket.payload, docket.serial, ledger)
                if planned is not None:
                    row, docket_id = planned
                    ledger.candidates.append(row)
                    payloads[row.docket_number] = (docket.payload, docket_id)
            result.terms.append(ledger)
    if not apply:
        return result
    assert max_rows is not None  # checked on entry
    return _land(result, payloads, corpus_db_path, data_root, today=today, max_rows=max_rows)


def render_ledger(result: ApplicationBackfillResult, *, max_rows: int | None = None) -> str:
    """The ledger a maintainer reads the apply's bound off, as Markdown-safe text."""
    verb = "landed" if result.applied else "would land"
    lines: list[str] = []
    for ledger in result.terms:
        by_action = {"onboard": 0, "enrich": 0, "unresolved": 0}
        by_kind: dict[str, int] = {}
        capital = referred = pending = 0
        for row in ledger.candidates:
            by_action[row.action] += 1
            kind = row.application_kind or "unread"
            by_kind[kind] = by_kind.get(kind, 0) + 1
            capital += row.capital_case
            referred += bool(row.referred_to_court)
            pending += row.disposition is None and row.date_decided is None
        end = {
            "end": f"end after {ledger.end_misses} consecutive misses past serial "
            f"{ledger.stored_max_serial or 0}",
            "limit": "stopped at the fetch limit",
            "deadline": "stopped at the run deadline",
            "upstream-error": "stopped by an upstream error",
            None: "not walked",
        }[ledger.stopped]
        lines.append(
            f"OT20{ledger.term:02d}: {verb} {len(ledger.candidates)} row(s) "
            f"(onboard={by_action['onboard']} enrich={by_action['enrich']}); "
            f"fetched={ledger.fetched} served={ledger.served} live_owned={ledger.live_owned} "
            f"withheld={len(ledger.withheld)} held={len(ledger.held)} "
            f"failures={len(ledger.failures)}; stored max {ledger.stored_max_serial}; "
            f"last served {ledger.last_served}; {end}"
        )
        if by_action["unresolved"]:
            lines.append(
                f"  unresolved={by_action['unresolved']}: read without the corpus, so the "
                "writer resolves identity, re-reads ownership and applies the prediction "
                "guard; an apply lands at most this many"
            )
        kinds = " ".join(f"{kind}={count}" for kind, count in sorted(by_kind.items()))
        lines.append(
            f"  by kind: {kinds or 'none'}; capital={capital} referred={referred} pending={pending}"
        )
        if ledger.withheld:
            lines.append(f"  withheld serials: {', '.join(map(str, ledger.withheld))}")
        for held in ledger.held:
            lines.append(f"  held {held['docket']}: {held['reason']}")
        for failure in ledger.failures:
            lines.append(f"  failed {failure['docket']}: {failure['reason']}")
        for row in ledger.candidates:
            lines.append(
                f"  {row.action} {row.docket_number} -> {row.case_id}: "
                f"kind={row.application_kind} capital={row.capital_case} "
                f"referred={row.referred_to_court} disposition={row.disposition} "
                f"filed={row.date_filed} decided={row.date_decided} counsel={row.counsel}"
            )
    total = len(result.candidates)
    mode = "applied" if result.applied else "dry-run"
    bound = "" if max_rows is None else f" (--max-rows {max_rows})"
    lines.append(f"backfill-applications ({mode}): {verb} {total} row(s){bound}")
    if result.refused:
        lines.append(f"backfill-applications: refused — {result.refused}")
    return "\n".join(lines)
