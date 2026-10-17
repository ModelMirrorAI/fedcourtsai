"""The generated part of a promotion PR's body.

A promotion batch is assembled from the feature PRs merged into `staging` since
the last promotion. Each of them is asked (AGENTS.md) to carry its effect check
as a handover note, and the promotion body is where those notes meet, beside
the gate's state and what is still owed after the merge. Writing that by hand
is the mechanical part of a promotion; this module writes it, and the
promotion train (the `promotion-prep` workflow) keeps it current on each
`promote/<date>` candidate it cuts, with the train's latest step beside the
gate. A hand-opened `staging` → `main` promotion renders the same batch with
the manual next steps instead.

The block sits between two HTML-comment markers, so everything a maintainer
writes outside them survives a refresh: the narrative stays theirs, the lists
stay in step with `staging`.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from pydantic import BaseModel

BEGIN = "<!-- promotion-prep:begin -->"
END = "<!-- promotion-prep:end -->"

#: Written once into a promotion train candidate's body, outside the
#: generated block, when the train marks it ready (`promotion_train`).
READY_MARKER = "<!-- promotion-train:marked-ready -->"

# A handover note is any heading that names an effect check, at any level and in
# any of the phrasings feature PRs use ("Effect check, after the next
# promotion", "Handover: effect check for the promotion", "Post-promotion effect
# check", "Promotion and effect check").
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_EFFECT_HEADING = re.compile(r"effect[\s-]+checks?\b", re.IGNORECASE)
# What ends a section besides the next heading: the tool footer every agent PR
# carries, and an edit note appended after it.
_FOOTER = re.compile(r"^(?:🤖 Generated with|https://claude\.ai/code/|_Body edited)")
# A fence opener or closer. Inside a fence a `#` line is a shell comment, not a
# heading, so neither headings nor the footer are read there.
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
# An inline code span, which a mention escape must leave alone: an entity
# inside backticks renders literally.
_CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
# A mention: `@` opening a login, not inside a word (an email address).
_MENTION = re.compile(r"(?<![\w@])@(?=[A-Za-z0-9])")
# A digit run in a gate verdict line, which varies between refreshes (run
# counts, run ids) without the batch changing.
_DIGITS = re.compile(r"\d+")

# GitHub refuses a PR body over 65,536 characters. The block keeps well under
# that, so prose the maintainer adds outside it still fits.
BLOCK_BUDGET = 50_000


class BatchPR(BaseModel):
    """One feature PR merged into `staging` since the last promotion."""

    number: int
    title: str
    body: str = ""


class GateCheck(BaseModel):
    """One promotion-gate stage as the prep job read it."""

    name: str
    ok: bool
    detail: str = ""


class Batch(BaseModel):
    """Everything the generated block is rendered from."""

    staging_sha: str
    main_sha: str
    prs: list[BatchPR]
    sync_prs: list[int] = []
    # `main`→`staging` sync PRs still open (and so possibly armed to
    # auto-merge) when the job read the batch.
    open_sync_prs: list[int] = []
    # First-parent staging commits no merged PR names: a direct push (the
    # admin escape hatch), whose change no feature PR's note covers.
    unmapped_commits: list[str] = []
    gate: list[GateCheck] = []
    owed_fills: list[str] = []
    # The promotion's head ref: `staging` for a hand-opened promotion, or the
    # promotion train's frozen `promote/<date>` candidate, whose head is
    # `staging_sha` for good.
    head_ref: str = "staging"
    # The train's latest step on a candidate, one line (`fedcourts
    # promotion-train-step`'s reason).
    train_status: str = ""

    @property
    def is_candidate(self) -> bool:
        """Whether this is a promotion train candidate rather than `staging` itself."""
        return self.head_ref != "staging"


class _Fence:
    """Open-fence state: a fence closes only on a run of its own character at
    least as long as the one that opened it, so the two kinds cannot close each
    other."""

    def __init__(self) -> None:
        self.opener: str | None = None

    def step(self, line: str) -> bool:
        """Update the state for ``line``; return whether it is a fence line."""
        match = _FENCE.match(line)
        if match is None:
            return False
        run = match.group(1)
        if self.opener is None:
            self.opener = run
            return True
        if run[0] == self.opener[0] and len(run) >= len(self.opener):
            self.opener = None
            return True
        return False

    @property
    def open(self) -> bool:
        return self.opener is not None


def extract_effect_check(body: str) -> str | None:
    """The PR's effect-check section, without its heading, or ``None``.

    The section runs from the first heading that names an effect check to the
    next heading at the same or a higher level, or to the tool footer. Inside a
    fenced block no line is read as a heading or the footer. An empty section
    is ``None``: a heading with nothing under it is not a check.
    """
    lines = body.replace("\r\n", "\n").split("\n")
    outer = _Fence()
    for index, line in enumerate(lines):
        if outer.step(line) or outer.open:
            continue
        heading = _HEADING.match(line)
        if heading is None or not _EFFECT_HEADING.search(heading.group(2)):
            continue
        level = len(heading.group(1))
        section: list[str] = []
        inner = _Fence()
        for following in lines[index + 1 :]:
            if not inner.step(following) and not inner.open:
                nested = _HEADING.match(following)
                ends = nested is not None and len(nested.group(1)) <= level
                if ends or _FOOTER.match(following):
                    break
            section.append(following)
        if inner.opener is not None:
            # A section cut off inside a fence would leave the rest of the
            # generated block rendered as code, so close it with its own kind.
            section.append(inner.opener)
        text = "\n".join(section).strip()
        return _unmark(text) or None
    return None


def _unmark(text: str) -> str:
    """PR text with the block's own markers — and the train's ready marker —
    defused, so it can neither forge nor cut the generated block, nor read as
    the train having marked the candidate ready. Nothing else is touched: a
    command's `@` or `<!--` must survive verbatim to be copied."""
    for marker in (BEGIN, END, READY_MARKER):
        text = text.replace(marker, marker.replace("<!--", "&lt;!--"))
    return text


def _quote_note(text: str) -> str:
    """A handover note as a blockquote, with mentions outside code escaped.

    The quote is a container, so an unclosed `<!--` in a note ends with it
    rather than hiding the rest of the block. A mention outside code would
    notify its target on every refresh; inside a fence or a code span it is a
    command's `@` and is kept verbatim, since that is what a reader copies.
    """
    fence = _Fence()
    out = []
    for raw in text.split("\n"):
        line = raw if fence.step(raw) or fence.open else _escape_mentions(raw)
        out.append(f"> {line}" if line else ">")
    return "\n".join(out)


def _escape_mentions(line: str) -> str:
    parts = []
    last = 0
    for span in _CODE_SPAN.finditer(line):
        parts.append(_MENTION.sub("&#64;", line[last : span.start()]))
        parts.append(span.group(0))
        last = span.end()
    parts.append(_MENTION.sub("&#64;", line[last:]))
    return "".join(parts)


def _title(title: str) -> str:
    """A PR title for the block: markers defused and `@` escaped, since a
    mention in a heading or list item would notify on every refresh."""
    return _unmark(title).replace("@", "&#64;")


def _gate_lines(batch: Batch) -> list[str]:
    if not batch.gate:
        return ["- not read this run"]
    lines = []
    for check in batch.gate:
        verdict = "**clean**" if check.ok else "**not yet**"
        detail = f" — {check.detail}" if check.detail else ""
        lines.append(f"- {check.name}: {verdict}{detail}")
    return lines


def _next_step(batch: Batch) -> list[str]:
    """What the maintainer does next, in the order that keeps evidence valid.

    Marking the PR ready comes first: it stops `sync-staging` moving the head,
    and the integration evidence is per-SHA, so a gate run dispatched while the
    PR is still a draft can be invalidated by the next sync.
    """
    if not batch.gate:
        return []
    failing = {check.name for check in batch.gate if not check.ok}
    syncs = ", ".join(f"#{n}" for n in batch.open_sync_prs)
    sync_line = (
        [
            f"- let the open sync PR {syncs} land (or close it) first: marking ready stops a new",
            "  sync, not one already armed, and its merge would move the head.",
        ]
        if batch.open_sync_prs
        else []
    )
    if not failing:
        return [
            "**Next:** the gate reads clean at this head. If this PR is still a draft, mark",
            "it ready (which stops new syncs moving the head), then:",
            *sync_line,
            "- edit the body once to re-run `promotion-gate`, and merge with a **merge commit**.",
        ]
    lines = [
        "**Next:** mark this PR ready for review first (that stops `sync-staging`",
        "opening a new sync under the evidence), then:",
        *sync_line,
    ]
    if "quiescence" in failing:
        lines.append("- let the running predict/evaluate/back-test rounds finish (or reject")
        lines.append("  their holds); the gate needs those lanes idle.")
    if "freshness" in failing:
        lines.append(
            f"- run the integration gate at this head: `gh workflow run integration-test.yml"
            f" --ref staging -f scenario=gate` (staging `{batch.staging_sha[:9]}`), or"
            " `offline-gate` plus the `promote:skip-engine-smoke` label for a batch that"
            " cannot affect a cell."
        )
    lines.append("- then edit the body once to re-run `promotion-gate`, and merge with a")
    lines.append("  **merge commit**.")
    return lines


def _train_next_step(batch: Batch) -> list[str]:
    """What the maintainer does on a promotion train candidate.

    The head is frozen, so nothing the maintainer does here can be invalidated
    by a sync or a later staging merge, and the train does every mechanical
    step; the maintainer's one act is the approval of this head.
    """
    sha = batch.staging_sha[:9]
    return [
        f"**Train:** {_unmark(batch.train_status) or 'not yet stepped'}",
        "",
        f"**Next (maintainer):** read the batch and approve this PR at `{sha}`. The "
        "train then merges it with a **merge commit** once the integration `gate` run, "
        "the required checks and the registry gate hold at this head and no "
        "predict/evaluate/back-test round is in flight. Merging it yourself instead is "
        "fine. To stop it, request changes or close it: a closed candidate is not re-cut "
        "at the same staging tip, and the next one is cut once staging moves.",
    ]


def _header(batch: Batch, *, drafted_at: str) -> list[str]:
    """The block's stamp, gate status and next step: the train's for a candidate."""
    if batch.is_candidate:
        return [
            f"_Drafted by the promotion train at {drafted_at} for `{batch.head_ref}` at "
            f"`{batch.staging_sha[:9]}` over main `{batch.main_sha[:9]}`. The branch was cut "
            "from staging and never moves, so the integration evidence and an approval of "
            "this head stay valid while staging carries on. The train regenerates the block "
            "between the markers while this PR is open; write anything else outside it._",
            "",
            f"**Gate status** (`{batch.head_ref}` at `{batch.staging_sha[:9]}`):",
            *_gate_lines(batch),
            "",
            *_train_next_step(batch),
        ]
    return [
        f"_Drafted by `fedcourts promotion-body` at {drafted_at} for staging "
        f"`{batch.staging_sha[:9]}` over main `{batch.main_sha[:9]}`. Write anything "
        "else outside the markers; the gate status and next step below are as of this "
        "stamp._",
        "",
        f"**Gate status** (staging `{batch.staging_sha[:9]}`):",
        *_gate_lines(batch),
        "",
        *_next_step(batch),
    ]


def render(batch: Batch, *, drafted_at: str) -> str:
    """The generated block, markers included."""
    header = _header(batch, drafted_at=drafted_at)
    out = [
        BEGIN,
        *header,
        "",
        "## The batch",
        "",
    ]
    if batch.prs:
        out.extend(f"- #{pr.number}: {_title(pr.title)}" for pr in batch.prs)
    else:
        out.append("- no feature PR found between main and staging")
    if batch.sync_prs:
        out.append("- Sync: " + ", ".join(f"#{n}" for n in batch.sync_prs))
    if batch.unmapped_commits:
        out.append(
            "- Pushed to staging with no PR (no handover note covers it): "
            + ", ".join(f"`{sha[:9]}`" for sha in batch.unmapped_commits)
        )
    out += ["", "## Effect checks", ""]
    missing = []
    deferred: list[BatchPR] = []
    used = sum(len(line) + 1 for line in out)
    for pr in batch.prs:
        check = extract_effect_check(pr.body)
        if check is None:
            missing.append(pr)
            continue
        section = [f"### #{pr.number}: {_title(pr.title)}", "", _quote_note(check), ""]
        size = sum(len(line) + 1 for line in section)
        if deferred or used + size > BLOCK_BUDGET:
            deferred.append(pr)
            continue
        out += section
        used += size
    if deferred:
        out.append(
            f"…{len(deferred)} more effect-check note(s), too long to copy here; read them on "
            + ", ".join(f"#{pr.number}" for pr in deferred)
            + "."
        )
        out.append("")
    if missing:
        out.append(
            "**No effect-check note found.** Add one to the feature PR's description (the "
            "next refresh picks it up) or write it below the end marker, or say there why "
            "none applies:"
        )
        out.extend(f"- #{pr.number}: {_title(pr.title)}" for pr in missing)
        out.append("")
    out += [
        "## After the merge",
        "",
        "1. Tag `promotion/<YYYY-MM-DD>` on the merge commit (`-2` for a same-day second batch).",
    ]
    if batch.owed_fills:
        out.append("2. Fill the freeze-record placeholders this batch owes:")
        out.extend(f"   - `{fill.strip()}`" for fill in batch.owed_fills)
        out.append("3. Run the effect checks above and record what they printed.")
    else:
        out.append("2. Run the effect checks above and record what they printed.")
    out.append(END)
    return "\n".join(out)


def splice(existing: str, block: str) -> str:
    """Replace the generated block in ``existing``, or put it first if absent.

    Text outside the markers is kept as written, less trailing whitespace, so a
    body that round-trips through the API and back is stable rather than
    growing a blank line per refresh. A body with a begin marker and no end
    marker is treated as having no block, so a damaged body never loses what
    follows the stray marker.
    """
    existing = existing.replace("\r\n", "\n").rstrip()
    start = existing.find(BEGIN)
    end = existing.find(END, start + len(BEGIN)) if start != -1 else -1
    if start == -1 or end == -1:
        return block if not existing else f"{block}\n\n{existing}"
    return (existing[:start] + block + existing[end + len(END) :]).rstrip()


_GATE_LINE = re.compile(r"^- (?:quiescence|freshness|registry): \*\*")


def same_body(left: str, right: str) -> bool:
    """Whether two bodies differ only in the drafted-at stamp, a gate line's
    counts, or trailing space.

    Every body edit re-runs CI on the PR, so a refresh that would change nothing
    else is not written.
    """

    def norm(body: str) -> list[str]:
        return [
            # A gate verdict line's digits (run counts, run ids) change between
            # reads of an unchanged batch; the verdict itself does not.
            _DIGITS.sub("N", line.rstrip()) if _GATE_LINE.match(line) else line.rstrip()
            for line in body.replace("\r\n", "\n").rstrip().split("\n")
            if not line.startswith(
                ("_Drafted by `fedcourts promotion-body`", "_Drafted by the promotion train")
            )
        ]

    return norm(left) == norm(right)


def batch_prs(prs: Sequence[BatchPR]) -> tuple[list[BatchPR], list[int]]:
    """Split a batch into feature PRs and the main→staging sync PRs, by title.

    The sync workflow opens its PR under one fixed title, so a title match is
    the whole test; ordered by number, each PR once.
    """
    seen: dict[int, BatchPR] = {}
    for pr in prs:
        seen.setdefault(pr.number, pr)
    ordered = sorted(seen.values(), key=lambda pr: pr.number)
    sync = [pr.number for pr in ordered if pr.title == "chore: sync main into staging"]
    features = [pr for pr in ordered if pr.number not in sync]
    return features, sync
