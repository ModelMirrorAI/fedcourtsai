"""Restore a day's live snapshot where a same-day refresh stored over it.

A case has one snapshot key per day (``snapshots/<date>.json``), shared by the
live channel and the CourtListener refresh. ``pull_case`` leaves a stored live
snapshot of the day in place, so a key whose current object is a refresh's
read while an earlier version is the Court's docket is a day on which that
did not hold. The bucket keeps versioning on, so the earlier body is still
held as a noncurrent version until the lifecycle rule expires it.

This pass reads the version listing of every row both channels have read
(``last_live_polled`` and ``last_pulled`` both set), and for each dated key
whose current version is not live-shaped but which holds an earlier
live-shaped version, writes that earlier body back as the key's current
version. The CourtListener body it displaces becomes a noncurrent version in
turn. Nothing in the index moves: the row was already written from the live
poll, and the pass changes only which body the day's key serves.

Idempotent: a restored key's current version is live-shaped, so a second pass
plans nothing for it.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from .. import casestore
from ..corpus import ReadConnection

#: The key a supremecourt.gov docket payload carries and a CourtListener docket does not.
LIVE_MARKER = "ProceedingsandOrder"


#: Concurrent case reads, under the S3 client's default connection pool of ten.
#: Each is a listing and a few small gets.
READ_WORKERS = 8


class RestoreUnavailable(RuntimeError):
    """The store cannot serve version reads, so the pass can say nothing."""


class Restore(BaseModel):
    """One planned restore: a case-day and the version that holds its live body."""

    case_id: str
    snapshot_date: date
    #: Opaque to a reader of the ledger, so kept out of the serialized result.
    version_id: str = Field(exclude=True)


class LiveSnapshotRestoreResult(BaseModel):
    """What one pass restored (or would restore on a dry run).

    A model so the command serializes it whole: the workflow tees it into the
    run summary as the ledger a maintainer reads before the apply.
    """

    #: Rows both channels have read, whose version listings the pass read.
    cases_read: int = 0
    #: Dated keys holding more than one version.
    rewritten_keys: int = 0
    #: Of those, keys whose current version is already live-shaped.
    live_current: int = 0
    #: Keys written more than once with no live-shaped version among them.
    no_live_version: int = 0
    #: Keys whose current version could not be read or parsed.
    unreadable: int = 0
    restores: list[Restore] = []
    total_restores: int = 0
    #: Cases among the restores that hold no live-shaped current snapshot on any day.
    cases_without_live_snapshot: int = 0
    refused: bool = False
    applied: bool = False


@dataclass
class _KeyVersions:
    current: casestore.ObjectVersion | None = None
    earlier: list[casestore.ObjectVersion] = field(default_factory=list)


def _is_live(body: bytes | None) -> bool | None:
    """Whether a snapshot body is live-shaped; ``None`` when it cannot be read."""
    if body is None:
        return None
    try:
        payload = json.loads(body)
    except ValueError:
        return None
    return isinstance(payload, dict) and LIVE_MARKER in payload


def _versions_by_key(
    transport: casestore.VersionedTransport, prefix: str
) -> dict[str, _KeyVersions]:
    """Each key under ``prefix`` with its current version and its earlier ones."""
    by_key: dict[str, _KeyVersions] = {}
    for version in transport.list_versions(prefix):
        held = by_key.setdefault(version.key, _KeyVersions())
        if version.is_latest:
            held.current = version
        else:
            held.earlier.append(version)
    return by_key


def _live_earlier_version(
    transport: casestore.VersionedTransport, key: str, held: _KeyVersions
) -> tuple[str, bytes] | Literal["unreadable", "live_current"] | None:
    """The newest live-shaped earlier version of a key whose current one is not.

    ``"live_current"`` when the key already serves the live shape,
    ``"unreadable"`` when its current version cannot be read, ``None`` when no
    earlier version is live-shaped.
    """
    assert held.current is not None
    current_live = _is_live(transport.get_version(key, held.current.version_id))
    if current_live is None:
        return "unreadable"
    if current_live:
        return "live_current"
    for version in sorted(held.earlier, key=lambda v: v.last_modified, reverse=True):
        body = transport.get_version(key, version.version_id)
        if body is not None and _is_live(body):
            return version.version_id, body
    return None


def _snapshot_date(key: str, prefix: str) -> date | None:
    stem = key[len(prefix) :]
    if not stem.endswith(".json"):
        return None
    try:
        return date.fromisoformat(stem[: -len(".json")])
    except ValueError:
        return None


@dataclass
class _CaseRead:
    rewritten_keys: int = 0
    live_current: int = 0
    no_live_version: int = 0
    unreadable: int = 0
    found: list[tuple[date, str, bytes]] = field(default_factory=list)


def _read_case(transport: casestore.VersionedTransport, case_id: str) -> _CaseRead:
    """Read one case's snapshot versions and what, if anything, to restore."""
    read = _CaseRead()
    prefix = f"{casestore.case_prefix(case_id)}/snapshots/"
    by_key = _versions_by_key(transport, prefix)
    for key in sorted(by_key):
        held = by_key[key]
        day = _snapshot_date(key, prefix)
        # A key written once had nothing replaced.
        if day is None or held.current is None or not held.earlier:
            continue
        read.rewritten_keys += 1
        found = _live_earlier_version(transport, key, held)
        if found == "unreadable":
            read.unreadable += 1
        elif found == "live_current":
            read.live_current += 1
        elif found is None:
            read.no_live_version += 1
        else:
            read.found.append((day, *found))
    return read


def candidate_case_ids(conn: ReadConnection) -> list[str]:
    """Every row both channels have read: the only rows whose key two writers shared."""
    cursor = conn.execute(
        "SELECT case_id FROM cases WHERE last_live_polled IS NOT NULL "
        "AND last_pulled IS NOT NULL ORDER BY case_id"
    )
    return [row[0] for row in cursor]


def restore_replaced_live_snapshots(
    conn: ReadConnection,
    transport: casestore.ObjectTransport,
    *,
    apply: bool,
    max_restores: int | None = None,
) -> LiveSnapshotRestoreResult:
    """Plan, and on ``apply`` perform, the restore over every candidate row.

    The plan is the write set: an apply writes exactly what its own read found,
    and refuses whole when that is more than ``max_restores``.
    """
    if not isinstance(transport, casestore.VersionedTransport):
        raise RestoreUnavailable("the content store transport serves no version reads")
    try:
        return _restore(conn, transport, apply=apply, max_restores=max_restores)
    except casestore.CasestoreError as exc:
        raise RestoreUnavailable(str(exc)) from None


def _restore(
    conn: ReadConnection,
    transport: casestore.VersionedTransport,
    *,
    apply: bool,
    max_restores: int | None,
) -> LiveSnapshotRestoreResult:
    result = LiveSnapshotRestoreResult()
    bodies: dict[tuple[str, date], bytes] = {}
    live_days: dict[str, int] = {}
    case_ids = candidate_case_ids(conn)
    # One listing per case and a read per version of each rewritten key: the
    # reads are independent, and a key the live channel wrote several times in
    # a day is common, so they are pooled. Results are folded in case order.
    with ThreadPoolExecutor(max_workers=READ_WORKERS) as pool:
        for case_id, read in zip(
            case_ids, pool.map(lambda c: _read_case(transport, c), case_ids), strict=True
        ):
            result.cases_read += 1
            result.rewritten_keys += read.rewritten_keys
            result.unreadable += read.unreadable
            result.live_current += read.live_current
            result.no_live_version += read.no_live_version
            live_days[case_id] = read.live_current
            for day, version_id, body in read.found:
                bodies[(case_id, day)] = body
                result.restores.append(
                    Restore(case_id=case_id, snapshot_date=day, version_id=version_id)
                )
    result.total_restores = len(result.restores)
    restored_cases = sorted({restore.case_id for restore in result.restores})
    with ThreadPoolExecutor(max_workers=READ_WORKERS) as pool:
        holds = pool.map(lambda c: _holds_live_day(transport, c, live_days), restored_cases)
        result.cases_without_live_snapshot = sum(1 for held in holds if not held)
    if not apply:
        return result
    if max_restores is None or result.total_restores > max_restores:
        result.refused = True
        return result
    for restore in result.restores:
        transport.put(
            casestore.snapshot_key(restore.case_id, restore.snapshot_date),
            bodies[(restore.case_id, restore.snapshot_date)],
        )
    result.applied = True
    return result


def _holds_live_day(
    transport: casestore.ObjectTransport, case_id: str, live_days: dict[str, int]
) -> bool:
    """Whether the case serves a live-shaped snapshot on any day as the store stands."""
    if live_days.get(case_id):
        return True
    try:
        return casestore.read_latest_live_snapshot(transport, case_id) is not None
    except ValueError:
        # A stored body that does not parse is not a live snapshot to serve.
        return False
