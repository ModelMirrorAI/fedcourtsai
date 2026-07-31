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
carries (Rule 39.8 IFP dismissals, cert-before-judgment denials and dismissals,
and a SCOTUS merits judgment), where a false positive only parks a case for
triage rather than fabricating ground truth; anything neither instrument reads is
an accepted residual, surfaced by re-running the reachability probe
(``fedcourts probe-live-terms``) — do that after any pattern change to
re-establish the recall claim over the live sample.

The cert-before-judgment *grant* is read here, not left to routing — start-
anchored to the disposition entry's own noun so the expedite-motion recital
stays a miss — because a decided grant otherwise only wastes a forward-predict
cell each cycle (its event never resolves to be scored); its denial and
dismissal siblings, whose miss costs nothing but a triage parking, stay
routing-only.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from dateutil import parser as date_parser

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
    # Cert-before-judgment grant. The multi-word "before judgment" gap defeats the
    # single-word grant pattern above, so this names the shape explicitly. Start-
    # anchored — like the bare-vacate GVR row and the routing backstop's own CBJ
    # branch (``outcome._TERMINAL_ENTRY_RE``) — so the expedite *motion* reciting
    # the same noun phrase ("Motion ... to expedite consideration of the petition
    # for a writ of certiorari before judgment granted") opens with "Motion", so
    # the ``^`` anchor alone never lets it read here; ``_is_non_order_sentence``
    # is the second net for the rarer recital that *does* open with the petition
    # noun ("... before judgment granted filed."). Its
    # denial/dismissal siblings stay deliberate misses (routing-only): only the
    # grant is read, because a decided grant otherwise wastes forward-predict
    # cells every cycle. A CBJ grant that also vacates and remands is a GVR,
    # already read by the grant/vacate/remand rows above (scanned first).
    (
        re.compile(
            r"^(?:the\s+)?petitions? for (?:a )?writs? of certiorari before judgment "
            r"(?:is |are )?grant\w*",
            re.IGNORECASE,
        ),
        Disposition.granted,
        "cert granted before judgment",
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


# The two docket-progress signals the salience score reads. Defined here, beside
# the disposition patterns, because two consumers need them over two different
# shapes: ingest reads them off a synthesized entry list on the way into the
# corpus, and provisioning reads them off a raw snapshot payload to record what a
# cell could actually see. One definition, so a pattern change cannot move only
# one of those.
DISTRIBUTED_RE = re.compile(r"DISTRIBUTED\s+for\s+Conference\s+of\s+([\d/A-Za-z, ]+)", re.I)
CVSG_RE = re.compile(r"Solicitor\s+General\s+is\s+invited\s+to\s+file", re.I)


def proceedings_entries(payload: Mapping[str, Any]) -> list[tuple[str, str | None]]:
    """(description, date string) per proceedings entry, over either payload shape.

    The single reading of "what an entry is", shared by the signal parsers and by
    replay truncation, so a rule that keeps an entry and a rule that reads a
    signal off it cannot disagree about which entries exist.

    Returns an empty list when the payload carries no proceedings key at all —
    which a caller must distinguish from a docket with zero entries, since a
    redacted replay snapshot has the key removed wholesale.
    """
    live = payload.get("ProceedingsandOrder")
    if isinstance(live, list):
        out: list[tuple[str, str | None]] = []
        for entry in live:
            if isinstance(entry, Mapping):
                raw = entry.get("Date")
                out.append((str(entry.get("Text") or ""), str(raw) if raw else None))
        return out
    rest = payload.get("docket_entries")
    if isinstance(rest, list):
        return [
            (str(e.get("description") or ""), str(e.get("date_filed") or "") or None)
            for e in rest
            if isinstance(e, Mapping)
        ]
    return []


#: The two payload shapes' proceedings keys — live supremecourt.gov JSON and the
#: CourtListener REST record. Named once so a reader, a redactor, and a truncator
#: all mean the same thing by "the entries".
PROCEEDINGS_KEYS: tuple[str, ...] = ("ProceedingsandOrder", "docket_entries")


def entry_date(raw: str | None) -> date | None:
    """An entry's own filing date, or ``None`` unless it is fully specified.

    Strict, because this decides retention rather than merely reading a signal.
    ``dateutil`` fills missing components from *today*, so a partial string like
    "2025" or "Mar" yields a plausible-looking date that is really a function of
    the day the parser ran — which would both keep entries it should drop and make
    the retained set differ between two runs of the same replay.

    Parsing twice against two different defaults and rejecting a disagreement
    catches exactly that: a fully specified date is identical under both, and
    anything relying on a default is not.
    """
    if not raw:
        return None
    try:
        first = date_parser.parse(raw, default=datetime(1000, 1, 1)).date()
        second = date_parser.parse(raw, default=datetime(2000, 6, 15)).date()
    except (ValueError, OverflowError, TypeError):
        return None
    return first if first == second else None


def snapshot_carries_proceedings(payload: Mapping[str, Any]) -> bool:
    """Whether the payload discloses a proceedings list at all.

    ``False`` means the signals below are *unobservable* from this payload, not
    that they are zero — a redacted replay snapshot drops the key entirely, and a
    caller that read absence as "never distributed" would invent a fact.
    """
    return isinstance(payload.get("ProceedingsandOrder"), list) or isinstance(
        payload.get("docket_entries"), list
    )


def snapshot_distribution_count(payload: Mapping[str, Any]) -> int | None:
    """Distinct conferences the payload shows this petition distributed for.

    Distinct **parsed conference dates**, not raw entry matches, so a re-docketed
    notice of the same conference does not inflate the count and an unparseable
    capture is not counted at all — the same rule the corpus applies, so the two
    cannot disagree about one payload. Relists derive downstream as
    ``max(0, count - 1)``. ``None`` when the payload discloses no proceedings —
    unobservable rather than zero.
    """
    if not snapshot_carries_proceedings(payload):
        return None
    conferences: set[date] = set()
    for text, _ in proceedings_entries(payload):
        match = DISTRIBUTED_RE.search(text)
        if match is None:
            continue
        parsed = _conference_date(match.group(1))
        if parsed is not None:
            conferences.add(parsed)
    return len(conferences)


def _conference_date(raw: str) -> date | None:
    """The conference date a DISTRIBUTED entry names, or ``None`` if it will not parse.

    Deduping on the parsed date rather than on the matched text is what keeps this
    agreeing with the corpus: two spellings of one conference ("2/21/2025" and
    "February 21, 2025") are one relist, and the capture group is loose enough to
    match a non-date phrase, which must not count as a distribution at all.
    """
    try:
        return date_parser.parse(raw.strip().rstrip(".")).date()
    except (ValueError, OverflowError, TypeError):
        return None


def snapshot_cvsg_date(payload: Mapping[str, Any]) -> str | None:
    """The ISO date of the CVSG invitation the payload shows, if any.

    ``None`` covers both "no CVSG" and "no proceedings disclosed"; pair it with
    :func:`snapshot_carries_proceedings` where the difference matters.
    """
    if not snapshot_carries_proceedings(payload):
        return None
    for text, entry_date in proceedings_entries(payload):
        if CVSG_RE.search(text) and entry_date:
            return entry_date
    return None
