"""Grant rates by government-party status and administration — the party rates cut.

A standalone analytics artifact over the party annotations (:mod:`.party`): cert
grant rates and emergency-docket (application) grant rates, keyed on which side
of the caption the federal government occupies and which administration held
office on the cut's date. Nothing a predict or evaluate cell reads is derived
from it — not the statpack, the docket pack, salience, or a base rate — so a
change here moves no frozen input.

**What a cell is.** One administration x docket stratum x federal side. The
strata are the census's (:data:`.party.PARTY_STRATA`) less ``other``: paid
cert, IFP cert and applications, each read against its own denominator, because
the windows hold very different mixes of the three and the rates differ by an
order of magnitude between them. The federal side runs ``petitioner`` /
``respondent`` / ``both`` / ``none``, the last being the comparison cell — the
same stratum and window with no federal party the caption names.

**What a rate is.** Granted over resolved, where *resolved* is a
machine-readable disposition (:func:`.outcome.is_machine_readable`) and
*granted* is the binary outcome's granted side
(:data:`fedcourtsai.schemas.GRANTED_DISPOSITIONS`: plenary grants, partial
grants, GVRs, summary reversals) — the projection cert and interim scoring
already use, so a rate here means what a scored outcome means. A pending row
and an ``other`` row are counted beside the rate and never inside it. Every
cell also carries its raw per-label counts, so a reader who wants plenary
grants only, or withdrawals dropped from the denominator, recomputes from the
cell rather than trusting one convention.

**Reweighting.** The live slice stores a legacy block of IFP denials one row in
ten (``sample_weight`` 10). The census excludes that block because it counts
rows; a rate cannot, because dropping nine-tenths of a stratum's denials
inflates its grant rate roughly tenfold. So every cell carries two pairs —
raw rows, and rows counted ``sample_weight`` times — and ``grant_rate`` is the
weighted pair's quotient. Where a cell holds no sampled row the pairs are equal.

**The application population is the substantive asks.** An extension of time
is granted as a matter of course and would swamp an emergency-docket rate, so
the application cells count ``application_kind == substantive`` only, the same
slice the statpack's interim rate reads; extension, unreadable-ask and
never-parsed applications are counted beside each cell as exclusions.

**One docket, one row.** The corpus can hold a docket under two case ids (a
CourtListener id and a live-channel id for the same docket number); the second
row for a docket number already counted is dropped and tallied, so a docket
never votes twice in a rate. Rows stream in ``case_id`` order, so the kept row
is the one with the smaller id — deterministic, and immaterial on the blobs
measured, where the pairs agree on caption, dates and disposition.

**The date convention and the moment are the caller's.** ``as_of_field`` is
required exactly as the census requires it (``filed`` / ``resolved``, see
:data:`.party.PARTY_AS_OF_FIELDS`). ``through`` places the cut at a past
moment: rows later than it are left out, and a disposition dated after it reads
as pending — which is what lets a published tally be replicated as of its own
date rather than against outcomes that postdate it. Without ``through`` the
cut is the whole blob, and the newest window's rates are right-censored by its
pending rows: under ``filed`` they sit in their window outside the rate, and
since the petitions still pending are disproportionately the relisted and
CVSG'd ones, that window's rate over what has resolved is not yet its rate.
Under ``resolved`` a pending row has no date and lands in the unattributed
cells.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from typing import Final

from .. import corpus
from ..schemas import GRANTED_DISPOSITIONS, Disposition, PartyRateCell, PartyRates
from .interim_signals import ApplicationKind
from .outcome import granted_flag, is_machine_readable
from .party import (
    ADMINISTRATIONS,
    PARTY_AS_OF_FIELDS,
    PARTY_CAPTION_RULE_VERSION,
    PARTY_RULE_VERSION_V2,
    PARTY_SIDES,
    DocketStratum,
    PartySide,
    administration_for,
    docket_stratum,
    party_rule,
)

#: The strata a rate is published for, in reporting order. ``other`` (original,
#: miscellaneous, unparseable docket numbers) is left out and counted: it is a
#: residue of unlike dockets, not a population with a grant rate.
RATE_STRATA: Final[tuple[DocketStratum, ...]] = ("paid-cert", "ifp-cert", "application")

#: The annotation rule the rates cut defaults to. ``party-v2`` rather than the
#: census's ``party-v1`` because the application cells are a federal-*applicant*
#: series, and ``party-v1`` reads the officer-then-department caption the
#: Department of Homeland Security's applications carry as private.
DEFAULT_RATES_RULE: Final[str] = PARTY_RULE_VERSION_V2


@dataclass
class _Acc:
    """Streaming counters for one cell."""

    rows: int = 0
    sampled_rows: int = 0
    pending: int = 0
    unreadable: int = 0
    resolved: int = 0
    granted: int = 0
    weighted_resolved: int = 0
    weighted_granted: int = 0
    dispositions: Counter[str] = field(default_factory=Counter)
    excluded_extension: int = 0
    excluded_unknown_ask: int = 0
    excluded_unparsed: int = 0

    def cell(
        self, administration: str | None, stratum: DocketStratum, side: PartySide
    ) -> PartyRateCell:
        if stratum == "other":  # never keyed; RATE_STRATA leaves it out
            raise ValueError("the other stratum carries no rate cell")
        return PartyRateCell(
            administration=administration,
            stratum=stratum,
            federal_party=side,
            rows=self.rows,
            sampled_rows=self.sampled_rows,
            pending=self.pending,
            unreadable=self.unreadable,
            resolved=self.resolved,
            granted=self.granted,
            weighted_resolved=self.weighted_resolved,
            weighted_granted=self.weighted_granted,
            grant_rate=(
                self.weighted_granted / self.weighted_resolved if self.weighted_resolved else None
            ),
            dispositions=dict(sorted(self.dispositions.items())),
            excluded_extension=self.excluded_extension,
            excluded_unknown_ask=self.excluded_unknown_ask,
            excluded_unparsed=self.excluded_unparsed,
        )

    def exclude_application(self, kind: str | None) -> None:
        """Tally an application outside the substantive population, by why."""
        if kind is None:
            self.excluded_unparsed += 1
        elif kind == ApplicationKind.extension.value:
            self.excluded_extension += 1
        else:
            self.excluded_unknown_ask += 1

    def add(self, disposition: str | None, weight: int) -> bool:
        """Count one population row; ``True`` where it entered the rate as resolved."""
        self.rows += 1
        if weight > 1:
            self.sampled_rows += 1
        if disposition is None:
            self.pending += 1
            return False
        label = Disposition(disposition)
        if not is_machine_readable(label):
            self.unreadable += 1
            return False
        flag = granted_flag(label)
        self.resolved += 1
        self.granted += flag
        self.weighted_resolved += weight
        self.weighted_granted += weight * flag
        self.dispositions[label.value] += 1
        return True

    def populated(self) -> bool:
        return bool(
            self.rows
            or self.excluded_extension
            or self.excluded_unknown_ask
            or self.excluded_unparsed
        )


def _docket_key(row: corpus.CorpusRow) -> str | None:
    """The docket number a duplicate is recognized by, or ``None`` where there is none."""
    key = row.docket_number.strip().upper()
    return key or None


def party_rates(
    conn: corpus.ReadConnection,
    *,
    as_of_field: str,
    through: date | None = None,
    corpus_sha256: str = "",
    rule_version: str = DEFAULT_RATES_RULE,
) -> PartyRates:
    """The party rates cut over the live slice (module docstring for every rule).

    Deterministic and read-only: two runs over one corpus pointer with the same
    arguments agree byte for byte. Raises :class:`KeyError` for an unregistered
    rule and :class:`ValueError` for an unknown date convention, before any row
    is read.
    """
    party_rule(rule_version)  # an unregistered label fails before any row is read
    if as_of_field not in PARTY_AS_OF_FIELDS:
        raise ValueError(
            f"unknown as-of field {as_of_field!r}; known: {', '.join(PARTY_AS_OF_FIELDS)}"
        )
    return _rates(
        corpus.iter_rows(conn, court="scotus", live_slice=True),
        as_of_field=as_of_field,
        through=through,
        corpus_sha256=corpus_sha256,
        rule_version=rule_version,
        latest_pull=corpus.latest_pull_date(conn),
        latest_snapshot=corpus.latest_snapshot_date(conn),
    )


def _rates(
    rows: Iterable[corpus.CorpusRow],
    *,
    as_of_field: str,
    through: date | None,
    corpus_sha256: str,
    rule_version: str,
    latest_pull: date | None,
    latest_snapshot: date | None,
) -> PartyRates:
    """Fold the rows into the cut — the pure half of :func:`party_rates`."""
    annotator = party_rule(rule_version)
    accs: dict[tuple[str | None, DocketStratum, PartySide], _Acc] = {}
    seen: set[str] = set()
    counted = duplicates = other_stratum = after_through = undated = resolution_undated = 0
    for row in rows:
        key = _docket_key(row)
        if key is not None:
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
        stratum = docket_stratum(row)
        if stratum == "other":
            other_stratum += 1
            continue
        resolution = corpus.resolution_date(row)
        disposition = row.disposition
        if through is not None:
            anchor = row.date_filed or resolution
            if anchor is None or anchor > through:
                after_through += 1
                continue
            # A disposition dated after the cut had not happened at the cut.
            if resolution is not None and resolution > through:
                resolution = None
                disposition = None
        as_of = row.date_filed if as_of_field == "filed" else resolution
        if as_of_field == "resolved" and disposition is None:
            as_of = None
        annotation = annotator(row, as_of)
        administration = administration_for(as_of)
        acc = accs.setdefault((administration, stratum, annotation.federal_party), _Acc())
        if stratum == "application" and row.application_kind != ApplicationKind.substantive.value:
            acc.exclude_application(row.application_kind)
            continue
        counted += 1
        undated += as_of is None
        weight = max(1, row.sample_weight if row.sample_weight is not None else 1)
        if acc.add(disposition, weight) and resolution is None:
            resolution_undated += 1
    windows: list[str | None] = [*(admin.label for admin in ADMINISTRATIONS), None]
    cells = [
        accs[(window, stratum, side)].cell(window, stratum, side)
        for window in windows
        for stratum in RATE_STRATA
        for side in PARTY_SIDES
        if (window, stratum, side) in accs and accs[(window, stratum, side)].populated()
    ]
    return PartyRates(
        rule_version=rule_version,
        caption_rule_version=PARTY_CAPTION_RULE_VERSION,
        as_of_field=as_of_field,
        through=through,
        granted_labels=sorted(label.value for label in GRANTED_DISPOSITIONS),
        corpus_sha256=corpus_sha256,
        latest_pull=latest_pull,
        latest_snapshot=latest_snapshot,
        rows=counted,
        duplicate_rows=duplicates,
        other_stratum=other_stratum,
        filed_after_through=after_through,
        undated=undated,
        resolution_undated=resolution_undated,
        cells=cells,
    )
