"""Cert-disposition signal patterns over docket-entry / proceedings text.

The one deterministic instrument that reads a concrete cert disposition out of
free order-list language ("Petition DENIED.", "GVR'd", "certiorari granted"),
shared by every consumer that needs it — the recoverability probe
(:mod:`.recoverability`), the live channel's ingest-time resolution
(:mod:`.ingest`), and the live reachability probe (:mod:`.liveprobe`).
A leaf module on purpose: it depends only on the shared schema, so the
consumers can never form an import cycle around it.
"""

from __future__ import annotations

import re

from ..schemas import Disposition

# Docket-entry text patterns that signal a concrete cert disposition. Each maps the
# matched phrase to a :class:`Disposition` and a short human label; the first match
# (scanned in order) wins, so the more specific GVR pattern precedes bare "granted".
_ENTRY_SIGNALS: tuple[tuple[re.Pattern[str], Disposition, str], ...] = (
    # Grant/vacate/remand: the petition is granted, so it lands on the granted side.
    (re.compile(r"\bgvr\b", re.IGNORECASE), Disposition.granted, "GVR"),
    (
        re.compile(r"grant\w*.{0,60}?vacat\w*.{0,60}?remand\w*", re.IGNORECASE | re.DOTALL),
        Disposition.granted,
        "GVR",
    ),
    (
        re.compile(r"(?:writ of certiorari|cert\.?|petition)\s+\w*\s*?denied", re.IGNORECASE),
        Disposition.denied,
        "cert denied",
    ),
    (
        re.compile(r"(?:writ of certiorari|cert\.?|petition)\s+\w*\s*?dismiss\w*", re.IGNORECASE),
        Disposition.dismissed,
        "cert dismissed",
    ),
    (
        re.compile(r"(?:writ of certiorari|cert\.?|petition)\s+\w*\s*?grant\w*", re.IGNORECASE),
        Disposition.granted,
        "cert granted",
    ),
    (re.compile(r"\bcertiorari denied\b", re.IGNORECASE), Disposition.denied, "cert denied"),
    (re.compile(r"\bcertiorari granted\b", re.IGNORECASE), Disposition.granted, "cert granted"),
)

# How much text around a matched signal to surface as evidence.
_SNIPPET_PAD = 40


def match_disposition_signal(text: str) -> tuple[Disposition, str, str] | None:
    """First cert-disposition signal in ``text``, as (disposition, label, snippet).

    ``None`` when no order language matches — the caller's cue that the text
    carries no machine-readable cert disposition.
    """
    for pattern, disposition, label in _ENTRY_SIGNALS:
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - _SNIPPET_PAD)
            end = min(len(text), match.end() + _SNIPPET_PAD)
            snippet = " ".join(text[start:end].split())
            return disposition, label, snippet
    return None
