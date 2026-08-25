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
  JWTs, model-provider ``sk-`` keys, Google keys, ``key=value`` assignments
  with a token-shaped value).
- **High entropy**: long random-looking runs, tuned so the ledger's normal
  content — citations, docket numbers, hex digests, run ids, URLs — passes
  clean. A raw opaque blob pasted into free text *does* flag, by design: the
  cost of a rare false positive is one human look at a withheld run. One
  further family is exempt, and only when the caller names the run being
  collected (``scan-diff-for-secrets --run-id``): that run's own ledger
  paths — the ``predictions/`` / ``evaluations/`` layouts and the
  cell-relative forms (``<actor>/<run id>[/<file stem>]``,
  ``<evaluator>/<predictor>/<run id>``) — which a cell's
  logged shell commands name routinely. It cannot mask a credential: the run
  id segment is compared for *equality* with the run id the collect job is
  scanning, and every free segment is pinned to lowercase and capped far
  below the floor at which this detector judges a run at all.

One surface opts out of the entropy rule alone: an engine transcript
(``scan-diff-for-secrets --transcript-file``) carries server-generated tool
and request ids that are high-entropy by format, so the generic rule convicts
every real file and the artifact it gates could only ever publish empty.
There the load is carried by containment plus the structured shapes — which
is why every prefix-anchored credential format the pipeline could plausibly
touch belongs in the structured set, not only in redaction.

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
redaction leans harder on prefix-anchored shapes, holds its last-resort
entropy rule to a stricter length floor, and where a prefix is short enough to
turn up inside agent-authored text, confirms it against the same entropy
discriminator before rewriting.
"""

from __future__ import annotations

import base64
import math
import re
import string
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from .collect import DATA_JAIL, PathChange

# Below this length a "secret" is too short to search for safely (the
# containment scan would light up on incidental substrings) — skip it loudly.
MIN_KNOWN_SECRET_LENGTH = 8

# Repeat ceiling on every variable run in the patterns below. Redaction reads
# engine transcript text, which an agent influences and which arrives uncapped:
# an unbounded `{n,}` either side of a required literal is a
# quadratic-backtracking hang rather than a slow match. 4096 is far past any
# real token — a Fernet token carrying a kilobyte of plaintext is under 1500
# characters.
#
# The ceiling bounds *matching* only. It deliberately does not bound what the
# fernet rule reads to make its decision, because a ceiling that truncated the
# evidence as well as the match would hide a token straddling it; see the
# confirmation's own note below.
_MAX_SEGMENT = 4096

# Structured credential shapes. Each pattern anchors on a distinctive prefix
# or header, so ordinary legal text (citations, docket numbers, case slugs)
# cannot match. Order is the report order.
_STRUCTURED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-session-token", re.compile(r"\b(?:FwoG|IQoJ)[A-Za-z0-9+/=]{80,}")),
    ("pem-private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
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

# The shapes the path-like rule above does not cover: a cell's *relative*
# references to its own ledger directories, which carry at most two slashes —
# one short of `_PATHLIKE_SLASHES` — so they are judged whole. Whole, they
# clear the bar for many actor/run-id pairs: nothing about them is random —
# lowercase slugs, separators, and a run id whose digits and `T`/`Z` spread
# the character distribution flat enough to read as mixed alphabet — but the
# aggregate crosses anyway. Measured against the 0.82 threshold (the first
# bullet against the test suite's `20260816T173750Z`, the rest against the
# incident run id `20260824T231401Z`):
#
# - `predictions/<actor>/<run id>`, the predict cell's own directory: 0.829
#   for `gemini-baseline`, 0.836 for `claude-baseline`, 0.839 for
#   `codex-baseline`;
# - `evaluations/<evaluator>/<run id>`, the evaluate cell's own run
#   directory: 0.832-0.852 for every judge in the registry;
# - `<actor>/<run id>/<output file stem>`, the form a cell writes once it has
#   changed into its ledger parent — `codex-baseline/<run id>/evaluation`
#   scores 0.826, `claude-judge/<run id>/retrieval_log` 0.822;
# - `<evaluator>/<predictor>/<run id>`, the per-predictor output directory
#   written from inside `evaluations/` — `codex-judge/gemini-baseline/<run
#   id>` scores 0.821.
#
# The absolute forms of the same paths escape because their leading
# directories push them over the slash count; the relative forms are what a
# cell logs once it has changed into the event directory, so without this
# exemption a whole clean fan-out is withheld over a directory the collect
# job itself provisioned.
#
# So the exemption is keyed on the run actually being collected, never on the
# shape alone. Three properties carry the security argument, and each is worth
# stating because a reviewer must be able to check them by reading the pattern:
#
# 1. **The run id is compared for equality, not matched by shape.** The run
#    id segment (last, or second-to-last before a file stem) is the literal
#    run id the collect job passed in, escaped
#    into the pattern. `_RUN_ID_SHAPE` is deliberately *not* reused here: a
#    shape match would exempt this directory layout under any plausible
#    timestamp, including one an agent invented, whereas equality binds the
#    exemption to the single run whose own output is being scanned.
# 2. **Every free segment is capped at 24 characters.** The ledger's real
#    segments top out at 19 (`predicted_reasoning`), so 24 keeps every real
#    path exempt while holding each free segment far below the 40-char floor
#    at which this detector is willing to judge a run as credential material
#    at all. So an exempted candidate can hold no run of secret material that
#    the scan would have convicted had it stood alone — the exemption's
#    channel sits inside the short-segment gap `_PATHLIKE_SLASHES` already
#    documents, and opens no new class of miss. In any candidate the
#    whole-run branch can actually see (two slashes or fewer), its total
#    free-lowercase capacity is two segments — 48 chars around an
#    equality-pinned run id —
#    and all-lowercase material is invisible to this detector standalone at
#    *any* length (two character classes, below the three the rule demands).
#    What the exemption forgoes is the incidental *aggregate* hit, where the
#    whole path crossed the bar only because random sub-cap segments were
#    spliced into it — material the rule cannot see standalone.
# 3. **The free segments are lowercase-only.** Both base64 alphabets are
#    mixed-case, so a pasted blob cannot occupy an actor position; re-encoding
#    one into `[a-z0-9-]` would first have to survive the length cap above.
#    The trailing output-file position additionally admits `_` (the ledger's
#    file stems: `retrieval_log`), which changes nothing about the mixed-case
#    pin — neither base64 alphabet is lowercase.
#
# `fullmatch` plus the segment charset is the anchor. Extending a candidate
# with lowercase material inside the cap is absorbed as a free segment — the
# same accepted residual property 2 prices — while anything mixed-case,
# over-cap, or outside the charset fails the fullmatch and is scored as any
# other run; extending it with another path component adds a slash, toward
# the per-segment branch, where this predicate is not what saves it.
#
# The pattern itself is one generalized form — one to three free segments,
# the run id, an optional file stem — because the ledger literals
# (`predictions`, `evaluations`) are themselves lowercase segment-shaped, so
# a single form covers the anchored layouts (`predictions/<actor>/<run id>`,
# `evaluations/<evaluator>/<run id>`), the cell-relative forms written from
# inside a ledger parent (`<actor>/<run id>/<file>`,
# `<evaluator>/<predictor>/<run id>`), and — at three leading segments —
# `evaluations/<evaluator>/<predictor>/<run id>`, which carries three
# slashes and never reaches the whole-run branch at the current
# `_PATHLIKE_SLASHES`; it is covered anyway so the exemption does not
# silently depend on that knob keeping its exact value.
# Free-segment cap: the ledger's real segments top out well under this
# (actor ids at 15, file stems at 19, the layout literals at 11), and every
# character of headroom is exemptable lowercase capacity, so the cap hugs
# the ledger's shapes rather than the detector's 40-char floor.
_OWN_RUN_SEGMENT_CAP = 24
_OWN_RUN_SEGMENT = rf"[a-z0-9-]{{1,{_OWN_RUN_SEGMENT_CAP}}}"
# The output-file stem position: the ledger's committed filenames are
# lowercase with `_` as the only extra separator, and the candidate charset
# excludes `.`, so a logged `evaluation.json` reaches here as `evaluation`.
_OWN_RUN_FILE_SEGMENT = rf"[a-z0-9_-]{{1,{_OWN_RUN_SEGMENT_CAP}}}"


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


# The bare form the fan-outs mint (UTC `%Y%m%dT%H%M%SZ`), case-sensitive and
# unprefixed — stricter than `_RUN_ID_SHAPE`, because this validates the one
# caller-supplied value that defines the own-run exemption's shape.
_BARE_RUN_ID = re.compile(r"^20\d{6}T\d{6}Z$")


def is_run_id_shaped(value: str) -> bool:
    """Whether ``value`` is a bare fan-out run id, fit to key the exemption."""
    return _BARE_RUN_ID.match(value) is not None


@lru_cache(maxsize=4)
def _own_run_path_pattern(run_id: str) -> re.Pattern[str]:
    """The ledger directory layouts, pinned to one run id. See the note above.

    Cached because the scan asks per candidate per line and the run id is
    fixed for a whole scan; the cache is keyed on that id, so a different run
    can never read another's pattern.
    """
    return re.compile(
        rf"(?:{_OWN_RUN_SEGMENT}/){{1,3}}"
        rf"{re.escape(run_id)}"
        rf"(?:/{_OWN_RUN_FILE_SEGMENT})?"
    )


def _is_own_run_path(run: str, run_id: str) -> bool:
    """Whether ``run`` is exactly the ledger directory of the run being collected."""
    return _own_run_path_pattern(run_id).fullmatch(run) is not None


def _entropy_candidate_hits(run: str, *, run_id: str | None = None) -> bool:
    if _is_benign_run(run):
        return False
    # Truthiness, not a None test: an empty run id must never degenerate the
    # pattern to `predictions/<seg>/` and exempt a candidate ending in a slash.
    if run_id and _is_own_run_path(run, run_id):
        return False
    # Random credential material mixes cases and digits *and* fills its length
    # with near-random symbols; readable slugs/URLs/identifiers may reach three
    # classes but never the normalized-entropy bar.
    return _char_classes(run) >= 3 and _normalized_entropy(run) >= _NORM_ENTROPY_THRESHOLD


def _entropy_hits(line: str, *, run_id: str | None = None) -> bool:
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
        elif _entropy_candidate_hits(run, run_id=run_id):
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

# Shapes redaction removes over and above the ones the scan reports. Each is
# prefix-anchored on a token format's own header, so ordinary case prose,
# citations, and identifiers cannot match; where a header is short enough to
# turn up inside long agent-authored runs, an entropy confirmation decides.
_REDACTION_ONLY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # Fernet v1: `gAAAAA` is the base64url rendering of the version byte and
    # the leading zero bytes of the 64-bit timestamp. Unanchored on the left,
    # so a token pasted mid-run is still caught; the three pieces then divide
    # the work — the prefix fixes where a match starts, the repeat ceiling
    # bounds how far it runs, and `_fernet_substituter`'s confirmation decides
    # whether the run carries credential material. The confirmation is what the
    # other prefixes do not need: six characters of base64url header are short
    # enough to turn up inside a long agent-authored run in the same alphabet —
    # an id-dense listing, a slug chain — and there the prefix alone would
    # convict text that is not a token, costing the leakage grading a payload
    # it needs whole.
    (
        "fernet-token",
        re.compile(rf"gAAAAA[A-Za-z0-9_-]{{20,{_MAX_SEGMENT}}}={{0,2}}"),
    ),
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

# The fernet confirmation scores windows, and scores them over the *maximal*
# alphabet run its match sits in rather than over the match itself. Two
# separate reasons, and both are needed:
#
# Windows, because the alphabet has no separator and the match is greedy, so
# one span can hold a token beside arbitrary agent-chosen filler; averaged
# whole, the token vanishes under the bar, and the scan — which scores the same
# maximal run on the same threshold — would not catch what redaction let
# through. A window asks the question that survives padding: does *any* part of
# this look like credential material. 64 sits inside the threshold's calibrated
# band and below the 100-character floor of a real Fernet token (version byte,
# timestamp, IV, one cipher block, 32-byte HMAC), so a token always contains a
# whole window, and the quarter-window stride guarantees one lands well inside
# it wherever the token sits — at minimum token length a coarser stride can
# leave a single marginal window carrying the whole decision.
#
# The maximal run, because `_MAX_SEGMENT` truncates the match but not the text:
# a token whose own header falls in the last window-width of a ceiling-bounded
# match would be consumed with that match and never offered to the rule again,
# `re.sub` having resumed past its header. Scoring the run the match sits in
# asks about all the material actually adjacent, so a token straddling the
# ceiling is seen. The ceiling stays on the pattern, where it does its real job
# of bounding backtracking.
_FERNET_WINDOW = 64
_FERNET_STRIDE = 16
_FERNET_RUN_CHARS = frozenset(string.ascii_letters + string.digits + "_-")


def _redact_assignment(match: re.Match[str]) -> str:
    value = match.group("value")
    if not _holds_credential(value):
        return match.group()  # naming a credential, not holding one
    return match.group("prefix") + _REDACTION_MARKER.format(rule="credential")


def _carries_credential_material(run: str) -> bool:
    """Whether ``run``, whole or in any window of it, scores as credential material.

    Windowed as well as whole because the alphabet has no separator: a run can
    hold a token beside filler on either side of it, and the run's average is a
    knob the writer of the text controls. A window is not.

    Both scores are taken, not just the windowed one, because they miss in
    opposite directions. Windows are what survive dilution; the whole run is
    the steadier reading of a *short* token, where 64 characters is a large
    enough fraction of the whole that sampling variance starts to matter. Each
    can only add a redaction, so taking both is the conservative combination —
    and patterned or readable text clears neither bar.
    """
    if _entropy_candidate_hits(run):
        return True
    return any(
        _entropy_candidate_hits(run[start : start + _FERNET_WINDOW])
        for start in range(0, len(run) - _FERNET_WINDOW + 1, _FERNET_STRIDE)
    )


def _alphabet_run_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    """Widen ``[start, end)`` to the maximal surrounding fernet-alphabet run."""
    while start > 0 and text[start - 1] in _FERNET_RUN_CHARS:
        start -= 1
    while end < len(text) and text[end] in _FERNET_RUN_CHARS:
        end += 1
    return start, end


def _fernet_substituter() -> Callable[[re.Match[str]], str]:
    """Build the fernet replacement, memoized across one pass over one text.

    Rewrites a fernet-shaped match only where the alphabet run it sits in
    carries credential material, judged by the same discriminator as the opaque
    rule — so a header landing inside patterned or readable base64url text does
    not cost the leakage grading a whole payload. The confirmation is this
    rule's alone: every other prefix here is long or distinctive enough to
    convict by itself, and this one is six characters.

    A confirmed match is replaced entire, filler included; over-redacting text
    that shares a run with a token is the cheap error. Declining is
    all-or-nothing: the match comes back exactly as it arrived, so the collect
    scan reads what it would have read had redaction never run and no finding
    is silenced. That is the honest claim, and deliberately *not* that the scan
    backstops this rule — a diluted run is precisely what the scan's own
    entropy detector also misses, which is why the confirmation is windowed and
    run-scoped rather than a single average over the match.

    What remains is the entropy discriminator's own reach, shared with the
    opaque rule and the scan: a credential that looks random in no 64-character
    window of its run is not recognized here. Containment is the layer that
    does not care — it catches any credential the pipeline itself holds,
    whatever its entropy.

    Every match inside a given alphabet run gets the same verdict, so the run's
    bounds and its score are computed once and reused while the matches keep
    landing inside them. ``re.sub`` walks left to right over non-overlapping
    matches, so a single remembered run is enough — which is what keeps a
    run-scoped confirmation linear in the length of the text rather than
    quadratic in the number of headers an agent can write into one run.
    """
    marker = _REDACTION_MARKER.format(rule="fernet-token")
    remembered: tuple[int, int] | None = None
    verdict = False

    def substitute(match: re.Match[str]) -> str:
        nonlocal remembered, verdict
        if remembered is None or not remembered[0] <= match.start() < remembered[1]:
            remembered = _alphabet_run_bounds(match.string, match.start(), match.end())
            verdict = _carries_credential_material(match.string[remembered[0] : remembered[1]])
        return marker if verdict else match.group()

    return substitute


# Rules whose replacement is built per pass rather than being a literal marker,
# keyed by rule name so the substitution loop stays one walk over the pattern
# table. A key that stops matching its rule — a rename above without one here —
# drops the confirmation back to unconditional redaction, which is the strict
# behavior: the coupling is loose, but it fails in the safe direction.
_CONFIRMED_SUBSTITUTIONS: dict[str, Callable[[], Callable[[re.Match[str]], str]]] = {
    "fernet-token": _fernet_substituter,
}


def _redact_opaque(match: re.Match[str]) -> str:
    # Scored whole, not windowed as the fernet rule is, so the same dilution
    # that a windowed confirmation resists will hide a token inside a long
    # padded run here. The asymmetry is deliberate rather than an oversight:
    # this rule has no prefix to say a credential is even plausible, so it
    # judges a run it knows nothing about, and windowing it would convict long
    # ordinary runs on their most random-looking 64 characters — the false
    # positive that costs the leakage grading its evidence. The fernet rule can
    # afford the sharper reading because its header already narrowed the field.
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
        build = _CONFIRMED_SUBSTITUTIONS.get(rule)
        if build is None:
            text = pattern.sub(_REDACTION_MARKER.format(rule=rule), text)
        else:
            text = pattern.sub(build(), text)
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


def scan_lines(
    rel: str,
    lines: Iterable[str],
    known_secrets: Sequence[str],
    *,
    entropy: bool = True,
    run_id: str | None = None,
) -> list[Finding]:
    """Run every detector over one file's lines; findings carry ``rel`` as the path.

    ``entropy=False`` skips only the generic high-entropy heuristic — literal
    containment, the structured credential shapes, and the keyword-assignment
    rule all still run. For an engine transcript, whose format guarantees
    high-entropy runs as ordinary content (server-generated tool and request
    ids), the generic heuristic convicts every real file, which turns "scan
    then publish" into "never publish anything with content"; the detectors
    that still run are the ones that can actually name a credential there.

    ``run_id`` names the run being collected and narrows the high-entropy rule
    alone, exempting that run's own ledger directory where a cell's logged
    shell commands name it. Omitted, every detector reads exactly as it would
    without the argument.
    """
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
        if entropy and _entropy_hits(line, run_id=run_id):
            findings.append(Finding(path=rel, rule="high-entropy", line=lineno))
    return findings


def scan_file(
    path: Path,
    rel: str,
    known_secrets: Sequence[str],
    *,
    entropy: bool = True,
    run_id: str | None = None,
) -> list[Finding]:
    """Scan one file on disk; unreadable bytes are replaced, never fatal.

    Split on ``\\n`` only (not :meth:`str.splitlines`), so reported line
    numbers match what a reviewer sees on GitHub even for files carrying
    exotic unicode line separators. ``entropy`` and ``run_id`` pass through to
    :func:`scan_lines`.
    """
    text = path.read_bytes().decode("utf-8", errors="replace")
    return scan_lines(rel, text.split("\n"), known_secrets, entropy=entropy, run_id=run_id)


def scan_changes(
    changes: Iterable[PathChange],
    root: Path,
    known_secrets: Sequence[str],
    *,
    run_id: str | None = None,
) -> list[Finding]:
    """Scan every changed ``data/`` file under ``root`` (deletes have no blob).

    A non-addition is already a jail violation — but the jail only downgrades
    the PR to a draft, and a draft is still a *push*: a secret written into a
    modified tracked file would publish anyway. So content is scanned for
    every status that leaves bytes on disk, not just the adds the jail
    permits. Paths outside ``data/`` are left to the jail (they are never
    agent output). A listed file missing from disk is skipped (the jail
    check, not this one, owns change-list integrity). ``run_id`` passes
    through to :func:`scan_lines`.
    """
    findings: list[Finding] = []
    for change in changes:
        if change.status == "D" or not change.path.startswith(DATA_JAIL):
            continue
        target = root / change.path
        if not target.is_file():
            continue
        findings.extend(scan_file(target, change.path, known_secrets, run_id=run_id))
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
