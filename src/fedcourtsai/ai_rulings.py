"""Plain-language summaries of the AI watchlist's rulings, for the AI-cases update.

One markdown file per ruling, at ``data/ai-cases/summaries/<entry_id>.md``,
named for the CourtListener docket entry the activity record
(:mod:`fedcourtsai.ai_activity`) recorded. The AI-cases update renders it under
that entry's item, labeled with the model that wrote it
(``docs/case-summaries.md``, *AI watchlist rulings*). Display material only:
nothing scores a summary, and no metric or board reads one.

What a summary may be written from is fixed by the terms decision in
``docs/data-sources.md``: the ruling's own text (a federal court's work, public
domain, copied through RECAP) and court-record identifiers, and nothing from
CourtListener's curated docket layer. So the staged record is the ruling's main
document text alone, with the court, docket number, entry number, filing date
and the watchlist's own case name; no docket payload, entry description or
party field is staged or sent. Only the kinds a court writes are summarized
(:data:`SUMMARIZED_KINDS`): a party's filing is counsel's work, not public
domain by authorship.

The lane is the case-summary lane's (:mod:`fedcourtsai.summaries`): the same
model and caps, the same plan and hold (``summarize-plan --rulings`` adds the
owed rulings to the plan and its estimate), the same no-tools request and
one retry on a mechanical rejection, the same jail and review PR. A ruling is
summarized once: the file is never rewritten, since it describes that ruling.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Final
from xml.sax.saxutils import quoteattr

import httpx
import yaml
from pydantic import ValidationError
from tenacity.wait import wait_base

from . import secretscan
from .ai_activity import ACTIVITY_DIR
from .config import SummariesConfig
from .pipeline.documents import scrub_contact_details
from .pricing import MODEL_RATES, estimate_cost_usd
from .schemas import (
    AiCaseActivity,
    AiCaseActivityEntry,
    AiRulingPlanItem,
    AiRulingSummaryFrontMatter,
    CaseSummaryUsage,
    SummaryPlan,
)
from .serialize import load_yaml, read_model, write_raw_json, write_text
from .summaries import (
    HEADLINE_HEADING,
    RULING_STAGE_DIR,
    RULING_STAGE_KEYS,
    TRUNCATION_MARKER,
    CallResult,
    CaseResult,
    RetryTurn,
    SummarizeOutcome,
    SummaryCallError,
    add_usage,
    build_request,
    call_messages_api,
    estimate_cost,
    headline_problems,
    markup_problems,
    on_retry,
    prompt_digest,
    split_sections,
)

#: The ruling summarizer's system prompt, relative to the repository root.
PROMPT_PATH: Final = Path(".github/prompts/summarize-ai-ruling.md")

#: Where the summaries live, under the data root.
SUMMARY_DIR: Final = Path("ai-cases") / "summaries"

#: The body contract the harness writes, stamped as ``body_version``.
BODY_VERSION: Final = 1

#: The body's sections, in order: the shared one-sentence headline, then what
#: the ruling decided.
SECTION_HEADINGS: Final = (HEADLINE_HEADING, "## What the court decided")

#: Words across the sections the harness accepts: a tolerant band around the
#: ~150 the prompt asks for.
WORD_BAND: Final = (60, 350)

#: The activity kinds a court writes, and so the only ones summarized.
SUMMARIZED_KINDS: Final = frozenset({"opinion", "judgment", "ruling"})

#: A ruling recorded more than this many days before the plan is no longer
#: news, and is not planned; one whose text never reached the corpus drops out
#: of the plan here rather than being listed forever.
MAX_AGE_DAYS: Final = 30

_SUMMARY_NAME = re.compile(r"^([1-9][0-9]*)\.md$")
_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


class RulingSummaryFormatError(ValueError):
    """A ruling summary file whose front matter is missing or invalid."""


def summary_path(data_root: Path, entry_id: int) -> Path:
    """The ruling's summary file under ``data_root``."""
    return data_root / SUMMARY_DIR / f"{entry_id}.md"


def text_digest(text: str) -> str:
    """``sha256:<hex>`` of a ruling's stored text."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def ruling_text(payload: Mapping[str, Any], entry_id: int) -> str:
    """The stored text of the entry's main document in a docket snapshot, or ``""``.

    The main document is the entry's RECAP document without an attachment
    number. Only its ``plain_text`` is read: the ruling's own words, never the
    entry's description or any other curated field.
    """
    for entry in payload.get("docket_entries") or []:
        if not isinstance(entry, Mapping) or entry.get("id") != entry_id:
            continue
        for document in entry.get("recap_documents") or []:
            if isinstance(document, Mapping) and not document.get("attachment_number"):
                text = document.get("plain_text")
                return text if isinstance(text, str) and text.strip() else ""
        return ""
    return ""


# A filing a party drafted for the court to adopt or sign: proposed findings, a
# proposed or stipulated order or judgment. The activity rule can read one as an
# opinion or a judgment, but it is counsel's text, which the terms decision
# keeps out of a summary.
_PARTY_DRAFTED = re.compile(r"\bproposed\b|\bstipulat", re.IGNORECASE)


def court_written(payload: Mapping[str, Any], entry_id: int) -> bool:
    """Whether the entry reads as the court's own document rather than a party's draft.

    Read off the entry's description, which only classifies the entry here and
    is never staged, sent or published.
    """
    for entry in payload.get("docket_entries") or []:
        if isinstance(entry, Mapping) and entry.get("id") == entry_id:
            return not _PARTY_DRAFTED.search(str(entry.get("description") or ""))
    return True


def owed_rulings(
    data_root: Path, today: date, *, max_age_days: int = MAX_AGE_DAYS
) -> list[AiCaseActivityEntry]:
    """The recorded rulings owed a summary, oldest filing first.

    A ruling is owed when an activity record dated within ``max_age_days`` of
    ``today`` lists it under a kind a court writes and no summary file exists
    for its entry.
    """
    root = data_root / ACTIVITY_DIR
    oldest = today - timedelta(days=max_age_days)
    found: dict[int, AiCaseActivityEntry] = {}
    for path in sorted(root.glob("*.json")) if root.is_dir() else []:
        try:
            day = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if day < oldest:
            continue
        for entry in read_model(path, AiCaseActivity).entries:
            if (
                entry.kind in SUMMARIZED_KINDS
                and not summary_path(data_root, entry.entry_id).is_file()
            ):
                found.setdefault(entry.entry_id, entry)
    return sorted(found.values(), key=lambda e: (e.date_filed, e.entry_id))


def plan_rulings(
    owed: Iterable[AiCaseActivityEntry],
    read_payload: Callable[[str, int], Mapping[str, Any] | None],
    config: SummariesConfig,
) -> tuple[list[AiRulingPlanItem], list[int], tuple[float, float]]:
    """The owed rulings whose text the corpus holds, the entry ids of those it
    does not, and the low/high cost of summarizing the first.

    ``read_payload(court, docket_id)`` is the docket's newest snapshot, read
    once per docket.
    """
    payloads: dict[tuple[str, int], Mapping[str, Any] | None] = {}
    planned: list[AiRulingPlanItem] = []
    without: list[int] = []
    for entry in owed:
        key = (entry.court, entry.docket_id)
        if key not in payloads:
            payloads[key] = read_payload(*key)
        payload = payloads[key]
        text = ruling_text(payload, entry.entry_id) if payload is not None else ""
        if payload is not None and not court_written(payload, entry.entry_id):
            continue
        if not text:
            without.append(entry.entry_id)
            continue
        planned.append(
            AiRulingPlanItem(
                case=entry.case,
                court=entry.court,
                docket_id=entry.docket_id,
                docket_number=entry.docket_number,
                entry_id=entry.entry_id,
                entry_number=entry.entry_number,
                date_filed=entry.date_filed,
                kind=entry.kind,
                text_digest=text_digest(text),
                staged_digest=text_digest(scrub_contact_details(text).text),
                input_chars=min(len(text), config.max_document_chars),
            )
        )
    cost = estimate_cost(config, [r.input_chars for r in planned], prompt_path=PROMPT_PATH)
    return planned, without, cost


def with_rulings(
    plan: SummaryPlan,
    rulings: list[AiRulingPlanItem],
    without_text: list[int],
    cost: tuple[float, float],
) -> SummaryPlan:
    """``plan`` with the owed rulings added and priced into its estimate."""
    low, high = cost
    return plan.model_copy(
        update={
            "rulings": rulings,
            "rulings_without_text": without_text,
            "estimated_cost_usd_low": round(plan.estimated_cost_usd_low + low, 2),
            "estimated_cost_usd_high": round(plan.estimated_cost_usd_high + high, 2),
        }
    )


# --- staging --------------------------------------------------------------------


def stage_rulings(
    plan: SummaryPlan,
    read_payload: Callable[[str, int], Mapping[str, Any] | None],
    stage_root: Path,
) -> list[tuple[int, str]]:
    """Stage each planned ruling's text under ``stage_root``; ``(entry_id, reason)`` per skip.

    Writes ``<stage_root>/ai-rulings/<entry_id>.json`` holding the entry id,
    the stored text's digest and the text after the contact-detail scrub. A
    ruling is skipped, and stays owed, when its text has changed since the plan
    priced it, has gone, or keeps a contact-shaped residual after the scrub.
    """
    out = stage_root / RULING_STAGE_DIR
    payloads: dict[tuple[str, int], Mapping[str, Any] | None] = {}
    skipped: list[tuple[int, str]] = []
    for ruling in plan.rulings:
        key = (ruling.court, ruling.docket_id)
        if key not in payloads:
            payloads[key] = read_payload(*key)
        payload = payloads[key]
        text = ruling_text(payload, ruling.entry_id) if payload is not None else ""
        if not text:
            skipped.append((ruling.entry_id, "the corpus no longer holds its text"))
            continue
        if text_digest(text) != ruling.text_digest:
            skipped.append((ruling.entry_id, "its text changed since the plan"))
            continue
        scrubbed = scrub_contact_details(text)
        if not scrubbed.clean:
            skipped.append(
                (ruling.entry_id, f"{scrubbed.residuals} contact residual(s) after the scrub")
            )
            continue
        staged = {
            "entry_id": ruling.entry_id,
            "text_digest": ruling.text_digest,
            "text": scrubbed.text,
        }
        assert set(staged) == RULING_STAGE_KEYS
        write_raw_json(out / f"{ruling.entry_id}.json", staged)
    return skipped


def read_staged_ruling(stage_root: Path, ruling: AiRulingPlanItem) -> str | None:
    """The staged text for a planned ruling, or ``None`` when it was not staged as planned."""
    path = stage_root / RULING_STAGE_DIR / f"{ruling.entry_id}.json"
    if not path.is_file():
        return None
    try:
        staged = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(staged, dict):
        return None
    if staged.get("entry_id") != ruling.entry_id or staged.get("text_digest") != (
        ruling.text_digest
    ):
        return None
    text = staged.get("text")
    return text if isinstance(text, str) and text.strip() else None


def render_record(ruling: AiRulingPlanItem, text: str, cap: int) -> str:
    """The user message: the identifiers as attributes, then the ruling's text, capped."""
    shown = text
    if len(text) > cap:
        shown = text[:cap] + "\n" + TRUNCATION_MARKER.format(shown=cap, total=len(text))
    attrs = {
        "case": ruling.case,
        "court": ruling.court,
        "docket_number": ruling.docket_number,
        "date_filed": ruling.date_filed.isoformat(),
    }
    if ruling.entry_number is not None:
        attrs["entry_number"] = str(ruling.entry_number)
    rendered = " ".join(f"{k}={quoteattr(v)}" for k, v in attrs.items())
    # The text cannot close the element early and pose as text outside it.
    shown = re.sub(r"</?\s*ruling", lambda m: m.group().replace("<", "&lt;"), shown, flags=re.I)
    return f"<ruling {rendered}>\n{shown}\n</ruling>"


# --- the body contract ------------------------------------------------------------


def body_problems(body: str, *, check_length: bool = True) -> list[str]:
    """Why a ruling summary body breaks the contract; empty when it meets it.

    The case-summary contract's mechanical rules on these sections: no
    markup, the headings exactly and in order with nothing before the first,
    no empty section, no paragraph opening "Whether", a one-paragraph headline
    within the word cap, and (``check_length``) the word band.
    """
    problems = markup_problems(body)
    headings, sections, preamble = split_sections(body)
    if preamble:
        problems.append("text before the first section heading")
    if tuple(headings) != SECTION_HEADINGS:
        problems.append(
            "sections must be exactly "
            + ", ".join(repr(h) for h in SECTION_HEADINGS)
            + f" in order (found {headings!r})"
        )
    for heading, text in zip(headings, sections, strict=True):
        if not text:
            problems.append(f"section {heading!r} is empty")
        paragraphs = re.split(r"\n\s*\n", text)
        if any(p.strip().lower().startswith("whether") for p in paragraphs):
            problems.append(f"a paragraph in {heading!r} opens with 'Whether'")
        if heading == HEADLINE_HEADING and text:
            problems += headline_problems(heading, paragraphs)
    if check_length:
        words = sum(len(text.split()) for text in sections)
        low, high = WORD_BAND
        if not low <= words <= high:
            problems.append(f"{words} words, outside the {low}-{high} band")
    return problems


def render_summary(front: AiRulingSummaryFrontMatter, body: str) -> str:
    """The file: harness-written YAML front matter, then the model's body."""
    header = yaml.safe_dump(
        front.model_dump(mode="json", exclude_none=True),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    return f"---\n{header}---\n\n{body.strip()}\n"


def parse_summary(text: str) -> tuple[AiRulingSummaryFrontMatter, str]:
    """Split and validate a ruling summary's front matter; return it with the body."""
    match = _FRONT_MATTER.match(text)
    if match is None:
        raise RulingSummaryFormatError("no YAML front matter block")
    try:
        front = AiRulingSummaryFrontMatter.model_validate(load_yaml(match.group(1)))
    except (yaml.YAMLError, ValidationError) as exc:
        raise RulingSummaryFormatError(f"front matter: {exc}") from exc
    return front, text[match.end() :]


def summary_file_problems(file: Path, root: Path) -> list[str] | None:
    """Validate one file under ``<root>/ai-cases/summaries/``; ``None`` if it is not there.

    Positional, like the case summaries' check: anything under that directory
    is held to the contract. Checks the name is an entry id, the front matter
    validates and names that entry, and the body has the contract's sections in
    order. Length is not re-checked: the band gates what the harness accepts
    from the model.
    """
    base = len(root.parts)
    parts = file.parts[base:]
    if file.parts[:base] != root.parts or parts[:2] != SUMMARY_DIR.parts:
        return None
    name = _SUMMARY_NAME.match(parts[2]) if len(parts) == 3 else None
    if name is None:
        return ["not a ruling summary: expected ai-cases/summaries/<entry_id>.md"]
    try:
        front, body = parse_summary(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, RulingSummaryFormatError) as exc:
        return [str(exc)]
    problems: list[str] = []
    if front.entry_id != int(name.group(1)):
        problems.append(f"named for entry {name.group(1)} but records entry {front.entry_id}")
    problems += body_problems(body, check_length=False)
    return problems


@dataclass(frozen=True)
class RulingSummary:
    """A committed ruling summary, as the AI-cases update renders it."""

    model: str
    headline: str
    decided: str


def committed_summaries(data_root: Path) -> dict[int, RulingSummary]:
    """Every committed ruling summary that meets the contract, by entry id.

    A file that fails validation is left out rather than rendered: ``validate``
    reports it, and the update renders the entry without a summary.
    """
    found: dict[int, RulingSummary] = {}
    root = data_root / SUMMARY_DIR
    for path in sorted(root.glob("*.md")) if root.is_dir() else []:
        if summary_file_problems(path, data_root):
            continue
        front, body = parse_summary(path.read_text(encoding="utf-8"))
        _, sections, _ = split_sections(body)
        found[front.entry_id] = RulingSummary(
            model=front.model, headline=sections[0], decided=sections[1]
        )
    return found


# --- writing ------------------------------------------------------------------------


def _refusal(result: CallResult, rel: str, api_key: str) -> tuple[str, list[str]]:
    """Why a response is not written, and the problems a retry may fix.

    As for a case, plus a contact detail anywhere in the body, which, like a
    secret-scan finding, is not retried.
    """
    if result.stop_reason != "end_turn":
        return f"stop_reason {result.stop_reason!r}", []
    problems = body_problems(result.text)
    findings = secretscan.scan_lines(rel, result.text.split("\n"), [api_key] if api_key else [])
    # The contact scrub's shape pass over the whole body: a detail the staged
    # text's scrub missed, or one the model rebuilt, would reach a public email.
    contacts = scrub_contact_details(result.text).replacements
    retryable = [] if findings or contacts else list(problems)
    if findings:
        problems.append(f"secret scan: {len(findings)} finding(s)")
    if contacts:
        problems.append(f"{contacts} contact detail(s) in the body")
    return ("rejected: " + "; ".join(problems) if problems else ""), retryable


def summarize_ruling(  # noqa: PLR0913 - one ruling's inputs, each load-bearing
    ruling: AiRulingPlanItem,
    *,
    stage_root: Path,
    data_root: Path,
    config: SummariesConfig,
    system_prompt: str,
    prompt_sha: str,
    client: httpx.Client,
    api_key: str,
    now: datetime,
    wait: wait_base | None = None,
    may_retry: Callable[[], bool] = lambda: True,
) -> CaseResult:
    """Write one planned ruling's summary, or say why not.

    The case lane's rules: one call with no tools, one retry on a mechanical
    rejection while ``may_retry()`` holds, no retry for a truncated or empty
    response or a secret-scan finding, and both calls' usage recorded.
    """
    target = summary_path(data_root, ruling.entry_id)
    if target.is_file():
        return CaseResult(None, "already summarized")
    text = read_staged_ruling(stage_root, ruling)
    if text is None:
        return CaseResult(None, "no staged text (not staged, or changed since the plan)")
    record = render_record(ruling, text, config.max_document_chars)
    try:
        result = call_messages_api(
            client, api_key, build_request(config, system_prompt, record), wait=wait
        )
    except SummaryCallError as exc:
        return CaseResult(None, str(exc))
    usage = result.usage
    cost = estimate_cost_usd(config.model, usage)
    refusal, retryable = _refusal(result, str(target), api_key)
    first_rejection = ""
    if refusal and retryable and result.text.strip() and may_retry():
        first_rejection = refusal
        retry = RetryTurn(result.text, tuple(retryable))
        try:
            result = call_messages_api(
                client, api_key, build_request(config, system_prompt, record, retry), wait=wait
            )
        except SummaryCallError as exc:
            refusal = f"retry failed: {exc}"
        else:
            usage = add_usage(usage, result.usage)
            cost += estimate_cost_usd(config.model, result.usage)
            refusal = on_retry(_refusal(result, str(target), api_key)[0])
    if refusal:
        return CaseResult(None, refusal, cost, first_rejection)
    front = AiRulingSummaryFrontMatter(
        case=ruling.case,
        court=ruling.court,
        docket_id=ruling.docket_id,
        docket_number=ruling.docket_number,
        entry_id=ruling.entry_id,
        entry_number=ruling.entry_number,
        date_filed=ruling.date_filed,
        kind=ruling.kind,
        text_digest=ruling.text_digest,
        model=config.model,
        prompt_digest=prompt_sha,
        body_version=BODY_VERSION,
        generated_at=now.astimezone(UTC).replace(microsecond=0),
        usage=CaseSummaryUsage(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            estimated_cost_usd=round(cost, 6),
        ),
    )
    write_text(target, render_summary(front, result.text))
    return CaseResult(target, cost_usd=cost, first_rejection=first_rejection)


def summarize_rulings(  # noqa: PLR0913 - the run's inputs, each load-bearing
    plan: SummaryPlan,
    outcome: SummarizeOutcome,
    *,
    stage_root: Path,
    data_root: Path,
    config: SummariesConfig,
    prompt_bytes: bytes,
    client: httpx.Client,
    api_key: str,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    wait: wait_base | None = None,
    deadline: datetime | None = None,
) -> SummarizeOutcome:
    """Summarize every planned ruling into ``outcome``; a ruling that fails is skipped.

    Each ruling is reported under ``ruling <court>/<docket> entry <id>``.
    ``deadline`` and the model check are the case lane's
    (:func:`fedcourtsai.summaries.summarize_plan`).
    """
    if plan.rulings and plan.model != config.model:
        raise ValueError(
            f"plan was made for model {plan.model!r}, config now names {config.model!r}"
        )
    if plan.rulings and config.model not in MODEL_RATES:
        raise ValueError(f"model {config.model!r} has no rate in pricing.MODEL_RATES")
    system_prompt = prompt_bytes.decode("utf-8")
    prompt_sha = prompt_digest(prompt_bytes)
    for ruling in plan.rulings:
        label = f"ruling {ruling.court}/{ruling.docket_id} entry {ruling.entry_id}"
        if deadline is not None and now() >= deadline:
            outcome.skipped.append((label, "deferred: time budget reached", 0.0))
            continue
        result = summarize_ruling(
            ruling,
            stage_root=stage_root,
            data_root=data_root,
            config=config,
            system_prompt=system_prompt,
            prompt_sha=prompt_sha,
            client=client,
            api_key=api_key,
            now=now(),
            wait=wait,
            may_retry=lambda: deadline is None or now() < deadline,
        )
        if result.first_rejection:
            outcome.retried.append((label, result.first_rejection))
        if result.path is None:
            outcome.skipped.append((label, result.reason, result.cost_usd))
        else:
            outcome.written.append((label, result.path, result.cost_usd))
    return outcome
