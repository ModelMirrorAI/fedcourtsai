"""How often the executive prevails on the emergency docket — the executive success cut.

A standalone analytics artifact over the scope annotation (:mod:`.exec_action`):
the federal executive's record on the applications that challenge or defend a
general federal executive action, by administration and by who filed. Nothing a
predict or evaluate cell reads is derived from it, so a change here moves no
frozen input.

**Why not the party rates.** :mod:`.party_rates` reports a grant rate per
federal side. That is the executive's win rate where the government filed, and
its loss rate where a challenger did, because a challenger's application denied
is the government's win. This cut reads every row in the executive's
direction, so the two filers' cells and their pool share one meaning.

**What a cell is.** One administration x filer, where the filer is
``government`` (the federal government is the applicant) or ``challenger`` (it
is the respondent), with an ``all`` cell per administration pooling the two.

**What a rate is.** Wins over substantively decided rows. *Decided* is
granted in whole or in part, or denied; a win is a grant for a government
applicant and a denial for a challenger's application. Withdrawn applications
and those dismissed or denied as moot are counted beside the rate and never in
it, and so are pending and ``other`` rows, as the published tallies this cut is
replicated against do. Every cell carries its per-label counts so a reader can
recompute under another convention.

**A stored denial is re-read.** The corpus stores the registered interim
reading, which collapses a partial grant to ``denied`` and reads an application
denied as moot as ``denied`` too. Both errors move the executive's rate, and in
opposite directions on the two sides of the docket. So under the default
``finer`` reading, every in-scope or unknown-scope row stored ``denied`` is
re-read from its latest live-shaped snapshot under the finer interim reading
(:func:`.ingest.interim_reading`), which names both forms. A row with no live
snapshot, or no entry the reading matches, keeps its stored label and is
counted; so does one whose re-read entry is dated after ``through``, which the
cut's moment had not reached. The re-read is descriptive and writes nothing.
``registered`` keeps the stored labels.

**Deferred applications are pending.** An application the Court defers to
argument carries no disposition until it is decided, so it sits in
``pending``, outside the rate, as the published tallies exclude it.

**The population is the in-scope applications, extensions left out.**
Extensions of time are left out before scope is read. An in-scope application
whose ask the parser could not read is counted like any other and tallied
(``unknown_ask``), because granted federal applications sit among the
unreadable asks and the published tallies count them. One never
application-parsed is counted beside its cell, since it cannot be told from an
extension. A row the scope rule leaves ``unknown`` is counted per
administration beside every cell, and listed.

**The same population again, by controversy.** Beside the application cells,
the in-scope applications are grouped into controversies under
``controversy-v2`` (:mod:`.controversy`) and counted per administration and
filer, so applications the record links weigh once. A
controversy's result is its last decided application's; one with none decided
is indeterminate and sits beside the rate. The same applications are counted
once more per policy area (:mod:`.policy_area`), under ``policy-area-v2`` once
its measurement has passed and the hand-labeled ``policy-area-v1`` reference
until then; an application the source does not label is counted beside those
cells.

**One docket, one row; the date convention, moment and bound are the
caller's**, exactly as on the party rates cut: rows de-duplicate by docket
number, ``as_of_field`` is required, ``through`` places the cut at a past
moment, and ``since`` bounds the start where coverage begins mid-window.

**A row with no docketed date takes its first proceeding's.** Some
application dockets carry an empty docketed date, so the stored
``date_filed`` is null, and the row would sit in no administration. The first
proceeding entry is the application's submission, so where a live snapshot
is read its earliest entry date stands in, for the window, the ``filed``
attribution and the controversy's first application alike. Each review row
says which source its date came from, and ``filed_from_first_entry`` counts
the rows that took the fallback. Without a snapshot the row keeps no filing
date.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import date
from typing import Any, Final, Literal

from .. import corpus
from ..schemas import (
    Disposition,
    ExecutiveControversyCell,
    ExecutivePolicyCell,
    ExecutiveSuccess,
    ExecutiveSuccessCell,
    ExecutiveSuccessRow,
)
from .controversy import (
    CONTROVERSY_RULE_VERSION,
    controversy_links,
    docket_order,
    group_controversies,
)
from .exec_action import (
    EXEC_ACTION_COUNSEL_RULE,
    EXEC_ACTION_PARTY_RULE,
    EXEC_ACTION_RULE_VERSION,
    SCOPE_REASONS,
    ExecActionAnnotation,
    exec_action_rule,
)
from .ingest import first_proceeding_date, interim_reading
from .interim_signals import ApplicationKind, InterimReading
from .party import ADMINISTRATIONS, PARTY_AS_OF_FIELDS, administration_for, docket_stratum
from .party_rates import docket_key
from .policy_area import POLICY_AREAS, PolicySource, hand_source
from .prefetch import prefetch_by_case

Filer = Literal["government", "challenger", "all"]

Reading = Literal["finer", "registered"]

#: Who filed a controversy's applications.
ControversyFiler = Literal["government", "challenger", "both"]

_CONTROVERSY_FILERS: Final[tuple[ControversyFiler, ...]] = ("government", "challenger", "both")

#: The ways a stored ``denied`` can be read.
READINGS: Final[tuple[Reading, ...]] = ("finer", "registered")

#: The scope rule the cut defaults to.
DEFAULT_SCOPE_RULE: Final[str] = EXEC_ACTION_RULE_VERSION

#: Reading labels on the grant side: the executive's win where it applied. A
#: GVR and a summary reversal are the binary outcome's granted side; they reach
#: an application row only where the Court treated the application as a petition.
_GRANT_LABELS: Final[frozenset[str]] = frozenset(
    {
        InterimReading.granted.value,
        InterimReading.granted_in_part.value,
        Disposition.gvr.value,
        Disposition.summary_reversal.value,
    }
)

#: Reading labels outside the rate: the Court did not decide the ask.
_UNDECIDED_LABELS: Final[frozenset[str]] = frozenset(
    {
        InterimReading.withdrawn.value,
        InterimReading.dismissed.value,
        InterimReading.dismissed_moot.value,
    }
)

#: A row's latest live-shaped snapshot payload, or ``None`` where it has none.
Payload = Mapping[str, Any] | None

#: Fetches the payloads of the rows the cut counts or lists, one per row in order.
Fetcher = Callable[[Sequence[corpus.CorpusRow]], list[Payload]]


@dataclass
class _Acc:
    """Streaming counters for one cell."""

    rows: int = 0
    unknown_ask: int = 0
    pending: int = 0
    unreadable: int = 0
    withdrawn: int = 0
    dismissed: int = 0
    decided: int = 0
    wins: int = 0
    dispositions: Counter[str] = field(default_factory=Counter)
    excluded_unparsed: int = 0

    def add(self, label: str | None, applicant: bool) -> bool | None:
        """Count one population row; the executive's result where it was decided."""
        self.rows += 1
        if label is None:
            self.pending += 1
            return None
        self.dispositions[label] += 1
        if label == InterimReading.withdrawn.value:
            self.withdrawn += 1
            return None
        if label in _UNDECIDED_LABELS:
            self.dismissed += 1
            return None
        granted = label in _GRANT_LABELS
        if not granted and label != InterimReading.denied.value:
            self.unreadable += 1
            return None
        won = granted if applicant else not granted
        self.decided += 1
        self.wins += won
        return won

    def merge(self, other: _Acc) -> None:
        self.rows += other.rows
        self.unknown_ask += other.unknown_ask
        self.pending += other.pending
        self.unreadable += other.unreadable
        self.withdrawn += other.withdrawn
        self.dismissed += other.dismissed
        self.decided += other.decided
        self.wins += other.wins
        self.dispositions.update(other.dispositions)
        self.excluded_unparsed += other.excluded_unparsed

    def populated(self) -> bool:
        return bool(self.rows or self.excluded_unparsed)

    def cell(self, administration: str | None, filer: Filer) -> ExecutiveSuccessCell:
        return ExecutiveSuccessCell(
            administration=administration,
            filer=filer,
            rows=self.rows,
            unknown_ask=self.unknown_ask,
            pending=self.pending,
            unreadable=self.unreadable,
            withdrawn=self.withdrawn,
            dismissed=self.dismissed,
            decided=self.decided,
            wins=self.wins,
            success_rate=self.wins / self.decided if self.decided else None,
            dispositions=dict(sorted(self.dispositions.items())),
            excluded_unparsed=self.excluded_unparsed,
        )


def snapshot_fetcher(conn: corpus.ReadConnection) -> Fetcher:
    """Fetch each row's latest live-shaped snapshot payload, prefetched as one batch."""

    def fetch(rows: Sequence[corpus.CorpusRow]) -> list[Payload]:
        with prefetch_by_case(
            [row.case_id for row in rows],
            lambda case_id: corpus.latest_live_snapshot(conn, case_id),
            thread_name_prefix="executive-success",
        ) as fetched:
            return [found[1] if found else None for _, found in fetched]

    return fetch


def executive_success(
    conn: corpus.ReadConnection,
    *,
    as_of_field: str,
    through: date | None = None,
    since: date | None = None,
    corpus_sha256: str = "",
    scope_rule_version: str = DEFAULT_SCOPE_RULE,
    reading: Reading = "finer",
    policy: PolicySource | None = None,
) -> ExecutiveSuccess:
    """The executive success cut over the live slice (module docstring for every rule).

    ``policy`` is where the policy cells read their areas
    (:func:`~fedcourtsai.pipeline.policy_area.policy_source`); the hand set when
    omitted.

    Deterministic and read-only. Raises :class:`KeyError` for an unregistered
    scope rule and :class:`ValueError` for an unknown date convention or
    reading, before any row is read.
    """
    exec_action_rule(scope_rule_version)
    if as_of_field not in PARTY_AS_OF_FIELDS:
        raise ValueError(
            f"unknown as-of field {as_of_field!r}; known: {', '.join(PARTY_AS_OF_FIELDS)}"
        )
    if reading not in READINGS:
        raise ValueError(f"unknown reading {reading!r}; known: {', '.join(READINGS)}")
    return _success(
        corpus.iter_rows(conn, court="scotus", live_slice=True),
        as_of_field=as_of_field,
        through=through,
        since=since,
        corpus_sha256=corpus_sha256,
        scope_rule_version=scope_rule_version,
        fetch=snapshot_fetcher(conn),
        reading=reading,
        latest_pull=corpus.latest_pull_date(conn),
        latest_snapshot=corpus.latest_snapshot_date(conn),
        policy=policy,
    )


#: Where a row's filing date came from.
DateSource = Literal["docketed", "first-entry"]


@dataclass(frozen=True)
class _Placed:
    """One in-window application, its scope read and its stored label as of the cut."""

    row: corpus.CorpusRow
    annotation: ExecActionAnnotation
    as_of: date | None
    resolution: date | None
    disposition: Disposition | None
    filed: date | None = None
    date_source: DateSource | None = None

    @property
    def counted(self) -> bool:
        """A row the cut counts or lists: in scope or unknown, with a government side."""
        return self.annotation.in_scope is not False and self.annotation.government_side is not None


@dataclass
class _Fold:
    """The cut's running state: one cell accumulator per key, and the tallies beside them."""

    through: date | None
    rereading: bool
    accs: dict[tuple[str | None, Filer], _Acc] = field(default_factory=dict)
    reasons: Counter[str] = field(default_factory=Counter)
    unknown: Counter[str] = field(default_factory=Counter)
    rereads: Counter[str] = field(default_factory=Counter)
    review: list[ExecutiveSuccessRow] = field(default_factory=list)
    results: dict[str, bool | None] = field(default_factory=dict)

    def label(self, stored: Disposition | None, payload: Payload) -> str | None:
        """The label the cut reads a row under: a stored denial re-read, else as stored."""
        if stored is None:
            return None
        if stored != Disposition.denied or not self.rereading:
            return stored.value
        self.rereads["rows"] += 1
        reading, decided = interim_reading(payload) if payload is not None else (None, None)
        if reading is None:
            self.rereads["unobservable"] += 1
            return stored.value
        label = reading.value
        if self.through is not None and decided is not None and decided > self.through:
            self.rereads["after_through"] += 1
            return stored.value
        if label != InterimReading.denied.value:
            self.rereads["changed"] += 1
        return label

    def add(self, placed: _Placed, payload: Payload) -> None:
        """Count one in-window application where its scope puts it."""
        row, annotation, as_of = placed.row, placed.annotation, placed.as_of
        self.reasons[annotation.reason] += 1
        if annotation.in_scope is False or annotation.government_side is None:
            return
        administration = administration_for(as_of)
        applicant = annotation.government_side == "applicant"
        label = self.label(placed.disposition, payload)
        won: bool | None = None
        if annotation.in_scope is None:
            self.unknown[administration or "unattributed"] += 1
        else:
            acc = self.accs.setdefault(
                (administration, "government" if applicant else "challenger"), _Acc()
            )
            if row.application_kind is None:
                acc.excluded_unparsed += 1
            else:
                acc.unknown_ask += row.application_kind != ApplicationKind.substantive.value
                won = acc.add(label, applicant)
                self.results[row.docket_number] = won
        self.review.append(
            ExecutiveSuccessRow(
                docket_number=row.docket_number,
                administration=administration,
                date_filed=placed.filed,
                date_source=placed.date_source,
                in_scope=annotation.in_scope,
                reason=annotation.reason,
                government_side=annotation.government_side,
                application_kind=row.application_kind,
                stored_disposition=(
                    placed.disposition.value if placed.disposition is not None else None
                ),
                reading=label,
                executive_won=won,
            )
        )

    def cells(self) -> list[ExecutiveSuccessCell]:
        """The populated cells in reporting order, each administration's pool after its filers."""
        cells: list[ExecutiveSuccessCell] = []
        filers: tuple[Filer, ...] = ("government", "challenger")
        for window in [*(admin.label for admin in ADMINISTRATIONS), None]:
            pooled = _Acc()
            for filer in filers:
                acc = self.accs.get((window, filer))
                if acc is not None and acc.populated():
                    cells.append(acc.cell(window, filer))
                    pooled.merge(acc)
            if pooled.populated():
                cells.append(pooled.cell(window, "all"))
        return cells


def _windowed(
    row: corpus.CorpusRow, filed: date | None, since: date | None, through: date | None
) -> tuple[Literal["before", "after"] | None, date | None, Disposition | None]:
    """Place a row against the cut: outside it, or inside with its as-of-cut resolution."""
    resolution = corpus.resolution_date(row)
    disposition = Disposition(row.disposition) if row.disposition is not None else None
    anchor = filed or resolution
    if since is not None and (anchor is None or anchor < since):
        return "before", None, None
    if through is not None:
        if anchor is None or anchor > through:
            return "after", None, None
        # A disposition dated after the cut had not happened at the cut.
        if resolution is not None and resolution > through:
            return None, None, None
    return None, resolution, disposition


def _success(  # noqa: PLR0913 - one keyword per stamp the cut carries
    rows: Iterable[corpus.CorpusRow],
    *,
    as_of_field: str,
    through: date | None,
    since: date | None,
    corpus_sha256: str,
    scope_rule_version: str,
    fetch: Fetcher | None,
    reading: Reading,
    latest_pull: date | None,
    latest_snapshot: date | None,
    policy: PolicySource | None = None,
) -> ExecutiveSuccess:
    """Fold the rows into the cut — the pure half of :func:`executive_success`.

    The rows are collected first, so every snapshot read runs in a prefetched
    batch and never shares the row cursor: one batch for the rows with no
    docketed date, whose first proceeding dates them before they are placed,
    and one for the rest the cut counts or lists, after the caption half of
    the scope rule has said which those are. The scope rule then reads each
    counted row again with its snapshot. Without a ``fetch`` no snapshot is
    read: no row takes a first-entry date, no denial is re-read, the scope
    rule reads the caption alone, and controversies join on the caption alone.
    """
    annotator = exec_action_rule(scope_rule_version)
    outside: Counter[str] = Counter()
    candidates, duplicates, extensions = _candidates(rows)
    payloads: dict[str, Payload] = {}
    if fetch is not None:
        undated = [row for row in candidates if row.date_filed is None and _may_reach(row, since)]
        payloads = dict(zip((row.case_id for row in undated), fetch(undated), strict=True))
    placed: list[_Placed] = []
    for row in candidates:
        filed, source = _filing_date(row, payloads.get(row.case_id))
        where, resolution, disposition = _windowed(row, filed, since, through)
        if where is not None:
            outside[where] += 1
            continue
        as_of = filed if as_of_field == "filed" else resolution
        if as_of_field == "resolved" and disposition is None:
            as_of = None
        placed.append(
            _Placed(row, annotator(row, as_of, None), as_of, resolution, disposition, filed, source)
        )
    if fetch is not None:
        wanted = [item.row for item in placed if item.counted and item.row.case_id not in payloads]
        payloads.update(zip((row.case_id for row in wanted), fetch(wanted), strict=True))
        placed = [
            replace(
                item, annotation=annotator(item.row, item.as_of, payloads.get(item.row.case_id))
            )
            if item.counted
            else item
            for item in placed
        ]
    fold = _Fold(through=through, rereading=fetch is not None and reading == "finer")
    for item in placed:
        fold.add(item, payloads.get(item.row.case_id))
    policies = policy if policy is not None else hand_source()
    groups = _controversies(placed, payloads, fold.results)
    for review_row in fold.review:
        review_row.controversy_id = groups.ids.get(review_row.docket_number)
        label = policies.label(review_row.docket_number)
        if label is not None:
            review_row.policy_area = label.area
            review_row.policy_uncertain = label.uncertain
            review_row.policy_source = label.source
    policy_cells, unlabeled = _policy_cells(placed, fold.results, policies)
    order: dict[str, int] = {reason: index for index, reason in enumerate(SCOPE_REASONS)}
    return ExecutiveSuccess(
        scope_rule_version=scope_rule_version,
        party_rule_version=EXEC_ACTION_PARTY_RULE,
        counsel_rule_version=EXEC_ACTION_COUNSEL_RULE,
        reading="finer" if fold.rereading else "registered",
        as_of_field=as_of_field,
        through=through,
        since=since,
        corpus_sha256=corpus_sha256,
        latest_pull=latest_pull,
        latest_snapshot=latest_snapshot,
        applications=len(placed),
        filed_from_first_entry=sum(item.date_source == "first-entry" for item in placed),
        duplicate_rows=duplicates,
        extension_rows=extensions,
        filed_after_through=outside["after"],
        filed_before_since=outside["before"],
        reread_rows=fold.rereads["rows"],
        reread_changed=fold.rereads["changed"],
        reread_unobservable=fold.rereads["unobservable"],
        reread_after_through=fold.rereads["after_through"],
        scope_reasons={
            reason: fold.reasons[reason] for reason in sorted(fold.reasons, key=lambda r: order[r])
        },
        unknown_scope=dict(sorted(fold.unknown.items())),
        cells=fold.cells(),
        controversy_rule_version=CONTROVERSY_RULE_VERSION,
        controversy_cells=groups.cells,
        controversy_unlinked=groups.unlinked,
        policy_rule_version=policies.rule_version,
        policy_cells=policy_cells,
        policy_unlabeled=unlabeled,
        review_rows=sorted(fold.review, key=lambda r: r.docket_number),
    )


def _candidates(rows: Iterable[corpus.CorpusRow]) -> tuple[list[corpus.CorpusRow], int, int]:
    """The applications the cut places: one per docket number, extensions left out.

    Returns them with the counts of duplicate and extension rows dropped.
    """
    seen: set[str] = set()
    candidates: list[corpus.CorpusRow] = []
    duplicates = extensions = 0
    for row in rows:
        if docket_stratum(row) != "application":
            continue
        key = docket_key(row)
        if key is not None:
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
        if row.application_kind == ApplicationKind.extension.value:
            extensions += 1
            continue
        candidates.append(row)
    return candidates, duplicates, extensions


def _filing_date(row: corpus.CorpusRow, payload: Payload) -> tuple[date | None, DateSource | None]:
    """A row's filing date and its source: docketed, else its first proceeding's."""
    if row.date_filed is not None:
        return row.date_filed, "docketed"
    if payload is not None:
        first = first_proceeding_date(payload)
        if first is not None:
            return first, "first-entry"
    return None, None


def _may_reach(row: corpus.CorpusRow, since: date | None) -> bool:
    """Whether an undated row can fall on or after ``since``: its first entry precedes its end."""
    resolution = corpus.resolution_date(row)
    return since is None or resolution is None or resolution >= since


def _policy_cells(
    placed: Sequence[_Placed], results: Mapping[str, bool | None], source: PolicySource
) -> tuple[list[ExecutivePolicyCell], int]:
    """Count the in-scope population per administration, filer and policy area."""
    tallies: dict[tuple[str | None, Filer, str], Counter[str]] = {}
    unlabeled = 0
    for item in placed:
        docket = item.row.docket_number
        if item.annotation.in_scope is not True or docket not in results:
            continue
        label = source.label(docket)
        if label is None:
            unlabeled += 1
            continue
        filer: Filer = (
            "government" if item.annotation.government_side == "applicant" else "challenger"
        )
        tally = tallies.setdefault((administration_for(item.as_of), filer, label.area), Counter())
        tally["rows"] += 1
        tally["labeler"] += label.source == "labeler"
        won = results[docket]
        if won is not None:
            tally["decided"] += 1
            tally["wins"] += won
    order: dict[str, int] = {area: index for index, area in enumerate(POLICY_AREAS)}
    windows: dict[str | None, int] = {
        window: index
        for index, window in enumerate([*(admin.label for admin in ADMINISTRATIONS), None])
    }
    cells = [
        ExecutivePolicyCell(
            administration=window,
            filer=filer,
            area=area,
            rows=tally["rows"],
            decided=tally["decided"],
            wins=tally["wins"],
            labeler_rows=tally["labeler"],
            success_rate=tally["wins"] / tally["decided"] if tally["decided"] else None,
        )
        for (window, filer, area), tally in sorted(
            tallies.items(),
            key=lambda kv: (windows[kv[0][0]], kv[0][1] != "government", order[kv[0][2]]),
        )
    ]
    return cells, unlabeled


@dataclass(frozen=True)
class _Groups:
    ids: dict[str, str]
    cells: list[ExecutiveControversyCell]
    unlinked: int


def _controversies(
    placed: Sequence[_Placed], payloads: Mapping[str, Payload], results: Mapping[str, bool | None]
) -> _Groups:
    """Group the in-scope population into controversies and count them per cell."""
    members = {
        item.row.docket_number: item
        for item in placed
        if item.annotation.in_scope is True and item.row.docket_number in results
    }
    ids = group_controversies(
        controversy_links(
            item.row,
            payloads.get(item.row.case_id),
            government_applicant=item.annotation.government_side == "applicant",
            decided=item.disposition is not None,
            filed=item.filed,
            resolved=item.resolution,
        )
        for item in members.values()
    )
    grouped: dict[str, list[_Placed]] = {}
    for docket, group_id in ids.items():
        grouped.setdefault(group_id, []).append(members[docket])
    tallies: dict[tuple[str | None, ControversyFiler], Counter[str]] = {}
    for group in grouped.values():
        first = min(
            group,
            key=lambda item: (
                item.as_of is None,
                item.filed or date.max,
                docket_order(item.row.docket_number),
            ),
        )
        sides = {item.annotation.government_side for item in group}
        filer: ControversyFiler = (
            "both" if len(sides) > 1 else "government" if "applicant" in sides else "challenger"
        )
        decided = [item for item in group if results[item.row.docket_number] is not None]
        tally = tallies.setdefault((administration_for(first.as_of), filer), Counter())
        tally["controversies"] += 1
        tally["applications"] += len(group)
        if not decided:
            tally["indeterminate"] += 1
            continue
        last = max(
            decided,
            key=lambda item: (item.resolution or date.min, docket_order(item.row.docket_number)),
        )
        tally["determinate"] += 1
        tally["wins"] += bool(results[last.row.docket_number])
    cells: list[ExecutiveControversyCell] = []
    for window in [*(admin.label for admin in ADMINISTRATIONS), None]:
        pooled: Counter[str] = Counter()
        for side in _CONTROVERSY_FILERS:
            found = tallies.get((window, side))
            if found:
                cells.append(_controversy_cell(window, side, found))
                pooled.update(found)
        if pooled:
            cells.append(_controversy_cell(window, "all", pooled))
    unlinked = sum(payloads.get(item.row.case_id) is None for item in members.values())
    return _Groups(ids=ids, cells=cells, unlinked=unlinked)


def _controversy_cell(
    administration: str | None, filer: ControversyFiler | Literal["all"], tally: Counter[str]
) -> ExecutiveControversyCell:
    determinate = tally["determinate"]
    return ExecutiveControversyCell(
        administration=administration,
        filer=filer,
        controversies=tally["controversies"],
        applications=tally["applications"],
        indeterminate=tally["indeterminate"],
        determinate=determinate,
        wins=tally["wins"],
        success_rate=tally["wins"] / determinate if determinate else None,
    )
