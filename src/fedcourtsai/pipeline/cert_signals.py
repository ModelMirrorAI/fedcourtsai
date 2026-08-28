"""Cert-disposition signal patterns over docket-entry / proceedings text.

The one deterministic instrument that reads a concrete cert disposition out of
free order-list language ("Petition DENIED.", "GVR'd", "certiorari granted"),
shared by every consumer that needs it — the live channel's ingest-time
resolution (:mod:`.ingest`), the historical loader (:mod:`.historical`), the
live reachability probe (:mod:`.liveprobe`), and the forward-provisioning
leakage guard (``provision-snapshot --refuse-terminal``), whose false-positive
cost is the cheapest of the family: one refused cell, no recorded fact.
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
from types import MappingProxyType
from typing import Any

from dateutil import parser as date_parser

from ..schemas import GRANTED_DISPOSITIONS, Disposition

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
    # cells every cycle. A CBJ grant that also vacates and remands is a GVR:
    # the short form is read by the grant/vacate/remand rows above (scanned
    # first), and the prose form — where the vacatur sentence names the lower
    # court and so escapes both those rows' windows — is re-labelled at the
    # use site by the `_gvr_tail` upgrade in `match_disposition_signal`.
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

# The GVR upgrade's tail: an order sentence, elsewhere in a granted entry,
# that vacates and remands the judgment. Matched per sentence and anchored to
# the sentence's own subject — what actually defeats the bare-vacatur row on
# the prose form is that row's *entry-start* `^` anchor, since the vacatur is
# the entry's second sentence there — with the ordering voice required so a
# narrative or suggested vacatur ("the judgment ... was vacated last Term",
# "suggests that the judgment be vacated") never re-labels a real merits
# grant. That voice takes two forms. The prose copula ("is/are [hereby]
# vacated") carries the voice test in the words. The terse clerk form
# ("Judgment of the ... Court VACATED and case REMANDED") has no copula at
# all — its signature is the subject noun phrase running straight into the
# capitalized verb — so it is admitted case-sensitively via the scoped
# `(?-i:...)` group, barred by lookbehind where an auxiliary, "previously" /
# "already", or a comma (the citation-recital shape, "..., VACATED AND
# REMANDED (9th Cir. 2024)") marks a capitalized participle as narrative.
# Two accepted residuals, one per side: a capitalized participle behind an
# unlisted narrative marker would still upgrade, and a comma'd clerk variant
# would miss and keep its grant label — the miss is the cheap side, because
# a false upgrade is costlier than a miss on the label axis (`gvr` leaves
# the merits population silently), which is why every bound here is tight
# even though the upgrade can never *create* a disposition. The gaps only
# need to span a named lower court between "judgment" and "vacated".
_GVR_TAIL_RE = re.compile(
    r"^(?:the\s+)?judgment\b.{0,120}?\b(?:(?:is|are)\s+(?:hereby\s+)?vacated"
    r"|(?<!\bwas\s)(?<!\bwere\s)(?<!\bbe\s)(?<!\bbeen\s)(?<!\bbeing\s)"
    r"(?<!\bpreviously\s)(?<!\balready\s)(?<!,\s)(?-i:VACATED))\b"
    r".{0,120}?\bremand\w*",
    re.IGNORECASE | re.DOTALL,
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
#   - the order *on a motion about the petition* — the sentence's subject is a
#     motion (or an application, or a party's request) and the petition reaches
#     it only as that motion's **object**, so the trailing verb grants or denies
#     the motion and says nothing about the petition. The clerk writes this
#     shape a dozen ways, and each one fabricates a cert grant dated to an
#     ancillary order: "The motions to extend the time to file responses to the
#     petition for a writ of certiorari are granted ...", "Motion to delay
#     distribution of the petition for a writ certiorari granted.",
#     "Petitioner's request to delay distribution of the petition granted.",
#     "Motion to unseal the petition for a writ of certiorari GRANTED.",
#     "Joint motion to defer consideration of the petition ... GRANTED."
# What separates that class from the compound orders that *do* decide the
# petition is not the motion's purpose — enumerating those is a losing race
# against the clerk's vocabulary — but the petition's **grammatical role**. In
# every real compound the petition is a *conjunct of the ordering subject*, and
# the clerk marks the conjunction with "and": "The motion to expedite and the
# petition for a writ of certiorari are GRANTED.", the Rule 39.8 pair "The
# motion for leave to proceed in forma pauperis is denied, and the petition ...
# is dismissed.", the IFP grant "Motion to proceed in forma pauperis and
# petition for a writ of certiorari GRANTED.", and the stay-treated-as-cert
# grant "The application is also treated as a petition ..., and the petition is
# granted." So the guard fires on a motion-opening sentence *unless* it carries
# that conjunction — a rule about grammar, which the clerk's wording obeys even
# where a rule about motion purposes would need extending.
# One accepted residual, on the cheap side: a motion- or
# application-opening sentence that granted the petition without conjoining it
# would be suppressed and left to the routing backstop. Price that side at all
# three of its costs before widening this guard again, because two of them are
# not the obvious one: the missed grant wastes a forward-predict cell each
# cycle, ``provision-snapshot --refuse-terminal`` stops refusing a docket that
# is in fact decided, and — since
# :func:`fedcourtsai.disposition_convergence._recording_entry` reads a
# suppressed grant sentence as proof that a stored ``granted`` was a parse
# gap — a newly suppressed *real* grant order would read as one to withdraw.
# The bound still sits on that side: a fabricated grant records ground truth
# that never happened, on every one of those surfaces at once.
# The subject word carries an optional short qualifier ("Joint motion", "Consent
# motion", "Petitioner's motion", "The Special Counsel's request") — up to two
# qualifier words after an optional leading article, so "The unopposed joint
# motion ..." still anchors. The bound is what keeps the anchor meaning *the
# sentence's subject is a motion* rather than "a motion is mentioned somewhere
# ahead of the disposition word". The qualifier class admits both apostrophes
# the clerk types — ASCII and the typographic U+2019 — so a possessive qualifier
# counts as one word rather than splitting the bound. "Request" sits beside
# "motion" and "application" because the clerk uses it for the same papers
# ("Petitioner's request to delay distribution of the petition granted."); the
# conjunction escape is what keeps the one real grant written that way ("The
# Special Counsel's request to treat the stay application as a petition ..., and
# that petition is granted ...") readable.
_FILED_RECITAL_RE = re.compile(r"\bfiled\s*\.?\s*$", re.IGNORECASE)
_MOTION_OPEN_RE = re.compile(
    r"^\s*(?:the\s+)?(?:[\w'\u2019-]+\s+){0,2}?(?:motions?|applications?|requests?)\b",
    re.IGNORECASE,
)
# The petition conjoined into the ordering subject. Anchored on "and" running
# straight into the cert noun through at most one determiner, so the *motion's*
# own coordination ("... and to delay distribution of the petition ...") is
# never mistaken for it: there "and" is followed by the second infinitive, not
# by the noun. "and the time is extended" — the tail of every extension order —
# fails on the same anchor.
# The bare "petition" alternative is what admits the stay-treated-as-cert grant,
# whose conjunct names no writ ("..., and the petition is granted (case No.
# 25-332)"), so it cannot require the cert noun phrase. It excludes the *other*
# petitions the clerk conjoins instead — rehearing, leave, mandamus — with a
# lookahead that rejects a following "for" unless what it introduces is a writ
# of certiorari. Left loose, "and the petition for rehearing is denied" would
# read as the cert petition's own conjunct.
_CONJOINED_PETITION_RE = re.compile(
    r"\band\s+(?:the\s+|a\s+|that\s+|its\s+)?"
    r"(?:petitions?(?!\s+for\s+(?!(?:a\s+)?writs?\s+of\s+certiorari))"
    r"|writs?\s+of\s+certiorari|certiorari)\b",
    re.IGNORECASE,
)
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
    return bool(_MOTION_OPEN_RE.match(sentence)) and not _CONJOINED_PETITION_RE.search(sentence)


def refused_grant_sentence(text: str) -> str | None:
    """The sentence in ``text`` a cert grant would be read out of but for the guard.

    The inverse of :func:`match_disposition_signal` over the grant family: it
    returns the sentence that carries a grant-shaped match and is refused by
    :func:`_is_non_order_sentence` — the ancillary motion order, or the docketing
    recital — whitespace-collapsed for quoting. ``None`` when no grant-shaped
    match is refused here, which includes every entry whose grant *does* read
    (that one is :func:`match_disposition_signal`'s answer, not this one).

    It exists because a committed ``granted`` label is a claim about text, and
    the only way to tell a **parse gap** from a faithful record of an older
    vocabulary is to find the text the claim was read out of and see whether
    today's parser still stands behind it. The convergence sweep
    (:func:`fedcourtsai.disposition_convergence._recording_entry`) asks exactly
    that, and a sentence returned here is its evidence: this is what a grant was
    read from, and it is not an order on the petition. Nothing else may treat
    the return as a disposition — it is a *refused* read, surfaced for audit,
    which is why it comes back as prose rather than as a
    :class:`~fedcourtsai.schemas.Disposition`.
    """
    for pattern, disposition, _label in _ENTRY_SIGNALS:
        if disposition not in GRANTED_DISPOSITIONS:
            continue
        position = 0
        while (match := pattern.search(text, position)) is not None:
            sentence = _containing_sentence(text, match.start())
            if _is_non_order_sentence(sentence):
                return " ".join(sentence.split())
            position = match.end()
    return None


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
    for pattern, matched_disposition, _label in _ENTRY_SIGNALS:
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
            if _MOOTNESS_RE.search(clause):
                return True
            # The prose Munsingwear: the grant row wins, the GVR upgrade in
            # `match_disposition_signal` re-labels the entry off the vacatur
            # sentence — so the basis must read that sentence's own wording
            # too, or the pair would record a merits GVR (`gvr` + `standard`)
            # for a vacatur ordered "with instructions to dismiss as moot".
            if matched_disposition is Disposition.granted:
                tail = _gvr_tail_sentence(text)
                if tail is not None:
                    return bool(_MOOTNESS_RE.search(tail))
            return False
    return False


def _gvr_tail_sentence(text: str) -> str | None:
    """The order sentence in ``text`` that vacates and remands the judgment.

    Per sentence, subject-anchored, in the ordering voice — the prose copula
    or the terse clerk form (see ``_GVR_TAIL_RE``) — and
    still behind the non-order-sentence guard — a party paper suggesting a
    vacatur ("Brief of respondent suggesting that the judgment be vacated and
    the case remanded filed.") is a recital, not an order, and must not turn
    the grant beside it into a GVR. Returns the sentence so the mootness basis
    can read the vacatur's own wording, not just the grant's.
    """
    starts = _sentence_boundaries(text)
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        # Collapsed to single spaces before matching: the narrative-marker
        # lookbehinds are fixed-width, so an interior double space (which
        # upstream entry text does carry — ingestion strips but never
        # collapses) would otherwise un-bar every one of them.
        sentence = " ".join(text[start:end].split())
        if _GVR_TAIL_RE.match(sentence) and not _is_non_order_sentence(sentence):
            return sentence
    return None


def match_disposition_signal(text: str) -> tuple[Disposition, str, str] | None:
    """First cert-disposition signal in ``text``, as (disposition, label, snippet).

    ``None`` when no order language matches — the caller's cue that the text
    carries no machine-readable cert disposition. A match inside a non-order
    sentence (a filing recital, an order on a motion about the petition) is skipped and the
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
            if disposition is Disposition.granted and _gvr_tail_sentence(text) is not None:
                # A grant whose entry also vacates and remands the judgment is
                # a GVR wearing prose: the CBJ form names the lower court
                # between "granted" and "vacated", so the gap-bounded GVR rows
                # above miss it and the grant row wins. Upgrading here rather
                # than widening those gaps keeps the table's precision — the
                # upgrade can never invent a disposition where none matched.
                return Disposition.gvr, "GVR", snippet
            return disposition, label, snippet
    return None


# The order-list notations that record a noted dissent from — or a statement
# respecting — a denial of certiorari. Four templates, because the clerk spells
# one fact four ways and no single phrase covers them:
#   - the explicit dissent ("... dissenting from the denial of certiorari");
#   - the would-grant vote, which is a dissent recorded as a vote rather than a
#     writing ("Justice Thomas would grant the petition ...");
#   - the statement respecting the denial, which is not a dissent but is the
#     same observable — a Justice wrote separately about this denial;
#   - the bare notation ("Justice Sotomayor, dissenting."), which names no
#     denial of its own and therefore only counts inside a denial order (see
#     :func:`dissent_from_denial`).
# Each gap is bounded by `[^.;]` rather than by the sentence walker: order-list
# notations run to a period or a semicolon, so the bound keeps a notation and its
# scope in one place. It is close to the walker's split but not identical —
# stricter on an abbreviation period, which the walker merges through, and looser
# on `!`/`?`, which no order list uses — and the difference is immaterial to
# these four shapes.
_DISSENT_FROM_DENIAL_RE = re.compile(r"\bdissenting\s+from\s+the\s+denial\b", re.IGNORECASE)
_WOULD_GRANT_RE = re.compile(r"\bwould\s+grant\s+the\s+petitions?\b", re.IGNORECASE)
_RESPECTING_DENIAL_RE = re.compile(
    r"\bjustices?\b[^.;]{0,160}?\brespecting\s+the\s+denial\b", re.IGNORECASE
)
_BARE_DISSENT_RE = re.compile(
    r"\b(?:chief\s+)?justices?\s+[A-Za-z][A-Za-z'.-]*\b[^.;]{0,160}?,\s*dissenting\b",
    re.IGNORECASE,
)

#: The three notations that name the denial themselves, so they read on their
#: own entry — an order list files a statement respecting a denial as its own
#: line, with no disposition words beside it.
_SELF_ANCHORED_DISSENT_RES = (
    _DISSENT_FROM_DENIAL_RE,
    _WOULD_GRANT_RE,
    _RESPECTING_DENIAL_RE,
)


def dissent_from_denial(text: str) -> bool:
    """Whether this entry's order text records a noted dissent from a denial.

    **Aggregated existence only**: *that* some Justice dissented from, or wrote
    respecting, the denial — never which Justice, and never how many. The
    per-Justice form is deliberately not readable from here
    (``docs/outcome-decomposition.md``, the eight tests' volume condition): such
    notings sit near one percent of petitions and concentrate in two Justices,
    so the fine claim collapses to a Bernoulli draw while the aggregate does
    not.

    The entry's **own disposition** is the guard, read through
    :func:`match_disposition_signal` so the module's non-order-sentence rejects
    (a filing recital, an order on a motion about the petition) apply here unchanged: an entry
    whose order is a grant, a GVR or a dismissal records no dissent *from a
    denial*, whatever separate writings it also notes, so it reads False. An
    entry carrying no disposition at all — the statement filed on its own line —
    still reads, on the self-anchored notations only.

    The filing-recital rejection is deliberately **not** applied to the
    notations themselves. A dissent is routinely docketed as a filing
    ("Statement of Justice Alito, dissenting, filed."), so suppressing recitals
    here would drop exactly the shape the claim is about — the opposite of what
    the guard does for a disposition, where a recital would fabricate ground
    truth.

    One accepted residual, and it runs the safe way: a bare "Statement of Justice
    Alito filed." on an entry of its own spells none of the four notations and
    carries no disposition to anchor the bare-dissent shape, so it reads False.
    Naming a Justice is not itself the observable — the claim is about a
    *dissent or a statement respecting the denial*, and an entry that says
    neither is a miss rather than a signal. A false negative costs one unread
    denial; a false positive would commit a fact to the ground-truth record.
    """
    signal = match_disposition_signal(text)
    if signal is not None and signal[0] is not Disposition.denied:
        return False
    if any(pattern.search(text) for pattern in _SELF_ANCHORED_DISSENT_RES):
        return True
    # The bare notation names no denial, so it counts only where this entry's
    # own order is one; alone it is as likely to be a merits dissent.
    return signal is not None and _BARE_DISSENT_RE.search(text) is not None


# The two docket-progress signals the salience score reads. Defined here, beside
# the disposition patterns, because two consumers need them over two different
# shapes: ingest reads them off a synthesized entry list on the way into the
# corpus, and provisioning reads them off a raw snapshot payload to record what a
# cell could actually see. One definition, so a pattern change cannot move only
# one of those.
DISTRIBUTED_RE = re.compile(r"DISTRIBUTED\s+for\s+Conference\s+of\s+([\d/A-Za-z, ]+)", re.I)
CVSG_RE = re.compile(r"Solicitor\s+General\s+is\s+invited\s+to\s+file", re.I)

# The entry-initial reading of the same phrase. A conference distribution the
# clerk enters for the *petition* opens its entry with the word; a distribution
# of some ancillary paper always names that paper first ("Motion (25M82)
# DISTRIBUTED for Conference of …", "Application (23A242) DISTRIBUTED for
# Conference of …", "Suggestion of mootness DISTRIBUTED for Conference of …"),
# so the leading position is what separates the petition's own trajectory from
# traffic riding beside it.
_DISTRIBUTED_ENTRY_INITIAL_RE = re.compile(
    r"^\s*DISTRIBUTED\s+for\s+Conference\s+of\s+([\d/A-Za-z, ]+)", re.I
)

#: The registered distribution parses, keyed by label. The *count* of conference
#: distributions is a versioned input to the salience band
#: (``docs/salience.md``), so which phrase-reading produced a count has to be
#: nameable rather than implied by whichever pattern was live: a parse is added
#: here, never edited, and each salience version pins the one it was fitted on
#: (:attr:`~fedcourtsai.pipeline.salience.SalienceScorer.distribution_parse`).
#:
#: Every parse captures the conference phrase in group 1 and is read with
#: ``.search``, so the pattern is the whole of the difference between two
#: versions — ``dist-v2``'s ``^`` anchor is what excludes an ancillary paper's
#: distribution, and both feed the same date parse and same distinct-date dedupe
#: below. The two counters — ingest's over a synthesized entry list, the
#: snapshot reader's over a raw payload — both take their pattern from here, so
#: a parse cannot move for only one of them.
DISTRIBUTION_PARSES: Mapping[str, re.Pattern[str]] = MappingProxyType(
    {"dist-v1": DISTRIBUTED_RE, "dist-v2": _DISTRIBUTED_ENTRY_INITIAL_RE}
)

#: The parse every counter reads unless its caller names another — the reading
#: the corpus's stored ``distribution_count`` column holds.
DEFAULT_DISTRIBUTION_PARSE = "dist-v2"


def distribution_pattern(parse: str) -> re.Pattern[str]:
    """The registered pattern for ``parse``.

    Raises :class:`KeyError` for an unregistered label rather than falling back
    to the default: a caller asking for a parse this process cannot perform
    wants an error, not a count silently produced by a different reading than
    the one it named.
    """
    try:
        return DISTRIBUTION_PARSES[parse]
    except KeyError:
        registered = ", ".join(sorted(DISTRIBUTION_PARSES))
        raise KeyError(
            f"unregistered distribution parse {parse!r}; registered: {registered}"
        ) from None


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


def snapshot_distribution_count(
    payload: Mapping[str, Any], *, parse: str = DEFAULT_DISTRIBUTION_PARSE
) -> int | None:
    """Distinct conferences the payload shows this petition distributed for.

    Distinct **parsed conference dates**, not raw entry matches, so a re-docketed
    notice of the same conference does not inflate the count and an unparseable
    capture is not counted at all — the same rule the corpus applies, so the two
    cannot disagree about one payload. Relists derive downstream as
    ``max(0, count - 1)``. ``None`` when the payload discloses no proceedings —
    unobservable rather than zero.

    ``parse`` names the registered phrase-reading (:data:`DISTRIBUTION_PARSES`);
    an unregistered label raises. The date parse and the dedupe are the parse's
    only shared machinery, so two parses of one payload differ by exactly which
    entries they read.
    """
    if not snapshot_carries_proceedings(payload):
        return None
    pattern = distribution_pattern(parse)
    conferences: set[date] = set()
    for text, _ in proceedings_entries(payload):
        match = pattern.search(text)
        if match is None:
            continue
        parsed = conference_date(match.group(1))
        if parsed is not None:
            conferences.add(parsed)
    return len(conferences)


def conference_date(raw: str) -> date | None:
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
