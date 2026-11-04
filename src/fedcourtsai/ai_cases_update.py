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

A ruling with a committed model summary (``data/ai-cases/summaries/``,
:mod:`fedcourtsai.ai_rulings`) carries it under its item, quoted and labeled
with the model that wrote it. The summary is written from the ruling's own
text, so this is the one place the update says what a ruling decided; an item
without one renders as before.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Final

from .ai_activity import ACTIVITY_DIR
from .ai_rulings import RulingSummary, committed_summaries
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
    # The committed ruling summaries of the span's items, by entry id.
    summaries: Mapping[int, RulingSummary] = field(default_factory=dict)

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
    written = committed_summaries(data_root) if found else {}
    return AiCasesUpdate(
        start=start,
        end=end,
        cases=tuple(
            (name, entries[0].category, tuple(entries)) for name, entries in grouped.items()
        ),
        summaries={k: v for k, v in written.items() if k in found},
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


def _summary(summary: RulingSummary) -> list[str]:
    """A ruling's summary as a quote under its list item, labeled with its model."""
    paragraphs = [_escape(summary.headline)]
    paragraphs += [_escape(p) for p in re.split(r"\n\s*\n", summary.decided) if p.strip()]
    paragraphs.append(
        f"*Summary written by {_escape(summary.model)} from the ruling's own text. "
        + "It may contain errors; the ruling is the authority.*"
    )
    lines: list[str] = []
    for paragraph in paragraphs:
        lines += ["  >", f"  > {paragraph}"] if lines else [f"  > {paragraph}"]
    return ["", *lines, ""]


def render_ai_cases_update(update: AiCasesUpdate, *, title: bool = True) -> str:
    """The update as Markdown, ready for an email body; ``title=False`` leaves it to the subject."""
    lines = [f"# {ai_cases_subject(update)}", ""] if title else []
    lines += [_INTRO, ""]
    if update.empty:
        lines += ["No significant docket activity in this span.", ""]
    for name, category, entries in update.cases:
        kind_of_case = category.replace("-", " ").capitalize()
        lines += [f"## {_escape(name)}", "", f"*{_escape(kind_of_case)}*", ""]
        for entry in entries:
            lines.append(_item(entry))
            summary = update.summaries.get(entry.entry_id)
            if summary is not None:
                lines += _summary(summary)
        lines += [""]
    lines += ["---", "", _FOOTER, ""]
    return "\n".join(lines)
