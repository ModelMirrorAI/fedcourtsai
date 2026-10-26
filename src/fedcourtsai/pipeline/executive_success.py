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

**One docket, one row; the date convention, moment and bound are the
caller's**, exactly as on the party rates cut: rows de-duplicate by docket
number, ``as_of_field`` is required, ``through`` places the cut at a past
moment, and ``since`` bounds the start where coverage begins mid-window.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Final, Literal

from .. import corpus
from ..schemas import (
    Disposition,
    ExecutiveSuccess,
    ExecutiveSuccessCell,
    ExecutiveSuccessRow,
)
from .exec_action import (
    EXEC_ACTION_COUNSEL_RULE,
    EXEC_ACTION_PARTY_RULE,
    EXEC_ACTION_RULE_VERSION,
    SCOPE_REASONS,
    ExecActionAnnotation,
    exec_action_rule,
)
from .ingest import interim_reading
from .interim_signals import ApplicationKind, InterimReading
from .party import ADMINISTRATIONS, PARTY_AS_OF_FIELDS, administration_for, docket_stratum
from .party_rates import docket_key
from .prefetch import prefetch_by_case

Filer = Literal["government", "challenger", "all"]

Reading = Literal["finer", "registered"]

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

#: One re-read: the finer label and its entry's date, or ``None`` where unobservable.
Reread = tuple[str, date | None] | None

#: Re-reads rows stored ``denied``, one result per row in order.
Rereader = Callable[[Sequence[corpus.CorpusRow]], list[Reread]]


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


def snapshot_rereader(conn: corpus.ReadConnection) -> Rereader:
    """Re-read rows from their latest live-shaped snapshots under the finer interim reading."""

    def reread(rows: Sequence[corpus.CorpusRow]) -> list[Reread]:
        results: list[Reread] = []
        with prefetch_by_case(
            [row.case_id for row in rows],
            lambda case_id: corpus.latest_live_snapshot(conn, case_id),
            thread_name_prefix="executive-success",
        ) as fetched:
            for _, found in fetched:
                reading, decided = interim_reading(found[1]) if found else (None, None)
                results.append((reading.value, decided) if reading is not None else None)
        return results

    return reread


def executive_success(
    conn: corpus.ReadConnection,
    *,
    as_of_field: str,
    through: date | None = None,
    since: date | None = None,
    corpus_sha256: str = "",
    scope_rule_version: str = DEFAULT_SCOPE_RULE,
    reading: Reading = "finer",
) -> ExecutiveSuccess:
    """The executive success cut over the live slice (module docstring for every rule).

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
        reread=snapshot_rereader(conn) if reading == "finer" else None,
        latest_pull=corpus.latest_pull_date(conn),
        latest_snapshot=corpus.latest_snapshot_date(conn),
    )


@dataclass(frozen=True)
class _Placed:
    """One in-window application, its scope read and its stored label as of the cut."""

    row: corpus.CorpusRow
    annotation: ExecActionAnnotation
    as_of: date | None
    disposition: Disposition | None

    @property
    def needs_reread(self) -> bool:
        """A stored denial on a row the cut counts or lists."""
        return (
            self.disposition == Disposition.denied
            and self.annotation.in_scope is not False
            and self.annotation.government_side is not None
        )


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

    def label(self, stored: Disposition | None, finer: Reread, needed: bool) -> str | None:
        """The label the cut reads a row under: a stored denial re-read, else as stored."""
        if stored is None:
            return None
        if not needed:
            return stored.value
        self.rereads["rows"] += 1
        if finer is None:
            self.rereads["unobservable"] += 1
            return stored.value
        label, decided = finer
        if self.through is not None and decided is not None and decided > self.through:
            self.rereads["after_through"] += 1
            return stored.value
        if label != InterimReading.denied.value:
            self.rereads["changed"] += 1
        return label

    def add(self, placed: _Placed, finer: Reread) -> None:
        """Count one in-window application where its scope puts it."""
        row, annotation, as_of = placed.row, placed.annotation, placed.as_of
        self.reasons[annotation.reason] += 1
        if annotation.in_scope is False or annotation.government_side is None:
            return
        administration = administration_for(as_of)
        applicant = annotation.government_side == "applicant"
        label = self.label(placed.disposition, finer, placed.needs_reread and self.rereading)
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
        self.review.append(
            ExecutiveSuccessRow(
                docket_number=row.docket_number,
                administration=administration,
                date_filed=row.date_filed,
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
    row: corpus.CorpusRow, since: date | None, through: date | None
) -> tuple[Literal["before", "after"] | None, date | None, Disposition | None]:
    """Place a row against the cut: outside it, or inside with its as-of-cut resolution."""
    resolution = corpus.resolution_date(row)
    disposition = Disposition(row.disposition) if row.disposition is not None else None
    anchor = row.date_filed or resolution
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
    reread: Rereader | None,
    latest_pull: date | None,
    latest_snapshot: date | None,
) -> ExecutiveSuccess:
    """Fold the rows into the cut — the pure half of :func:`executive_success`.

    Two passes: the rows are placed and scope-read first, so the snapshot
    re-reads run as one prefetched batch and never share the row cursor.
    """
    annotator = exec_action_rule(scope_rule_version)
    seen: set[str] = set()
    outside: Counter[str] = Counter()
    placed: list[_Placed] = []
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
        where, resolution, disposition = _windowed(row, since, through)
        if where is not None:
            outside[where] += 1
            continue
        as_of = row.date_filed if as_of_field == "filed" else resolution
        if as_of_field == "resolved" and disposition is None:
            as_of = None
        placed.append(_Placed(row, annotator(row, as_of), as_of, disposition))
    finer: dict[str, Reread] = {}
    if reread is not None:
        wanted = [item.row for item in placed if item.needs_reread]
        finer = dict(zip((row.case_id for row in wanted), reread(wanted), strict=True))
    fold = _Fold(through=through, rereading=reread is not None)
    for item in placed:
        fold.add(item, finer.get(item.row.case_id))
    order: dict[str, int] = {reason: index for index, reason in enumerate(SCOPE_REASONS)}
    return ExecutiveSuccess(
        scope_rule_version=scope_rule_version,
        party_rule_version=EXEC_ACTION_PARTY_RULE,
        counsel_rule_version=EXEC_ACTION_COUNSEL_RULE,
        reading="finer" if reread is not None else "registered",
        as_of_field=as_of_field,
        through=through,
        since=since,
        corpus_sha256=corpus_sha256,
        latest_pull=latest_pull,
        latest_snapshot=latest_snapshot,
        applications=len(placed),
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
        review_rows=sorted(fold.review, key=lambda r: r.docket_number),
    )
