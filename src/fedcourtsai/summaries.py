"""Plain-language case summaries: selection, the model call, and the file contract.

One markdown file per predicted case per record, at
``data/cases/<court>/<docket>/summaries/<snapshot day>.md``, written for readers
who do not already know the case (``docs/case-summaries.md``). Display material
only: nothing scores a summary, and no metric or board reads one.

Three pieces, each a small pure function the CLI wraps:

- **Selection** is content-keyed. A case is eligible once it carries a committed
  prediction; it is owed a summary when the :func:`record_digest` of its newest
  corpus record differs from the digest its newest committed summary was
  written from (or it has none). Keyed on content rather than on the snapshot
  day, because most snapshot days re-serve an unchanged docket — only the
  payload's generation stamp moves — and a day-keyed rule would pay to rewrite
  an identical summary every day.
- **The call** is one Messages API request carrying the system prompt and the
  staged record, and nothing else: no tools, no retrieval, no thinking. That
  shape is what makes "grounded in the record only" a property of the request
  rather than a promise in the prompt.
- **The file** is harness-written front matter (:class:`CaseSummaryFrontMatter`)
  over the model's body, which is accepted only if it has exactly the three
  contract sections in order, sits inside a tolerant length band, opens no
  paragraph with "Whether", and passes the secret scan.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
import yaml
from pydantic import ValidationError
from tenacity import (
    RetryCallState,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)
from tenacity.wait import wait_base

from . import ids, secretscan
from .config import SummariesConfig
from .paths import CasePaths
from .pricing import MODEL_RATES, TokenCounts, estimate_cost_usd
from .provision import GENERATION_STAMPS
from .schemas import (
    CaseSummaryFrontMatter,
    CaseSummaryUsage,
    SummaryPlan,
    SummaryPlanCase,
)
from .serialize import write_text

#: The summarizer's system prompt, relative to the repository root.
PROMPT_PATH = Path(".github/prompts/summarize.md")

#: The body's three sections, in the order the contract fixes.
SECTION_HEADINGS: tuple[str, ...] = (
    "## What happened",
    "## What the Court is being asked",
    "## Where it stands",
)

#: The accepted body length, in words. The contract asks for about 250; the band
#: is tolerant so a faithful summary of a thin or a busy docket is not refused
#: for being one, and tight enough that a response which ignored the contract is.
WORD_BAND: tuple[int, int] = (120, 450)

#: The Messages API endpoint and the version header it requires.
API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

#: The environment variable the summarize command reads its API key from: the
#: environment's Anthropic key, the one the other Claude lanes spend on. The
#: lane's calls are on a model outside the prediction panel, whose provider rate
#: limits are separate from the cells'; the spend limit is shared, which the
#: workflow's `review` hold bounds.
API_KEY_ENV = "ANTHROPIC_API_KEY"

#: The marker a capped document ends with, in the text the model reads.
TRUNCATION_MARKER = "[truncated: {shown} of {total} characters shown]"

# Cost-estimate assumptions for the plan report, stated rather than implied.
# Characters per token span the tokenizer's range on legal prose (the low end is
# the current tokenizer's measured density on filings); the output side runs
# from a typical summary to the configured cap.
_CHARS_PER_TOKEN_LOW_COST = 3.5
_CHARS_PER_TOKEN_HIGH_COST = 2.5
_TYPICAL_OUTPUT_TOKENS = 500

#: The key only the supremecourt.gov docket JSON carries (its proceedings
#: list), the same discriminator ``casestore.read_latest_live_snapshot`` reads.
#: The lane summarizes only records whose snapshot has this shape: the Court's
#: own docket and filings are public records, while a CourtListener REST
#: docket is CC BY-ND content that no public surface of this project carries
#: (docs/data-sources.md), and the staged record crosses a public artifact.
LIVE_SHAPE_KEY = "ProceedingsandOrder"

_SUMMARY_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


class SummaryFormatError(ValueError):
    """A summary file or model body that does not meet the contract."""


# --- selection ------------------------------------------------------------------


def record_digest(payload: Mapping[str, Any], documents: Iterable[tuple[str, str]]) -> str:
    """``sha256:<hex>`` over one case record's content, generation stamps removed.

    The snapshot payload minus the keys that date the *pull* rather than the
    docket (:data:`fedcourtsai.provision.GENERATION_STAMPS`), canonically
    serialized, plus the sorted ``(kind, sha256(text))`` pair of each stored
    document. Documents count because they arrive days after the docket entry
    that links them: a record whose docket is unchanged but whose petition text
    has just landed is a different record to summarize.
    """
    snapshot = {k: v for k, v in payload.items() if k not in GENERATION_STAMPS}
    docs = sorted(
        (kind, hashlib.sha256(text.encode("utf-8")).hexdigest()) for kind, text in documents
    )
    canonical = json.dumps(
        {"snapshot": snapshot, "documents": docs},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def prompt_digest(prompt_bytes: bytes) -> str:
    """``sha256:<hex>`` of the prompt file's bytes, as recorded on each summary."""
    return "sha256:" + hashlib.sha256(prompt_bytes).hexdigest()


def input_chars(payload: Mapping[str, Any], documents: Iterable[tuple[str, str]], cap: int) -> int:
    """Characters of record the model would read for one case, documents capped."""
    snapshot = len(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return snapshot + sum(min(len(text), cap) for _, text in documents)


def newest_summary(data_root: Path, court_id: str, docket_id: int) -> Path | None:
    """The case's newest committed summary file by snapshot day, or ``None``."""
    directory = CasePaths(data_root, court_id, docket_id).summaries_dir
    if not directory.is_dir():
        return None
    dated = sorted(p for p in directory.iterdir() if _SUMMARY_NAME.match(p.name))
    return dated[-1] if dated else None


def committed_digest(path: Path) -> str | None:
    """The ``record_digest`` a summary file was written from; ``None`` if unreadable.

    An unreadable summary answers "no digest", which re-plans the case: the
    validator reports the broken file on its own, and a fresh summary for the
    same record is the repair.
    """
    try:
        front, _ = parse_summary(path.read_text())
    except (OSError, SummaryFormatError):
        return None
    return front.record_digest


@dataclass(frozen=True)
class CaseRecord:
    """A case's newest corpus record, as the plan reads it."""

    snapshot: date
    payload: Mapping[str, Any]
    documents: Sequence[tuple[str, str]]


def plan_summaries(
    data_root: Path,
    case_ids: Iterable[str],
    read: Callable[[str], CaseRecord | None],
    config: SummariesConfig,
    *,
    limit: int = 0,
) -> SummaryPlan:
    """Which eligible cases are owed a summary, and what writing them would cost.

    ``case_ids`` is the eligible set (cases with a committed prediction);
    ``read`` fetches a case's newest record from the corpus. Owed cases are
    ordered cases-without-a-summary first, then changed records, each by case id,
    so a ``limit`` spends on the cases a reader has nothing for. ``limit`` of 0
    means no limit.
    """
    owed: list[SummaryPlanCase] = []
    up_to_date = 0
    no_snapshot: list[str] = []
    not_live_shaped: list[str] = []
    eligible = sorted(set(case_ids))
    for case_id in eligible:
        court_id, docket = case_id.split("/", 1)
        docket_id = int(docket)
        record = read(case_id)
        if record is None:
            no_snapshot.append(case_id)
            continue
        if LIVE_SHAPE_KEY not in record.payload:
            not_live_shaped.append(case_id)
            continue
        digest = record_digest(record.payload, record.documents)
        newest = newest_summary(data_root, court_id, docket_id)
        committed = committed_digest(newest) if newest is not None else None
        if committed == digest:
            up_to_date += 1
            continue
        owed.append(
            SummaryPlanCase(
                case_id=ids.case_id(court_id, docket_id),
                court_id=court_id,
                docket_id=docket_id,
                snapshot=record.snapshot,
                record_digest=digest,
                reason="new" if newest is None else "record-changed",
                documents=len(record.documents),
                input_chars=input_chars(
                    record.payload, record.documents, config.max_document_chars
                ),
            )
        )
    owed.sort(key=lambda c: (c.reason != "new", c.case_id))
    planned = owed[:limit] if limit > 0 else owed
    low, high = estimate_cost(config, [c.input_chars for c in planned])
    return SummaryPlan(
        model=config.model,
        eligible=len(eligible),
        up_to_date=up_to_date,
        no_snapshot=no_snapshot,
        not_live_shaped=not_live_shaped,
        deferred=len(owed) - len(planned),
        cases=planned,
        estimated_cost_usd_low=round(low, 2),
        estimated_cost_usd_high=round(high, 2),
    )


def estimate_cost(config: SummariesConfig, chars: Sequence[int]) -> tuple[float, float]:
    """A low/high USD range for summarizing records of these sizes.

    Raises ``KeyError`` when the configured model has no rate, which is the
    point: a plan that cannot be priced must not be approved as if it were free.
    """
    prompt_chars = len(PROMPT_PATH.read_text()) if PROMPT_PATH.is_file() else 0
    low = high = 0.0
    for size in chars:
        total = size + prompt_chars
        low += estimate_cost_usd(
            config.model,
            TokenCounts(
                input_tokens=int(total / _CHARS_PER_TOKEN_LOW_COST),
                output_tokens=_TYPICAL_OUTPUT_TOKENS,
            ),
        )
        high += estimate_cost_usd(
            config.model,
            TokenCounts(
                input_tokens=int(total / _CHARS_PER_TOKEN_HIGH_COST),
                output_tokens=config.max_output_tokens,
            ),
        )
    return low, high


def render_plan_report(plan: SummaryPlan, *, run_url: str = "") -> str:
    """The markdown the review hold is judged on: counts, cost range, case list."""
    lines = [
        "## summarize — plan",
        "",
        f"- model: `{plan.model}`",
        f"- eligible cases (a committed prediction): {plan.eligible}",
        f"- up to date (newest summary matches the newest record): {plan.up_to_date}",
        f"- owed and planned: **{len(plan.cases)}**"
        + (f" ({plan.deferred} more deferred by the limit)" if plan.deferred else ""),
        f"- no corpus snapshot: {len(plan.no_snapshot)}",
        "- newest snapshot not the Court's own docket JSON (not summarized): "
        + f"{len(plan.not_live_shaped)}",
        f"- estimated cost: **${plan.estimated_cost_usd_low:.2f}"
        + f" to ${plan.estimated_cost_usd_high:.2f}**",
        "",
    ]
    if run_url:
        lines += [f"Run: {run_url}", ""]
    if plan.cases:
        lines += [
            "| case | snapshot | reason | documents | input chars |",
            "|---|---|---|---:|---:|",
        ]
        lines += [
            f"| `{c.case_id}` | {c.snapshot.isoformat()} | {c.reason} | {c.documents} "
            + f"| {c.input_chars:,} |"
            for c in plan.cases
        ]
    else:
        lines.append("Nothing is owed: every eligible case's summary matches its record.")
    return "\n".join(lines) + "\n"


# --- the staged record ----------------------------------------------------------


@dataclass(frozen=True)
class StagedDocument:
    kind: str
    text: str
    entry_date: str | None = None
    stored_truncated: bool = False


def prune_stage(plan: SummaryPlan, stage_root: Path) -> list[tuple[str, str]]:
    """Remove every staged record that may not leave the stage job.

    The staged tree crosses to the generate job as a run artifact, which on a
    public repository any signed-in user can download while it exists, so it
    may carry the Court's own docket JSON and filings and nothing else. The plan
    screened each case's newest snapshot, but staging runs later — after the
    review hold — and provisions whatever is newest then, so a CourtListener
    REST snapshot stored in between would be staged. This re-applies the screen
    to what was actually staged, on the side of the job boundary that holds the
    corpus credentials, as an allowlist: a case is kept only if the plan names
    it and its tree holds exactly what provisioning writes — the planned day's
    snapshot in the Court's shape, ``context.json``, and the documents manifest
    with one text file per listed document, each fetched from supremecourt.gov.
    Everything else under the stage root is removed, and a symlink anywhere
    removes the case rather than being followed. Returns ``(path, reason)`` for
    each removal.
    """
    planned = {(c.court_id, str(c.docket_id)): c for c in plan.cases}
    removed: list[tuple[str, str]] = []
    if not stage_root.is_dir() or stage_root.is_symlink():
        return removed
    cases_root = stage_root / "cases"
    for entry in sorted(stage_root.iterdir()):
        if entry != cases_root or entry.is_symlink() or not entry.is_dir():
            _remove(entry)
            removed.append((entry.name, "not a case tree"))
    if not cases_root.is_dir():
        return removed
    for court_dir in sorted(cases_root.iterdir()):
        if court_dir.is_symlink() or not court_dir.is_dir():
            _remove(court_dir)
            removed.append((court_dir.name, "not a court directory"))
            continue
        for case_dir in sorted(court_dir.iterdir()):
            label = f"{court_dir.name}/{case_dir.name}"
            case = planned.get((court_dir.name, case_dir.name))
            reason = "not planned" if case is None else _stage_problem(case_dir, case)
            if reason:
                _remove(case_dir)
                removed.append((label, reason))
    return removed


def _stage_problem(case_dir: Path, case: SummaryPlanCase) -> str:
    """Why one planned case's staged tree may not cross the artifact, or ``""``."""
    if case_dir.is_symlink() or not case_dir.is_dir():
        return "not a case directory"
    files: set[str] = set()
    for path in case_dir.rglob("*"):
        if path.is_symlink():
            return f"symlink {path.relative_to(case_dir)}"
        if path.is_file():
            files.add(path.relative_to(case_dir).as_posix())
    snapshot = f"record/snapshots/{case.snapshot.isoformat()}.json"
    problem = _snapshot_problem(case_dir, snapshot, files)
    if problem:
        return problem
    documents, problem = _staged_documents(case_dir)
    if problem:
        return problem
    extra = sorted(files - {snapshot, "record/context.json"} - documents)
    return f"unexpected staged file {extra[0]}" if extra else ""


def _snapshot_problem(case_dir: Path, snapshot: str, files: set[str]) -> str:
    """Whether the planned day's snapshot is staged, alone, in the Court's shape."""
    if snapshot not in files:
        others = sorted(f for f in files if f.startswith("record/snapshots/"))
        if others:
            return f"staged snapshot {others[0]} is not the planned {Path(snapshot).stem}"
        return "no staged snapshot"
    try:
        payload = json.loads((case_dir / snapshot).read_text())
    except (OSError, ValueError):
        return "staged snapshot is unreadable"
    if not isinstance(payload, dict) or LIVE_SHAPE_KEY not in payload:
        return "staged snapshot is not the Court's own docket JSON"
    return ""


def _staged_documents(case_dir: Path) -> tuple[set[str], str]:
    """The document files the staged manifest accounts for, or why it cannot cross.

    Each listed document must have been fetched from supremecourt.gov (every
    ``|``-joined part of its ``url``); a case with no manifest stages no documents.
    """
    manifest = "record/documents/documents.json"
    if not (case_dir / manifest).is_file():
        return set(), ""
    try:
        entries = json.loads((case_dir / manifest).read_text())
    except (OSError, ValueError):
        return set(), "documents manifest is unreadable"
    if not isinstance(entries, list):
        return set(), "documents manifest is not a list"
    allowed = {manifest}
    for entry in entries:
        kind = entry.get("kind") if isinstance(entry, dict) else None
        if not isinstance(kind, str):
            return set(), "documents manifest entry has no kind"
        if not all(_is_court_url(url) for url in str(entry.get("url", "")).split("|")):
            return set(), f"document {kind!r} was not fetched from supremecourt.gov"
        allowed.add(f"record/documents/{kind}.txt")
    return allowed, ""


def _is_court_url(url: str) -> bool:
    host = (urlsplit(url.strip()).hostname or "").lower()
    return urlsplit(url.strip()).scheme == "https" and (
        host == "supremecourt.gov" or host.endswith(".supremecourt.gov")
    )


def _remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def read_staged_record(
    stage_root: Path, court_id: str, docket_id: int, day: str
) -> tuple[dict[str, Any], list[StagedDocument]] | None:
    """The snapshot and documents ``provision-snapshot`` staged for one case.

    Reads the snapshot for ``day`` exactly: a staged snapshot of another day
    means the corpus moved between the plan and the stage, and the case is
    skipped rather than summarized under a digest it no longer matches. A move
    that keeps the day — documents landing between the plan and the stage — is
    not caught here: the summary is written from the newer documents under the
    plan's digest, so the next plan sees a changed record and writes it once
    more. The cost of that is one extra summary, never a stale one kept. The
    documents are the staged copies, so the contact-detail scrub provisioning
    applies has already run over them.
    """
    paths = CasePaths(stage_root, court_id, docket_id)
    snapshot = paths.snapshot(day)
    if not snapshot.is_file():
        return None
    payload = json.loads(snapshot.read_text())
    documents: list[StagedDocument] = []
    if paths.documents_manifest.is_file():
        for entry in json.loads(paths.documents_manifest.read_text()):
            kind = str(entry["kind"])
            text_path = paths.document(kind)
            if not text_path.is_file():
                continue
            documents.append(
                StagedDocument(
                    kind=kind,
                    text=text_path.read_text(),
                    entry_date=entry.get("entry_date"),
                    stored_truncated=bool(entry.get("truncated", False)),
                )
            )
    return payload, documents


def render_record(
    case_id: str,
    day: str,
    payload: Mapping[str, Any],
    documents: Sequence[StagedDocument],
    cap: int,
) -> str:
    """The user message: the staged record, each document capped and marked."""
    parts = [
        f'<case id="{case_id}" snapshot="{day}">',
        "<snapshot>",
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
        "</snapshot>",
    ]
    for doc in documents:
        text = doc.text
        if len(text) > cap:
            text = text[:cap] + "\n" + TRUNCATION_MARKER.format(shown=cap, total=len(doc.text))
        attrs = f'kind="{doc.kind}"'
        if doc.entry_date:
            attrs += f' entry_date="{doc.entry_date}"'
        if doc.stored_truncated:
            attrs += ' stored_text_truncated="true"'
        parts += [f"<document {attrs}>", text, "</document>"]
    parts.append("</case>")
    return "\n".join(parts)


# --- the model call -------------------------------------------------------------


class SummaryCallError(RuntimeError):
    """The call failed for good: retries exhausted, or a non-retryable status."""


def is_transient(exc: BaseException) -> bool:
    """Throttling, overload and server faults (429, 5xx incl. 529) and network faults."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return isinstance(exc, httpx.RequestError)


#: The longest single backoff wait, seconds — including one a server's
#: ``retry-after`` asks for — so one throttled case cannot sleep its way through
#: the run's time budget.
MAX_BACKOFF_SECONDS = 60.0


class _WaitRetryAfter(wait_base):
    """Honour a numeric ``retry-after`` (capped), else back off exponentially."""

    def __init__(self) -> None:
        self._fallback = wait_exponential(multiplier=2, min=2, max=MAX_BACKOFF_SECONDS)

    def __call__(self, retry_state: RetryCallState) -> float:
        outcome = retry_state.outcome
        exc = outcome.exception() if outcome is not None else None
        if isinstance(exc, httpx.HTTPStatusError):
            header = exc.response.headers.get("retry-after", "")
            try:
                return min(max(float(header), 0.0), MAX_BACKOFF_SECONDS)
            except ValueError:
                pass
        return float(self._fallback(retry_state))


def build_request(config: SummariesConfig, system: str, record: str) -> dict[str, Any]:
    """The request body: the system prompt and the record, and nothing else.

    No ``tools`` key, so the model can retrieve nothing; thinking explicitly
    off, because on the configured model an omitted ``thinking`` runs adaptive
    and a restatement task gains nothing from paying for it.
    """
    return {
        "model": config.model,
        "max_tokens": config.max_output_tokens,
        "system": system,
        "messages": [{"role": "user", "content": record}],
        "thinking": {"type": "disabled"},
    }


@dataclass(frozen=True)
class CallResult:
    text: str
    stop_reason: str
    usage: TokenCounts


def call_messages_api(
    client: httpx.Client,
    api_key: str,
    body: Mapping[str, Any],
    *,
    attempts: int = 5,
    wait: wait_base | None = None,
) -> CallResult:
    """POST one Messages request, retrying transient faults with bounded backoff.

    A throttle's ``retry-after`` is honoured up to :data:`MAX_BACKOFF_SECONDS`;
    otherwise the wait is exponential under the same cap.

    Raises :class:`SummaryCallError` when the call cannot succeed — a
    non-retryable status, or a transient one that outlived every attempt.
    """
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

    def post() -> httpx.Response:
        response = client.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        return response

    retrying = Retrying(
        stop=stop_after_attempt(attempts),
        wait=wait if wait is not None else _WaitRetryAfter(),
        retry=retry_if_exception(is_transient),
        reraise=True,
    )
    try:
        response = retrying(post)
    except httpx.HTTPStatusError as exc:
        raise SummaryCallError(f"HTTP {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise SummaryCallError(f"request failed: {type(exc).__name__}") from exc
    try:
        data = response.json()
        text = "".join(
            str(block.get("text", ""))
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
        usage = data.get("usage") or {}
    except (ValueError, TypeError, AttributeError) as exc:
        raise SummaryCallError(f"unreadable response body: {type(exc).__name__}") from exc
    return CallResult(
        text=text,
        stop_reason=str(data.get("stop_reason", "")),
        usage=TokenCounts(
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
            cache_read_input_tokens=int(usage.get("cache_read_input_tokens") or 0),
            cache_creation_input_tokens=int(usage.get("cache_creation_input_tokens") or 0),
        ),
    )


# --- the body contract ------------------------------------------------------------


def _sections(body: str) -> tuple[list[str], list[str], str]:
    """The body's headings, each section's text, and any text before the first."""
    headings: list[str] = []
    sections: list[list[str]] = []
    preamble: list[str] = []
    for line in body.strip().split("\n"):
        if line.lstrip().startswith("#"):
            headings.append(line.strip())
            sections.append([])
        elif sections:
            sections[-1].append(line)
        else:
            preamble.append(line)
    return headings, ["\n".join(s).strip() for s in sections], "\n".join(preamble).strip()


# Markup a summary body may not carry, because the body reaches a public page
# and its text derives from third-party filings a model read: an injected
# instruction that survived into the output could otherwise place a script, a
# frame, a tracking image or a link there. The contract is three headings and
# plain paragraphs, so every construct below is off-contract whatever it says.
_MARKUP: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("an HTML tag or autolink", re.compile(r"<\s*[A-Za-z/!?]")),
    ("a markdown link or image", re.compile(r"\]\(|!\[")),
    ("a URL", re.compile(r"\b(?:https?|ftp)://|\bwww\.", re.IGNORECASE)),
    ("a list item", re.compile(r"^\s*(?:[-*+]|\d+[.)])\s", re.MULTILINE)),
    ("emphasis markup", re.compile(r"\*\*|__|`")),
)


def body_problems(body: str, *, check_length: bool = True) -> list[str]:
    """Why a summary body breaks the contract; empty when it meets it."""
    problems: list[str] = []
    for label, pattern in _MARKUP:
        if pattern.search(body):
            problems.append(f"carries {label}")
    headings, sections, preamble = _sections(body)
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
        for paragraph in re.split(r"\n\s*\n", text):
            if paragraph.strip().lower().startswith("whether"):
                problems.append(f"a paragraph in {heading!r} opens with 'Whether'")
    if check_length:
        words = sum(len(text.split()) for text in sections)
        low, high = WORD_BAND
        if not low <= words <= high:
            problems.append(f"{words} words, outside the {low}-{high} band")
    return problems


def render_summary(front: CaseSummaryFrontMatter, body: str) -> str:
    """The file: harness-written YAML front matter, then the model's body."""
    header = yaml.safe_dump(
        front.model_dump(mode="json", exclude_none=True),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    return f"---\n{header}---\n\n{body.strip()}\n"


def parse_summary(text: str) -> tuple[CaseSummaryFrontMatter, str]:
    """Split and validate a summary file's front matter; return it with the body."""
    match = _FRONT_MATTER.match(text)
    if match is None:
        raise SummaryFormatError("no YAML front matter block")
    try:
        front = CaseSummaryFrontMatter.model_validate(yaml.safe_load(match.group(1)))
    except (yaml.YAMLError, ValidationError) as exc:
        raise SummaryFormatError(f"front matter: {exc}") from exc
    return front, text[match.end() :]


def summary_file_problems(file: Path, root: Path) -> list[str] | None:
    """Validate one file under a case's ``summaries/`` tree; ``None`` if not one.

    Positional against the case layout, like the provisioning-tree test beside
    it in :mod:`fedcourtsai.validate`: ``cases/<court>/<docket>/summaries/<name>``.
    Checks the name is a snapshot day, the front matter validates, it names the
    case its path spells and the day its name spells, and the body carries the
    three sections in order. Length is not re-checked: that band gates what the
    harness accepts from the model, and a committed summary is judged on shape.
    """
    try:
        parts = file.relative_to(root).parts
    except ValueError:  # pragma: no cover - callers pass paths under root
        return None
    if len(parts) < 5 or parts[0] != "cases" or parts[3] != "summaries":
        return None
    name = _SUMMARY_NAME.match(parts[4]) if len(parts) == 5 else None
    if name is None:
        return ["not a summary file: expected summaries/<YYYY-MM-DD>.md"]
    try:
        front, body = parse_summary(file.read_text())
    except (OSError, UnicodeDecodeError, SummaryFormatError) as exc:
        return [str(exc)]
    problems: list[str] = []
    if parts[2].isdigit():
        expected_case = ids.case_id(parts[1], int(parts[2]))
        if front.case_id != expected_case:
            problems.append(f"case_id {front.case_id!r} does not match the path {expected_case!r}")
    else:
        problems.append(f"docket directory {parts[2]!r} is not a docket id")
    if front.snapshot.isoformat() != name.group(1):
        problems.append(f"snapshot {front.snapshot} does not match the file name")
    problems += body_problems(body, check_length=False)
    return problems


# --- the publish jail --------------------------------------------------------------

# A summary file at the one layout `fedcourtsai.paths` puts it at, repo-relative.
# Matched whole, with a numeric docket segment and a dated name, so nothing else
# under a case — an event, a record file — can pass as one.
_SUMMARY_PATH = re.compile(
    r"data/cases/[a-z0-9._-]+/[0-9]+/summaries/[0-9]{4}-[0-9]{2}-[0-9]{2}\.md"
)


def is_summary_path(rel: str) -> bool:
    """Whether a repo-relative path is a case summary file."""
    if ".." in rel.split("/"):
        return False
    return _SUMMARY_PATH.fullmatch(rel) is not None


def summary_changes(changes: Iterable[tuple[str, str]]) -> tuple[list[str], list[str]]:
    """Split ``(status, path)`` changes into summary writes and everything else.

    A summary write is an addition or a modification of a summary file — the
    only change the summaries lane makes. Anything else (a deletion, a rename,
    any other path) is returned as a violation, each rendered ``<status> <path>``.
    """
    writes: list[str] = []
    violations: list[str] = []
    for status, path in changes:
        if status in {"A", "M"} and is_summary_path(path):
            writes.append(path)
        else:
            violations.append(f"{status} {path}")
    return sorted(writes), sorted(violations)


# --- writing ------------------------------------------------------------------------


@dataclass(frozen=True)
class CaseResult:
    """One case's result: the written path, or why not, and what the call cost.

    A rejected response still cost its tokens, so ``cost_usd`` is set whenever a
    call returned, written or not.
    """

    path: Path | None
    reason: str = ""
    cost_usd: float = 0.0


@dataclass
class SummarizeOutcome:
    """What a summarize run did, case by case."""

    written: list[tuple[str, Path, float]] = field(default_factory=list)
    skipped: list[tuple[str, str, float]] = field(default_factory=list)

    @property
    def cost_usd(self) -> float:
        """Spend on every call that returned, including rejected responses."""
        return sum(c for _, _, c in self.written) + sum(c for _, _, c in self.skipped)


def summarize_case(  # noqa: PLR0913 - one case's inputs, each load-bearing
    case: SummaryPlanCase,
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
) -> CaseResult:
    """Write one planned case's summary, or say why not."""
    target = CasePaths(data_root, case.court_id, case.docket_id).summary(case.snapshot.isoformat())
    if target.is_file() and committed_digest(target) == case.record_digest:
        return CaseResult(None, "already summarized from this record")
    staged = read_staged_record(
        stage_root, case.court_id, case.docket_id, case.snapshot.isoformat()
    )
    if staged is None:
        return CaseResult(
            None,
            f"no staged snapshot for {case.snapshot.isoformat()} (corpus moved since the plan?)",
        )
    payload, documents = staged
    if LIVE_SHAPE_KEY not in payload:
        return CaseResult(None, "staged snapshot is not the Court's own docket JSON")
    record = render_record(
        case.case_id, case.snapshot.isoformat(), payload, documents, config.max_document_chars
    )
    try:
        result = call_messages_api(
            client, api_key, build_request(config, system_prompt, record), wait=wait
        )
    except SummaryCallError as exc:
        return CaseResult(None, str(exc))
    cost = estimate_cost_usd(config.model, result.usage)
    refusal = _refusal(result, str(target), api_key)
    if refusal:
        return CaseResult(None, refusal, cost)
    front = CaseSummaryFrontMatter(
        case_id=case.case_id,
        snapshot=case.snapshot,
        record_digest=case.record_digest,
        model=config.model,
        prompt_digest=prompt_sha,
        generated_at=now.astimezone(UTC).replace(microsecond=0),
        usage=CaseSummaryUsage(
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            estimated_cost_usd=round(cost, 6),
        ),
    )
    write_text(target, render_summary(front, result.text))
    return CaseResult(target, cost_usd=cost)


def _refusal(result: CallResult, rel: str, api_key: str) -> str:
    """Why a response is not written; empty when it meets the contract."""
    if result.stop_reason != "end_turn":
        return f"stop_reason {result.stop_reason!r}"
    problems = body_problems(result.text)
    findings = secretscan.scan_lines(rel, result.text.split("\n"), [api_key] if api_key else [])
    if findings:
        problems.append(f"secret scan: {len(findings)} finding(s)")
    return "rejected: " + "; ".join(problems) if problems else ""


def summarize_plan(  # noqa: PLR0913 - the run's inputs, each load-bearing
    plan: SummaryPlan,
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
    """Summarize every planned case; a case that fails is skipped, never fatal.

    ``deadline`` is the run's time budget: once ``now()`` passes it, every case
    not yet started is skipped as deferred rather than begun, so the run
    returns in time for its caller to collect what was written. A deferred case
    is still owed, and the next plan picks it up.

    Refuses a plan written for another model than the configured one: the plan
    was approved at that model's price, and a config change since is a new plan.
    """
    if plan.model != config.model:
        raise ValueError(
            f"plan was made for model {plan.model!r}, config now names {config.model!r}"
        )
    if config.model not in MODEL_RATES:
        raise ValueError(f"model {config.model!r} has no rate in pricing.MODEL_RATES")
    system_prompt = prompt_bytes.decode("utf-8")
    prompt_sha = prompt_digest(prompt_bytes)
    outcome = SummarizeOutcome()
    for case in plan.cases:
        if deadline is not None and now() >= deadline:
            outcome.skipped.append((case.case_id, "deferred: time budget reached", 0.0))
            continue
        result = summarize_case(
            case,
            stage_root=stage_root,
            data_root=data_root,
            config=config,
            system_prompt=system_prompt,
            prompt_sha=prompt_sha,
            client=client,
            api_key=api_key,
            now=now(),
            wait=wait,
        )
        if result.path is None:
            outcome.skipped.append((case.case_id, result.reason, result.cost_usd))
        else:
            outcome.written.append((case.case_id, result.path, result.cost_usd))
    return outcome


def render_outcome_report(outcome: SummarizeOutcome, planned: int) -> str:
    """The job-summary markdown for a summarize run."""
    lines = [
        "## summarize — result",
        "",
        f"- planned: {planned}",
        f"- written: **{len(outcome.written)}**",
        f"- skipped: {len(outcome.skipped)}",
        f"- cost of every call that returned, from response usage: **${outcome.cost_usd:.2f}**",
        "",
    ]
    if outcome.skipped:
        lines += ["| skipped case | reason |", "|---|---|"]
        lines += [f"| `{case}` | {reason} |" for case, reason, _ in outcome.skipped]
    return "\n".join(lines) + "\n"
