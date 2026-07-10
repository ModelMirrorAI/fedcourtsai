"""Loads the predictor and evaluator registries.

The registries are the routing table for the multi-agent ``run-predict`` and
``run-evaluate`` workflows: each enabled entry becomes one matrix job. Adding a
new competing predictor is a one-line config change (and, later, the output of
the hypothesis-generation harness). Since #525 each registry also carries the
**tool manifest** (``mcp_servers:``) — the pinned MCP servers its actors'
cells are configured with, referenced per actor by id.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .schemas import EvaluatorConfig, McpServerConfig, PredictorConfig


def load_predictors(path: Path) -> list[PredictorConfig]:
    data = yaml.safe_load(path.read_text()) or {}
    return [PredictorConfig.model_validate(p) for p in data.get("predictors", [])]


def load_evaluators(path: Path) -> list[EvaluatorConfig]:
    data = yaml.safe_load(path.read_text()) or {}
    return [EvaluatorConfig.model_validate(e) for e in data.get("evaluators", [])]


def enabled_predictors(path: Path) -> list[PredictorConfig]:
    return [p for p in load_predictors(path) if p.enabled]


def enabled_evaluators(path: Path) -> list[EvaluatorConfig]:
    return [e for e in load_evaluators(path) if e.enabled]


def load_mcp_servers(path: Path) -> list[McpServerConfig]:
    """The tool manifest (``mcp_servers:``) from a registry file (#525).

    Lives in the same file as the actor entries that reference it by id, so an
    actor's retrieval configuration is one reviewable diff. A missing section
    means an empty manifest (pre-#525 registries stay valid).
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
