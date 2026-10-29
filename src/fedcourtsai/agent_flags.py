"""Make a cell's ``flags.json`` triageable: never fail a cell, collapse re-reports, mark themes.

``flags.json`` is the agents' durable channel to a maintainer (see
:class:`fedcourtsai.schemas.AgentFlags`). Three things keep it readable:

* **A flag never fails a predict or evaluate cell.** A cell's flags are
  advisory; its prediction or gradings are the output. So an off-vocabulary
  ``severity`` or ``category``, an over-long message, an unknown key, or a file
  that does not parse at all is *normalised* (:func:`normalise_flags`) by the
  stamp, before ``validate`` runs, instead of failing the cell and discarding
  its schema-true output with it. Every coerced flag is marked ``normalised``
  (the field's spelling) and a ``harness`` note beside it says what changed.
  Message text is never cut: an over-long message continues in further flags,
  and a file with no recoverable structure is carried verbatim (up to
  :data:`_RAW_CHUNKS_LIMIT` parts). What the note quotes of a *replaced* value
  — an off-vocabulary severity, a dropped key — is bounded. ``validate`` stays
  strict: a committed ``flags.json`` is schema law like any other artifact.
* **Collapse re-reports.** The roll-up (:func:`roll_up`) groups flags by
  ``(case, event, source, theme)``, where the theme is the tracked theme a flag
  cites or matches, else the issue it cites, else its category, and shows one
  row per group with the actors who raised it, instead of one row per actor per
  run.
* **Mark tracked themes.** A committed map (``flag_themes.json``,
  :func:`load_flag_themes`) names the themes an open issue already tracks. An
  agent flag matching one is counted against its issue instead of re-listed in
  full, so a new theme stands out. A flag may cite the issue itself
  (``issue``), which places it in that issue's theme whatever its wording. A
  ``blocker`` and a ``normalised`` flag are always listed, tracked or not, and
  a harness note is never counted as tracked. Nothing checks that the issue is
  still open: a theme is retired from the map when its issue closes.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .schemas import (
    SCHEMA_VERSION,
    AgentFlag,
    AgentFlags,
    FlagCategory,
    FlagSeverity,
    FlagSource,
    UsageRole,
)

#: The schema's cap on one flag's message, read off the field so the two cannot drift.
FLAG_MESSAGE_LIMIT: int = next(
    meta.max_length
    for meta in AgentFlag.model_fields["message"].metadata
    if getattr(meta, "max_length", None) is not None
)

#: The opening of the harness's note on a normalised file. A reading aid in the
#: roll-up, like every harness prefix: ``source`` is what the roll-up counts on.
NORMALISED_PREFIX = "Harness normalised this cell's flags.json so it validates"

#: How many harness flags may carry the text of a file that did not parse at all,
#: each at most :data:`FLAG_MESSAGE_LIMIT` long. Beyond it the text is clipped and
#: the clip is said, so a runaway file cannot grow the roll-up without bound.
_RAW_CHUNKS_LIMIT = 8

#: How much of a replaced value the harness note quotes.
_QUOTE_LIMIT = 80

#: Off-vocabulary severities with an unambiguous reading. Never ``blocker``: that
#: claims the cell could not finish, which only the schema's own spelling says.
_SEVERITY_SYNONYMS: dict[str, FlagSeverity] = {
    **dict.fromkeys(("low", "minor", "note", "trivial"), FlagSeverity.info),
    **dict.fromkeys(
        ("medium", "moderate", "high", "warn", "error", "critical", "severe", "fatal"),
        FlagSeverity.warning,
    ),
}

#: Off-vocabulary categories with an unambiguous reading: the names the cells
#: reached for before the vocabulary had a place for them.
_CATEGORY_SYNONYMS: dict[str, FlagCategory] = {
    **dict.fromkeys(
        ("outcome-exposure", "leakage", "leak", "outcome-leakage"),
        FlagCategory.leakage_disclosure,
    ),
    **dict.fromkeys(("capture", "data-capture"), FlagCategory.capture_gap),
    **dict.fromkeys(
        ("provision", "mis-provisioning", "missing-document"), FlagCategory.provisioning
    ),
}

_ISSUE_REFERENCE = re.compile(r"^\s*(?:#|gh-)?(\d+)\s*$", re.IGNORECASE)

_FLAG_KEYS = frozenset(AgentFlag.model_fields)
_ENVELOPE_KEYS = frozenset(AgentFlags.model_fields)
_ROLES = {member.value: member for member in UsageRole}
_SOURCES = {member.value: member for member in FlagSource}


@dataclass(frozen=True)
class CellCoordinates:
    """What the harness knows about a cell independently of what its file says."""

    case_id: str
    run_id: str
    role: UsageRole
    actor_id: str


def _quote(value: object) -> str:
    try:
        text = repr(value)
    except RecursionError:
        text = f"<a {type(value).__name__} too deeply nested to quote>"
    return text if len(text) <= _QUOTE_LIMIT else text[: _QUOTE_LIMIT - 1] + "…"


def _vocabulary_key(value: str) -> str:
    return re.sub(r"[\s_]+", "-", value.strip().lower())


def _coerce_enum[E: (FlagSeverity, FlagCategory)](
    value: object,
    enum: type[E],
    default: E,
    name: str,
    changes: list[str],
    synonyms: dict[str, E] | None = None,
) -> E:
    """``value`` as a member of ``enum``, else a synonym, else ``default`` — and say which."""
    if isinstance(value, str):
        if value in {member.value for member in enum}:
            return enum(value)
        spelled = _vocabulary_key(value)
        for member in enum:
            if member.value == spelled:
                changes.append(f"{name} {_quote(value)} read as '{member.value}'")
                return member
        if synonyms and spelled in synonyms:
            changes.append(f"{name} {_quote(value)} read as '{synonyms[spelled].value}'")
            return synonyms[spelled]
    changes.append(f"{name} {_quote(value)} is not one of the schema's values; set to '{default}'")
    return default


def _parts(text: str) -> list[str]:
    """``text`` cut into consecutive pieces that each fit one flag message."""
    return [text[i : i + FLAG_MESSAGE_LIMIT] for i in range(0, len(text), FLAG_MESSAGE_LIMIT)]


def _coerce_issue(value: object, changes: list[str]) -> int | None:
    """An ``issue`` citation as a positive number, reading ``"#123"`` as 123; else dropped."""
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    if isinstance(value, str):
        match = _ISSUE_REFERENCE.match(value)
        if match and int(match.group(1)) > 0:
            changes.append(f"issue {_quote(value)} read as {int(match.group(1))}")
            return int(match.group(1))
    changes.append(f"issue {_quote(value)} is not an issue number; dropped")
    return None


def _coerce_flag(raw: object, index: int, changes: list[str]) -> list[AgentFlag]:
    """One flag item coerced into :class:`AgentFlag` s — one, or several if it overflows.

    An over-long message continues in further flags of the same category,
    severity and event, so its text survives whole. ``[]`` when the item says
    nothing. ``changes`` collects a line per coercion, prefixed with the flag's
    position.
    """
    local: list[str] = []
    if isinstance(raw, str):
        raw = {"message": raw}
        local.append("was a bare string; read as the message")
    if not isinstance(raw, dict):
        changes.append(f"flag {index + 1}: {_quote(raw)} is not an object; dropped")
        return []
    message = raw.get("message")
    if message is not None and not isinstance(message, str):
        message = json.dumps(message, ensure_ascii=False)
        local.append("message was not text; carried as its JSON")
    if not isinstance(message, str) or not message.strip():
        changes.append(f"flag {index + 1}: no message; dropped (it read {_quote(raw)})")
        return []
    severity = _coerce_enum(
        raw.get("severity", FlagSeverity.info.value),
        FlagSeverity,
        FlagSeverity.warning,
        "severity",
        local,
        _SEVERITY_SYNONYMS,
    )
    category = _coerce_enum(
        raw.get("category"),
        FlagCategory,
        FlagCategory.other,
        "category",
        local,
        _CATEGORY_SYNONYMS,
    )
    issue = _coerce_issue(raw.get("issue"), local)
    event_id = raw.get("event_id")
    if event_id is not None and not isinstance(event_id, str):
        local.append(f"event_id {_quote(event_id)} is not a string; read as text")
        event_id = json.dumps(event_id, ensure_ascii=False)
    source = raw.get("source", FlagSource.agent.value)
    if not isinstance(source, str) or source not in _SOURCES:
        local.append(f"source {_quote(source)} is not one of the schema's values; set to 'agent'")
        source = FlagSource.agent.value
    extra = sorted(str(key) for key in raw if key not in _FLAG_KEYS)
    if extra:
        dropped = ", ".join(f"{key}={_quote(raw[key])}" for key in extra)
        local.append(f"unknown key(s) dropped: {dropped}")
    parts = _parts(message)
    if len(parts) > 1:
        local.append(f"message of {len(message)} characters continued across {len(parts)} flags")
    changes.extend(f"flag {index + 1}: {line}" for line in local)
    marked = bool(local) or raw.get("normalised") is True
    return [
        AgentFlag(
            category=category,
            severity=severity,
            message=part,
            event_id=event_id,
            issue=issue,
            source=_SOURCES[source],
            normalised=marked,
        )
        for part in parts
    ]


def _note(changes: Sequence[str], where: CellCoordinates) -> list[AgentFlag]:
    """The harness's account of a normalisation, continued across flags if it is long."""
    head = f"{NORMALISED_PREFIX} ({where.actor_id}): "
    return [
        AgentFlag(
            category=FlagCategory.other,
            severity=FlagSeverity.info,
            message=part,
            source=FlagSource.harness,
        )
        for part in _parts(head + "; ".join(changes) + ".")
    ]


def _unparsed(text: str, reason: str, where: CellCoordinates) -> AgentFlags:
    """A file with no recoverable structure, kept as its own text in harness flags."""
    chunks = _parts(text) or [""]
    clipped = len(chunks) > _RAW_CHUNKS_LIMIT
    chunks = chunks[:_RAW_CHUNKS_LIMIT]
    head = (
        f"{NORMALISED_PREFIX} ({where.actor_id}): the file {reason}, so its text is carried "
        f"below verbatim in {len(chunks)} part(s)"
        + (f", clipped at {_RAW_CHUNKS_LIMIT} parts of {len(text)} characters" if clipped else "")
        + "."
    )
    flags = [
        AgentFlag(
            category=FlagCategory.other,
            severity=FlagSeverity.info,
            message=head,
            source=FlagSource.harness,
        )
    ]
    flags.extend(
        AgentFlag(
            category=FlagCategory.other,
            severity=FlagSeverity.info,
            message=chunk if chunk.strip() else "(empty)",
            source=FlagSource.harness,
            normalised=True,
        )
        for chunk in chunks
    )
    return AgentFlags(
        case_id=where.case_id,
        run_id=where.run_id,
        role=where.role,
        actor_id=where.actor_id,
        flags=flags,
    )


def _envelope_string(raw: dict[str, Any], key: str, fallback: str, changes: list[str]) -> str:
    value = raw.get(key)
    if isinstance(value, str) and value:
        return value
    changes.append(f"{key} {_quote(value)} missing or not text; set to {fallback!r}")
    return fallback


@dataclass(frozen=True)
class Normalised:
    """What :func:`normalise_flags` made of a file: the set, and whether it moved."""

    flags: AgentFlags
    changed: bool


def normalise_flags(text: str, where: CellCoordinates) -> Normalised:
    """Coerce a cell's ``flags.json`` text into a valid :class:`AgentFlags`.

    Total: whatever ``text`` is, the result validates and never raises — any
    shape no rule below anticipates is carried verbatim instead. A file that
    already validates comes back unchanged (``changed`` false). Otherwise every
    coercion is recorded in a ``harness`` note appended to the set, and each
    coerced flag is marked ``normalised``:

    * an off-vocabulary ``severity`` is matched case- and underscore-insensitively,
      then through a small synonym table (``low`` reads as ``info``, ``high`` or
      ``critical`` as ``warning``), and is otherwise ``warning`` — loud enough to
      be read, never ``blocker``; an off-vocabulary ``category`` is matched the
      same way, then through its own synonyms (``outcome-exposure`` reads as
      ``leakage-disclosure``), and is otherwise ``other``;
    * an ``issue`` written as ``"#123"`` reads as 123; one that is not an issue
      number is dropped;
    * a message over the schema's cap continues in further flags, never cut;
    * an unknown key is dropped and its value quoted (bounded) in the note;
    * a missing envelope field (case, run, role, actor) is filled from the
      harness's own coordinates for the cell; a present one is kept as written;
    * a flag with no message is dropped and quoted (bounded) in the note;
    * a file that is not a JSON object is carried verbatim in harness flags.
    """
    # Broad on purpose, both times: totality is the contract. Any refusal of the
    # strict read falls through to coercion, and any shape coercion did not
    # foresee is carried verbatim rather than failing the cell.
    try:
        return Normalised(AgentFlags.model_validate_json(text), changed=False)
    except Exception:
        pass
    try:
        return _normalise_structure(text, where)
    except Exception:
        return Normalised(_unparsed(text, "could not be normalised", where), changed=True)


def _normalise_structure(text: str, where: CellCoordinates) -> Normalised:
    try:
        raw = json.loads(text)
    except (ValueError, RecursionError):
        return Normalised(_unparsed(text, "does not parse as JSON", where), changed=True)
    if isinstance(raw, list):
        raw = {"flags": raw}
    if not isinstance(raw, dict):
        return Normalised(_unparsed(text, "is not a JSON object", where), changed=True)

    changes: list[str] = []
    if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        changes.append(f"schema_version {_quote(raw.get('schema_version'))} set to '1.0'")
    case_id = _envelope_string(raw, "case_id", where.case_id, changes)
    run_id = _envelope_string(raw, "run_id", where.run_id, changes)
    actor_id = _envelope_string(raw, "actor_id", where.actor_id, changes)
    role_value = raw.get("role")
    role = where.role
    if isinstance(role_value, str) and role_value in _ROLES:
        role = _ROLES[role_value]
    else:
        changes.append(f"role {_quote(role_value)} set to '{where.role}'")
    extra = sorted(str(key) for key in raw if key not in _ENVELOPE_KEYS)
    if extra:
        dropped = ", ".join(f"{key}={_quote(raw[key])}" for key in extra)
        changes.append(f"unknown top-level key(s) dropped: {dropped}")

    items = raw.get("flags")
    if isinstance(items, dict | str):
        items = [items]
        changes.append("flags was a single item; read as a one-item list")
    if not isinstance(items, list):
        changes.append(f"flags {_quote(items)} is not a list")
        items = []
    coerced = [
        flag for index, item in enumerate(items) for flag in _coerce_flag(item, index, changes)
    ]
    if not coerced:
        changes.append("no usable flag survived")
    if not changes:
        # Every field read as valid on its own and the model still refused the
        # whole: no rule above knows the reason, so carry the file verbatim
        # rather than claim a normalisation that did not happen.
        return Normalised(_unparsed(text, "does not validate", where), changed=True)
    return Normalised(
        AgentFlags(
            case_id=case_id,
            run_id=run_id,
            role=role,
            actor_id=actor_id,
            flags=[*coerced, *_note(changes, where)],
        ),
        changed=True,
    )


def coordinates_from_path(path: Path) -> CellCoordinates | None:
    """A ``flags.json``'s cell, read off its ledger path, or ``None`` off the layout.

    ``.../cases/<court>/<docket>/events/<event>/predictions/<actor>/<run>/flags.json``
    or ``.../evaluations/<actor>/<run>/flags.json``.
    """
    parts = path.parts
    if len(parts) < 9 or parts[-1] != "flags.json":
        return None
    stage, actor, run = parts[-4], parts[-3], parts[-2]
    roles = {"predictions": UsageRole.predictor, "evaluations": UsageRole.evaluator}
    if stage not in roles or parts[-6] != "events" or parts[-9] != "cases":
        return None
    return CellCoordinates(
        case_id=f"{parts[-8]}/{parts[-7]}", run_id=run, role=roles[stage], actor_id=actor
    )


# --- tracked themes -----------------------------------------------------------

#: The committed theme map: a package resource, so the roll-up needs no config path.
FLAG_THEMES_RESOURCE = "flag_themes.json"


class FlagTheme(BaseModel):
    """One recurring flag theme an open issue already tracks.

    A flag belongs to the theme when **every** pattern in ``all_of`` matches its
    message (case-insensitive regex search): one pattern names the subject, the
    others pin the reading, so a flag that merely mentions the subject is not
    swept into a tracked count.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    issue: int = Field(gt=0)
    summary: str = Field(min_length=1, max_length=200)
    all_of: tuple[str, ...] = Field(min_length=1)

    @field_validator("all_of")
    @classmethod
    def _compiles(cls, patterns: tuple[str, ...]) -> tuple[str, ...]:
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ValueError(f"pattern {pattern!r} does not compile: {exc}") from exc
        return patterns

    def matches(self, message: str) -> bool:
        return all(re.search(pattern, message, re.IGNORECASE) for pattern in self.all_of)


class _FlagThemes(BaseModel):
    model_config = ConfigDict(extra="forbid")

    themes: tuple[FlagTheme, ...]


def load_flag_themes(text: str | None = None) -> tuple[FlagTheme, ...]:
    """The tracked themes in map order; ``text`` overrides the packaged file.

    Refuses a theme id registered twice, so a count never splits across two rows.
    """
    if text is None:
        return _packaged_themes()
    themes = _FlagThemes.model_validate_json(text).themes
    seen: set[str] = set()
    for theme in themes:
        if theme.id in seen:
            raise ValueError(f"{FLAG_THEMES_RESOURCE} registers theme {theme.id!r} twice")
        seen.add(theme.id)
    return themes


@cache
def _packaged_themes() -> tuple[FlagTheme, ...]:
    return load_flag_themes(
        files("fedcourtsai").joinpath(FLAG_THEMES_RESOURCE).read_text(encoding="utf-8")
    )


def theme_of(flag: AgentFlag, themes: Sequence[FlagTheme]) -> FlagTheme | None:
    """The tracked theme a flag cites by ``issue``, else the first its message matches.

    ``None`` when neither holds.
    """
    if flag.issue is not None:
        cited = next((theme for theme in themes if theme.issue == flag.issue), None)
        if cited is not None:
            return cited
    return next((theme for theme in themes if theme.matches(flag.message)), None)


# --- roll-up ------------------------------------------------------------------

# Loudest first, so the roll-up leads with anything that blocked a cell.
SEVERITY_RANK = {FlagSeverity.blocker: 0, FlagSeverity.warning: 1, FlagSeverity.info: 2}


@dataclass
class FlagGroup:
    """Every flag one ``(case, event, source, theme)`` key collected.

    The theme key is the tracked theme's id where one matched, else ``#<issue>``
    where the flag cites an untracked issue, else the category, so sibling
    actors' notes on one event land in one row.
    """

    case_id: str
    event_id: str
    source: FlagSource
    category: str
    theme: FlagTheme | None
    severity: FlagSeverity = FlagSeverity.info
    #: The untracked issue every flag in the group cites, where the group is keyed on one.
    issue: int | None = None
    count: int = 0
    actors: list[str] = field(default_factory=list)
    runs: set[str] = field(default_factory=set)
    #: Distinct messages in first-seen order, each with the actors who wrote it.
    notes: dict[str, list[str]] = field(default_factory=dict)

    def add(self, actor_id: str, run_id: str, flag: AgentFlag) -> None:
        severity = FlagSeverity(flag.severity)
        if SEVERITY_RANK[severity] < SEVERITY_RANK[self.severity]:
            self.severity = severity
        self.count += 1
        self.runs.add(run_id)
        if actor_id not in self.actors:
            self.actors.append(actor_id)
        writers = self.notes.setdefault(" ".join(flag.message.split()), [])
        if actor_id not in writers:
            writers.append(actor_id)


@dataclass(frozen=True)
class TrackedCount:
    """How many flags matched one tracked theme, shown as a count, not as rows."""

    theme: FlagTheme
    flags: int
    actors: int
    cases: int


@dataclass(frozen=True)
class FlagRollup:
    """A set of flags collapsed for triage: listed groups, tracked counts, totals."""

    groups: tuple[FlagGroup, ...]
    tracked: tuple[TrackedCount, ...]
    total: int
    #: Flags marked ``source: harness``.
    harness: int
    #: Cells (flag sets) carrying at least one ``normalised`` flag — one per
    #: malformed file, however many flags its normalisation produced. Overlaps
    #: ``harness``: a file carried verbatim is carried in harness flags.
    normalised_cells: int


def roll_up(
    flag_sets: Iterable[AgentFlags], themes: Sequence[FlagTheme] | None = None
) -> FlagRollup:
    """Collapse flag sets by ``(case, event, source, theme)`` and count tracked themes.

    ``themes`` defaults to the committed map. A flag matching a tracked theme is
    counted against it and not listed, unless it is a ``blocker`` (a cell that
    could not finish is always shown in full) or ``normalised`` (a coerced flag
    is never hidden inside a count). A harness note is never counted as tracked.
    """
    themes = _packaged_themes() if themes is None else themes
    groups: dict[tuple[str, str, str, str], FlagGroup] = {}
    tracked: dict[str, tuple[FlagTheme, int, set[str], set[str]]] = {}
    total = harness = normalised_cells = 0
    for fs in flag_sets:
        normalised_cells += any(flag.normalised for flag in fs.flags)
        for flag in fs.flags:
            total += 1
            source = FlagSource(flag.source)
            harness += source == FlagSource.harness
            theme = theme_of(flag, themes) if source == FlagSource.agent else None
            listed_anyway = flag.severity == FlagSeverity.blocker or flag.normalised
            if theme is not None and not listed_anyway:
                _, count, actors, cases = tracked.get(theme.id, (theme, 0, set(), set()))
                tracked[theme.id] = (theme, count + 1, actors | {fs.actor_id}, cases | {fs.case_id})
                continue
            event = flag.event_id or ""
            if theme is not None:
                theme_key = theme.id
            elif flag.issue is not None:
                theme_key = f"#{flag.issue}"
            else:
                theme_key = str(flag.category)
            key = (fs.case_id, event, source.value, theme_key)
            group = groups.get(key)
            if group is None:
                group = groups[key] = FlagGroup(
                    case_id=fs.case_id,
                    event_id=event,
                    source=source,
                    category=str(flag.category),
                    theme=theme,
                    severity=FlagSeverity(flag.severity),
                    issue=flag.issue if theme is None else None,
                )
            group.add(fs.actor_id, fs.run_id, flag)
    ordered = sorted(
        groups.values(),
        key=lambda g: (SEVERITY_RANK[g.severity], g.case_id, g.event_id, g.source, g.category),
    )
    counts = sorted(
        (
            TrackedCount(theme=theme, flags=count, actors=len(actors), cases=len(cases))
            for theme, count, actors, cases in tracked.values()
        ),
        key=lambda t: (-t.flags, t.theme.issue),
    )
    return FlagRollup(
        groups=tuple(ordered),
        tracked=tuple(counts),
        total=total,
        harness=harness,
        normalised_cells=normalised_cells,
    )
