"""Cert-disposition signal patterns over docket-entry / proceedings text.

The one deterministic instrument that reads a concrete cert disposition out of
free order-list language ("Petition DENIED.", "GVR'd", "certiorari granted"),
shared by every consumer that needs it — the live channel's ingest-time
resolution (:mod:`.ingest`), the historical loader (:mod:`.historical`), and
the live reachability probe (:mod:`.liveprobe`).
A leaf module on purpose: it depends only on the shared schema, so the
consumers can never form an import cycle around it.

Because a match here *records ground truth* (disposition + decision date), the
patterns trade recall for precision: a shape that could also appear in a
pending-docket entry — a motion order reciting the petition as its object, a
party paper suggesting a vacatur — must not match. A deliberate miss falls to
the high-recall routing backstop
(:func:`fedcourtsai.pipeline.outcome.termination_signal`) for the shapes it
carries (Rule 39.8 IFP dismissals, cert-before-judgment denials), where a
false positive only parks a case for triage; anything neither instrument reads
(a bare CBJ grant set for argument) is an accepted residual, surfaced by
re-running the reachability probe (``fedcourts probe-live-terms``) — do that
after any pattern change to re-establish the recall claim over the live
sample.
"""

from __future__ import annotations

import re

from ..schemas import Disposition

# Docket-entry text patterns that signal a concrete cert disposition. Each maps the
# matched phrase to a :class:`Disposition` and a short human label; the first match
# (scanned in order) wins, so the more specific GVR patterns precede bare "granted".
_ENTRY_SIGNALS: tuple[tuple[re.Pattern[str], Disposition, str], ...] = (
    # Grant/vacate/remand: the petition is granted, so it lands on the granted side.
    (re.compile(r"\bgvr\b", re.IGNORECASE), Disposition.granted, "GVR"),
    (
        re.compile(r"grant\w*.{0,60}?vacat\w*.{0,60}?remand\w*", re.IGNORECASE | re.DOTALL),
        Disposition.granted,
        "GVR",
    ),
    # The bare vacate-and-remand order — no "grant" word at all. Two forms carry
    # it: the cert-track GVR whose order-list entry skips the grant recital, and
    # the mandatory-jurisdiction direct appeal ("Judgment VACATED and case
    # REMANDED for further consideration in light of ..."), which by convention
    # lands on the granted side like every GVR. Anchored to the *start of the
    # entry* — a disposition entry opens with its judgment ("Judgment VACATED
    # ...", "The judgment of the ... Circuit is vacated, and the case is
    # remanded ...") — so a party paper *reciting* a vacatur ("Brief of
    # respondent suggesting that the judgment be vacated and the case remanded
    # filed."), the SG's confession-of-error motion, and an en banc
    # panel-opinion vacatur never read as a disposition. The first gap is wide
    # enough for the prose form to name the lower court between "judgment" and
    # "vacated".
    (
        re.compile(
            r"^(?:the\s+)?judgment\b.{0,80}?\bvacated\b.{0,80}?\bremand\w*",
            re.IGNORECASE | re.DOTALL,
        ),
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
