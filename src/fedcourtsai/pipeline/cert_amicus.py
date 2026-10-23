"""The cert-stage amicus count: how many amicus briefs a petition drew before the Court acted.

Amicus support at the cert stage is a long-studied grant signal, and the cert
docket records it in the same Clerk's vocabulary the interim docket does. So
this module owns no reading of what a brief is: every count here is
:func:`~fedcourtsai.pipeline.interim_signals.amicus_briefs` over a **cut** of the
docket's entries, and what this module decides is which entries are in the
cut. A widening of the per-entry reading reaches the cert count and the interim
count in one edit, and the two cannot disagree about what one entry is.

**One entry the cut leaves out that the interim reading counts: the Court's
order on a motion for leave to file as amicus curiae** ("Motion of X for leave
to file a brief as amicus curiae GRANTED.", :func:`is_amicus_motion_order`).
Until the Rule 37 amendment of January 1, 2023 dropped the consent
requirement, an amicus without the parties' consent filed by motion, the brief
riding the motion entry, and the order on it is a second entry reciting the
Latin for the same brief: one amicus, counted twice. The motion entry stays
counted, since it is where that brief reached the docket; its order adds no
brief. The interim reading keeps counting the order, because its column is
max-latched and frozen onto committed outcomes, and narrowing it is a
re-derivation of its own; the cert column is new, so its reading can be the
narrower one from its first write.

**The cert stage ends at the first disposition entry**, in docket order
(:func:`~fedcourtsai.pipeline.cert_signals.match_disposition_signal`, the same
first-entry rule :func:`~fedcourtsai.pipeline.cert_signals.cert_grant_date` and
the cert-stage moment triggers read). A granted case goes on to draw its merits
amici — usually far more than it drew on the petition — and those briefs are
the outcome's consequence, not a signal of it, so a count that ran past the
grant would read the answer into the question. The cut is **positional**
rather than dated: it holds on an entry with no readable date, and an amicus
entry the Clerk docketed after the grant on the grant day itself stays out,
which is the merits-stage reading of a brief that could only have been filed
after the conference sat.

Two counts, for two readers:

- :func:`cert_amicus_briefs` is the count **at disposition** — every entry
  before the disposing one, undated entries included. A resolved petition's
  value is fixed by the cut and an open petition's only grows as entries
  accumulate, so the count is monotone over a docket's life and max-latch
  compatible. It is what the corpus ``cert_amicus_briefs`` column stores and
  what the stat pack's amicus cut buckets on, the timing the relist cut takes:
  where the petition ended up, not what a forecaster faced.
- :func:`cert_amicus_briefs_before` is the **prediction-side** count, over the
  cert-stage entries dated strictly before a cutoff. An undated entry is left
  out there, the opposite discipline from the count above, because the stakes
  are: a guessed date can put a brief filed after the cutoff in front of a
  forecast, while a dropped one only lowers a count no column latches.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date

from .cert_signals import entry_date, match_disposition_signal
from .interim_signals import _AMICUS_RE, amicus_briefs

# The Court's ruling on an amicus motion: an entry opening on the motion (or
# "The motion"), reciting the Latin, and carrying a ruling verb. The filing of
# the motion carries "filed" and no ruling, and stays in the count. Read
# alongside the shared accepted-form phrase (`interim_signals._AMICUS_RE`) so
# "amicus curiae" is spelled in one place.
_MOTION_OPENING_RE = re.compile(r"^\s*(?:the\s+)?(?:joint\s+)?motions?\b", re.IGNORECASE)
_RULING_RE = re.compile(r"\b(?:granted|denied|dismissed)\b", re.IGNORECASE)


def is_amicus_motion_order(text: str) -> bool:
    """Whether an entry is the Court's order on a motion for leave to file as amicus curiae."""
    return bool(
        _MOTION_OPENING_RE.search(text) and _AMICUS_RE.search(text) and _RULING_RE.search(text)
    )


def cert_stage_entries(entries: Sequence[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
    """The entries before the first disposition entry, in docket order.

    The disposing entry itself is not in the cut — an order is not a brief —
    and neither is anything after it: a rehearing paper, a merits filing, a
    post-denial motion. A docket with no disposition entry yet is all cert stage.
    """
    kept: list[tuple[str, str | None]] = []
    for text, raw in entries:
        if match_disposition_signal(text) is not None:
            break
        kept.append((text, raw))
    return kept


def _counted(entries: Sequence[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
    """The cert-stage entries the shared reading is run over: less the amicus-motion orders."""
    return [
        (text, raw) for text, raw in cert_stage_entries(entries) if not is_amicus_motion_order(text)
    ]


def cert_amicus_briefs(entries: Sequence[tuple[str, str | None]]) -> int:
    """How many amicus briefs the docket recorded at the cert stage, through its disposition.

    The per-entry reading is
    :func:`~fedcourtsai.pipeline.interim_signals.amicus_briefs` — accepted-form
    entries one apiece, plus each distinct lead filer whose brief is docketed as
    submitted and not yet accepted — over :func:`cert_stage_entries`, less the
    Court's orders on amicus motions (:func:`is_amicus_motion_order`). That
    reading's other stated approximations carry over unchanged: a multi-filer
    entry counts once, an entry reciting the Latin without being a brief (a
    consent to the filing of amicus briefs, a certificate of service on one)
    counts beside the briefs, and a refused submission stays counted. The
    Solicitor General's invited brief is an amicus brief and counts as one.
    """
    return amicus_briefs([text for text, _raw in _counted(entries)])


def cert_amicus_briefs_before(entries: Sequence[tuple[str, str | None]], cutoff: date) -> int:
    """How many cert-stage amicus briefs the docket recorded **strictly before** ``cutoff``.

    The entries :func:`cert_amicus_briefs` reads whose own fully specified date
    (:func:`~fedcourtsai.pipeline.cert_signals.entry_date`) falls before
    ``cutoff``. An entry dated on the cutoff day is out, as it is out of a
    cell's snapshot cut at that day, and an undated entry is out because no
    date places it before the cutoff. This is the count a cert cell's
    ``record/context.json`` would freeze beside ``distribution_count``, once a
    process change admits it under its own re-bless.
    """
    kept = [
        text
        for text, raw in _counted(entries)
        if (when := entry_date(raw)) is not None and when < cutoff
    ]
    return amicus_briefs(kept)
