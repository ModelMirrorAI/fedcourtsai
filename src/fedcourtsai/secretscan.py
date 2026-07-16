"""Secret scan over a run's staged changes, before anything is published.

The collect job unions agent-written artifacts into a PR that merges without a
human once the required checks are green. Those artifacts carry free-text
surfaces (reasoning/evaluation markdown, flag messages), and the schema checks
deliberately validate shape, not content — so a prompt-injected agent that got
hold of any secret reachable from its cell could write it into free text and
have it published. This module is the third producer-side gate beside the path
jail and the schema check, and the only one that must act *before* the push:
a hit **withholds the branch entirely** — nothing is pushed and no PR opens,
because the push itself would be the exposure — and a redacted report rides to
the trigger issue while the flagged files stay reviewable in the run's cell
artifacts. It lives here as small pure functions the CLI wraps, so the
workflow YAML only plumbs files (the logic-in-tested-Python rule).

Detectors, strongest first:

- **Known-secret containment**: the literal value of each credential the
  pipeline actually holds (taken from the environment, never from arguments),
  searched raw and in the cheap encodings an exfiltrator might reach for
  (standard and URL-safe base64 — unpadded needles, so padded occurrences
  match too — hex in both cases, URL-escaped). Chunking, rot13, or
  interleaving are out of scope: this is a layer, not a guarantee; transforms
  long enough to look random fall to the entropy rule.
- **Structured patterns**: credential shapes with distinctive prefixes (AWS
  key ids and session tokens, PEM private-key headers, GitHub/Slack tokens,
  ``key=value`` assignments with a token-shaped value).
- **High entropy**: long random-looking runs, tuned so the ledger's normal
  content — citations, docket numbers, hex digests, run ids, URLs — passes
  clean. A raw opaque blob pasted into free text *does* flag, by design: the
  cost of a rare false positive is one human look at a withheld run.

A :class:`Finding` carries the file, rule, and line — never the matched text —
so the report itself cannot re-leak what it caught.
"""

from __future__ import annotations

import base64
import math
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from .collect import DATA_JAIL, PathChange

# Below this length a "secret" is too short to search for safely (the
# containment scan would light up on incidental substrings) — skip it loudly.
MIN_KNOWN_SECRET_LENGTH = 8

# Structured credential shapes. Each pattern anchors on a distinctive prefix
# or header, so ordinary legal text (citations, docket numbers, case slugs)
# cannot match. Order is the report order.
_STRUCTURED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-session-token", re.compile(r"\b(?:FwoG|IQoJ)[A-Za-z0-9+/=]{80,}")),
    ("pem-private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
)

# `key = value` / `key: value` where the key names a credential and the value
# is token-shaped. The value must carry a digit and must not look like an
# environment-variable *name* (all-caps identifiers are how the docs and
# prompts legitimately talk about credentials without holding one).
_KEYWORD_ASSIGNMENT = re.compile(
    r"""(?ix)
    \b (?: api[_-]?key | secret | password | passwd | token | credential ) \b
    ["'\s]* [:=] \s* ["']?
    (?P<value> [A-Za-z0-9+/_\-]{16,} )
    """,
)
_ENV_VAR_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

# Candidate runs for the entropy detector: long enough that citations, docket
# numbers, and prose fragments never qualify. `/` is included so a base64 blob
# is scanned as one run rather than fragments.
_ENTROPY_CANDIDATE = re.compile(r"[A-Za-z0-9+/=_\-]{40,}")
_ENTROPY_THRESHOLD_BITS = 4.5
# Benign high-length shapes the ledger commits routinely.
_HEX_RUN = re.compile(r"^[0-9a-f]+$")  # content digests (sha256 etc.)
_RUN_ID_SHAPE = re.compile(r"(?i)^(?:run[_-]?)?20\d{6}t\d{6}z$")


@dataclass(frozen=True)
class Finding:
    """One detector hit: the file, the rule that fired, and the line.

    Deliberately does **not** carry the matched text — the scan report rides
    into workflow logs, PR comments, and issue comments, and a report that
    quoted its match would re-leak the very thing it caught.
    """

    path: str
    rule: str
    line: int


def _shannon_entropy(text: str) -> float:
    counts: dict[str, int] = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    total = len(text)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def _char_classes(text: str) -> int:
    classes = 0
    for predicate in (str.isupper, str.islower, str.isdigit):
        classes += any(predicate(c) for c in text)
    classes += any(not c.isalnum() for c in text)
    return classes


def _is_benign_run(run: str) -> bool:
    if _HEX_RUN.match(run) and len(run) <= 128:
        return True  # a content digest, not a credential shape
    return bool(_RUN_ID_SHAPE.match(run))


def _entropy_hits(line: str) -> bool:
    for match in _ENTROPY_CANDIDATE.finditer(line):
        run = match.group()
        if _is_benign_run(run):
            continue
        # Random credential material mixes cases and digits; slugs, URLs, and
        # identifiers rarely reach three classes *and* this entropy together.
        if _char_classes(run) >= 3 and _shannon_entropy(run) >= _ENTROPY_THRESHOLD_BITS:
            return True
    return False


def _keyword_assignment_hits(line: str) -> bool:
    for match in _KEYWORD_ASSIGNMENT.finditer(line):
        value = match.group("value")
        if _ENV_VAR_NAME.match(value) or _RUN_ID_SHAPE.match(value):
            continue  # naming a credential (or a run id), not holding one
        if any(c.isdigit() for c in value):
            return True
    return False


def secret_variants(secret: str) -> tuple[str, ...]:
    """The literal forms the containment detector searches for one secret.

    Raw, plus the cheap encodings an exfiltrating agent might reach for:
    standard and URL-safe base64 (unpadded needles — a substring match also
    catches the padded forms), hex in both cases, and URL-escaping (only when
    escaping changes the value). Deduplicated, order-preserving.
    """
    encoded = secret.encode()
    variants = [
        secret,
        base64.b64encode(encoded).decode().rstrip("="),
        base64.urlsafe_b64encode(encoded).decode().rstrip("="),
        encoded.hex(),
        encoded.hex().upper(),
    ]
    escaped = quote(secret, safe="")
    if escaped != secret:
        variants.append(escaped)
    return tuple(dict.fromkeys(variants))


def scan_lines(rel: str, lines: Iterable[str], known_secrets: Sequence[str]) -> list[Finding]:
    """Run every detector over one file's lines; findings carry ``rel`` as the path."""
    variant_sets = [secret_variants(secret) for secret in known_secrets]
    findings: list[Finding] = []
    for lineno, line in enumerate(lines, start=1):
        for variants in variant_sets:
            if any(variant in line for variant in variants):
                findings.append(Finding(path=rel, rule="known-token", line=lineno))
                break
        for rule, pattern in _STRUCTURED_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path=rel, rule=rule, line=lineno))
        if _keyword_assignment_hits(line):
            findings.append(Finding(path=rel, rule="keyword-assignment", line=lineno))
        if _entropy_hits(line):
            findings.append(Finding(path=rel, rule="high-entropy", line=lineno))
    return findings


def scan_file(path: Path, rel: str, known_secrets: Sequence[str]) -> list[Finding]:
    """Scan one file on disk; unreadable bytes are replaced, never fatal.

    Split on ``\\n`` only (not :meth:`str.splitlines`), so reported line
    numbers match what a reviewer sees on GitHub even for files carrying
    exotic unicode line separators.
    """
    text = path.read_bytes().decode("utf-8", errors="replace")
    return scan_lines(rel, text.split("\n"), known_secrets)


def scan_changes(
    changes: Iterable[PathChange], root: Path, known_secrets: Sequence[str]
) -> list[Finding]:
    """Scan every changed ``data/`` file under ``root`` (deletes have no blob).

    A non-addition is already a jail violation — but the jail only downgrades
    the PR to a draft, and a draft is still a *push*: a secret written into a
    modified tracked file would publish anyway. So content is scanned for
    every status that leaves bytes on disk, not just the adds the jail
    permits. Paths outside ``data/`` are left to the jail (they are never
    agent output). A listed file missing from disk is skipped (the jail
    check, not this one, owns change-list integrity).
    """
    findings: list[Finding] = []
    for change in changes:
        if change.status == "D" or not change.path.startswith(DATA_JAIL):
            continue
        target = root / change.path
        if not target.is_file():
            continue
        findings.extend(scan_file(target, change.path, known_secrets))
    return findings


def render_warnings(findings: Sequence[Finding]) -> list[str]:
    """One ``::warning::`` workflow-command line per finding."""
    return [
        f"::warning::secret-scan: {finding.rule} in {finding.path} (line {finding.line})"
        for finding in findings
    ]


# Cell agents choose their filenames, so the path column is the one
# attacker-influenced value in a rendered report: display it through a strict
# charset (anything else becomes ``?``) so a crafted name cannot smuggle
# markdown into the trusted-looking bot comment. Cap the table so a file
# engineered to hit thousands of times cannot push the comment past GitHub's
# body limit.
_SAFE_PATH_CHARS = re.compile(r"[^A-Za-z0-9._/-]")
_MAX_TABLE_ROWS = 20


def _findings_table(findings: Sequence[Finding]) -> str:
    rows = [
        f"| `{_SAFE_PATH_CHARS.sub('?', f.path)}` | {f.rule} | {f.line} |"
        for f in findings[:_MAX_TABLE_ROWS]
    ]
    if len(findings) > _MAX_TABLE_ROWS:
        rows.append(f"| … | {len(findings) - _MAX_TABLE_ROWS} more finding(s) | |")
    return "| file | rule | line |\n| --- | --- | --- |\n" + "\n".join(rows)


def render_misconfigured_comment(run_url: str) -> str:
    """The trigger-issue comment when the scan itself could not run.

    A misconfigured gate (a missing token env, a missing rendered file) fails
    closed — the run's output is withheld — and that must be as loud on the
    issue as a real hit would be, or a broken gate silently swallows runs.
    """
    return (
        "🔒 The **secret scan could not run** for a run on this issue (a "
        "misconfigured gate, not a finding), so its output was withheld — "
        "nothing was pushed and no PR opened. The cells' artifacts remain on "
        f"the run for review.\n\nRun log: {run_url}"
    )


def render_issue_comment(findings: Sequence[Finding], run_url: str) -> str:
    """The trigger-issue comment for a run whose output the scan withheld."""
    if not findings:
        return ""
    return (
        "🔒 A run for this issue tripped the **secret scan**: the flagged "
        "output was **withheld** — nothing was pushed and no PR opened for "
        "it. The files remain in the run's cell artifacts for maintainer "
        "review.\n\n"
        f"{_findings_table(findings)}\n\n"
        f"Run log: {run_url}\n\n"
        "The matched text is not quoted anywhere; the flagged files identify "
        "the lines to review. If a live credential really is present in the "
        "artifacts, rotate it."
    )
