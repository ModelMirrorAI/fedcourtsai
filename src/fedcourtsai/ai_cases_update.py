"""The AI-cases update: the watchlist's significant docket activity over a span, for email.

Rendered from the committed daily activity records
(``data/ai-cases/activity/<YYYY-MM-DD>.json``, :mod:`fedcourtsai.ai_activity`)
alone: no corpus, no model call, so the same tree and span render the same
bytes. Each item is a date, the kind of entry the activity rule assigned, the
docket and entry number, and a link to the entry on CourtListener; no docket
text is quoted, so the update points to the public record rather than copying
it.

A span is either one day or one ISO week. Its items are the entries recorded on
days inside it, grouped by case in the order each case's first item was filed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Final

from .ai_activity import ACTIVITY_DIR
from .schemas import AiCaseActivity, AiCaseActivityEntry
from .serialize import read_model

#: The kinds in the reader's words.
KIND_LABELS: Final = {
    "opinion": "Opinion",
    "judgment": "Judgment",
    "ruling": "Ruling on a motion",
    "motion": "Motion filed",
    "complaint": "Complaint",
    "appeal": "Appeal",
    "resolution": "Settlement or dismissal",
}

_INTRO: Final = (
    "New rulings and major filings in the federal AI cases FedCourtsAI follows, "
    "read from the public docket. Each item links to the entry on CourtListener."
)
_FOOTER: Final = (
    "Docket data from [CourtListener](https://www.courtlistener.com/), a project of "
    "Free Law Project. The list of cases and the rule that picks which entries "
    "appear are public in the "
    "[FedCourtsAI repository](https://github.com/ModelMirrorAI/fedcourtsai/blob/main/config/ai-watchlist.yaml)."
)


@dataclass(frozen=True)
class AiCasesUpdate:
    start: date
    end: date
    # Each case's items, cases in the order of their first item.
    cases: tuple[tuple[str, str, tuple[AiCaseActivityEntry, ...]], ...]

    @property
    def empty(self) -> bool:
        return not self.cases

    @property
    def items(self) -> int:
        return sum(len(entries) for _, _, entries in self.cases)


def build_ai_cases_update(data_root: Path, start: date, end: date) -> AiCasesUpdate:
    """The span's items from the activity records of the days ``start`` through ``end``."""
    found: dict[int, AiCaseActivityEntry] = {}
    day = start
    while day <= end:
        path = data_root / ACTIVITY_DIR / f"{day.isoformat()}.json"
        if path.is_file():
            for entry in read_model(path, AiCaseActivity).entries:
                found.setdefault(entry.entry_id, entry)
        day += timedelta(days=1)
    ordered = sorted(found.values(), key=lambda e: (e.date_filed, e.case, e.entry_id))
    grouped: dict[str, list[AiCaseActivityEntry]] = {}
    for entry in ordered:
        grouped.setdefault(entry.case, []).append(entry)
    return AiCasesUpdate(
        start=start,
        end=end,
        cases=tuple(
            (name, entries[0].category, tuple(entries)) for name, entries in grouped.items()
        ),
    )


def ai_cases_subject(update: AiCasesUpdate) -> str:
    """The update's title and email subject: one per span."""
    start, end = update.start, update.end
    if start == end:
        return f"AI cases in federal court: {start:%B} {start.day}, {start.year}"
    span = f"{start:%B} {start.day} \N{EN DASH} {end:%B} {end.day}, {end.year}"
    return f"AI cases in federal court: {span}"


def _escape(text: str) -> str:
    """Neutralize Markdown in a name, collapsing whitespace so it cannot open a block."""
    return re.sub(r"([\\`*_\[\]<>#|])", r"\\\1", " ".join(text.split()))


def _item(entry: AiCaseActivityEntry) -> str:
    where = f"{entry.court} {entry.docket_number}"
    if entry.entry_number is not None:
        where += f", entry {entry.entry_number}"
    when = f"{entry.date_filed:%b} {entry.date_filed.day}"
    label = KIND_LABELS[entry.kind]
    return f"- {when}: {label} ({_escape(where)}). [View on CourtListener]({entry.url})"


def render_ai_cases_update(update: AiCasesUpdate, *, title: bool = True) -> str:
    """The update as Markdown, ready for an email body; ``title=False`` leaves it to the subject."""
    lines = [f"# {ai_cases_subject(update)}", ""] if title else []
    lines += [_INTRO, ""]
    if update.empty:
        lines += ["No significant docket activity in this span.", ""]
    for name, category, entries in update.cases:
        kind_of_case = category.replace("-", " ").capitalize()
        lines += [f"## {_escape(name)}", "", f"*{_escape(kind_of_case)}*", ""]
        lines += [_item(entry) for entry in entries]
        lines += [""]
    lines += ["---", "", _FOOTER, ""]
    return "\n".join(lines)
