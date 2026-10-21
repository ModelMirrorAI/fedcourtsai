"""The per-cell planning rates every predict and evaluate plan prices its fan-out at.

These rates are spend authority, not only reporting: the review hold's
auto-release (:mod:`fedcourtsai.review_hold`) compares a round's priced
fan-out against its per-round cap, so lowering a rate lets a larger round
skip the maintainer's release. The module is owned by the maintainer for
that reason (``.github/CODEOWNERS``), and a re-anchor lands as a visible edit
to ``tests/test_cli_matrix.py``'s pinned totals.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

#: The **fallback** per-cell rate: the ~$17 a fully-tournamented case costs,
#: divided across its design mix of six cells. It prices a cell whose engine the
#: table below does not name — a new engine, or a registry entry ahead of the
#: table — so a plan never silently drops such a cell from its total. Re-anchor
#: it when the table below moves.
PLANNING_USD_PER_CELL = 2.80

#: Per-cell rates in USD, keyed (seam, engine) — the source for every spend
#: figure a plan prints; ``docs/budget.md`` sizes the program from measurements
#: like these, not the other way round. The claude-code and codex predict cells
#: are measured: one stamped fan-out, 81 cells over 27 events, since re-based
#: out of the frozen partition by the predictor re-blesses that followed it.
#: Their evaluate cells are the better-matched of the two pre-freeze cert-stage
#: anchors — the ``proc-v2`` grading — scaled by the whole predict move
#: (x1.218), the same scaling the per-case derivation uses. The other stamped
#: evaluate gradings are interim-stage, graded before the current instant under
#: superseded evaluator digests, so they re-anchor nothing here. The gemini
#: cells price ``gemini-4-argon``: its first measured cells (5 predictions at
#: about $1.06, 18 grading runs at about $0.64, at the introductory $2 / $10)
#: doubled for the $4 / $20 rate in force from 2026-12-01, so the row holds
#: across that change. See the spend-basis caveats every plan carries
#: (``fedcourtsai.cli``). The two seams sum to $8.27 + $8.51 = $16.78 a case,
#: which the $2.80 fallback is the six-cell rounding of — so a full
#: three-engine, both-seam fan-out prices within a cent either way.
#: ``docs/milestones.md``'s ~$17 per fully evaluated event is that same total:
#: one table, described twice, not two measurements. What
#: conditioning buys is the *narrowed* plan: within a seam the engines differ
#: up to ~4.6x, so an engine-narrowed backfill priced at the flat rate is wrong
#: by up to ~2.2x.
#:
#: Engine keys, not actor ids: a cell carries its resolved ``engine``, and the
#: per-actor measurements behind these rows are one actor per engine in the
#: shipped registries.
PLANNING_RATES_USD_PER_CELL: dict[str, dict[str, float]] = {
    "predict": {"claude-code": 4.27, "codex": 1.88, "gemini": 2.12},
    "evaluate": {"claude-code": 5.92, "codex": 1.30, "gemini": 1.29},
}


def price_cells(cells: Iterable[Mapping[str, Any]], *, seam: str) -> tuple[float, int]:
    """The summed per-(seam, engine) price of ``cells``, and how many fell back.

    A cell whose ``engine`` the table does not name is priced at the design-mix
    fallback and counted, so an unrecognised engine is a stated approximation
    rather than a cell missing from the total.
    """
    rates = PLANNING_RATES_USD_PER_CELL[seam]
    total = 0.0
    at_fallback = 0
    for cell in cells:
        rate = rates.get(str(cell.get("engine")))
        if rate is None:
            rate = PLANNING_USD_PER_CELL
            at_fallback += 1
        total += rate
    return total, at_fallback
