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

try:
    # libyaml's safe loader, which PyYAML's wheels are built with. It resolves the
    # same tags as the pure-Python ``SafeLoader`` at roughly ten times the speed,
    # and the ledger scan parses one YAML file per event.
    from yaml import CSafeLoader as _SafeLoader
except ImportError:  # pragma: no cover - a PyYAML built without libyaml
    from yaml import SafeLoader as _SafeLoader  # type: ignore[assignment]


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


def write_text(path: Path, text: str) -> None:
    """Write rendered text (e.g. a Markdown report), newline-terminated, creating parents.

    The plain-text counterpart of :func:`write_json` for a deterministically rendered
    document, so a rerun over unchanged input reproduces the file byte for byte.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n")


def load_yaml(text: str) -> Any:
    """Parse one YAML document with the safe loader — :func:`yaml.safe_load`, faster."""
    return yaml.load(text, Loader=_SafeLoader)


def read_model[T: BaseModel](path: Path, model: type[T]) -> T:
    text = path.read_text()
    data = load_yaml(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)
    return model.model_validate(data)
