"""The weekly public update: one ISO week of the ledger, in plain words, for the email list.

A reader-facing digest rendered from **committed data only**, so the same tree
and the same week always render the same bytes. Two sections:

* **Resolved this week** — every event whose committed ``outcome.json`` has a
  ``resolved_at`` inside the week, beside each predictor's counted forward
  forecast on it.
* **New forecasts this week** — every counted forward forecast whose harness
  clock (:func:`fedcourtsai.integrity.cell_clock`) falls inside the week.

What counts as a forecast here is what the headline ledger counts and nothing
looser: the predictor's counted cell on the event
(:func:`fedcourtsai.store.ledger_counts`, so shakedown and de-counted cells
never appear), in ``forward`` mode, on an event that is not voided
(:func:`fedcourtsai.voids.is_voided`). Beside a resolution, a forecast is shown
only where it falls in the forward stratum as the scored boards draw it —
committed before the outcome existed, on an outcome that is not
mootness-basis, with no breach of its own forward claim, and not set aside
(:func:`fedcourtsai.set_aside.set_aside_reason`): a cell the record cannot show
was made before its outcome was public is left out of the default figures, so it
is never presented here as a forecast made in advance. The same rules keep a
cell stamped on or after its outcome, and a cell on a listed set-aside event,
out of the new-forecasts list.

The update **computes no score**. It states a forecast and an outcome side by
side and links the committed cell; any accuracy figure belongs to a committed
metrics artifact with its reading rule (``metrics/README.md``), never to this
page. It is display material: nothing scores it and no metric reads it.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Final

from . import set_aside
from .analytics import DEFAULT_REPO_TREE_URL
from .integrity import FORWARD, cell_clock, classify_stratum, forward_claim_breach
from .paths import CasePaths, EventPaths
from .schemas import Disposition, Judgment, Moment, Outcome, PredictableEvent, Stage
from .serialize import read_model, write_text
from .short_caption import short_caption
from .store import (
    LedgerPrediction,
    iter_predictions,
    latest_resolvable,
    ledger_counts,
    normalized_moment,
    normalized_stage,
    pre_mint_poll,
)
from .supremecourt import reserved_docket_number
from .voids import is_voided

#: The public repository tree every link in the update points into.
REPO_TREE_URL: Final = DEFAULT_REPO_TREE_URL

#: The repository-relative directory the ledger lives under, whatever local
#: ``data_root`` a render reads from — so a link never carries a local path.
_REPO_DATA_DIR: Final = Path("data")

#: The cell mode whose case was pending when it ran (``record/context.json``).
_FORWARD_MODE: Final = "forward"

_WEEK_RE: Final = re.compile(r"^(\d{4})-W(\d{2})$")

#: The site's running history of weekly updates, under the metrics root: one
#: Markdown file per ISO week, named ``<YYYY-Www>.md`` and written once.
ARCHIVE_DIR: Final = "updates"

#: The first week the email list was sent an update. The history starts here,
#: so it never reaches back before the list existed.
ARCHIVE_FIRST_WEEK: Final = "2026-W42"

_QUESTION: Final[dict[Stage, str]] = {
    Stage.cert: "Will the Court take the case?",
    Stage.interim: "Will the Court grant the application?",
    Stage.merits: "Will the Court reverse or vacate the decision below?",
}

#: What a forecast's ``probability`` is the chance of, by stage — the binary
#: the stage names (``Prediction.probability``).
_CHANCE_OF: Final[dict[Stage, str]] = {
    Stage.cert: "a grant",
    Stage.interim: "a grant",
    Stage.merits: "reversal or vacatur",
}

_CERT_WORDS: Final[dict[Disposition, str]] = {
    Disposition.granted: "Granted: the Court will hear the case",
    Disposition.denied: "Denied: the Court will not hear the case",
    Disposition.granted_in_part: "Granted in part",
    Disposition.gvr: "Granted, vacated and remanded to the court below",
    Disposition.summary_reversal: "Summarily reversed",
    Disposition.dismissed: "Dismissed",
    Disposition.withdrawn: "Withdrawn",
    Disposition.other: "Resolved another way",
}

_INTERIM_WORDS: Final[dict[Disposition, str]] = {
    Disposition.granted: "Application granted",
    Disposition.denied: "Application denied",
    Disposition.granted_in_part: "Application granted in part",
    Disposition.dismissed: "Application dismissed",
    Disposition.withdrawn: "Application withdrawn",
}

_MERITS_WORDS: Final[dict[Judgment, str]] = {
    Judgment.affirmed: "Affirmed",
    Judgment.reversed: "Reversed",
    Judgment.vacated: "Vacated",
    Judgment.affirmed_in_part: "Affirmed in part, reversed in part",
    Judgment.dig: "Dismissed as improvidently granted",
    Judgment.equally_divided: "Affirmed by an equally divided Court",
}

_MOMENT_WORDS: Final[dict[Moment, str]] = {
    Moment.distribution: "at its distribution for conference",
    Moment.relist: "after the Court first relisted it",
    Moment.cvsg: "after the Court invited the Solicitor General's views",
    Moment.sg_brief: "after the Solicitor General filed the invited brief",
    Moment.arrival: "when it was filed",
    Moment.response_requested: "after the Court requested a response",
    Moment.response_filed: "after the response was filed",
    Moment.grant: "after cert was granted",
    Moment.briefed: "after briefing closed",
}

_MOMENT_VALUES: Final = frozenset(m.value for m in Moment)

_FOOTER: Final = (
    "Every forecast above is a committed file in a public git ledger, made before "
    "the outcome existed; its timestamp in the ledger is the proof. A forecast is "
    "not an accuracy claim: scored results, and the rules for reading them, are on "
    "the [Results page](https://fedcourts.ai/results/). Each predictor is a "
    "frontier model given the same prompt and the same provisioned case record, "
    "though not at the same moment."
)

#: The two halves of a group's outcome count, by stage: the stage's usual
#: outcome, and everything else.
_USUAL_LABEL: Final[dict[Stage, tuple[str, str]]] = {
    Stage.cert: ("denied", "not denied"),
    Stage.interim: ("denied", "not denied"),
    Stage.merits: ("left standing", "reversed or vacated"),
}

#: What a lay reader needs to know to read a stage's percentages.
_STAGE_NOTE: Final[dict[Stage, str]] = {
    Stage.cert: " A grant, vacate and remand (GVR) counts as a grant.",
}


@dataclass(frozen=True)
class Forecast:
    """One predictor's counted forward forecast on an event."""

    predictor_id: str
    probability: float
    cell_path: str  # repository-relative, ``data/cases/...``


@dataclass(frozen=True)
class EventItem:
    """One event as the update shows it: the case, the question, its forecasts."""

    case_id: str
    event_id: str
    caption: str
    docket_number: str | None
    stage: Stage | None
    moment: Moment | None
    forecasts: tuple[Forecast, ...]
    event_path: str  # repository-relative event directory, ``data/cases/...``
    outcome: str | None = None  # the resolution in plain words; resolved items only
    resolved_at: date | None = None
    #: Whether the resolution is the stage's usual one — a denial, or an
    #: affirmance on the merits. Always true for an unresolved item.
    usual: bool = True


@dataclass(frozen=True)
class PublicUpdate:
    """One week of the ledger, ready to render."""

    week: str
    start: date  # Monday
    end: date  # Sunday, inclusive
    resolved: tuple[EventItem, ...]
    new: tuple[EventItem, ...]

    @property
    def empty(self) -> bool:
        """Nothing resolved and nothing newly forecast — a week the list skips."""
        return not self.resolved and not self.new


def week_bounds(week: str) -> tuple[date, date]:
    """Monday and Sunday of an ISO week spelled ``YYYY-Www``.

    Raises :class:`ValueError` on anything else, including a week number the
    year does not have.
    """
    match = _WEEK_RE.match(week)
    if match is None:
        raise ValueError(f"not an ISO week (YYYY-Www): {week!r}")
    monday = date.fromisocalendar(int(match.group(1)), int(match.group(2)), 1)
    return monday, monday + timedelta(days=6)


def last_complete_week(now: datetime) -> str:
    """The ISO week before the one ``now`` falls in, as ``YYYY-Www``."""
    year, week, _ = (now.astimezone(UTC).date() - timedelta(days=7)).isocalendar()
    return f"{year}-W{week:02d}"


def weeks_through(first: str, last: str) -> list[str]:
    """Every ISO week from ``first`` to ``last`` inclusive, oldest first (empty when reversed)."""
    monday, _ = week_bounds(first)
    final, _ = week_bounds(last)
    weeks: list[str] = []
    while monday <= final:
        year, week, _ = monday.isocalendar()
        weeks.append(f"{year}-W{week:02d}")
        monday += timedelta(days=7)
    return weeks


def archive_path(metrics_root: Path, week: str) -> Path:
    """Where ``week``'s update sits in the site's running history."""
    week_bounds(week)
    return metrics_root / ARCHIVE_DIR / f"{week}.md"


@dataclass(frozen=True)
class ArchiveResult:
    """What one archiving pass did, each tuple oldest week first."""

    written: tuple[str, ...]
    present: tuple[str, ...]
    empty: tuple[str, ...]


def archive_public_updates(data_root: Path, metrics_root: Path, through: str) -> ArchiveResult:
    """Write each missing week's update from :data:`ARCHIVE_FIRST_WEEK` through ``through``.

    A week already in the history is never re-rendered: its file is what the
    site first published, so neither a later resolution dated inside that week
    nor a later void or set-aside rewrites it, and a correction to a published
    week is a reviewed change, not this pass. A week with nothing to show gets
    no file, as it gets no email, and is looked at again on every pass: a week
    missed by a skipped run, or one that was empty and later gains a dated
    entry, is written when a pass first finds it non-empty, rendered from the
    ledger as it then stands.
    """
    written: list[str] = []
    present: list[str] = []
    empty: list[str] = []
    for week in weeks_through(ARCHIVE_FIRST_WEEK, through):
        path = archive_path(metrics_root, week)
        if path.exists():
            present.append(week)
            continue
        update = build_public_update(data_root, week)
        if update.empty:
            empty.append(week)
            continue
        write_text(path, render_public_update(update))
        written.append(week)
    return ArchiveResult(tuple(written), tuple(present), tuple(empty))


def build_public_update(data_root: Path, week: str) -> PublicUpdate:
    """Collect one ISO week of the committed ledger under ``data_root``."""
    start, end = week_bounds(week)
    rows = iter_predictions(data_root)
    kept = [
        row
        for row, counted in zip(rows, ledger_counts(rows), strict=True)
        if counted
        and row.prediction.context is not None
        and row.prediction.context.mode == _FORWARD_MODE
        and not is_voided(row.case_id, row.event_id)
    ]
    by_event: dict[tuple[str, str], list[LedgerPrediction]] = {}
    for row in _one_per_predictor(kept):
        by_event.setdefault((row.case_id, row.event_id), []).append(row)

    resolved: list[EventItem] = []
    new: list[EventItem] = []
    for event_rows in by_event.values():
        first = event_rows[0]
        event_paths = CasePaths(data_root, first.court_id, first.docket_id).event(first.event_id)
        event = read_model(event_paths.event_file, PredictableEvent)
        outcome = (
            read_model(event_paths.outcome, Outcome) if event_paths.outcome.is_file() else None
        )
        stage = normalized_stage(event.kind, event.stage)
        if outcome is not None and start <= outcome.resolved_at <= end:
            before = [
                row
                for row in event_rows
                if _in_advance(row, outcome) and not _set_aside(row, outcome, stage, event_paths)
            ]
            if before:
                resolved.append(_item(first, event, before, outcome=outcome))
        # A cell stamped on or after its outcome is retrospective whatever its
        # mode says, so it never appears as a forecast made in advance.
        fresh = [
            row
            for row in event_rows
            if start <= cell_clock(row.prediction).date() <= end
            and (outcome is None or _in_advance(row, outcome))
            and not _set_aside(row, outcome, stage, event_paths)
        ]
        if fresh:
            new.append(_item(first, event, fresh, outcome=None))

    return PublicUpdate(
        week=week,
        start=start,
        end=end,
        resolved=tuple(sorted(resolved, key=_order)),
        new=tuple(sorted(new, key=_order)),
    )


def _one_per_predictor(rows: Sequence[LedgerPrediction]) -> list[LedgerPrediction]:
    """Each predictor's one counted cell per event, in path order.

    Within a counting window every run is a candidate, so a predictor that
    re-ran inside its window holds several counted cells; the one shown is the
    one the scored boards pick (:func:`fedcourtsai.store.latest_resolvable`).
    """
    groups: dict[tuple[str, str, str], list[LedgerPrediction]] = {}
    for row in rows:
        groups.setdefault((row.case_id, row.event_id, row.predictor_id), []).append(row)
    chosen: list[LedgerPrediction] = []
    for group in groups.values():
        picked = latest_resolvable([row.prediction for row in group])
        chosen.append(next(row for row in group if row.prediction is picked))
    return chosen


def _in_advance(row: LedgerPrediction, outcome: Outcome) -> bool:
    """Whether a cell is a forecast made in advance of this outcome.

    The forward stratum as the scored boards draw it: never a mootness-basis
    outcome, which routes procedural whatever the timing; never a cell whose own
    record contradicts its forward claim
    (:func:`fedcourtsai.integrity.forward_claim_breach`); otherwise the timing
    rule, under which a cell stamped on or after the outcome's day is
    retrospective.
    """
    if outcome.disposition_basis == "mootness":
        return False
    if forward_claim_breach(row.prediction, outcome) is not None:
        return False
    return classify_stratum(cell_clock(row.prediction), outcome.resolved_at) == FORWARD


def _set_aside(
    row: LedgerPrediction, outcome: Outcome | None, stage: Stage | None, event_paths: EventPaths
) -> bool:
    """Whether the scored boards set this cell aside from their default figures.

    With an outcome, the boards' own rule (:func:`fedcourtsai.set_aside.set_aside_reason`),
    reading the cell's pre-mint poll as :func:`fedcourtsai.store.stratify` does.
    Behind :func:`_in_advance` only its listed reason can fire, since a cell
    stamped on its interim decision's day is already retrospective there; the
    whole rule is asked so the two stay in step if a reason is added. Without an
    outcome, only a listed event can be known to be set aside, since that reason
    keys on the event alone.
    """
    if outcome is None:
        return (row.case_id, row.event_id) in set_aside.SET_ASIDE_EVENTS
    cell_dir = event_paths.prediction_dir(row.predictor_id, row.run_id)

    def poll_state() -> str | None:
        poll = pre_mint_poll(cell_dir)
        return poll.state if poll is not None else None

    reason = set_aside.set_aside_reason(
        row.case_id, row.event_id, row.prediction, outcome, stage, poll_state
    )
    return reason is not None


def _order(item: EventItem) -> tuple[str, str, str]:
    return (item.caption.casefold(), item.case_id, item.event_id)


def _item(
    first: LedgerPrediction,
    event: PredictableEvent,
    rows: Sequence[LedgerPrediction],
    *,
    outcome: Outcome | None,
) -> EventItem:
    stage = normalized_stage(event.kind, event.stage)
    declared = normalized_moment(stage, event.moment)
    moment = Moment(declared) if declared in _MOMENT_VALUES else None
    forecasts = tuple(
        sorted(
            (
                Forecast(
                    predictor_id=row.predictor_id,
                    probability=row.prediction.probability,
                    cell_path=_repo_cell_path(row).as_posix(),
                )
                for row in rows
            ),
            key=lambda f: (f.predictor_id, f.cell_path),
        )
    )
    return EventItem(
        case_id=first.case_id,
        event_id=first.event_id,
        caption=short_caption(event.title) or event.title,
        docket_number=reserved_docket_number(first.docket_id)
        if first.court_id == "scotus"
        else None,
        stage=stage,
        moment=moment,
        forecasts=forecasts,
        event_path=CasePaths(_REPO_DATA_DIR, first.court_id, first.docket_id)
        .event(first.event_id)
        .base.as_posix(),
        outcome=_outcome_words(stage, outcome) if outcome is not None else None,
        usual=_usual(stage, outcome) if outcome is not None else True,
        resolved_at=outcome.resolved_at if outcome is not None else None,
    )


def _repo_cell_path(row: LedgerPrediction) -> Path:
    """The cell's run directory as the public repository spells it."""
    paths = CasePaths(_REPO_DATA_DIR, row.court_id, row.docket_id).event(row.event_id)
    return paths.prediction_dir(row.predictor_id, row.run_id)


def _usual(stage: Stage | None, outcome: Outcome) -> bool:
    if stage == Stage.merits:
        return outcome.judgment is None or outcome.judgment in {
            Judgment.affirmed,
            Judgment.dig,
            Judgment.equally_divided,
        }
    return outcome.actual_disposition == Disposition.denied


def _outcome_words(stage: Stage | None, outcome: Outcome) -> str:
    if stage == Stage.merits:
        return _MERITS_WORDS[outcome.judgment] if outcome.judgment is not None else "Decided"
    if stage == Stage.interim:
        return _INTERIM_WORDS.get(outcome.actual_disposition, "Resolved another way")
    return _CERT_WORDS[outcome.actual_disposition]


def _escape(text: str) -> str:
    """Neutralize the Markdown a case caption could otherwise trigger.

    Whitespace runs, line breaks among them, collapse to one space first, so a
    caption cannot open a block of its own (a heading, a rule, a list).
    """
    return re.sub(r"([\\`*_\[\]<>#|])", r"\\\1", " ".join(text.split()))


def _heading(stage: Stage | None, moment: Moment | None) -> str:
    """One group's heading: the question, then when it was forecast."""
    question = _QUESTION.get(stage, "Other events") if stage is not None else "Other events"
    when = _MOMENT_WORDS.get(moment) if moment is not None else None
    return f"### {question} Forecast {when}" if when else f"### {question}"


def _chance_of(stage: Stage | None) -> str:
    return _CHANCE_OF.get(stage, "the outcome") if stage is not None else "the outcome"


def _item_line(item: EventItem, repo_url: str) -> str:
    """One event on one line: case, outcome if resolved, each forecast, the ledger link."""
    docket = f" (No. {item.docket_number})" if item.docket_number else ""
    outcome = f" — {item.outcome}." if item.outcome is not None else "."
    forecasts = " · ".join(
        f"{forecast.predictor_id} {_percent(forecast.probability)}" for forecast in item.forecasts
    )
    return (
        f"- **{_escape(item.caption)}**{docket}{outcome} Forecasts: {forecasts}"
        f" ([ledger]({repo_url}/{item.event_path}))"
    )


def _percent(probability: float) -> str:
    """A probability as a whole percentage, never rounded to certainty."""
    if probability < 0.005:
        return "<1%"
    if probability > 0.995:
        return ">99%"
    return f"{round(probability * 100)}%"


def _outcome_count(stage: Stage | None, members: Sequence[EventItem]) -> str:
    """How a resolved group split, so the ordering below cannot hide the base rate."""
    usual_label, other_label = (
        _USUAL_LABEL.get(stage, ("usual", "other")) if stage is not None else ("usual", "other")
    )
    usual = sum(1 for item in members if item.usual)
    return f"{len(members)} resolved: {len(members) - usual} {other_label}, {usual} {usual_label}. "


def _group_order(stage: Stage | None, moment: Moment | None) -> tuple[int, str]:
    stages = list(Stage)
    return (
        stages.index(stage) if stage is not None else len(stages),
        moment.value if moment is not None else "",
    )


def _section(title: str, items: Sequence[EventItem], repo_url: str, *, resolved: bool) -> list[str]:
    """A section's lines, grouped by question and moment.

    Within a group, the events whose outcome is not the stage's usual one (a
    grant rather than a denial) come first, so a long conference's denials do
    not bury the cases that went the other way.
    """
    groups: dict[tuple[Stage | None, Moment | None], list[EventItem]] = {}
    for item in items:
        groups.setdefault((item.stage, item.moment), []).append(item)
    lines = [f"## {title}", ""]
    for stage, moment in sorted(groups, key=lambda key: _group_order(*key)):
        members = groups[(stage, moment)]
        lines += [
            _heading(stage, moment),
            "",
            (_outcome_count(stage, members) if resolved else "")
            + f"Each percentage is a model's committed chance of {_chance_of(stage)}."
            + (_STAGE_NOTE.get(stage, "") if stage is not None else ""),
            "",
        ]
        usual = [item for item in members if item.usual]
        lines += [_item_line(item, repo_url) for item in members if not item.usual]
        lines += [_item_line(item, repo_url) for item in usual]
        lines.append("")
    return lines


def public_update_subject(update: PublicUpdate) -> str:
    """The update's title, which is also the email's subject: one per ISO week."""
    start, end = update.start, update.end
    span = f"{start:%B} {start.day} \N{EN DASH} {end:%B} {end.day}, {end.year}"
    return f"FedCourtsAI weekly update: {span}"


def render_public_update(
    update: PublicUpdate, *, repo_url: str = REPO_TREE_URL, title: bool = True
) -> str:
    """The update as Markdown, ready for an email body.

    ``title=False`` drops the heading, for a channel that carries the title as
    the message's subject instead.
    """
    lines = [f"# {public_update_subject(update)}", ""] if title else []
    if update.empty:
        lines += ["Nothing resolved and no new forecasts were committed this week.", ""]
    if update.resolved:
        lines += _section(
            "Resolved this week, with forecasts made in advance",
            update.resolved,
            repo_url,
            resolved=True,
        )
    if update.new:
        lines += _section("New forecasts this week", update.new, repo_url, resolved=False)
    lines += ["---", "", _FOOTER, ""]
    return "\n".join(lines)
