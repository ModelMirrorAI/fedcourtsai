"""Cert-disposition signal patterns over docket-entry / proceedings text.

The one deterministic instrument that reads a concrete cert disposition out of
free order-list language ("Petition DENIED.", "GVR'd", "certiorari granted"),
shared by every consumer that needs it — the live channel's ingest-time
resolution (:mod:`.ingest`), the historical loader (:mod:`.historical`), the
live reachability probe (:mod:`.liveprobe`), and the forward-provisioning
leakage guard (``provision-snapshot --refuse-terminal``), whose false-positive
cost is the cheapest of the family: one snapshot-less cell, no recorded fact.
A leaf module on purpose: it depends only on the shared schema, so the
consumers can never form an import cycle around it.

Because a match here *records ground truth* (disposition + decision date), the
patterns trade recall for precision: a shape that could also appear in a
pending-docket entry — a motion order reciting the petition as its object, a
party paper suggesting a vacatur — must not match. A deliberate miss falls to
the high-recall routing backstop
(:func:`fedcourtsai.pipeline.outcome.termination_signal`) for the shapes it
carries (Rule 39.8 IFP dismissals, cert-before-judgment grants, denials, and
dismissals, and a SCOTUS merits judgment), where a false positive only parks a
case for triage rather than fabricating ground truth; anything neither
instrument reads is an accepted residual, surfaced by re-running the
reachability probe (``fedcourts probe-live-terms``) — do that after any pattern
change to re-establish the recall claim over the live sample.
"""

from __future__ import annotations

import re

from ..schemas import Disposition

# Docket-entry text patterns that signal a concrete cert disposition. Each maps the
# matched phrase to a :class:`Disposition` and a short human label; the first match
# (scanned in order) wins, so the more specific GVR patterns precede bare "granted".
_ENTRY_SIGNALS: tuple[tuple[re.Pattern[str], Disposition, str], ...] = (
    # Grant/vacate/remand: its own `gvr` disposition (a grant on the binary axis,
    # but distinct from a plain merits cert grant on the label axis).
    (re.compile(r"\bgvr\b", re.IGNORECASE), Disposition.gvr, "GVR"),
    (
        re.compile(r"grant\w*.{0,60}?vacat\w*.{0,60}?remand\w*", re.IGNORECASE | re.DOTALL),
        Disposition.gvr,
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
        Disposition.gvr,
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


# Sentence-level rejections for pending-docket text that carries disposition
# words without deciding anything, derived from a survey of every matched entry
# in the corpus. Two shapes exist in the wild or in the clerk's known repertoire:
#   - a docketing *recital* — the sentence ends in "filed", so any disposition
#     words inside are quoted or conditional, never an order ("Motion of
#     petitioner to expedite consideration of the petition ... in the event the
#     petition is granted filed."); this shape fabricated a real corpus row's
#     grant, with the motion's filing date as the "decision" date;
#   - the order *on an expedite motion* — the sentence opens with a motion word
#     and recites the petition as the object of "consideration of", so the
#     trailing verb grants/denies expedition, not the petition. The guard needs
#     both conditions: a legitimate compound order also opens with a motion
#     word ("The motion to expedite and the petition ... are GRANTED." — a real
#     grant, conjunctive subject) and the Rule 39.8 compound opens with "The
#     motion for leave ..." — neither contains "consideration of".
_FILED_RECITAL_RE = re.compile(r"\bfiled\s*\.?\s*$", re.IGNORECASE)
_MOTION_OPEN_RE = re.compile(r"^\s*(?:the\s+)?(?:motion|application)\b", re.IGNORECASE)
_CONSIDERATION_RE = re.compile(r"\bconsideration of\b", re.IGNORECASE)
# Candidate sentence boundaries; a semicolon counts so a trailing "...filed"
# clause never swallows the genuine order before it ("Petition GRANTED;
# statement of Justice Alito filed.").
_SENTENCE_END_RE = re.compile(r"(?<=[.!?;])\s+")
# A period that ends one of these is a citation/abbreviation, not a sentence —
# "No. 25-332", "ECF Doc. 52", "Trump v. Anderson", "U. S.", "Acme Inc." A
# false boundary here would strip the guard's anchors (a fragment losing its
# motion-word opening, or a recital losing its terminal "filed"), so the
# splitter must merge through them; merging is strictly safe for the guards.
_ABBREVIATION_TAIL_RE = re.compile(r"(?:\bNos?|\bv|\bvs|\bInc|\bCorp|\bDoc|\b[A-Z])\.$")


def _sentence_boundaries(text: str) -> list[int]:
    """Start offsets of each sentence in ``text``, abbreviation-aware."""
    starts = [0]
    for boundary in _SENTENCE_END_RE.finditer(text):
        if _ABBREVIATION_TAIL_RE.search(text, 0, boundary.start()):
            continue
        starts.append(boundary.end())
    return starts


def _containing_sentence(text: str, position: int) -> str:
    """The sentence of ``text`` that contains character ``position``."""
    starts = _sentence_boundaries(text)
    start = max(s for s in starts if s <= position)
    later = [s for s in starts if s > position]
    return text[start : later[0] if later else len(text)]


def _is_non_order_sentence(sentence: str) -> bool:
    """Whether disposition words in this sentence decide nothing (see above)."""
    if _FILED_RECITAL_RE.search(sentence):
        return True
    return bool(_MOTION_OPEN_RE.match(sentence)) and bool(_CONSIDERATION_RE.search(sentence))


_MOOTNESS_RE = re.compile(r"\bmoot\w*\b", re.IGNORECASE)
# Comma-conjoined clauses within one order sentence rule independently; the
# bare "and" without a comma stays one clause ("Judgment VACATED and case
# REMANDED ... as moot" must keep its mootness basis).
_CLAUSE_SPLIT_RE = re.compile(r",\s+and\s+", re.IGNORECASE)


def mootness_disposition(text: str) -> bool:
    """Whether ``text``'s disposition order is mootness practice, not a merits call.

    True when the matched disposition's *own sentence* carries mootness language
    — the Munsingwear vacatur ("Judgment VACATED and case REMANDED ... with
    instructions to dismiss the case as moot") or a plain dismissal as moot.
    Such an order's wording tracks the Court's vacatur practice rather than
    cert-worthiness, so scoring segments these cells into their own leaderboard
    stratum (see ``Outcome.disposition_basis``). Sentence-scoped on purpose: a
    denial followed by a separate sentence discussing mootness stays a merits
    disposition. False when no disposition matches at all.
    """
    for pattern, _disposition, _label in _ENTRY_SIGNALS:
        position = 0
        while (match := pattern.search(text, position)) is not None:
            if _is_non_order_sentence(_containing_sentence(text, match.start())):
                position = match.end()
                continue
            # The GVR patterns can span sentences ("Petition GRANTED. Judgment
            # VACATED ... as moot."), so the basis reads the whole sentence
            # window the match covers — then narrows to the comma-conjoined
            # clause(s) the match actually sits in, so a compound order pairing
            # a motion "denied as moot" with the cert denial ("... is denied as
            # moot, and the petition ... is denied.") never retro-tags the
            # merits denial as mootness practice.
            starts = _sentence_boundaries(text)
            window_start = max(s for s in starts if s <= match.start())
            later = [s for s in starts if s >= match.end()]
            window = text[window_start : later[0] if later else len(text)]
            clause_starts = [0] + [boundary.end() for boundary in _CLAUSE_SPLIT_RE.finditer(window)]
            rel_start, rel_end = match.start() - window_start, match.end() - window_start
            clause_from = max(c for c in clause_starts if c <= rel_start)
            clause_after = [c for c in clause_starts if c >= rel_end]
            clause = window[clause_from : clause_after[0] if clause_after else len(window)]
            return bool(_MOOTNESS_RE.search(clause))
    return False


def match_disposition_signal(text: str) -> tuple[Disposition, str, str] | None:
    """First cert-disposition signal in ``text``, as (disposition, label, snippet).

    ``None`` when no order language matches — the caller's cue that the text
    carries no machine-readable cert disposition. A match inside a non-order
    sentence (a filing recital, an expedite-motion order) is skipped and the
    scan continues, so a later genuine order in the same entry still reads.
    """
    for pattern, disposition, label in _ENTRY_SIGNALS:
        position = 0
        while (match := pattern.search(text, position)) is not None:
            if _is_non_order_sentence(_containing_sentence(text, match.start())):
                position = match.end()
                continue
            start = max(0, match.start() - _SNIPPET_PAD)
            end = min(len(text), match.end() + _SNIPPET_PAD)
            snippet = " ".join(text[start:end].split())
            return disposition, label, snippet
    return None
