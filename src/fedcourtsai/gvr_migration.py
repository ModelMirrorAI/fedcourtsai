"""One-time migration: relabel the identifiable historical GVR outcomes to ``gvr``.

Introducing the ``gvr`` disposition is a **forward-convention** change (see
``docs/salience.md``): new resolutions label a grant/vacate/remand ``gvr``, but
outcomes recorded before the label keep ``granted``. The one shape identifiable
from the committed ledger *alone* is the **Munsingwear vacatur** — a ``granted``
outcome whose ``disposition_basis`` is ``mootness`` — which this migration
relabels to ``gvr`` so the ledger matches the new convention (a Munsingwear
vacatur is ``gvr`` + ``mootness``).

It touches nothing else. A plain-``granted`` merits GVR in history is
indistinguishable post-hoc without re-resolving the source docket text (which the
``outcome.json`` does not carry), and is an accepted residual — immaterial on the
binary ``actual_granted`` axis, where ``gvr`` already counts as a grant, so the
Brier score and the ranked leaderboard are unaffected regardless. Relabeling is
also inert for the leaderboard: it reads the committed ``evaluation.json`` records
(whose ``correct`` / Brier were frozen at evaluation time), not the outcome, and
the relabeled cell keeps ``disposition_basis == "mootness"`` so it stays in the
procedural stratum. Deterministic, offline, idempotent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .schemas import Disposition, Outcome
from .serialize import read_model, write_json


@dataclass
class GvrMigrationResult:
    """What the GVR relabel migration changed (or would change on a dry run)."""

    applied: bool = False
    relabeled: list[str] = field(default_factory=list)  # case ids whose outcome flipped to gvr


def relabel_munsingwear_gvr_outcomes(data_root: Path, *, apply: bool) -> GvrMigrationResult:
    """Relabel each ``granted`` + ``mootness`` outcome to ``gvr`` under ``data/cases``.

    Dry run by default (finds the records, writes nothing); ``apply`` rewrites each
    matching ``outcome.json`` with ``actual_disposition = gvr`` (``actual_granted``
    is already 1 and stays 1 — ``gvr`` is a grant). Idempotent: a second run finds
    nothing because the relabeled records no longer read ``granted``.
    """
    relabeled: list[str] = []
    cases_root = data_root / "cases"
    for path in sorted(cases_root.glob("*/*/events/*/outcome.json")):
        outcome = read_model(path, Outcome)
        if (
            outcome.actual_disposition == Disposition.granted
            and outcome.disposition_basis == "mootness"
        ):
            relabeled.append(outcome.case_id)
            if apply:
                write_json(path, outcome.model_copy(update={"actual_disposition": Disposition.gvr}))
    return GvrMigrationResult(applied=apply, relabeled=sorted(relabeled))
