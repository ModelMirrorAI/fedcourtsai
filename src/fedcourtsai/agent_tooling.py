"""Coercing a cell's mis-shaped ``tooling.json`` into the schema's shape.

A predict or evaluate cell's ``tooling.json`` is its advisory self-report on the
tooling it was given (:class:`fedcourtsai.schemas.AgentToolingFeedback`): never
graded, never a gate. Its prediction or gradings are its output, so a report
the agent mis-shaped — an invented key, a list written as a string — must not
fail ``validate`` and discard the output beside it. ``stamp-cell`` runs
:func:`normalise_tooling` before ``validate``, the same place it normalises
``flags.json`` (:mod:`fedcourtsai.agent_flags`); ``validate`` stays strict.

One field is not coerced: ``used_corpus_query``, which the ``collect`` job reads
as the cell's own word on whether it queried the corpus. Where the agent did not
answer it as a yes or no, no value can be supplied without inventing that
answer, so the file is left as written and the cell fails as before.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .agent_flags import CellCoordinates
from .schemas import AgentToolingFeedback

_LIST_KEYS = ("tools_used", "helpful", "gaps")
_FIELDS = AgentToolingFeedback.model_fields
#: The schema's caps; a test pins them to the model's own.
_LIST_LIMIT = 50
_MANIFEST_LIMIT = 20
_NOTES_LIMIT = 2000
#: How much of a dropped or replaced value the harness note quotes.
_QUOTE_LIMIT = 80
#: Strings an agent writes for "nothing here" in a list field.
_EMPTY_WORDS = frozenset({"", "none", "n/a", "na", "null", "nil", "-"})
_TRUE_WORDS = frozenset({"true", "yes", "y", "1"})
_FALSE_WORDS = frozenset({"false", "no", "n", "0"})
_HARNESS_PREFIX = "[harness] "


@dataclass(frozen=True)
class NormalisedTooling:
    """What :func:`normalise_tooling` made of a file, and whether it moved.

    ``feedback`` is ``None`` when the file was left as written: it already
    validated (``changed`` false), or it could not be made valid without
    inventing ``used_corpus_query`` (``changed`` false too, so nothing is
    rewritten and ``validate`` decides).
    """

    feedback: AgentToolingFeedback | None
    changed: bool


def _quote(value: object) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        text = repr(value)
    return text if len(text) <= _QUOTE_LIMIT else text[: _QUOTE_LIMIT - 3] + "..."


def _boolean(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        word = value.strip().lower()
        if word in _TRUE_WORDS:
            return True
        if word in _FALSE_WORDS:
            return False
    return None


def _text_list(key: str, value: object, changes: list[str]) -> list[str]:
    if isinstance(value, list):
        items = [item if isinstance(item, str) else _quote(item) for item in value]
        items = [item for item in items if item.strip().lower() not in _EMPTY_WORDS]
        if items != value:
            changes.append(f"{key} items made text, empty ones dropped")
    elif isinstance(value, str):
        items = [] if value.strip().lower() in _EMPTY_WORDS else [value]
        changes.append(f"{key} {_quote(value)} written as text; read as a list")
    elif value is None:
        items = []
    else:
        items = [_quote(value)]
        changes.append(f"{key} {_quote(value)} not a list; quoted as one item")
    if len(items) > _LIST_LIMIT:
        changes.append(f"{key} cut from {len(items)} to {_LIST_LIMIT} items")
        items = items[:_LIST_LIMIT]
    return items


def _envelope(raw: dict[str, Any], key: str, fallback: str, changes: list[str]) -> str:
    value = raw.get(key)
    if isinstance(value, str) and value:
        return value
    changes.append(f"{key} {_quote(value)} missing or not text; set to {fallback!r}")
    return fallback


def normalise_tooling(text: str, where: CellCoordinates) -> NormalisedTooling:
    """Coerce a cell's ``tooling.json`` text into a valid report, where that is honest.

    Never raises. A file that already validates comes back untouched. Otherwise,
    when ``used_corpus_query`` reads as a yes or no (a boolean, or a ``"true"``
    / ``"no"``-style word), the report is rebuilt:

    * an unknown key is dropped and its value quoted (bounded) in a
      ``[harness]`` line appended to ``notes``;
    * a list field written as a string is read as one item, or as none when it
      says "None" and the like; non-text items are quoted; a list over the
      schema's cap is cut;
    * ``used_base_rates`` is read as a yes or no, else left at its default;
    * a missing envelope field (case, run, role, actor) is filled from the
      harness's own coordinates for the cell; a present one is kept;
    * ``notes`` and ``tool_manifest`` are kept when they fit, else dropped and
      named in the note.

    Where ``used_corpus_query`` is missing or not a yes or no, or the text is not
    a JSON object, the file is left as written (``feedback`` is ``None``).
    """
    try:
        AgentToolingFeedback.model_validate_json(text)
        return NormalisedTooling(None, changed=False)
    except Exception:
        pass
    # Broad on purpose: totality is the contract, and an unforeseen shape leaves
    # the file to `validate` rather than failing the stamp.
    try:
        return _rebuild(text, where)
    except Exception:
        return NormalisedTooling(None, changed=False)


def _optional_fields(raw: dict[str, Any], changes: list[str]) -> dict[str, Any]:
    """The report's optional fields as the schema reads them, coerced where they can be."""
    fields: dict[str, Any] = {}
    if "used_base_rates" in raw:
        base_rates = _boolean(raw["used_base_rates"])
        if base_rates is None:
            changes.append(f"used_base_rates {_quote(raw['used_base_rates'])} not a yes or no")
        else:
            fields["used_base_rates"] = base_rates
    for key in _LIST_KEYS:
        if key in raw:
            fields[key] = _text_list(key, raw[key], changes)
    manifest = raw.get("tool_manifest")
    if manifest is not None:
        if isinstance(manifest, list) and all(isinstance(item, str) for item in manifest):
            fields["tool_manifest"] = manifest[:_MANIFEST_LIMIT]
            if len(manifest) > _MANIFEST_LIMIT:
                changes.append(f"tool_manifest cut from {len(manifest)} to {_MANIFEST_LIMIT} items")
        else:
            changes.append(f"tool_manifest {_quote(manifest)} not a list of text; dropped")
    return fields


def _rebuild(text: str, where: CellCoordinates) -> NormalisedTooling:
    raw = json.loads(text)
    if not isinstance(raw, dict):
        return NormalisedTooling(None, changed=False)
    used_corpus_query = _boolean(raw.get("used_corpus_query"))
    if used_corpus_query is None:
        return NormalisedTooling(None, changed=False)
    changes: list[str] = []
    if not isinstance(raw.get("used_corpus_query"), bool):
        changes.append(f"used_corpus_query {_quote(raw['used_corpus_query'])} read as a yes or no")
    report: dict[str, Any] = {
        "case_id": _envelope(raw, "case_id", where.case_id, changes),
        "run_id": _envelope(raw, "run_id", where.run_id, changes),
        "role": where.role,
        "actor_id": _envelope(raw, "actor_id", where.actor_id, changes),
        "used_corpus_query": used_corpus_query,
    }
    if raw.get("role") != where.role.value:
        changes.append(f"role {_quote(raw.get('role'))} set to {where.role.value!r}")
    report.update(_optional_fields(raw, changes))
    for key in sorted(set(raw) - set(_FIELDS)):
        changes.append(f"unknown key {key!r} = {_quote(raw[key])} dropped")
    notes = raw.get("notes")
    if notes is not None and not isinstance(notes, str):
        changes.append(f"notes {_quote(notes)} not text; quoted")
        notes = _quote(notes)
    note = _HARNESS_PREFIX + "tooling.json did not validate; normalised: " + "; ".join(changes)
    combined = f"{notes}\n{note}" if notes else note
    if len(combined) > _NOTES_LIMIT:
        combined = combined[: _NOTES_LIMIT - 3] + "..."
    report["notes"] = combined
    return NormalisedTooling(AgentToolingFeedback.model_validate(report), changed=True)
