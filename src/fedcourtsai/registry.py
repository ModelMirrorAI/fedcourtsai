"""Loads the predictor and evaluator registries.

The registries are the routing table for the multi-agent ``run-predict`` and
``run-evaluate`` workflows: each enabled entry becomes one matrix job on each
event of its own prediction population's dockets. Adding a
new competing predictor is a one-line config change (and, later, the output of
the hypothesis-generation harness). Each registry also carries the
**tool manifest** (``mcp_servers:``) — the pinned MCP servers its actors'
cells are configured with, referenced per actor by id.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .prediction_slices import SCOTUS_POPULATION_KEY, SLICES
from .schemas import EvaluatorConfig, McpServerConfig, PredictorConfig


def _known_population[A: (PredictorConfig, EvaluatorConfig)](actor: A) -> A:
    """Refuse an actor of a population no code declares.

    A misspelt population would leave an enabled actor that no docket is ever
    routed to, which reads as a fleet member and mints nothing.
    """
    if actor.population != SCOTUS_POPULATION_KEY and actor.population not in SLICES:
        raise ValueError(
            f"actor {actor.id!r} names population {actor.population!r}; known: "
            f"{sorted({SCOTUS_POPULATION_KEY, *SLICES})}"
        )
    return actor


def load_predictors(path: Path) -> list[PredictorConfig]:
    data = yaml.safe_load(path.read_text()) or {}
    return [
        _known_population(PredictorConfig.model_validate(p)) for p in data.get("predictors", [])
    ]


def load_evaluators(path: Path) -> list[EvaluatorConfig]:
    data = yaml.safe_load(path.read_text()) or {}
    return [
        _known_population(EvaluatorConfig.model_validate(e)) for e in data.get("evaluators", [])
    ]


def enabled_predictors(path: Path) -> list[PredictorConfig]:
    return [p for p in load_predictors(path) if p.enabled]


def enabled_evaluators(path: Path) -> list[EvaluatorConfig]:
    return [e for e in load_evaluators(path) if e.enabled]


def predictors_for(path: Path, population: str) -> list[PredictorConfig]:
    """The enabled predictors that forecast ``population``'s dockets.

    :func:`enabled_predictors` is the whole fleet, which the process registry
    and the blinding scrub read; a reader that asks who owes a docket a cell
    asks for the docket's population.
    """
    return [p for p in enabled_predictors(path) if p.population == population]


def evaluators_for(path: Path, population: str) -> list[EvaluatorConfig]:
    """The enabled evaluators that grade ``population``'s dockets."""
    return [e for e in enabled_evaluators(path) if e.population == population]


def load_mcp_servers(path: Path) -> list[McpServerConfig]:
    """The tool manifest (``mcp_servers:``) from a registry file.

    Lives in the same file as the actor entries that reference it by id, so an
    actor's retrieval configuration is one reviewable diff. A missing section
    means an empty manifest (registries written before the manifest existed stay valid).
    """
    data = yaml.safe_load(path.read_text()) or {}
    return [McpServerConfig.model_validate(s) for s in data.get("mcp_servers", [])]


def resolve_mcp_servers(manifest: list[McpServerConfig], ids: list[str]) -> list[McpServerConfig]:
    """The manifest entries an actor's ``mcp_servers`` ids name, in id order.

    Raises ``KeyError`` on an unknown id — a typo in the registry must fail the
    plan loudly, never silently configure a cell with fewer tools than the
    attribution record claims.
    """
    by_id = {server.id: server for server in manifest}
    return [by_id[server_id] for server_id in sorted(ids)]
