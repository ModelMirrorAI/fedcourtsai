"""Convergence of stored docket numbers on the marking-free spelling.

The population is the one the ``docket_numbers_carry_no_capital_marking`` corpus
check reports, and this is what drains it: the check reads a stored number that
still carries the marking, counts it against a ceiling, and turns red once the
population grows — which distinguishes a write path that stopped stripping from
the finite residue this pass exists to clear. Selection is court-agnostic for the
same reason, even though the marking is a SCOTUS habit upstream: a pass that
filtered on court would leave a row the check reports with no repair.

The ingest write site stores a docket number with the Court's
``*** CAPITAL CASE ***`` marking removed and carries the signal in the
``capital_case`` column instead (:func:`corpus.strip_docket_annotation` paired
with :func:`corpus.is_capital_docket_number`). Stored rows converge on that
spelling only when the write site touches them again, and no *automatic* channel
does so outside the live slice: a live-slice row normalizes on its next poll,
while a row outside it converges only under a re-read aimed at it —
``refresh-dockets`` on named rows, or a Term re-walk. This is the dedicated sweep
that clears the backlog without one, which is what the population needs, being
overwhelmingly decided rows the rotation has long since left behind.

Only the marking's **exact words** select a row, never the ``*** … ***`` shape
:data:`corpus._DN_ANNOTATION` reads, and the difference is the whole safety
argument: a shape match treats the asterisks as delimiters, so on a consolidated
circuit docket that uses ``***`` as a *separator* between numbers it would delete
an entire docket number out of the column that is the record. The pass therefore
delegates both halves of the decision to the ingest write site's own pair, and
inherits its guarantee that the number it keeps and the flag it raises can never
disagree about what was there.

The rewrite cannot create a duplicate pair for :mod:`fedcourtsai.dedupe` to find.
Both SCOTUS channels reconcile identity on :func:`corpus.normalize_docket_number`
— registered as the SQLite ``norm_dn`` function, and the value the dedupe scan
groups on — and that normalization already strips the annotation by shape. The
marked and marking-free spellings of one docket therefore already compare equal
to the join, so replacing one with the other moves no row into or out of any
group: the pair set is identical before and after. Rows that already share a
normalized identity with another row are reported as a count beside the rewrite,
because they are the dedupe pass's population and this pass neither creates nor
resolves them — it only makes the collision visible in the stored spelling.

``capital_case`` is raised rather than assigned a computed value: it sits in the
upsert's max-latch family, so a row whose flag is already set stays set and the
write can only ever advance it. That is what makes a re-run a no-op — a rewritten
row no longer carries the marking, so it leaves the population it was selected
from — and what makes an interrupted run safe to finish by running it again.

Like its ``set_*`` siblings the write is a direct ``UPDATE`` of the index and
**never the casestore mirror**, so a store-side rebuild from ``case.json`` would
resurrect both the marked spelling and the cleared flag.
"""

from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass, field

from . import corpus


@dataclass
class MarkingRewrite:
    """One stored docket number converging on its marking-free spelling."""

    case_id: str
    was: str
    now: str
    #: The normalized identity this row already shares with another stored row.
    #: The rewrite does not create the collision (the join normalizes the marking
    #: away either way) and does not resolve it — it is `dedupe-live-rows`' work.
    shares_identity: bool = False


@dataclass
class DocketMarkingResult:
    """What the marking convergence rewrote (or would rewrite on a dry run)."""

    applied: bool = False
    rewritten: list[MarkingRewrite] = field(default_factory=list)
    #: True when ``apply`` was asked for but the blast-radius bound refused it.
    #: Nothing is written in that case — the plan is reported and abandoned.
    refused: bool = False


def normalize_docket_markings(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_rewrites: int | None = None,
) -> DocketMarkingResult:
    """Rewrite marked SCOTUS docket numbers to their stored spelling, flag raised.

    ``max_rewrites`` is the blast-radius bound and lives here rather than in the
    caller, so a code caller is bounded on the same terms as the command. Over the
    bound nothing is written and ``refused`` is set.
    """
    result = DocketMarkingResult(applied=apply)
    # Court-agnostic, matching the `docket_numbers_carry_no_capital_marking` corpus check whose
    # population this drains: the marking is a SCOTUS habit upstream, but a pass
    # that selects on court would leave a row the check reports unrepairable. The
    # asterisk prefilter is what keeps this off a full table scan; the word match
    # is the authority on what is a marking, and the only thing that selects a row.
    candidates = [
        (str(row["case_id"]), str(row["court"]), str(row["docket_number"]))
        for row in conn.execute(
            "SELECT case_id, court, docket_number FROM cases "
            "WHERE docket_number LIKE '%*%' ORDER BY case_id"
        )
        if corpus.is_capital_docket_number(str(row["docket_number"]))
    ]
    if not candidates:
        return result

    # One pass for the shared-identity count, and only when a SCOTUS candidate
    # needs it: `norm_dn` is a Python callback, so this is the pass's one expensive
    # read and it is not worth doing to answer an empty plan or an all-circuit one.
    # Scoped to SCOTUS because that is the join's own scope — the two-channel
    # identity reconciliation these keys belong to exists for SCOTUS dockets only.
    # The callback runs once per row rather than twice, the NULL being dropped here
    # rather than by a WHERE that would re-evaluate it.
    keys: Counter[str] = Counter()
    if any(court == "scotus" for _, court, _ in candidates):
        keys = Counter(
            key
            for (key,) in conn.execute(
                "SELECT norm_dn(docket_number) FROM cases WHERE court = 'scotus'"
            )
            if key is not None
        )
    for case_id, court, was in candidates:
        now = corpus.strip_docket_annotation(was)
        # A number that normalizes to nothing has no identity to share, so it is
        # not looked up — the join skips such a row for the same reason.
        key = corpus.normalize_docket_number(now)
        result.rewritten.append(
            MarkingRewrite(
                case_id=case_id,
                was=was,
                now=now,
                shares_identity=court == "scotus" and key is not None and keys[key] > 1,
            )
        )

    if apply and max_rewrites is not None and len(result.rewritten) > max_rewrites:
        result.refused = True
        result.applied = False
        return result
    if not apply:
        return result

    with conn:
        for entry in result.rewritten:
            # `capital_case` is raised, never computed: the column max-latches in
            # the upsert, so a flag another channel already set stays set and this
            # write can only advance it. `MAX` is safe against the SQLite
            # `max(NULL, 1) = NULL` hazard only because the column is NOT NULL.
            conn.execute(
                "UPDATE cases SET docket_number = ?, capital_case = MAX(capital_case, 1) "
                "WHERE case_id = ?",
                (entry.now, entry.case_id),
            )
    return result
