"""Loads the predictor and evaluator registries.

The registries are the routing table for the multi-agent ``run-predict`` and
``run-evaluate`` workflows: each enabled entry becomes one matrix job. Adding a
new competing predictor is a one-line config change (and, later, the output of
the hypothesis-generation harness).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .schemas import EvaluatorConfig, PredictorConfig


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
