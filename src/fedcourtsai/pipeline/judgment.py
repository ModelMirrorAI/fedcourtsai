"""Merits-judgment extraction: read what the Court did to the judgment below.

Once certiorari is granted, the case's terminal docket entry states the merits
disposition — "Judgment REVERSED and case REMANDED.", "Adjudged to be
AFFIRMED.", "Writ of certiorari DISMISSED as improvidently granted." — which
no other seam normalizes (the corpus row's ``disposition`` carries the
*cert* label; the routing backstop ``_TERMINAL_ENTRY_RE`` in
:mod:`fedcourtsai.pipeline.outcome` only detects that such an entry exists).
This module is the deterministic parser from that entry text onto the
:class:`fedcourtsai.schemas.Judgment` vocabulary, plus the ``disturbed``
projection the merits base rate scores against, and a best-effort authorship
reader.

Every shape here is **anchored on a sentence opening with the disposition's own
noun** ("Judgment ...", "Adjudged to be ...", "Writ of certiorari ... dismissed
...") for the same reason the routing backstop start-anchors: a
lower-court-history recital or a motion opens with "Notice of appeal ..." /
"Motion ..." (the SG's confession-of-error motion, respondent's motion to
dismiss the writ as improvidently granted) and names the judgment only
mid-sentence, so it must stay unmatched — while the canonical GVR order, whose
disposition sentence follows the cert recital ("Petition GRANTED.  Judgment
VACATED ..."), still parses. A false negative costs one unparsed row in a
descriptive count; a false positive would fabricate a merits ground truth — so
the parser is deliberately conservative.

Two writers stamp the parsed judgment onto the corpus row (``merits_judgment``
/ ``merits_decided``), both through this parser so detection stays
single-sourced: the live poll latches it at ingest for a granted docket
(:func:`fedcourtsai.pipeline.ingest.map_live_docket`), which is what lets
outcome detection resolve the open merits event from the columns alone, and
the batch pass (:func:`backfill_merits_judgments`) reads each merits-bound
SCOTUS case's latest stored snapshot through :func:`fedcourtsai.corpus.latest_snapshot`
— the same offline access path the salience replay uses, which under the
corpus-split mode transparently serves from the per-case content store — as
the offline reconciler over rows the poller has not touched. Both feed the
statpack's merits stage section.
"""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from collections.abc import Mapping
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..schemas import Judgment
from .cert_signals import entry_date, proceedings_entries

# A judgment shape may open the entry or any later sentence of it: the
# canonical GVR order leads with the cert recital ("Petition GRANTED.  Judgment
# VACATED and case REMANDED for further consideration in light of ..."), so
# entry-start anchoring alone would silently drop the GVR class — an
# outcome-correlated miss, since a GVR is always a vacatur. Sentence-start
# keeps the conservatism the anchoring exists for: a motion or recital names
# the judgment mid-sentence ("Motion of respondent to vacate the judgment and
# remand ... filed.", "Notice of appeal filed from the judgment affirmed on
# ..."), and no sentence of either opens with the noun.
_SENTENCE_START = r"(?:^|(?<=[.!?])\s+)"

# The disposition sentence opens with its noun; every judgment shape requires
# it. "The judgment(s) ..." and the older "Adjudged to be ..." recital are the
# two merits spellings; the DIG order opens on the writ (or, rarely, the case /
# appeal) instead, so it carries its own anchor below.
_JUDGMENT_NOUN = _SENTENCE_START + r"(?:the\s+)?(?:judgments?|adjudged(?:\s+to\s+be)?)\b"

# Checked before the plain single-verb shape, which "affirmed" would otherwise
# swallow: an affirmance by an equally divided Court is its own (non-merits)
# outcome, never a merits affirmance.
_EQUALLY_DIVIDED_RE = re.compile(
    _JUDGMENT_NOUN + r".{0,80}?\baffirmed\s+by\s+an\s+equally\s+divided\s+court\b",
    re.IGNORECASE | re.DOTALL,
)

# Both part-verbs required, in either order ("affirmed in part and reversed in
# part" / "reversed in part, affirmed in part"); a vacatur-in-part reads onto
# the same mixed member — the enum carries one mixed value, and either verb
# disturbs the judgment below identically. Checked before the single-verb
# shape, whose first verb would otherwise decide alone.
_IN_PART_RE = re.compile(
    _JUDGMENT_NOUN
    + r".{0,80}?(?:\baffirmed\s+in\s+part\b.{0,80}?\b(?:reversed|vacated)\s+in\s+part\b"
    + r"|\b(?:reversed|vacated)\s+in\s+part\b.{0,80}?\baffirmed\s+in\s+part\b)",
    re.IGNORECASE | re.DOTALL,
)

# The plain merits verbs. The noun-verb gap is 80 — wide enough for the prose
# form to name the lower court between the noun and the verb ("Judgment of the
# United States Court of Appeals for the Ninth Circuit REVERSED ..."), the same
# width the resolver's vacate-and-remand rule uses for the same reason; a
# "... and case REMANDED" suffix rides after the match and needs no handling
# (a GVR's "Judgment VACATED and case REMANDED for further consideration in
# light of ..." reads as vacated).
_SINGLE_RE = re.compile(
    _JUDGMENT_NOUN + r".{0,80}?\b(affirmed|reversed|vacated)\b",
    re.IGNORECASE | re.DOTALL,
)

# The DIG order: "Writ of certiorari DISMISSED as improvidently granted." Its
# sentence-opening anchor deliberately excludes "Motion ..." (respondent moving
# to dismiss the writ is not the Court dismissing it) and "Petition ..." (a
# petition-stage dismissal is a cert event, not a merits exit).
_DIG_RE = re.compile(
    _SENTENCE_START + r"(?:the\s+)?(?:writs?(?:\s+of\s+certiorari)?|cases?|appeals?)\b"
    r".{0,60}?\bdismissed\b.{0,20}?\bas\s+improvidently\s+granted\b",
    re.IGNORECASE | re.DOTALL,
)

#: The sentinel :func:`opinion_author` returns for a per curiam opinion —
#: distinguishable from any parsed Justice name, which is a single
#: space-free token.
PER_CURIAM = "per curiam"

# "Gorsuch, J., delivered the opinion of the Court ..." — the modern authorship
# recital. One space-free name token before ", J.," / ", C. J.,", so a
# preceding sentence ("... case REMANDED.") can never bleed into the capture;
# best-effort by design: a "The Chief Justice delivered ..." spelling parses as
# absent, and a multi-token historical name ("Van Devanter") reads as its final
# token — acceptable on an advisory surface nothing stored or scored reads.
_AUTHOR_RE = re.compile(
    r"([A-Za-z][A-Za-z'-]*),\s*(?:C\.\s*J\.|J\.),\s+delivered\s+the\s+opinion\s+of\s+the\s+Court",
    re.IGNORECASE,
)

_PER_CURIAM_RE = re.compile(r"\bper\s+curiam\b", re.IGNORECASE)

# The judgments that disturb the decision below. A DIG and an equally divided
# affirmance are non-merits exits that leave the lower judgment standing — a
# DIG dissolves the writ, not the judgment, and an equally divided Court
# affirms by operation of law — so both project to False (undisturbed) and are
# scored on that footing, since the pooled baseline's denominator counts them
# the same way (see docs/decision-model.md and the Judgment docstring).
_DISTURBED: frozenset[Judgment] = frozenset(
    {Judgment.reversed, Judgment.vacated, Judgment.affirmed_in_part}
)


def match_judgment(text: str) -> Judgment | None:
    """Parse one docket-entry description onto the merits-judgment vocabulary.

    Deterministic and conservative: a shape matches only where a sentence opens
    with the disposition's own noun, so recitals and motions return ``None``
    and a shape this parser does not know stays an unparsed gap rather than a
    guess.
    The specific shapes (equally divided, in-part) are checked before the
    general single-verb one, whose first verb would otherwise decide.
    """
    entry = text.strip()
    if _EQUALLY_DIVIDED_RE.search(entry):
        return Judgment.equally_divided
    if _IN_PART_RE.search(entry):
        return Judgment.affirmed_in_part
    if match := _SINGLE_RE.search(entry):
        return Judgment(match.group(1).lower())
    if _DIG_RE.search(entry):
        return Judgment.dig
    return None


def judgment_disturbed(judgment: Judgment) -> bool:
    """Whether the Court disturbed the judgment below — the merits binary.

    True for reversed / vacated / the mixed in-part outcome; False for a plain
    affirmance. The two non-merits exits also project to False because both
    leave the lower court's judgment intact: a dismissal as improvidently
    granted dissolves the *writ* while the judgment below stands untouched, and
    an equally divided Court affirms by operation of law. They are not merits
    wins for respondent, but they are scored on this projection all the same:
    the pooled baseline's denominator counts them as undisturbed too, so
    keeping them in holds the scored population and its baseline to one
    population. ``judgment_correct`` preserves their own labels, so the
    exact-match axis never confuses a DIG with an affirmance.
    """
    return judgment in _DISTURBED


def judgment_rode_the_grant_order(merits_decided: date, date_cert_granted: date) -> bool:
    """Whether a parsed judgment's disposition rode the cert order itself.

    The label-independent guard on the merits pool (`docs/decision-model.md`):
    the `gvr` label is a forward convention and `summary-reversal` has no
    resolver, so a grant Term resolved into the corpus before those labels
    existed carries such grants as plain `granted` — passing
    `opens_merits_proceeding` — with a vacatur that parses the day it was
    granted. What separates that class without reading the label is the
    grant→judgment gap: a disposition riding in the cert order carries the
    grant's own date, while an argued judgment lands months later (an
    expedited argued case still lands days later, never same-day). `<=` rather
    than `==` so a data-noise judgment date *before* its grant is excluded on
    the same reasoning rather than admitted by accident.
    """
    return merits_decided <= date_cert_granted


def grant_term_year(granted: date) -> int:
    """The October Term a cert-grant date falls in (a new Term opens in October).

    The merits cohort's Term axis, shared by the statpack's merits section and
    the merits base rate's leakage guard: keyed on the grant date rather than
    the docket number because a case is often granted the Term after it was
    docketed, and the merits cohort is defined by the grant. The pivot is the
    calendar month, a deliberate convention: a late-September long-conference
    grant order — issued for the *incoming* Term — lands in the outgoing Term's
    row. Consistent and stated, so do not "fix" it in one caller.
    """
    return granted.year if granted.month >= 10 else granted.year - 1


def opinion_author(text: str) -> str | None:
    """Best-effort: who delivered the opinion of the Court, from the entry text.

    Returns the Justice's name exactly as the entry prints it ("Gorsuch"),
    :data:`PER_CURIAM` when the entry marks a per curiam opinion instead, and
    ``None`` when neither is present. Deliberately simple — one space-free name
    token before ", J.," / ", C. J.," — so an unrecognized spelling reads as
    absent rather than wrong. Advisory only: nothing stored or scored reads it.
    """
    if match := _AUTHOR_RE.search(text):
        return match.group(1)
    if _PER_CURIAM_RE.search(text):
        return PER_CURIAM
    return None


def last_judgment_entry(payload: Mapping[str, Any]) -> tuple[Judgment, date | None] | None:
    """The last judgment-shaped entry in a stored docket payload, with its date.

    Reads either payload shape through
    :func:`fedcourtsai.pipeline.cert_signals.proceedings_entries`. The **last**
    match wins: a granted-rehearing or amended-judgment docket restates the
    disposition, and the docket's final word is the realized one. The date is
    the entry's own docket date under the strict
    :func:`~fedcourtsai.pipeline.cert_signals.entry_date` parse — ``None`` for
    an undated or partially dated entry, never a guess.
    """
    found: tuple[Judgment, date | None] | None = None
    for text, raw in proceedings_entries(payload):
        judgment = match_judgment(text)
        if judgment is not None:
            found = (judgment, entry_date(raw))
    return found


class MeritsBackfillResult(BaseModel):
    """What one merits backfill pass over the merits-bound SCOTUS rows did (or would do)."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the corpus (False = dry-run)")
    eligible: int = Field(
        ge=0,
        description="SCOTUS rows whose cert grant opens a merits proceeding "
        "(`corpus.opens_merits_proceeding`)",
    )
    no_snapshot: int = Field(
        ge=0, description="Eligible rows with no stored snapshot reachable — skipped"
    )
    no_match: int = Field(
        ge=0, description="Snapshotted rows whose entries matched no judgment shape"
    )
    stale: int = Field(
        ge=0,
        description="Rows carrying a stored judgment the current pass could not "
        "re-derive (snapshot unreachable, or no longer matching) — the pass "
        "never clears a stored value, so this is the visibility a retracted "
        "parse gets; a persistent count is the maintainer's triage signal",
    )
    parsed: int = Field(ge=0, description="Rows with a parsed merits judgment")
    unchanged: int = Field(
        ge=0, description="Parsed rows whose stored columns already carry the parse"
    )
    updated: int = Field(ge=0, description="Parsed rows written (apply) or that would be (dry-run)")
    judgments: dict[str, int] = Field(
        default_factory=dict,
        description="Parsed-judgment distribution, Judgment value -> row count",
    )


def backfill_merits_judgments(conn: sqlite3.Connection, *, apply: bool) -> MeritsBackfillResult:
    """Parse each merits-bound SCOTUS row's stored snapshot for its judgment.

    The population is :func:`fedcourtsai.corpus.opens_merits_proceeding` — a
    cert grant that is actually followed by briefing, argument, and a separate
    judgment, so a GVR's own vacatur never enters the merits record. For each
    such row, read the case's latest stored
    snapshot (:func:`fedcourtsai.corpus.latest_snapshot` — SQLite, or the
    per-case content store under the corpus-split mode), parse the **last**
    judgment-shaped entry, and stamp ``merits_judgment`` / ``merits_decided``
    through :func:`fedcourtsai.corpus.set_merits_judgment`. Idempotent — a
    re-run over an unchanged corpus reports everything ``unchanged`` and writes
    nothing new — and degradation is counted, never fatal: a row whose snapshot
    is unreachable (none stored, or the content store not configured) lands in
    ``no_snapshot`` and keeps whatever the columns already carry. A stored
    judgment the pass can no longer re-derive is never cleared but is counted
    (``stale``), so a parser tightening that retracts a reading stays visible
    instead of silently persisting in the statpack. Dry-run unless ``apply``.
    """
    eligible = no_snapshot = no_match = parsed = unchanged = stale = 0
    judgments: Counter[str] = Counter()
    updates: list[tuple[str, Judgment, date | None]] = []
    for row in corpus.iter_rows(conn, court="scotus"):
        if not corpus.opens_merits_proceeding(row):
            continue
        eligible += 1
        found = corpus.latest_snapshot(conn, row.case_id)
        if found is None:
            no_snapshot += 1
            if row.merits_judgment is not None:
                stale += 1
            continue
        entry = last_judgment_entry(found[1])
        if entry is None:
            no_match += 1
            if row.merits_judgment is not None:
                stale += 1
            continue
        judgment, decided = entry
        parsed += 1
        judgments[judgment.value] += 1
        if row.merits_judgment == judgment.value and row.merits_decided == decided:
            unchanged += 1
            continue
        updates.append((row.case_id, judgment, decided))
    if apply:
        for case_id, judgment, decided in updates:
            corpus.set_merits_judgment(conn, case_id, judgment, decided)
    return MeritsBackfillResult(
        applied=apply,
        eligible=eligible,
        no_snapshot=no_snapshot,
        no_match=no_match,
        stale=stale,
        parsed=parsed,
        unchanged=unchanged,
        updated=len(updates),
        judgments=dict(sorted(judgments.items())),
    )
