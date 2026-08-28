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

Beside the disposition vocabulary sits a second, smaller one: the
**terminations** (:class:`fedcourtsai.schemas.MeritsTermination`), for entries
that end a granted case's merits proceeding while saying nothing about the
judgment below — the post-grant Rule 46 voluntary dismissal, a dismissal as
moot, an abatement on the petitioner's death, the Court vacating its own grant
order, and the bare mandate notation on a docket whose disposition entry the
corpus never captured.
They are read only as a *fallback*, once no disposition shape matched anywhere
in the payload, and the batch pass stamps them onto their own column
(``merits_terminated``) rather than ``merits_judgment``. That split is the
point: the row stops reading pending, so the forward-forecast gates that key on
an unlatched judgment close over it, while nothing enters the parsed slice the
merits base rate is pooled from — there is no disposition to enter. The batch
pass is the sole writer; the live poll latches dispositions only, and until a
sweep reaches a freshly terminated docket the high-recall snapshot scan
(:func:`fedcourtsai.pipeline.outcome.snapshot_shows_judgment`, which reads the
same termination shapes) holds the line.
"""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from collections.abc import Mapping
from datetime import date
from typing import Any, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..schemas import Judgment, MeritsTermination
from .cert_signals import entry_date, proceedings_entries
from .prefetch import prefetch_by_case

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

# The terminations: a granted case whose merits proceeding ended with no
# disposition of the judgment below. They anchor on the entry's own subject for
# the reason the disposition shapes do — the *motion* that precedes a Rule 46
# dismissal ("Motion to dismiss the case pursuant to Rule 46 filed by
# petitioner.", "Stipulation of dismissal under Rule 46.1 filed.") and a
# lower-court recital ("Notice of appeal filed from the judgment issued on ...")
# both name the shape mid-sentence and must stay unmatched.
#
# Most anchor at the ENTRY start rather than any sentence start, which is
# stricter than the disposition shapes' `_SENTENCE_START`: the Clerk enters a
# termination as its own one-sentence entry, so the strictness costs nothing on
# those shapes and a second-sentence spelling would read as a false negative,
# the cheap direction here. `_GRANT_VACATED_RE` is the one exception, and it
# says why in place.
#
# The subject noun is what carries the *stage*, the same cut `_DIG_RE` makes.
# Once certiorari has issued the Clerk writes about the case or the writ
# ("Case Dismissed - Rule 46.", "Writ of Certiorari Dismissed - Rule 46."), so
# either subject is a post-grant exit on its own evidence. The **petition** is
# stage-ambiguous: the same "Petition Dismissed - Rule 46." entry closes a
# granted docket's merits proceeding and, on a docket still at the petition
# stage, is a cert event the cert seam owns. So shapes built on the petition
# subject are admitted only where the caller can say the grant is on record
# (`cert_granted`) — the conditionality, rather than a wider subject
# alternation, is what keeps a petition-stage dismissal out of the merits
# vocabulary.
_POST_GRANT_SUBJECT = r"(?:the\s+)?(?:cases?|writs?(?:\s+of\s+certiorari)?)\b"
_PETITION_SUBJECT = r"(?:the\s+)?petitions?\b"

# Rule 46 — the parties' own voluntary dismissal, in the Clerk's terse docket
# spelling ("- Rule 46.") and the prose one ("dismissed pursuant to Rule 46.1").
_RULE_46_TAIL = r".{0,40}?\bdismissed\b.{0,40}?\brule\s*46\b"

# "dismissed as moot" — the controversy ended outside the Court (the petitioner
# was resentenced, the challenged action was withdrawn), so the merits question
# the grant opened is gone with nothing decided.
_AS_MOOT_TAIL = r".{0,40}?\bdismissed\b.{0,20}?\bas\s+moot\b"


def _entry_shape(subject: str, tail: str) -> re.Pattern[str]:
    """One termination shape: the subject noun at the entry start, then its tail."""
    return re.compile("^" + subject + tail, re.IGNORECASE | re.DOTALL)


# Abatement: a party died and the Court dismissed on that ground. The order is
# the one termination that opens on a *recital* rather than on its subject —
# "It appearing that petitioner died on ..., the petition for a writ of
# certiorari is DISMISSED." — so the entry anchor lands on the recital, and the
# subject the other shapes anchor on rides in the middle. The *suggestion* of
# death and the response to it ("Suggestion of death filed by counsel for
# petitioner.") open on their own filing nouns and stay unmatched.
#
# The recital alone is not enough, because a death also opens orders that
# *raise* dismissal instead of ordering it ("It appearing that respondent died
# on ..., the parties are directed to file supplemental briefs addressing
# whether the case should be dismissed.") — a live docket, and the one place in
# this table a subordinate clause could otherwise close a case forever. So the
# shape requires the order's own **operative verb on its named subject**:
# "... the petition ... is DISMISSED", never "should be dismissed". The subject
# is read through the same two fragments the dismissal shapes use, so an
# abatement spelled on the case or the writ is admitted on its own evidence
# while the petition spelling waits for the recorded grant, exactly as Rule 46
# and mootness do.
#
# The decree's subject must open its own clause — the gap ends on the comma
# that closes the recital — because the fragments would otherwise read the
# *object* of the petition spelling as a post-grant subject: "the petition for
# a **writ of certiorari** is DISMISSED" carries both nouns, and matching the
# inner one would admit the petition-stage order ungated and silently undo the
# conditionality. Excluding "." from the gaps keeps the recital and its decree
# in one sentence for the same reason the vacatur shape does.
def _abatement_shape(subject: str) -> re.Pattern[str]:
    """The abatement order for one subject noun: recital, death, then the decree."""
    return re.compile(
        r"^it\s+appearing\s+that\b[^.]{0,80}?\bdied\b[^.]{0,120}?,\s+"
        + subject
        + r"[^.]{0,40}?\b(?:is|are)\s+(?:hereby\s+)?dismissed\b",
        re.IGNORECASE,
    )


# The Court vacating its own grant order returns the case to the cert stage
# with the merits proceeding ended and nothing decided ("This case is no longer
# consolidated with No. 19-508 ...  The July 9, 2020 order granting the
# petition for a writ of certiorari in this case is vacated."). It is the one
# shape that rides as a **later sentence** of its entry — the Clerk states the
# reason first — so it takes the disposition shapes' `_SENTENCE_START` rather
# than the entry-start anchor. Two things carry the narrowness the entry anchor
# would otherwise: the sentence must open on the *order granting* (bare, or
# dated as the Clerk writes it), so a motion asking for the vacatur ("Motion to
# vacate the order granting certiorari filed.") names it mid-sentence and stays
# unmatched; and the order must be granting the **petition, writ, or
# certiorari** itself, so the Court vacating an interlocutory grant on the same
# docket ("The order granting the motion for divided argument is vacated.")
# leaves the live merits case alone. The gap excludes "." so the noun and the
# verb must share one sentence.
_GRANT_VACATED_RE = re.compile(
    _SENTENCE_START
    + r"(?:the\s+)?(?:\w+\s+\d{1,2},\s+\d{4}\s+)?orders?\s+granting\s+(?:the\s+)?"
    + r"(?:petitions?|writs?|certiorari)\b[^.]{0,80}?\bvacated\b",
    re.IGNORECASE,
)

# "as to" is how the Clerk marks a **partial** exit ("Case dismissed as to
# petitioner Smith only under Rule 46.1.", "Case Dismissed - Rule 46 as to
# respondent Jones."). Such a case continues as to the remaining parties, so
# its merits question is still live and closing pendency would lose a forecast
# the docket still owes — the false positive that actually costs something, and
# the same partial/whole line the disposition parser draws with its own mixed
# member. A veto over the **whole entry** rather than a tempered gap, because
# the phrase lands on either side of the citation.
_PARTIAL_SCOPE_RE = re.compile(r"\bas\s+to\b", re.IGNORECASE)

# A *rehearing* petition is a different filing from the one certiorari issued
# on: it is filed after the case is over, so disposing of it ("Petition for
# rehearing dismissed as moot.") says nothing about how the merits proceeding
# ended and must not be read as the exit. Bare "Petition ..." is the spelling
# the real shapes use, so the qualifier is what separates them, and it is
# checked as a veto rather than excluded inside each subject fragment.
_REHEARING_RE = re.compile(r"\bpetitions?\s+for\s+rehearing\b", re.IGNORECASE)

# "Judgment issued." — the mandate analog. On a docket whose disposition entry
# the corpus captured, this notation follows it and never decides anything (the
# disposition scan wins, because terminations are only consulted when no
# judgment shape matched anywhere). Standing alone it is all the record says:
# the case is over, and the entry states no verb for what happened to the
# judgment below.
_JUDGMENT_ISSUED_RE = re.compile(r"^judgments?\s+issued\b", re.IGNORECASE)


class _TerminationShape(NamedTuple):
    """One termination shape, its vetoes, its class, and the stage it needs."""

    #: The shape itself.
    pattern: re.Pattern[str]
    #: What disqualifies a match — empty where the shape stands alone. A veto is
    #: checked over the whole entry, so it can disqualify a match on text the
    #: shape's own bounded gaps never see.
    vetoes: tuple[re.Pattern[str], ...]
    #: The vocabulary member a match records.
    termination: MeritsTermination
    #: Whether the shape's subject is the stage-ambiguous *petition*, so the
    #: match counts as a merits termination only under a recorded cert grant.
    petition_subject: bool


#: The vetoes every dismissal shape carries: a partial exit leaves the case
#: live, and a rehearing petition is not the petition the grant issued on.
_DISMISSAL_VETOES: tuple[re.Pattern[str], ...] = (_PARTIAL_SCOPE_RE, _REHEARING_RE)

# Table order decides, because the first match wins. It rarely matters — the
# shapes want different words — but the tails can co-occur ("Case dismissed as
# moot pursuant to Rule 46."), and then the earlier row names the class. Rule 46
# leads deliberately: the citation is the Clerk's own statement of the
# authority the case exited under, while "as moot" is the reason the parties
# invoked it, so the rule is the more specific fact. Pendency reads the same
# either way; what the order settles is which bucket the published
# `terminations` distribution counts the row in.

_TERMINATION_SHAPES: tuple[_TerminationShape, ...] = (
    _TerminationShape(
        _entry_shape(_POST_GRANT_SUBJECT, _RULE_46_TAIL),
        _DISMISSAL_VETOES,
        MeritsTermination.voluntary_dismissal,
        petition_subject=False,
    ),
    _TerminationShape(
        _entry_shape(_PETITION_SUBJECT, _RULE_46_TAIL),
        _DISMISSAL_VETOES,
        MeritsTermination.voluntary_dismissal,
        petition_subject=True,
    ),
    _TerminationShape(
        _entry_shape(_POST_GRANT_SUBJECT, _AS_MOOT_TAIL),
        _DISMISSAL_VETOES,
        MeritsTermination.dismissed_moot,
        petition_subject=False,
    ),
    _TerminationShape(
        _entry_shape(_PETITION_SUBJECT, _AS_MOOT_TAIL),
        _DISMISSAL_VETOES,
        MeritsTermination.dismissed_moot,
        petition_subject=True,
    ),
    _TerminationShape(
        _abatement_shape(_POST_GRANT_SUBJECT),
        _DISMISSAL_VETOES,
        MeritsTermination.abated,
        petition_subject=False,
    ),
    _TerminationShape(
        _abatement_shape(_PETITION_SUBJECT),
        _DISMISSAL_VETOES,
        MeritsTermination.abated,
        petition_subject=True,
    ),
    _TerminationShape(
        _GRANT_VACATED_RE,
        _DISMISSAL_VETOES,
        MeritsTermination.grant_vacated,
        petition_subject=False,
    ),
    _TerminationShape(
        _JUDGMENT_ISSUED_RE, (), MeritsTermination.judgment_issued, petition_subject=False
    ),
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


def match_merits_termination(text: str, *, cert_granted: bool) -> MeritsTermination | None:
    """Parse one docket-entry description onto the merits-*termination* vocabulary.

    The complement of :func:`match_judgment`, for the entries that end a merits
    proceeding without stating what happened to the judgment below. Same
    conservatism, opposite failure cost: a false positive here does not
    fabricate a disposition (there is none to fabricate) but it does close a
    row's merits state, so the shapes stay start-anchored on the entry's own
    subject and the motion that *asks* for the dismissal never matches.

    ``cert_granted`` says whether the **docket** this entry belongs to is on
    record as having been granted certiorari, and it gates exactly the shapes
    whose subject is the stage-ambiguous *petition*: "Petition Dismissed - Rule
    46." is a merits exit on a granted docket and a cert-stage exit on an
    ungranted one, and the entry text alone cannot tell them apart. The
    caller — which holds the row, or knows it holds none — is where that fact
    lives, so it is threaded rather than assumed either way; the shapes whose
    subject is the case or the writ carry their own stage and are admitted
    regardless.
    """
    entry = text.strip()
    for shape in _TERMINATION_SHAPES:
        if shape.petition_subject and not cert_granted:
            continue
        if shape.pattern.search(entry) and not any(veto.search(entry) for veto in shape.vetoes):
            return shape.termination
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
    grant's own date, while an argued judgment lands months later — measured
    over the walked corpus, every labeled GVR sits at exactly gap 0 and the
    nearest genuine judgment (an expedited argued case) a full month after
    its grant, so the separation the guard rests on is 0 versus 30 days, not
    0 versus 1. `<=` rather
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


def last_merits_termination(
    payload: Mapping[str, Any], *, cert_granted: bool
) -> MeritsTermination | None:
    """The last termination-shaped entry in a stored docket payload, or ``None``.

    The :func:`last_judgment_entry` twin, and strictly its **fallback**: callers
    consult it only when no entry anywhere in the payload matched a judgment
    shape, so the mandate-analog notation that trails a real disposition can
    never displace it. The **last** match wins for the same reason it does
    there — the docket's final word is the realized one. No date is read: a
    termination records no outcome, so it has nothing to stamp a ``resolved_at``
    from. ``cert_granted`` is the docket-level fact
    :func:`match_merits_termination` gates its petition-subject shapes on,
    passed straight through — it is a property of the docket, so every entry in
    one payload is read under the same value.
    """
    found: MeritsTermination | None = None
    for text, _ in proceedings_entries(payload):
        termination = match_merits_termination(text, cert_granted=cert_granted)
        if termination is not None:
            found = termination
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
        ge=0,
        description="Snapshotted rows whose entries matched no judgment shape "
        "**and** no termination shape — the genuine residue",
    )
    terminated: int = Field(
        default=0,
        ge=0,
        description="Snapshotted rows with no judgment shape whose entries show "
        "the merits proceeding ended anyway (`MeritsTermination`) — resolved as "
        "to pendency, deliberately never as to disposition, so they stay out of "
        "the statpack's parsed slice and the disturbed rate",
    )
    terminations_written: int = Field(
        default=0,
        ge=0,
        description="Terminated rows whose `merits_terminated` column the pass "
        "wrote (apply) or would write (dry-run); the rest already carry it",
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
    terminations: dict[str, int] = Field(
        default_factory=dict,
        description="Termination distribution, MeritsTermination value -> row "
        "count. Published per class rather than only as the `terminated` total "
        "because the classes carry different evidence, and two of them are "
        "triage signals rather than docket trends: a voluntary dismissal, a "
        "mootness dismissal, and an abatement are proceedings the docket says "
        "ended with nothing decided, but the mandate notation is all a docket "
        "says about a case that *was* decided (a climb there is a "
        "disposition-parser gap), and a vacated grant leaves the row's cert "
        "`disposition` describing an order the Court withdrew (a climb there is "
        "a cert-label gap). Counted per row from its **last** matching entry, "
        "so a docket carrying two termination shapes is attributed to the later "
        "one — this is a distribution over dockets' final words, not a "
        "partition of the shapes the corpus holds",
    )


def backfill_merits_judgments(conn: sqlite3.Connection, *, apply: bool) -> MeritsBackfillResult:
    """Parse each merits-bound SCOTUS row's stored snapshot for its judgment.

    The population is :func:`fedcourtsai.corpus.opens_merits_proceeding` — a
    cert grant that is actually followed by briefing, argument, and a separate
    judgment, so a GVR's own vacatur never enters the merits record. For each
    such row, read the case's latest stored
    snapshot (:func:`fedcourtsai.corpus.latest_snapshot` — SQLite, or the
    per-case content store under the corpus-split mode, where the reads go
    through :func:`~fedcourtsai.pipeline.prefetch.prefetch_by_case` so the
    pass costs a bounded fan-out rather than a serial walk of GET latency),
    parse the **last** judgment-shaped entry, and stamp ``merits_judgment`` /
    ``merits_decided``
    through :func:`fedcourtsai.corpus.set_merits_judgment`. Idempotent — a
    re-run over an unchanged corpus reports everything ``unchanged`` and writes
    nothing new — and degradation is counted, never fatal: a row whose snapshot
    is unreachable (none stored, or the content store not configured) lands in
    ``no_snapshot`` and keeps whatever the columns already carry. A row with no
    judgment shape anywhere gets the termination fallback
    (:func:`last_merits_termination`) before it is written off as ``no_match``:
    a match stamps ``merits_terminated`` through
    :func:`fedcourtsai.corpus.set_merits_termination`, resolving the row's
    pendency without asserting a disposition it does not have. A stored
    judgment the pass can no longer re-derive is never cleared but is counted
    (``stale``), so a parser tightening that retracts a reading stays visible
    instead of silently persisting in the statpack. Dry-run unless ``apply``.
    """
    no_snapshot = no_match = parsed = unchanged = stale = terminated = 0
    judgments: Counter[str] = Counter()
    terminations_found: Counter[str] = Counter()
    updates: list[tuple[str, Judgment, date | None]] = []
    terminations: list[tuple[str, MeritsTermination]] = []
    # Materialized before the prefetch, not walked beside it: `iter_rows` is a
    # lazily consumed cursor on `conn`, and stepping it while the prefetch's
    # workers read would put two readers on one connection. The rows are
    # metadata — the payloads stay in the prefetch's streamed window.
    rows = [
        row for row in corpus.iter_rows(conn, court="scotus") if corpus.opens_merits_proceeding(row)
    ]
    eligible = len(rows)
    # `latest_snapshot` never touches `conn` where payload reads are offloaded
    # (the registered source serves it, and its Protocol requires tolerance of
    # concurrent reads), which is what makes handing the call to the prefetch
    # pool's worker threads sound; the mode cannot flip mid-pass because
    # nothing here re-registers the source. The loop body below runs on the
    # calling thread either way, so pooled and serial passes classify, count,
    # and order identically.
    with prefetch_by_case(
        [row.case_id for row in rows],
        lambda case_id: corpus.latest_snapshot(conn, case_id),
        thread_name_prefix="merits-backfill",
    ) as fetched:
        for row, (_, found) in zip(rows, fetched, strict=True):
            if found is None:
                no_snapshot += 1
                if row.merits_judgment is not None:
                    stale += 1
                continue
            entry = last_judgment_entry(found[1])
            if entry is None:
                if row.merits_judgment is not None:
                    # A row that already carries a judgment this pass can no
                    # longer re-derive is a **retracted parse**, not a
                    # terminated proceeding, so the fallback does not run here.
                    # The mandate notation trails an ordinary decided docket,
                    # so absorbing these into `terminated` would silence the
                    # very retraction `stale` exists to surface — and would
                    # pair a stored disposition with a termination on one row,
                    # the one state the two columns are defined never to share.
                    no_match += 1
                    stale += 1
                    continue
                # Only now — no disposition anywhere in the payload, and none
                # stored — does the termination fallback run, so a termination
                # can never displace a judgment or sit beside one.
                # Every row here passed `opens_merits_proceeding`, so the grant
                # is on record and the petition-subject shapes are in scope —
                # read off the row rather than assumed, so a widening of that
                # population cannot silently promote a petition-stage dismissal.
                termination = last_merits_termination(
                    found[1], cert_granted=row.date_cert_granted is not None
                )
                if termination is None:
                    no_match += 1
                    continue
                terminated += 1
                terminations_found[termination.value] += 1
                if row.merits_terminated != termination.value:
                    terminations.append((row.case_id, termination))
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
        for case_id, termination in terminations:
            corpus.set_merits_termination(conn, case_id, termination)
    return MeritsBackfillResult(
        applied=apply,
        eligible=eligible,
        no_snapshot=no_snapshot,
        no_match=no_match,
        terminated=terminated,
        terminations_written=len(terminations),
        stale=stale,
        parsed=parsed,
        unchanged=unchanged,
        updated=len(updates),
        judgments=dict(sorted(judgments.items())),
        terminations=dict(sorted(terminations_found.items())),
    )
