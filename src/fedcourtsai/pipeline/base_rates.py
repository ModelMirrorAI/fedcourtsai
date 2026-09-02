"""The baselines a forecast is scored against, and the scorer that uses them.

Every skill number in the project is scored against a base rate: the
strictly-prior pooled band rate a cert cell faced, the realized-Term rate its
ex-post complement is measured against, the historical disturbed rate a merits
cell is scored against, and the per-claim difference form that consumes any of
them. They are gathered here because the leaderboard and the claim scorer both
read them, and neither may reach through :mod:`fedcourtsai.pipeline.evaluate`
to do it: that module bands a corpus row, so it pulls the salience scorer
behind it, and the salience scorer reaches the store to mint events — a chain
that runs back into the very module the board is read from.

A leaf module by construction: it depends only on the shared schema, so no
consumer can form an import cycle around it.

:func:`realized_band_rate` is here but is deliberately **not** a cell's to
compute: it reads the Term the case is in, whose rate keeps moving until that
Term closes, so a value frozen onto an ``evaluation.json`` would say when the
cell was graded rather than what the Term did. It sits beside its
strictly-prior sibling because the two share a definition, and is called from
the leaderboard build over the current statpack instead.

This module reads no config. Every tunable — today, the pooling lookback window
— arrives as an argument, so the functions stay pure and a test, a replay cell,
and the cert back-test all get the same number from the same inputs. Config
resolves one level out, at the caller.
"""

from __future__ import annotations

from ..schemas import (
    CERT_ORDER_DISPOSITIONS,
    GRANTED_DISPOSITIONS,
    FeeClass,
    PredictionContext,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
)


def _version_segments(entry: StatPackTerm, band_version: str) -> list[StatPackTermSegment] | None:
    """One Term's band slices under ``band_version``, or ``None`` if it has none.

    ``None`` rather than an empty list: arithmetically the two are the same to
    the pool, since an empty list adds nothing to either accumulator, but they
    are different facts. ``None`` says the Term never carried this version at
    all, which is what a caller reasoning about coverage needs to be able to
    ask, and what keeps a future caller from reading an empty band list as a
    measured zero.
    """
    if entry.salience_version == band_version:
        return entry.segments
    for block in entry.alt_segments:
        if block.salience_version == band_version:
            return block.segments
    return None


def _pooled_band_rate(
    band: str,
    band_version: str,
    term: int,
    statpack: StatPack,
    *,
    lookback_terms: int,
    risk_set: bool,
) -> float | None:
    """One band's grant rate pooled over Terms strictly before ``term``.

    ``risk_set`` picks which of the two published rates is pooled, and the choice
    has to match how ``band`` was obtained — see the two callers,
    :func:`prediction_base_rate` here and
    :func:`fedcourtsai.pipeline.evaluate.segment_base_rate`. Pooled as a
    resolved-weighted mean of the per-Term rates, which equals aggregate weighted
    grants over aggregate weighted resolved, so a Term contributes at the weight
    belonging to the rate being pooled.

    ``band_version`` is the frozen salience version that produced ``band``, and
    the pool is **version-pinned**: only Terms whose ``salience_version`` matches
    contribute. A band name is meaningful only under the function that assigned
    it — a sal-v2 ``high`` and a sal-v1 ``high`` are different populations that
    happen to share a label, and pooling them would publish a number no version
    ever defined. When no Term carries the band's version the pool is empty and
    the result is ``None``, the already-contracted no-baseline answer — a
    lagging statpack reads as "no honest baseline yet", never as a silently
    blended one.
    """
    # A Term-YEAR floor, not a row count — see the callers' docstrings. `0` means no
    # floor; `term - 0` would exclude every Term, so the sentinel must short-circuit.
    # A negative window would read as unbounded-plus-a-Term; `ge=0` guards the config
    # path, and clamping here guards a direct caller.
    oldest = term - lookback_terms if lookback_terms > 0 else None
    weighted_grants = 0.0
    weighted_resolved = 0.0
    for entry in statpack.terms:
        # Version pin: a band name only means something under its own scorer, so
        # take that scorer's slices — the Term's own `segments` when it is the
        # active version, else the matching `alt_segments` block, else nothing.
        segments = _version_segments(entry, band_version)
        if segments is None:
            continue
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        for seg in segments:
            if seg.band != band:
                continue
            rate = seg.prefix_est_grant_rate if risk_set else seg.est_grant_rate
            denominator = seg.prefix_weighted_resolved if risk_set else seg.weighted_resolved
            if rate is not None:
                weighted_grants += rate * denominator
                weighted_resolved += denominator
    if weighted_resolved == 0:
        return None
    return weighted_grants / weighted_resolved


def prediction_base_rate(
    context: PredictionContext | None, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The band rate a cell actually faced, from its frozen conditioning.

    Pools ``prefix_est_grant_rate`` — the **risk-set** rate over every petition
    that ever *reached* the band, not only those that ended in it. That is the
    right rate precisely because ``context.band`` is the band as at prediction: a
    band only ever strengthens, so a cell sitting at ``baseline`` may still relist,
    and the population it belongs to is everyone who has reached ``baseline``.
    "Everyone" is the scorer's own reachable ladder, not the band order's prefix
    (:meth:`fedcourtsai.pipeline.salience.SalienceScorer.reachable_bands`): under a
    caption-banded version a federal petition is never in ``baseline``'s risk set,
    because its caption put it in ``federal`` at filing and no trajectory could
    have taken it there. The statpack builds the segments that way, so this pooler
    reads them as they come.

    The pairing is the whole point. Reading the risk-set rate against a *terminal*
    band would overstate the baseline for exactly the petitions whose band moved,
    and reading the terminal rate against a frozen band would understate it
    several-fold in the weak bands. Neither half is correct alone.

    ``None`` three ways, and the caller's answer is **not** the same in all
    three. Where there is no frozen context, or the snapshot disclosed no
    proceedings so no band could be derived, nothing is being conditioned on and
    the caller legitimately falls back to
    :func:`fedcourtsai.pipeline.evaluate.segment_base_rate` — the terminal band
    and the terminal rate, which at least agree with each other. Where a band
    *is* frozen but no prior Term carries it **under the version that assigned
    it**, there is no fallback: the answer is no baseline at all. Relabelling
    that cell terminal would pair a risk-set population with a terminal rate and
    stamp the live scorer's version onto a band an older one assigned, which is
    the mispairing this pairing exists to prevent (``docs/salience.md``). (The
    harness stamps ``salience_version`` whenever it derives a band, so a
    versionless band never arrives from a cell in the first place.)
    """
    if (
        context is None
        or context.band is None
        or context.term is None
        or context.salience_version is None
    ):
        return None
    return _pooled_band_rate(
        context.band,
        context.salience_version,
        context.term,
        statpack,
        lookback_terms=lookback_terms,
        risk_set=True,
    )


#: The smallest resolved sample a **realized-Term** band rate may rest on. It
#: binds twice, on the leave-one-out **weighted** denominator that scores the
#: case and on the **observed** row count behind it, because a Term walked under
#: denial sampling can carry a weighted 31 over some fourteen real petitions and
#: the standard error follows the rows. Below either, :func:`realized_band_rate`
#: returns ``None`` and the cell carries no realized-Term skill — a visible
#: omission (the aggregate's own ``*_scored`` count), never a zero folded into a
#: mean.
#:
#: Thirty, the figure :data:`MERITS_BASE_RATE_MIN_PARSED` states, for a sharper
#: version of the same reason. A rate over thirty observed rows carries a
#: standard error of at most ~0.09, and the skill ratio divides by
#: ``(rate - outcome)**2``, so noise in the rate lands on the denominator of
#: every cell in the band at once rather than averaging out across them. What
#: binds harder here than on the pooled prior-Term baseline is that this pool is
#: **one Term**: it cannot be widened by reaching further back, so a thin band
#: is not a sampling choice but a fact about how far the Term has got. The floor
#: is therefore a wait-for-the-Term rule — the trajectory bands clear it in
#: order, `high` partway through an October Term and the weaker ones almost at
#: once, while a band that never clears is omitted for that Term entirely. A
#: **caption class floor** is the case to watch: its risk set is that class
#: alone rather than every band above it, and the caption classes are the
#: docket's smallest populations, so `federal` and `state` are the bands a Term
#: most often omits — for a whole Term, not merely early in it. A stated
#: pre-registration choice, not a knob: only tests pass ``min_resolved``
#: anything else.
REALIZED_BAND_RATE_MIN_RESOLVED = 30


def realized_band_rate(
    band: str,
    band_version: str,
    term: int,
    statpack: StatPack,
    *,
    risk_set: bool,
    own_grant_family: int,
    min_resolved: int = REALIZED_BAND_RATE_MIN_RESOLVED,
) -> float | None:
    """One band's grant rate **in ``term`` itself**, leave-one-out for the scored case.

    The ex-post sibling of :func:`_pooled_band_rate`, and identical to it in
    every respect but one: it reads the case's **own** Term instead of every
    strictly-prior one. Same band, same version pin (a band name means something
    only under the scorer that assigned it), same ``risk_set`` pairing — a
    frozen-context band takes ``prefix_est_grant_rate``, a band derived from the
    row now takes ``est_grant_rate``.

    Because the level is held at the one that obtained, skill against this rate
    nets out level-knowledge and leaves **discrimination**: a predictor that has
    the Term's level right but cannot tell its cases apart scores positive
    against the prior-Term pool and ~0 here. It is **not** leakage-safe and no
    predictor could have known it in-season, so it never ranks and is never
    pooled or averaged with the prior-Term skill; ``metrics/README.md`` carries
    the claim contract.

    **Leave-one-out.** The scored case sits inside this rate, and in a thin band
    that bites — one case moves a band of seventy-odd by well over a point. The
    pack publishes no grant count, but the rate is a ratio of integer weighted
    counts, so ``rate * weighted_resolved`` rounds back to the numerator
    exactly; ``own_grant_family`` comes off it and one unit of weight off the
    denominator. The ``risk_set`` pairing is what makes that subtraction well
    defined: a band only ever strengthens, so a case frozen at a band ends at
    that band or a stronger one and is therefore in the band's **risk set**,
    while a case banded from the row now is in the band's **terminal**
    population. Against the wrong rate the case would be subtracted from a
    population it was never counted in.

    ``own_grant_family`` is 1 iff the case's disposition is in
    :data:`fedcourtsai.schemas.GRANT_FAMILY_DISPOSITIONS`, the numerator's own
    definition — **not** ``actual_granted``, which is the binary scoring target
    and additionally admits ``granted-in-part``. Subtracting the latter would
    remove a grant the published numerator never counted.

    **What the correction does to the scale**, exactly. Jackknifing moves the
    baseline away from the case's own outcome by a fixed factor, so
    ``skill = 1 - (1 - skill_uncorrected) * ((n - 1) / n)**2`` for a band of
    weighted ``n`` (exactly, wherever ``own_grant_family`` equals the case's
    ``actual_granted``, i.e. everywhere but a ``granted-in-part`` cert
    disposition). Two readings follow. It is monotone in the uncorrected score,
    so it never reorders cells within a band. And the attainable level-only
    null is **not** 0 but ``(2n - 1) / n**2`` — the score of a forecaster
    reporting the band's *published* rate, which contains its own case: about
    +0.03 at n = 72 and about +0.06 at the floor of n = 31. (A forecaster
    reporting the leave-one-out level itself would score exactly 0, but that
    level is ``(g - y) / (n - 1)``, so reporting it requires knowing the
    outcome — an oracle, not a null.) Read "~0" as that bound. Note the shift
    itself, ``(1 - skill_uncorrected) * (2n - 1) / n**2``, is bounded only at
    the null: Brier skill has no lower bound, so a badly negative cell shifts
    much further.

    Three bounded approximations, stated rather than corrected. The subtraction
    removes one unit of weight rather than the row's own ``sample_weight``,
    which the pack does not publish per row; the two coincide on a Term walked
    at weight 1 — every live Term, so every forward cell — while on a
    reweighted historical Term, where the retrospective cells sit, the
    correction falls short of a sampled denial's full weight. The case is
    assumed to be a row of the segment's population (the Term's live-slice paid
    modern-cert petitions), which the salience gate makes true of every cell it
    provisions but which an IFP or off-slice row would break — as would a caption
    re-parse that moved the row between petition classes after its band was
    frozen, since a risk set is the class's own ladder. And the pack is a
    **vintage**: a case resolved after it was built is not yet in its own Term's
    counts, so the subtraction over-corrects by one unit until the next refresh
    — bounded by ``1 / min_resolved`` and self-correcting as the Term closes.

    ``None`` when the Term carries no segment for the band under that version,
    when the band holds a single resolved row (leaving it out leaves nothing),
    when either leave-one-out sample is below ``min_resolved``, or when the
    subtraction lands outside ``[0, loo_weighted]`` — which cannot happen for a
    case the counts contain, so it is proof that this vintage does not contain
    it and the honest answer is no baseline rather than a clamped certainty.
    """
    for entry in statpack.terms:
        # Version pin, resolved the same way the pooler resolves it — including
        # through `alt_segments`. An asymmetry here would drop the realized-Term
        # skill of every cell frozen at a non-active version while leaving its
        # prior-Term skill standing, so the board would print two skill columns
        # over two different populations, split on a version label rather than
        # on the resolved-count floor that is this field's only stated omission.
        segments = _version_segments(entry, band_version)
        if segments is None:
            continue
        if entry.term != term:
            continue  # the case's OWN Term, and only it — the whole difference from the pooler
        for seg in segments:
            if seg.band != band:
                continue
            rate = seg.prefix_est_grant_rate if risk_set else seg.est_grant_rate
            weighted = seg.prefix_weighted_resolved if risk_set else seg.weighted_resolved
            observed = seg.prefix_resolved if risk_set else seg.resolved
            if rate is None:
                continue
            loo_weighted = weighted - 1
            if loo_weighted <= 0:
                return None  # a single resolved row: leaving it out leaves no band at all
            if loo_weighted < min_resolved or observed - 1 < min_resolved:
                return None
            loo_grants = round(rate * weighted) - own_grant_family
            if not 0 <= loo_grants <= loo_weighted:
                return None  # the case is not in this vintage's counts; invent nothing
            return loo_grants / loo_weighted
    return None


#: The smallest parsed sample a merits baseline may rest on. Below it the
#: pooled rate is ``None`` (claim unscored, no skill score) rather than
#: published: ``docs/outcome-decomposition.md`` requires a stated minimum
#: observation count of any thin-history baseline before it ships, and the
#: merits section exists from its very first parsed judgment — so without a
#: floor a one-row prior Term would hand out a degenerate 0.0/1.0 baseline. In
#: `claim_score`'s difference form — the consumer today — such a baseline
#: produces a score of magnitude ~1 that swamps every other claim in a total;
#: and `pipeline.evaluate.brier_skill`, the consumer once merits cells fan out,
#: masks exactly the
#: cells such a baseline got *right* (its Brier is 0 there), leaving a
#: published mean taken only over the ones it got wrong.
#: At a rate near 0.7 this bounds the standard error around 0.08, and the Court
#: decides roughly sixty argued cases a Term. The pool takes whole Terms
#: strictly prior, so within-Term accumulation never counts toward a case's own
#: baseline: the floor clears on one prior grant Term of parsed judgments, or
#: two thin ones. A stated pre-registration choice, not a knob.
MERITS_BASE_RATE_MIN_PARSED = 30


def merits_base_rate(
    grant_term: int, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The historical disturbed rate a merits cell's skill is scored against.

    Pools the statpack merits section's per-grant-Term counts — ``parsed`` and
    ``disturbed`` — over Terms **strictly before** ``grant_term``, as aggregate
    disturbed over aggregate parsed. The merits sibling of
    :func:`fedcourtsai.pipeline.evaluate.segment_base_rate`, under the identical
    leakage rule, but deliberately **version-free**: the section is not a
    salience-band product, so there is no scorer version to pin
    (``docs/decision-model.md`` pre-registers this baseline).

    **The baseline's population is the scored population.** The merits section
    admits exactly the grants that open a merits proceeding
    (:func:`fedcourtsai.corpus.opens_merits_proceeding`), which is where a
    merits cell comes from — further guarded, label-independently, against
    parsed judgments dated on or before their own grant, the
    pre-convention cert-order class (``docs/decision-model.md``): a GVR and a
    summary reversal terminate at the cert
    order and never mint one, so their near-certain vacaturs — a cert-stage
    fact the cert sections already carry — never anchor a merits forecast to a
    rate its own population does not face, whatever the row's label says. An
    *undated* parse is untestable rather than guarded: it stays in the
    section's ``granted`` cohort as a coverage gap, outside the ``parsed``
    slice this rate divides.

    ``grant_term`` is the October Term certiorari was **granted** in
    (:func:`fedcourtsai.pipeline.judgment.grant_term_year` over the merits
    event's ``opened_at``), the axis the statpack merits section is keyed on.
    It must not be substituted with the docket-number Term: the two disagree
    for a petition docketed into the incoming Term and granted before that Term
    opens, and there the docket Term is one *later* than the grant Term, which
    would admit the case's own cohort into its own baseline. Keying both on the
    grant Term also keeps cohort-mates comparable — two cases granted in the
    same Term are scored against the same pool.

    ``lookback_terms`` bounds the pool as a Term-year band exactly as
    :func:`fedcourtsai.pipeline.evaluate.segment_base_rate` does (``0`` =
    unbounded). ``None`` when the pack
    carries no merits section, when no prior Term has a parsed judgment, when
    any Term **inside the pooled window** carries a null
    ``cert_order_excluded`` — a build
    :func:`fedcourtsai.pipeline.judgment.judgment_rode_the_grant_order` never
    ran on, whose parsed counts may still contain the cert-order class the
    rate must exclude (``metrics/README.md`` rules such a section unquotable;
    this makes the rule structural for every consumer, the recorded
    ``segment_base_rate`` included — ``stamp-cell`` stamps a merits cell's from
    this function, so a section the guard refuses leaves the field null rather
    than resting on an evaluator honouring an omit rule) — or
    when the pooled sample is below :data:`MERITS_BASE_RATE_MIN_PARSED` — the
    already-contracted no-baseline answer, never an invented or degenerate rate.
    """
    if statpack.merits is None:
        return None
    oldest = grant_term - lookback_terms if lookback_terms > 0 else None
    disturbed = 0
    parsed = 0
    for entry in statpack.merits.terms:
        if entry.term >= grant_term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        if entry.cert_order_excluded is None:
            # Null marks a build the cert-order pool guard never ran on, so
            # this Term's parsed counts may include the class the rate must
            # exclude — no honest baseline pools from it.
            return None
        disturbed += entry.disturbed
        parsed += entry.parsed
    if parsed < MERITS_BASE_RATE_MIN_PARSED:
        return None
    return disturbed / parsed


#: The smallest strictly-prior grant sample the summary-route baseline may rest
#: on, and the same figure — and the same reasoning — as
#: :data:`MERITS_BASE_RATE_MIN_PARSED`: a rate near 0.35 over thirty grants
#: carries a standard error of about 0.09, and a degenerate rate off one or two
#: prior grants would dominate a claim total in ``claim_score``'s difference
#: form. It clears on a single prior Term of paid live-slice grants (the paid
#: grant family runs some ninety a Term), so it binds only at the very start of
#: a corpus's history. Like the merits floor it states the count and **defers
#: the smoothing rule**, which is the standing debt on it: at the floor the
#: unpriced baseline-estimation expectation is ``p(1-p)/n ~ 0.008`` per claim,
#: the same order as the drift term ``docs/outcome-decomposition.md`` already
#: calls dominant. A stated pre-registration choice, not a knob.
SUMMARY_ROUTE_BASE_RATE_MIN_GRANTS = 30

#: The fee class the salience gate actually predicts on. IFP petitions are
#: Tier-0-excluded (``docs/salience.md``), so they are never a scored cell — and
#: they are 28% of the pack's pooled grant family at roughly three-quarters GVR,
#: so pooling them would price a population no cell belongs to.
_SCORED_FEE_CLASS = FeeClass.paid


def summary_route_base_rate(
    term: int, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The rate at which a grant disposed in the cert order, over prior Terms.

    The baseline for the declared cert-stage summary-route claim: pooled
    ``CERT_ORDER_DISPOSITIONS`` count over pooled ``GRANTED_DISPOSITIONS`` count,
    taken over Terms **strictly before** ``term`` — the same leakage rule
    :func:`_pooled_band_rate` and :func:`merits_base_rate` apply, with the same
    ``lookback_terms`` Term-year band (``0`` = unbounded).

    **The population is the scored population**, which is why the counts come
    from each Term's **paid** :class:`~fedcourtsai.schemas.StatPackTermClass`
    rather than from the Term-level ``base_rates.dispositions``. IFP petitions
    are Tier-0-excluded by the salience gate, so no cell is ever an IFP row —
    yet they supply nearly a third of the pack's pooled grant family at
    roughly three-quarters GVR, so the all-class rate runs about eleven points
    above the paid one. Against a difference-form rule that is not a rounding
    error: a predictor knowing only the paid segment's own rate would bank
    ``(b_all - b_paid)^2 ~ 0.012`` per scored claim, which the identically-zero
    floor cannot price. The band cut is *not* needed for the same reason it
    would be harmless — the cert-order share is flat across the salience bands —
    so the fee class is the whole of the population gap.

    Reading the class blocks is also a **coverage** cut, not only a population
    one: the two classes do not sum to the Term-level total (1,125 against 1,158
    on the committed pack), so a row the census places in neither stream is
    dropped rather than pooled. Dropping it is the conservative direction — the
    scored population is exactly the paid stream — but it means this denominator
    is a subset of the Term's published grant family, and the floor below is
    measured against the subset.

    Reading the fee-class cut also sidesteps the ``gvr`` label's
    forward-convention hazard, which the Term-level split carries and
    :class:`~fedcourtsai.schemas.StatPackTerm` warns is "meaningless between"
    Terms: the un-relabelled Terms sit entirely in the IFP class, whose
    cert-order count drops to zero where its neighbours run near 0.9, while the
    paid series stays inside a 0.29-0.46 band throughout.

    **Conditioned on the grant, deliberately.** The unconditional summary rate
    over all petitions is around one percent, close enough to the boundary that
    a season's realized total would be one Bernoulli draw
    (``docs/outcome-decomposition.md``, the eight tests' volume condition). The
    claim's resolver masks every denial, so its population is the grant family
    and its baseline has to be the same population — a denominator of all
    resolved petitions would be a baseline conditioned differently from the
    claim.

    **The published counts are denial-reweighted, and here that is harmless.**
    Only denials were ever subsampled, so every row inside the grant family
    carries weight 1 and this ratio is an unweighted count of grants either way.

    **One residual bias remains, and it is not a safety margin.** A summary
    reversal is a cert-order disposition that no resolver mints — the
    ``summary-reversal`` label has none — so such an order sits in the
    ``granted`` bucket and counts in the denominator but not the numerator,
    pushing the rate down by an amount nothing the pack publishes bounds. Note
    what that does and does not buy: under this project's difference-form rule a
    baseline that is wrong in *either* direction hands a predictor reporting the
    true rate ``(pi - b)^2`` for free, and the floor prices none of it. A
    downward-biased baseline is therefore not "conservative"; it is unearned
    score, and the cut that would retire it is exactly the one
    ``Outcome.disposition_route`` exists to build.

    ``None`` when no strictly-prior Term carries a paid class, or when the
    pooled grant sample is below :data:`SUMMARY_ROUTE_BASE_RATE_MIN_GRANTS` —
    the already-contracted no-baseline answer, never an invented or degenerate
    rate.
    """
    oldest = term - lookback_terms if lookback_terms > 0 else None
    cert_order = 0
    grants = 0
    for entry in statpack.terms:
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        for klass in entry.classes:
            if klass.fee_class != _SCORED_FEE_CLASS:
                continue
            for share in klass.dispositions:
                if share.disposition not in GRANTED_DISPOSITIONS:
                    continue
                grants += share.count
                if share.disposition in CERT_ORDER_DISPOSITIONS:
                    cert_order += share.count
    if grants < SUMMARY_ROUTE_BASE_RATE_MIN_GRANTS:
        return None
    return cert_order / grants


#: The smallest pooled resolved sample an **interim** baseline may rest on.
#: Below it :func:`interim_base_rate` is ``None`` — no baseline, and no
#: substitute: not the pack-level rate (it contains the case's own Term), not a
#: single Term's, not the cert band table (a different population on a different
#: standard).
#:
#: Fifty rather than the thirty its cert and merits siblings use. Thirty rests
#: on an absolute
#: standard-error argument, which is tolerable where the baseline enters as a
#: *difference* (``claim_score``'s ``(b - y)^2 - (p - y)^2``) or as the
#: denominator of a ratio at a rate near one half. Neither holds here. This
#: baseline's principal consumer is
#: :func:`fedcourtsai.pipeline.evaluate.brier_skill`, whose denominator is
#: ``(b - y)^2``; the modal interim outcome is a denial, so on most cells that
#: denominator is ``b^2``. Squaring **doubles** the relative error transmitted
#: from the rate, and — unlike per-cell noise — it lands on every cell's
#: denominator at once, so it biases the published mean rather than averaging
#: out of it.
#:
#: Holding the transmitted relative error at or under one third therefore needs
#: ``n >= 36(1 - p) / p``: 36 at ``p = 0.5``, 84 at ``p = 0.3``, and unbounded as
#: ``p`` falls. **The criterion cannot pin a number**, and 50 is not claimed to
#: satisfy it: it is monotone decreasing in ``p`` and unbounded, so at the rates
#: this docket has actually shown it asks for roughly 231 resolutions at the
#: pooled 13.5% and roughly 364 at a single Term's 9%. 50 clears it only for
#: ``p`` above about 0.42. What the criterion does establish is that **thirty is
#: too low here**, and what 50 buys is stated exactly: an absolute standard
#: error of at most 0.071, inside the bound the siblings accept at thirty
#: (0.091). So the figure is chosen on the siblings' own absolute-SE standard at
#: a tighter tolerance, with the relative-error argument as the reason for
#: tightening rather than as a bound it meets.
#:
#: The floor binds on the **pooled** strictly-prior sample, so it clears by
#: accumulation exactly as :data:`MERITS_BASE_RATE_MIN_PARSED` does. Its effect
#: today is that no single-Term pool qualifies, and that effect is accepted
#: rather than incidental: 50 was chosen with the committed pack visible, and
#: the criterion's own value at ``p = 0.5`` (36) would have admitted the one
#: single-Term pool that exists. What is *not* registered is an "at least two
#: Terms" companion condition — considered and rejected, because a second
#: parameter with no derivation behind it, chosen in knowledge of which cells it
#: would exclude, is a forking path however reasonable it sounds. A stated
#: pre-registration choice, not a knob (``docs/salience.md``, *The interim
#: docket*).
INTERIM_BASE_RATE_MIN_RESOLVED = 50


def interim_base_rate(
    application_term: int, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The historical grant rate an interim cell's skill is scored against.

    Pools the statpack interim section's per-application-Term counts —
    ``substantive_resolved`` and ``substantive_granted`` — over Terms **strictly
    before** ``application_term``, as aggregate granted over aggregate resolved.
    The interim sibling of :func:`fedcourtsai.pipeline.evaluate.segment_base_rate`
    and of :func:`merits_base_rate`, under the identical leakage rule, and
    deliberately **version-free** for the same reason the merits rate is: the
    interim section is not a salience-band product (an application freezes no
    band by rule), so there is no scorer version to pin.

    **The baseline's population is wider than the scored population, and the gap
    is registered rather than corrected.** The section pools the *substantive*
    slice alone — a stay, an injunction, a vacatur — and the administrative
    extension majority is counted in the section but never in a rate, because an
    extension is granted as a matter of course and would hand the baseline the
    Court's calendar rather than its judgment. But the substantive slice is not
    the *scored* set: the interim reserve fills its bounded slots in escalation
    ladder order (a requested response first, then the amicus count —
    ``pipeline.salience``), so a predicted application sits systematically higher
    on those rungs than the pooled cohort behind this rate. The rate is
    unconditioned on the ladder while the scored cells are selected on it, which
    is the register's own test 3 answered in the negative
    (``docs/outcome-decomposition.md``). Two consequences travel with the number:
    a positive interim skill against it is *not* by itself evidence of forecast
    skill, and the conditioned rate the claim would need is not derivable from
    any committed cut, because the pack publishes no ladder-by-grant cross-tab.
    Conditioning the pool on the frozen rung is the registered next step, and it
    is a new estimator applied forward, never a silent re-reading of this one.

    Two further selections are properties of the pooled counts themselves.
    Resolution is machine-matched, so the denominator is selected for
    machine-matchable resolution text. And parse coverage is not uniform across
    application-Terms — the live poller reaches recently-active applications, so
    a Term it reached late contributes a subsample rather than a census, and a
    pooled rate blends Terms of different coverage. Both belong beside any quoted
    figure.

    ``application_term`` is the October Term the application was docketed in
    (:func:`fedcourtsai.corpus.scotus_application_term_year` over the ``YYAnnn``
    docket number), which is the axis the interim section is keyed on. It is
    read from the docket number rather than from a date, so it needs no
    resolution clock and cohort-mates are scored against the same pool.

    ``lookback_terms`` bounds the pool as a Term-year band exactly as the two
    siblings do (``0`` = unbounded). The window is the caller's — the shipped
    value is the cert baseline's ``salience.base_rate_lookback_terms``, applied
    here unchanged, which is a stated choice and not a separate registration.
    ``None`` when the pack carries no interim
    section, when no prior Term resolved anything substantive, or when the pooled
    sample is below :data:`INTERIM_BASE_RATE_MIN_RESOLVED` — the already-contracted
    no-baseline answer, never an invented or degenerate rate. Two label collapses
    ride the number wherever it is quoted, both pre-registered in
    ``docs/salience.md``: withdrawn and dismissed resolutions count as ungranted,
    and a mixed partial disposition reads denial-first.

    No pool-integrity guard corresponds to :func:`merits_base_rate`'s
    ``cert_order_excluded`` refusal, and none is missing: that guard exists
    because a merits Term's parsed counts can silently contain a class the rate
    must exclude, whereas the interim section carries no column whose absence
    could contaminate a Term's counts the same way.
    """
    if statpack.interim is None:
        return None
    oldest = application_term - lookback_terms if lookback_terms > 0 else None
    granted = 0
    resolved = 0
    for entry in statpack.interim.terms:
        if entry.term >= application_term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        granted += entry.substantive_granted
        resolved += entry.substantive_resolved
    if resolved < INTERIM_BASE_RATE_MIN_RESOLVED:
        return None
    return granted / resolved


def claim_score(p: float, y: int, b: float) -> float:
    """One claim's score: the baseline's Brier minus the forecast's.

    ``(b - y)**2 - (p - y)**2``, for predicted probability ``p``, realized outcome
    ``y`` in {0, 1}, and harness-computed baseline ``b``. Positive when the forecast
    landed closer to the outcome than the baseline did, negative when a bold call
    missed.

    **Proper.** For a fixed ``b`` the score differs from ``-(p - y)**2`` by a term
    that depends on ``b`` and ``y`` but not on ``p``, so nothing done to ``p`` can
    move it; expected score is therefore maximized by reporting the probability
    actually held. (Not an affine transform in the usual sense — the added term
    varies with ``y`` — but the ``p``-independence is what propriety needs, and it is
    exact.)

    **Restating the baseline is worth nothing.** At ``p == b`` the score is
    identically 0 for *either* outcome, realized and not merely in expectation.

    The difference form rather than
    :func:`fedcourtsai.pipeline.evaluate.brier_skill`'s ratio, because per-claim
    scores are summed and a ratio does not compose — and because the ratio explodes
    near the endpoints where these baselines live.
    """
    return (b - y) ** 2 - (p - y) ** 2
