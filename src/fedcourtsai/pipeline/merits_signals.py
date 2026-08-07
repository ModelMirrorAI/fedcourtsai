"""Reading the merits docket: how far a granted case has been briefed.

Between the cert grant and the judgment a granted case does most of its visible
work, and the docket records it. This module reads the one milestone the
pipeline forecasts from — the respondent's brief on the merits — which is the
point at which both sides' arguments are on the record and the case is
substantively ready to be decided.

**Why this milestone and not another.** Measured over 139 granted OT2021-OT2023
petitions, the respondent's merits brief appears on **96.4%** of them, lands a
median **84 days** after the grant, and precedes the judgment by a median
**159 days** — never fewer than 44, and never on or after it. So a forecast
taken here is both well-covered and genuinely prospective, which is more than
can be said for most later docket signals: argument and circulation cluster
much closer to the decision.

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

# The respondent's brief ON THE MERITS. Start-anchored, because the anchor is
# what separates it from the many other filings that mention a respondent: a
# motion, a blanket consent, a divided-argument request. Up to three words may
# sit between "of" and "respondent" — the Court writes "Brief of State
# respondents filed" and "Brief of NAACP respondents filed" where a case has
# several respondent groups, and requiring the bare noun drops those.
_RESPONDENT_BRIEF_RE = re.compile(
    r"^\s*brief\s+of\s+(?:the\s+)?(?:\S+\s+){0,3}?respondents?\b", re.I
)

# Three exclusions, each removing a filing that matches the anchor but is not
# the adversarial merits brief:
#
# - **in opposition** is the *cert*-stage brief in opposition, which shares the
#   shape exactly. The post-grant date restriction below already excludes it,
#   and this is the belt to that braces: a supplemental BIO, or an opposition to
#   a rehearing petition, can be filed after the grant.
# - **amicus / amici** is a friend of the court supporting the respondent, not
#   the respondent.
# - **in support of petitioner** is a respondent siding *with* the petitioner —
#   a real merits brief, but not an adversarial one. The moment this module
#   exists to name is the one where the opposing argument is on the record, and
#   a respondent supporting the petitioner leaves that still to come (sometimes
#   from a Court-appointed amicus).
_NOT_THE_MERITS_BRIEF_RE = re.compile(
    r"\bin\s+opposition\b"
    r"|\bamicus\b|\bamici\b"
    r"|\b(?:in\s+support\s+of|supporting)\s+(?:the\s+)?petitioners?\b",
    re.I,
)


def respondent_brief_date(payload: Mapping[str, Any], *, granted_on: date | None) -> date | None:
    """When the respondent filed its brief on the merits, or ``None``.

    ``granted_on`` bounds the scan to entries **after** the cert grant, which is
    the strongest of the three filters: it is what keeps the cert-stage brief in
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
        if not _RESPONDENT_BRIEF_RE.search(text) or _NOT_THE_MERITS_BRIEF_RE.search(text):
            continue
        filed = entry_date(raw)
        if filed is not None and filed > granted_on:
            return filed
    return None
