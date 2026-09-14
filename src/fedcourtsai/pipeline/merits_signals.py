"""Reading the merits docket: how far a granted case has been briefed.

Between the cert grant and the judgment a granted case does most of its visible
work, and the docket records it. This module reads the parties' briefs on the
merits: **which** entry is each side's brief, which is how the document selector
fetches them, and **when** the respondent filed — the one milestone the pipeline
forecasts from, which is the point at which both sides' arguments are on the
record and the case is substantively ready to be decided.

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
is a leaf module — it reads entry text and returns dates — so no consumer can
form an import cycle around it.
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
# The **reply** is deliberately outside both: the Court files it as "Reply of
# <party> filed." or "Reply Brief of <party> filed.", an entry family the
# start anchor never reaches. It is a separate document, not a variant of these.
_RESPONDENT_BRIEF_RE = re.compile(
    r"^\s*brief\s+of\s+(?:the\s+)?(?:\S+\s+){0,3}?respondents?\b", re.I
)
_PETITIONER_BRIEF_RE = re.compile(
    r"^\s*brief\s+of\s+(?:the\s+)?(?:\S+\s+){0,3}?petitioners?\b", re.I
)

# Three exclusions, each removing a filing that matches the anchor but is not
# the adversarial merits brief:
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
#   mirror is stated so one side is not read more loosely than the other.
_NOT_THE_RESPONDENT_MERITS_BRIEF_RE = re.compile(
    r"\bin\s+opposition\b"
    r"|\bamicus\b|\bamici\b"
    r"|\b(?:in\s+support\s+of|supporting)\s+(?:the\s+)?petitioners?\b",
    re.I,
)
_NOT_THE_PETITIONER_MERITS_BRIEF_RE = re.compile(
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
    ) and not _NOT_THE_RESPONDENT_MERITS_BRIEF_RE.search(text)


def is_petitioner_merits_brief(text: str) -> bool:
    """Whether an entry reads as the petitioner's brief on the merits.

    The mirror of :func:`is_respondent_merits_brief`, and the same contract: text
    alone, with the post-grant bound owed by the caller. Nothing dates a
    petitioner-side moment — the milestone this module forecasts from is the
    respondent's — so this exists for the document selector, which needs to know
    *which entry* the brief is rather than when it arrived.
    """
    return bool(
        _PETITIONER_BRIEF_RE.search(text)
    ) and not _NOT_THE_PETITIONER_MERITS_BRIEF_RE.search(text)


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
