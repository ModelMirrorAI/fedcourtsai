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

The same credential-shape knowledge serves a second consumer, one layer
earlier: :func:`redact_credentials` rewrites rather than reports, and the
harness applies it to every string it harvests from an engine transcript into
``retrieval_log.json`` (:mod:`fedcourtsai.retrieval`). Capture-time redaction
and the scan are complements, not duplicates — a credential the agent never
chose to write, pulled in verbatim because it happened to sit in a tool-call
payload, should not reach the staged tree at all, and a withheld run costs a
whole fan-out's model spend. The two are tuned differently on purpose: a scan
false positive costs one human look at a withheld run, while a redaction false
positive silently eats audit content the evaluators' leakage grading reads, so
redaction leans harder on prefix-anchored shapes and holds its last-resort
entropy rule to a stricter length floor.
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

# Keys that name a credential, shared by the scan's assignment detector and
# capture-time redaction below so the two cannot drift apart on what counts as
# one. The HTTP header names are here because a pasted request header is the
# realistic way a short key — one below the entropy detector's 40-char floor —
# reaches either surface.
_CREDENTIAL_KEYWORDS = r"""
    authorization | proxy-authorization | x-api-key | api[_-]?key
    | secret | password | passwd | token | credential
"""

# `key = value` / `key: value` where the key names a credential and the value
# is token-shaped. The value must carry a digit and must not look like an
# environment-variable *name* (all-caps identifiers are how the docs and
# prompts legitimately talk about credentials without holding one).
_KEYWORD_ASSIGNMENT = re.compile(
    rf"""(?ix)
    \b (?: {_CREDENTIAL_KEYWORDS} ) \b
    ["'\s]* [:=] \s* ["']?
    (?P<value> [A-Za-z0-9+/_\-]{{16,}} )
    """,
)
_ENV_VAR_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

# Candidate runs for the entropy detector: long enough that citations, docket
# numbers, and prose fragments never qualify. `/` is included so a base64 blob
# is scanned as one run rather than fragments.
_MIN_ENTROPY_RUN = 40
_ENTROPY_CANDIDATE = re.compile(rf"[A-Za-z0-9+/=_\-]{{{_MIN_ENTROPY_RUN},}}")

# The discriminator is *normalized* Shannon entropy — bits/char over the most
# a run of this length could carry (`log2(min(len, base64_alphabet))`) — not
# raw bits/char, because a fixed bits/char bar cannot separate the two
# classes: entropy is length-capped, so a long *readable* string and a short
# *random* one land at the same raw value, and any bar tuned to clear the
# former misses a third to a half of 40-43 char random blobs. Normalized, the
# classes separate length-robustly. Calibrated over 10k+ random samples per
# length plus the real strings this ledger carries:
#
# - readable shapes (document-URL filename segments, camelCase caption slugs)
#   top out at **0.802** — measured over a real predict run's files;
# - random base64 / url-safe secrets sit at or above **0.820** at the 1st
#   percentile for every length from 40 to 86 chars.
#
# 0.82 sits in that gap. The tails do touch (a rare random run scores as low
# as 0.78), so the bar accepts a sub-1% miss (peak 0.85% at len 64, the knee
# where the ceiling switches from log2(len) to log2(64)) rather than risk
# withholding a whole clean run — 12 predictions of real model spend — over a
# filename. Do NOT read the →1.0 limit of normalized entropy as headroom to
# raise this: at these operating lengths random runs sit at ~0.86-0.90
# (medians), not near 1.0, so the miss rate climbs steeply — 0.83 misses 3.2%,
# 0.85 misses 21.5%. This is the last-resort net for opaque blobs; containment
# carries known secrets and the structured patterns carry distinctive shapes.
# Hex and other low-alphabet secrets fall below any workable floor and are
# covered there.
_BASE64_ALPHABET_SIZE = 64
_NORM_ENTROPY_THRESHOLD = 0.82

# At three or more slashes a run reads as a filesystem/URL path, not one
# opaque token: paths concatenate many short wordy segments whose *aggregate*
# entropy can cross the bar — a cell's own workspace output path (slashes,
# dashes, digits, a run id's T/Z) once withheld a whole clean run.
#
# The sizeable gap this leaves, stated plainly because it is this layer's
# *dominant* miss — an order of magnitude larger than the threshold's: a
# standard-base64 secret carrying 3+ incidental `/`s (~1 in 64 per char) is
# scored per segment, and segments below the 40-char floor are never scored at
# all. End-to-end that misses ~2.8% of 32-byte and ~7.3% of 64-byte pasted
# std-base64 secrets (url-safe, which has no `/`, is ≤0.9%). Tune this knob,
# not the threshold, if the layer ever needs to catch more. Scoring path-like
# runs with the slashes stripped was measured and rejected: it collapses the
# separation to zero (the real supremecourt URL scores 0.819 stripped, against
# a random-blob 1st percentile of 0.819).
_PATHLIKE_SLASHES = 3
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


def _normalized_entropy(run: str) -> float:
    """Shannon entropy as a fraction of the maximum a run this length can carry.

    Length-robust where a raw bits/char score is not: a random run scores near
    its ceiling while a readable string plateaus below it, at any length. The
    ceiling is only *approached* asymptotically, though — at the lengths this
    scans (40-86 chars) random runs land around 0.86-0.90, not near 1.0. See
    the threshold comment for the measured separation and its calibration.
    """
    ceiling = math.log2(min(len(run), _BASE64_ALPHABET_SIZE))
    if ceiling == 0:  # unreachable via the callers' >= 40-char floor
        return 0.0
    return _shannon_entropy(run) / ceiling


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


def _entropy_candidate_hits(run: str) -> bool:
    if _is_benign_run(run):
        return False
    # Random credential material mixes cases and digits *and* fills its length
    # with near-random symbols; readable slugs/URLs/identifiers may reach three
    # classes but never the normalized-entropy bar.
    return _char_classes(run) >= 3 and _normalized_entropy(run) >= _NORM_ENTROPY_THRESHOLD


def _entropy_hits(line: str) -> bool:
    for match in _ENTROPY_CANDIDATE.finditer(line):
        run = match.group()
        if run.count("/") >= _PATHLIKE_SLASHES:
            # Path-like: evaluate per segment, so a path is judged by its
            # pieces (all short and wordy) while a credential-length blob
            # *inside* a path still flags on its own segment. The accepted
            # miss — a secret pre-split into short path segments — is the
            # layered-detector trade: containment carries the real load.
            if any(
                len(segment) >= _MIN_ENTROPY_RUN and _entropy_candidate_hits(segment)
                for segment in run.split("/")
            ):
                return True
        elif _entropy_candidate_hits(run):
            return True
    return False


def _holds_credential(value: str) -> bool:
    """Whether an assignment's right-hand side *holds* a credential.

    An all-caps identifier is how the docs, prompts, and configs legitimately
    name one without carrying it, and a run id is token-shaped by coincidence;
    everything else must carry a digit to count.

    Shared by the reporting gate and capture-time redaction, whose tuning
    pressures point opposite ways: loosening this to make redaction eat less
    also weakens the pre-push scan.
    """
    if _ENV_VAR_NAME.match(value) or _RUN_ID_SHAPE.match(value):
        return False
    return any(c.isdigit() for c in value)


def _keyword_assignment_hits(line: str) -> bool:
    return any(_holds_credential(m.group("value")) for m in _KEYWORD_ASSIGNMENT.finditer(line))


# --- Capture-time redaction -------------------------------------------------

# What replaces a redacted run. Square brackets and `:` sit outside every
# credential alphabet below, so a marker can never be re-matched as one on a
# later pass (redaction is idempotent), and it reads unmistakably as machine
# insertion to anyone reviewing a query slice. The rule name says which shape
# fired and nothing about the match. A marker is not proof of harness
# provenance — nothing stops an agent writing the literal string into a tool
# call — so it is a reading aid, not evidence.
REDACTION_MARKER_PREFIX = "[redacted:"
_REDACTION_MARKER = REDACTION_MARKER_PREFIX + "{rule}]"

# Repeat ceilings on the multi-part patterns. Redaction runs over engine
# transcript text, which an agent influences and which arrives uncapped, so an
# unbounded `{n,}` either side of a required literal is a quadratic-backtracking
# hang, not just a slow match. 4096 is far past any real token segment.
_MAX_SEGMENT = 4096

# Shapes redaction removes on sight, over and above the ones the scan reports.
# Each is prefix-anchored on a token format's own header, so ordinary case
# prose, citations, and identifiers cannot match.
_REDACTION_ONLY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # Fernet v1: `gAAAAA` is the base64url rendering of the version byte and
    # the leading zero bytes of the 64-bit timestamp. Unanchored on the left —
    # the prefix is distinctive enough that a mid-run occurrence is a token,
    # not a coincidence.
    ("fernet-token", re.compile(r"gAAAAA[A-Za-z0-9_-]{20,}={0,2}")),
    # A JWT's three base64url segments. The signature may be empty (`alg=none`).
    (
        "jwt",
        re.compile(
            rf"\beyJ[A-Za-z0-9_-]{{8,{_MAX_SEGMENT}}}"
            rf"\.[A-Za-z0-9_-]{{8,{_MAX_SEGMENT}}}"
            rf"\.[A-Za-z0-9_-]{{0,{_MAX_SEGMENT}}}"
        ),
    ),
    # Model-provider keys: the `sk-proj-` / `sk-ant-` variants continue in the
    # same alphabet, so one pattern covers them. No English word starts `sk-`.
    ("model-provider-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    # Google API keys and OAuth access tokens.
    ("google-key", re.compile(r"\b(?:AIza|ya29\.)[A-Za-z0-9_-]{20,}")),
)

# The scan's report rules plus redaction's own: redaction is a superset of the
# shapes, because it has no cost beyond the run it rewrites.
_REDACTION_PATTERNS = _STRUCTURED_PATTERNS + _REDACTION_ONLY_PATTERNS

# How a captured HTTP header or client config carries a credential that has no
# recognizable prefix. Same keys the scan's assignment detector uses; the auth
# scheme is part of the *prefix* group, so `Authorization: Bearer <token>`
# keeps the scheme and loses only the token. The value class is wider than the
# scan's — `.`, `=` and `~` included — because a rule that redacted only the
# first half of a dotted `<public-id>.<secret>` credential would leave the
# usable half behind *and* rewrite the line past what the scan would have
# flagged: a partial redaction is worse than none.
# Anchored on the keyword rather than on the scheme alone: bare `bearer`/
# `basic` are ordinary English beside a 16-char run ("basic
# responsibilities1"), and eating docket text costs the leakage grading its
# evidence.
_CREDENTIAL_ASSIGNMENT = re.compile(
    rf"""(?ix)
    (?P<prefix>
        \b (?: {_CREDENTIAL_KEYWORDS} ) \b
        ["'\s]* [:=] \s* ["']?
        (?: (?: bearer | basic ) \s+ )?
    )
    (?P<value> [A-Za-z0-9+/_.=~\-]{{16,}} )
    """,
)

# The last-resort net, for an opaque token whose format this does not know.
# 64 chars, against the scan's 40: the shapes above carry every credential
# format the pipeline can plausibly meet, so the generic rule exists for the
# unknown one, and a rule that silently eats a long docket slug or caption
# would cost the leakage grading its evidence. Judged by the scan's calibrated
# discriminator (>= 3 character classes and normalized entropy over the bar),
# with the same per-segment treatment of path-like runs.
#
# The deliberate consequence: an unrecognized opaque run of 40-63 chars — a
# base64url-encoded 32-byte token is 43 — is left alone here and still
# withholds the run at the collect scan. Redaction spares the runs it can name;
# it does not replace the gate.
_OPAQUE_MIN_RUN = 64
_OPAQUE_CANDIDATE = re.compile(rf"[A-Za-z0-9+/=_\-]{{{_OPAQUE_MIN_RUN},}}")


def _redact_assignment(match: re.Match[str]) -> str:
    value = match.group("value")
    if not _holds_credential(value):
        return match.group()  # naming a credential, not holding one
    return match.group("prefix") + _REDACTION_MARKER.format(rule="credential")


def _redact_opaque(match: re.Match[str]) -> str:
    run = match.group()
    marker = _REDACTION_MARKER.format(rule="opaque")
    if run.count("/") >= _PATHLIKE_SLASHES:
        # Path-like: rewrite per segment, so a workspace path or a document URL
        # survives intact while a blob sitting inside one still goes.
        return "/".join(
            marker
            if len(segment) >= _OPAQUE_MIN_RUN and _entropy_candidate_hits(segment)
            else segment
            for segment in run.split("/")
        )
    return marker if _entropy_candidate_hits(run) else run


def redact_credentials(text: str) -> str:
    """Replace credential-shaped runs in captured text with ``[redacted:rule]``.

    Pure and deterministic: the same input always yields the same output, and
    the marker names the shape that fired, never the matched text. Applied by
    the harness to everything it harvests from an engine transcript, *before*
    any truncation, so a credential cannot survive by sitting past a cut.

    Nothing here is a parser: the goal is that a token pulled into a logged
    tool-call payload leaves the harness unusable, not that the surrounding
    text stays perfectly legible. Nor is it a gate — what it cannot name it
    leaves for the scan to withhold the run over.
    """
    for rule, pattern in _REDACTION_PATTERNS:
        text = pattern.sub(_REDACTION_MARKER.format(rule=rule), text)
    text = _CREDENTIAL_ASSIGNMENT.sub(_redact_assignment, text)
    return _OPAQUE_CANDIDATE.sub(_redact_opaque, text)


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
