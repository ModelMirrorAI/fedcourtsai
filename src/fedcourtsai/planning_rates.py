"""The planning rates spend plans price their rounds at: per cell, and per labeled row.

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


#: Per-row topic-labeler rates in USD, keyed by the labeler's model — what a
#: label round's plan prices its batch at, and so what the review hold's
#: auto-release compares against the per-round cap. Set at or above the
#: measured runs, each a ceiling-sized 1,200-row batch read in one headless
#: session: ``claude-opus-5-5`` measured $10.01 a batch (about $0.0083 a row),
#: priced at $0.02 a row ($24 a batch, about 2.4x the one measurement, since a
#: run's spend varies with how many turns it takes); ``claude-fable-5``
#: measured $37.48 and $60.16 a batch (about $0.031 and $0.050 a row), priced
#: at $0.06 a row ($72 a batch, above the dearer of the two). A refused or short
#: run spends like a published one, so the rate prices every run whatever its
#: outcome.
LABEL_RATES_USD_PER_ROW: dict[str, float] = {
    "claude-opus-5-5": 0.02,
    "claude-fable-5": 0.06,
}


#: Per-row merits side-coder rates in USD, keyed by the coder's model — what a
#: side-coding round (the ``alignment-sides`` frame) prices its batch at. No
#: side-coding run has been measured, so each row is three times the topic
#: labeler's rate for the same model: a side code reads the same
#: questions-presented text a topic label does, and writes a scored call and a
#: one-sentence note where a topic label writes a register, so it is priced as
#: the dearer task until the first run's spend record re-anchors it.
SIDE_CODE_RATES_USD_PER_ROW: dict[str, float] = {
    "claude-opus-5-5": 0.06,
    "claude-fable-5": 0.18,
}

#: The frame whose rounds the side-coder table prices; every other frame is a
#: topic-label frame.
SIDE_CODE_FRAME = "alignment-sides"


def label_rates_for(frame: str) -> dict[str, float]:
    """The per-row rate table a label round of ``frame`` prices at."""
    return SIDE_CODE_RATES_USD_PER_ROW if frame == SIDE_CODE_FRAME else LABEL_RATES_USD_PER_ROW


def label_rate_usd_per_row(model: str, *, frame: str = "petitions") -> float:
    """The per-row rate a label round of ``model`` over ``frame`` prices at.

    A model the frame's table does not name prices at that table's highest
    rate, so a new labeler model is never priced below the dearest one the
    table names.
    """
    rates = label_rates_for(frame)
    return rates.get(model, max(rates.values()))
