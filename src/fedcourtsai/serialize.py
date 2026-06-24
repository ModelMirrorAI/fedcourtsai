"""Deterministic (re)serialization helpers.

All writes are sorted and newline-terminated so that re-running a pull or
prediction produces minimal, reviewable git diffs.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def write_json(path: Path, model: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = model.model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_yaml(path: Path, model: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = model.model_dump(mode="json")
    path.write_text(yaml.safe_dump(payload, sort_keys=True, default_flow_style=False))


def write_raw_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, models: Iterable[BaseModel]) -> None:
    """Write models as newline-delimited JSON, one compact object per line.

    Lines are sorted so the packed artifact is byte-stable regardless of the
    order rows are produced in — the same minimal-diff guarantee ``write_json``
    gives single artifacts, applied to the packed corpus.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = sorted(
        json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        for model in models
    )
    path.write_text("".join(line + "\n" for line in lines))


def read_model[T: BaseModel](path: Path, model: type[T]) -> T:
    text = path.read_text()
    data = yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)
    return model.model_validate(data)
