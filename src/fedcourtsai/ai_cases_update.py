"""The AI-cases update: the watchlist's significant docket activity over a span, for email.

Rendered from the committed daily activity records
(``data/ai-cases/activity/<YYYY-MM-DD>.json``, :mod:`fedcourtsai.ai_activity`)
and the watchlist (``config/ai-watchlist.yaml``): no corpus, no model call, so
the same tree and span render the same bytes. Each item is a date, the kind of
entry the activity rule assigned (with the principal motion it names, where it
names one), the court and docket number, and a link to the entry on
CourtListener; no docket text is quoted, so the update points to the public
record rather than copying it.

A span is either one day or one ISO week. A count by kind opens it. Its cases
follow in sections by the weightiest item each case has: rulings (opinions,
judgments and rulings on a motion), then appeals and settlements, then new
filings (complaints and motions). A case keeps all its items together under
its one section; within a section, cases come in the order of their first
item. Each case is introduced by its category, its court and the watchlist's
own one-line account of why it is listed, which is the project's sentence, not
the docket's.

A span with nothing recorded renders as a short quiet note, so subscribers
hear every week that the feed is alive.

A last *Newly available* section lists, by case, the entries filed earlier
whose documents became readable on CourtListener in the span (the record's
``available`` list, :data:`fedcourtsai.ai_activity.AVAILABILITY_RULE`), at most
:data:`AVAILABLE_PER_CASE` per case, the rest counted beside a link to the
docket, since a sealed summary-judgment record unsealed at once can make
dozens of entries readable in a day.

A ruling with a committed model summary (``data/ai-cases/summaries/``,
:mod:`fedcourtsai.ai_rulings`) carries it under its item, quoted and labeled
with the model that wrote it. The summary is written from the ruling's own
text, so this is the one place the update says what a ruling decided; an item
without one carries only its line.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Final

from .ai_activity import ACTIVITY_DIR, merge_available
from .ai_rulings import RulingSummary, committed_summaries
from .ai_watchlist import AiWatchlist
from .schemas import AiCaseActivity, AiCaseActivityEntry, AiCaseAvailableEntry
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

#: The principal motions in the reader's words, completing "a motion …".
MOTION_LABELS: Final = {
    "partial-summary-judgment": "for partial summary judgment",
    "summary-judgment": "for summary judgment",
    "judgment-on-the-pleadings": "for judgment on the pleadings",
    "dismiss": "to dismiss",
    "class-certification": "for class certification",
    "preliminary-injunction": "for a preliminary injunction",
    "temporary-restraining-order": "for a temporary restraining order",
    "compel-arbitration": "to compel arbitration",
    "transfer": "to transfer",
    "stay-pending-appeal": "for a stay pending appeal",
}

#: The update's sections, weightiest first, and the kinds each holds.
SECTIONS: Final[tuple[tuple[str, frozenset[str]], ...]] = (
    ("Rulings", frozenset({"opinion", "judgment", "ruling"})),
    ("Appeals and settlements", frozenset({"appeal", "resolution"})),
    ("New filings", frozenset({"complaint", "motion"})),
)

#: The opening count's groups, in order, as (singular, plural) and the kinds counted.
_TALLY: Final[tuple[tuple[str, str, frozenset[str]], ...]] = (
    ("ruling", "rulings", frozenset({"opinion", "judgment", "ruling"})),
    ("appeal", "appeals", frozenset({"appeal"})),
    ("settlement or dismissal", "settlements or dismissals", frozenset({"resolution"})),
    ("new filing", "new filings", frozenset({"complaint", "motion"})),
)

#: The most newly readable entries listed for one case in one update; the rest
#: are counted, with a link to the docket.
AVAILABLE_PER_CASE: Final = 5

_AVAILABLE_INTRO: Final = (
    "Documents filed earlier that became readable on CourtListener in this span."
)

#: CourtListener court ids in the standard short form readers know. An id
#: missing here renders as the id itself; a test keeps every watchlist court here.
COURT_NAMES: Final = {
    "scotus": "U.S. Supreme Court",
    "jpml": "J.P.M.L.",
    "ca1": "1st Cir.",
    "ca2": "2d Cir.",
    "ca3": "3d Cir.",
    "ca4": "4th Cir.",
    "ca5": "5th Cir.",
    "ca6": "6th Cir.",
    "ca7": "7th Cir.",
    "ca8": "8th Cir.",
    "ca9": "9th Cir.",
    "ca10": "10th Cir.",
    "ca11": "11th Cir.",
    "cadc": "D.C. Cir.",
    "cafc": "Fed. Cir.",
    "cand": "N.D. Cal.",
    "cacd": "C.D. Cal.",
    "casd": "S.D. Cal.",
    "caed": "E.D. Cal.",
    "nysd": "S.D.N.Y.",
    "nyed": "E.D.N.Y.",
    "nynd": "N.D.N.Y.",
    "nywd": "W.D.N.Y.",
    "dcd": "D.D.C.",
    "ded": "D. Del.",
    "mad": "D. Mass.",
    "njd": "D.N.J.",
    "paed": "E.D. Pa.",
    "pawd": "W.D. Pa.",
    "pamd": "M.D. Pa.",
    "flnd": "N.D. Fla.",
    "flmd": "M.D. Fla.",
    "flsd": "S.D. Fla.",
    "txed": "E.D. Tex.",
    "txnd": "N.D. Tex.",
    "txsd": "S.D. Tex.",
    "txwd": "W.D. Tex.",
    "tnmd": "M.D. Tenn.",
    "tned": "E.D. Tenn.",
    "tnwd": "W.D. Tenn.",
    "ilnd": "N.D. Ill.",
    "wawd": "W.D. Wash.",
    "waed": "E.D. Wash.",
    "vaed": "E.D. Va.",
    "gand": "N.D. Ga.",
    "cod": "D. Colo.",
    "azd": "D. Ariz.",
    "nvd": "D. Nev.",
    "ord": "D. Or.",
    "utd": "D. Utah",
    "mnd": "D. Minn.",
    "mied": "E.D. Mich.",
    "ohnd": "N.D. Ohio",
    "ohsd": "S.D. Ohio",
    "mdd": "D. Md.",
    "ctd": "D. Conn.",
}

SITE_URL: Final = "https://fedcourts.ai/"

_INTRO: Final = (
    "New rulings and major filings in the {cases} FedCourtsAI "
    + "follows, read from the public docket. Each item links to the record on CourtListener."
)
_QUIET: Final = "No new rulings or major filings {span} in the {cases} FedCourtsAI follows."
_FOOTER: Final = (
    "More from FedCourtsAI, including its Supreme Court forecasts, at "
    + f"[fedcourts.ai]({SITE_URL}). "
    + "Docket data from [CourtListener](https://www.courtlistener.com/), a project of "
    + "Free Law Project. The list of cases and the rule that picks which entries "
    + "appear are public in the "
    + "[FedCourtsAI repository](https://github.com/ModelMirrorAI/fedcourtsai/blob/main/config/ai-watchlist.yaml)."
)


@dataclass(frozen=True)
class CaseIntro:
    """What the update says about a listed case before its items."""

    court: str
    why: str


@dataclass(frozen=True)
class AiCasesUpdate:
    start: date
    end: date
    # Each case's items, cases in the order of their first item.
    cases: tuple[tuple[str, str, tuple[AiCaseActivityEntry, ...]], ...]
    # The committed ruling summaries of the span's items, by entry id.
    summaries: Mapping[int, RulingSummary] = field(default_factory=dict)
    # Entries filed earlier whose documents became readable in the span, by
    # case, cases in the order of their first entry.
    available: tuple[tuple[str, str, tuple[AiCaseAvailableEntry, ...]], ...] = ()
    # How many cases the watchlist follows, and each listed case's introduction
    # by name; empty when rendered without a watchlist.
    followed: int = 0
    intros: Mapping[str, CaseIntro] = field(default_factory=dict)

    @property
    def empty(self) -> bool:
        return not self.cases and not self.available

    @property
    def items(self) -> int:
        return sum(len(entries) for _, _, entries in (*self.cases, *self.available))


def build_ai_cases_update(
    data_root: Path, start: date, end: date, watchlist: AiWatchlist | None = None
) -> AiCasesUpdate:
    """The span's items from the activity records of the days ``start`` through ``end``."""
    found: dict[int, AiCaseActivityEntry] = {}
    readable: dict[int, AiCaseAvailableEntry] = {}
    day = start
    while day <= end:
        path = data_root / ACTIVITY_DIR / f"{day.isoformat()}.json"
        if path.is_file():
            record = read_model(path, AiCaseActivity)
            for entry in record.entries:
                found.setdefault(entry.entry_id, entry)
            for later in record.available:
                readable[later.entry_id] = merge_available(readable.get(later.entry_id), later)
        day += timedelta(days=1)
    by_case: dict[str, list[AiCaseAvailableEntry]] = {}
    for later in sorted(readable.values(), key=lambda e: (e.date_filed, e.case, e.entry_id)):
        by_case.setdefault(later.case, []).append(later)
    ordered = sorted(found.values(), key=lambda e: (e.date_filed, e.case, e.entry_id))
    grouped: dict[str, list[AiCaseActivityEntry]] = {}
    for entry in ordered:
        grouped.setdefault(entry.case, []).append(entry)
    written = committed_summaries(data_root) if found or readable else {}
    listed = watchlist.cases if watchlist is not None else []
    return AiCasesUpdate(
        start=start,
        end=end,
        cases=tuple(
            (name, entries[0].category, tuple(entries)) for name, entries in grouped.items()
        ),
        summaries={k: v for k, v in written.items() if k in found or k in readable},
        available=tuple(
            (name, entries[0].category, tuple(entries)) for name, entries in by_case.items()
        ),
        followed=len(listed),
        intros={case.name: CaseIntro(court=case.court, why=case.why) for case in listed},
    )


def ai_cases_subject(update: AiCasesUpdate) -> str:
    """The update's title and email subject: one per span."""
    start, end = update.start, update.end
    if start == end:
        return f"AI cases in federal court: {start:%B} {start.day}, {start.year}"
    span = f"{start:%B} {start.day} \N{EN DASH} {end:%B} {end.day}, {end.year}"
    return f"AI cases in federal court: {span}"


def court_name(court: str) -> str:
    """A CourtListener court id in its standard short form, else the id itself."""
    return COURT_NAMES.get(court, court)


def _escape(text: str) -> str:
    """Neutralize Markdown in a name, collapsing whitespace so it cannot open a block."""
    return re.sub(r"([\\`*_\[\]<>#|])", r"\\\1", " ".join(text.split()))


def item_label(entry: AiCaseActivityEntry) -> str:
    """The entry's kind in the reader's words, naming its principal motion where known."""
    motion = MOTION_LABELS.get(entry.motion or "")
    if motion is None:
        return KIND_LABELS[entry.kind]
    if entry.kind == "motion":
        return f"Motion {motion} filed"
    if entry.kind == "ruling":
        return f"Ruling on a motion {motion}"
    return f"{KIND_LABELS[entry.kind]} on a motion {motion}"


def _item(entry: AiCaseActivityEntry) -> str:
    where = f"{court_name(entry.court)} {entry.docket_number}"
    if entry.entry_number is not None:
        where += f", entry {entry.entry_number}"
    when = f"{entry.date_filed:%b} {entry.date_filed.day}"
    return f"- {when}: {item_label(entry)} ({_escape(where)}). [View on CourtListener]({entry.url})"


#: A Claude model id: family, then a major and an optional minor version.
_CLAUDE_MODEL: Final = re.compile(r"claude-(opus|sonnet|haiku|fable)-(\d+)(?:-(\d{1,2}))?")


def model_name(model: str) -> str:
    """The model in the reader's words: ``claude-sonnet-5-5`` reads "Claude Sonnet 5.5".

    An id of another shape is shown as recorded, since a guessed name could
    credit the wrong model.
    """
    match = _CLAUDE_MODEL.fullmatch(model.strip())
    if match is None:
        return model
    family, major, minor = match.groups()
    return f"Claude {family.capitalize()} {major}" + (f".{minor}" if minor else "")


def _summary(summary: RulingSummary) -> list[str]:
    """A ruling's summary as a quote under its list item, labeled with its model."""
    paragraphs = [_escape(summary.headline)]
    paragraphs += [_escape(p) for p in re.split(r"\n\s*\n", summary.decided) if p.strip()]
    paragraphs.append(
        f"*Summary written by {_escape(model_name(summary.model))} from the ruling's own text. "
        + "It may contain errors; the ruling is the authority.*"
    )
    lines: list[str] = []
    for paragraph in paragraphs:
        lines += ["  >", f"  > {paragraph}"] if lines else [f"  > {paragraph}"]
    return ["", *lines, ""]


def tally(update: AiCasesUpdate) -> str:
    """The span's items counted by kind, weightiest first: "2 rulings · 1 appeal"."""
    kinds: Counter[str] = Counter(entry.kind for _, _, entries in update.cases for entry in entries)
    parts = []
    for one, many, counted in _TALLY:
        n = sum(kinds[kind] for kind in counted)
        if n:
            parts.append(f"{n} {one if n == 1 else many}")
    readable = sum(len(entries) for _, _, entries in update.available)
    if readable:
        parts.append(f"{readable} newly readable")
    return " \N{MIDDLE DOT} ".join(parts)


def section_of(entries: tuple[AiCaseActivityEntry, ...]) -> int:
    """The index in :data:`SECTIONS` of the weightiest section a case's items reach."""
    return min(
        index
        for index, (_, kinds) in enumerate(SECTIONS)
        for entry in entries
        if entry.kind in kinds
    )


def _case_heading(update: AiCasesUpdate, name: str, category: str) -> list[str]:
    """A case's heading and the line that introduces it."""
    intro = update.intros.get(name)
    about = [category.replace("-", " ").capitalize()]
    if intro is not None:
        about += [court_name(intro.court), intro.why]
    return [f"### {_escape(name)}", "", f"*{_escape(' · '.join(about))}*", ""]


def _case_lines(
    update: AiCasesUpdate, name: str, category: str, entries: tuple[AiCaseActivityEntry, ...]
) -> list[str]:
    lines = _case_heading(update, name, category)
    for entry in entries:
        lines.append(_item(entry))
        summary = update.summaries.get(entry.entry_id)
        if summary is not None:
            lines += _summary(summary)
    return [*lines, ""]


def available_line(entry: AiCaseAvailableEntry) -> str:
    """What became readable, in the reader's words: "Ruling … of Oct 3 is now readable"."""
    when = f"{entry.date_filed:%b} {entry.date_filed.day}"
    motion = MOTION_LABELS.get(entry.motion or "")
    on = f" on a motion {motion}" if motion else ""
    with_motion = f" with a motion {motion}" if motion else ""
    n = entry.documents
    if entry.kind == "exhibits":
        what = "exhibit" if n == 1 else "exhibits"
        return f"{n} {what} filed {when}{with_motion} {'is' if n == 1 else 'are'} now readable"
    if entry.kind == "unsealed":
        count = "1 document" if n == 1 else f"{n} documents"
        return f"Unsealed or public version of a filing of {when}{on} ({count}) now readable"
    if entry.kind == "transcript":
        return f"Transcript filed {when} is now readable"
    if entry.kind == "ruling":
        label = f"Ruling on a motion {motion}" if motion else "Ruling on a motion"
    else:
        label = KIND_LABELS[entry.kind] + on
    return f"{label} of {when} is now readable"


def _available_lines(
    update: AiCasesUpdate, name: str, category: str, entries: tuple[AiCaseAvailableEntry, ...]
) -> list[str]:
    lines = _case_heading(update, name, category)
    listed = {e.entry_id for _, _, items in update.cases for e in items}
    for entry in entries[:AVAILABLE_PER_CASE]:
        where = f"{court_name(entry.court)} {entry.docket_number}"
        if entry.entry_number is not None:
            where += f", entry {entry.entry_number}"
        lines.append(
            f"- {available_line(entry)} ({_escape(where)}). [View on CourtListener]({entry.url})"
        )
        # A ruling also listed above already carries its summary there.
        summary = update.summaries.get(entry.entry_id)
        if summary is not None and entry.entry_id not in listed:
            lines += _summary(summary)
    rest = entries[AVAILABLE_PER_CASE:]
    if rest:
        dockets = {e.docket_id for e in rest}
        docket = f"https://www.courtlistener.com/docket/{rest[0].docket_id}/"
        link = f" [View the docket]({docket})" if len(dockets) == 1 else ""
        lines.append(f"- And {len(rest)} more in this case.{link}")
    return [*lines, ""]


def render_ai_cases_update(update: AiCasesUpdate, *, title: bool = True) -> str:
    """The update as Markdown, ready for an email body; ``title=False`` leaves it to the subject."""
    lines = [f"# {ai_cases_subject(update)}", ""] if title else []
    n = update.followed
    followed = f"{n} federal AI case{'' if n == 1 else 's'}" if n else "federal AI cases"
    if update.empty:
        span = "this week" if (update.end - update.start).days == 6 else "in this span"
        lines += [_QUIET.format(span=span, cases=followed), ""]
    else:
        lines += [_INTRO.format(cases=followed), "", f"**This update:** {tally(update)}", ""]
    for index, (heading, _) in enumerate(SECTIONS):
        cases = [case for case in update.cases if section_of(case[2]) == index]
        if not cases:
            continue
        lines += [f"## {heading}", ""]
        for name, category, entries in cases:
            lines += _case_lines(update, name, category, entries)
    if update.available:
        lines += ["## Newly available", "", _AVAILABLE_INTRO, ""]
        for name, category, readable in update.available:
            lines += _available_lines(update, name, category, readable)
    lines += ["---", "", _FOOTER, ""]
    return "\n".join(lines)
