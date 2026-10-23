"""The cert-stage amicus count: how many amicus briefs a petition drew before the Court acted.

Amicus support at the cert stage is a long-studied grant signal, and the cert
docket records it in the same Clerk's vocabulary the interim docket does. So
this module owns no reading of its own: every count here is
:func:`~fedcourtsai.pipeline.interim_signals.amicus_briefs` over a **cut** of the
docket's entries, and what this module decides is only which entries are in the
cut. A widening of the per-entry reading reaches the cert count and the interim
count in one edit, and the two cannot disagree about what one entry is.

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

from collections.abc import Sequence
from datetime import date

from .cert_signals import entry_date, match_disposition_signal
from .interim_signals import amicus_briefs


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


def cert_amicus_briefs(entries: Sequence[tuple[str, str | None]]) -> int:
    """How many amicus briefs the docket recorded at the cert stage, through its disposition.

    The per-entry reading is
    :func:`~fedcourtsai.pipeline.interim_signals.amicus_briefs` — accepted-form
    entries one apiece, plus each distinct lead filer whose brief is docketed as
    submitted and not yet accepted — over :func:`cert_stage_entries`. That
    reading's stated approximations carry over with it unchanged: a multi-filer
    entry counts once, an entry reciting the Latin without being a brief (a
    motion for leave to file as amicus curiae, the Solicitor General's invited
    brief among the briefs) counts beside the briefs, and a refused submission
    stays counted.
    """
    return amicus_briefs([text for text, _raw in cert_stage_entries(entries)])


def cert_amicus_briefs_before(entries: Sequence[tuple[str, str | None]], cutoff: date) -> int:
    """How many cert-stage amicus briefs the docket recorded **strictly before** ``cutoff``.

    The cert-stage entries (:func:`cert_stage_entries`) whose own fully
    specified date (:func:`~fedcourtsai.pipeline.cert_signals.entry_date`) falls
    before ``cutoff``, read by the shared per-entry rule. An entry dated on the
    cutoff day is out, as it is out of a cell's snapshot cut at that day, and
    an undated entry is out because no date places it before the cutoff.
    """
    kept = [
        text
        for text, raw in cert_stage_entries(entries)
        if (when := entry_date(raw)) is not None and when < cutoff
    ]
    return amicus_briefs(kept)
