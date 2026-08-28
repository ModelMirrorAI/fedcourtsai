"""Re-derive the corpus ``distribution_count`` column under a named parse.

The count of conference distributions is the salience band's primary feature,
and it is *parsed* out of free docket-entry text — so which entries a reading
admits is part of what a band label means
(:data:`fedcourtsai.pipeline.cert_signals.DISTRIBUTION_PARSES`,
``docs/salience.md``). Activating a newly registered parse therefore starts
here: until the stored column is genuinely re-derived under it, every
downstream consumer — the gate's banding, the statpack's per-band base rates,
the relist-tier cutpoints — is still reading the incumbent parse's counts, and
a registered version pinning the new one would be banding on numbers the
corpus never produced.

**The write is a direct ``UPDATE``, and that is the whole point.** The
ordinary ingestion path max-latches this column
(:func:`fedcourtsai.corpus._update_clause`): proceedings are append-only
upstream, so a live payload served *without* its proceedings yields a
confident ``0`` that must never wipe a stored count, and the latch takes the
larger of stored and incoming. A re-derive under a **narrower** reading is
exactly the write that latch is built to reject — every changed row moves
down — so routing it through :func:`fedcourtsai.corpus.upsert_rows` would
write nothing at all while reporting success. A silent no-op that reads as
convergence is worse than a refusal, so this sweep bypasses the latch
deliberately and says so.

Bypassing a guard obliges naming what the guard was for, and saying how much
of it is replaced. The max latch rejects **any** regression, from any cause.
What replaces it here is narrower: a row whose latest live-shaped snapshot is
missing, or discloses no proceedings **entries**, is counted ``unobservable``
and **left untouched** — never written to ``0``. That covers the served shell
the latch was really built for — the proceedings key removed, and equally an
empty list, since every live-polled SCOTUS docket carries at least its
docketing entry — and it does not cover a payload whose entry list is merely
*short*. Nothing here can tell a truncated docket from a shorter reading of a
whole one.

The check that closes that gap is procedural rather than mechanical, and it is
cheap: **run the sweep under the incumbent parse first.** That pass must report
``changed = 0``, because the stored column is the incumbent reading of these
very snapshots — so anything it moves is stored-column drift (a degraded
payload, a dedupe merge-max, a backfill gap), not a parse effect. Only once it
reports zero does a candidate parse's changed set mean what it is read as: the
difference between two readings, and nothing else.

**The frame is the live slice, because that is where the column is populated.**
``distribution_count`` is non-null on live-channel SCOTUS rows and nowhere
else: the bulk import never parsed proceedings text, so a non-live row has no
count for a parse to disagree with. Walking the live slice therefore converges
the whole column rather than a segment of it — which the census cannot do,
since its frame is the gate's *scored* segment (paid, modern-cert, parseable
Term) and a column left mixed-parse outside that segment would be a corpus
whose meaning depends on which row you read. The slice is not all petitions,
though: it also carries the interim application dockets, which the live channel
writes a null count on purpose (an application is never distributed). Those and
every other null-count row are reported and left alone rather than filled —
the column's null is the parse-coverage sentinel for the whole live-signal
family, so filling the count on its own would promote an unknown CVSG to an
observed absence. ``backfill-live-signals`` owns that family, in one statement.

Every figure here is a **raw count of rows**, never denial-reweighted, because
they count writes rather than estimate a population — which is also why one of
them may not be read against a reweighted cert cut from the statpack.

**Band moves are reported over the census frame, not over the write frame**,
for the matching reason: a band label is only meaningful where the gate scores,
so banding an IFP or pre-modern row would report labels the gate never assigns.
The two counts are published side by side, each with its own unreadable
residue. One thing the sweep's matrix does *not* share with the census's: the
census bands two **readings of one snapshot** against each other, while this
sweep bands the **stored column** against the re-derived reading — so its
``from`` side carries whatever the max latch accumulated across pulls, which is
what the gate is really reading today. The two therefore need not agree cell
for cell; where the incumbent-parse control run reports ``changed = 0`` they
must, on the frame they share, and where it does not the difference is the
drift that control measures.

**A re-derivation is durable only as far as the ingest default is.** The live
channel re-polls pending petitions and open merits proceedings
(:func:`fedcourtsai.corpus.live_rotation`) and upserts a count read under
:data:`.cert_signals.DEFAULT_DISTRIBUTION_PARSE`; the max latch takes the
larger of stored and incoming, so a re-polled row's re-derived (lower) count is
re-latched back to the incumbent reading on its next poll — on exactly the rows
the parse moved, since those are the ones where the incumbent count is higher.
The standing poll is not the only channel that does it: ``refresh-dockets`` and
the Term walker's re-serve run **resolved** rows through the same upsert, so
the revert set is "whatever is re-served", not "whatever is pending".
``backfill-live-signals`` is the one that does not — it fills nulls and touches
nothing else. So the sweep converges the column, and the ingest default moving
to the same parse is what *keeps* it converged — one change in the same batch,
not two independent ones.

Ledger-side artifacts are **never** rewritten here. The column is the corpus's;
a frozen ``context.json`` records the count the cell actually saw, and a
committed prediction or evaluation is a record of a judgment made on that
input. Re-deriving the column moves the corpus forward without retconning
what any agent was handed — see :func:`rederive_distribution_counts`.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from . import caption, cert_signals, salience
from .prefetch import prefetch_by_case


class DistributionBandMove(BaseModel):
    """One cell of the sweep's band-move matrix: stored band → re-derived band."""

    model_config = ConfigDict(extra="forbid")

    from_band: str = Field(description="The band the **stored** column implies today")
    to_band: str = Field(description="The band the re-derived count implies")
    n: int = Field(ge=0, description="Cases making this move (diagonal cells are unmoved)")


class DistributionRederiveResult(BaseModel):
    """What one re-derive pass over the live slice wrote (or would write)."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(
        description="Whether the pass ran in apply mode (False = dry-run). Not the "
        "same as having written: pair it with `refused`, which is the apply that "
        "hit the bound and wrote nothing"
    )
    refused: bool = Field(
        default=False,
        description="Whether the blast-radius bound stopped the apply — nothing was written",
    )
    parse: str = Field(
        description="The registered distribution parse the counts were re-derived under"
    )
    salience_version: str = Field(
        description="The registered salience version whose band function keys the band-move matrix"
    )
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the pass read — the ledger of a "
        "latch-bypassing write, so what it names must be recoverable, and a figure "
        "quoted beside the census's is only comparable where both name one blob",
    )
    eligible: int = Field(
        ge=0,
        description="Live-slice SCOTUS rows walked — every row the column is "
        "populated on, plus the interim application dockets the live channel "
        "keeps deliberately null (reported under `no_stored_count`, never written)",
    )
    observable: int = Field(
        ge=0,
        description="Eligible rows whose latest live-shaped snapshot disclosed a proceedings list",
    )
    unobservable: int = Field(
        ge=0,
        description="Eligible rows with no live-shaped snapshot, or one disclosing no "
        "proceedings — counted and **left untouched**, never written to 0",
    )
    unchanged: int = Field(
        ge=0, description="Observable rows whose stored count already equals the re-derived one"
    )
    changed: int = Field(ge=0, description="Observable rows whose count this pass moves")
    decreased: int = Field(
        ge=0,
        description="Changed rows whose count falls — the expected direction under a "
        "narrower parse, and the direction the max latch would have silently eaten",
    )
    increased: int = Field(
        ge=0,
        description="Changed rows whose count rises — under a narrowing parse this is "
        "the stored column sitting *below* its own reading, not the parse's doing",
    )
    no_stored_count: int = Field(
        default=0,
        ge=0,
        description="Observable rows carrying **no** stored count — reported and "
        "left alone, not filled: the column's null is the parse-coverage "
        "sentinel for the whole live-signal family, so writing the count on its "
        "own would promote an unknown CVSG to an observed absence. "
        "`backfill-live-signals` owns them, and interim application dockets "
        "(deliberately null) sit here too",
    )
    scored_segment: int = Field(
        ge=0,
        description="Observable rows inside the census frame (paid, modern-cert, "
        "parseable Term) — the denominator the band-move matrix partitions",
    )
    scored_segment_unobservable: int = Field(
        default=0,
        ge=0,
        description="Census-frame rows that could not be read — the frame's own "
        "coverage residue, published so the band matrix is never mistaken for a "
        "cut over the whole frame",
    )
    scored_segment_no_stored_count: int = Field(
        default=0,
        ge=0,
        description="Census-frame rows readable but carrying no stored count, so "
        "they have no incumbent band to move from — the frame's second residue, "
        "published beside the first so its parts sum to the frame",
    )
    scored_segment_changed: int = Field(
        ge=0, description="Census-frame rows whose count this pass moves"
    )
    band_changed: int = Field(
        ge=0, description="Census-frame rows whose salience band label this pass moves"
    )
    band_moves: list[DistributionBandMove] = Field(
        default_factory=list,
        description="The full band-by-band square over the census frame, zero-filled — "
        "an omitted cell and an observed zero are different findings",
    )
    changed_case_ids: list[str] = Field(
        default_factory=list,
        description="Every changed case id, complete rather than sampled, in case_id order",
    )


def rederive_distribution_counts(
    conn: sqlite3.Connection,
    *,
    parse: str,
    apply: bool,
    corpus_sha256: str = "",
    max_changes: int | None = None,
    version: str | None = None,
) -> DistributionRederiveResult:
    """Recount every live-slice SCOTUS row's conference distributions under ``parse``.

    One pass **within an invocation**: the plan reported is exactly the write
    set, so a dry run and the apply inside one call cannot describe different
    work. Across two dispatches it is a reading, not a guarantee — the live
    channel re-polls between them — which is why the apply prints its own
    report as the record of what it actually did. For each row, the latest
    **live-shaped** snapshot
    (:func:`fedcourtsai.corpus.latest_live_snapshot` — split-aware, serving
    from the per-case content store under the corpus-split mode) is recounted
    by :func:`.cert_signals.snapshot_distribution_count` and the result written
    with :func:`fedcourtsai.corpus.set_distribution_count`, a **direct
    ``UPDATE`` that bypasses the upsert path's max latch** — see the module
    docstring for why that bypass is the sweep rather than a shortcut through
    it, and for what replaces the guard it steps around. The live-shaped
    restriction is the same one the census keeps: the entry-initial reading is
    a claim about the live channel's entry conventions, so counting a REST
    payload's ``docket_entries`` under it would write a channel artifact into
    the column.

    The reads ride
    :func:`~fedcourtsai.pipeline.prefetch.prefetch_by_case`, so a live slice in
    the tens of thousands costs a bounded fan-out rather than a serial walk of
    GET latency. ``parse`` is resolved before the walk, so an unregistered
    label raises on an empty corpus too rather than only where a snapshot
    happens to be readable.

    ``max_changes`` is the blast-radius bound and lives here rather than in the
    caller, so a code caller is bounded on the same terms as the command. Above
    it nothing is written and :attr:`DistributionRederiveResult.refused` comes
    back true. ``None`` is unbounded; a dry run never consults it either way,
    since it writes nothing.

    Idempotent: a second pass over an unchanged corpus recomputes the same
    counts, finds them already stored, and writes nothing.

    **Corpus-side only.** ``data/`` is never touched. A frozen
    ``record/context.json`` records the count the cell was actually handed and a
    committed ``prediction.json`` is a record of a judgment made on that input;
    rewriting either would retcon an agent's information set to match a reading
    it never saw. The column moves forward, the record of what was seen does
    not.
    """
    active = salience.scorer(version)
    # Resolved up front: a caller naming a parse this process cannot perform
    # wants the error before the walk, not after a full-population read.
    cert_signals.distribution_pattern(parse)
    moves: dict[tuple[str, str], int] = defaultdict(int)
    eligible = observable = unobservable = unchanged = 0
    increased = decreased = no_stored_count = 0
    scored_unobservable = scored_no_count = 0
    scored = scored_changed = band_changed = 0
    updates: list[tuple[str, int]] = []
    # Materialized before the prefetch, not walked beside it: `iter_rows` is a
    # lazily consumed cursor on `conn`, and stepping it while the prefetch's
    # workers read would put two readers on one connection. The rows are
    # metadata — the payloads stay in the prefetch's streamed window.
    rows = list(corpus.iter_rows(conn, court="scotus", live_slice=True))
    eligible = len(rows)
    # `latest_live_snapshot` never touches `conn` where payload reads are
    # offloaded (the registered source serves it, and its Protocol owes
    # tolerance of concurrent reads), which is what makes handing the call to
    # the pool's workers sound. The loop body runs on the calling thread either
    # way, so pooled and serial passes classify and order identically.
    with prefetch_by_case(
        [row.case_id for row in rows],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="distribution-rederive",
    ) as fetched:
        for row, (_, found) in zip(rows, fetched, strict=True):
            in_census_frame = (
                caption._scored_segment(row)
                and corpus.scotus_term_year(row.docket_number) is not None
            )
            # An **empty** proceedings list is degradation here, not a docket
            # with no entries: every live-polled SCOTUS docket carries at least
            # its docketing entry, so a payload disclosing none is a served
            # shell. `snapshot_carries_proceedings` alone would call that
            # observable and let a confident 0 through — the precise write the
            # max latch this sweep bypasses exists to reject — so the entry
            # list, not the key, is what decides observability.
            entries = cert_signals.proceedings_entries(found[1]) if found is not None else []
            recount = (
                cert_signals.snapshot_distribution_count(found[1], parse=parse)
                if found is not None and entries
                else None
            )
            if recount is None:
                # No live-shaped snapshot, or one disclosing no entries. The row
                # keeps whatever it carries and is counted: absence is not
                # agreement, and it is certainly not a count of zero.
                unobservable += 1
                scored_unobservable += int(in_census_frame)
                continue
            observable += 1
            if in_census_frame and (row.sample_weight or 1) != 1:
                # The same refusal the caption and distribution censuses keep:
                # every figure here is a raw count, and a denial-sampled row
                # would stand for ten in a matrix published beside theirs. The
                # *write* is per-row and indifferent to weight; the banded cut
                # is not, so the refusal is keyed on the census frame.
                raise ValueError(
                    f"{row.case_id}: sample_weight {row.sample_weight} — the band cut "
                    "counts raw and must not run over a subsampled census frame"
                )
            stored = row.distribution_count
            if stored is None:
                scored_no_count += int(in_census_frame)
                # The column's null is the **parse-coverage sentinel for the
                # whole live-signal family** (`corpus.CorpusRow`): a null count
                # is what makes a null `cvsg_date` read as "never parsed"
                # rather than "no CVSG". Filling the count alone would promote
                # an unknown CVSG to an observed absence, so these rows are
                # reported and left to `backfill-live-signals`, which fills the
                # family in one statement. Interim application dockets live
                # here too — the live channel writes them a null count on
                # purpose, an application never being distributed.
                no_stored_count += 1
                continue
            if stored == recount:
                unchanged += 1
            else:
                updates.append((row.case_id, recount))
                increased += int(recount > stored)
                decreased += int(recount < stored)
            # The band cut is the census's frame, not the write's: a band label
            # is a claim about a petition the gate scores, so an IFP or
            # pre-modern row is written without being banded.
            if not in_census_frame:
                continue
            scored += 1
            # One row, two counts: every other band input is held at the
            # corpus's own value, so the move isolates the re-derived column.
            before = active.band(row)
            after = active.band(row.model_copy(update={"distribution_count": recount}))
            # The same refusal the census keeps, for the same reason: a band
            # outside the version's declared vocabulary would drop the row out
            # of the square while the totals still counted it.
            salience._require_declared_bands(active, {before, after}, case_id=row.case_id)
            moves[(before, after)] += 1
            scored_changed += int(stored != recount)
            band_changed += int(before != after)
    result = DistributionRederiveResult(
        applied=apply,
        parse=parse,
        salience_version=active.version,
        corpus_sha256=corpus_sha256,
        eligible=eligible,
        observable=observable,
        unobservable=unobservable,
        unchanged=unchanged,
        changed=len(updates),
        decreased=decreased,
        increased=increased,
        no_stored_count=no_stored_count,
        scored_segment=scored,
        scored_segment_unobservable=scored_unobservable,
        scored_segment_no_stored_count=scored_no_count,
        scored_segment_changed=scored_changed,
        band_changed=band_changed,
        # The full square, zero-filled, for the reason the census publishes one:
        # an absent cell and an observed zero are different findings.
        band_moves=[
            DistributionBandMove(from_band=before, to_band=after, n=moves[(before, after)])
            for before in active.bands
            for after in active.bands
        ],
        changed_case_ids=[case_id for case_id, _ in updates],
    )
    if not apply:
        return result
    if max_changes is not None and len(updates) > max_changes:
        result.refused = True
        return result
    written = corpus.set_distribution_count(conn, updates)
    if written != len(updates):
        # The report is a claim about what the corpus now holds, so a write set
        # the statements did not land on is a report that lies. Louder than a
        # silently short pass, and unreachable in the writer lane's own single
        # transaction — which is the point: if it ever fires, the plan and the
        # store disagreed about which rows exist.
        raise RuntimeError(
            f"planned {len(updates)} distribution-count rewrite(s) but the UPDATE "
            f"touched {written} row(s) — the plan and the corpus disagree"
        )
    return result
