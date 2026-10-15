"""The corpus-check lane's decisions: who may ask, what may run, and what is posted.

`corpus-check.yml` runs a check a same-repository pull request declares, at the
PR's head, against the production corpus read-only, once the maintainer
approves the `corpus-check` deployment (docs/corpus-check.md). Its three jobs
are thin wrappers over this module, so every rule here is testable without the
Actions API:

- **The plan job** lists the open PRs and hands them to
  :func:`candidate_requests` — a fenced ``corpus-check`` block, a head in this
  repository, an author on the maintainer-owned requester list
  (``config/corpus-check.yaml``) — then the candidates' comments to
  :func:`select_request`, which takes the oldest whose head SHA carries no
  result comment from this workflow's own bot. It pins the SHA and the command
  as job outputs and renders both to the run summary, the page the approver
  lands on (:func:`render_plan_summary`).
- **The run job** hands the pinned command to :func:`parse_command` again and
  then to :func:`run_check`, which executes it without a shell, its output to
  a file rather than the public job log, under a hard timeout, and reads back
  only the summary file the check wrote (:func:`read_summary`).
- **The post job** treats every value the run job emitted as untrusted text
  and renders one comment from them (:func:`render_comment`): fenced, with
  mentions neutralised, and clamped under GitHub's comment limit, which
  refuses an over-long body rather than truncating it.

The command grammar narrows mistakes, not attacks: either accepted form runs the
PR's own code, which can do anything the job can. The approval and the
read-only role's trust are what bound it.
"""

from __future__ import annotations

import base64
import binascii
import contextlib
import os
import re
import shlex
import shutil
import signal
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

#: The requester list's own file, apart from ``tracking.yaml`` because it decides
#: whose PR code runs with a corpus credential (``.github/CODEOWNERS``).
CONFIG_FILENAME = "corpus-check.yaml"

#: The identity every result comment is posted as: the post job's own
#: ``GITHUB_TOKEN``. Brackets cannot appear in a user login, so no account can
#: wear it; a comment from anyone else carrying the marker does not count.
BOT_LOGIN = "github-actions[bot]"

#: The block a PR body declares its check in.
BLOCK_INFO = "corpus-check"

#: Where the check writes what it means to report, relative to its working
#: directory (the PR head's checkout). Exported as ``CHECK_SUMMARY`` too; the
#: fixed name is what lets a ``uv run fedcourts …`` command, which gets no shell
#: to expand a variable, point a ``--summary-out``-style option at it.
SUMMARY_FILENAME = "corpus-check-summary.md"

#: The summary the run job emits, in UTF-8 bytes (the job's outputs are capped
#: at 1 MB in all, and the comment at 65,536 characters).
SUMMARY_LIMIT_BYTES = 50_000

#: GitHub's comment limit, in characters. An over-long body is refused, not
#: truncated, so the rendered comment must fit with room to spare.
COMMENT_LIMIT = 65_536
_COMMENT_MARGIN = 512

#: The longest command line accepted, and the most arguments.
COMMAND_MAX_CHARS = 400
COMMAND_MAX_ARGS = 40

#: The exit code reported for a check the timeout ended (coreutils' convention).
TIMEOUT_EXIT = 124
#: The exit code reported when the command's program could not be started.
NOT_FOUND_EXIT = 127

#: Every argument is drawn from this set: no quoting, no expansion, no
#: redirection, no separator — so a command means the same with or without a
#: shell, and splitting on spaces is the whole parse.
_ARG = re.compile(r"[A-Za-z0-9_./:=,+-]+")
_ARG_CHARSET = "A-Z a-z 0-9 _ . / : = , + -"
_SCRIPT = re.compile(r"scripts/checks/[A-Za-z0-9_-]+\.py")
_SHA = re.compile(r"[0-9a-f]{40}")
_LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})(?:\[bot\])?")
_FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,})" + re.escape(BLOCK_INFO) + r"[ \t]*$")
_MARKER = "<!-- corpus-check-result sha={sha} -->"

#: The run job's result values the post job can name; anything else is unknown.
RunResult = Literal["success", "failure", "cancelled", "skipped"]
_RUN_RESULTS: frozenset[str] = frozenset({"success", "failure", "cancelled", "skipped"})

#: Removed from the check's environment. The file-command paths are how a step
#: writes the run summary, its outputs and later steps' environment; the OIDC
#: request pair is how a step mints a token. A check needs none of them, so an
#: honest one cannot write to them by accident. This is hygiene, not a
#: boundary: the check runs as the job's own user and can still reach them.
_SCRUBBED_ENV = (
    "GITHUB_STEP_SUMMARY",
    "GITHUB_OUTPUT",
    "GITHUB_ENV",
    "GITHUB_PATH",
    "GITHUB_STATE",
    "ACTIONS_ID_TOKEN_REQUEST_URL",
    "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    "VIRTUAL_ENV",
)

#: Values replaced in the summary before it leaves the job: the session the
#: read-only role issued, the job's tokens, and the corpus estate's address,
#: which is kept out of band. A guard against an honest check that prints its
#: environment, not against one that encodes a value first.
REDACTED_ENV = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    "ACTIONS_RUNTIME_TOKEN",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "FEDCOURTS_CORPUS_BASE_URL",
    "CORPUS_BASE_URL",
)
_REDACTION = "[redacted]"


class CommandRefused(ValueError):
    """A declared command outside the grammar; the message is ours, never the PR's text."""


class CorpusCheckConfig(BaseModel):
    """Who may request a corpus check (``config/corpus-check.yaml``).

    A request runs PR-head code with a corpus credential once approved, so the
    list is maintainer-owned. Empty — the default when the file is absent —
    means nobody may, and every request is passed over.
    """

    model_config = ConfigDict(extra="forbid")

    requesters: list[str] = Field(default_factory=list)

    @field_validator("requesters")
    @classmethod
    def _logins(cls, value: list[str]) -> list[str]:
        for login in value:
            if not _LOGIN.fullmatch(login):
                raise ValueError(f"not a GitHub login: {login!r}")
        return value


def load_config(config_root: Path) -> CorpusCheckConfig:
    """Read the requester list from ``config_root/corpus-check.yaml``; absent is empty."""
    path = config_root / CONFIG_FILENAME
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    return CorpusCheckConfig.model_validate(data or {})


def extract_block(body: str | None) -> str | None:
    """The one line inside the body's fenced ``corpus-check`` block, or None for no block.

    Raises :class:`CommandRefused` for a block that cannot be read as one
    command: more than one block, an unclosed one, or anything but exactly one
    non-blank line inside it.
    """
    if not body:
        return None
    lines = body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: list[list[str]] = []
    index = 0
    while index < len(lines):
        opened = _FENCE_OPEN.match(lines[index])
        index += 1
        if opened is None:
            continue
        width = len(opened.group("fence"))
        closing = re.compile(r"^ {0,3}`{" + str(width) + r",}[ \t]*$")
        content: list[str] = []
        while index < len(lines) and not closing.match(lines[index]):
            content.append(lines[index])
            index += 1
        if index >= len(lines):
            raise CommandRefused("the corpus-check block is never closed")
        index += 1
        blocks.append(content)
    if not blocks:
        return None
    if len(blocks) > 1:
        raise CommandRefused("the body declares more than one corpus-check block")
    filled = [line for line in blocks[0] if line.strip()]
    if len(filled) != 1:
        raise CommandRefused(
            f"the corpus-check block holds {len(filled)} non-blank lines; it takes exactly one"
        )
    return filled[0].strip(" ")


def parse_command(command: str) -> list[str]:
    """Split a declared command into its argv, refusing anything outside the two forms.

    ``uv run fedcourts <subcommand> [args…]`` or ``uv run python
    scripts/checks/<name>.py [args…]``, one line of printable ASCII, arguments
    separated by spaces and each drawn from a closed character set — so no
    quoting, expansion, redirection or command separator exists to interpret,
    and the split is the same with or without a shell.
    """
    if not command:
        raise CommandRefused("the command is empty")
    if len(command) > COMMAND_MAX_CHARS:
        raise CommandRefused(f"the command is longer than {COMMAND_MAX_CHARS} characters")
    if any(not (char.isascii() and char.isprintable()) for char in command):
        raise CommandRefused("the command carries a non-printable or non-ASCII character")
    argv = [token for token in command.split(" ") if token]
    if len(argv) > COMMAND_MAX_ARGS:
        raise CommandRefused(f"the command has more than {COMMAND_MAX_ARGS} arguments")
    for position, token in enumerate(argv, start=1):
        if not _ARG.fullmatch(token):
            raise CommandRefused(
                f"argument {position} carries a character outside [{_ARG_CHARSET}]"
            )
    if argv[:3] == ["uv", "run", "fedcourts"]:
        if len(argv) < 4:
            raise CommandRefused("`uv run fedcourts` needs a subcommand")
    elif argv[:3] == ["uv", "run", "python"]:
        if len(argv) < 4 or not _SCRIPT.fullmatch(argv[3]):
            raise CommandRefused(
                "`uv run python` runs only scripts/checks/<name>.py, name in [A-Za-z0-9_-]"
            )
    else:
        raise CommandRefused(
            "the command must start `uv run fedcourts` or `uv run python scripts/checks/`"
        )
    # The character set leaves shlex nothing to interpret; say so in code, so
    # widening the set without revisiting the parse fails here.
    if shlex.split(command) != argv:  # pragma: no cover - unreachable by construction
        raise CommandRefused("the command does not split the same way with and without a shell")
    return argv


class Request(BaseModel):
    """One PR's corpus-check request: runnable (``command``) or refused (``refusal``)."""

    pr: int
    sha: str
    author: str
    base_ref: str
    created_at: str
    command: str | None = None
    refusal: str | None = None


class Passed(BaseModel):
    """A PR with a corpus-check block the plan passes over without answering."""

    pr: int
    reason: str


def _get(data: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(data, Mapping):
            return None
        data = data.get(key)
    return data


def flatten_pages(document: Any) -> list[Mapping[str, Any]]:
    """The objects of a REST listing: one array, or ``gh api --paginate --slurp``'s pages."""
    items: list[Mapping[str, Any]] = []
    stack = [document]
    while stack:
        current = stack.pop()
        if isinstance(current, list):
            stack.extend(reversed(current))
        elif isinstance(current, Mapping):
            items.append(current)
    return items


def candidate_requests(
    prs: Iterable[Mapping[str, Any]], *, repo: str, requesters: Sequence[str]
) -> tuple[list[Request], list[Passed]]:
    """The requests the plan may answer, oldest first, and the blocks it passes over.

    A request is answerable only from a PR whose head is in ``repo`` itself
    (a fork's code never runs) and whose author is on ``requesters``; the rest
    are passed over without a comment, so the lane is no channel for anyone
    else. An answerable request with an unreadable block or a command outside
    the grammar is kept, refused, so its author is told why.
    """
    allowed = {login.casefold() for login in requesters}
    requests: list[Request] = []
    passed: list[Passed] = []
    for pr in prs:
        number = pr.get("number")
        if not isinstance(number, int) or isinstance(number, bool):
            continue
        body = pr.get("body")
        try:
            line = extract_block(body if isinstance(body, str) else None)
            refusal = None
        except CommandRefused as exc:
            line, refusal = None, str(exc)
        if line is None and refusal is None:
            continue
        head_repo = _get(pr, "head", "repo", "full_name")
        author = _get(pr, "user", "login")
        sha = _get(pr, "head", "sha")
        if not isinstance(head_repo, str) or head_repo.casefold() != repo.casefold():
            passed.append(Passed(pr=number, reason="head is not in this repository"))
            continue
        if not isinstance(author, str) or not _LOGIN.fullmatch(author):
            passed.append(Passed(pr=number, reason="author login unreadable"))
            continue
        if author.casefold() not in allowed:
            passed.append(Passed(pr=number, reason="author is not on the requester list"))
            continue
        if not isinstance(sha, str) or not _SHA.fullmatch(sha):
            passed.append(Passed(pr=number, reason="head SHA unreadable"))
            continue
        command = None
        if line is not None:
            try:
                parse_command(line)
                command = line
            except CommandRefused as exc:
                refusal = str(exc)
        base_ref = _get(pr, "base", "ref")
        created_at = pr.get("created_at")
        requests.append(
            Request(
                pr=number,
                sha=sha,
                author=author,
                base_ref=base_ref if isinstance(base_ref, str) else "",
                created_at=created_at if isinstance(created_at, str) else "",
                command=command,
                refusal=refusal,
            )
        )
    requests.sort(key=lambda request: (request.created_at, request.pr))
    passed.sort(key=lambda item: item.pr)
    return requests, passed


def result_marker(sha: str) -> str:
    """The hidden first line of a result comment, naming the head SHA it answers."""
    return _MARKER.format(sha=sha)


def is_answered(comments: Iterable[Mapping[str, Any]], sha: str) -> bool:
    """Whether this workflow's bot has already posted a result for ``sha``."""
    marker = result_marker(sha)
    for comment in comments:
        if _get(comment, "user", "login") != BOT_LOGIN or _get(comment, "user", "type") != "Bot":
            continue
        body = comment.get("body")
        if isinstance(body, str) and body.startswith(marker):
            return True
    return False


def select_request(
    requests: Sequence[Request], comments: Mapping[int, Iterable[Mapping[str, Any]]]
) -> Request | None:
    """The oldest request whose head SHA has no result yet; None when all are answered.

    A request whose comments were not read is an error, not "unanswered": the
    caller must hand in every candidate's comments, or the same SHA would be
    planned again on every poll.
    """
    for request in requests:
        if request.pr not in comments:
            raise KeyError(f"no comments were read for PR #{request.pr}")
        if not is_answered(comments[request.pr], request.sha):
            return request
    return None


def plan_outputs(request: Request | None) -> dict[str, str]:
    """The plan job's outputs, each a single line by construction."""
    if request is None:
        return {"found": "false"}
    return {
        "found": "true",
        "pr": str(request.pr),
        "sha": request.sha,
        "author": request.author,
        "command": request.command or "",
        "refusal": request.refusal or "",
    }


def neutralize_mentions(text: str) -> str:
    """Break every ``@`` so no login or team in the text is notified."""
    return text.replace("@", "@\u200b")


def fence(text: str, info: str = "text") -> str:
    """``text`` in a code fence longer than any backtick run inside it."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    ticks = "`" * max(3, longest + 1)
    return f"{ticks}{info}\n{text}\n{ticks}"


def _printable(text: str) -> str:
    """Drop control characters other than newline and tab."""
    return "".join(
        char for char in text if char in "\n\t" or not (ord(char) < 32 or 127 <= ord(char) < 160)
    )


def clamp_utf8(text: str, limit_bytes: int) -> tuple[str, bool]:
    """``text`` cut to at most ``limit_bytes`` of UTF-8 on a character boundary."""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit_bytes:
        return text, False
    return encoded[:limit_bytes].decode("utf-8", errors="ignore"), True


def render_plan_summary(
    request: Request | None,
    passed: Sequence[Passed],
    *,
    server_url: str,
    repo: str,
    candidates: int,
) -> str:
    """The run summary the approver reads before approving the `corpus-check` deployment.

    The approval page shows a workflow and a ref, not a diff, so this names
    exactly what approval runs: the PR, its head SHA, its author and the
    command, fenced and with mentions broken.
    """
    lines = ["## corpus-check — plan", ""]
    if request is None:
        lines.append(
            f"No request to answer: {candidates} request(s) from listed authors, "
            + "every head SHA already answered."
        )
    elif request.refusal is not None:
        lines += [
            f"**PR #{request.pr}** at `{request.sha}` by `{request.author}` is **refused**: "
            + f"{request.refusal}.",
            "",
            "Nothing runs. The post job tells the PR why; a new push re-asks.",
        ]
    else:
        lines += [
            f"**PR #{request.pr}** (`{request.author}`, into `{request.base_ref}`) "
            + f"at head `{request.sha}`.",
            "",
            "Approving the `corpus-check` deployment runs exactly this command, at exactly "
            + "this commit, with the production corpus read-only:",
            "",
            fence(neutralize_mentions(request.command or "")),
            "",
            f"- the commit: {server_url}/{repo}/commit/{request.sha}",
            f"- the PR's changes: {server_url}/{repo}/pull/{request.pr}/files",
            "",
            "The check's code can read everything the read-only role reads and post what "
            + "it chooses to the PR (docs/corpus-check.md, *What it gives up*).",
        ]
    if passed:
        lines += ["", "Passed over (no comment is posted):", ""]
        lines += [f"- #{item.pr}: {item.reason}" for item in passed]
    return "\n".join(lines) + "\n"


def decode_b64(value: str, limit_bytes: int) -> tuple[str, str | None]:
    """A run-job output decoded to text; the second value says why it is not shown."""
    if not value:
        return "", None
    try:
        raw = base64.b64decode(value.strip(), validate=True)
    except (binascii.Error, ValueError):
        return "", "the run's output was not valid base64, so nothing is shown"
    text = _printable(raw.decode("utf-8", errors="replace"))
    text, _ = clamp_utf8(text, limit_bytes)
    return text, None


def parse_exit_code(value: str) -> int | None:
    """The run job's exit code, or None when it is not a plain integer."""
    return int(value) if re.fullmatch(r"-?[0-9]{1,3}", value.strip()) else None


def outcome(*, refusal: str, run_result: str, exit_code: str, timed_out: str) -> tuple[str, str]:
    """The comment's short status and its one-line explanation."""
    if refusal:
        return "refused", f"Not run: {refusal}."
    result = run_result if run_result in _RUN_RESULTS else "unknown"
    if result != "success":
        return (
            "not run",
            f"The run job ended `{result}` before it reported a result: an approval "
            + "rejected or left to expire, a cancelled run, or a failed setup step "
            + "(the run says which).",
        )
    code = parse_exit_code(exit_code)
    if timed_out.strip() == "true":
        return "timed out", f"The check hit its timeout and was stopped (exit {TIMEOUT_EXIT})."
    if code is None:
        return "no exit code", "The run job reported no readable exit code."
    if code == 0:
        return "exit 0", "The check exited 0."
    return f"exit {code}", f"The check exited {code}."


@dataclass(frozen=True)
class PostInputs:
    """What the post job hands the renderer, every field as the job received it.

    ``sha``, ``command`` and ``refusal`` are the plan's outputs; the rest are
    the run job's, and the run job executed the check, so they are text the
    check could have shaped.
    """

    sha: str
    command: str
    refusal: str
    run_result: str
    exit_code: str
    timed_out: str
    summary_b64: str
    vintage_b64: str
    run_url: str


def render_comment(inputs: PostInputs) -> str:
    """The one result comment for the planned SHA, from values the post job does not trust.

    Every text is decoded defensively, stripped of control characters, has its
    mentions broken and is fenced; the summary is clamped first to
    :data:`SUMMARY_LIMIT_BYTES` and then until the whole body fits under
    :data:`COMMENT_LIMIT`.
    """
    sha = inputs.sha
    if not _SHA.fullmatch(sha):
        raise ValueError("the planned SHA is not a 40-hex commit id")
    status, explanation = outcome(
        refusal=inputs.refusal,
        run_result=inputs.run_result,
        exit_code=inputs.exit_code,
        timed_out=inputs.timed_out,
    )
    ran = not inputs.refusal and inputs.run_result == "success"
    vintage, vintage_note = decode_b64(inputs.vintage_b64, 2_000) if ran else ("", None)
    summary, summary_note = (
        decode_b64(inputs.summary_b64, SUMMARY_LIMIT_BYTES) if ran else ("", None)
    )
    summary = neutralize_mentions(summary)
    vintage = neutralize_mentions(vintage)
    # The run job clamps at the limit on a character boundary, so a summary
    # within a character's width of it was cut there.
    clamped = len(summary.encode("utf-8")) > SUMMARY_LIMIT_BYTES - 4

    def body(text: str, was_clamped: bool) -> str:
        parts = [
            result_marker(sha),
            f"### Corpus check: {status}",
            "",
            explanation,
            "",
            f"- commit: `{sha}`",
            f"- run: {_printable(inputs.run_url).strip()}",
            "",
            "**Command**",
            "",
            fence(neutralize_mentions(_printable(inputs.command) or "(none)")),
        ]
        if ran:
            parts += [
                "",
                "**Corpus** — production, read-only; the vintage `fedcourts corpus-info` "
                + "reported before the check ran:",
                "",
                fence(vintage_note or vintage.strip() or "(no vintage was reported)"),
                "",
                "**Summary** — what the check wrote to `CHECK_SUMMARY`"
                + (", clamped" if was_clamped else "")
                + ":",
                "",
                fence(summary_note or text or "(the check wrote no summary)"),
            ]
        return "\n".join(parts) + "\n"

    rendered = body(summary, clamped)
    budget = COMMENT_LIMIT - _COMMENT_MARGIN
    while len(rendered) > budget and summary:
        summary = summary[: max(0, len(summary) - (len(rendered) - budget) - 64)]
        rendered = body(summary, True)
    return rendered


@dataclass(frozen=True)
class CheckResult:
    """How the check ended: its exit code, whether the timeout ended it, its output size."""

    exit_code: int
    timed_out: bool
    output_bytes: int


def check_env(
    environ: Mapping[str, str],
    *,
    summary_path: Path,
    corpus_root: Path,
    drop_path_entries: Sequence[str] = (),
) -> dict[str, str]:
    """The check's environment: the job's, scrubbed, with the check's two paths set.

    ``CHECK_SUMMARY`` is the file the check reports through and
    ``FEDCOURTS_CORPUS_ROOT`` the pulled production corpus. ``drop_path_entries``
    removes the wrapper's own virtualenv from ``PATH``, so the check resolves
    its tools from its own checkout's environment.
    """
    env = {key: value for key, value in environ.items() if key not in _SCRUBBED_ENV}
    dropped = {str(Path(entry)) for entry in drop_path_entries}
    path = env.get("PATH")
    if path is not None:
        env["PATH"] = os.pathsep.join(
            entry for entry in path.split(os.pathsep) if entry and str(Path(entry)) not in dropped
        )
    env["CHECK_SUMMARY"] = str(summary_path)
    env["FEDCOURTS_CORPUS_ROOT"] = str(corpus_root)
    return env


def prepare_summary(cwd: Path) -> Path:
    """An empty summary file at the fixed name in ``cwd``, whatever the PR left there."""
    path = cwd / SUMMARY_FILENAME
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()
    path.write_bytes(b"")
    return path


def read_summary(path: Path, *, redact: Iterable[str] = ()) -> tuple[str, bool]:
    """The summary the check wrote, redacted and clamped; True when it was clamped.

    Reads a regular file only (a check that replaced it with anything else
    reports nothing), and at most a few times the limit.
    """
    if path.is_symlink() or not path.is_file():
        return "", False
    with path.open("rb") as handle:
        raw = handle.read(SUMMARY_LIMIT_BYTES * 4)
    text = redact_values(raw.decode("utf-8", errors="replace"), redact)
    return clamp_utf8(text, SUMMARY_LIMIT_BYTES)


def redact_values(text: str, values: Iterable[str]) -> str:
    """``text`` with every listed value of eight or more characters replaced."""
    for value in sorted({v for v in values if len(v) >= 8}, key=len, reverse=True):
        text = text.replace(value, _REDACTION)
    return text


def _kill_group(pgid: int) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pgid, signal.SIGKILL)


def run_check(
    argv: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
    timeout_seconds: float,
    output_path: Path,
) -> CheckResult:
    """Run ``argv`` with no shell, stdout and stderr to ``output_path``, under a timeout.

    The check runs in its own session, and the whole process group is killed
    once it ends or times out, so a background process it started does not
    outlive the step. A signal death reports ``128 + signal``; a program that
    could not be started reports :data:`NOT_FOUND_EXIT`.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timed_out = False
    with output_path.open("wb") as out:
        try:
            # An argv list and no shell: nothing in the command is interpreted.
            process = subprocess.Popen(
                list(argv),
                cwd=cwd,
                env=dict(env),
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except (FileNotFoundError, PermissionError) as exc:
            out.write(f"corpus-check: cannot start {argv[0]!r}: {exc}\n".encode())
            code = NOT_FOUND_EXIT
        else:
            try:
                code = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                _kill_group(process.pid)
                process.wait()
                code = TIMEOUT_EXIT
            finally:
                _kill_group(process.pid)
            if code < 0:
                code = 128 - code
    return CheckResult(exit_code=code, timed_out=timed_out, output_bytes=output_path.stat().st_size)


def run_outputs(result: CheckResult, summary: str) -> dict[str, str]:
    """The run job's outputs: single lines, the summary base64-encoded."""
    return {
        "exit_code": str(result.exit_code),
        "timed_out": "true" if result.timed_out else "false",
        "summary_b64": base64.b64encode(summary.encode("utf-8")).decode("ascii"),
    }


def write_outputs(path: Path, outputs: Mapping[str, str]) -> None:
    """Append ``key=value`` lines to a step's output file, refusing a multi-line value."""
    for key, value in outputs.items():
        if "\n" in value or "\r" in value or not re.fullmatch(r"[a-z_]+", key):
            raise ValueError(f"output {key!r} is not a single line")
    with path.open("a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            handle.write(f"{key}={value}\n")
