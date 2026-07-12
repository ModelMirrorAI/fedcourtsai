"""Casestore-backed provisioning reads (corpus split, phase 3).

The predict/evaluate cells materialize a read-only ``record/`` — the point-in-time
snapshot, the case's documents, and the predictable event — from the corpus. This
module lets those reads come from the per-case content store
(:mod:`fedcourtsai.casestore`) instead of the SQLite corpus, behind
``--corpus-backend casestore``.

:class:`CasestoreSource` returns the *same shapes* as the corpus read functions
(``latest_snapshot`` / ``documents_for_case`` / ``events_for_case``), so the
provisioning commands reproduce **byte-identical** ``record/`` output whichever
backend they read from — proven by ``tests/test_provision_casestore.py``. It is
opt-in: nothing selects it by default, and it is only usable once dual-write has
populated the store.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from . import casestore
from .corpus import CaseDocument, CorpusEvent


class ProvisionError(RuntimeError):
    """A provisioning-source configuration problem, surfaced with context."""


class CasestoreSource:
    """Read a case's snapshot / documents / events from the per-case content store.

    Mirrors the corpus read functions the provisioning commands use, so a
    casestore-sourced ``record/`` is byte-identical to a corpus-sourced one.
    """

    def __init__(self, transport: casestore.ObjectTransport) -> None:
        self._transport = transport

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        """The newest dated snapshot — ``(date, payload)`` — or ``None``.

        Lists the case's ``snapshots/`` and picks the max date, mirroring the
        corpus ``ORDER BY snapshot_date DESC LIMIT 1``.
        """
        prefix = f"{casestore.case_prefix(case_id)}/snapshots/"
        dates: list[date] = []
        for key in self._transport.list_keys(prefix):
            stem = key[len(prefix) :]
            if stem.endswith(".json"):
                try:
                    dates.append(date.fromisoformat(stem[: -len(".json")]))
                except ValueError:
                    continue
        if not dates:
            return None
        latest = max(dates)
        body = self._transport.get(casestore.snapshot_key(case_id, latest))
        if body is None:
            return None
        return latest, json.loads(body)

    def documents_for_case(self, case_id: str) -> list[CaseDocument]:
        """The case's documents, kind-ordered — reconstructed from the manifest
        and the content-addressed text leaves (empty if none stored)."""
        body = self._transport.get(casestore.documents_manifest_key(case_id))
        if body is None:
            return []
        documents: list[CaseDocument] = []
        for entry in json.loads(body).get("documents", []):  # manifest is kind-sorted
            leaf = self._transport.get(entry["text_key"])
            documents.append(
                CaseDocument(
                    case_id=case_id,
                    kind=entry["kind"],
                    url=entry["url"],
                    entry_date=entry["entry_date"],
                    fetched_at=date.fromisoformat(entry["fetched_at"]),
                    pages=entry["pages"],
                    truncated=entry["truncated"],
                    text=leaf.decode("utf-8") if leaf is not None else "",
                )
            )
        return documents

    def events_for_case(self, case_id: str) -> list[CorpusEvent]:
        """The case's predictable events, event_id-ordered (empty if none stored)."""
        body = self._transport.get(casestore.events_key(case_id))
        if body is None:
            return []
        return [CorpusEvent.model_validate(entry) for entry in json.loads(body)]


def casestore_source_from_settings() -> CasestoreSource:
    """Build a :class:`CasestoreSource` from ``FEDCOURTS_CASESTORE_URL``.

    Raises :class:`ProvisionError` when the store is not configured — the casestore
    backend cannot serve reads without it.
    """
    transport = casestore.transport_from_settings()
    if transport is None:
        raise ProvisionError(
            "the casestore backend needs FEDCOURTS_CASESTORE_URL (s3://<bucket>[/<prefix>])"
        )
    return CasestoreSource(transport)
