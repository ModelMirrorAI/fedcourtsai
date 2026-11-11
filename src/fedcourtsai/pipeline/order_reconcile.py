"""Reconcile the corpus with the Court's order lists, docket by docket.

Every other completeness check starts from the corpus and so can only find a
ruling the corpus already holds. This one starts from what the Court published:
each order list and miscellaneous order the Court lists for a window of days is
split into one entry per docket (:func:`fedcourtsai.pipeline.order_lineups.list_entries`),
and each entry is checked against the corpus four ways.

1. **Presence.** The docket or application number has a corpus row.
2. **Disposition.** What the list says happened agrees with the row's recorded
   disposition and its date.
3. **Outcome record.** Where the row is selected or an event of the order's
   stage carries a prediction, the ledger holds an ``outcome.json`` for it.
4. **Timeliness.** For an application, the row's first stored snapshot is
   dated no later than the order: an application first seen only after it was
   ruled on could never have been forecast. Snapshots are dated to the day, so
   one first stored on the order's own day counts as timely.

**What the list says.** The section heading is read first, because it is the
Court's own classification and no grammar of this pipeline stands between it
and the reading: a docket under ``CERTIORARI DENIED`` was denied, whatever its
entry goes on to say about a motion. Under a denial heading the text is asked
two narrow questions only, each by a pattern of this module: whether it
dismisses the petition instead (Rule 39.8 dismissals are printed among the
denials), and whether it denies leave to proceed in forma pauperis with time
to pay, which leaves the petition pending. Under ``ORDERS IN PENDING CASES``
it is asked whether the Solicitor General was invited. A disposition is read
out of order text only where no heading gives one (a summary disposition, an
application, a list that prints no heading), and there the readers are the
ones ingest applies to docket entries
(:func:`~fedcourtsai.pipeline.cert_signals.match_disposition_signal`,
:func:`~fedcourtsai.pipeline.interim_signals.match_interim_disposition`), with
one difference: an application's order is read clause by clause, so a side
motion's word in the same sentence is not taken for the application's. A
misreading those share is therefore not caught on such an entry; the heading
reading, which covers most of a list, is independent of them.

**One status per entry**, first match:

- ``out_of_frame``: a motion (``26M23``) or original (``22O141``) number, which
  the corpus does not follow;
- ``no_row``: the corpus has no row for the number, whatever the entry says;
- ``unparsed``: an entry under a heading outside the vocabulary here, or order
  text the readers take no disposition from where one was expected. Counted on
  every report, so a grammar failure on a docket the corpus holds never reads
  as a clean list;
- ``presence_only``: the entry disposes of nothing the corpus records (an order
  on a motion, a rehearing denied, an in forma pauperis denial that leaves the
  petition pending), or the docket is named by a document that is not printed
  as a list, whose order is not read. Presence is all there is to check;
- ``renewed``: an application the corpus already records with the same
  disposition on an earlier date, which is how a renewed application to a
  second Justice reads;
- ``disposition_mismatch`` / ``date_mismatch``: the row says something else
  happened, or the same thing on another day;
- ``matched``.

**Alarms.** A listed docket with no row once the list is 48 hours old, a
mismatch once it is 12 hours old (two six-hour pull windows), an outcome
record still missing once it is three days old, and any document the reader
could not read whole (a failed fetch, an extraction with no text or cut at
the cap, an order list that yields no entry). The Court's listing dates a
document to the day and not the hour, so a list's age is counted from the end
of its day, UTC: an alarm can be late by up to that day, never early.
Everything else is reported and never alarms: the unparsed and out-of-frame
counts, the renewed applications, the applications first stored after their
order's day, those with no stored snapshot to date them by, and the documents
whose cut recorded a problem.

**Read-only, and not a scored figure.** Nothing here writes the corpus, the
content store, the ledger or ``data/``. The readout is outcome-selected by
construction and enters no board, base rate or release figure. The report
carries docket numbers, case ids, section headings, disposition labels and
dates: public court record and the pipeline's own identifiers, never stored
snapshot or document text.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel

from .. import corpus
from ..matrix import event_has_predictions
from ..paths import CasePaths
from ..schemas import GRANTED_DISPOSITIONS, Disposition, Stage
from . import moments
from .cert_signals import match_disposition_signal
from .interim_signals import application_clauses, match_interim_disposition
from .order_lineups import (
    FetchedDocument,
    ListEntry,
    OrderDocumentRef,
    OrderFetcher,
    list_entries,
    listing_terms,
    split_document,
)

#: How old a list must be before a docket it names with no corpus row alarms.
NO_ROW_GRACE: Final = timedelta(hours=48)
#: Two pull windows: how old a list must be before a mismatch alarms.
MISMATCH_GRACE: Final = timedelta(hours=12)
#: How long after its order a selected or predicted event may lack an outcome record.
OUTCOME_GRACE: Final = timedelta(days=3)
#: How far back the command reads by default. Every threshold above has passed
#: well inside it, so a finding is re-reported for days after it first alarms.
DEFAULT_LOOKBACK_DAYS: Final = 14

_CORPUS_DOCKET_RE = re.compile(r"^\d{2}-\d{1,5}$|^\d{2}A\d{1,5}$")
_CVSG_RE = re.compile(r"\bSolicitor General is invited to file\b", re.I)
# An in forma pauperis denial that gives the petitioner time to pay: the
# petition stays pending whatever heading the entry is printed under.
_FEE_ALLOWANCE_RE = re.compile(r"\ballowed until\b.{0,120}?\bto pay the docketing fees?\b", re.I)
_PLURAL_MOTIONS_RE = re.compile(r"\bmotions\b[^.;]{0,120}?\bare denied\b", re.I)
_PETITION_DISMISSED_RE = re.compile(
    r"\bpetitions?\b[^.;]{0,160}?\b(?:is|are)\s+dismissed\b"
    + r"|\bappeals?\b[^.;]{0,80}?\b(?:is|are)\s+dismissed\b",
    re.I,
)
_CHAMBERS_DOCKET_RE = re.compile(r"^No\.\s+(?P<docket>\d{2}-\d{1,5}|\d{2}A\d{1,5})$")

ReadingKind = Literal["cert", "application", "cvsg", "presence"]


class EntryStatus(StrEnum):
    """What one listed docket's comparison with the corpus found."""

    matched = "matched"
    no_row = "no_row"
    disposition_mismatch = "disposition_mismatch"
    date_mismatch = "date_mismatch"
    renewed = "renewed"
    presence_only = "presence_only"
    out_of_frame = "out_of_frame"
    unparsed = "unparsed"


#: The statuses that are a disagreement between the list and the corpus.
MISMATCH_STATUSES: Final = frozenset({EntryStatus.disposition_mismatch, EntryStatus.date_mismatch})


class Expectation(BaseModel):
    """What one list entry says happened to its docket.

    ``dispositions`` is every label the corpus may carry and agree with the
    list; empty where the entry disposes of nothing (``presence``) or says the
    Solicitor General was invited (``cvsg``). ``unparsed`` carries the reason
    no reading was taken.
    """

    kind: ReadingKind
    dispositions: frozenset[Disposition] = frozenset()
    unparsed: str | None = None
    out_of_frame: bool = False


def _presence() -> Expectation:
    return Expectation(kind="presence")


def _unparsed(reason: str) -> Expectation:
    return Expectation(kind="presence", unparsed=reason)


def _application_reading(text: str) -> Expectation:
    """The registered interim reading of the clauses whose subject is an application.

    Clause-scoped, so an order on a motion about the application ("leave to
    file redacted copies of the application is granted") disposes of nothing.
    """
    clauses = application_clauses(text)
    if not clauses:
        return _presence()
    for clause in clauses:
        reading = match_interim_disposition(clause)
        if reading is not None:
            return Expectation(kind="application", dispositions=frozenset({reading[0]}))
    return _unparsed("an application's order text reads as no disposition")


def _heading_reading(entry: ListEntry, section: str, text: str) -> Expectation | None:
    """The reading a dispositive heading gives, or ``None`` where it gives none."""
    if section.endswith("GRANTED") or section.endswith("NOTED"):
        return Expectation(
            kind="cert",
            dispositions=frozenset({Disposition.granted, Disposition.granted_in_part}),
        )
    if section.endswith("DISMISSED"):
        return Expectation(kind="cert", dispositions=frozenset({Disposition.dismissed}))
    if not section.endswith("DENIED"):
        return None
    if _FEE_ALLOWANCE_RE.search(text) and (entry.closes_run or _PLURAL_MOTIONS_RE.search(text)):
        # The allowance speaks of the caption it follows, and of the captions
        # above that one only where it says so in the plural.
        return _presence()
    if _PETITION_DISMISSED_RE.search(text):
        # A petition dismissed under Rule 39.8 is printed among the denials.
        labels = {Disposition.dismissed}
        if not entry.closes_run:
            labels.add(Disposition.denied)
        return Expectation(kind="cert", dispositions=frozenset(labels))
    return Expectation(kind="cert", dispositions=frozenset({Disposition.denied}))


def read_entry(entry: ListEntry) -> Expectation:  # noqa: PLR0911 - one return per entry shape
    """What one list entry says happened to its docket, by heading first."""
    if not _CORPUS_DOCKET_RE.match(entry.docket):
        return Expectation(kind="presence", out_of_frame=True)
    section = entry.section or ""
    text = " ".join(entry.text.split())
    if "REHEARING" in section:
        return _presence()
    if corpus.is_scotus_application_form(entry.docket):
        return _application_reading(text)
    if "PENDING CASE" in section:
        return Expectation(kind="cvsg") if _CVSG_RE.search(text) else _presence()
    if "DISPOSITION" in section or not section:
        signal = match_disposition_signal(text, direct_appeal_exit=section.startswith("APPEAL"))
        if signal is None:
            where = "a summary disposition" if section else "an entry under no heading"
            return _unparsed(f"{where} reads as no disposition")
        return Expectation(kind="cert", dispositions=frozenset({signal[0]}))
    heading = _heading_reading(entry, section, text)
    if heading is None:
        return _unparsed(f"a heading outside the vocabulary: {section}")
    return heading


class EntryFinding(BaseModel):
    """One listed docket, what the list says, what the corpus holds, and the verdict."""

    docket: str
    section: str | None
    status: EntryStatus
    kind: ReadingKind
    expected: list[str] = []
    case_id: str | None = None
    recorded: str | None = None
    recorded_on: date | None = None
    detail: str | None = None
    missing_outcomes: list[str] = []
    first_observed: date | None = None
    observed_late: bool = False
    alarms: list[str] = []


class DocumentReconciliation(BaseModel):
    """One document the Court lists: whether it was read, and its entries' verdicts."""

    url: str
    kind: str
    day: date
    status: Literal["read", "refused"]
    reason: str | None = None
    problems: list[str] = []
    counts: dict[str, int] = {}
    entries: list[EntryFinding] = []


class OrderReconciliation(BaseModel):
    """Every document listed in a window, reconciled against the corpus."""

    as_of: datetime
    since: date
    until: date
    documents: list[DocumentReconciliation]
    counts: dict[str, int]
    late_applications: list[str]
    undated_applications: list[str]
    alarms: list[str]


#: The corpus's answer about one case, read once however many entries name it.
FirstObserved = Callable[[str], date | None]


def find_rows(conn: corpus.ReadConnection, dockets: Sequence[str]) -> dict[str, str]:
    """The SCOTUS row for each docket number, keyed by normalized number.

    The live slice first, off its index. Only the numbers that misses are
    looked for among every SCOTUS row, in one walk: a docket the live channel
    never polled can still hold a row, and reporting it absent would be the
    one false alarm this check must not raise. Two rows on one number resolve
    to the lowest docket id, as the identity join does.
    """
    wanted = {n for raw in dockets if (n := corpus.normalize_docket_number(raw)) is not None}
    found = dict(corpus.live_scotus_case_ids_by_docket_numbers(conn, sorted(wanted)) or {})
    missing = wanted - found.keys()
    if not missing:
        return found
    matched: dict[int, str] = {}
    for record in conn.execute(
        "SELECT rowid AS rid, docket_number FROM cases INDEXED BY idx_cases_court WHERE court = ?",
        ("scotus",),
    ):
        norm = corpus.normalize_docket_number(str(record["docket_number"] or ""))
        if norm in missing:
            matched[int(record["rid"])] = norm
    if not matched:
        return found
    marks = ",".join("?" for _ in matched)
    for record in conn.execute(
        f"SELECT rowid AS rid, case_id FROM cases WHERE rowid IN ({marks})", list(matched)
    ):
        norm, case_id = matched[int(record["rid"])], str(record["case_id"])
        held = found.get(norm)
        if held is None or _docket_id(case_id) < _docket_id(held):
            found[norm] = case_id
    return found


def _docket_id(case_id: str) -> int:
    return int(case_id.rsplit("/", 1)[-1])


def _missing_outcomes(
    conn: corpus.ReadConnection, data_root: Path, row: corpus.CorpusRow, stage: Stage
) -> list[str]:
    """The stage's events that owe an outcome record and have none.

    An event owes one when it carries a committed prediction, or when its row
    is selected, in predict scope, and the event is not closed without an
    outcome on purpose. An event's stage is its own where it records one, else
    the one its id declares.
    """
    court, docket = row.case_id.split("/", 1)
    paths = CasePaths(data_root, court, int(docket))
    missing: list[str] = []
    for event in corpus.events_for_case(conn, row.case_id):
        if moments.event_stage(event.stage, event.event_id) != stage:
            continue
        predicted = event_has_predictions(data_root, court, int(docket), event.event_id)
        selected = row.salience_selected and not row.predict_excluded
        owed = predicted or (selected and not event.resolved_without_outcome)
        if owed and not paths.event(event.event_id).outcome.exists():
            missing.append(event.event_id)
    return missing


def _compare(  # noqa: PLR0911 - one return per verdict
    row: corpus.CorpusRow, expected: Expectation, day: date
) -> tuple[EntryStatus, str]:
    """The verdict for a row the list disposes of, and the reason for a mismatch."""
    if expected.kind == "cvsg":
        if row.cvsg_date == day:
            return EntryStatus.matched, ""
        return EntryStatus.date_mismatch, f"the invitation is recorded on {row.cvsg_date}"
    recorded = Disposition(row.disposition) if row.disposition is not None else None
    if recorded is None:
        return EntryStatus.disposition_mismatch, "the row records no disposition"
    if recorded not in expected.dispositions:
        return EntryStatus.disposition_mismatch, f"the row records {recorded.value}"
    dates = {row.date_cert_granted, row.date_cert_denied, row.date_decided} - {None}
    if day in dates:
        return EntryStatus.matched, ""
    if expected.kind == "application" and row.date_decided is not None and row.date_decided < day:
        return EntryStatus.renewed, ""
    return EntryStatus.date_mismatch, "the row dates it " + (
        ", ".join(sorted(str(d) for d in dates)) or "on no day"
    )


def _recorded_on(row: corpus.CorpusRow) -> date | None:
    if row.disposition in {d.value for d in GRANTED_DISPOSITIONS}:
        return row.date_cert_granted or row.date_decided
    return row.date_cert_denied or row.date_decided


def reconcile_entry(
    entry: ListEntry,
    *,
    day: date,
    now: datetime,
    conn: corpus.ReadConnection,
    data_root: Path,
    rows: Mapping[str, str],
    first_observed: FirstObserved,
    order_read: bool = True,
) -> EntryFinding:
    """One listed docket's verdict against the corpus as it stands at ``now``.

    ``order_read`` is false for a docket named by a document that is not
    printed as a list, whose order is not read: presence is all it is checked
    for.
    """
    expected = read_entry(entry)
    if not order_read and not expected.out_of_frame:
        expected = _presence()
    finding = EntryFinding(
        docket=entry.docket,
        section=entry.section,
        status=EntryStatus.matched,
        kind=expected.kind,
        expected=sorted(d.value for d in expected.dispositions),
    )
    if expected.out_of_frame:
        finding.status = EntryStatus.out_of_frame
        return finding
    age = now - datetime.combine(day + timedelta(days=1), time(), tzinfo=UTC)
    case_id = rows.get(corpus.normalize_docket_number(entry.docket) or "")
    row = corpus.get_row(conn, case_id) if case_id is not None else None
    if row is None:
        finding.status = EntryStatus.no_row
        if age >= NO_ROW_GRACE:
            finding.alarms.append("no corpus row")
        return finding
    finding.case_id = row.case_id
    finding.recorded = row.disposition
    finding.recorded_on = _recorded_on(row)
    application = corpus.is_scotus_application_form(entry.docket)
    if application:
        finding.first_observed = first_observed(row.case_id)
        finding.observed_late = finding.first_observed is not None and finding.first_observed > day
    if expected.unparsed is not None:
        finding.status = EntryStatus.unparsed
        finding.detail = expected.unparsed
        return finding
    if expected.kind == "presence":
        finding.status = EntryStatus.presence_only
        return finding
    finding.status, detail = _compare(row, expected, day)
    finding.detail = detail or None
    if finding.status in MISMATCH_STATUSES and age >= MISMATCH_GRACE:
        finding.alarms.append(finding.status.value.replace("_", " "))
    if expected.kind != "cvsg" and finding.status != EntryStatus.presence_only:
        stage = Stage.interim if application else Stage.cert
        finding.missing_outcomes = _missing_outcomes(conn, data_root, row, stage)
        if finding.missing_outcomes and age >= OUTCOME_GRACE:
            finding.alarms.append("no outcome record: " + ", ".join(finding.missing_outcomes))
    return finding


def document_entries(text: str) -> tuple[list[ListEntry], list[str], bool]:
    """Every docket one document's text names, the cut's problems, and whether it is a list.

    The list proper's entries where it has any. A document with none is an
    opinion relating to orders or an order in chambers, neither printed as a
    list: the dockets its appended sections or its ``No.`` line name come back
    as entries with no heading and no text, and the last value is false, so
    the caller checks them for presence and reads no order.
    """
    entries, problems = list_entries(text)
    if entries:
        return entries, problems, True
    named: list[str] = []
    for section in split_document(text).heads:
        named.extend(d for d in section.dockets if d not in named)
    for line in text.splitlines():
        match = _CHAMBERS_DOCKET_RE.match(" ".join(line.split()))
        if match is not None and match.group("docket") not in named:
            named.append(match.group("docket"))
    return [ListEntry(d, None, "", closes_run=True) for d in named], problems, False


def reconcile_document(
    document: FetchedDocument,
    *,
    now: datetime,
    conn: corpus.ReadConnection,
    data_root: Path,
    first_observed: FirstObserved,
) -> DocumentReconciliation:
    """Every entry of one fetched document against the corpus."""
    ref = document.ref
    assert ref is not None
    result = DocumentReconciliation(url=document.url, kind=ref.kind, day=ref.day, status="read")
    if document.text is None:
        result.status, result.reason = "refused", document.reason
        return result
    entries, problems, is_list = document_entries(document.text)
    result.problems = list(problems)
    if document.truncated:
        # A cut list is missing its last entries, and nothing says how many.
        result.status, result.reason = "refused", "the text was cut at the extraction cap"
        return result
    if not entries or (ref.kind == "order-list" and not is_list):
        result.status, result.reason = "refused", "the reader split no entry out of it"
        return result
    rows = find_rows(conn, [e.docket for e in entries if _CORPUS_DOCKET_RE.match(e.docket)])
    result.entries = [
        reconcile_entry(
            entry,
            day=ref.day,
            now=now,
            conn=conn,
            data_root=data_root,
            rows=rows,
            first_observed=first_observed,
            order_read=is_list,
        )
        for entry in entries
    ]
    result.counts = dict(sorted(Counter(f.status.value for f in result.entries).items()))
    return result


def refs_in_window(fetcher: OrderFetcher, since: date, until: date) -> list[OrderDocumentRef]:
    """Every document the Court lists from ``since`` through ``until``, each once, oldest first.

    Raises ``httpx.HTTPError`` when a listing is not served: a window whose
    listing cannot be read is not an empty window.
    """
    terms: list[int] = []
    for offset in range((until - since).days + 1):
        terms.extend(t for t in listing_terms(since + timedelta(days=offset)) if t not in terms)
    seen: set[str] = set()
    refs: list[OrderDocumentRef] = []
    for term in terms:
        for ref in fetcher.listed(term):
            if since <= ref.day <= until and ref.url not in seen:
                seen.add(ref.url)
                refs.append(ref)
    return sorted(refs, key=lambda r: (r.day, r.url))


def reconcile(
    documents: Sequence[FetchedDocument],
    *,
    since: date,
    until: date,
    now: datetime,
    conn: corpus.ReadConnection,
    data_root: Path,
    first_observed: FirstObserved,
) -> OrderReconciliation:
    """Reconcile every fetched document of a window. No network: the caller fetched."""
    cache: dict[str, date | None] = {}

    def observed(case_id: str) -> date | None:
        if case_id not in cache:
            try:
                cache[case_id] = first_observed(case_id)
            except Exception:
                # The store's answer feeds a count that never alarms; a fault
                # reading it must not cost the checks that do. The case is
                # reported undated.
                cache[case_id] = None
        return cache[case_id]

    results = [
        reconcile_document(d, now=now, conn=conn, data_root=data_root, first_observed=observed)
        for d in documents
    ]
    counts: Counter[str] = Counter()
    alarms: list[str] = []
    late: list[str] = []
    undated: list[str] = []
    for result in results:
        counts["documents"] += 1
        counts["documents_with_problems"] += bool(result.problems)
        counts["entries"] += len(result.entries)
        counts.update(result.counts)
        if result.status == "refused":
            counts["documents_refused"] += 1
            alarms.append(f"{result.day} {result.url}: not read ({result.reason})")
        for finding in result.entries:
            if finding.observed_late and finding.docket not in late:
                late.append(finding.docket)
            if (
                finding.case_id is not None
                and finding.first_observed is None
                and corpus.is_scotus_application_form(finding.docket)
                and finding.docket not in undated
            ):
                undated.append(finding.docket)
            alarms.extend(f"{result.day} {finding.docket}: {alarm}" for alarm in finding.alarms)
    return OrderReconciliation(
        as_of=now,
        since=since,
        until=until,
        documents=results,
        counts=dict(sorted(counts.items())),
        late_applications=late,
        undated_applications=undated,
        alarms=alarms,
    )


def fetch_window(fetcher: OrderFetcher, since: date, until: date) -> list[FetchedDocument]:
    """Fetch every order list and miscellaneous order listed in the window.

    An opinion relating to orders is fetched too: it names the dockets its
    order disposes of, which the presence check reads. Raises
    ``httpx.HTTPError`` on an unserved listing; a document that cannot be
    fetched or extracted is returned with its reason and refuses whole.
    """
    return [fetcher.document(ref.url, ref) for ref in refs_in_window(fetcher, since, until)]


def digest_lines(report: OrderReconciliation) -> list[str]:
    """One line per document, named by its file: entries read, matched, mismatched, unparsed."""
    lines: list[str] = []
    for document in report.documents:
        name = f"{document.day} {document.kind} {document.url.rsplit('/', 1)[-1]}"
        if document.status == "refused":
            lines.append(f"{name}: not read ({document.reason})")
            continue
        counts = Counter(document.counts)
        mismatched = sum(counts[s.value] for s in MISMATCH_STATUSES)
        lines.append(
            f"{name}: {len(document.entries)} entries read, "
            f"{counts[EntryStatus.matched.value]} matched, {mismatched} mismatched, "
            f"{counts[EntryStatus.no_row.value]} with no row, "
            f"{counts[EntryStatus.unparsed.value]} unparsed"
            + (f", {len(document.problems)} problems in the cut" if document.problems else "")
        )
    return lines


def render_markdown(report: OrderReconciliation, *, vintage: str | None = None) -> str:
    """The verdict as Markdown: the alarms, every document's line, then what is only reported."""
    verdict = "failing" if report.alarms else "passing"
    lines = [
        f"## Order-list reconciliation: {verdict}",
        "",
        f"Order documents the Court lists from {report.since} through {report.until}, "
        f"read at {report.as_of:%Y-%m-%d %H:%M}Z against the corpus"
        + (f" ({vintage})." if vintage else "."),
        "",
    ]
    if report.alarms:
        lines += ["### Alarms", "", *(f"- {alarm}" for alarm in report.alarms), ""]
    lines += ["### Per document", "", *(f"- {line}" for line in digest_lines(report)), ""]
    waiting = [
        f"{d.day} {f.docket}: {f.status.value.replace('_', ' ')}"
        + (f" ({f.detail})" if f.detail else "")
        for d in report.documents
        for f in d.entries
        if not f.alarms and (f.status in MISMATCH_STATUSES or f.status == EntryStatus.no_row)
    ]
    if waiting:
        lines += ["### Inside the grace period", "", *(f"- {item}" for item in waiting), ""]
    counts = Counter(report.counts)
    lines += [
        "### Reported, never an alarm",
        "",
        f"- Applications first stored after their order's day: {len(report.late_applications)}"
        + (f" ({', '.join(report.late_applications)})" if report.late_applications else ""),
        "- Applications with no stored snapshot to date them by: "
        f"{len(report.undated_applications)}"
        + (f" ({', '.join(report.undated_applications)})" if report.undated_applications else ""),
        f"- Documents whose cut recorded a problem: {counts['documents_with_problems']}",
        f"- Entries the reader took no disposition from: {counts[EntryStatus.unparsed.value]}",
        f"- Renewed applications already recorded: {counts[EntryStatus.renewed.value]}",
        f"- Motion and original numbers the corpus does not follow: "
        f"{counts[EntryStatus.out_of_frame.value]}",
        "",
    ]
    return "\n".join(lines)


__all__ = [
    "DEFAULT_LOOKBACK_DAYS",
    "EntryFinding",
    "EntryStatus",
    "OrderReconciliation",
    "digest_lines",
    "fetch_window",
    "find_rows",
    "read_entry",
    "reconcile",
    "render_markdown",
]
