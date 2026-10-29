"""Merits-judgment extraction: read what the Court did to the judgment below.

Once certiorari is granted, the case's terminal docket entry states the merits
disposition — "Judgment REVERSED and case REMANDED.", "Adjudged to be
AFFIRMED.", "Writ of certiorari DISMISSED as improvidently granted." — which
no other seam normalizes (the corpus row's ``disposition`` carries the
*cert* label; the routing backstop ``_TERMINAL_ENTRY_RE`` in
:mod:`fedcourtsai.pipeline.outcome` only detects that such an entry exists).
This module is the deterministic parser from that entry text onto the
:class:`fedcourtsai.schemas.Judgment` vocabulary, plus the ``disturbed``
projection the merits base rate scores against, a best-effort authorship
reader, and the two opinion-form predicates (:func:`signed_opinion`,
:func:`per_curiam_opinion`) the merits decision record
(:mod:`fedcourtsai.pipeline.decision_record`) reads.

Every shape here is **anchored on a sentence opening with the disposition's own
noun** ("Judgment ...", "Adjudged to be ...", "Writ of certiorari ... dismissed
...") for the same reason the routing backstop start-anchors: a
lower-court-history recital or a motion opens with "Notice of appeal ..." /
"Motion ..." (the SG's confession-of-error motion, respondent's motion to
dismiss the writ as improvidently granted) and names the judgment only
mid-sentence, so it must stay unmatched — while the canonical GVR order, whose
disposition sentence follows the cert recital ("Petition GRANTED.  Judgment
VACATED ..."), still parses. The subject may also be the lower-court ruling
certiorari ran to ("The en banc order of the United States Court of Appeals
... is vacated", "Determination of ... REVERSED"), and a summary disposition
may follow its grant recital after a comma or "and" ("Petition for certiorari
GRANTED, judgment REVERSED."). A consolidated entry that disposes of several
dockets clause by clause is read for the docket's own clause
(:func:`match_judgment`). A false negative costs one unparsed row in a
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

import html
import re
import sqlite3
from collections import Counter
from collections.abc import Mapping
from datetime import date
from typing import Any, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..schemas import Judgment, MeritsTermination, Stage
from .cert_signals import entry_date, proceedings_entries
from .justices import resolve_surname
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

# A summary disposition can share one sentence with the grant it rides on:
# "Petition for certiorari GRANTED, judgment REVERSED." / "Petition GRANTED and
# judgment REVERSED." The noun then follows a comma or "and", never a sentence
# break, so the entry's own opening grant recital is the second anchor. It is
# entry-start and petition-subject on purpose: a motion granted in the same
# breath ("Motion ... GRANTED, judgment ...") opens on its filing noun and stays
# unmatched, and so does a rehearing petition, which is filed after the case is
# over and is not the petition the grant issued on.
_GRANT_RECITAL = (
    r"^(?:the\s+)?petition(?!s?\s+for\s+rehearing\b)s?\b[^.]{0,80}?\bgranted\s*(?:,|\s+and)\s+"
)

# A consolidated entry can label a companion's disposition by opening its
# sentence on the companion's number: "No. 25-567, adjudged to be affirmed.",
# "No. 25-406, judgment REVERSED and case REMANDED." The citation then stands
# where the sentence break would, and the clause reading
# (:func:`match_judgment`) attributes the disposition to the cited docket.
_CITATION_LEAD = (
    _SENTENCE_START + r"nos?\.\s*\d{2}-\d+(?:\s*(?:,\s*(?:and\s+)?|and\s+|&\s*)\d{2}-\d+)*,\s+"
)

# The disposition sentence opens with its noun; every judgment shape requires
# it. "The judgment(s) ..." and the older "Adjudged to be ..." recital are the
# two merits spellings; the DIG order opens on the writ (or, rarely, the case /
# appeal) instead, so it carries its own anchor below.
_JUDGMENT_NOUN = (
    r"(?:" + _SENTENCE_START + "|" + _GRANT_RECITAL + "|" + _CITATION_LEAD + r")"
    r"(?:the\s+)?(?:judgments?|adjudged(?:\s+to\s+be)?)\b"
)

# Where certiorari ran to a ruling short of a final judgment — a preliminary
# injunction, an en banc order, a qualified-immunity determination — the Court
# disposes of that ruling by name: "The en banc order of the United States Court
# of Appeals ... is vacated", "The December 29, 2020 order of the United States
# District Court ... is reversed", "February 13, 2018 order VACATED, November 9,
# 2017 order AFFIRMED IN PART, ...", "Determination of United States Court of
# Appeals ... that Rivas-Villegas is not entitled to qualified immunity
# REVERSED."
#
# The Court also writes "The order ... is vacated" about its *own* orders ("The
# order heretofore entered by The Chief Justice is vacated.", "The order of
# October 2, 2023 consolidating the cases is vacated.", "The order setting the
# case for argument is vacated."), so a bare "order" is never a subject. It is
# admitted only where the sentence identifies it as the lower court's ruling, by
# an allow-list: the en banc order; an order dated in front of the noun, the way
# the Court names a lower court's ruling (a date *after* "order of" is how it
# names its own); or an order or determination "of" a named court other than
# this one ("of the United States Court of Appeals ...", "of the District Court
# ...", "of the Supreme Court of Ohio").
_MONTH = (
    r"(?:january|february|march|april|may|june|july|august|september|october"
    r"|november|december)"
)
_OF_A_LOWER_COURT = (
    r"\s+of\s+(?!(?:the\s+|this\s+)?court\b)(?:the\s+)?(?:united\s+states\s+)?"
    r"(?:court\s+of\s+(?:criminal\s+)?appeals|district\s+court|(?:[a-z]+\s+){1,4}?court)\b"
)
_RULING_NOUN = (
    _SENTENCE_START
    + r"(?:the\s+)?(?:en\s+banc\s+orders?\b|"
    + _MONTH
    + r"\s+\d{1,2},\s+\d{4}\s+orders?\b|(?:orders?|determination)"
    + _OF_A_LOWER_COURT
    + r")"
)

# The ruling subject's gap to its verb may not cross what marks an order as
# interlocutory or as the Court's own — "granting", "staying", "denying" ("The
# January 13, 2021 order of the Court of Appeals granting a stay is vacated."
# disposes of a stay, never of the judgment below), "heretofore", "entered by".
# The judgment subject carries no such veto: "The judgment of the Court of
# Appeals denying habeas relief is reversed." is a merits reversal.
_RULING_GAP = r"(?:(?!\b(?:granting|staying|denying|heretofore|entered\s+by)\b).){0,120}?"

# The Clerk's entry for an application's own disposition ("Application (20A134)
# granted by the Court.  ... The January 13, 2021 order of the Court of Appeals
# granting a stay is vacated.") disposes of interim relief on the application,
# so its sentences never name a merits ruling: the ruling subject is not read in
# an entry opening on it. The judgment subject is, since a merits judgment can
# follow an application's disposal in one entry ("Application (22A444) DENIED AS
# MOOT.  Judgment REVERSED and case REMANDED.").
_APPLICATION_ENTRY_RE = re.compile(r"^application\s*\(", re.IGNORECASE)

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
# shape, whose first verb would otherwise decide alone. Each shape below is
# compiled twice, with and without the ruling subject (see
# `_APPLICATION_ENTRY_RE`).
_IN_PART_TAIL = (
    r".{0,80}?(?:\baffirmed\s+in\s+part\b.{0,80}?\b(?:reversed|vacated)\s+in\s+part\b"
    + r"|\b(?:reversed|vacated)\s+in\s+part\b.{0,80}?\baffirmed\s+in\s+part\b)"
)
_IN_PART_RE = re.compile(_JUDGMENT_NOUN + _IN_PART_TAIL, re.IGNORECASE | re.DOTALL)
_IN_PART_RULING_RE = re.compile(
    r"(?:" + _JUDGMENT_NOUN + "|" + _RULING_NOUN + r")" + _IN_PART_TAIL,
    re.IGNORECASE | re.DOTALL,
)

# The plain merits verbs. The judgment subject's gap to its verb is 120, wide
# enough for the prose form to name the lower court and its own docket numbers
# between them ("The judgment of the United States Court of Appeals for the
# District of Columbia Circuit in Nos. 19-5094 and 19-5096 is vacated"); the
# ruling subject's is the same width under `_RULING_GAP`'s veto. A "... and case
# REMANDED" suffix rides after the match and needs no handling (a GVR's
# "Judgment VACATED and case REMANDED for further consideration in light of
# ..." reads as vacated).
_VERB = r"\b(affirmed|reversed|vacated)\b"
_SINGLE_RE = re.compile(_JUDGMENT_NOUN + r".{0,120}?" + _VERB, re.IGNORECASE | re.DOTALL)
_SINGLE_RULING_RE = re.compile(
    r"(?:" + _JUDGMENT_NOUN + r".{0,120}?|" + _RULING_NOUN + _RULING_GAP + r")" + _VERB,
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
# the cheap direction here. `_GRANT_VACATED_RE` and the in-order Rule 46 decree
# (`_decree_rule_46_shape`) are the exceptions, and each says why in place.
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


# The Court's own Rule 46 decree can ride inside a longer order rather than as
# the Clerk's one-sentence entry: "In light of the Government's representations,
# the motions for leave to intervene are denied, and the petitions in Nos.
# 20-429, 20-454, and 20-539 are dismissed pursuant to Rule 46.1." So the subject
# may open the entry, a sentence, or a clause after a comma or semicolon — and
# what carries the narrowness the entry anchor gives the other shapes is the
# **operative verb**: "is/are dismissed pursuant to (or under) Rule 46". The
# parties' stipulation ("Joint stipulation to dismiss the cases ... pursuant to
# Rule 46.1 filed.") and a motion asking for the dismissal open on their filing
# nouns and never say "are dismissed"; a dissent from the dismissal ("would ...
# deny the stipulations to dismiss the petitions") does not either. The gap
# keeps the subject and the verb in one clause, while letting a "No." / "Nos."
# citation's period through.
def _decree_rule_46_shape(subject: str) -> re.Pattern[str]:
    """The in-order Rule 46 decree for one subject noun."""
    return re.compile(
        r"(?:^|(?<=[.;,])\s+(?:and\s+)?)"
        + subject
        + r"(?:[^.;]|\bnos?\.){0,80}?\b(?:is|are)\s+(?:hereby\s+)?dismissed\s+"
        + r"(?:pursuant\s+to|under)\s+rule\s*46\b",
        re.IGNORECASE,
    )


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
        _decree_rule_46_shape(_POST_GRANT_SUBJECT),
        _DISMISSAL_VETOES,
        MeritsTermination.voluntary_dismissal,
        petition_subject=False,
    ),
    _TerminationShape(
        _decree_rule_46_shape(_PETITION_SUBJECT),
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
#: distinguishable from any parsed Justice name because no surname the roster
#: (:mod:`fedcourtsai.pipeline.justices`) resolves is spelled ``per curiam``
#: (a test pins that), and the unknown-name fallback yields one token, which
#: cannot carry the sentinel's space.
PER_CURIAM = "per curiam"

# "Gorsuch, J., delivered the opinion of the Court ..." — the modern authorship
# recital. The capture is a short window of name-shaped tokens (no periods, so
# a preceding sentence's "... case REMANDED." can never bleed in) rather than
# one token, because a surname may span tokens ("Van Devanter"); which suffix
# of the window is the name is resolved against the committed roster, so a
# joining word swept into the window ("and Gorsuch") costs nothing, and an
# entirely unknown spelling yields its final token — a single-token result.
# Best-effort by design: a "The Chief Justice delivered ..." spelling parses
# as absent. Advisory only; nothing stored or scored reads it.
_AUTHOR_RE = re.compile(
    r"((?:[A-Za-z][A-Za-z'-]*\s+){0,2}[A-Za-z][A-Za-z'-]*)"
    r",\s*(?:C\.\s*J\.|J\.),\s+delivered\s+the\s+opinion\s+of\s+the\s+Court",
    re.IGNORECASE,
)

_PER_CURIAM_RE = re.compile(r"\bper\s+curiam\b", re.IGNORECASE)

# The live docket wraps the opinion in a link — "Gorsuch, J., delivered the <a
# href = '...'>opinion</a> of the Court", "<a href = '...'>Opinion</a> per
# curiam." — so the authorship shapes read the entry's text with its markup
# dropped, the way the Court's own page renders it.
_TAG_RE = re.compile(r"<[^>]+>")


def entry_plain_text(text: str) -> str:
    """An entry's text with its HTML markup and entities dropped, whitespace collapsed."""
    return " ".join(html.unescape(_TAG_RE.sub(" ", text)).split())


# The judgments that disturb the decision below. A DIG and an equally divided
# affirmance are non-merits exits that leave the lower judgment standing — a
# DIG dissolves the writ, not the judgment, and an equally divided Court
# affirms by operation of law — so both project to False (undisturbed) and are
# scored on that footing, since the pooled baseline's denominator counts them
# the same way (see docs/decision-model.md and the Judgment docstring).
_DISTURBED: frozenset[Judgment] = frozenset(
    {Judgment.reversed, Judgment.vacated, Judgment.affirmed_in_part}
)


# A consolidated judgment entry states each docket's disposition in its own
# clause, and each docket's copy of the entry carries every clause: "Judgment
# AFFIRMED (as to No. 22-23); Judgment REVERSED and case REMANDED (as to No.
# 22-331).", "Judgment REVERSED and case REMANDED. No. 25-567, adjudged to be
# affirmed." The clauses are the entry's sentences and semicolon-separated
# parts. A period ends a clause except after the abbreviations a disposition
# entry carries — "No." / "Nos.", a single initial ("U. S.", "C. J.", "J.",
# "v."), "JJ.", "Inc.", "Co.", "Corp.", "St." An abbreviation outside that list
# splits a sentence early; the cost is bounded, because a clause that splits a
# judgment noun from its verb matches nothing, and an entry with no matching
# clause is read whole.
_CLAUSE_BREAK_RE = re.compile(
    r"(?<!\bno\.)(?<!\bnos\.)(?<!\b[a-z]\.)(?<!\bjj\.)(?<!\binc\.)(?<!\bco\.)"
    r"(?<!\bcorp\.)(?<!\bst\.)(?<=[.;])\s+",
    re.IGNORECASE,
)

# A docket-number citation — "No. 25-567", "Nos. 19-5094 and 19-5096", "Nos.
# 20-429, 20-454, and 20-539" — and the numbers inside it, every one of a list.
_CITATION_RE = re.compile(
    r"\bnos?\.\s*(\d{2}-\d+(?:\s*(?:,\s*(?:and\s+)?|and\s+|&\s*)\d{2}-\d+)*)",
    re.IGNORECASE,
)
_DOCKET_NUMBER_RE = re.compile(r"\d{2}-\d+")


def _cited_numbers(text: str) -> set[str]:
    """Every docket number ``text`` cites, each of a listed citation included."""
    return {
        number
        for citation in _CITATION_RE.findall(text)
        for number in _DOCKET_NUMBER_RE.findall(citation)
    }


def _own_number(docket_number: str | None) -> str | None:
    """The docket's own number, out of however the caller spells it.

    A capital-case marking or a payload's raw ``CaseNumber`` included.
    """
    own = _DOCKET_NUMBER_RE.search(docket_number or "")
    return own.group(0) if own else None


def _match_clause(entry: str, *, ruling: bool = True) -> Judgment | None:
    """The disposition one stretch of entry text states, specific shapes first.

    ``ruling`` admits the lower-court ruling subject beside the judgment noun;
    an application's own disposition entry reads without it.
    """
    if _EQUALLY_DIVIDED_RE.search(entry):
        return Judgment.equally_divided
    if (_IN_PART_RULING_RE if ruling else _IN_PART_RE).search(entry):
        return Judgment.affirmed_in_part
    if match := (_SINGLE_RULING_RE if ruling else _SINGLE_RE).search(entry):
        return Judgment(match.group(1).lower())
    if _DIG_RE.search(entry):
        return Judgment.dig
    return None


def match_judgment(text: str, *, docket_number: str | None = None) -> Judgment | None:
    """Parse one docket-entry description onto the merits-judgment vocabulary.

    Deterministic and conservative: a shape matches only where a sentence opens
    with the disposition's own subject (the judgment, or the lower-court order
    or determination certiorari ran to), or where the judgment follows the
    grant recital the entry opens on, so recitals and motions return ``None``
    and a shape this parser does not know stays an unparsed gap rather than a
    guess.
    The specific shapes (equally divided, in-part) are checked before the
    general single-verb one, whose first verb would otherwise decide.

    ``docket_number`` is the docket the entry was read from. Where the entry is
    a consolidated judgment that disposes of several dockets clause by clause,
    the docket's own disposition is the one to read, not the entry's first
    verb: the first matching clause that names the docket's own number wins;
    failing that, the first matching clause that names no docket number at all
    (the docket's own disposition is the unlabelled one, its companions'
    the labelled ones); failing both — every clause names some other number,
    which is how a single docket's entry cites the lower court's own case
    numbers — the whole entry is read as one. An entry that cites no docket
    number is read whole from the start, so a disposition split across a
    semicolon ("AFFIRMED IN PART; REVERSED IN PART") keeps its mixed reading.
    Without ``docket_number`` the clause reading still prefers an unlabelled
    clause.

    In an application's own disposition entry ("Application (20A134) granted
    by the Court. ...") the lower-court ruling subject is not read: such an
    entry disposes of interim relief, and its sentences name stays and
    injunctions, not merits rulings. The judgment noun is still read there.
    """
    entry = text.strip()
    ruling = not _APPLICATION_ENTRY_RE.match(entry)
    if not _CITATION_RE.search(entry):
        return _match_clause(entry, ruling=ruling)
    own_number = _own_number(docket_number)
    unlabelled: Judgment | None = None
    for clause in _CLAUSE_BREAK_RE.split(entry):
        judgment = _match_clause(clause, ruling=ruling)
        if judgment is None:
            continue
        cited = _cited_numbers(clause)
        if own_number is not None and own_number in cited:
            return judgment
        if not cited and unlabelled is None:
            unlabelled = judgment
    if unlabelled is not None:
        return unlabelled
    return _match_clause(entry, ruling=ruling)


def match_merits_termination(
    text: str, *, cert_granted: bool, docket_number: str | None = None
) -> MeritsTermination | None:
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

    ``docket_number`` is the docket the entry was read from. An order carried on
    a consolidated docket can name the dockets it dismisses ("the petitions in
    Nos. 20-429, 20-454, and 20-539 are dismissed"), and can dismiss a companion
    while this docket goes on, so a match whose own text cites docket numbers
    ends this docket's proceeding only where its own number is among them. A
    match that cites none, or a call that names no docket, is read as the
    docket's own.
    """
    entry = text.strip()
    own_number = _own_number(docket_number)
    for shape in _TERMINATION_SHAPES:
        if shape.petition_subject and not cert_granted:
            continue
        if any(veto.search(entry) for veto in shape.vetoes):
            continue
        for match in shape.pattern.finditer(entry):
            cited = _cited_numbers(match.group(0))
            if not cited or own_number is None or own_number in cited:
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


# Whether *any* named Justice wrote for the Court — the stored half of the
# authorship question, which the decision record reads to tell a signed opinion
# from a per curiam. Wider than `_AUTHOR_RE` on purpose, because it needs no name:
# the docket also writes "Kagan, J., delivered the opinion for a unanimous
# Court." and, for a fractured Court, "Roberts, C. J., announced the judgment of
# the Court and delivered the opinion of the Court with respect to Parts ..."
# (or "... and delivered an opinion, in which ..." for a plurality). The recital
# anchors on the Justice's own title, so a concurrence or dissent ("Thomas, J.,
# filed a concurring opinion") never reads as the Court's opinion.
_SIGNED_RE = re.compile(
    r"(?:C\.\s*J\.|J\.),\s+(?:announced\s+the\s+judgment\s+of\s+the\s+court\b"
    r"|delivered\s+(?:the|an)\s+opinion\b)",
    re.IGNORECASE,
)

# "Opinion per curiam." — the Court's own notation that the opinion is
# unsigned. "opinion" is required, because a bare "(per curiam)" is how an order
# *cites* some other case's per curiam ("... in light of Clark v. Sweeney, 607
# U. S. 7 (2025) (per curiam)."), which says nothing about how this one was
# decided.
_OPINION_PER_CURIAM_RE = re.compile(r"\bopinion\s+per\s+curiam\b", re.IGNORECASE)


def signed_opinion(text: str) -> bool:
    """Whether the entry recites a named Justice delivering the Court's opinion or judgment."""
    return bool(_SIGNED_RE.search(entry_plain_text(text)))


def per_curiam_opinion(text: str) -> bool:
    """Whether the entry notes its own opinion as per curiam ("Opinion per curiam.")."""
    return bool(_OPINION_PER_CURIAM_RE.search(entry_plain_text(text)))


def opinion_author(text: str) -> str | None:
    """Best-effort: who delivered the opinion of the Court, from the entry text.

    Returns the roster's spelling of the Justice's surname ("Gorsuch",
    "Van Devanter" — however the entry cased it),
    :data:`PER_CURIAM` when the entry marks a per curiam opinion instead, and
    ``None`` when neither is present. The captured window is resolved to its
    **longest suffix that is a known surname**
    (:func:`~fedcourtsai.pipeline.justices.resolve_surname`, case-blind), so a
    compound surname survives whole while a joining word swept into the window
    is dropped; an entirely unrecognized spelling yields the window's final
    token as printed, reading as an unknown-but-name-shaped author rather than
    as absent. This is what lets the surname spelling here be the
    normalization target every vote surface shares (the SCDB entry in
    ``docs/data-sources.md``). Advisory only: nothing stored or scored reads
    it.

    Reads the entry's plain text (:func:`entry_plain_text`), so the live
    docket's linked spelling parses the same as the bare one.
    """
    text = entry_plain_text(text)
    if match := _AUTHOR_RE.search(text):
        tokens = match.group(1).split()
        for start in range(len(tokens)):
            if resolved := resolve_surname(" ".join(tokens[start:])):
                return resolved
        return tokens[-1]
    if _PER_CURIAM_RE.search(text):
        return PER_CURIAM
    return None


class JudgmentEntry(NamedTuple):
    """The last judgment-shaped entry of a docket: what it says, when, and its text."""

    judgment: Judgment
    decided: date | None
    text: str


def _payload_docket_number(payload: Mapping[str, Any]) -> str | None:
    """The docket number a stored payload carries for itself, in either shape."""
    # `or`, not a key test: an empty or null number is no number, and reading it
    # as one would scope a consolidated entry to nothing.
    raw = payload.get("CaseNumber") or payload.get("docket_number")
    return str(raw) if raw else None


def last_judgment_entry_text(
    payload: Mapping[str, Any], *, docket_number: str | None = None
) -> JudgmentEntry | None:
    """:func:`last_judgment_entry`, keeping the entry's own text beside the parse.

    The decision record reads *how* the case was decided (a signed opinion, a
    per curiam) off the same entry the judgment was parsed from, so it takes the
    text from here rather than re-scanning for it. ``docket_number`` is as
    :func:`last_judgment_entry` takes it.
    """
    own = docket_number or _payload_docket_number(payload)
    found: JudgmentEntry | None = None
    for text, raw in proceedings_entries(payload):
        judgment = match_judgment(text, docket_number=own)
        if judgment is not None:
            found = JudgmentEntry(judgment, entry_date(raw), text)
    return found


def last_judgment_entry(
    payload: Mapping[str, Any], *, docket_number: str | None = None
) -> tuple[Judgment, date | None] | None:
    """The last judgment-shaped entry in a stored docket payload, with its date.

    Reads either payload shape through
    :func:`fedcourtsai.pipeline.cert_signals.proceedings_entries`. The **last**
    match wins: a granted-rehearing or amended-judgment docket restates the
    disposition, and the docket's final word is the realized one. The date is
    the entry's own docket date under the strict
    :func:`~fedcourtsai.pipeline.cert_signals.entry_date` parse — ``None`` for
    an undated or partially dated entry, never a guess.

    ``docket_number`` names the docket the payload belongs to, so a consolidated
    judgment entry is read for this docket's own clause
    (:func:`match_judgment`). Omitted, it is the number the payload carries for
    itself (the live ``CaseNumber``, the REST ``docket_number``); a payload
    carrying neither reads without one.
    """
    found = last_judgment_entry_text(payload, docket_number=docket_number)
    return None if found is None else (found.judgment, found.decided)


def last_merits_termination(
    payload: Mapping[str, Any], *, cert_granted: bool, docket_number: str | None = None
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
    one payload is read under the same value. ``docket_number`` is as
    :func:`last_judgment_entry` takes it, defaulting the same way.
    """
    own = docket_number or _payload_docket_number(payload)
    found: MeritsTermination | None = None
    for text, _ in proceedings_entries(payload):
        termination = match_merits_termination(text, cert_granted=cert_granted, docket_number=own)
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
    terminated_events_closed: int = Field(
        default=0,
        ge=0,
        description="Open merits-stage events on rows that ended with nothing "
        "decided (every termination but `judgment-issued`) that the pass "
        "closed (apply) or would close (dry-run) without an outcome, marked "
        "`resolved_without_outcome` with the reason `merits-terminated`: the "
        "proceeding ended with nothing decided, so there is no outcome to record",
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


def _closed_by_termination(
    conn: sqlite3.Connection, case_id: str, termination: MeritsTermination
) -> list[tuple[str, str]]:
    """The open merits events a termination closes without an outcome, as ``(case, event)``.

    None for the bare mandate notation: that docket was decided and the parser
    missed the entry, so its events wait for the parse.
    """
    if termination is MeritsTermination.judgment_issued:
        return []
    return [
        (case_id, event.event_id)
        for event in corpus.events_for_case(conn, case_id)
        if event.stage == Stage.merits and not event.resolved
    ]


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
    pendency without asserting a disposition it does not have. The reverse
    holds too: a row carrying a termination whose snapshot now parses a
    judgment is written, and the write clears the termination, because a read
    disposition supersedes the no-disposition record. Every open merits-stage
    event on a row that ended with nothing decided (a termination other than
    ``judgment-issued``) is closed without an outcome, marked
    ``resolved_without_outcome`` with the reason ``merits-terminated``, so it
    stops reading as pending: nothing would ever resolve it. A
    ``judgment-issued`` row is left open, because the docket was decided and
    the parser missed the entry, so its events wait for the parse. Should a judgment
    later parse on the row, the outcome convergence records it over the mark
    (:func:`fedcourtsai.pipeline.outcome.converge_ledger_outcomes`). A stored
    judgment the pass can no longer re-derive is never cleared but is counted
    (``stale``), so a parser tightening that retracts a reading stays visible
    instead of silently persisting in the statpack. Dry-run unless ``apply``.
    """
    no_snapshot = no_match = parsed = unchanged = stale = terminated = 0
    judgments: Counter[str] = Counter()
    terminations_found: Counter[str] = Counter()
    updates: list[tuple[str, Judgment, date | None]] = []
    terminations: list[tuple[str, MeritsTermination]] = []
    closing: list[tuple[str, str]] = []
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
            entry = last_judgment_entry(found[1], docket_number=row.docket_number)
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
                    found[1],
                    cert_granted=row.date_cert_granted is not None,
                    docket_number=row.docket_number,
                )
                if termination is None:
                    no_match += 1
                    continue
                terminated += 1
                terminations_found[termination.value] += 1
                if row.merits_terminated != termination.value:
                    terminations.append((row.case_id, termination))
                closing.extend(_closed_by_termination(conn, row.case_id, termination))
                continue
            judgment, decided = entry
            parsed += 1
            judgments[judgment.value] += 1
            if (
                row.merits_judgment == judgment.value
                and row.merits_decided == decided
                and row.merits_terminated is None
            ):
                unchanged += 1
                continue
            updates.append((row.case_id, judgment, decided))
    if apply:
        for case_id, judgment, decided in updates:
            corpus.set_merits_judgment(conn, case_id, judgment, decided)
        for case_id, termination in terminations:
            corpus.set_merits_termination(conn, case_id, termination)
        for case_id, event_id in closing:
            corpus.mark_resolved_without_outcome(
                conn, case_id, event_id, corpus.NO_OUTCOME_MERITS_TERMINATED
            )
    return MeritsBackfillResult(
        applied=apply,
        eligible=eligible,
        no_snapshot=no_snapshot,
        no_match=no_match,
        terminated=terminated,
        terminations_written=len(terminations),
        terminated_events_closed=len(closing),
        stale=stale,
        parsed=parsed,
        unchanged=unchanged,
        updated=len(updates),
        judgments=dict(sorted(judgments.items())),
        terminations=dict(sorted(terminations_found.items())),
    )
