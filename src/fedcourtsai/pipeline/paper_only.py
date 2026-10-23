"""Whether a SCOTUS docket's party filings are on paper only (Rule 34.6).

The Court puts a docket under Rule 34.6 and Paragraph 9 of its electronic filing
guidelines (a case that was sealed or privacy-restricted below, most often
immigration or detention) with an entry saying filings are to be submitted in
paper form only. Nothing is posted behind them, so the document selector finds
no link and a cell gets no ``documents/`` for a reason no repair reaches. Once
the Court schedules briefing and argument, a second entry quoting the rule calls
for electronic versions, and filings are posted again from then on.

A leaf over the payload, like :mod:`.vide_links`, so the cell-context builder
reads it without importing the fetcher.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

# "Pursuant to Rule 34.6 and Paragraph 9 of the Guidelines for the Submission of
# Documents to the Supreme Court's Electronic Filing System, filings in this case
# should be submitted in paper form only ...". Anchored at the entry's start,
# since the rule is also quoted mid-sentence by the entry that lifts it.
_PAPER_ONLY_ENTRY_RE = re.compile(
    r"^\s*pursuant\s+to\s+rule\s+34\.6\s+and\s+paragraph\s+9\b", re.IGNORECASE
)
# "As Rule 34.6 provides, 'If the Court schedules briefing and oral argument in a
# case ... the parties shall submit electronic versions of all prior and
# subsequent filings ...'".
_PAPER_ONLY_LIFTED_RE = re.compile(
    r"^\s*as\s+rule\s+34\.6\s+provides\b.*\belectronic\s+versions\b",
    re.IGNORECASE | re.DOTALL,
)


def paper_only_filings(payload: Mapping[str, Any]) -> bool | None:
    """Whether the payload puts the docket's party filings on paper only.

    ``True`` where the payload carries the paper-only entry and no later entry
    lifting it; ``False`` where its entries carry neither, or the lift follows;
    ``None`` where the payload carries no live ``ProceedingsandOrder`` list —
    the REST shape, or a payload whose cut removed the key because no moment
    could be placed — which says nothing either way. An empty list reads
    ``False``: a real cut keeps the list even when nothing survives it, as an
    observation that the docket had no entries yet
    (:func:`fedcourtsai.provision.truncate_snapshot`). Read in docket order over
    the payload as handed in, so a truncated payload answers as at its cut.
    """
    entries = payload.get("ProceedingsandOrder")
    if not isinstance(entries, list):
        return None
    paper_only = False
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        text = str(entry.get("Text") or "")
        if _PAPER_ONLY_ENTRY_RE.search(text):
            paper_only = True
        elif _PAPER_ONLY_LIFTED_RE.search(text):
            paper_only = False
    return paper_only
