"""The weekly Court update: what the Supreme Court did in one ISO week, for the email list.

The companion of the forecasts update (:mod:`fedcourtsai.public_update`), with
the two kept apart on purpose: this one says what happened at the Court and
carries **no forecast**, so a reader who wants the Court's week does not have
to read past the models' numbers, and a reader of the numbers gets them in
their own email. Rendered from **committed data only**, so the same tree and
the same week always render the same bytes.

It covers the cases the ledger follows, which is every case the pipeline
opened an event on, not the Court's whole docket. Four parts:

* **Decisions** — each case whose committed ``outcome.json`` has a
  ``resolved_at`` inside the week, once per stage however many forecast
  moments the stage's question was opened at: argued cases decided, emergency
  applications ruled on, and petitions for review granted or denied. Every
  decision that is not the stage's usual one (a grant, a reversal) is listed.
  The usual ones (denials) are counted, and where there are more than
  :data:`LISTED_TOP` of them only that many are listed.
* **Other actions** — the Court's steps short of a decision, read from the
  events the pipeline opens on them (``opened_at`` inside the week): an
  argument heard, a call for the Solicitor General's views, a first relist, a
  response requested.
* **New filings** — the emergency applications and petitions that arrived in
  the week and that the ledger opened an event on at arrival, less any the
  Court also decided inside the week, which is listed once, as a decision.
* **Ahead** — the Court's first conference after the week, from the committed
  term calendar (:mod:`fedcourtsai.term_calendar`).

Each case carries the one-sentence *In brief* line of its newest committed
summary (``docs/case-summaries.md``) where it has one, and a link to the
Court's own docket page where its docket number is known.

Where a list is cut to :data:`LISTED_TOP`, the cases kept are the ones the
models rated the biggest, by the mean ``big_case_score`` of the counted forward
forecasts on the case. That stakes read is a panel opinion about which cases
matter, used here as it is in the forecasts update: it picks which lines a
reader sees and nothing else, it is never shown, and every count still covers
the whole group.

A voided event (:func:`fedcourtsai.voids.is_voided`) is left out: its committed
outcome describes another petition, so it is not this case's news. The update
is display material: nothing scores it and no metric reads it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Final

from pydantic import ValidationError

from .paths import CasePaths, EventPaths
from .public_update import escape_text, outcome_words, usual_outcome, week_bounds
from .schemas import Moment, Outcome, PredictableEvent, Stage
from .serialize import read_model
from .short_caption import short_caption
from .store import iter_predictions, ledger_counts, normalized_moment, normalized_stage
from .summaries import SummaryFormatError, newest_summary, parse_summary, split_sections
from .supremecourt import docket_page_url, reserved_docket_number
from .term_calendar import committed_calendar, next_conference
from .voids import is_voided

#: The one court this update covers.
_COURT: Final = "scotus"

#: The cell mode whose case was pending when it ran (``record/context.json``).
_FORWARD_MODE: Final = "forward"

#: How many cases a list that is cut keeps: a group's usual decisions, and each
#: group of new filings.
LISTED_TOP: Final = 10

#: The summary section whose one sentence introduces a case.
_IN_BRIEF: Final = "## In brief"

#: The decision groups, in the order a reader looks for them.
_STAGE_ORDER: Final = (Stage.merits, Stage.interim, Stage.cert)

_DECISION_HEADING: Final[dict[Stage, str]] = {
    Stage.merits: "Argued cases decided",
    Stage.interim: "Emergency applications",
    Stage.cert: "Petitions for review",
}

#: The two halves of a group's count: the stage's usual decision, and the rest.
_COUNT_LABEL: Final[dict[Stage, tuple[str, str]]] = {
    Stage.merits: ("left standing", "reversed or vacated"),
    Stage.interim: ("denied", "another outcome"),
    Stage.cert: ("denied", "another outcome"),
}

#: The Court's steps short of a decision, by the forecast moment the pipeline
#: opens on each, in the order they are listed.
_ACTION_HEADING: Final[dict[Moment, str]] = {
    Moment.argued: "Argued",
    Moment.cvsg: "Solicitor General's views invited",
    Moment.relist: "Relisted for the first time",
    Moment.response_requested: "Response requested",
}

#: The arrivals listed as new filings, by stage.
_FILING_HEADING: Final[dict[Stage, str]] = {
    Stage.interim: "Emergency applications filed",
    Stage.cert: "Newly filed petitions FedCourtsAI is following",
}

_MOMENT_VALUES: Final = frozenset(m.value for m in Moment)

_FOOTER: Final = (
    "This update covers the cases FedCourtsAI follows, not every matter on the "
    "Court's docket, and is generated from the project's public ledger. Each "
    "one-sentence case description is written by an AI model from the case's "
    "filings and is not reviewed by a person; the Court's docket, linked beside "
    "each case, is the authority. The models' forecasts on these cases go out in "
    "a separate weekly email, which you can add or drop in your subscription "
    "preferences, and are on [fedcourts.ai](https://fedcourts.ai/)."
)


@dataclass(frozen=True)
class CourtCase:
    """One case as the update names it."""

    case_id: str
    caption: str
    docket_number: str | None
    #: The *In brief* sentence of the case's newest committed summary.
    brief: str | None
    #: The mean ``big_case_score`` of the case's counted forward forecasts. It
    #: picks which cases a cut list keeps and is never shown.
    stakes: float | None


@dataclass(frozen=True)
class Decision:
    """One case decided at one stage."""

    case: CourtCase
    stage: Stage
    words: str
    #: Whether the decision is the stage's usual one — a denial, or an
    #: affirmance on the merits.
    usual: bool
    resolved_at: date


@dataclass(frozen=True)
class Action:
    """One step the Court took on a case short of deciding it."""

    case: CourtCase
    moment: Moment


@dataclass(frozen=True)
class Filing:
    """One application or petition that arrived."""

    case: CourtCase
    stage: Stage


@dataclass(frozen=True)
class CourtUpdate:
    """One week at the Court, ready to render."""

    week: str
    start: date  # Monday
    end: date  # Sunday, inclusive
    decisions: tuple[Decision, ...]
    actions: tuple[Action, ...]
    filings: tuple[Filing, ...]
    #: The Court's first scheduled conference after the week, where the
    #: committed term calendar names one.
    next_conference: date | None

    @property
    def empty(self) -> bool:
        """Nothing decided, done or filed — a week the list skips."""
        return not (self.decisions or self.actions or self.filings)


def _stakes(data_root: Path) -> dict[str, float]:
    """Each case's mean big-case score over its counted forward forecasts."""
    rows = iter_predictions(data_root)
    reads: dict[str, list[float]] = {}
    for row, counted in zip(rows, ledger_counts(rows), strict=True):
        score = row.prediction.big_case_score
        context = row.prediction.context
        if (
            counted
            and score is not None
            and context is not None
            and context.mode == _FORWARD_MODE
            and not is_voided(row.case_id, row.event_id)
        ):
            reads.setdefault(row.case_id, []).append(score)
    return {case_id: sum(scores) / len(scores) for case_id, scores in reads.items()}


def _brief(data_root: Path, docket_id: int) -> str | None:
    """The *In brief* sentence of the case's newest committed summary, if it reads."""
    path = newest_summary(data_root, _COURT, docket_id)
    if path is None:
        return None
    try:
        _, body = parse_summary(path.read_text(encoding="utf-8"))
    except (OSError, SummaryFormatError):
        return None
    headings, sections, _ = split_sections(body)
    for heading, text in zip(headings, sections, strict=True):
        if heading == _IN_BRIEF:
            return " ".join(text.split()) or None
    return None


def _event_dirs(data_root: Path) -> list[tuple[int, EventPaths]]:
    """Every committed event directory of the Court's cases, in path order."""
    court_dir = data_root / "cases" / _COURT
    if not court_dir.is_dir():
        return []
    found: list[tuple[int, EventPaths]] = []
    for case_dir in sorted(court_dir.iterdir()):
        if not case_dir.name.isdigit():
            continue
        docket_id = int(case_dir.name)
        events_dir = CasePaths(data_root, _COURT, docket_id).events_dir
        if not events_dir.is_dir():
            continue
        found.extend(
            (docket_id, EventPaths(event_dir))
            for event_dir in sorted(events_dir.iterdir())
            if event_dir.is_dir()
        )
    return found


def build_court_update(data_root: Path, week: str) -> CourtUpdate:
    """Collect one ISO week of the Court's actions from the ledger under ``data_root``."""
    start, end = week_bounds(week)
    stakes: Mapping[str, float] | None = None
    cases: dict[int, CourtCase] = {}

    def case_of(docket_id: int, event: PredictableEvent) -> CourtCase:
        nonlocal stakes
        if docket_id not in cases:
            if stakes is None:
                stakes = _stakes(data_root)
            case_id = f"{_COURT}/{docket_id}"
            cases[docket_id] = CourtCase(
                case_id=case_id,
                caption=short_caption(event.title) or event.title,
                docket_number=reserved_docket_number(docket_id),
                brief=_brief(data_root, docket_id),
                stakes=stakes.get(case_id),
            )
        return cases[docket_id]

    decisions: dict[tuple[int, Stage], Decision] = {}
    actions: dict[tuple[int, Moment], Action] = {}
    filings: dict[tuple[int, Stage], Filing] = {}
    for docket_id, event_paths in _event_dirs(data_root):
        if not event_paths.event_file.is_file():
            continue
        try:
            event = read_model(event_paths.event_file, PredictableEvent)
        except (OSError, ValueError, ValidationError):
            continue
        if is_voided(event.case_id, event.event_id):
            continue
        stage = normalized_stage(event.kind, event.stage)
        if stage is None:
            continue
        if event_paths.outcome.is_file():
            outcome = read_model(event_paths.outcome, Outcome)
            if start <= outcome.resolved_at <= end:
                decisions.setdefault(
                    (docket_id, stage),
                    Decision(
                        case=case_of(docket_id, event),
                        stage=stage,
                        words=outcome_words(stage, outcome),
                        usual=usual_outcome(stage, outcome),
                        resolved_at=outcome.resolved_at,
                    ),
                )
        if event.opened_at is None or not start <= event.opened_at <= end:
            continue
        declared = normalized_moment(stage, event.moment)
        moment = Moment(declared) if declared in _MOMENT_VALUES else None
        if moment in _ACTION_HEADING:
            actions.setdefault((docket_id, moment), Action(case_of(docket_id, event), moment))
        elif moment == Moment.arrival and stage in _FILING_HEADING:
            filings.setdefault((docket_id, stage), Filing(case_of(docket_id, event), stage))

    calendar = committed_calendar(data_root)
    return CourtUpdate(
        week=week,
        start=start,
        end=end,
        decisions=tuple(sorted(decisions.values(), key=lambda d: _order(d.case))),
        actions=tuple(sorted(actions.values(), key=lambda a: _order(a.case))),
        # A filing the Court also decided inside the week is listed once, as a decision.
        filings=tuple(
            sorted(
                (filing for key, filing in filings.items() if key not in decisions),
                key=lambda f: _order(f.case),
            )
        ),
        next_conference=next_conference(calendar, end + timedelta(days=1)),
    )


def _order(case: CourtCase) -> tuple[str, str]:
    return (case.caption.casefold(), case.case_id)


def _biggest(cases: Sequence[CourtCase], top: int) -> set[str]:
    """The ``top`` cases the models rated biggest, as case ids.

    Highest stakes read first, ties in caption order, so the same tree always
    picks the same cases. A case with no stakes read is picked only after
    every rated one, in caption order.
    """
    ranked = sorted(
        cases,
        key=lambda case: (
            case.stakes is None,
            -(case.stakes if case.stakes is not None else 0.0),
            *_order(case),
        ),
    )
    return {case.case_id for case in ranked[:top]}


def _case_line(case: CourtCase, *, said: str = "") -> str:
    """One case on one line: caption, what happened, its one-sentence description, the docket."""
    number = f" (No. {case.docket_number})" if case.docket_number else ""
    happened = f" — {said}." if said else "."
    brief = f" {escape_text(case.brief)}" if case.brief else ""
    url = docket_page_url(case.docket_number) if case.docket_number else None
    link = f" ([docket]({url}))" if url else ""
    return f"- **{escape_text(case.caption)}**{number}{happened}{brief}{link}"


def _cut_note(shown: int, total: int, what: str) -> str:
    return (
        f"Showing {shown} of the {total} {what}: the cases the project's models rated the biggest."
    )


def _decision_lines(update: CourtUpdate, top: int | None) -> list[str]:
    lines: list[str] = []
    for stage in _STAGE_ORDER:
        members = [d for d in update.decisions if d.stage == stage]
        if not members:
            continue
        usual = [d for d in members if d.usual]
        keep = (
            _biggest([d.case for d in usual], top) if top is not None and len(usual) > top else None
        )
        lines += [f"### {_DECISION_HEADING[stage]}", ""]
        intro: list[str] = []
        if len(members) > 1:
            usual_label, other_label = _COUNT_LABEL[stage]
            intro.append(
                f"{len(members)} decided: {len(usual)} {usual_label}, "
                f"{len(members) - len(usual)} {other_label}."
            )
        if keep is not None:
            intro.append(_cut_note(len(keep), len(usual), f"cases {_COUNT_LABEL[stage][0]}"))
        if intro:
            lines += [" ".join(intro), ""]
        lines += [_case_line(d.case, said=d.words) for d in members if not d.usual]
        lines += [
            _case_line(d.case, said=d.words)
            for d in usual
            if keep is None or d.case.case_id in keep
        ]
        lines.append("")
    return lines


def _listed(heading: str, cases: Sequence[CourtCase], top: int | None, what: str) -> list[str]:
    """One group of cases under its heading, cut to the biggest where it runs long."""
    keep = _biggest(cases, top) if top is not None and len(cases) > top else None
    lines = [f"### {heading}", ""]
    if keep is not None:
        lines += [_cut_note(len(keep), len(cases), what), ""]
    lines += [_case_line(case) for case in cases if keep is None or case.case_id in keep]
    lines.append("")
    return lines


def court_update_subject(update: CourtUpdate) -> str:
    """The update's title, which is also the email's subject: one per ISO week."""
    start, end = update.start, update.end
    span = f"{start:%B} {start.day} \N{EN DASH} {end:%B} {end.day}, {end.year}"
    return f"FedCourtsAI Supreme Court update: {span}"


def render_court_update(
    update: CourtUpdate, *, title: bool = True, top: int | None = LISTED_TOP
) -> str:
    """The update as Markdown, ready for an email body.

    ``title=False`` drops the heading, for a channel that carries the title as
    the message's subject instead. ``top`` is how many cases a cut list keeps;
    ``None`` lists every case.
    """
    lines = [f"# {court_update_subject(update)}", ""] if title else []
    if update.empty:
        lines += ["The Court took no action this week on the cases FedCourtsAI follows.", ""]
    if update.decisions:
        lines += ["## Decisions", "", *_decision_lines(update, top)]
    if update.actions:
        lines += ["## Other actions by the Court", ""]
        for moment, heading in _ACTION_HEADING.items():
            cases = [a.case for a in update.actions if a.moment == moment]
            if cases:
                lines += _listed(heading, cases, None, "cases")
    if update.filings:
        lines += ["## New filings", ""]
        for stage, heading in _FILING_HEADING.items():
            cases = [f.case for f in update.filings if f.stage == stage]
            if cases:
                lines += _listed(heading, cases, top, "filings")
    if update.next_conference is not None:
        day = update.next_conference
        lines += [
            "## Ahead",
            "",
            f"The Court's next scheduled conference is {day:%A}, {day:%B} {day.day}, {day.year}.",
            "",
        ]
    lines += ["---", "", _FOOTER, ""]
    return "\n".join(lines)
