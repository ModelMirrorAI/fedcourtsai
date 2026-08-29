# Salience: which cases we predict, and the scores we pre-register

The design contract for **salience-ordered prediction scope** — the gate that
decides *which* eligible cert petitions are worth the expensive three-engine
tournament — and for the two **pre-registered scores** the program commits before
a term plays out: the deterministic **salience score** (which cases to forecast,
ranked) and the model-produced **big-case score** (how big we called them). For
the ingestion/prediction scope split this refines see the *Scope* section of
[data-pipeline.md](data-pipeline.md); for the cost argument it hangs on see
[budget.md](budget.md); for where the board lands on the roadmap see
[milestones.md](milestones.md).

This doc fixes the vocabulary and the seams and describes the gate as it runs;
its knobs are the `salience:` block of `config/tracking.yaml`. Where a piece is
still ahead of the implementation, it says so in place.

**One predicted stream sits outside this gate entirely.** A cert grant opens a
merits event, and that event is forecastable on its own terms — no salience
score, no rank, and no reserve, because the case was already selected once as a
petition and the grant cohort is self-limiting at the Court's own volume. The
gate below governs which *petitions* and which *applications* earn cells; the
merits cell rides the grant. Its cost is priced in [budget.md](budget.md) and
its scoring contract in [decision-model.md](decision-model.md).

## Why salience

The agentic stages cost one to two orders of magnitude more than ingestion, so
running the tournament over the whole cert denominator would spend that budget
on thousands of petitions denied as a matter of course. Prediction scope is
therefore **salience-ordered**: the hard eligibility filters run first, then a
cheap deterministic score **ranks** the surviving petitions and the
predict/evaluate tournament runs only on the most salient slice, up to a
fundable **capacity `N`**.

The gate is live. The selection pass runs inside every live-channel cycle, its
decision is carried by the `salience_selected` corpus latch, and both the
predict matrix and the pull queue read that latch (*Selection* below).

Two scores fall out, and they are deliberately distinct:

- The **salience score** is *deterministic and pre-conference* — the pipeline's own
  cheap opinion of which petitions are worth forecasting, computed from features
  already in the corpus, published as a ranking before the conference sits.
- The **big-case score** is *model-produced and pre-registered* — each predictor's
  opinion of a case's stakes, committed with the grant/deny forecast and judged
  later by an independent evaluator rather than against a ground truth. It is a
  direct answer to the "bigness is only ever assigned in hindsight" critique: the
  git timestamp proves the stakes call preceded the term.

## The three tiers

Selection is a funnel, cheap filters first:

- **Tier 0 — hard eligibility (deterministic, at the row).**
  `corpus.OUT_OF_SCOPE_RULES`, evaluated through `out_of_scope_reason_full`,
  including the rule excluding **pro se / in-forma-pauperis** petitions. Fee
  class is derivable — IFP serials start at `IFP_SERIAL_BASE` (`5001`) in the
  SCOTUS docket number (`supremecourt.parse_scotus_docket_number`), so the rule
  is a row-only predicate needing no new column. This is a **documented scope
  decision** — a named rule in `OUT_OF_SCOPE_RULES` carrying its own reason
  string, not a silent drop: IFP grants are rare but non-zero (Gideon arrived
  IFP), so excluding them is a deliberate, recorded choice, not a claim that
  IFP cases never matter. A Tier-0 exclusion means *never predict, and prune any
  prediction already committed* — the same destructive-on-purpose semantics
  every hard-scope rule already carries.
- **Tier 1 — salience scoring (cheap, over all eligible).** A deterministic score
  over every Tier-0 survivor, from features the corpus already carries. This is a
  *scoring* pass, **not** a cheap *prediction* of every case — the whole point is to
  avoid spending tournament budget on the denominator.
- **Tier 2 — the tournament (expensive, over the salient slice).** The existing
  three-engine, cross-evaluated predict/evaluate, unchanged, run only on the
  selected cases. This is where the big-case score is produced and where the
  segment base rate (below) becomes the agent's prior and the evaluator's baseline.

## The salience score

A **frozen, versioned** function — `SALIENCE_VERSION` names the active one in
code (`pipeline.salience`), first release `sal-v1` — a
weighted combination of Tier-1 features. It is reproducible from committed corpus
inputs; a scoring-function change is a **new version**, never an in-place edit, so
a skeptic can replay any past ranking against the version that produced it.

`sal-v1`'s weights are **fit to the empirical per-bucket grant rates**, not
hand-tuned: a case's score approximates `P(grant | its relist / CVSG / circuit
cell)` read off the committed statpack, so the ranking is directly
interpretable — a higher score means a historically higher grant rate for cases
like this — and calibrated to reality rather than to arbitrary coefficients. The
exact coefficients are pinned and documented in the implementing change against
the statpack numbers in force.

`sal-v1` uses only features that exist today and are available **pre-conference**:

- **Relist count** — `distribution_count − 1`, floored at 0 (a petition
  distributed once has not been relisted). The strongest cheap signal: the tier
  rates the constants were fitted to run from ~0.8% at relist-0 to ~39.4% at
  relist-2+, a ~50× spread. Those constants are **frozen at their fitted
  values**, and the spread the corpus actually carries is smaller — 19.7×
  granted-only, 21.4× on the grant family, under `dist-v2`. See *The relist
  tiers, re-measured* below, the standing mis-fit finding rather than a
  correction. `NULL` `distribution_count` (never live-parsed) scores as unknown, not 0.
- **CVSG present** — `cvsg_date IS NOT NULL`. A Call for the Views of the Solicitor
  General is the Court's own signal of stakes; CVSG petitions grant ~28% vs ~3%
  without.
- **Originating circuit** — `originating_court`. Circuits vary in grant rate; a
  documented per-circuit weight.

Fee class (paid vs IFP) deliberately does **not** enter the score: IFP petitions
are Tier-0-excluded, leaving the scored set paid-only.

Deferred, each with a stated reason:

- **Below-decision division** (a dissent or en-banc split in the court below) is a
  strong salience signal but is **not recoverable** from the corpus today — no
  column, and not cheaply derivable from stored text. A later-version feature
  once the below-court signal is extracted.
- **Amicus-brief count** is arguably the strongest pre-decision salience proxy,
  and it is **readable**: `pipeline.interim_signals.amicus_briefs` counts the
  docket entries naming amicus or amici curiae, and the as-of projection counts
  them on a cert docket too (`pipeline.asof`). What is deferred is the rest of
  the feature — the persisted `amicus_briefs` column is the live application
  branch's alone, so no cert-branch count is stored, and no weight for one has
  been fitted. A later-version enrichment; neither shipped scorer depends on
  it.
- **Cheap-model QP enrichment** — an optional model pass over the questions
  presented to sharpen the deterministic score — is **default off** for the first
  release, so `sal-v1` is fully deterministic and free.

### `sal-v2`: two cohorts, never pooled

`sal-v1`'s features are docket-acquired — relists and CVSG accumulate over a
petition's life — so at arrival every observable petition scores `baseline` and the gate
is structurally inert at the one moment a truly prospective selection would
have to act: no cohort forms, no band stratifies, recall over realized grants
is zero by construction (the gate replay measures exactly this). `sal-v2`
opens that moment — at the draw rate plus one measured class, not full
coverage — with **two cohorts, never pooled**:

- **The arrival cohort** — selected at docketing by two named rules (the
  active carve-out predicate also applies there, but no trajectory score can
  clear the floor at zero distributions, so in effect the two rules are the
  cohort): a **random slice** (a keyed-hash draw over the case id under a
  registration-fixed key — the literal inside `pipeline.salience.arrival_draw`,
  deliberately not `SALIENCE_VERSION` — at
  `salience.arrival_sample_rate: 0.05`, effectively frozen once the cohort
  runs) plus the **federal-petitioner carve-in** below. The cohort begins at
  the registration-fixed `ARRIVAL_COHORT_SINCE` (the OT2026 docket-year roll)
  and fills forward: a case filed earlier — including the standing
  never-resolved backlog whose distribution count was simply never parsed —
  is not at its arrival moment and never enters this cohort, though it still
  earns escalation selection as signals accrue. Moving that bound changes the
  arrival population and is a new pre-registered population, never a quiet
  widening. The two rules select
  populations with grant rates an order of magnitude apart, so they report
  separately, always: the **random-slice subcohort's** baseline is exactly the
  unconditional paid-arrival grant rate, no selection rule can game it, and it
  alone is the subcohort whose skill numbers transfer to live prospective use;
  the **carve-in subcohort** is a selected class with its own baseline, and
  any figure pooling the two (the leaderboard's `cert@arrival` block pools
  them mechanically) is not claimable without the per-rule cut
  (`metrics/README.md`).
- **The escalation cohort** — re-selected as relist / CVSG / response signals
  accumulate: `sal-v1`'s scoring, carried into `sal-v2` unchanged, which
  remains the right way to
  spend tournament budget on cases that have become interesting. It reports
  against its own risk-set baselines and never against — or blended with —
  the arrival cohort's.

**The caption class is the arrival feature's committed form.** The
petitioner's caption is the one party signal fixed at filing, and
`pipeline.caption` holds the registered rules: federal / state / private, read
from the structured `petitioner_title` column (else the caption's pre-` v. `
half), with the fixtures as the specification. Their census
(`fedcourts caption-census`) is the artifact any caption-keyed **selection**
constant must be frozen from — and only from a statistically reviewed run of
it under the rule version it names. That review of record has run for
`caption-v1`: the **federal carve-in predicate** (`classify_petitioner ==
"federal"` — the predicate, deliberately not the concept "government
petitioner", whose recall gap `caption-v2` below is what answers) is frozen
into `sal-v2` on a verified census replicating in all eight complete Terms
(OT2017–OT2024, lift 8.1–16.4×, intervals fully separated; OT2025 is
right-censored and counted as supportive, never held-out). The **state**
class never enters selection — per-Term unstable, its below-cap
slice underperforming the arrival population — though it is a *band* under
the caption-banded versions (placed above `elevated` from the class
marginal, and the band's own realized rate, net of its strongest members
leaving for `high`, does not settle that placement). Four Terms clear the
30-row realized floor — OT2017 n=33, OT2019 n=37, OT2020 n=33, OT2021 n=46 —
and what decides nothing is not the spread alone but the **sign flip** inside
it: state lands *below* `elevated`'s terminal rate in two of the four (6.1% vs
8.5%, 8.1% vs 10.6%) and above it in the other two (30.3% vs 11.4%, 23.9% vs
11.5%). Pooled over those same four Terms state runs 17.5% (26/149) against
`elevated`'s 10.5% (116/1107), which would weakly support the registered
placement — but the four were selected on sample size out of nine, and the
floor is a *per-Term* rule, so that pooled cut is a post-hoc read the
registration does not authorize and it is not claimed. The ordering rests on
the registration, frozen per version, rather than on a measurement. The gate replay still
cannot validate any caption feature, because the replay's reconstruction
carries the terminal caption: a declared gap, never papered over with a
replay number.

**`caption-v2` is the widened read, registered beside `caption-v1`, never over
it.** `caption-v1`'s census verification measured a federal recall gap:
genuinely federal petitioners its patterns classify `private`, in five shapes —
the `Office of the United States <office>` word order and the United States
Trustee; agencies and offices whose caption name leads with neither `United
States` nor `Federal`; the spelled-out form of an agency v1 carries only as an
initialism; the military departments as an officer's qualifier and the
deputy / under / assistant ranks of a federal office; and the sovereign behind
an `In re` caption. `caption-v2` reads those shapes, keeping v1's three
classes, its role-suffix stripping, and qui tam's precedence over every federal
read — the `In re` prefix reaching the relator pattern as well as the
sovereign's. Both rules are registered predicates in
`pipeline.caption.CAPTION_RULES`, and `fedcourts caption-census
--rule-version` cuts the same frame under either, so a widening is reviewable
as a per-class, per-Term delta rather than as an unlabeled re-run. It is
one-directional **by construction**, because `caption-v2` runs `caption-v1`
first and keeps any non-`private` answer: no caption can lose a `federal` or
`state` read it had under v1, so the delta is drawn from the `private` cell
only, which is what makes the two censuses comparable cell by cell. A caption
rule reaches **selection** only through a salience version that names it,
because a frozen constant names the predicate it was frozen from: `caption-v1`
through `sal-v2`, `caption-v2` through `sal-v3` and `sal-v4`.

A caption-banded version's activation sequences deliberately: the promotion
carrying the flip, then a metrics refresh, then prediction. A cell minted
under a version before that version's first refreshed statpack has **no
published baseline** — the version-pinned pool's designed `None`, never a
blend — so its skill column is legitimately empty and supports no claim; the
refresh, not the flip, is what opens the scored window.

Three constraints carry over from the versioning discipline. `sal-v2` is a
**new frozen version, never an in-place edit** — `sal-v1` rankings must replay
under `sal-v1` forever, which the scorer registry below is what enforces, and
`sal-v2` keeps `sal-v1`'s score function byte-for-byte: what it adds is the
caption dimension (two bands, one carve-in predicate) and the arrival draw,
never a refit of the escalation ranking. Any *fitted* arrival-time scoring
remains a later version's question — arrival-time signals live in small
subgroups, and the candidate's bar is the arrival population's own weighted
grant rate at comparable recall, measured against the denial-complete corpus,
not quoted from the census. And the
carve-out/band alignment is pinned by test: the always-include floor and the
carved bands' cutpoints are separate constants in separate files, and the
identity between "carved in" and "the expected strongest-band prefix" —
`(high,)` for `sal-v1`, `(federal, high)` for every caption-banded version — is
checked exhaustively over the achievable score lattice (relist count x CVSG x
originating circuit x petitioner class, the class axis carrying a caption each
registered rule reads differently), so a refit cannot open a silent gap
between carve and band, and a version keying on a feature outside that
enumeration must extend it or say here that its coverage is partial.

### `sal-v3`: the same scorer, reading `caption-v2`

`sal-v3` is `sal-v2` with the caption predicate swapped to `caption-v2` — the
same `sal-v1` ranking score, the same five bands in the same order, the same
carve-in shape, the same arrival selection. Only recall of the frozen thing
moves: `sal-v2` carves in `classify_petitioner == "federal"` under
`caption-v1`, `sal-v3` the same predicate under `caption-v2`, so `sal-v3`
carves in every petition `sal-v2` does plus the federal captions v1's patterns
miss. Those captions move in the **band** dimension too, from their trajectory
tier into `federal`, which is what makes `sal-v3`'s per-band base rates a
different published pool from `sal-v2`'s rather than a relabeling of one. That
is why it is a **new registered version and not an edit**: the
`sal-v2` carve-in is frozen on a reviewed `caption-v1` census, and a rule
widening under the old label would re-point a published constant at a
population it was never measured on.

`sal-v3` is a **frozen, superseded** scorer: the active version is `sal-v4`
below, which is `sal-v3` read under a second distribution parse. Everything in
this section is `sal-v3`'s own record — the caption widening it registered, the
review that licensed it, and the pools its frozen predictions still replay
against — and none of it moved when the pointer did. Registration and activation are separate
steps, and the gap between them is where the review sits: a version is
registered while `SALIENCE_VERSION` still names its predecessor, so nothing
the live pass selects, latches, or stamps changes until the flip. The
registration order does not matter to scoring, because the statpack build
emits every registered version's bands in every Term — the active version's
in `segments`, each other's in `alt_segments` — so whichever version is
active at render time, every registered version's pool is in the
next-rendered pack. The refresh is still what opens the scored window: a
committed pack rendered before a version was registered carries no block for
it, so a `sal-v3` cell minted before the first post-registration refresh has
the version-pinned pool's designed `None` — legitimately empty, supporting no
claim, exactly as a pre-refresh `sal-v2` cell did. The bar the flip cleared is the same one
`sal-v2` cleared: a statistically reviewed `caption-v2` census, per Term and
pooled on the same frame as `caption-v1`'s, showing the widened class
replicating rather than diluting — with the evidential weight on the migrated
captions' outcome-free precision and the pre-registered replication shape,
never on the pooled-rate rise (the recovered captions were surfaced partly by
a grant-ranked residual scan, so any recall-gain figure is outcome-selected).
That selection also reaches the published number itself, in a known
direction, so it is stated where the number is read: the migrated rows enter
the `federal` pool with an outcome-selected grant record, sitting the pooled
`federal` rate roughly two to three points above an unbiased forward
estimate, and the trajectory bands they drained about a point low — on the
skill denominator a relative effect of a few tenths of a percent, far inside
a band that runs 11–41 resolved rows per complete Term on the census frame
(the statpack band, whose denominators the realized floor reads, runs 9–39
under `caption-v1`). Only an out-of-sample
re-census under `caption-v2`, once frozen-window Terms accrue, can estimate
the incremental class's forward rate; the activation review is not a
substitute for it. The sequencing holds as it did for `sal-v2`: the promotion
carrying the flip, then a metrics refresh, then prediction. On the realized
column, the flip only relieves pressure: under
`REALIZED_BAND_RATE_MIN_RESOLVED = 30` the `federal` band clears the floor in
one complete Term under either rule (OT2020 — 39 rows under `caption-v1`, 41
under `caption-v2`, with OT2023 moving from 22 to 29), so the other Terms'
realized-Term suppression is the designed answer for a thin pool, not a
consequence of the flip.

Two things the extra registered version does **not** license. The gate replay
scores `sal-v3` as it scores every registered version, but `sal-v2` and
`sal-v3` differ in nothing except a caption feature, and the replay's
reconstruction carries the terminal caption — so a `sal-v2` / `sal-v3` replay
comparison is exactly the measurement this artifact declares it cannot make,
and no precision or recall delta between them may be read from it (the two are
not run at a matched operating point either, and `sal-v3` carves in strictly
more, so its raw precision reads lower mechanically). And the two carve-in
subcohorts are **different arrival populations**, one selected by each rule's
predicate, so their outcomes never pool — the same rule that keeps the random
slice and the carve-in apart.

### The scorer registry

A salience version is not a function but five things that decide together what
a band label means: the score function, the band function, the band *names*,
the always-include rule, and the **distribution parse** the ranking's primary
feature is read under (below). A sixth belongs with them and deliberately does
not travel on the record: the always-include **floor** the carve-out compares
against is `config/tracking.yaml`'s single shared `salience.floor`, so it is
config rather than code and every registered version is held to the same value.
That is a real cost, stated rather than hidden — a replay run today reproduces
a past ranking only if the floor has not moved since, and a candidate scorer
cannot choose its own carve-out threshold without moving the shared one.
`pipeline.salience.SCORERS` holds each version as
one `SalienceScorer` record, and `SALIENCE_VERSION` names the **active** one —
the version the live pass scores with and stamps onto the corpus and onto every
prediction's frozen context. A refit registers a new record beside the old
rather than editing it, and `scorer(version)` raises on an unregistered label
rather than falling back, so no consumer can silently receive output banded
under a version it did not ask for.

Three consequences are worth stating, because each is a place the discipline
could otherwise leak:

- **The corpus is single-version by design.** `salience_score` and
  `salience_version` are one column each, holding the active scorer's view. What
  makes history safe is not the corpus but the band and version frozen onto each
  committed prediction, so re-pointing the active version can never retroactively
  re-band a prediction **that carries a frozen band**. A prediction written
  before that block existed has its band re-derived from the row by the active
  scorer, and is re-baselined by a version switch; `base_rate_salience_version`
  on the evaluation is what makes that visible after the fact.
- **`statpack.json` publishes every version.** A base-rate pool is pinned to the
  scorer that assigned the band it quotes, so a prediction frozen at a retired
  version would lose its baseline the day the live pass moved on. Each Term
  carries the active version's `segments` plus an `alt_segments` block per other
  registered version, so every registered scorer's bands are published whether
  or not it is the live one. The **Markdown** pack renders the active version
  only, so a reader of `statpack.md` is reading one version of several. One
  qualification the parse adds, and it is a live one: the pack bands every
  version off the corpus's single `distribution_count` column, so a version
  whose declared parse is not the column's is published under the pool the
  *column's* reading built rather than its own, and the block carries no parse
  field to say so. Which version that is today, and why nothing consumes the
  mislabeled block, is in the parse section below.
- **The gate replay is a three-axis report.** Cells span Term x policy x
  version, and each (Term, policy, distribution parse) is projected once and
  scored by every registered version pinning that parse, so two versions cannot
  differ in the dockets they saw except where one deliberately reads them
  differently.
  They are not compared at a matched operating point, though: the floor and the
  capacity are shared, so a scorer with a different score scale selects a
  differently sized set. Read a cross-version comparison at matched **recall** —
  the bar pre-registered above — never as a bare precision delta
  (`metrics/README.md`).

### The distribution parse

The relist bucket is the score's primary signal, and it is derived — not
observed. A petition's distribution count is *parsed* out of free docket-entry
text, so which entries the reading admits is as much a part of the band as the
cutpoints are. `pipeline.cert_signals.DISTRIBUTION_PARSES` registers each
reading under a label, every `SalienceScorer` pins the one it was fitted on, and
a parse is added to the registry rather than edited — the same discipline the
scorer registry itself keeps, for the same reason: a reading that changed under
a stable label would silently redefine every band derived from it.

Two readings are registered. **`dist-v1`** matches the conference phrase
anywhere in an entry. **`dist-v2`** matches it only at the start of the entry,
which excludes a distribution belonging to some paper other than the petition:
a motion, an application, or a suggestion of mootness going to conference always
names that paper first (`Motion (25M82) DISTRIBUTED for Conference of …`), while
the petition's own distribution opens its entry with the word. Under `dist-v1`
that ancillary traffic counts toward the petition's trajectory, which reads a
petition as relisted on the strength of a motion's trip to conference.

Both parses share the rest of the machinery — the same capture group, the same
date parse, the same distinct-conference-date dedupe — so two counts of one
docket differ by exactly which entries were read. The parse governs the
trajectory **count** only: `distributed_for_conference`, the cohort key, stays
unversioned, because an ancillary paper is distributed for the conference the
petition is on and a case must sit in one cohort rather than one per parse.

`sal-v1` through `sal-v3` pin `dist-v1`; the **active** `sal-v4` pins `dist-v2`
(below), which is also the reading the corpus's `distribution_count` column now
holds. The active scorer's parse and the column's therefore agree, which is the
alignment that is load-bearing beyond banding: the relist-increment
claim reads its prediction-time count from the frozen context (which follows the
active scorer's parse) and its resolution-time count from the corpus column
(which is at the default), and the claim's "the count never falls" premise holds
across that pair only while the two readings agree. A `dist-v2` version made
active before the column was re-derived would have broken that premise
**upward** — a narrower prediction-time count against a wider resolution-time
one — which is why the column re-derivation orders first in the activation steps
below, and why the flip moves `SALIENCE_VERSION` and the parse registry's
default in one commit rather than two. The three frozen `dist-v1` versions keep
that pin **after** the flip: a prediction frozen at `sal-v3` replays against the
reading its band was derived from, whatever the column now holds.

The evidence a new parse would be argued from is the **`distribution-census`**
artifact ([cli.md](cli.md)): two parses counted over one frame — the gate's scored
segment with pending rows kept, since the count is a banding input read long
before a petition resolves — banded by one scorer, reporting changed counts, the
band-transition matrix, a per-Term rollup split by docket maturity, a per-band
rollup keyed on the baseline parse's band, and every changed case id. Both
counts come off each case's latest **live-shaped** snapshot, because the
entry-initial rule is a claim about the live channel's entry conventions, and
counting a REST payload under it would report a channel artifact as a parse
delta.

Three things about the artifact's shape decide what may be read off it:

- **Every cut carries its own denominator.** `cases` is the rows whose latest
  **live-shaped** snapshot disclosed a proceedings list, not the frame: a case
  with no live-shaped snapshot at all — a REST-only docket among them, whose
  entries the entry-initial rule may not be read against — counts `unobservable`
  instead, and the frame is `cases + unobservable`. The banner prints the
  coverage fraction, so a census that read a tenth of its frame cannot announce
  itself like one that read all of it. Maturity likewise has two denominators,
  at both levels: `frame_pending` (census-wide and per Term) counts pending
  across the whole frame, while the per-Term `pending` counts it among the
  observable rows only. Which way the two diverge is itself a finding — maturity
  is a property of the docket and readability a property of the pull, so neither
  count may stand in for the other.
- **The transition matrix is the full band-by-band square, zero-filled.** An
  omitted cell and an observed zero are different findings. Which half of the
  square a parse pair can occupy at all is a property of the pair, not of the
  artifact: where the candidate's matches are a subset of the baseline's — the
  entry-anchored reading against the entry-anywhere one — the count can only
  fall, and every registered band function is monotone in it (pinned by a test
  over the registry), so no case can move to a stronger band. `count_increased`
  is the frame-level check on the nesting; the zero-filled strengthening cells
  are the conclusion, measured. The empty half is an identity, not a finding,
  and reversing the two parse arguments moves it — which is why the banner
  counts occupied cells rather than reporting a density over the whole square.
- **The per-band cut is keyed on the baseline band** — the incumbent *reading*
  of the same snapshot, which is not necessarily the label the case carries in
  the corpus (that comes off the max-latched `distribution_count` column, which
  no side of this census reads). So "what share of `elevated` would move" is
  answerable from the artifact rather than only by joining the changed ids back
  against the corpus. It partitions the observable rows: an unobservable case
  has no count and so no band, and the per-band `cases` sum to `cases`, never to
  the frame. Each band carries its own `pending`, because the bands are built
  from the conference count and a pending docket has had fewer conferences —
  band and maturity are correlated by construction.

It is produced by `run-analytics`'s **`census`** mode ([pipeline.md](pipeline.md)),
which pulls the corpus under the read-only role, runs the command over that
frame, and uploads the JSON as a run artifact beside the step summary — the
review is conducted over a file with a `corpus_sha256` in it, so it says which
corpus state it is re-derivable against and outlives the run page. `dist-v1`
against `dist-v2` are the dispatch defaults; both parse labels are inputs, so
once a further reading is registered it is argued from the same surface with no
workflow change — and because `dist-v2` is now the incumbent, a dispatch left on
those defaults reads the activation backwards rather than arguing a candidate,
which is a re-derivable check on what the flip moved but not a review of
anything. The band function is not a *dispatch* input — the workflow
reads against the active scorer, though the command itself takes `--version`
and defaults to it.

On the command, only the **incumbent** parse defaults. `--baseline-parse`
follows `DEFAULT_DISTRIBUTION_PARSE` because the registry names the incumbent;
`--candidate-parse` is required, as it is on the library function, because the
challenger is whatever a caller is arguing for and the registry cannot know it.
Defaulting the challenger to a label would also mean that the commit activating
that label quietly turns a bare invocation into a parse-against-itself census,
reporting no movement on every row.

**Activating a parse is three pieces of work, not one.** The census is the
*input-level* cut and its matrix is conditional on the first of them:

1. **Re-derive the corpus `distribution_count` column** under the new parse, on
   a writer job — `fedcourts rederive-distribution-counts --parse <label>`
   ([cli.md](cli.md)), dispatched as run-seed's `rederive_distribution_parse`
   step (`dry-run`, read, then `apply`; [pipeline.md](pipeline.md)). Its write
   bypasses the max latch (a direct `UPDATE`, the shape the bulk scrubs use),
   because the latch lives in the upsert path
   itself: a narrower reading routed through `upsert_rows` is a silent no-op
   that reads as convergence. Until the column is genuinely re-derived, every
   downstream consumer is still reading the outgoing parse's counts. Three properties of
   that command decide what the step can honestly claim.

   Its frame is the **live slice**, wider than this census's scored segment,
   because the column is the corpus's and one left mixed-parse outside the
   gate's segment would mean different things on different rows — so its
   changed count can exceed the census's, and only its census-frame sub-count
   is the figure this artifact measured.

   What it compares is **the stored column against the candidate reading**, not
   two readings of one snapshot as the census does. Those coincide only where
   the stored column is a faithful incumbent reading, which is why the command
   is run **twice**: once under the incumbent parse, which must report `changed
   = 0`, and then under the candidate. A non-zero control run is stored-column
   drift — a degraded payload, a dedupe merge-max, a backfill gap — and until
   it is triaged the candidate's count is a sum of the parse and that drift,
   with no way to tell which is which.

   And a row whose latest live-shaped snapshot discloses no proceedings
   **entries** is reported `unobservable` and left as it is, never written to
   0. That is narrower than the max latch it replaces, which rejected any
   regression whatever its cause: an empty or absent entry list is caught, a
   merely truncated one is not. The control run above is what stands in for the
   rest.

   The re-derivation is durable only as far as the ingest default is. The live
   channel re-polls pending petitions and open merits proceedings and upserts a
   count read under `cert_signals.DEFAULT_DISTRIBUTION_PARSE`, which the latch
   takes wherever it is higher — so a re-polled row reverts to the incumbent
   reading unless that default moves to the same parse, and on exactly the rows
   the parse moved. The standing poll is not the only channel: `refresh-dockets`
   and the Term walker's re-serve run **resolved** rows through the same upsert,
   so the revert set is "whatever is re-served", not "whatever is pending"
   (`backfill-live-signals` is the exception — it fills nulls and touches
   nothing else). The sweep converges the column; moving the default is what
   keeps it converged, and the two belong in one batch rather than two.2. **Rebuild the statpack**, so each band's published base rate is measured over
   a population banded under the same parse. A band whose membership moved but
   whose quoted rate did not is a mislabeled baseline. Expect the rebuild to
   move a *rate*, not merely to relabel members: on the `dist-v1` → `dist-v2`
   census of record ([freeze-record.md](freeze-record.md)) `elevated` shed 118
   of its 2,364 rows, 5.0% of the band, and the rebuild moved its published
   rates accordingly — a rebuild that leaves the expected band's rate where it
   was is evidence the rebuild did not happen.
   The rebuild also **re-bases every other registered version's
   `alt_segments`**, and that half is consumed: the pack bands all versions off
   the one column, so once the column reads the new parse the `sal-v1` /
   `sal-v2` / `sal-v3` blocks are measured on populations *their* declared parse
   never defined, and a prediction frozen at the outgoing active version silently
   re-baselines against one. The block carries no parse field to make that
   visible, unlike a replay cell. So the rebuild is not a mechanical step: it
   needs a decision, taken at activation, either to record the parse on the block
   or to state that the outgoing version's frozen predictions re-baseline.
3. **Re-measure the relist-tier grant rates** the cutpoints sit between. The
   tiers are empirical rates for "0 relists", "1 relist", "2+"; re-reading which
   entries count as a relist re-populates those buckets, so the cutpoints are
   fitted to the old populations until they are re-measured.

Step 1's position is an **invariant, not an ordering preference**: a narrower
version must never be made active before the column is re-derived. Frozen
contexts would then carry the narrow counts while the corpus column still held
the wide ones, and the relist-increment claim's "the count never falls" premise
would break upward — a resolution-time count exceeding a prediction-time count
by the ancillary lines the narrower reading dropped, which would read as docket
movement that never happened. The test suite pins only the **label** here (the
active scorer's parse equals the registry's default), which a commit moving both
together would satisfy with the stored column untouched. So the invariant is
settled by a data check rather than a test.

**The check is the writer's own report, not a census.** `distribution-census`
takes *neither* side off the column — both counts come off the latest live-shaped
snapshot, deliberately, because the column holds one parse's answer max-latched
and so could not supply either side on equal terms. So a census run after the
re-derivation compares the incoming parse against itself and its zero is a
tautology about the label. What settles the invariant is the re-derivation
dispatch's own applied-row count, plus a `query` spot check on named rows whose
stored count must have fallen to the narrow reading's value. That fails loudly if
the writer's latch bypass did not bite.

**And the window does not close at the merge — it closes at the promotion.**
`run-pull`'s `live` mode is a scheduled workflow, so it runs from the **default
branch**, where the outgoing default parse is still in force until the flip is
promoted. Every live poll in that window re-derives the wide count for the rows
it touches and writes it through `upsert_rows`, whose `distribution_count` latch
is a `MAX` — so the re-inflation is **permanent**, and no later narrow write can
lower it again. Once the flip is live that is exactly the upward break the
invariant exists to prevent, on whichever pending rows the poll happened to
reach. So the re-derivation is run **again after the promotion lands**, or the
live writers are held across the window; the spot check is taken on the far side
of it, never before.

And the census answers the *input* question only. Who the gate would actually
fund is a rank-and-cap question — a band move also moves a petition's cohort
rank, and a band move out of the strongest band moves it out of the
always-include carve-out into the rank contest — so that is read from
`salience-replay` with the candidate version registered, never from the
transition matrix. The replay does that for a version that is registered but
**not active**: it scores every registered scorer, and builds one reconstruction
per (Term, policy, distribution parse), so a candidate pinning a second parse is
projected under its own reading and each cell records its own
`distribution_parse` — which is what lets a cross-version comparison say whether
two cells saw one reading.

### `sal-v4`: the same scorer, reading `dist-v2`

`sal-v4` is `sal-v3` with the pinned distribution parse changed to `dist-v2` and
nothing else — the same `sal-v1` ranking score, the same `caption-v2` band rule,
the same five bands in the same order, the same carve-in shape, the same
reachable ladders, the same arrival selection. In the registry it reuses
`sal-v3`'s callables rather than copies of them, so the two versions cannot drift
apart in anything but the parse. What moves is not how a docket is scored but
what the score's primary feature is read off: `dist-v1` counts an ancillary
paper's trip to conference toward the petition's relist trajectory, `dist-v2`
counts only the petition's own distributions. Because `dist-v2`'s matches are a
subset of `dist-v1`'s and every registered band function is monotone in the
count, a row's `sal-v4` band is its `sal-v3` band **or weaker, never stronger**.

That direction is what makes this a new registered version and not an edit, on
the same argument `sal-v3` rests on: `sal-v3`'s per-band rates are frozen on
populations counted under `dist-v1`, and re-reading the count under a stable
label would re-point a published constant at a population it was never measured
on.

`sal-v4` is the **active** scorer — `SALIENCE_VERSION` names it, and
`DEFAULT_DISTRIBUTION_PARSE` names `dist-v2` beside it. Those two constants move
in **one commit**, never two: the relist-increment claim reads its
prediction-time count from the frozen context (the active scorer's parse) and
its resolution-time count from the corpus column (the default parse), so a
commit that moved one and left the other would break that claim's monotonicity
premise for as long as the split stood. What licensed the *registration* was the
`dist-v1` → `dist-v2` distribution census recorded in
[freeze-record.md](freeze-record.md), scoped to a `sal-v4` that is `sal-v3` with
the pinned parse changed and nothing else; it explicitly did not license
activation. What licensed activation is the three steps listed above, taken in
that order, with the sequencing invariant settled by its own data check — the
activation record, with the decision step 2 asks for and the tier re-measure
step 3 asks for, is in [freeze-record.md](freeze-record.md).

**The scored window opens at the first post-promotion metrics refresh, not at
the flip** — the same sequencing `sal-v2` and `sal-v3` took, and it is stated
here rather than only in their sections because it is an operator's constraint
on the next predict dispatch after any future flip: a cell minted under a
version the committed pack does not yet render reads the version-pinned pool's
designed `None` — legitimately empty, supporting no claim — and a whole round
minted before the refresh has no skill column. For `sal-v4` that refresh has
run: the committed pack's Terms stamp `sal-v4`, its `alt_segments` hold
`sal-v1`/`sal-v2`/`sal-v3`, and `elevated`'s published rates moved with the
re-derived column (the falsification check the activation registered — a
rebuild leaving them unmoved would have been evidence it did not happen).

One maintenance command is worth naming beside that, because the flip changes
what it would do. `unlatch-overselected` recomputes each pending cohort under
the **current** scorer and clears the rows the recomputation would not pick — so
run after the flip it would de-select pending petitions the parse demoted, the
41 rows that leave `high` on the census frame among them. That is a selection
change, and the replay run of record has close to no power to license it. It is
not part of activation; do not fold it in.

Two of those steps left a decision rather than a number, and both are settled
here so a reader of the committed artifacts is not left to infer them.

**The outgoing version's frozen predictions re-baseline; the block does not
record its parse.** `statpack.json` bands **every** registered version off the
corpus's single `distribution_count` column, so once that column reads `dist-v2`
the `sal-v1` / `sal-v2` / `sal-v3` `alt_segments` blocks are measured on
populations *their* declared parse never defined — and a prediction frozen at
`sal-v3` reads one of them. Step 2 offers two ways out: record the parse on the
block, or state that the re-baselining happens. The second is taken. Recording
the parse would be a schema change on the committed pack, which is its own
review and its own drift check, and it would not repair the frozen prediction —
it would only label the substitution. Stating it does the work the label would:
a `sal-v3` cell's published baseline after the rebuild is `sal-v3`'s band rule
over `dist-v2` counts, which is `sal-v4`'s pool wearing `sal-v3`'s name, and the
difference is bounded by the census delta — 159 changed bands on 13,839
observable rows, 1.149% pooled, but the bound that matters is per band, since the
movement concentrates: `elevated` 118 of 2,364 (**5.0%**) and `high` 41 of 1,023
(**4.0%**), four to five times the pooled figure, and `high` is the always-include
tier. (Those are the registration census's figures, taken on blob `b16b856f…`,
not this section's `c6b43484…`.) Any cross-parse comparison of a `sal-v3` cell's
skill against a `sal-v4` cell's is reading through that substitution and must
say so.

**The relist-tier cutpoints do not move, and the re-measure that would have
moved them is published instead** — the next subsection. The cutpoints stay at
`sal-v3`'s: moving a fitted constant under a stable version label is the exact
edit the registry exists to forbid, and a refit is a `sal-v5`, argued from the
re-measure as the census argued `sal-v4`.

#### The relist tiers, re-measured

Activation step 3. The tiers `sal-v1`'s ranking score is fitted to — the
empirical grant rates for "0 relists", "1 relist", "2+" — are re-populated by
the parse, because which entries count as a relist decides who is in each
bucket. Measured over the **same frame the distribution census reads**
(live-slice, paid, modern-cert SCOTUS petitions with a parseable Term), on the
**resolved** rows, with both counts taken snapshot-side off each case's latest
live-shaped snapshot so the two readings are compared on identical rows.

The basis, stated because a rate without one is not a measurement:
**snapshot-side recount, not a column read** — the corpus column still held
`dist-v1` counts when this was taken, so the `dist-v2` column-side confirmation
lands with the post-apply statpack rebuild. Corpus blob
`c6b43484cab17ac7495d23d1c81f01ad686be098914d88cbe6d9b9cb7085e085`, latest pull
`2026-08-28`, latest stored snapshot `2026-07-13`, store-served. Frame 13,840
rows, 13,839 observable, 1 unobservable, 13,341 resolved.

This is a **fit diagnostic for a ranking constant, not a scoring baseline.** It
pools the whole walked range with no own-Term exclusion and no
`base_rate_lookback_terms` cut, so none of these numbers is the per-Term,
prior-Terms-only band rate an evaluator scores Brier skill against (*Base rates
& baselines for the predicted segment*, below). Quoting one as a forecast anchor
would break the leakage guard registered there.

**Two outcome vocabularies, and the reading depends on which.** The pipeline has
two granted-side membership tests, and both include GVR:
`GRANTED_DISPOSITIONS` (the binary target `actual_granted` projects onto) and
`GRANT_FAMILY_DISPOSITIONS` (what the statpack's published `est_grant_rate`
counts). They coincide on this frame, whose only resolved dispositions are
granted, GVR, denied and dismissed. A granted-only cut that drops GVR is a
*third* vocabulary the pipeline neither scores nor publishes — so it is reported
here beside the grant family rather than instead of it, because the mis-fit below
lands in different tiers under each.

| relist tier | resolved (`dist-v1` / `dist-v2`) | granted-only (`dist-v1` / `dist-v2`) | grant family (`dist-v1` / `dist-v2`) | fitted constant |
| --- | --: | --: | --: | --: |
| 0 | 9,768 / 9,892 | 1.188% / **1.284%** | 1.730% / **1.820%** | 0.8% |
| 1 | 2,566 / 2,486 | 8.262% / **8.407%** | 13.016% / **13.475%** | 7.8% |
| 2+ | 1,007 / 963 | 24.926% / **25.234%** | 38.431% / **38.941%** | 39.4% |

Pending rows sit outside those denominators and are censored unevenly across the
tiers — 449, 42 and 7 under `dist-v2`, which is 4.3%, 1.7% and 0.7% of each
tier's observable rows. The censoring cuts toward conservatism at relist-0, where
it is largest.

Two findings, and they point in different directions.

**The parse itself barely moves the tiers, and does not sharpen them.** All three
rates rise, by 0.096, 0.145 and 0.308 percentage points. All three rising is a
**mixture shift, not a uniform improvement**: the overall grant rate is fixed at
579/13,341 = 4.340% under either reading, so the rates can only all rise because
mass moved into the low-rate tier. Two of the flows are exact rather than
inferred, because relist-2+ is the ceiling of a count that can only fall (pure
outflow) and relist-0 its floor (pure inflow): **44 resolved rows carrying 8
grants left 2+** (18.2%, below 2+'s own 24.9%, so 2+'s rate rises), and **124
resolved rows carrying 11 grants entered 0** (8.87%, far above 0's own 1.19%, so
0's rate rises too).

That second number is the informative one. The petitions `dist-v2` demotes grant
at roughly the relist-1 level, so they are *not* indistinguishable from genuine
relist-0 petitions, and demoting them costs a little top-to-bottom separation:
the 2+-to-0 rate ratio falls from **20.99× to 19.65×**, and on the grant family
from 22.21× to 21.40×, so the direction does not depend on the vocabulary.
Whether that ~4–6% loss is real or sampling noise is not settled by 11 grants on
124 rows, and it is not
what the parse was argued for — `dist-v2` is a correctness claim about what the
DISTRIBUTED phrase means, not a discrimination improvement. It is recorded here
so a `sal-v5` refit starts from it rather than from the assumption that a
narrower reading is a cleaner one. It inherits one caveat from how the re-measure
was taken: the tier here is read off each case's **latest** live snapshot, its
final count, while the score applies these constants to the count **as at
prediction** — the same final-versus-as-at gap
[outcome-decomposition.md](outcome-decomposition.md) names for its 37% bound. A
refit taking these numbers at face value would fit final-count tier rates for
prospective use on systematically lower as-at-prediction tiers. Nothing in any of
it moves a cutpoint.

**The standing constants mis-fit the corpus, and which tier mis-fits depends on
the vocabulary.** Against **granted-only**, the 2+ constant is the outlier: 0.394
against 25.234% is 1.56×, +14.2 points, while relist-0 and relist-1 sit *below*
their measured rates at 0.62× and 0.93×. Against the **grant family** — the
vocabulary the statpack publishes in and `salience.py` names as the constants'
source — it inverts: 0.394 against 38.941% is **1.01×, +0.46 points**, essentially
exact, and the mis-fit moves to relist-0 (0.44×) and relist-1 (0.58×). One
constant is nearly right in each reading and never the same one. So the three
constants are not all estimating the same quantity on this frame; which of them
is wrong is not answerable from the measurement, only from the fitting frame they
were taken from, which is not recoverable here.

Two things the measurement *does* establish. The divergence is **invariant to the
parse** — 1.56× at `dist-v2` and 1.58× at `dist-v1` granted-only, 1.01× and 1.03×
on the grant family — so whatever causes it, the parse does not. And corpus drift
does not cause it either, at least at 2+: the fresh `dist-v1` reading (24.926%)
agrees with the committed statpack's own 2+ pooling (≈24.89%) to within four
hundredths of a point, so a corpus that had drifted 14 points under the constant
would have had to drift the published pack with it, and it did not. The cause is
unidentified and is stated as unidentified.

**This is recorded, not corrected.** The mis-fit is a `sal-v5` question and it
cannot be closed by editing one constant, because the always-include **floor**
is entangled with it — and entangled *differently* under each vocabulary, which
is the sharpest reason the refit has to be a registered version rather than an
edit. `salience.floor` is 0.28, set to sit at the relist-2 / CVSG grant-rate
band. Substituting the **granted-only** 0.25234 for 0.394 leaves the band alone —
every 2+ petition still clears the `high` cutpoint of 0.20 — but drops it out of
the carve-out for every originating circuit except `cadc`, the only nudge large
enough to reach 0.28: 0.2980, against `ca5`'s 0.2780, `ca9`'s 0.2691 and an
unlinked petition's 0.2573. Substituting the **grant-family** 0.38941 instead
changes nothing at all, since it sits above the floor already. So one refit
silently strips the always-include tier of almost every 2+ petition and the other
is a no-op, and the choice between them is a vocabulary decision nobody has taken
on the record. A refit therefore has to re-decide the floor and the vocabulary in
the same version, which is exactly why it is a new registration and not a
constant edit.

Because the floor consequence turns on it, note what the floor's own comment
means today: `config/tracking.yaml` describes 0.28 as "the relist-2 / CVSG
grant-rate band", and on this measurement that description is true of CVSG
(0.283) and, on the grant family, of relist-2+ (0.38941 — above it), but not of
relist-2+ read granted-only (0.25234 — below it).

Three consequences of the parse change, each measured on the census of record
rather than assumed. The figures are dated evidence and live in
[freeze-record.md](freeze-record.md); what they are quoted for here is what they
mean for the activation now taken.

- **Five cases read never-distributed under `dist-v2`** — four falling 1 → 0 and
  one, `scotus/68076851`, 3 → 0 on three motion lines. The four are relist-0
  under both readings (relists are `max(0, count − 1)`), so their bands do not
  move; the fifth crosses two cutpoints and bands `high` → `baseline`, which puts
  it among the 41 `high`-leavers rather than beside the other four. All five are
  a declared divergence from the cohort key either way:
  `distributed_for_conference` is deliberately unversioned, so they stay in the
  conference cohort their ancillary paper was distributed for while carrying a
  zero count. That is the designed behaviour of an unversioned cohort key, not a
  defect, and it is on the record so a later reader does not rediscover it as
  one.
- **41 cases leave `high`**, the always-include tier — a real selection
  consequence, since leaving `high` means leaving the carve-out and entering the
  rank contest. Whether such a case is still funded is a rank-and-cap question,
  which is `salience-replay`'s to answer and not the census's.
- **118 cases leave `elevated` for `baseline`**, 5.0% of that band, which is why
  the statpack rebuild should be expected to move `elevated`'s published rate.

The **selection** question those consequences raise is answered by
`salience-replay` — the replay scores every registered scorer, so registration
alone was enough to ask it, and `sal-v3` stays askable beside the active
`sal-v4` for the same reason. The run taken at the registration commit, with its
numbers and its vintage, is in [freeze-record.md](freeze-record.md), and its
standing is the part that belongs here: it is **provisional and carries almost
no power**. It settled nothing about the activation, and the activation does not
close it — the question of what the rank contest does with a demoted petition is
still open, and the instrument that would settle it is named at the end of this
section.

Two facts about that run, either of which would be enough on its own. Only four
of its nine (Term, policy) cells select anything at all — the three OT2022 cells
and both `arrival` cells select nothing under either scorer — so "the two
scorers agree" rests on four comparisons, not nine. And the rows it could
reconstruct are not a sample of the frame but the *granted* end of it: on this
blob the reconstructable rows carry grant-family rates of 42.1% (OT2023) and
40.0% (OT2024) against 3.2% and 0.09% on the rows it could not read, and hold 90
of OT2024's 91 grants. No rate, band mix, precision or recall from such a run
transfers to the frame.

The cause is data availability rather than the replay's method, and it is worth
naming precisely because `corpus_sha256` invites the opposite reading: that hash
identifies the SQLite **index**, while the snapshot payloads the replay
reconstructs from live in the per-case content store. A checkout without the
store wired reads only the snapshots the blob itself carries — the same census
re-run in that state observes a few percent of the frame where the `run-analytics`
census reached 99.993%. On so small a read almost no conference cohort is
capacity-bound, so the rank contest has hardly any opportunity to drop a demoted
petition and an observed zero disruption is consistent with any amount of it at
full coverage. The instrument that would settle the question is the same replay
run where the store is wired, which is `run-backtest`'s salience-gate replay
([metrics/README.md](../metrics/README.md)) — a dispatch, not a local command.

## Selection — deterministic rank-and-cap, sticky per conference

Selection ranks the scored set and caps it to `N` — and, where the active
scorer selects arrivals (`selects_arrivals` — true of every caption-banded version), the same write pass runs
a second, cohort-less arm: every undistributed pending petition the keyed draw
or the carve-in predicate picks is latched with no rank and no capacity, and
its owed `evt-petition-arrival-disposition` event is minted in the same pass —
**both halves**, the corpus row and the ledger `event.yaml`, through the shared
mint seam (`outcome.persist_moment_events`), because a declared moment's two
halves are one write. Idempotently, and keyed on the pair: a crash between
latch and mint, or between the two halves, heals on the next pass while the
pick still reads as an arrival (undistributed, baseline open), since the
mint is state-driven off what is missing and never off the draw recomputed. The
arrival arm rides beside `N`, never inside it, and the freshness guard on the
mint (`outcome.arrival_event_for`) refuses a case any distribution has already
reached — an arrival cell exists only where the forecast genuinely precedes
the docket's first move. Everything below describes the rank-and-cap arm.
**The enforcement mechanism is
the load-bearing decision here, because the obvious one is wrong.**

**Why below-cap is not a scope exclusion.** The shared reason evaluator
`out_of_scope_reason_full` is consumed by several seams, and one of them —
`cleanup.find_out_of_scope_predictions` — **deletes committed prediction
artifacts** (`shutil.rmtree`) for any case it flags. That deletion is correct for a Tier-0 hard
exclusion (a pre-1925 mandatory case should never carry a prediction). It is
**fatal** for below-cap selection: a petition legitimately predicted early, whose
salience later drifts below the cap as fresher petitions distribute, must **keep**
its committed forward forecast — deleting it would destroy exactly the
pre-registered prediction the whole thesis rests on and corrupt the leaderboard's
forward stratum. So below-cap selection **must not** route through
`out_of_scope_reason_full` / `predict_excluded` / cleanup.

**The mechanism: a separate, sticky latch.** A case-level corpus column
`salience_selected` (with `salience_score` and `salience_version` alongside),
written only by the deterministic selection pass — applied inside every live
cycle, with `reconcile-salience-selection` as its manual entry point,
structurally analogous to the scope reconcile — carries the decision:

1. **Cohort key = `distributed_for_conference`.** Capacity is a *per-conference*
   fundable slice, not a global one. This is what makes replay tractable: "why this
   case and not that one" is always answered within one conference's candidate pool
   at a fixed score version.
2. **Score** every Tier-0-eligible SCOTUS row in the cohort (`salience_score`,
   `salience_version`) — including an already-**decided** petition, so its
   historical row still carries a band. A decided petition never enters cohort
   selection, though: it has no open event left to predict, and latching it
   would muddy "`salience_selected` = tournament spend" with cases the gate
   never actually funds.
3. **Always-include carve-outs**, unconditionally selected **above** the `N`
   budget: CVSG petitions (`cvsg_date IS NOT NULL`) and anything at or above a
   documented **salience floor** — set at the grant-rate level of clearly
   cert-worthy cases, ≈ the relist-2 / CVSG band (~25%+ historical grant rate). A
   major case can never fall below the capacity line.
4. **Rank the remainder** by score and fill to `N`, minus any **interim reserve
   slots in use** in the current (latest) cohort — the one carve-*in*: a live
   substantive application's slot displaces the lowest-ranked rank-fill pick,
   never a carve-out (see *The interim docket* below). **Additive-above-N**
   otherwise: carve-outs and sticky latches may push the realized count above
   `N`. This is the simplest policy and never destructive.
5. **Latch `salience_selected = 1`** for the union. The latch is **one-way
   (`0 → 1`, never `1 → 0`) for every pass**: once selected, a case stays
   selected for its lifetime unless the maintainer runs the one sanctioned
   reconcile below. The score recomputes every pass on fresh features, and
   ranking uses the fresh scores to *fill remaining capacity* — but the pass
   itself never de-commits.

This resolves the temporal dynamics of a live conference cleanly: a case selected
early and later out-ranked **stays selected** (its committed prediction is safe,
cleanup never touches it, no thrash); a high-salience petition appearing mid-cycle
is picked up on the next pass if capacity or a carve-out admits it. Because
the passes are additive-only and scores are versioned, the selected set at any
time is reconstructable from committed columns *and the record of any
maintainer reconcile below* — the pre-registration replay is unaffected either
way, since it deliberately re-derives selection rather than reading the latch.

The additive latch has one structural consequence a **capacity resize** exposes:
petitions latched under a larger cap stay latched under a smaller one — a
standing overhang the live pass can never shrink, spending cells the resized
envelope never budgeted. The sanctioned answer is `fedcourts
unlatch-overselected`, a deliberate, maintainer-run, dry-run-default reconcile
(never scheduled): it recomputes each **pending** cohort's selection from
scratch under the current config and clears the latch on pending petitions that
recomputation would not pick, touching neither decided rows (their latch is the
historical record of selection), interim applications, nor any committed
prediction — which also stays **graded**: the evaluate matrix reads the scope
filter without the salience skip, so a cleared case's prediction still scores
when its event resolves. It is the latch's one `1 → 0` writer, its result
carries the full cleared-id ledger (the write erases the corpus's own record
of the pre-resize sticky set, so the run output is that record — note the
pre-apply `corpus.db.ref` beside it), and running it is a recorded operational
decision, not part of the pass: run `dedupe-live-rows --apply` first (a merge
takes the latch stickily from either twin), and disclose the cleared set in
any write-up whose cohort it reshapes. Because the corpus is written only by
the writer lane, the `--apply` runs there rather than from a checkout: dispatch
**`run-seed` with `unlatch_overselected`** set, which runs the `dedupe-live-rows`
sweep and the scope reconcile ahead of the clear in the same run — so the
"dedupe first" prerequisite is satisfied by ordering, and the clear is gated on
that sweep succeeding — then commits the pointer to `main` like every other
corpus write. Prefer a dispatch when the walk is already at its frontier, so
the walk loop exits early and leaves the sweep budget to the clear (the clear
plus the ~1GB push runs several minutes, and the dispatch shares the job's
wall-clock cap with the walk). Dry-run it first from a read-only checkout
(`fedcourts unlatch-overselected`, the default) to see the count and the
cleared-id set before the dispatch.

**Enforcement wiring** is small but real (it is not free):

- `predict-matrix`'s scope filter carries one skip branch — a hard-in-scope SCOTUS
  docket with `salience_selected == 0` is dropped from the tournament matrix with a
  distinct "not selected this salience round" note (read-time, non-destructive),
  except where **cohort completion** keeps it narrowed to its already-predicted
  events (below).
  The **evaluate** matrix reads the same filter *without* that branch: selection
  decides which cases earn new cells, never whether a committed prediction is
  scored, so a cleared or below-cap case's prediction still grades on resolution.
- The pull queue declines to enqueue unselected cases, with the same
  cohort-completion exception at the sweep seam.
- **Cleanup stays keyed to hard-scope only.** It never consults `salience_selected`;
  a below-cap-but-hard-in-scope case keeps its committed predictions and simply
  gets no *new* ones.
- **Fail-open**: a legacy row with `salience_selected` unset is treated as
  *selected*, so nothing already committed is ever stranded.

**Production wiring — the live cycle.** The write pass runs inside every
live-channel cycle (`live-poll`), after the polls have ingested the day's
distribution transitions and before the workflow pushes the corpus, so the
committed pointer carries the **post-pass** latch state: every sweep pick is
either selected at the pointer the predict matrix gate reads, or a
cohort-completion pick that gate keeps narrowed rather than admits whole, and a fail-open queue
entry (a never-scored petition queued at transition time) that the same
cycle's pass scores-and-defers is dropped by that read-time gate,
non-destructively. Ordering is the load-bearing detail: the queue-time
deferral check reads
the *pre-pass* latch, so transition routing alone would silently drop a petition
whose first transition and first selection land in the same cycle. The cycle
therefore ends with a **selection sweep**: every selected petition with an open
case-baseline (petition/appeal-kind) event still *owed* a prediction is
re-polled, provisioned, and queued — stalest
first, capped by `salience.sweep_cases_per_cycle` in `config/tracking.yaml`. Owed
is per `(predictor, event)` cell — mirroring the evaluate backlog deriver — so a
case where two of three engines landed and one quota-failed is still swept for
the missing engine, and the per-cell attempt cap `predict.max_attempts_per_cell`
keeps one cell that fails every attempt from re-queuing forever without
suppressing a sibling engine still owed the same event.

**Cohort completion** is the one salience-gate ground on which a *deferred* case
re-enters that sweep. (The sweep admits an unselected case on one other ground,
outside this gate's frame: a granted docket's open merits event, where the Court
has already made the selection this gate exists to make — see
[pipeline.md](pipeline.md).) A petition selected when its run fired can drift below the
capacity line before every engine landed, leaving an open event with a partial
predictor cohort and no path back: its distribution transition has already
passed, and the deferral check refuses it at queue time. So a case the ledger
holds any committed prediction for is admitted as a sweep candidate — admission
only, and deliberately the cheaper question — and on that ground the queue is narrowed to the events that pass **both**
bounds below. The `predict-matrix` scope backstop applies the same two bounds
to a deferred case's *listed* events, so a queued cell and a planned cell answer
to the same test. The two seams are not identical at the edges, and both
divergences refuse rather than admit: the plan seam reads
`corpus.is_salience_deferred`, which treats an unscored row as fail-open
selected and so keeps it whole, where the sweep's own predicate counts it
unselected and narrows it; and a request listing *no* events is dropped outright
at the plan seam rather than narrowed, since an unlisted request asks for
defaults, which is a request for new cells. A deferred case with no prediction at all is never a candidate, and the
per-cell owed check and attempt cap apply unchanged — so a complete or
poison-pilled cohort is not swept either.

The **spend bound** is the first: only the case's already-predicted events are
queued. Finishing a cohort buys the missing engines on a case the project already
funded, while the case's *untouched* open events would be new cells on a case the
gate declined. This half mirrors the evaluate backlog's reading of the same gate
(a prediction on a since-deferred case must still be graded): selection funds
forecasts, and it does not un-fund one already made. The mirror reaches the
funding question and stops there — grading scores a fixed artifact, while cohort
completion mints a new forecast at a new information set, which is what the
second bound answers.

The **comparability bound** is the second: an event qualifies only if its
existing cohort is one a claimable board will count once the event resolves and
is graded — at least one committed prediction on it in the **frozen process
scope** ([process-version.md](process-version.md)),
keyed per predictor on the latest run, the same rule the boards' scope gate
joins on. Without it the carve-out would defeat its own purpose. The completing
cell is stamped with a blessed digest at a post-freeze instant — so long as the
running process's digest is blessed, which a re-bless window briefly suspends —
and so lands inside the frozen partition; if every sibling on the event sits outside it —
an unstamped pre-freeze run, say — the board does not gain a completed cohort at
all. It gains an event on which one engine is scored and its rivals are
structurally excluded: the differential-coverage shape
[../metrics/README.md](../metrics/README.md) refuses to license a cross-engine
claim over, manufactured rather than inherited. An event no board counts is
better left uncounted than half-counted.

**What completing a cohort still costs in comparability.** Passing both bounds
does not make the completed cohort a like-for-like comparison; it makes it one
worth having. Three residues remain, and a number read off a completed cohort
carries all three.

- **Information asymmetry.** The completing cell is minted later than its
  siblings, the cert petition baseline is the one moment that is *not*
  cutoff-placed (it reads the latest snapshot), and the sweep re-polls the docket
  immediately before queueing. So the late engine forecasts from a strictly
  fresher docket — at unequal information, **in a direction the record does not
  establish**: fresher is not monotonically better, and nothing here measures the
  sign. The ordinary missing-engine retry has the same asymmetry, and it is not
  bounded either: the daily `predict_queued_at` debounce bounds re-queue
  *cadence*, never the age of the skew, and the per-cell attempt cap counts
  committed `attempt.json` facts, so a whole-engine gap that recorded none never
  reaches it at all. What separates the two is when they start. The ordinary
  retry begins within a day of the gap appearing; cohort completion is the path
  that reaches a gap already weeks old, which is where the skew is widest.
- **Band and base-rate divergence.** `PredictionContext` is derived from the
  provisioned snapshot payload and the salience band only ever strengthens, so a
  cell provisioned from a fresher payload can freeze a stronger band than its
  siblings. Its `brier_skill_score` is then scored against a different
  `segment_base_rate`, possibly under a different basis. Nothing prevents this:
  the base-rate section below enforces the *intra-cell* pairing (a basis that
  carries its version, a band that matches the cell), and the cross-cell rule —
  that a figure is only comparable within one basis — lives in
  [../metrics/README.md](../metrics/README.md). Two siblings on one event
  carrying different bands is exactly the case neither guard covers, which is
  why it is a residue rather than an error.
- **It is only identifiable where every cell carries `context`.** The honest key
  to "this is a completed cohort" is the spread of `context.snapshot_date` within
  the event's cohort; run-id spread is not the key, since ordinary cohorts
  already span run ids within hours. Cells written before the harness wrote a
  `context` block carry no such date, so for those the asymmetry is not
  recoverable from the artifact at all — which is a further reason the
  comparability bound refuses them.

The same sweep is the catch-up for petitions whose transitions all predate the
first applied pass, and the retry for a selected petition whose queued run left a
cell without a committed prediction; the `predict_queued_at` stamp the routing writes with every
queue entry debounces that retry to daily, so an open-but-unmerged run PR is not
re-queued every cycle. Document provisioning follows the same gate: a deferred
petition's transition fetches nothing, and its documents are provisioned by the
sweep — when it is latched, or when cohort completion admits it.

**The relist requeue cooldown.** A **relist** — a distribution transition on a
petition already distributed before, as opposed to its first distribution — inside
`salience.relist_requeue_cooldown_days` (default 1) of the case's last
`predict_queued_at` stamp is treated as administrative churn rather than a
materially different posture, and is not requeued: the divert is surfaced on
`predict_skipped_relist_cooldown` for triage, never silently dropped, and it
re-stamps `predict_queued_at` (anchoring the next cooldown check and keeping
the same-cycle sweep from immediately re-queuing what was just suppressed). The
default suppresses only a same-day repeat — a petition re-tournamented hours
after its first prediction, the observed failure mode — while a relist the
next day or later queues normally. Only applies under the gated scope with a
salience config in force (capacity actually enforced); `0` disables it.

## Replaying the gate

Because `sal-v1` scoring is a pure function of a row's features — and
selection a pure function of a cohort's — the frozen gate can be **replayed
over past Terms at reconstructed moments**: `fedcourts salience-replay`
projects each of a named Term's resolved, live-slice, paid modern-cert
petitions to the state its docket disclosed at a chosen cutoff
— petition **arrival**, the **first distribution**, or the **last
pre-resolution distribution** — and runs the same selection core the live pass
runs (`plan_cohorts`) over the projection, into `metrics/salience-replay.json`.

The projection layer (`fedcourtsai.pipeline.asof`) is the honesty mechanism:
time-invariant identity (docket number, fee class, originating court, sampling
weight) is copied from the row, the docket-acquired signals (relists, CVSG,
the conference cohort) are re-derived from a point-in-time payload via the
same parsers the predict cell's conditioning context uses, and every outcome
and latch field is nulled. A payload that discloses no proceedings projects as
**unobservable** — unknown posture, never banded, never selected — and the
reconstruction reuses the cert back-test's leakage machinery (redaction,
date-keyed truncation, the dated-snapshot preference, the fail-closed
disposition scan), so the two replays share one definition of a
point-in-time docket.

What the report shows, per (Term, policy, salience version): the would-have-been selection
split into carve-outs and rank fill, where capacity actually bit, the band and
provenance mix, and sample-weighted precision/recall of the selection against
the realized grant-family outcomes. The arrival cells quantify the gate's
structural degeneracy — the primary signals the score turns on are
docket-acquired (the circuit rides only as a bounded nudge that can never move
a band or clear the floor), so at arrival every observable projection reads
baseline and nothing is selected — and the
resolution cells bound what the carve-outs would have caught. The same
population frame and cutoffs are what a full predict/evaluate backtest over a
past Term inherits. What the numbers may and may not be read as:
`metrics/README.md`.

## Capacity `N` — the funding knob

`N` is the parameter that scales *how many events* are forecast, and the mechanism
the budget's "more funding = more cases" equation and the milestones' funding
milestone both hang on. It is one of two dials on inference cost — the registry
size `P` sets what one event costs, and takes over once `N` reaches full
paid-gate coverage ([budget.md](budget.md)). It is a **per-conference** config
value, and raising it **deepens the
salience-ranked slice rather than changing the ranking**. The **OT2026 default** is
sized to the **bootstrapping** budget — the flagship three-engine release fits the
~$18.5K envelope: ≈$13K inference at the $15 planning rate with the active
scorer's arrival cohort included (~$11.1–11.5K for the escalation program alone) — **12
per regular conference and 24
for the long conference** (double, because that one cohort clears the summer
backlog at once). The caps are sized to **bind**, and the gate replay at this
capacity (`metrics/salience-replay.json`, sal-v1, OT2022–24) measures that they
do: the mean replay-reconstructable conference cohort runs ~37–38 petitions
against a cap of 12, and the cap binds **29 of each Term's 33–36
reconstructable first-distribution cohorts**. The measured yield is **495–522
selected petitions a Term** — rank fill 398–413 plus floor/CVSG carve-outs of
97–115, riding above `N` uncapped — carrying **0.76–0.81 of the Term's
replay-reconstructable grant-family outcomes** (grant denominators 90/108/91
for OT2022/23/24, GVRs and summary reversals included). Of those grants, 4/6/3
a Term sit on blind rows — no reconstructable selection moment, so no gate
could select them — leaving selectable denominators of 86/102/88: recall of
the *selectable* outcomes is 0.80–0.84, and 0.944–0.967 is the achievable
ceiling at any capacity (the prior committed replay, at the then-shipped
150/200 caps on this same pool, measured exactly that ceiling), with the
carve-outs supplying most of the grant coverage
([budget.md](budget.md) works the decomposition). A per-conference cap
matches the Court's cadence and scopes replay to one conference's candidate pool;
the long conference carries a larger `N` so a flat cap does not under-serve it. At
the top of the same dial, `N` = "every eligible event" makes salience purely the
public ranking rather than a spend control. `budget.md` works the `N → funding`
math; this doc owns the default and the knob's semantics.

## The big-case score (a pre-registered stakes opinion)

A field on `prediction.json` — `big_case_score` (0–1) plus an optional one-line
rationale — capturing the predictor's view of the case's **stakes / importance /
newsworthiness, decoupled from grant likelihood**. Define it as *significance if
decided*: a case can be denied yet high-stakes and closely watched, or granted yet
narrow and technical, so the score carries information beyond `probability` rather
than shadowing it.

It is **judged by an independent evaluator, not against a ground truth**. At
evaluation the evaluator forms its **own** read of how big the case is, and the
grade is the *agreement* between the predictor's pre-registered score and the
evaluator's independent read:

- The evaluator's read must be formed **before** it is shown the predictor's
  number, or it anchors and the agreement is circular.
- Under cross-evaluation this yields a **panel** of independent reads per case;
  aggregate against the panel to damp single-judge noise.
- The evaluator is a **judge, not a forecaster**: it may use post-decision context
  available at evaluation time (the outcome, the immediate reaction). This is the
  mirror of the leakage rule — press coverage is the classic post-hoc salience
  proxy, forbidden as a *predictor* input but fair as *evaluator* context.

Both scores are 0–1 absolute, but the meaningful signal is **ordering across the
cohort** ("big relative to this term's docket"), so leaderboard aggregation uses
**rank-agreement** across the evaluated set, not only per-case absolute deltas.

## Base rates & baselines for the predicted segment

Salience gating makes the predicted population a **biased subsample** — high-relist
and CVSG petitions dominate the selected slice and grant far above the ~1–3%
whole-docket cert rate. So the docket-wide base rate is the wrong anchor for both
consumers that need one: the **prediction agent** (its prior) and the **evaluator**
(the naive baseline a real forecast must beat). Both need a base rate conditioned
on **the segment we predict on**.

**The leakage constraint is the crux.** The statpack is a pure function of the
whole committed corpus — it has no clock. Leakage-safety comes solely from the
**per-Term self-selection surface**: a replay/back-test cell restricts itself to
Term rows strictly preceding its `DECIDED_BEFORE` clock. Today that per-Term
surface carries only *overall + per-fee-class* grant rates; the relist/CVSG cuts
are **pack-wide marginals blended across all Terms** and would leak the current
term's outcomes if a replay cell read them. Therefore the segment base rate **must
live in the per-Term surface**, keyed by a deterministic salience-score band, so it
inherits the per-Term self-selection contract. A pack-wide segment section may also
be published for the current-term human board, but only the per-Term cut is
replay-safe.

The base rate then flows to both consumers on the same footing as the grant/deny
prediction's timing contract:

- **Predictor** — reads the committed statpack (no per-case provisioning) and
  anchors on the selected-segment per-Term rate, adjusting from the case's own
  relist/CVSG/circuit/fee-class detail.
- **Evaluator** — scores a **Brier skill score / lift vs the segment base rate**,
  so a prediction that merely parrots the base rate earns ~zero skill and a genuine
  edge shows as positive lift. The leaderboard carries the aggregated
  skill-vs-baseline column, **per stratum** — so a forward cell's skill lands
  there, aggregated as a population ratio of summed Briers rather than a mean of
  per-cell ratios. Beside it the board publishes a second, deliberately **ex-post**
  column: the same band scored against the rate the case's *own* Term realized,
  leave-one-out, which nets out level-knowledge and leaves discrimination. It is
  a board-only figure — no cell records it, no predictor could have known it,
  and it never ranks — with its claim contract in
  [metrics/README.md](../metrics/README.md). The ops dashboard reports the selected segment's size and its base grant
  rate, and compares predictions to that baseline **for the replay stratum
  only**: its calibration block filters to retrospective cells before averaging,
  so no volume of forward grading ever fills that line. Replay cells come from
  the cert back-test, not the evaluate channel.

**The lookback window is a stated choice, not a default.** The band rate is pooled
over prior Terms — but *how many* prior Terms is a real parameter, and it moves the
anchor. Per-Term high-band grant rates over the walked range (OT2017–OT2025),
on the **`sal-v4`** segments the committed pack is rendered against, run
**24.5%–42.3%**, a ~1.73× spread. The pack's `sal-v1`/`sal-v2` alternative
segments give materially different high pools, while its `sal-v3` block is
`sal-v4`'s pool wearing `sal-v3`'s name — the pack bands every registered
version off the single stored `distribution_count` column, so an alternative
block cannot exhibit a parse effect. Read the version before the number,
know the block does not record its parse, and read every figure here against
the pack's own vintage. Nothing
reachable sits above `high`, so that is its **risk-set** range as well as its
terminal one; elevated runs 13.2%–19.2% on the risk-set rate a
forecast is scored against (6.9%–13.1% on the terminal rate the same table shows
in the lead column — see below). Those risk-set figures are what the
reachable-ladder pooling produces. Anchored at an OT2026
petition, the high band reads roughly **35.5% (n=923)** pooling every prior Term,
**36.4% (n=505)** over the last five, and **≈42%** over the last one — a Term
still resolving (64 of OT2025's 80 high-band petitions resolved), so the
shortest window's anchor is censored as well as thin — recompute from the
statpack's per-Term band table rather than quoting these. That is a
~7-point spread in the number a forecast's Brier skill is scored against, and in
the prior a cell is told to start from, turning on a parameter — and the
per-Term range above is wider still, so the parameter is stated rather than
left to a default.

**Two rates per band, and which one is scored depends on how the band was
obtained.** A band only ever strengthens — the distribution count is max-latched
and a CVSG date, once set, stays set — so a band re-derived at evaluation is the
band a petition *ended* at, while the band frozen on the prediction is the one
the cell faced. The statpack publishes both rates against each band: the terminal
one over petitions that ended there, and the **risk-set** one over every petition
that ever reached it. A cell carrying a frozen band **under a resolvable
salience version** is scored against the risk-set rate, because that is the
population it belonged to; a cell that froze no band at all
falls back to the terminal band and the terminal rate, which at least agree with
each other. The version is the operative key rather than the band, because a
band name means something only under the version that assigned it — a frozen
band whose version is absent or unmatched yields **no** baseline, never a
terminal relabel (see the version pin below). Reading either rate against the other kind of band is the error the
pairing exists to prevent — the risk-set rate against a terminal band overstates
the baseline for exactly the petitions whose band moved, and the terminal rate
against a frozen band understates it several-fold in the weak bands.

**A risk set walks the petition's reachable ladder, not the band order.** The
caption-banded versions read two features of different kinds: `federal` and
`state` come off the caption, which is fixed at filing, while the relist/CVSG
tier only ever rises. So the class *partitions* the band vocabulary rather than
sitting inside it, and each class walks its own ladder — `federal` alone;
`state` → `high`; `baseline` → `elevated` → `high`. A federal petition is
therefore in no weaker band's risk set (it was `federal` on day one and no
trajectory could have taken it elsewhere), a state one is in none of `federal`'s,
`elevated`'s or `baseline`'s, and a private one is in neither caption band's. Each class's
weakest reachable band carries that whole class, so the three floors — `federal`,
`state`, `baseline` — partition the scored segment instead of nesting into one
another, and a band with nothing reachable above it has its two rates coinciding
exactly: `federal`, and `high`, which is the ceiling of both the state and the
private ladder. Pooling the band order's prefix instead would price a private
petitioner's forecast against a population containing every federal petition —
the class with the highest grant rate on the docket. The ladder is registered
with the band rule it belongs to (`SalienceScorer.reachable`, read through
`reachable_bands`), so a version that bands on one monotone score alone — `sal-v1`
— keeps the whole vocabulary reachable and its risk sets stay the plain
cumulative prefix.

**The pool is version-pinned, and a lagging statpack yields no baseline rather
than a blended one.** A band name is meaningful only under the salience version
that assigned it — a `sal-v2 high` and a `sal-v1 high` are
different populations that happen to share a label. So every band-rate entry
point pins the version — the two scored baselines
(`fedcourtsai.pipeline.evaluate.segment_base_rate` and
`fedcourtsai.pipeline.base_rates.prediction_base_rate`, through the pooler they
share), and the board's ex-post
`realized_band_rate`, which pins identically on its single Term. They read
**only** the statpack
Terms whose `salience_version` matches the version that produced the band
(the frozen `PredictionContext.salience_version` on the risk-set path; the
live scorer's version on the terminal path), and when no Term matches, the
baseline is `None` — the same contracted no-baseline answer as a case with no
prior-Term data. On a statpack that lags the band's version both paths are
version-starved, so `brier_skill_score` is omitted rather than computed
against a number no version ever defined; and in the mirror case — a pack
already re-rendered under a newer version while an old frozen-band cell is
scored — the risk-set path yields `None` and **that is the whole answer**. The
cell records no `segment_base_rate` and no skill, and flags the mismatch. It
does **not** fall back to the terminal band: `terminal` is the basis for a
prediction that froze no band at all, and relabelling a frozen band's cell as
terminal would pair a risk-set population with a terminal rate — the several-fold
mispairing the two bases exist to keep apart — while stamping the *live*
scorer's version onto a cell banded under an older one. The evaluator
prompt carries the agent-side half of the same rule, in the same terms: the
rendered band table's heading names its salience version, and where that does
not match the prediction's frozen `context.salience_version` — or the
prediction froze a band with no version beside it — the agent omits the baseline
and flags it rather than pooling from a table another version rendered. The
harness holds the same line from the other side, and it is worth being
exact about which parts: a recorded `risk_set` basis whose version resolves to
**nothing** fails the cell at the stamp, so a versionless frozen band cannot
pass as a scored cell — and a recorded `terminal` basis while the prediction
froze a band **at all** fails the same way, so the relabel is machine-refused
rather than merely forbidden, whether or not the band's version resolves.
`validate`'s `base_rate_basis_carries_version` holds both refusals over the
merged ledger, so neither shape rides a green cell into `main`. A version that
resolves but does not *match* the pack's rendered one passes both — there the
omission is prompt discipline rather than an enforced rule, and the
discipline is what this paragraph registers. The
operational consequence is deliberate: after a salience version ships, forward
cells scored under it have no skill baseline until the statpack re-renders
under the same version, and that gap is visible instead of silently papered
over.

The tension is bias against variance, and it has no free answer. Per-Term
high-band samples are small (64–133 weighted-resolved petitions), so a short
window is noisy: two Terms gives n=176. Pooling every prior Term buys n=923 and a
stable estimate, but assumes the Court's grant behaviour is stationary across the
whole range — and the spread above cannot adjudicate that either way: at 64–133
petitions a Term the widest per-Term deviation is about 2.2 standard errors over
nine looks, which is what a constant rate produces as often as a drifting one.
The window is therefore stated rather than defaulted, and no skill claim rests
on which of the two is true. Two second-order effects push the same way. The bands are frozen per version, and each per-Term entry
carries its own `salience_version` — the field the version pin above reads, so
cross-version pooling is impossible at any window length and the window carries
no versioning duty. And the pooling weights are
`weighted_resolved`, not `resolved` — identical on every segment of the current
pack, whose walked Terms are denial-complete censuses, but they diverge wherever
a Term's walk was sampled, so a long window compounds Terms whose walk coverage
differs.

So the window is **config, not a constant**: `salience.base_rate_lookback_terms`
in `config/tracking.yaml`, where `0` would mean every prior Term. It is set to
**10**, matching `statpack.markdown_terms`, so the scored baseline and the band
table the agents anchor on share one window by construction and cannot silently
diverge as walked Terms accumulate; with nine Terms walked the bound excludes
nothing, so every published skill number is what the unbounded pool produced.
The choice is on the record and a change to it is
a reviewable diff rather than an invisible shift in every published
skill number. It is counted in Term *years*, not statpack rows: a Term absent from
the pack, or present only as a zero-row cursor entry, shortens the sample rather
than pulling an older Term in to refill the slot, so the window cannot move as the
walker's coverage changes.

**The scored baseline and the anchor an agent reads share the window by
configuration, not by mechanism.** The
baseline is computed in code
(`fedcourtsai.pipeline.evaluate.segment_base_rate`) and honours
`salience.base_rate_lookback_terms`. No agent runs that code: every agent that
needs a prior — the forward predictor and evaluator, and the cert back-test's
replayed predictors, which run the same prompt — reads the band table in
`metrics/statpack.md`, so its window is whatever that table renders, capped by
`statpack.markdown_terms` (default 10). The bound is conventional, not a capability
limit: `statpack.json` sits in the same checkout and carries every Term, and the
prompts are what direct anchoring at the table.

With the walked range at OT2017–OT2025 the pack holds nine Terms, nothing is
truncated, and the two windows **coincide** — and because both knobs read `10`,
they keep coinciding when the pack passes ten Terms, instead of parting inside a
single back-test run where a replayed agent would be scored against a Term it
was never shown. Both knobs are stated so the pair is moved — or deliberately
split — as one decision rather than two accidents. Both per-Term captions in
`statpack.md` state the rendered window, so a truncation is visible to the agent
reading the table rather than silent.

The ops dashboard's segment rate is a **third, different number**: pack-wide,
blended across every Term and unmasked by any clock (`fedcourtsai.ops`). It is an
operational statistic for the human board, never the scored baseline, so neither
knob applies to it.

### Scope: SCOTUS cert only, deliberately

The segment baseline is **not** generalised to other courts, and that is a
decision rather than an omission. Circuit rows are ingested for retrieval context
and never predicted; when they enter prediction scope they will need a skill
baseline, and this one does not translate. Three of its four load-bearing parts
are SCOTUS-cert-shaped by construction:

- **The Term is the leakage control**, not a label. Pooling Terms strictly before
  the case's own is what makes the anchor replay-safe, and `segment_base_rate`
  returns `None` without one. A circuit docket has no Term, so an equivalent
  guard has to be built from something else — a rolling window on the decision
  date is the nearest candidate, and a calendar year is not a natural unit of
  appellate practice the way a Term is for the Court.
- **The trajectory bands do not generalise at all.** Relist count, CVSG presence
  and originating circuit have no circuit analogues — there is no relist, no
  CVSG, no court below in the same sense, and no IFP serial convention to read
  the Tier-0 fee-class exclusion from. A circuit band function is a new scorer over
  different features, not a re-parameterisation.
- **The outcome is a different act.** `granted` means cert was granted on a
  SCOTUS row and a motion was granted on a circuit one. A circuit baseline has to
  choose which binary it estimates before it can estimate a rate, and the useful
  one is probably affirm/reverse — which no column carries cleanly today.

What *does* generalise is the **per-court always-deny floor**, which
`metrics/backtest.json` already reports per court. That is the reason the cut is
per-court rather than SCOTUS-only: a circuit predictor gets an interpretable
floor the day it runs, with no new machinery.

So the near-term position is that circuits are covered by the floor and by
nothing else. Publishing a cross-court "segment base rate" would produce a number
that looks comparable between courts and is not, which is worse than reporting
none — the same reasoning the generic back-test applies in declining a segment
baseline of its own.

## GVR as a first-class label

A grant/vacate/remand — and especially a Munsingwear vacatur, where the Court
grants and vacates because a case became moot — conflates *cert-worthiness* with
*vacatur practice*: the disposition tracks the Court's housekeeping wording, not
whether the question was worth deciding. The prediction vocabulary makes GVR a
**first-class predictable label** so an agent can forecast a GVR specifically
rather than folding it into an undifferentiated "granted."

- The realized-outcome vocabulary gains a **`gvr`** disposition. The Munsingwear
  *mootness* sub-type stays encoded by the existing `Outcome.disposition_basis`
  (`gvr` + `mootness` = a Munsingwear vacatur, segmented into the procedural
  leaderboard stratum; `gvr` + `standard` = a merits GVR). There is no separate
  `vacated-moot` label — the basis attribute already carries that distinction.
- **A GVR still counts as a grant on the binary axis** (`gvr` joins the granted set
  for `actual_granted`), so `probability` (P(granted)) and the Brier score remain
  **fully comparable across all history** — the binary axis is the comparability
  anchor; only the disposition-label axis gains the new value.
- **Migration is a forward-convention change, not a retroactive relabel.** New
  resolutions label a GVR `gvr`; outcomes recorded before the label keep `granted`,
  because retroactively flipping a decided outcome would penalize a past
  `granted` prediction for using the *then-current* vocabulary. `correct` is no
  defence there: it is stamped from the outcome, so a re-stamp after a relabel
  would recompute it — what protects the past cell is that the relabel does not
  happen, not that its bit could not move. The one exception a one-time
  deterministic backfill *can* fix
  from committed data alone is the **identifiable Munsingwear vacatur** (`granted`
  + `mootness` basis → `gvr`), which is already in the non-ranked procedural
  stratum and unranked whatever its bit says, so no published metric moves —
  and nothing re-stamps it in any case. A plain-`granted` **merits** GVR in history is an
  accepted residual — indistinguishable post-hoc without re-resolving the source
  docket text (the `outcome.json` does not carry it), and immaterial on the binary
  axis.
- **A mislabel is not a vocabulary artifact, and the separation between them is
  drawn in code — by a date where nothing better exists, and by the docket's own
  order text where it does.** The residual above is what the convention
  protects: a cert
  label normalized from the upstream record's own fields, which never passed
  through the disposition parser at all, so `granted` there is a faithful record
  of what the older vocabulary could say. It does not cover a resolution the
  parser itself recorded by reading the docket's order text and got wrong. Two
  shapes do that. The **prose GVR** names the lower court between the grant and
  the vacatur, and fell to the cert-before-judgment grant row until
  `cert_signals._gvr_tail_sentence` closed the gap. The **ancillary-order grant**
  is read off text that decides nothing about the petition, in either of the two
  shapes `cert_signals._is_non_order_sentence` refuses: an order *about* the
  petition rather than one on it — an extension of time to respond, a delayed
  distribution, an unsealing — or a docketing recital, whose disposition word is
  quoted or conditional inside a sentence ending "filed". Both disagree with their own
  order text rather than with a superseded convention, and one order can sit
  behind both labels, so leaving them makes the ledger contradict itself about a
  single day's work. `converge-disposition-labels` converges them, re-resolving
  the stored docket text and rewriting only what the parser confirms.

  The separation is enforced in its predicate, not left to which snapshots
  happen to be stored, and each shape meets it on its own terms. For the prose
  GVR the boundary is the date: outcomes resolved before
  `disposition_convergence.PARSED_ORDER_TEXT_SINCE` are reported and never
  rewritten, so widening snapshot coverage cannot reach the protected residual.
  The ancillary-order grant carries its own proof of provenance instead — an
  entry *dated the recorded resolution* carries a grant-shaped sentence today's
  parser refuses (`cert_signals.refused_grant_sentence`), and nothing anywhere
  on the docket parses as a grant any more, so an order sat there and the label
  was read out of a sentence the parser will not stand behind — which is a
  parse gap with a date on it rather than a vocabulary flip, and is correctable
  however old it is. Requiring that refused sentence, rather than merely an
  entry on the day, is what keeps the warrant honest: a real grant whose order
  text the payload does not carry would otherwise be withdrawn on any unrelated
  entry sharing its date. The warrant fails two ways, each reported as the one
  it was: the docket still parses a grant somewhere, or the label's provenance
  cannot be established at all — no entry on the recorded date, or entries with
  nothing a grant could have been read from. The warrant is the
  arm's whole licence, so a fuller snapshot store buys text to judge and never a
  way past it. The penalization worry does not reach either
  class — their labels were the parser's reading of an order, not the best word
  an earlier vocabulary offered — and any candidate already carrying committed
  predict *or* evaluate output is held back by default, since an evaluation's
  `correct` bit was stamped from the label being corrected; `--include-scored`
  opts in and reports the re-grade the relabel creates.
- **Routing.** "Is this a likely GVR / mootness-prone case" is a genuine routing
  signal, but deterministic **pre-decision** detection does not exist today (a
  strategically-mooted case reveals itself only through docket text that no
  extractor parses). So the near-term fold-in is the **model-produced** call — the
  predictor forecasts `gvr` when it reads the posture that way, and the big-case
  score captures the stakes — with deterministic mootness-proneness deferred to a
  possible later scorer version.

## The interim docket (predicted, quota'd; its estimator registered and wired)

The cert program above selects petitions. The interim docket — stays,
injunctions, vacaturs pending certiorari — needs its own, because no
trajectory feature exists there: an application is not distributed for
conference, and a CVSG is a cert-stage act. (The caption class *does* exist
on an application, but every band's base rate is a cert-petition population,
so banding an application on caption alone would be the same mismatch.)
Reusing the band would be the
conditioning mismatch this document spends its length warning about.

**Most of the docket is not the thing predicted.** Over the 1,797 parsed
application dockets — every walked Term pooled, though seven of the ten
contribute none and OT2025 alone is 76% of the total — **81.9%** are requests
to extend the time to file: granted
by a single Justice as a matter of course, with nothing about the case moving
the answer. **13.9%** are substantive and **4.3%** carry an ask the parser
cannot read. The cohort accumulates with every walk, so recompute these from
the statpack's `interim` section rather than quoting them. Admitting the whole docket would hand a
predictor a base rate it beats by answering "granted" every time — the IFP
problem in a sharper form. `interim_signals.is_predictable_application` keeps only
the substantive ones, and excludes an unreadable ask with them: that is a parser
gap, and shrinking coverage visibly is better than admitting a matter of unknown
character into a scored population.

**The escalation ladder is the salience structure.** Three signals are readable
from the proceedings before an application resolves:

| signal | what it is |
| --- | --- |
| the Court **requests** a response | an affirmative act of attention — the interim analogue of a CVSG, and *not* the same event as a response arriving uninvited |
| the application is **referred to the Court** | the full bench takes it, rather than a Circuit Justice acting alone — which is also what selects the aggregation rule |
| **amicus briefs** filed | a proxy for stakes, counted rather than flagged — per docket *entry*, so it is an approximation: an entry naming several filers counts once, and a few matched entries recite the phrase without being briefs |

The three sampled substantive applications separate on exactly that ladder — a
two-entry summary denial with no signals, a referred denial with a response
filed, and a granted application that drew a requested response, an amicus brief
and oral argument. That is a suggestive shape and **not a base rate**: three
observations cannot support a rate, and none is published or scored against.

**The two traps transfer unchanged.** All three signals are monotone over an
application's life — the Court does not un-request a response, un-refer an
application, or un-file a brief. So the band derived at resolution is the band the
application *ended* at rather than the one a cell faced, and a rate conditioned on
the ending band understates what a live application faces. Those are the same two
defects the cert program corrected, and the answers carry over: freeze the band as
at prediction, and pool the rate over a risk set.

**Predict scope is the substantive slice, funded by a bounded reserve inside
`N`.** Only a substantive application
(`interim_signals.is_predictable_application`) is ever predicted — the scope
rules keep extensions and unreadable asks excluded, and the next run of the
two-directional reconcile releases an application's latch once a poll has
latched its substantive reading. Selection is a **quota, not a ranking**: the trajectory
features do not exist here, so each selection pass fills up to
`salience.interim_reserve_slots` (5) with pending substantive applications in
**escalation-ladder order** — requested response first, then the amicus
count, `case_id` for determinism. The referral signal sits on the ladder as
an observation but not in the pick order: a referral usually arrives *as* the
disposition entry itself, so it carries no forecast horizon — a slot it
earned would fund a prediction of an already written order. The pick order is
a deterministic *pick sequence*, not a scored rate: choosing by the ladder
asserts no grant probability. Its rungs are the max-latched columns, so they are
as fresh as each row's last poll: two applications alike on the docket can order
by which the rotation reached more recently, and any change in how the
proceedings text is read reaches the pending cohort one poll at a time rather
than all at once. A selected application occupies its slot until
it resolves (the sticky latch never de-selects), so the reserve bounds
*concurrent* live interim predictions and a slot frees only on resolution —
where "resolves"
means the machine-matched resolution the accumulation rule below requires, so
an application decided in language the vocabulary misses pins its slot until a
maintainer resolves the residue;
it is visible as the application rotation's long-unresolved tail. The slots in
use lower the cert **rank-fill limit** one-for-one in the **latest
conference cohort of the pass** — never a carve-out — so the reserve is defined
inside `N`. Whether it *spends* inside `N` depends on the cohort: a lowered
limit costs a real cert pick wherever the *eligible* non-carve-out remainder
exceeds it — at the shipped capacity a full reserve leaves a rank fill of 7,
far below the ~37–38-petition mean replay-reconstructable cohort, so a full
reserve would displace a pick at essentially every capacity-bound conference;
the displacement *frequency* itself is unmeasured, because the gate replay
runs with no reserve occupancy ([budget.md](budget.md)). An
unfilled reserve lowers nothing. Where it does bite, it bites prospectively, pass by
pass: a cohort whose rank fill latched *before* a slot was occupied keeps its
sticky picks, and an application queued in the fail-open window before its
first scoring pass rides outside the quota for that cycle — both can push a
conference's realized count transiently above `N`, the same drift-above-`N`
the carve-outs and sticky latch already produce. The predict trigger is the
interim analogue of the
distribution transition: an application has no conference calendar, so any
observed docket change on a still-unresolved substantive application in scope
queues its motion/interim baseline forward, debounced to daily by the shared
`predict_queued_at` stamp; the selection sweep addresses reserve-selected
applications too, since a selection can postdate the application's last
docket change. A machine-matched resolution then records the interim
`outcome.json` on the same baseline — the interim disposition vocabulary,
dated by the disposing entry, carrying the interim escalation block
(`interim_signals`) in place of the cert-only `signals` one.

**The cohort keeps accumulating, and both ends of a claim are now committed.**
The live
cycle re-polls unresolved applications up to a small per-cycle cap
(`live.max_applications_per_run`). Each poll persists the ask
(`application_kind` — arrival-time,
so safe to condition on) and the three ladder signals as latched corpus
columns, so an interim cohort can be assembled from the index: which
applications, which asks, how far each had escalated by resolution. The latched
signals are the *ending* band — the thing the two traps above forbid
conditioning a rate on directly — so the as-at-prediction values a valid rate
needs are re-derived from the provisioned snapshot and frozen onto the cell's
own `PredictionContext`, while the ending values are frozen onto the
`outcome.json` as `interim_signals`. That pair is what makes an interim
increment claim resolvable at all
([outcome-decomposition.md](outcome-decomposition.md), *The declared interim
set*). One caveat bounds the accumulation itself: an
application counts as resolved only when the interim disposition vocabulary
matches its disposing entry, so the resolved set is selected for
machine-matchable resolution text (an unmatched resolution stays in the
rotation as a visibly long-unresolved residue rather than silently counting).
The cohort is published — the statpack's interim section carries the counts by
ask, the substantive slice's resolved/granted counts and raw grant rate, and
the escalation-signal counts, pack-level and per application-Term (the amicus
column there counts applications carrying **at least one** brief, not briefs —
the count itself stays on the corpus row) — and its
**per-Term entries are what the scored baseline pools**:
`segment_base_rate` takes an application arm keyed on the `YYAnnn` Term
(`base_rates.interim_base_rate`), which is the estimator registered below. The
pack-level rate beside it stays descriptive and is never the baseline, because
it contains the case's own Term. The leaderboard still segments an interim cell
into its unranked `interim` stage block rather than the cert board: the two
stages resolve on different standards over different populations, and a shared
ranking would compare them. The predict and evaluate prompts carry the
agent-side half of the claim set, and it moved on its
own re-bless (`docs/process-version.md`), because a prompt edit moves the
pre-registered process digest: from that re-bless forward an interim cell
answers all four `interim-v1` claims and anchors on this estimator by name. The
**baseline** never depended on that re-bless, because it is not the evaluator's
to record: `stamp-cell` writes an interim cell's `segment_base_rate` from the
estimator above — keyed on the application Term the scored prediction froze —
together with the `brier_score` it recomputes from the scored prediction and
the committed outcome and the `brier_skill_score` derived from those two,
overwriting whatever the cell carried — and clearing `base_rate_basis` with
them, so the null the
interim pool (no band product) requires is structural rather than a rule an
evaluator has to honour.
**Pre-registered claimability rule:** the stage stopped being descriptive-only
once the statpack's substantive **resolved count reached 25** — a condition on
the *stage*, long since satisfied, and not on any individual cell. Whether a
given cell gets a baseline is the separate per-pool floor registered below, and
that is the one that binds today. The estimator was pre-registered with the
stage rule, because the forking paths close now or never: the rate is
pooled over the **substantive resolved slice of application-Terms strictly
before the case's own** (the same leakage rule the cert band rate uses),
**unweighted raw counts** (the application stream has no denial sampling, so
every row stands for itself), with withdrawn/dismissed counted as ungranted
and the machine-matched-resolution selection caveat traveling with the number
wherever it is quoted. Two collapses in the resolved labels are likewise
recorded here rather than discovered later: an unmatched resolution never
enters the denominator (the accumulation rule above), and a mixed partial
disposition — "granted in part and denied in part", a real shadow-docket
shape — currently reads **denial-first** through the interim vocabulary and
lands as `denied` / ungranted; if that collapse proves material once volume
exists, changing it is a new reading applied forward, never a silent
relabel. The floor, the estimator, and the collapses are fixed here, before
any interim cell has been scored, so none can be tuned to a result. The
**merits** stage's baseline is registered the same way and likewise wired — the
statpack merits section's disturbed rate pooled strictly-prior
(`docs/decision-model.md`).

**Pre-registered: the per-pool floor is 50 resolved.** The pack-level count
above governs when the *stage* stops being descriptive-only; this governs
whether any individual cell gets a baseline at all. `interim_base_rate` returns
a rate only where the **pooled strictly-prior** substantive resolved sample
reaches `INTERIM_BASE_RATE_MIN_RESOLVED = 50`. The figure is derived, not
preferred, and it is deliberately not the 30 its cert and merits siblings use.
Thirty rests on an absolute standard-error argument, which is tolerable where
the baseline enters as a *difference* (the claim rule's `(b − y)² − (p − y)²`)
or as the denominator of a ratio at a rate near one half. Neither holds here.
This baseline's principal consumer is `brier_skill`, whose denominator is
`(b − y)²`; the modal interim outcome is a denial, so on most cells that
denominator is `b²`. Squaring **doubles** the relative error transmitted from
the rate, and — unlike per-cell noise — it lands on every cell's denominator at
once, biasing the published mean rather than averaging out of it. Holding the
transmitted relative error at or under one third therefore needs
`n ≥ 36(1 − p)/p`: 36 at `p = 0.5`, 84 at `p = 0.3`, unbounded as `p` falls.
**The criterion cannot pin a number, and 50 is not claimed to satisfy it.** It
is monotone decreasing in `p` and unbounded, so at the rates this docket has
actually shown it asks for roughly 231 resolutions at the pooled 13.5% and
roughly 364 at a single Term's 9%; 50 clears it only for `p` above about 0.42.
What the criterion establishes is that **thirty is too low here**, and what 50
buys is stated exactly: an absolute standard error of at most 0.071, inside the
bound the siblings accept at thirty (0.091). So the figure is chosen on the
siblings' own absolute-SE standard at a tighter tolerance, with the
relative-error argument as the reason for tightening rather than as a bound it
meets. The floor
binds on the **pooled** sample, so it clears by accumulation exactly as the
merits floor does. Below it there is **no baseline and no substitute**: not the
pack-level rate (it contains the case's own Term), not a single Term's, and not
the cert band table (a different population on a different standard) — the cell
carries a null skill, visibly, rather than a borrowed number. Its effect today
is that no single-Term pool qualifies, which on the committed pack is the whole
of the live docket: an OT2025 application's only strictly-prior contributor is
OT2024's 44 resolutions, so **no currently predictable application carries a
baseline at all** until OT2026 opens and OT2025's own resolutions join the
pool. That effect is **accepted rather
than incidental**: 50 was chosen with the committed pack visible, and the
criterion's own value at `p = 0.5` (36) would have admitted the one single-Term
pool that exists. What is *not* registered is a companion "at least two Terms"
condition — considered and **rejected**, because a
second parameter with no derivation behind it, chosen in knowledge of which
cells it would exclude, is a forking path however reasonable it sounds.

**Pre-registered: `base_rate_basis` stays null on every interim cell**, as it
does on every merits cell. Both of the field's literal values name
salience-band populations, and the interim pool is not a band product — an
application freezes no band by rule, so there is no band whose population the
basis could be naming. Adding a third value would redefine the field from
"which band was this scored against" to "which pool", orphan the role of
`base_rate_salience_version` beside it, and widen a published `Literal` for a
distinction the record already carries: the **stage axis on the event** says
which pool a cell was scored against, and it says it for every cell rather than
only the ones that got a baseline. `base_rate_salience_version` stays null
beside it for the same reason — the interim estimator is version-free, because
there is no scorer to version.

**Pre-registered: the pooled population is wider than the scored one, and the
gap is recorded rather than corrected.** The estimator pools the whole
strictly-prior substantive slice, while the cells scored against it are the
reserve's occupants — and the reserve fills its bounded slots in **escalation
ladder order** (a requested response first, then the amicus count). A predicted
application therefore sits systematically higher on those rungs than the cohort
behind the rate: of the accumulated substantive slice only about a fifth (53 of
257, `metrics/statpack.json` as refreshed 2026-08-24) ever
drew a response request, while a reserve-selected cell is frequently picked
*because* it did. The baseline is unconditioned on the ladder and the scored set
is selected on it, which is the outcome-decomposition register's test 3 answered
in the negative. Two consequences travel with any interim skill number: it is
**not by itself evidence of forecast skill** — a positive value is consistent
with the reserve's pick order alone — and the conditioned rate the claim really
wants is not derivable from any committed cut, because the pack publishes no
ladder-by-grant cross-tab. Conditioning the pool on the rung frozen in the
cell's own context (which now carries it) is the registered **next** estimator,
applied forward as a new reading, never a silent re-reading of this one. Two
further selections ride the counts themselves and belong beside any quoted
figure: resolution is machine-matched, and **parse coverage is uneven across
application-Terms** — the live poller reaches recently-active applications, so a
Term it reached late contributes a subsample rather than a census, and a pooled
rate blends Terms of unlike coverage. That unevenness is the leading candidate
explanation for the spread between Term rates, and no interim comparison should
treat that spread as a change in the Court's behaviour.

The three decisions are fixed here, before any interim cell has been scored, so
none can be tuned to a result.

## Shared discipline: leakage / timing

The deterministic salience features and the predictor's big-case score both rest on
**pre-conference / pre-decision** material only. Allowed predictor signals: the
docket facts (relists, CVSG, circuit, fee class, questions presented, the petition
and brief in opposition). Forbidden on the predictor side: the post-hoc press proxy
and anything dated after the event — the same signals the evaluator *may* use as a
judge. This makes both scores' timing contract identical to the grant/deny
prediction's, so they slot into the existing forward/replay frame with no new
machinery: a forward cell computes them live, a replay cell self-selects its
statpack Term rows behind the `DECIDED_BEFORE` clock.

"Live" is per **moment**, not per wall clock. A stage's moments are declared
because their information sets differ, so `provision-snapshot` places a forward
cell whose `--event` names a declared moment at that moment's cutoff — the day
after the event opened — and derives the frozen conditioning from the cut
payload like any other. The band therefore states the trajectory as at the
moment being forecast, not as at the day the cell happened to run, and a merits
cell run months into briefing is banded on what its grant-moment docket showed.

The cert petition **baseline** is the one moment not placed this way, and the
exception is that one moment rather than the cert stage: its opening date is
docketing rather than the distribution its moment declares, so cutting there
would delete the relist history the band is made of, and it reads the latest
snapshot. The stage's `cvsg` and `arrival` moments are placed like any other —
an arrival cell is banded on a docket with no distribution yet recorded, which
is what `arrival` declares — as is the interim application baseline, whose
declared moment *is* arrival. `context.cutoff` separates the two conditionings:
non-null where a moment placed the cell, null where nothing did.

For those two cert moments the placement moves the **base rate**, not just the
description. The cut removes the relists filed after the trigger, so the frozen
count and therefore the band are the ones the petition had at the moment — and
since the band is the key the risk-set rate is chosen on, a placed cell is
scored against a different anchor than the same petition banded at its terminal
posture. That is the intended reading (the rate a petition at *that* band
actually faces), and it is why a band must never be pooled across the cutoff
boundary. The merits moments differ: distributions are a cert-stage signal that
stops at the grant, so a merits cell's band is near enough invariant under
placement and what the cut removes there is the merits calendar.

## Where it plugs in (seams)

- **`scope.json`** records each entry's `salience_score`, `salience_version`, and
  `salience_selected` as the published transparency artifact — but only for cases
  that already have a committed `data/cases` directory (its enumerate-from-the-tree
  invariant; it never scans the corpus). It is a *record*, not an input: no pipeline
  seam reads it back to drive selection. The **full candidate pool** —
  including Tier-0-excluded and below-cap cases that have no committed
  directory — belongs on the salience board (below), not here.
- **The selection is driven by the `salience_selected` corpus latch**, not by
  reading `scope.json`. `predict-matrix`'s scope filter consumes the latch
  directly, the same way it consumes `predict_excluded` and the court predicate
  today.
- **Hard eligibility** stays in `corpus.OUT_OF_SCOPE_RULES` /
  `out_of_scope_reason_full` (the IFP rule among them). Below-cap selection is a
  **separate** latch and never enters this evaluator.
- **The salience ranking** has no published board yet: the scores and the latch
  live in the corpus and reach git only through `scope.json`. The planned
  artifact is a deterministic board under `metrics/salience.{json,md}`,
  regenerated like the other roll-ups — the pre-registered big-case board,
  carrying the ranking, the full candidate pool, the selected set, and the
  segment base rate ([milestones.md](milestones.md)).

## Ratified decisions (config, tunable)

The knobs are settled for the first release; each is config, so changing one is a
config edit, not a redesign. `N` **is a guaranteed floor, not a hard ceiling** —
the posture below keeps selection additive and never destructive:

- **Capacity `N`** — per-conference, OT2026 default 12 / regular conference and
  24 / long conference (the bootstrapping envelope above). The caps sit well
  under the raw median ~34-petition paid cohort and well under the pool the
  replay ranks — the mean replay-reconstructable conference cohort runs ~37–38
  petitions — and the gate replay at this capacity measures the cap binding
  **29 of each Term's 33–36 reconstructable first-distribution cohorts** across
  OT2022–24 (`metrics/salience-replay.json`; [budget.md](budget.md)); carve-outs ride
  above `N` untouched, the interim reserve's slots in use trade inside it, and
  the cert rank fill is what remains. The Tier-0 IFP filter shapes that pool too,
  and it is larger than it sounds — measured on the accumulating OT2026
  long-conference cohort, **roughly two thirds** of the petitions distributed
  are IFP and leave at Tier 0, so the eligible pool is about a third of the
  raw distribution volume. Read a raw distribution count as a *ceiling* on the
  candidate pool, never an estimate of it — and re-measure the ratio rather
  than assuming it holds, since it is a property of who files, not of the
  pipeline.
- **Carve-outs sit above `N`** (not consuming it): CVSG and above-floor cases are
  guaranteed in, and `N` still fills with the next-best ranked cases, so no major
  case is ever crowded out.
- **Mid-cycle arrivals: additive-above-N** — a late high-salience petition is
  simply selected too (consistent with the sticky, never-de-select latch); no
  reserved headroom.
- **Unspent capacity is never reclaimed** — a small conference may under-fill `N`;
  reclaiming would break per-cohort replay reproducibility.
- **`sal-v1` weights are fit to the empirical per-bucket grant rates** (above); the
  salience floor sits at the relist-2 / CVSG grant-rate band (~25%+). Exact
  coefficients are pinned in the implementing change.
- **The segment base rate's lookback matches the agent-facing window** —
  `salience.base_rate_lookback_terms: 10` equals `statpack.markdown_terms: 10`,
  so the scored baseline and the band table the agents anchor on share one
  window; with nine Terms walked the bound excludes nothing. Both are stated so
  the pair can be moved together, on evidence, in one reviewable diff (*Base
  rates & baselines for the predicted segment* above).
- **The segment baseline stays SCOTUS-cert-only** — the Term is its leakage
  control, the `sal-v1` bands have no circuit analogue, and `granted` names a
  different act on a circuit docket. Other courts are covered by the per-court
  always-deny floor and nothing else, because a cross-court "segment base rate"
  would look comparable between courts without being so (*Scope* above).
- **The `big_case` grade is rank-agreement across the cohort** (bigness is
  comparative), with a per-case absolute delta kept only as a secondary diagnostic.
