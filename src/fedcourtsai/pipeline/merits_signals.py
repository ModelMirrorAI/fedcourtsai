"""Reading the merits docket: how far a granted case has been briefed.

Between the cert grant and the judgment a granted case does most of its visible
work, and the docket records it. This module reads the parties' merits filings:
**which** entry is each side's opening brief and each side's reply, which is how
the document selector fetches them, and **when** the respondent filed its brief
— the one milestone the pipeline forecasts from, which is the point at which
both sides' arguments are on the record and the case is substantively ready to
be decided.

**Why that milestone and not another.** Measured over 139 granted OT2021-OT2023
petitions, the respondent's merits brief appears on **96.4%** of them, lands a
median **84 days** after the grant, and precedes the judgment by a median
**159 days** — never fewer than 44, and never on or after it. So a forecast
taken here is both well-covered and genuinely prospective, which is more than
can be said for most later docket signals: argument and circulation cluster
much closer to the decision.

**The stage is a date, never a word.** The Court writes a merits brief and a
cert-stage response in the same words — "Brief of respondent United States
filed." either way — and "on the merits" appears on the *scheduling* order, not
on the brief entry. So every predicate here reads the text alone and leaves the
post-grant bound to its caller, which is the stronger half of the reading.

The cert-stage analogue is :mod:`fedcourtsai.pipeline.cert_signals`, the interim
one :mod:`fedcourtsai.pipeline.interim_signals`; this is the merits sibling. It
also dates the argument (:func:`argued_date`), which the merits decision record
carries. It is a leaf module — it reads entry text and returns dates — so no
consumer can form an import cycle around it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from typing import Any

from .cert_signals import entry_date, proceedings_entries

# Each side's brief ON THE MERITS. Start-anchored, because the anchor is what
# separates it from the many other filings that mention a party: a motion, a
# blanket consent, a divided-argument request, and — the one that would
# otherwise swamp the merits stage — an amicus brief, which opens "Brief amicus
# curiae of ..." and so fails the anchor before any exclusion is consulted. Up
# to three words may sit between "of" and the party, because the Court writes
# "Brief of State respondents filed" and "Brief of NAACP respondents filed"
# where a case has several respondent groups, and requiring the bare noun drops
# those. The petitioner form is the mirror of it, and takes the same shapes:
# "Brief of petitioner Floyd Johnson filed.", "Brief of petitioners Department
# of Labor, et al. filed.", with the docket's ordinary tails ("VIDED.",
# "(Distributed)", "(as to 24-656)") riding after the verb.
#
# The **reply** is outside both anchors and has its own pair below: the Court
# files it as "Reply of <party> filed." or "Reply Brief of <party> filed.", an
# entry family the opening anchor never reaches. It is a separate document, not
# a variant of these.
_RESPONDENT_BRIEF_RE = re.compile(
    r"^\s*brief\s+of\s+(?:the\s+)?(?:\S+\s+){0,3}?respondents?\b", re.I
)

# The **document selector's** opening, which reads two spellings the moment's
# anchor above does not: "Brief **for** the petitioner filed." — the Court's own
# title form, naming no party — and a leading **"Redacted"**, the public copy of
# a brief filed under seal ("Redacted brief of petitioner Jane Roe filed.").
# Still start-anchored, and that is what keeps a filing *about* a brief out: "Motion
# to file petitioner's brief on the merits under seal with redacted copies" and
# "Motion for an extension of time to file the briefs on the merits" open on
# "Motion", so neither reaches "brief" at the start of the entry.
#
# The petitioner arm takes it outright, because nothing dates a moment off the
# petitioner's brief. The respondent arm takes it only through the selector's
# predicate (:func:`is_respondent_merits_brief_document`), and the moment's
# reading (:func:`is_respondent_merits_brief`, behind
# :func:`respondent_brief_date`) reads the narrower anchor above, because that
# reading dates the registered briefed moment, and moving that moment is a
# different change from giving a cell a document it can read.
_BRIEF_DOCUMENT_OPENING = r"^\s*(?:redacted\s+)?brief\s+(?:of|for)\s+(?:the\s+)?(?:\S+\s+){0,3}?"
_RESPONDENT_BRIEF_DOCUMENT_RE = re.compile(_BRIEF_DOCUMENT_OPENING + r"respondents?\b", re.I)
_PETITIONER_BRIEF_RE = re.compile(_BRIEF_DOCUMENT_OPENING + r"petitioners?\b", re.I)

# Each side's REPLY on the merits — the last word on the argument, and the one
# filing that answers the other side's brief directly. The mirror of the pair
# above in every respect but the opening word, and it takes the same party
# shapes: "Reply of petitioner Michael Nance filed.", "Reply of petitioners
# Enbridge Energy, Limited Partnership, et al. filed.", "Reply of Federal
# Petitioners filed. VIDED.", "Reply Brief of petitioner Acme Corp. filed.", and
# — where the true adversary is a Court-appointed amicus or the posture is a
# cross-petition — "Reply of respondent New Jersey Transit Corporation filed."
# The optional "Brief" is what lets one anchor read both spellings.
#
# The **stage** is a date here exactly as it is above, and the trap is sharper:
# a cert-stage reply to the brief in opposition is spelled "Reply of petitioner
# X filed." word for word, and it is a routine filing rather than a rarity. The
# post-grant bound its callers apply is the only thing separating the two, which
# is why these predicates are text-only like their siblings.
#
# One reply shape the anchor refuses on its own: a reply the Clerk records under
# counsel's own name rather than a party's ("Reply of AT&T, Inc. and Verizon
# Communications Inc. filed."), which no party-word anchor can reach and which is
# left unfetched rather than guessed at.
#
# The reply takes the same two widenings as the opening briefs — "Reply brief
# for the petitioner filed." and a leading "Redacted" — so a side's last word is
# read on the terms its opening brief is. Nothing dates a moment off a reply.
_REPLY_OPENING = (
    r"^\s*(?:redacted\s+)?reply\s+(?:brief\s+)?(?:of|for)\s+(?:the\s+)?(?:\S+\s+){0,3}?"
)
_RESPONDENT_REPLY_RE = re.compile(_REPLY_OPENING + r"respondents?\b", re.I)
_PETITIONER_REPLY_RE = re.compile(_REPLY_OPENING + r"petitioners?\b", re.I)

# Collateral **motion** practice, which the reply family reaches and the opening
# briefs do not. The unpartied form falls outside the anchor already ("Reply on
# motion to intervene filed.", "Reply in support of motion of Missouri, et al. to
# intervene filed." — neither names a party right after "of"), but the partied
# one does not: "Reply of petitioners in support of motion for divided argument
# filed." satisfies the anchor word for word.
#
# Excluding it matters more than the filing is worth, because each arm takes the
# **first** qualifying entry in docket order and then closes: a motion reply
# filed between the grant and the briefs would occupy the side's slot and put its
# real merits reply permanently out of reach. A procedural paper stored as merits
# advocacy is the smaller of the two costs.
#
# Reply-only, rather than folded into the three exclusions below: the opening
# brief anchors have no such exposure — the Clerk writes no "Brief of <party> in
# support of motion" form — and widening a predicate that dates a registered
# moment to fix a reply-side shape would move a reading nothing here needs moved.
# "in support of reversal" and "in support of vacatur" are deliberately not here:
# those are genuine merits replies in the confession-of-error posture.
_NOT_A_MERITS_REPLY_RE = re.compile(
    r"\bin\s+support\s+of\s+(?:the\s+)?(?:motion|application)\b", re.I
)

# Three exclusions, each removing a filing that matches one of the anchors above
# but is not that side's adversarial merits filing. They gate the reply arms as
# well as the brief arms, because every one of the three has a reply form:
#
# - **in opposition** is the *cert*-stage brief in opposition, which shares the
#   shape exactly. The post-grant date restriction the callers apply already
#   excludes it, and this is the belt to those braces: a supplemental BIO, or an
#   opposition to a rehearing petition, can be filed after the grant.
# - **amicus / amici** is a friend of the court supporting the party, not the
#   party. The anchor already refuses the ordinary "Brief amicus curiae of ..."
#   spelling; this catches the one that opens "Brief of amici curiae ...".
# - **in support of the other side** is a party siding *with* its opponent — a
#   real merits brief, but not an adversarial one. The moment
#   :func:`respondent_brief_date` exists to name is the one where the opposing
#   argument is on the record, and a respondent supporting the petitioner leaves
#   that still to come (sometimes from a Court-appointed amicus); the petitioner
#   mirror is stated so one side is not read more loosely than the other. The
#   reply form is on the docket too ("Reply of respondent United States in
#   support of petitioner filed."), and it is excluded on the same reading and
#   at the same cost: that filing is real advocacy no arm here fetches.
_NOT_THE_RESPONDENT_MERITS_FILING_RE = re.compile(
    r"\bin\s+opposition\b"
    r"|\bamicus\b|\bamici\b"
    r"|\b(?:in\s+support\s+of|supporting)\s+(?:the\s+)?petitioners?\b",
    re.I,
)
_NOT_THE_PETITIONER_MERITS_FILING_RE = re.compile(
    r"\bin\s+opposition\b"
    r"|\bamicus\b|\bamici\b"
    r"|\b(?:in\s+support\s+of|supporting)\s+(?:the\s+)?respondents?\b",
    re.I,
)


def is_respondent_merits_brief(text: str) -> bool:
    """Whether an entry reads as the respondent's brief on the merits.

    The **text** half of the reading only: a cert-stage brief in opposition
    shares this shape word for word, so a caller that does not also bound the
    entry to after the grant will read the cert stage as the merits one. Both
    callers do — :func:`respondent_brief_date` scans post-grant entries, and the
    document selector keys its ``merits-brief-respondent`` arm on the same bound.
    """
    return bool(
        _RESPONDENT_BRIEF_RE.search(text)
    ) and not _NOT_THE_RESPONDENT_MERITS_FILING_RE.search(text)


def is_respondent_merits_brief_document(text: str) -> bool:
    """Whether an entry is the respondent's brief on the merits, as the selector reads it.

    :func:`is_respondent_merits_brief` plus the two spellings the selector's
    opening reads (:data:`_BRIEF_DOCUMENT_OPENING`): "Brief for the
    respondent(s) …" and a leading "Redacted". Kept apart from that predicate
    because that one dates the registered briefed moment
    (:func:`respondent_brief_date`), and which document a cell is given is a
    different question from when its moment opens. Same exclusions, same
    contract: text alone, the post-grant bound owed by the caller.
    """
    return bool(
        _RESPONDENT_BRIEF_DOCUMENT_RE.search(text)
    ) and not _NOT_THE_RESPONDENT_MERITS_FILING_RE.search(text)


def is_petitioner_merits_brief(text: str) -> bool:
    """Whether an entry reads as the petitioner's brief on the merits.

    The mirror of :func:`is_respondent_merits_brief_document`, and the same
    contract: text alone, with the post-grant bound owed by the caller. Nothing
    dates a petitioner-side moment — the milestone this module forecasts from is
    the respondent's — so this exists for the document selector, which needs to
    know *which entry* the brief is rather than when it arrived, and it reads the
    selector's wider opening ("Brief for the petitioner filed.", "Redacted brief
    of petitioner … filed.") directly.
    """
    return bool(
        _PETITIONER_BRIEF_RE.search(text)
    ) and not _NOT_THE_PETITIONER_MERITS_FILING_RE.search(text)


def is_petitioner_merits_reply(text: str) -> bool:
    """Whether an entry reads as the petitioner's reply brief on the merits.

    The ordinary reply: under Rule 25.3 it is the petitioner who answers the
    respondent's brief, so this is the side the family is usually seen on.

    Text alone, with the post-grant bound owed by the caller, and here that bound
    carries more weight than anywhere else in this module: the *cert*-stage reply
    to a brief in opposition is spelled identically and is a routine filing, so
    an unbounded caller would read a reply to the BIO as merits advocacy across a
    large part of the docket stock. The document selector keys its
    ``merits-reply-petitioner`` arm on the same post-grant bound its brief arms
    use. Nothing dates a moment from a reply — this exists for the selector,
    which needs to know *which entry* the filing is rather than when it arrived.
    """
    return (
        bool(_PETITIONER_REPLY_RE.search(text))
        and not _NOT_THE_PETITIONER_MERITS_FILING_RE.search(text)
        and not _NOT_A_MERITS_REPLY_RE.search(text)
    )


def is_respondent_merits_reply(text: str) -> bool:
    """Whether an entry reads as the respondent's reply brief on the merits.

    The mirror of :func:`is_petitioner_merits_reply`, and the rarer side: a
    respondent replies where the posture gives it the last word — cross-petitions
    and the cases the Court appoints an amicus to defend the judgment in. Read
    on the same terms rather than left out, so neither side's reply is reached
    more loosely than the other's.
    """
    return (
        bool(_RESPONDENT_REPLY_RE.search(text))
        and not _NOT_THE_RESPONDENT_MERITS_FILING_RE.search(text)
        and not _NOT_A_MERITS_REPLY_RE.search(text)
    )


def respondent_brief_date(payload: Mapping[str, Any], *, granted_on: date | None) -> date | None:
    """When the respondent filed its brief on the merits, or ``None``.

    ``granted_on`` bounds the scan to entries **after** the cert grant, which is
    the strongest of the filters: it is what keeps the cert-stage brief in
    opposition — same shape, same words — out of a merits signal. Without a
    grant date there is no merits proceeding to be briefed, so the answer is
    ``None`` rather than a scan of the whole docket.

    The **first** qualifying brief wins. A case with several respondent groups
    files several, and the moment being named is when the opposing argument
    first reaches the record, not when the last group finishes.

    An undated entry is skipped rather than guessed at, matching the discipline
    every other dated read in the pipeline applies: this date opens an event and
    fixes the moment a forecast is taken from, so an approximate one would put a
    cell at a moment the docket never had.
    """
    if granted_on is None:
        return None
    for text, raw in proceedings_entries(payload):
        if not is_respondent_merits_brief(text):
            continue
        filed = entry_date(raw)
        if filed is not None and filed > granted_on:
            return filed
    return None


# The Clerk's record of an oral argument: "Argued. For petitioner: ... For
# respondent: ...", and "Reargued. ..." where the Court set the case for a
# second argument. Start-anchored on the verb, because the anchor is what keeps
# out every entry that merely talks about argument: the scheduling notice ("SET
# FOR ARGUMENT on Monday, October 6, 2025."), the invitation to an appointed
# amicus ("... is invited to brief and argue this case ..."), a motion for
# divided argument, and the argument calendar's own "CIRCULATED". A doubled verb
# ("Argued. Argued. For ...") is a Clerk's slip and still opens on the verb.
_ARGUED_RE = re.compile(r"^\s*(?:re)?argued\b", re.I)


def is_argument_entry(text: str) -> bool:
    """Whether an entry records the case being argued (or reargued)."""
    return bool(_ARGUED_RE.search(text))


def argued_date(payload: Mapping[str, Any], *, granted_on: date | None) -> date | None:
    """When the granted case was last argued, or ``None``.

    The **last** argument entry wins, unlike the first-brief rule above: a case
    the Court set for reargument is decided on the reargument, so the date the
    decision record wants — and a post-argument forecast moment would — is the
    later one.
    ``granted_on`` bounds the scan to entries on or after the grant, and
    without one there is no merits proceeding to argue, so the answer is
    ``None`` — the same post-grant contract as :func:`respondent_brief_date`.
    "On or after" rather than strictly after, because nothing at the cert stage
    shares the shape and an expedited grant can be argued days later. An undated
    entry is skipped rather than guessed at.
    """
    if granted_on is None:
        return None
    found: date | None = None
    for text, raw in proceedings_entries(payload):
        if not is_argument_entry(text):
            continue
        argued = entry_date(raw)
        if argued is not None and argued >= granted_on:
            found = argued
    return found
