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

from datetime import date
from typing import Any

from . import casestore
from .corpus import CaseDocument, CorpusEvent


class ProvisionError(RuntimeError):
    """A provisioning-source configuration problem, surfaced with context."""


class CasestoreSource:
    """Read a case's snapshot / documents / events from the per-case content store.

    Mirrors the corpus read functions the provisioning commands use, so a
    casestore-sourced ``record/`` is byte-identical to a corpus-sourced one. Thin
    over the shared ``casestore.read_*`` helpers (the same implementation the
    process read source uses under the corpus-split mode), bound to an explicit
    transport so a test can point it at an in-memory store.
    """

    def __init__(self, transport: casestore.ObjectTransport) -> None:
        self._transport = transport

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        """The newest dated snapshot — ``(date, payload)`` — or ``None``."""
        return casestore.read_latest_snapshot(self._transport, case_id)

    def documents_for_case(self, case_id: str) -> list[CaseDocument]:
        """The case's documents, kind-ordered, reconstructed from the manifest + leaves."""
        return casestore.read_documents(self._transport, case_id)

    def events_for_case(self, case_id: str) -> list[CorpusEvent]:
        """The case's predictable events, event_id-ordered (empty if none stored)."""
        return casestore.read_events(self._transport, case_id)


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
