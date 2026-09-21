# Metrics

Pipeline metrics: small, deterministic, git-tracked roll-ups whose reviewed
diffs track predictor and corpus quality over time.

**Process scope: frozen vs alpha.** Every claimable figure here about
*predictor performance* is scoped to the **frozen** process partition
([docs/process-version.md](../docs/process-version.md)): a cell counts toward
a frozen-scope performance artifact only if its **prediction's**
`process_version` stamp carries a digest in `FROZEN_PROCESS_DIGESTS` with a
stamp at or after the `FROZEN_SINCE` freeze instant — the partition keys on
the prediction because the predictor is the competitor being ranked; the
evaluator's own digest is recorded and never enforced for counting — *and* the
evaluation's own harness stamp is at or after that instant (the stamp, never
the agent-written `created_at`: the boundary rests only on clocks the agent
cannot write), both constants set in the
pre-registration commit the `prereg/<label>` tag marks. Everything else in
`data/` is the **alpha/shakedown ledger** — cells written before the stamp
existed (they carry no `process_version` at all; the absent stamp is the
marker), or run or graded before the freeze instant, or stamped under
predictor digests a later freeze deliberately retired: a
**declared-shakedown cohort**, whose period is describable as a beta only
because its declaration — a dated entry in the freeze record — preceded the
outcomes of the claim window it governs (*the third supersession shape* in
[docs/process-version.md](../docs/process-version.md); the declaration
itself states any slice whose own outcomes had already resolved). For such a
cohort the exclusion takes effect at the retiring freeze, not at the
declaration: between the two, committed frozen-scope artifacts still count
the cohort, and the declaration is what marks their figures as shakedown
reading in the meantime. Alpha cells stay
committed with their timestamps, but they are **excluded from every
frozen-scope performance artifact and from any claimed performance result** —
they exercised the pipeline while the process was still moving, and nothing
about them was pre-registered. `leaderboard.json` and `claim-scores.json`
publish which scope they were built under as `process_scope` (`"frozen"` or
`"all"`); an `"all"` build — the `--all-versions` CLI toggle — is a
diagnostic view, never a results surface.

**One prediction per predictor per event, and re-predicting a live event is a
registered rule.** A predictor may hold several committed runs on one event —
a re-queue after a failed cell, or a deliberate re-forecast — and the board
reads exactly one of them: the run the grading evaluation's harness-stamped
`prediction_run_id` names, falling back to the predictor's **newest** run where
that field is absent or the run it names is not on disk. So the staged and scored cell is the
newest one, and an earlier run is history that no figure counts twice.

That matters because a predictor-half re-bless de-counts every cell stamped
under the retired digests, including cells on events that have **not yet
resolved**. Those events would otherwise be consumed for nothing: graded on
resolution, then dropped from this scope, leaving the frozen board with no
population at all. The predict backlog therefore **re-owes** a cell on a
still-forward event at a still-open moment whose whole committed cohort is
retired ([docs/pipeline.md](../docs/pipeline.md)), so the cell that is
eventually graded was produced under a blessed process. Two readings this does
**not** license. It is not a re-grade: nothing about an existing evaluation
moves, and `superseded_gradings` is untouched. And a rise in any figure across
the re-predict boundary is **not** a measurement of model improvement — the two
sides are different processes on different information sets, which is the whole
reason the partition exists. Nor is the resulting board a sample of the docket
or even of its own conference: the first frozen cert population is **n = 110
cert/distribution events, all distributed for 2026-09-28** (70 baseline, 37
elevated, 1 high, 1 federal, 1 state), with 10 cert/cvsg (all high band) and 2
interim events beside it. It spans bands — the salience funding line does not
cut it, because the re-predict rule re-owes a wholly retired cohort on a
declined case too — but it is **110 of the 180 in-scope petitions** distributed
for that conference (557 distributed in all), being the previously-predicted
residue of earlier funded rounds, and so is selected **upward on band**: 63.6%
baseline against the in-scope conference's 76.7%. Read it on the **per-band
cut**, never as a pooled row, against the registered sal-v4 segment base rates —
always-deny floors of 94.98% baseline / 83.11% elevated / 64.49% high / 29.21%
federal / 76.37% state, the risk-set family the evaluator scores skill against
(`metrics/statpack.md`'s *Segment base rate by salience band*, not its terminal
composition table). Its high band is **n = 1 on cert/distribution and n = 10 on
cert/cvsg**, which do not pool with each other, and none of it pools with any
`"all"`-scope board. That paragraph travels with the number rather than sitting
a section away, because it is the number's population.

And a third reading the boundary does not license: **a cohort complete on the
board is not the same as a cohort complete in fact.** The rule's moment gate
closes with the conference, so a cell that fails on the last tick before it
cannot be re-minted afterwards, leaving an event with some engines blessed and
some retired — per-predictor cells over *different event sets*, which the
ranking (N-unweighted point estimates) cannot show. A figure over such a cohort
is published over the events carrying every blessed engine, or it prints the
per-engine `n` and the complete-grid `n` beside it.

The cohort rule, its exclusions and its expected
size are pre-registered in [docs/freeze-record.md](../docs/freeze-record.md)
before any of its outcomes were observable; that entry, not this paragraph, is
the record. The prediction census and the
leakage digest deliberately stay version-blind (they are plumbing
diagnostics, and shakedown contamination is exactly what the leakage digest
exists to surface), and the corpus-descriptive artifacts here — the statpack,
the docket pack, the salience replay — carry no process version at all: they
are facts about the corpus, scoped by their own salience version and vintage.

The offline gate
(`fedcourts corpus-status`) checks that the five gate-tracked artifacts —
`leaderboard.json`, `claim-scores.json`, `backtest.json`, `statpack.json`,
`statpack.md` — exist
and are committed. Others land here without being gate-checked:
`cert-backtest.json`, which only a released replay writes, `docket.{json,md}`,
which is regenerated on demand by `fedcourts docket`, `big-cases.{json,md}`,
which the daily `big-cases` lane keeps current on its own cadence, and
`salience-replay.json`, produced on demand by the free, deterministic
`fedcourts salience-replay` (locally, or via the `run-backtest` dispatch's
`replay: salience-gate` mode, landing as a reviewed PR), and
`semantic-grades-<stratum>-<scope>.json`, which `fedcourts semantic-summary`
writes **only** when the semantic census clears both preconditions below — it
is outside the gate precisely because its absence is a state the contract
requires, not a missing artifact. One resident is a **record, not a roll-up**:
`arrival-backfill-membership.json`, the durable copy of the arrival repair's
filled-membership list (the enumeration `docs/freeze-record.md`'s apply entry
requires committing before its source object lapses). It is written once and
never regenerated — its diff is not a quality signal — it is never a
predictor-performance surface, and nothing may be claimed from it beyond the
population identities it preserves. The gate's presence check
tracks the set the weekly refresh regenerates, so an artifact outside that set
stays outside the gate:

- `backtest.json` — results of replaying predictors against historical *resolved*
  events in the corpus (outcome hidden at predict time, scored against the known
  `disposition`): per predictor, disposition accuracy, binary granted accuracy,
  and the mean Brier score of P(granted). `fedcourts backtest` produces it —
  a deterministic, offline replay over the corpus —
  empty (zero counts) until a corpus with outcome labels is present. **Labeled
  retrospective by construction** (see the stratification note below): every
  replayed event resolved long before any modern model's training cutoff, so the
  figures measure recall and calibration over known history, never foresight.

  **Each entry carries the always-deny floor and the lift over it, per court and
  overall.** Raw accuracy here is close to meaningless alone: a constant predictor
  scores its slice's base rate *exactly*, so `constant-denied` posting a high
  accuracy is arithmetic, not skill. The floor beside it is what makes the number
  readable — a lift of zero says the predictor learned nothing. One structural
  case to read differently: `prior-vote` retrieves on shared judges, and SCOTUS
  rows largely carry none, so on that court it votes the whole-history majority
  — `denied` — and its lift is ~zero *by construction* rather than by failing to
  learn. There is nothing there to retrieve on. What it still measures on SCOTUS
  is calibration: P(granted) and the Brier score.

  **Read the per-court cut, not the pooled row.** The pooled figure is dominated by
  whichever court supplies the most resolved events, and that court's floor may be
  near zero, so a pooled lift can average away a severe failure on the population
  that is actually predicted. It also mixes outcome vocabularies: `granted` means
  cert was granted on a SCOTUS row and a motion was granted on a court-of-appeals
  docket. The overall row is a reference point; the per-court rows are where floor
  and lift are comparable.

  Lift is **presentational** — entries still rank on accuracy then Brier, because
  ranking on a pooled floor that spans those vocabularies would promote an
  incomparable number to the headline. Skill against a *leakage-safe* baseline, with
  the salience adjustment, is `cert-backtest.json`'s job on the predicted
  population; this one is the broad reproducibility floor plus enough context to
  read it. One asymmetry worth knowing: this artifact refreshes on every
  scheduled metrics pass, while `cert-backtest.json` moves at most once a
  fortnight and only when a maintainer releases the replay's hold — it spends
  tokens on agentic replay — so cert-scoped skill against a leakage-safe
  baseline is a sampled retrospective series with declared gaps, never a
  continuous or claimable one.
- `leaderboard.json` — predictors ranked best-first from the evaluations ledger
  under `data/`, with the committed `statpack.json` as a second input (the
  realized-Term skill column below is scored against it at build time): per
  predictor, accuracy, mean Brier score, mean vote accuracy — over the declared
  **merits** moments and nothing else, because an individual cert vote is never
  scored (`docs/decision-model.md`), so the ranked cert board carries no vote
  mean — a mean reasoning-quality summary, and counts (events scored,
  evaluations) reported **per stratum** — the `forward` and
  `retrospective` timing blocks plus the basis-driven `procedural` block,
  never blended into one number, with only the timing strata ranked. Two counts
  sit on the entry rather than the stratum, because they describe the whole
  entry: `evaluators`, the distinct judges that scored it, and `events_scored`
  pooled across its strata, which the coverage contract below reads against the
  board's own. The **accuracy** column is the mean of each cell's `correct`,
  which the harness stamps on **every** stage — cert included, unlike the skill
  record beside it — from the scored prediction's committed label and the
  outcome's, so the board's first rank key is recomputed from committed
  artifacts rather than taken on the evaluator's word. A cell whose `correct`
  the stamp could not compute (no readable prediction, or no committed outcome)
  leaves both halves of the fraction rather than entering as a wrong call, which
  is what `accuracy_scored` beside the column records; read accuracy against
  that count. Harness authorship makes the number **verifiable, not
  meaningful**: it certifies that the bit reproduces from committed artifacts,
  and says nothing about whether the accuracy it sums to is skill. Read it
  against `population_brier_skill_score` and that column's own `skill_scored`,
  never alone — on the cert board a predictor that denies everything scores the
  denial rate, so an accuracy near it is the **floor**, not performance, exactly
  as the back-test section below states the rule for a constant-`denied`
  predictor. Each
  stratum block reports `skill_scored` beside `population_brier_skill_score` — the
  skill figure's true denominator (the cells carrying a non-null skill score),
  which can sit far below `evaluations` because a cell scores skill only where
  a segment base rate exists; read the figure against that count, never against
  the stratum's evaluation total. A cell also drops out of that count when its
  recorded skill does not reproduce from its own recorded base rate and Brier:
  the published figure is computed from those inputs, and `Evaluation`
  constrains no relation between its numbers, so a record that disagrees with
  itself is omitted rather than published on a baseline it was never graded
  against. That coherence check is the only one, and what it guards in
  practice is the **cert** cell, because it is the only stage whose numbers are
  the evaluator's arithmetic at all: on a **merits** or **interim** cell
  whose `event.yaml` names its stage, `stamp-cell` writes all three together —
  `brier_score` recomputed from the scored prediction's probability and the
  committed outcome, `segment_base_rate` pooled from the statpack, and the
  ratio over them — so they agree by construction and there is no hand-computed
  number left to catch. Reproducing from the record is not the same as being
  right, which is why the numerator is stamped too rather than checked: a skill
  derived from an unverified Brier would satisfy the coherence check and still
  publish the wrong number. The cert numbers stay the evaluator's
  because they alone require a judgment — which band population the rate is
  taken over, recorded in `base_rate_basis` — while both pooled rates are a
  ratio of published integer counts with nothing to decide.

  **One grading per cell per judge.** A re-graded cell commits a second
  `evaluation.json` beside the first, and both describe one observation, so
  every figure on the board — the counts, the means, both skill columns, and
  both agreement views — is taken after the ledger read collapses to one
  evaluation per (case, event, predictor, evaluator): the newest on the
  harness clock (`fedcourtsai.integrity.evaluation_clock` — the process stamp,
  with the agent-written `created_at` only where no stamp exists, which the
  frozen scope excludes), ties broken deterministically, and the collapse
  applied inside the scope so a re-grade outside the frozen partition cannot
  displace the frozen grading it superseded. **`superseded_gradings` is what
  the collapse dropped from the stratified pass that produced the ranked
  cells** — the two agreement views collapse separately, over their own scope,
  and are not in the figure. It is the board's only trace of a re-grade: a
  survivor is indistinguishable from a cell graded once, and every figure
  around it is already post-collapse, so re-grading — a maintainer-reachable
  operation — could otherwise move a standing with nothing on any published
  artifact recording that it happened. It does **not** cover an **in-place
  rewrite**: running `stamp-cell` again over an existing `evaluation.json`
  rewrites `correct` — the first rank key — *in place*, on the same file, so no
  second grading exists, nothing is collapsed away, and `superseded_gradings`
  stays where it was. Two operations hide under that, and they part on whether
  a **judgment** changed.
  A new judgment — the same cell graded again under a changed rubric, prompt,
  or registry — is a second observation, and its honest route is a second
  `evaluation.json` from a new evaluator run, which the collapse counts and
  this figure then records; never a bare re-stamp of the existing one, which
  would move a standing with nothing published saying so.
  A **corrected outcome** is not a second observation. `correct`, the claim
  block, and the skill record are deterministic functions of the committed
  artifacts, so re-committing an outcome changes those functions' *inputs*
  while nothing about the grading run changes: minting a second
  `evaluation.json` would fabricate an observation for the collapse to count,
  and would copy prose its agent wrote under different ground truth. It would
  also convert a ground-truth correction into a **process** change: a genuine
  evaluator re-run resolves a *current* stamp — `stamped_at` moving across
  `FROZEN_SINCE` and the digest to today's registry — which migrates the cell
  into a pre-registration cohort it was never produced under, and that is the
  decisive objection, not merely the copied prose. The
  sanctioned route there is therefore in place — `stamp-cell --regrade`, which
  recomputes exactly those harness-owned fields and preserves the producing
  run's process stamp — and its two trades are worth saying plainly. It leaves
  **no** `superseded_gradings` trace, so `data/`'s git history is the only
  record that the numbers moved. And the recomputed `claim_scores` and skill
  fields pool from the **statpack committed at re-grade time**, not the one the
  stamp dates, so a re-graded set is comparable within itself and should be
  re-graded together against one pack. What the ledger gate catches of a
  partial recompute is narrower than it sounds:
  `evaluation_correct_agrees` holds the **`correct` bit only**, and only inside
  a `(case, event, predictor)` group where two or more evaluators left stamped,
  non-null gradings — so a lone judge's cell, or a recompute that leaves
  `claim_scores` and the skill record stale while `correct` agrees, passes it
  clean. The whole-event discipline is the operator's; the gate is the backstop
  for the one bit the accuracy column averages. Read it as an
  audit line, never as a
  term: it is **not** subtracted from any count on the board, and a count
  plus it is not a ledger total. Its population is the **scope gate's**, which
  is the board's process scope but a slightly wider set of cells. The scope
  half is exact: the collapse runs after the gate, so a `frozen` board's figure
  counts only supersessions among frozen-scope cells and a re-grade the freeze
  excludes appears on the `--all-versions` board instead. The cell half is
  wider in two ways. It is stage-blind like `forward_claim` (a superseded
  grading shares its survivor's stage), so it spans the ranked board and every
  `stages` block at once and must never be netted against a stage-scoped
  total. And it is taken where the collapse runs, which is *before* both
  exclusions — the forward-claim rule and the leakage bit — exactly like
  `claimed_forward` and `assessed` beside it, so a supersession
  of a cell an exclusion then drops is counted while the cell itself reaches
  no block, and a board reading `predictors_ranked: 0` can still carry a
  nonzero count. Nonzero is not by itself a fault — a
  re-grade is a legitimate operation — but it is the cue to ask **why** a cell
  was graded twice before reading a standing that a re-grade could have moved.
  Read it beside the scope, because a zero has two meanings: on an empty
  frozen board — the committed state while no stamped grading has yet reached
  the population the board ranks — nothing was in scope to supersede, so `0` is the
  shakedown state rather than a clean audit, and re-grades in the shakedown
  ledger are counted on no committed artifact at all. `--all-versions` is where
  they show. The collapse stops at the
  evaluator: a panel of judges reading one prediction is several observations,
  which is what `evaluators`, the panel means, and the leave-one-out agreement
  figures measure. (`claim-scores.json`'s *aggregates* collapse one step
  further, to the event, for a reason that does not apply here — every
  evaluator of one prediction carries an *identical* harness-computed block, so
  there is no second observation to keep. Its judge validation stays per cell.
  The ops report's substance funnel reads the same collapsed pass and publishes
  no count of its own; the board's is the audit line for all three, since one
  collapse rule builds them.)

  **Check coverage before comparing two engines.** Grading is gated at
  `(evaluator, event)` grain: a run gives a judge the events it has not graded
  yet, so a prediction committed after that judge graded its event is never
  scored by that judge — only a judge still to reach the event can pick it up.
  The scored set
  is therefore **selected, not sampled**, and the selection can fall
  differentially — an engine whose cells backfill late accumulates
  systematically fewer scored events than one that ran on time, and nothing in
  the ranking, the means, or either skill column adjusts for that. Each entry
  publishes its own `events_scored` and its population publishes the
  `events_scored` union across entries. An entry **at** its population's
  figure was scored on the whole set — the entry's events are a subset of the
  union, so equal cardinality is equal set — and an entry **below** it was
  ranked over a subset. Never sum the **entries** to recover that union: two
  predictors scored on one event are one event, so the sum overstates it.
  (Summing an entry's *stratum* blocks is a different matter and does
  reproduce its figure — a predictor's strata partition its events.) A
  cross-engine claim over unequal coverage is a claim over two different
  populations and is not licensed by this artifact; where the coverage is
  unequal, the honest reading is per-predictor coverage figures, or a
  comparison restricted by hand to the events both engines were scored on. The
  denominator is the events *someone* was scored on: an event nobody was scored
  on leaves numerator and denominator alike and is invisible here, so this
  measures coverage **relative between entries**, never coverage of the
  predicted population. The absolute gap — a prediction carrying no evaluation
  at all — is still a ledger scan (`fedcourtsai.matrix.event_has_evaluations`
  names the seam it comes from).

  **Equal coverage is necessary, not sufficient.** It certifies the same event
  *set* and nothing else, and two residuals survive it, so equality is never
  on its own a licence to compare. **Stratum mix**: `events_scored` pools
  forward, retrospective and procedural, while the rank key is the forward
  stratum — two entries at equal coverage can carry a forward block against no
  forward block at all, which is not a comparison. **Panel depth**: the gate is
  per judge, so a late prediction can still be picked up by a judge that has
  yet to run, on a thinner panel — equal coverage with unequal `evaluations`
  or `evaluators` means the two means are taken over differently-weighted
  cells. Read each stratum's own `evaluations` and the entry's `evaluators`
  beside the coverage figure, and require both entries to carry a non-null
  `forward` block over the same events before any forward comparison. The
  pre-registered form of the condition is per-stratum, per-(predictor, event,
  evaluator); this artifact publishes the pooled grain, which is why it can
  refuse a comparison but never bless one. The build says so out loud — `fedcourts leaderboard` warns per
  population, naming each short predictor and its coverage — so the hazard does
  not depend on a reader doing the subtraction, and the refresh PR's headline
  flags it too. One absence shape only the refresh PR's line catches: a
  configured predictor with **no entry at all** in a populated block (the shape
  an engine-wide outage produces) is invisible to the build warning, which
  iterates the entries that exist; the refresh line checks the configured
  roster and names the predictor and the block. Each `stages` block denominates its own coverage the same way,
  against its own entries and never the cert board's, and is warned on
  separately: a stage is scored on its own events, so measuring a merits entry
  against the cert union would report short coverage for every one of them.

  **The board also names its partitions.** `frozen_process` records the freeze
  constants in force at build time — the blessed digest set and the freeze
  instant — so *what was blessed* is readable from the artifact rather than by
  resolving the build's commit back to `fedcourtsai.process_version`. The
  digest list pools predictors and evaluators; only the predictor subset is the
  enforced membership filter, which the flat list does not distinguish. It also
  drops the per-digest **bless moment** the constant carries beside each entry —
  that moment bounds retroactivity, not counting, so it changes no figure on the
  board; read it off `fedcourtsai.process_version` or the dated entry in
  [freeze-record.md](../docs/freeze-record.md). It
  appears on every build, an `"all"`-scope
  one included, as the partition's definition rather than a claim it was
  applied (`claim-scores.json` carries the identical block; null on a
  board built before the record existed). `forward_claim` sits beside it —
  the forward-claim integrity rule the build applied and how many cells it
  caught (the exclusion defined beside the strata below) — and
  `leakage_exclusion` beside that, the leakage bit's own count, denominator and
  per-predictor split. The two are independent rules over one population, so a
  cell both caught appears in both counts and neither may be subtracted from a
  board total nor summed with the other. And `salience_versions` lists the distinct
  salience versions the ranked cells' baselines were read under. The gate is
  not part of any actor's process, so a change to it moves **no process
  digest** and the frozen/shakedown partition cannot see it — but it decides
  which petitions earn cells at all, so two versions on one board mean the
  aggregates pool two differently-gated **populations**. More than one entry
  therefore demotes the means to coverage figures, exactly as
  `declared_set_versions` does for a claim total. This is a rule for the
  reader, not a partition the code applies.

  Beside it runs a second, complementary skill number —
  `population_realized_term_skill_score`, with its own `realized_term_skill_scored`
  denominator. Same band, same basis, same formula; only the baseline differs.
  Where `population_brier_skill_score` scores against the **strictly-prior** pooled
  band rate (leakage-safe, and the primary outcome measure), this one scores
  against the grant rate the case's **own Term** actually realized, computed
  **leave-one-out** so a case never sits inside the rate that scores it. The two
  **decompose skill, per cell**. Prior-Term skill rewards knowing the level
  *and* discriminating within it, so a Term that runs hot or cold credits or
  penalises every predictor for the shift. Realized-Term skill holds the level
  at what obtained, nets the level out, and leaves **discrimination**: a
  predictor with the Term's level right but no ability to tell its cases apart
  scores positive on the first and ~0 on the second, and one that beat history
  while losing to the Term scores positive then negative. That sign
  disagreement is the point of publishing both. (A predictor that merely
  parrots the *historical* rate scores exactly 0 on the first — that is what
  the prior-Term baseline means — and, on average wherever the Term moved,
  negative on the second.)

  Three things sharpen the "~0". The attainable level-only null is **not** 0
  but `(2n − 1) / n²` for a band of weighted `n` — the score of a forecaster
  reporting the band's *published* rate, which contains its own case: about
  +0.03 at n = 64 and about +0.06 at the floor of n = 31. (A forecaster
  reporting the case-excluded level would score exactly 0, but reaching that
  level requires knowing the case's outcome, so it is an oracle rather than a
  null.) More generally the correction is the exact rescale
  `skill = 1 − (1 − skill_uncorrected)·((n − 1)/n)²`, so it never reorders
  cells within a band — but the shift it applies, `(1 − skill_uncorrected)·(2n
  − 1)/n²`, is bounded only at the null: Brier skill has no lower bound, so a
  badly negative cell moves much further than the figures above. And the two
  published **figures** run over different cell sets — the qualifying rules
  below are narrower in practice and never the same set, since
  `base_rate_basis` is the evaluator's own field and inclusion is therefore a
  convention rather than a construction — so the decomposition is a statement
  about a cell, never a licence to subtract one column from the other.

  **Both columns aggregate as a ratio of sums, not a mean of per-cell
  ratios**: a stratum's figure is `1 − Σ(cell Brier) / Σ(cell baseline Brier)`
  over the cells that column scores. The distinction is load-bearing under
  cert's class imbalance, because the per-cell skill ratio caps at +1 but is
  unbounded below, so a mean of ratios is dominated by the many low-baseline
  denial cells and pays a predictor to under-forecast the rare event.
  Illustratively, on three of the `sal-v4` pack's five OT2025 risk-set
  segments (every cell scored against its band's own OT2025 reached rate `p`,
  over that band's risk-set population — whose grant share is `p` by
  construction, which is what reduces the whole computation to two closed
  forms: the mean of per-cell ratios is `1 − p/(1−p)²`, the ratio of sums
  `−p/(1−p)`; a self-consistent illustration rather than a leakage-safe
  baseline): the mean of ratios prices an always-deny forecaster at
  **+0.96** in the `baseline` band (`p` = 3.9%, n = 1132), **+0.825** in
  `elevated` (13.19%, n = 273) and **−0.26** in `high` (42.2%, n = 64 — the
  thinnest cell, in a Term still resolving) — rewarded exactly where denial
  dominates — while the constant level-only forecaster sits at exactly 0
  under either estimator: definitionally, since it reports the very `p` the
  baseline is computed from, which is the case the leave-one-out null above
  excludes. So the ordering between the two *forecasters* inverts in
  `baseline` and `elevated`, and there it is structural: the closed form is
  positive for any `p` below `(3 − √5)/2 ≈ 38.2%` and negative above, so the
  denial-dominated bands invert under any rate a refresh could print, while
  `high`'s negative sign is a fact about OT2025's 42.2% — its per-Term rates
  straddle the threshold, and that sign does flip across refreshes. The
  ratio of sums prices the same always-deny forecaster at
  **−0.04 / −0.15 / −0.73**, and *its* sign is the estimator's invariant:
  `−p/(1−p)` is negative for every `p > 0`, whatever a refresh prints.
  Re-derive the figures from the current pack rather than quoting them
  across refreshes — the rate is `prefix_est_grant_rate` per band, the
  `[reached …]` bracket in `statpack.md`'s band table. The `population_` prefix on both field names records exactly
  this, against the plain `mean_*` fields beside them (`mean_brier_score` and
  the rest *are* per-cell means), so the estimator travels with the number
  rather than only with its description. One consequence to know when reading
  either figure: a cell whose baseline Brier is zero — the base rate matched
  the outcome exactly — is excluded, since the ratio is undefined there. That
  is right for the ratio but not neutral, because those are the baseline's
  best cells and dropping them nudges the published figure up; the minimum
  resolved count and the leave-one-out range guard make a rate of exactly 0.0
  or 1.0 near unreachable.

  **Never pooled, never a rank key, never in-season evidence.** The two
  baselines answer different questions, so nothing averages, blends, or
  otherwise combines them into one figure, and each is read against its
  own count. The ranking is unchanged — forward accuracy, forward Brier, the
  retrospective pair, then `predictor_id` — and could not include this number:
  it is **ex post**, since no predictor could have known its Term's realized
  rate when it ran, so ordering predictors on it during a live Term would rank
  them on a fact that did not exist at prediction time. Read it as a diagnostic
  of one predictor's discrimination within a band, never as a standing. One
  further asymmetry to hold in view: only the prior-Term half moves with
  `salience.base_rate_lookback_terms`, so a change to that window re-bases one
  member of the pair and not the other, and readings taken across such a change
  are not comparable.

  Scope rules travel with the figure. It is **cert stage only** — no other
  stage has a salience band, so none has a band rate to realize, and every
  non-cert `stages` block reports it null with a zero count (a scope fact,
  not a merits skill rule: merits has no band, so it has nothing to
  realize). It is **version-pinned** exactly like
  the prior-Term pool: a band name means something only under the salience
  version that assigned it, so a Term carrying another version contributes
  nothing rather than a blend. It rests on a **stated minimum** —
  `pipeline.base_rates.REALIZED_BAND_RATE_MIN_RESOLVED`, 30 measured *after* the
  leave-one-out and binding on the weighted denominator **and** the observed
  row count behind it, since a reweighted Term can otherwise clear a weighted
  31 on as few as five real petitions wherever a Term's walk was sampled —
  below which the cell is omitted rather
  than scored on a handful of cases. It bites hardest on a **caption class
  floor**, whose risk set is that class alone rather than every band above it —
  the caption classes are the docket's smallest populations, so `federal` and
  `state` are the columns a Term most often omits. Unlike the prior-Term pool this one is a
  single Term and cannot be widened by reaching further back, so the floor is a
  wait-for-the-Term rule: a band that never clears it is omitted for that Term
  entirely, and early in a live Term the forward cells' own Term is exactly the
  one that has not accumulated, so the first realized-Term numbers to appear on
  a board are typically retrospective cells sitting in closed Terms — read the
  stratum before the number. Coverage is narrower than the prior-Term
  column's for one further reason: only a cell whose recorded `base_rate_basis`
  is `risk_set` is scored, because the `terminal` basis re-derives the band
  from the corpus row, which the committed ledger does not carry — pairing this
  number with a different band population than the one beside it would stop the
  pair being a decomposition. Every one of these is a visible omission in
  `realized_term_skill_scored`, never a silent zero.

  Finally, the figure carries a **vintage**, and mid-Term that is a bias and not
  only a wobble. The board reads the committed `statpack.json` at build time
  rather than a value carried on the cell, because a Term's own rate is
  term-to-date and keeps moving — so every cell on a given board is scored on
  one pack, and the number converges as the Term closes. But a term-to-date
  band rate is **grant-depleted**: grants resolve months after denials (the
  pack's own median days-to-grant runs roughly double its overall median
  days-to-resolution), so while the Term is open the realized level reads low,
  and the resulting error is outcome-dependent — too harsh on denied cases,
  too generous on granted ones — which means it does not average out of the
  mean. Treat an open Term's realized-Term figure as directional; only a closed
  Term's is settled. The leave-one-out itself carries a matching residual: it
  removes one unit of weight rather than the row's own sample weight (identical
  on a weight-1 live Term, short by `w − 1` on a reweighted historical one), and
  on a pack built before the case resolved it over-corrects by one unit —
  bounded by `1 / 30` and self-correcting at the next refresh.

  The ranked board is the **cert stage's first declared moment** (see the stage
  axis note below); every other population — a later cert moment included —
  reports in its own unranked `stages` block. Each entry
  also carries a `big_case` block — the predictor's `big_case_score`
  rank-agreement (Kendall's tau-b) with the evaluator panel's independent reads —
  a second, orthogonal skill dimension that never affects the ranking.
  The board also carries an `evaluator_agreement` map — per evaluator, how far its
  big-case reads track the rest of the panel's, computed **leave-one-out** so a
  grader is never correlated against a mean containing itself. This is the check
  on grader latitude that the per-predictor view cannot make: a uniformly generous
  or strict judge biases every predictor it scores equally, so the distortion
  cancels out of the predictor ordering and shows up only when graders are
  compared to each other. Read it as a property of the **panel**, not of one
  judge: with three evaluators a single dissenting grader sits inside both peers'
  comparison and can turn all three negative, so a low figure locates a
  disagreement rather than assigning blame. It never affects the ranking, and
  `events` beside it is small enough to matter — tau-b over a handful of shared
  events moves a long way on one disagreement.

  Both agreement figures read a judge's **current** read of a case, under the
  one-grading-per-cell-per-judge rule above: the collapse to the newest grading
  runs before the stakes read is looked for, so a judge that re-graded a cell
  without recording a `big_case` block has no current read of it and leaves the
  panel rather than falling back to the read its re-grade superseded. That is
  the honest reading of a re-grade — the newest grading is the observation, all
  of it — but it means a withdrawn read moves `cases` / `events` as well as the
  coefficient, so read the two together.

  Both also run over a **wider population than the ranked figures beside them**:
  they read the ledger directly, so neither the forward-claim exclusion nor the
  leakage exclusion (both below) applies, and a leakage-suspected cell the board
  drops is still a point in these correlations. That is deliberate — a stakes
  read is neither scored nor ranked — but it is a caveat that has to travel with
  a quoted tau, and it bites hardest on `big_case`: a stakes read is partly a
  read of the disposition, so a predictor that saw its own outcome may have read
  the stakes off it too, and over a handful of cases two contaminated points can
  carry the coefficient.
  `fedcourts leaderboard` produces it — a deterministic, offline roll-up of the
  ledger and the committed `statpack.json` — empty (`{}` plus the zero counts)
  until the first evaluation lands.
- `claim-scores.json` — the mechanical claim-score surface: every
  harness-computed `claim_scores` block in the evaluations ledger (minus any
  forward-claim breaching cell and any leakage-suspected one — both exclusions
  apply to every scored surface), rolled up per predictor **per stratum** and
  published beside the leaderboard.
  `fedcourts claim-scores` produces it, deterministic and offline, defaulting
  to the same frozen process scope as the board. While no committed
  `claim_scores` block reaches that scope *and* this surface's population —
  every block committed today is `interim-v1`, and the population is the cert
  stage's first moment only (below) — it renders its honest suppressed state:
  zero counts, every
  coefficient null, and a stratum with no cells at all carrying a null
  agreement record rather than a zero-filled one. The scoring rule, the claim
  declarations, and every
  rule below are pre-registered in
  [outcome-decomposition.md](../docs/outcome-decomposition.md); this section is
  the reading contract. Nothing on this surface is a **placed** cell: it is the
  cert stage's first moment only, and that moment's `opened_at` is the
  docketing rather than its trigger, so provisioning fixes no cutoff and every
  cell of it reads the latest snapshot (`as-stored`, lag 0). The
  provenance-and-lag obligations stated under `salience-replay.json` below
  therefore bind the *other* moments' claim totals — the ones that reach a
  scoring surface through the unranked `stages` blocks — and not this one.

  **Advisory, never a rank key.** Nothing here alters or reorders the
  leaderboard, and the artifact assigns no standings — entries are
  alphabetical. A claim total's variance is unbounded above and a bold
  uninformed spray has a fat right tail, so ranking on it would buy rank with
  variance. The comparison that carries a skill claim is **head-to-head at
  equal coverage**, which cancels the baseline term entirely; nothing in this
  artifact is that comparison, so nothing in it is evidence of case-level
  skill on its own.

  **The total travels with its floor and lift.** Per predictor × stratum the
  artifact reports the mean per-event claim total (Brier units — never bits),
  the mean floor, and the mean lift. The floor is the realized total of the
  baseline-restating control — identically zero by propriety, *computed*
  per block rather than asserted — so it prices baseline-restating and
  nothing else: the information-free expectation from base-rate drift and
  baseline estimation error remains unpriced, which is why a positive total
  or lift is not skill. The **largest single-claim contribution** is reported
  beside the means because extreme baselines pay asymmetrically — one lucky
  surprise can swamp dozens of honest calls, and a total that is one claim in
  disguise must be visible in the same breath. Per-claim means are
  diagnostic rows, never headlines: a claim singled out after the fact
  describes that claim, not the predictor, and a declared claim that never
  scored still appears with `scored: 0` so the coverage gap stays visible.

  **A `cert-v2` mean total is a mixture, and its added addends are selected on
  the outcome.** Under `cert-v1` every cert cell scored exactly one claim, so a
  mean total pooled a single quantity. `cert-v2` adds two claims on complementary
  halves of the disposition: `summary-disposition-route`, which scores only where
  the petition was granted *and* its outcome retained a route marker, and
  `dissent-from-denial`, which scores only where it was denied *and* its outcome
  carries a noted-dissent marker. A cell therefore scores two claims where its
  own half supplied the marker and one otherwise. `declared_set_versions`
  catches a cert-v1/cert-v2 mixture but not this one, because it is a single
  declaration with a per-event denominator that varies with the realized disposition. So the
  per-claim rows with their own `scored` counts are the readable cut, and
  `mean_total` is not comparable across predictors whose scored cells differ
  in grant rate. The floor is identically zero and `lift` is a sum too, so
  both inherit the same property.

  **Counts and comparability.** The population is the **cert stage's first
  moment's** cells: the board never blends stages or moments, so although the
  other two stages declare their own sets (`interim-v1` on every interim
  moment, `merits-v1` on every merits moment), a non-cert cell's block sits
  outside this surface (and
  outside its absence counts) entirely until a per-stage claim surface exists. The reporting unit is the **event**: every
  evaluator of the same prediction carries an identical harness block, so
  blocks are deduplicated to one per event before averaging (the newest
  evaluation's block wins where a statpack revision between evaluator stamps
  ever made copies differ — newest on the harness stamp,
  `fedcourtsai.integrity.evaluation_clock`, never the agent-written
  `created_at`), and `cells` beside `events` is the census of counted
  gradings — one per judge, after the board-wide run collapse above, so a
  superseded re-grade appears in neither; the leaderboard's
  `superseded_gradings` is the audit line for both surfaces, since one collapse
  rule builds them. Strata are never pooled, and a total or pair set is never
  comparable across process versions or across the frozen/all scope: the
  artifact publishes its scope, keyed on the prediction's stamp exactly like
  the leaderboard, and a scope that comes to hold more than one
  claims-carrying process version must not be read as one population. A total
  is likewise never comparable across claim-set declarations —
  `declared_set_versions` lists what the means pool, and more than one entry
  there demotes them to coverage figures. Retrospective aggregates are
  iteration signal under the backtest-as-iteration doctrine below, never
  claimable — a resolved case's claims are retrievable, not forecastable —
  and procedural aggregates never carry a cert-forecasting claim of any kind,
  for the stratum's own reason: a mootness-basis label tracks the Court's
  vacatur practice, not cert-worthiness.

  **A grade formed blind and a grade formed unblinded are two populations.**
  `reasoning_quality` is the semantic side of the judge validation and the
  source of the leaderboard's `mean_reasoning_quality`, and the evaluate cell
  forms it with the predictor's identity masked (`docs/outcome-decomposition.md`,
  *Semantic claims*). A grade formed before that bracket carries an anchor on
  which predictor wrote the rationale; one formed after does not. So a
  `reasoning_quality` mean, or a judge-validation tau-b, whose cells span that
  boundary is not one population and may not be read as one — the same rule
  `declared_set_versions` states for a claim total, applied to the evaluator's
  process. The boundary is visible per cell: the bracket rides a prompt change,
  so it moves every evaluator's process digest. It is not enforced as a
  *counting* partition — the frozen filter keys on the **prediction's** stamp,
  because the competitor being ranked is the predictor — so for pooling this is
  a rule for the reader rather than a partition the code applies. Two
  consequences follow: report the distinct evaluator process digests a pooled
  grade figure spans, and treat more than one as demoting the figure to
  coverage. The same boundary moves the denominator, not only the anchor:
  under the bracket exactly one candidate is staged per predictor, so an
  event a predictor ran twice contributes one grade rather than several.
  (The evaluation digest's *retroactivity* is separately guarded: the
  evaluation-ledger tripwire in `tests/test_process_version.py` fails the
  suite on a stamp that predates the bless moment of a digest currently
  blessed.)

  The anchor is not the only channel the bracket closes, and the second one
  reaches further than `reasoning_quality`. The bracket also takes the committed
  `evaluations/` tree out of the cell's working tree for the duration of its
  run, so a judge cannot read another judge's — or its own earlier — committed
  grade of the prediction it is grading. That is a herding channel, and grades
  formed while it was open can agree for reasons other than the work: an
  agreement figure spanning the boundary is demoted for the same reason a
  `reasoning_quality` mean is, which covers the leaderboard's
  `evaluator_agreement` and `semantic-summary`'s leave-one-out agreement as well
  as the tau-b.

  **The judge validation is the headline.** Per stratum, the pre-registered
  Kendall tau-b between per-cell mechanical claim totals and
  `reasoning_quality` grades, over the **intersection** population only —
  cells carrying both numbers — with the intersection `n` printed beside the
  coefficient and the coefficient **suppressed (null) below n = 10**, the `n`
  still published. The `n` counts cells, the unit the pre-registration fixed
  the threshold on, with the distinct-event count (`pair_events`) published
  beside it because evaluator multiplicity repeats an identical mechanical
  total against several grades. It validates the semantic grader against the
  mechanical record, not the reverse: agreement says the judge tracks
  something the ground truth also sees, disagreement says it grades prose,
  and either result publishes. It says nothing about which predictor is
  better, and a high tau does not certify the judge's *level* (a uniformly
  shifted — generous but rank-preserving — judge is invisible to a rank
  correlation) — grader level is `evaluator_agreement`'s job on the
  leaderboard, the sole inter-evaluator agreement number **on the board**, and
  deliberately not duplicated here. Operational absences (a cell missing a
  block, or missing a grade) are counted beside the intersection because
  differential absence selects the pair set on difficulty; the counts cover
  committed cells only — a cell that failed outright commits nothing and
  stays invisible, upstream of them; and a block whose every claim is masked
  is the availability mask at work — a property of the record, never of the
  predictor — counted separately.

**Semantic grades publish nothing today, and this is the contract for when they
do.** No artifact here carries a semantic claim grade. The merits moments
declare `semantic-v1`, both prompts ask for it — a merits cell for the
propositions, a grader for the grades — and the evaluate cell is handed its
case's majority opinion wherever the corpus holds one. But **opinion coverage is
a rounding error** — 35 rows carry the `has_opinion` bit an ingested body sets,
against the 1,232 rows carrying a cert-grant date on the corpus blob pulled
2026-09-14, the figure
[outcome-decomposition.md](../docs/outcome-decomposition.md) states and
maintains under *What remains unbuilt* — and both declared claims require a
majority opinion, so on essentially every cell there is no staged body and the
grade is `not-addressed`: the availability mask, a property of the record.
Blocks accumulate; ordinal grades do not. `fedcourts
semantic-summary` is the surface that publishes them, and it writes
`semantic-grades-<stratum>-<scope>.json` only where **both** preconditions below
are met — the floor *and* a non-null agreement coefficient. Below either it
prints the withheld state and writes nothing, which is what it does today: for
this artifact the file's **absence is the withheld state**, and the command's
output is where the counts behind it are read. The rules are fixed before any
artifact exists so that a first publication has a contract to
meet rather than one written around it. The methodology behind them is
[outcome-decomposition.md](../docs/outcome-decomposition.md)'s *The semantic
family, alpha*, and it is **alpha** — `semantic-v1` is provisional, has never
met a real opinion, and is explicitly not a pre-registered commitment of the
kind the mechanical claim sets are. A grade produced under it would be a design
under test, not evidence about a predictor.

Not to be confused with the judge validation above, which calls
`reasoning_quality` "the semantic side" of its pair. That is a **different
number**: one judge-graded score of a prediction's reasoning as a whole,
standing in for a claim family whose own grades are all mask. A `semantic-v1`
grade is per declared claim and graded against opinion text. The pre-registered
pairing keeps `reasoning_quality`; whether it ever changes hands is a later
version's question, not this contract's.

**Descriptive only, and never a rank key** — under the alpha caveat above,
which travels with each rule below rather than being spent on the lead. A
semantic grade is an ordinal reading of a **declared proposition** — the
prediction's `semantic_claims` entry for that claim, never its
`predicted_reasoning.md`, which is graded by nothing — against the opinion:
`supported` / `partially-supported` / `unsupported`, plus a distinct
`not-addressed`. What may be published is the **census**: counts per level, per
declared claim, with the graded count beside them, and a pooled
`overall` census that is a coverage figure rather than a headline (different
claims are propositions of different difficulty, so a pooled share describes
the claim mix as much as the predictor — and it reaches its minimum on units
pooled across claims, so it publishes the distinct-cell and distinct-**case**
counts that actually bound it). The case count is the strictest of the three
and the one to read: one opinion backs a cell per predictor, every claim in the
set is read off that same opinion in a single pass, so units and cells both
multiply against a case count that does not. No standing, no ordering, and no entry
into the leaderboard or any headline. Nothing derived from a grade is a skill,
calibration, or forecasting claim of any kind.

**The mask publishes split by its ground, never as one total.** A
`not-addressed` count is counted apart from the ordinal levels, and the census
splits it again into three kinds of fact plus a bucket for silence:
`no-judgment` (no opinion body of the kind the claim requires was filed — the
case's posture, which bounds what could ever have been graded), `not-ingested`
(one exists and the record does not carry it — work this pipeline still owes),
`silent-on-axis` (the body is in hand and says nothing on the claim's axis — a
finding about what the Court wrote), and `unstated` for a grade naming none.
None of the three substitutes for another, so a figure quoting a mask total
without its grounds is not readable. The four buckets sum to the mask total
exactly. Read each as *units resolved to that ground*, not as panel agreement: a
panel naming different grounds is settled by a fixed precedence,
`not-ingested` > `no-judgment` > `silent-on-axis` — the two availability grounds
before the substantive one, so a `not-ingested`/`silent-on-axis` split reports a
coverage gap and a `no-judgment`/`silent-on-axis` split reports that no opinion
existed where one grader says it read one. The bias therefore runs one way and
should be read that way: the split can under-state what an opinion said and
never over-state it, and nothing in the artifact bounds how many units were
resolved rather than agreed.

**No mask total here has grounds behind it yet, because no mask exists here
yet.** `SemanticGrade.mask_ground` is elicited — the evaluate prompt asks a
grader to name the ground on every `not-addressed` row, on the closed vocabulary
above, and `validate` fails the cell on anything outside it — and the ledger
carries no `semantic_grades` block at all, so every bucket including `unstated`
is empty and a mask total is **not quotable**. Two readings arm the moment one
is. `unstated` records *nobody was asked*, never *nobody could tell*, and a
grade written under a superseded evaluator process that did not ask for the
ground lands there; since `semantic-summary`'s scope gate filters on the
*prediction's* stamp rather than the evaluation's digest, a census legitimately
pools graders from both sides of such a boundary, making `unstated` a mixture of
"asked and declined" and "never asked" that the artifact cannot separate. The
freeze-record entry for the evaluator-half re-bless that elicited the field is
what dates that boundary, and a mask total quoted across it is not a
like-for-like figure. And the
offline stub grader writes `not-ingested` unconditionally, so on any ledger a
stub cascade wrote into, that bucket is a harness constant rather than a grader
finding.

**A `majority-ground` census is an upper bound on forecasting skill, not a
measure of it.** Nothing pins a merits predict cell to the grant, and a forward
cell may retrieve without restriction, so a cell running after oral argument can
read a transcript in which the doctrinal ground is frequently telegraphed — the
claim's forecastability decays across the Term. Discharging this would mean
publishing each prediction's date relative to argument beside its grade, and no
artifact in this project records an argument date, so the caveat travels as
prose. `docs/outcome-decomposition.md`, *The declared set*, is where it is
argued.

**Never pooled with a mechanical claim score.** A semantic grade never enters
a claim `total`, `floor`, or `lift`, is never summed with one, and never
appears in the same aggregate. The mechanical rule scores against a
harness-computed prior drawn from strictly-prior history; a semantic
proposition has no such frequency, so there is no baseline, no score, and no
common unit — adding the two would be adding a Brier difference to a reading.
Whether a semantic baseline is ever derivable is an open empirical question,
not a pending feature.

**Agreement is published beside every grade, or the grade is not published.**
Unlike the harness-computed mechanical block, a semantic grade *is* the
grader's word — resolving it needs a reader — so inter-grader agreement is the
only check on grader latitude this surface has. It uses the same estimator and
the same leave-one-out shape as the board's `evaluator_agreement`, over a
different population and **never the same figure**: per grader, over the
`(cell, claim)` units it shares with a peer. Read as a property of the
**panel** rather than a verdict on one judge, and pooled across claims by
design — per-claim unit counts are too thin to correlate, so a per-claim share
travels with a panel-level figure. That pooling has a cost with a name: graders
who merely order the claim *types* alike can carry a coefficient near +1 with
within-claim agreement of zero. The **number of claims pooled** publishes
beside the coefficient so a reader can bound it — at one claim the contrast is
unavailable, and the higher it runs the more of the number it could be.

A count or share standing alone, with no agreement figure for the same cell
set, is one reader's opinion presented as a measurement — and **a null
coefficient is not an agreement figure**. It is null two reachable ways, and
both bar publication. *Withheld*, below the 10-unit minimum: the unit count,
the distinct-cell count, and the claims-pooled count publish anyway, and the
cell count is the one to read, since a five-claim set reaches 10 units on two
cells whose grades share one reading pass. *Undefined for want of variation*,
where one axis is constant across units and every pair ties on it.

That second case is the one to read carefully, because it looks like unanimity
and is not. Tau-b is undefined on a **constant** axis, not on an agreeing
panel: graders who agree on grades that differ from unit to unit read +1. A
constant axis means either a record uniform enough that every unit graded
alike, or a **uniformly generous grader** whose own axis never moves — and the
number cannot tell those apart. The second is the exact pathology the figure
exists to catch, so an undefined coefficient is treated as no coefficient. The
record separates withheld from undefined, so a thin sample and a degenerate one
are distinguishable; neither publishes.

**The mask is the record's, and sits outside every denominator.**
`not-addressed` means the record does not put the claim in question, on one of
the three grounds named above, which the census splits it by. It gets the same *treatment* as a masked mechanical
claim — counted apart, never averaged with the ordinal levels, never inside a
share's denominator, never inside the agreement coefficient — though not the
same provenance: the mechanical mask is harness-computed with no latitude and
this one is a reader's call. That is why a unit graders *split* on gets a row
of its own: the disagreement measures the record's adequacy rather than the
panel's. It also selects what the coefficient is computed over, and in the
worst direction — the excluded units are the ones graders disagreed on most
sharply — so the published coefficient is agreement **conditional on the panel
unanimously agreeing the record spoke**, and it is read against the
mask-dispute count rather than merely beside it.

**Suppression, population, and comparability.** Any derived figure — a
supported share, an agreement coefficient — is withheld below its minimum count,
with the count still published, so a withheld number is visibly withheld and
never reads as a missing one. Grades are never pooled across strata, across
process versions, or across semantic claim-set declarations: a set version
fixes what the propositions *are*, so a census spanning two of them is a
coverage figure and nothing more. A graded unit carries none of those three
labels, so **a census must state its stratum and its process scope or it is not
readable at all** — an unstated census could have pooled forward and replay
cells and look identical to one that did not. And a replay cell's grades are
never claimable: its opinion is public, so the claim is retrievable rather than
forecastable, and with no baseline to subtract the *whole* of the grade is
retrievable rather than an increment over one. The backtest-as-iteration
doctrine below applies to them in full.

**Forward vs retrospective.** Snapshotting controls what a predictor can *read*,
but not what its model already *knows*: a prediction over an event that resolved
before the model's training cutoff has the outcome inside the model's weights —
the caption alone can retrieve it — so scoring it measures recall plus
calibration, not ex-ante forecasting skill. The clean structural separator is the
pre-registration standard: a cell is **forward** when the event was still
unresolved at the prediction's **harness clock** and **retrospective** when it
had already resolved (same-day ties count as retrospective, the conservative
reading). The split is deterministic and offline — the harness clock (the
harness-written process stamp; an unstamped **shakedown** cell falls back to
its agent-written `created_at`, which is safe exactly because an unstamped
cell can never be frozen — the fallback only ever positions cells inside
diagnostic views, so no pre-registration boundary rests on a clock the agent
controls — `fedcourtsai.integrity.cell_clock`) against the
outcome's `resolved_at`, both committed artifacts (`classify_stratum` in
`fedcourtsai.integrity` is the single definition). Retrospective cells remain
valuable — they measure calibration and label-mapping fit — but only the forward
stratum is evidence of forecasting skill, so no headline metric may mix them.
The label is a *floor*, not a claim that the stratum is homogeneous: a forward
cell **placed at a declared moment** differs from its neighbours both in how
its snapshot was built and in how old that placement was when it ran, and both
are owed beside a figure that pools them — the provenance counts
(`as-stored`/`dated`/`truncated`) and the placement-lag distribution
(`integrity.context_lag_days`), stated under `salience-replay.json` below.

**The forward-claim exclusion.** A cell whose harness-written record *claims*
`forward` (`context.mode`) while its event had resolved **strictly before**
the cell's harness clock day is **not a forecast** — its claim and its record
contradict each other, so it is not a valid observation of any scored stratum
(`fedcourtsai.integrity.forward_claim_breach`, a property of the record alone,
never of predictor behavior). A same-day resolution is deliberately not a
breach: the record cannot distinguish an honest forward cell that lost a
same-day race from a mis-provisioned one, so the tie falls to the rule above
— same-day counts as retrospective — and exclusion is reserved for the
unambiguous contradiction. Under the registered policy
(`integrity.FORWARD_CLAIM_POLICY = "exclude"`) a breaching cell is excluded
from every scored stratum; the boards publish the policy and the count in
their `forward_claim` block, and the board builders name each dropped cell on
stderr, so the exclusion is never silent. The provisioning-side record gate
reads the corpus's view at provisioning time, so a resolution the corpus has
not yet ingested can still slip through it; this scoring-side rule is the
defense in depth that makes the claim mechanical rather than trusted.

**The leakage exclusion.** A cell whose grading carries `leakage_suspected`
— the evaluators' coarse bit, true where the structured `leakage` block reads
`influenced_prediction` as possible or likely — is **excluded from every rank
key and every scored aggregate**
(`fedcourtsai.integrity.leakage_excluded`, applied at the same join as the rule
above). The bit says the graded prediction may have read its own outcome, which
makes the cell an observation of no scored stratum: not forward, where it would
be published as forecasting skill, and not retrospective, which is the
iteration signal a contaminated cell degrades. The exclusion therefore reaches
the **retrospective pair** that breaks ties on the ranked board as well as the
forward pair, since that is where a near-perfect leaked number would otherwise
order a predictor with no forward cells.

The rule is **independent of timing and of the forward-claim rule**, and that is
what it is for. The stratum boundary compares the outcome's `resolved_at` to the
prediction's harness clock, and a clock cannot see a leak: a leaked cell whose
outcome resolves *after* its prediction's clock classifies `forward` on the
timing rule alone. Only the bit keeps it out. A cell both rules catch is counted
in **both** ledgers — they answer different questions over one population — so
the two counts sit side by side and are never summed into an exclusion total.

**The unit is the grading, not the prediction.** The bit lives on one judge's
`evaluation.json`, so it drops that judge's cell and no other: on a split panel
the same prediction stays in the scored set through the judges that did not
flag it, at reduced panel depth, and `by_predictor` counts gradings rather than
predictions. Read a nonzero `excluded` as "this many judge-readings left",
divide it by the panel depth to recover predictions, and treat a *partial* flag
on one prediction as the signal it is — the panel disagreed about whether the
cell read its own outcome, which is a question about the record no aggregate
here answers.

**It changes membership, never value.** No score on any record is altered,
recomputed, or reweighted by the bit; the cell simply is not counted. And a
**null** bit is "not assessed", not "clean" — offline evaluators and records
written before the field existed carry null, and those cells are scored. That is
why the published block carries a denominator: the boards' `leakage_exclusion`
records `excluded`, `assessed` (in-scope cells whose grading recorded the bit at
all), and the per-predictor split, so `excluded: 0` over a ledger of nulls reads
as "nothing was checked" rather than "nothing leaked". The split is published
because exclusion falling differentially on one engine changes the scored
population, which is the cross-engine comparability condition. The board
builders name each dropped cell on stderr and the refresh PR body carries the
count, so the exclusion is never silent.

Both figures in that block are **stage-blind and taken before the exclusion**,
exactly like `forward_claim`'s pair and `superseded_gradings`: they span the
ranked cert board and every `stages` block at once, and they count cells the
board's own totals never saw. So neither may be netted against a count on the
board — `excluded` is not `evaluations_total`'s missing term and `assessed` is
not its denominator. Read them as an audit line about the pass, never as terms
in the board's arithmetic. For the same reason `leakage_exclusion` is never the
ops report's `leakage` digest, which is uncollapsed, all-versions, and
window-scoped: the two answer different questions over different populations and
are never differenced.

The scope is the **stratified scored stream** — the ranked board and its stage
blocks, `claim-scores.json`, the ops report's substance funnel, and the semantic
census, all of which read one `store.stratify` pass. Three surfaces read the
ledger by their own path and so do not apply it, deliberately and for the same
reason they do not apply the forward-claim exclusion: the board's `big_case` and
`evaluator_agreement` views measure stakes reads and grader latitude rather than
scored performance, `big-cases.json` publishes those same stakes reads per case
(and marks a leakage-flagged read rather than dropping it, since here the
contaminated cell *is* the published number), and the tool-usefulness figures
are a declared superset
(below). A figure there that differs from a board figure is two populations
rather than an error in either.

**A row-blind `codex-baseline` grading is "not assessed", never "clean".** A
`codex-baseline` `retrieval_log.json` whose rows all carry a null `call_source`
(the null's meaning is stated on `RetrievalCall.call_source` itself) records
none of the calls its program made as rows of their own: no manifest search,
document read or fetch inside the program has a tool class, a result marker or
a `retrieved_doc_date` of its own. What such a log gives the grader is each
wrapper row's head slice of program text, whatever date the combined output
surfaced onto that row, and the prose. Those are exactly the `codex-baseline`
logs from runs before `20260820T181919Z`; a zero-row log is unassessed for the
same reason rather than by vacuity. The marker is sufficient for row-blindness,
not necessary: a later log whose code-mode parent rows stand beside no lifted
row (`fedcourtsai.collect.code_mode_lift_blind`) is a separate open case, and
on the runs from `20260820T181919Z` through `20260825T231742Z`, before the
builtin idiom was lifted, a program's shell calls still have no rows while its
manifest calls do — half-blind on the channel most able to reach an outcome, so
the rule below reads those gradings the same way. An unsuspected verdict on a
row-blind or half-blind grading — `none`, or `not_applicable` — is read as a
null bit: assessed nothing, scored, never evidence that the cell did not read
its outcome. A `possible` or `likely` verdict on the same vintage
stands, since a positive finding from the visible evidence is still evidence;
and the distinction is not idle, because every row-blind grading on the ledger
declares `mode: forward` and six of them read `likely` with outcome material
retrieved, so the declared mode is not what settles a verdict. Two consequences
bind any reading. The suspected share of a row-blind vintage is a **lower bound
on leakage, not a rate**: its negatives are null bits, so there is no assessed
denominator to divide by. And a cross-engine leakage comparison over cells
before `20260820T181919Z` is not a comparison: the other engines' logs of that
vintage carry their manifest calls as rows, so their unsuspected verdicts are
real reads where codex's are null bits. `assessed` still counts such a
grading — it counts gradings that recorded the bit, not gradings that could
see — but only the all-versions build ever reaches one: no row-blind or
half-blind prediction carries a frozen digest, so the frozen boards exclude
them a gate earlier. The [freeze record](../docs/freeze-record.md) fixes their
number, in the ledger and after the run collapse, and dates the rule.

**The procedural stratum.** A cell whose outcome was mootness practice — a
Munsingwear vacatur ("granted", but the wording tracks the Court's vacatur
practice) or a dismissal as moot — segments into a third, `procedural` stratum
regardless of timing (the outcome's `disposition_basis` marks it at
resolution). Its aggregates are reported per predictor but never enter the
ranking: scoring them as merits calls would conflate cert-worthiness
calibration with vacatur-practice prediction.

**The stage axis.** Orthogonal to the strata runs the event's decision
**stage** (cert / interim / merits — the `event.yaml` vocabulary), and within a
stage its forecast **moment**: `granted` answers a different question at each
stage, and a later moment answers the same one with strictly more evidence, so
the ranked board — its entries and evaluation counts — is the **cert stage's
first declared moment**, and every other population, a later cert moment
included, reports its own unranked per-predictor block under `stages`, keyed
`<stage>@<moment>` (bare stage where none is recorded) and **never blended** —
no skill or count figure pools into the cert board, into another block, or into
any headline number. (The `big_case`
and `evaluator_agreement` blocks are the deliberate exception: they describe
stakes reads and grader latitude, not stage-scoped skill, and stay
stage-blind.) A petition/appeal-kind event with no
recorded stage reads as cert (the case-baseline kinds resolve on the cert
standard by construction); a stage-less cell of any other kind shares one
`(none)` bucket so coverage stays visible — that bucket's *counts* are the
claimable part, while its means pool cells of unknown, possibly heterogeneous
decision standards and support no cross-cell claim. Skill scores appear only
where a scored base rate exists for the stage. All three now have one. The
**interim stage's** is the statpack interim section's substantive grant rate,
pooled over application Terms strictly before the case's own
(`pipeline.base_rates.interim_base_rate`), subject to its own per-pool floor and
carrying the selection caveats registered in
[`docs/salience.md`](../docs/salience.md) — notably that the pool is the whole
substantive slice while the scored cells are reserve-selected on the escalation
ladder, so an interim skill number is not by itself evidence of forecast skill.
The **merits stage has a registered baseline** — the statpack merits section's
`disturbed_rate`, pooled over grant Terms strictly before the case's
(`pipeline.base_rates.merits_base_rate`; `docs/decision-model.md` is the
registered design) — so a merits cell's Brier is `(P(disturbed) −
disturbed)²` and its skill is scored **only against that declared
baseline**, which holds by construction rather than by a check:
`stamp-cell` writes a merits cell's
`segment_base_rate` from that same pooler (and an interim cell's from its
own), and writes the Brier beside it from the scored prediction's committed
probability and the committed outcome, so no cell this harness stamps on a
stage-resolving event can be ranked on a rate or a Brier the harness did not
compute — the record itself does not distinguish a stamped number from a
written one, so that is a property of how a cell is produced, not something the
board can re-derive. Skill is
scored only
where the pooled prior-Term sample clears the baseline's
stated minimum (`MERITS_BASE_RATE_MIN_PARSED`, 30 parsed judgments); below it
there is no baseline,
no skill score, and no substitute rate. Three things travel with any merits
figure. The baseline's population is the section's population is the scored
population — up to predict scope: the section admits every grant that opens
a merits proceeding while the forecast side further excludes IFP,
consolidated-out-of-scope, and date-inconsistent rows, a small residue now
that the guard removes the (mostly IFP) stale-labeled vacaturs. The two
procedural
exits count as undisturbed (a DIG and an equally divided affirmance leave
the judgment below standing) exactly as the outcome writer scores them, and
GVRs and summary reversals are absent because they are cert-stage
dispositions that mint no merits cell. That exclusion does not rest on the
row's disposition label alone: the `gvr` label is a forward convention, a
row's label can lag its own cert order (measured, the stale labels sit on
recent IFP GVRs), and no
resolver produces `summary-reversal` at all — both classes parse as
near-certain
vacaturs — so the section also applies the label-independent guard
`docs/decision-model.md` registers
(`pipeline.judgment.judgment_rode_the_grant_order`): a parsed judgment dated
on or before its own grant rode the cert order and is excluded from the
cohort entirely, whatever its label says, with the removed rows published as
the section's `cert_order_excluded`. Read those counts as two populations, not
three nested ones: a removed row is counted there *instead of* in `granted`, so
`cert_order_excluded` is disjoint from `granted` — per Term, their sum is that
Term's pre-guard population of merits-opening grants — while only `parsed` nests
inside `granted` and never exceeds it. A Term whose `parsed` + `cert_order_excluded` runs past
its `granted` is adding across the two populations, and says nothing is wrong.
When that count is a number, the pooled
**rate** is clean of every cert-order vacatur whose judgment parsed with a
date; when it is `null`, the pack predates the guard, and the section's
figures carry whatever contamination the guard would have removed — quote
nothing from a null-guard merits section. The merits baseline enforces this
structurally at the granularity that matters: `merits_base_rate` returns no
baseline when any Term **inside its pooled window** carries a null
count (a null on a Term the leakage rule or the lookback window already
excludes contributes nothing and so cannot contaminate the rate). Four residues
survive, and they travel with any quoted figure: a summary reversal issued in
a later order than its grant is caught by neither guard; an *unparsed*
cert-order vacatur stays in `granted`, so the `parsed`/`granted` coverage
figure can still carry it even though the rate cannot; a parsed judgment
with no date stays in `granted` the same way, since the gap test cannot run
on it; and a granted case recorded as `merits_terminated` stays in `granted`
too. That last residue covers two unlike kinds, and the distinction matters
for what may be said about it: a proceeding that ended before the merits were
reached — a post-grant Rule 46 dismissal, a dismissal as moot, an abatement on
the petitioner's death, a grant the Court vacated — has **no
disposition to record**, while a bare mandate
notation marks a case that *was* decided on a docket whose disposition entry
the corpus never captured, which is a coverage failure of the same family as
the two residues above. Neither is folded into the judgment vocabulary,
because a seventh value would be scored as an undisturbed judgment, asserting
in the first case that the decision below survived a merits ruling nobody
made, and in the second that it survived a ruling whose direction is simply
unread. One of the four pre-merits shapes carries a further debt, and it is
not the merits column's to pay: a **vacated grant** returns the case to the
cert stage, so the row's cert `disposition` goes on describing an order the
Court withdrew — 19-825 is stamped `granted` and was ultimately denied. The
termination resolves the row's merits pendency correctly and keeps it out of
every merits figure, but it also releases the row from
`no_stale_unparsed_grants`, which was the only check naming it. Such a row
remains owed a cert-label reconciliation that no sweep performs, and it counts
as a grant in the cert-side rates until one does. And the window is the same ten-Term
band the cert baseline uses (`salience.base_rate_lookback_terms`), so state it
with the figure. `correct` — and so the stage block's accuracy — is the **judgment**
exact-match on a merits cell, not the disposition match, since a merits
outcome's `actual_disposition` is always the off-vocabulary `other`. The
interim stage's base rate is registered and pooled from the pack's interim
section — the substantive slice's grant rate over application-Terms strictly
before the case's own, subject to its own pooled floor
([`docs/salience.md`](../docs/salience.md)) — so its block reports skill on the
same terms as the merits one: a figure where a cell's baseline exists, and null
with `skill_scored` zero where the pooled sample is below the floor or the
cell's own evaluation recorded no skill. Every
non-cert block — both stages and the `(none)` bucket — reports the realized-Term
skill null with a zero count, by construction rather than by coincidence:
only the cert segment has a salience band whose realized rate the pack
publishes.

A merits **skill** number exists only where the pack can support it: the
merits section publishes only once a corpus row carries a parsed judgment
(the guarded cohort above), the pooled prior-Term sample must clear the
stated minimum, and every Term inside the pooled window must carry a
non-null guard count (the null-provenance refusal under `statpack.json`
above) — behind any of these there is no baseline, the declared claim goes
unscored, and the merits stage block's skill figure is null with
`skill_scored` zero. The interim block is null the same way and for the same
class of reason, its own floor standing in for these. A merits cell
records `segment_base_rate` read from the
merits section rather than the cert band, with `base_rate_basis` and
`base_rate_salience_version` null because that rate is no band product.

- `cert-backtest.json` — the cert-specific back-test (not regenerated by the
  weekly metrics refresh): predictors
  replayed over decided modern discretionary-cert petitions,
  outcome hidden behind a redacted snapshot, scored on accuracy, Brier, **lift
  over the always-deny floor** (the honest signal under cert's denial skew), and
  a P(granted) calibration view. The report names the scorer whose bands
  segment it (`salience_version`): a band label means something only under the
  function that assigned it, so a per-band figure is not comparable with one
  produced under another version. Each entry also carries a **per-salience-band
  skill breakdown** over the paid scored segment — the mean leakage-safe segment
  base rate (each petition's own prior-Term band grant rate) and the mean Brier
  skill against it — so the back-test measures the same segment-baseline skill the
  forward stratum does, not just raw Brier. Comparable across the two strata while
  `salience.base_rate_lookback_terms` (the in-code window, shipped at 10 to match
the rendered table) and
  `statpack.markdown_terms` (what the prompts' Term table renders, 10) agree; see
  [salience.md](../docs/salience.md). A replayed predictor's pre-registered
  **big-case-score distribution** (coverage + mean/min/max stakes) rides alongside
  — a distribution, not a grade, since the replay has no independent evaluator to
  rank against. **Read the report's `provenance` block before any of it.**
  Predictor ids are identical under every backend — an `engine: stub` rehearsal
  writes entries named `claude-baseline` — so the block records the replay's run
  id and the dispatch behind it (`engine`, `skip_engines`, `scope`, `spread`,
  `limit`), and each entry records the backend that actually ran it plus the
  model that backend was invoked with. A null `model` means no model ran **in
  that run**: the offline reference baselines, and the offline `stub`/`replay`
  backends — `stub` being canned numbers, while `replay` re-emits one captured
  forecast across every petition, a constant predictor here. The dispatch is
  part of the reading, not bookkeeping: `scope`, `spread`, and `limit` choose
  the population, and the always-deny floor a lift is measured against — the
  set's, or, for an entry short some cells, that entry's own scored subset —
  moves with them, so two differently dispatched reports are two samples whose
  top lines are not comparable. Two config values ride the block for the same
  reason, because they move the population and the baselines under an *identical*
  dispatch: `salience_floor` (what `--scope selected` means) and
  `base_rate_lookback_terms` (what every `segment_base_rate`, and so every
  `mean_brier_skill`, is scored against — it sits in no process digest, so
  without it here a per-band comparison across two reports is not one).
  `dropped_predictors` names the predictors lost at run time (no registered
  runner, a missing CLI binary, or every one of its cells unreadable — the ids
  carry no cause, which the run log states) as against the deliberate
  `skip_engines` opt-out, since a board silently short one engine is not the
  three-engine comparison it looks like. `lost_cells` is the per-cell
  counterpart: a (petition, predictor) cell that ran and produced no readable
  prediction, with its reason (`missing`, `invalid`, or
  `wrote-outside-work-root`). It is a reading rule, not bookkeeping — a
  predictor short *some* cells is scored, and its lift floored, over the
  petitions that came back, so its `events_scored` is below the set and its top
  line is not measured over the same sample as an entry that lost none; one
  short every cell has no entry at all and is in `dropped_predictors` instead.
  The board keeps a short entry below every full one whatever its lift —
  dropping a petition a predictor would have got wrong raises the figure — so
  `rank` orders comparably only within one `events_scored`, and the rows below
  the full ones are a listing rather than a ranking. A **null** `provenance` means unknown, never offline: read
  nothing from such a report. `provisioning` counts the replayed **petitions**
  by the snapshot provenance each was given — `dated` (a snapshot the docket
  really served before the cutoff), `truncated` (a later payload with its
  post-cutoff entries removed), `blind` (no trajectory shown at all, from
  either cause: no forward moment fixed a cutoff, or truncation left a
  disposition visible and the fail-closed leakage guard withdrew the
  trajectory) — and those are three information sets, so a score over their
  union is a score over a mixture: a blind petition cannot observe its own
  relist history, which is most of what a cert forecast turns on. The
  always-deny floor is not one of the figures the information set moves — it is
  the replayed set's own denial share, a property of the labels. What moves it
  is **composition**: a docket with no distribution to show is the strongest
  denial signal here, so the blind arm is selected on a feature that correlates
  with the outcome and comes out denial-purer than the rest. A blind-heavy draw
  therefore carries a *higher* pooled floor and dilutes every lift measured
  over the union, rather than depressing them. Read the mix before the scores,
  and read a shift in it between two fortnights the way you read a change of
  dispatch. The weekly digest's cert back-test line carries the mix and the
  dispatch beside the figure for that reason. Two things the mix does not
  capture. The first is that the day bar narrows the **dated** cells'
  retrieval and not the blind ones', so the two arms differ in what they could
  *retrieve* as well as in what their snapshots showed — one more reason to
  read the mix before the scores. The second is the offline `prior-vote` row:
  it is masked on each dated cell's own cutoff day, the clock its engine cells
  retrieved under, and only an **engine replay** provisions those cutoffs. So a
  run with no replay at all (`--engine` unset) carries a prior-vote row masked
  on the Terms alone, while any replay — a stub rehearsal included, since it
  provisions the same cells — carries one masked on the days. That changes
  `prior-vote`'s own accuracy, Brier and **lift**, because a narrower retrieved
  set is a different vote; no other entry's figures move on account of the
  mask, and the always-deny floor is not a clocked quantity at all — it is the
  replayed set's denial share, a property of the labels. Do not compare
  `prior-vote`'s top line between a replay run and a no-replay one regardless:
  `--engine` also narrows the population to the replayable petitions, so the
  two are scored over different sets and their floors are different floors. Produced by the
  `run-backtest` workflow and labeled retrospective like `backtest.json`. A
  real-engine replay spends tokens, so **the schedule asks and the hold
  spends**: no run spends without an explicit maintainer decision. The
  fortnightly cron (even ISO weeks, Saturday 06:23 UTC) derives its plan under
  pinned parameters — `replay: cert`, `engine: auto`, `--limit 10`,
  `--scope paid`, `--spread` — and then waits on the `review` environment's
  required reviewers, with no timer that could release it unattended; an
  unreleased fortnight is a skipped sample that cost nothing, and the report's
  own `provenance.run_id` is what identifies the sample still standing. The
  other way in is a `workflow_dispatch`, which
  GitHub gates on repository write and which keeps its free parameters
  (`replay`, `engine`, `limit`, `terms`, `skip_engines`, `scope`, and `spread`
  inputs —
  ~one predict cell per petition per routable predictor; `engine: stub` is a
  free dry run; `replay: salience-gate` instead runs the token-free
  salience-gate replay). The cron pins `paid` rather than the wider `all`
  because ten petitions have to carry signal: the paid class resolves
  grant-or-GVR at roughly 2.3× the whole population's rate, and the per-band
  breakdown scores paid rows only — so an unfiltered draw would leave the lift
  reading against a floor that denial purity pins near 1.00 and the bands
  genuinely empty. Even so, a fortnight with **nothing granted** is an ordinary
  outcome at this size — roughly half of them — and there every denial-heavy
  predictor ties the floor and the ranking is not a measurement: the review PR
  withholds the top line and states the granted-side count instead, which it
  recovers from the calibration view rather than from the floor (a dismissal is
  neither denied nor granted, so `1 - floor` is a different quantity). Size
  governs the rest of the reading too: at this limit an ordering turns on one or
  two granted outcomes and a band on fewer, so read the series and each
  segment's own `events_scored`, never one fortnight's rank. Three things to hold when
  reading consecutive fortnights: they are samples of one dispatch, one salience
  floor and one lookback, which is what makes them comparable **in population**;
  the report carries no process digest, so a prompt or predictor-config change
  between them is legible only from the promotion history; and a dispatched
  campaign's report is not comparable to either. The
  `provenance` block is where all of that is checked, not assumed. The
  refreshed report lands as
  a **reviewed, never auto-merged** PR. Only petitions holding a snapshot
  replay; the report names what it skips. `fedcourts cert-backtest` remains
  runnable locally with the engine CLIs authenticated.
- `salience-replay.json` — the **salience gate** replayed over past Terms
  (`fedcourts salience-replay`; deterministic, offline, spends nothing). One
  cell per (October Term, cutoff policy, **salience version**): each of the
  Term's resolved,
  **live-slice**, paid modern-cert petitions — live-slice because only a
  docket with parsed proceedings offers a state to reconstruct, so a cell's
  `eligible` count is walk coverage, not the Term's whole paid cert docket —
  is projected to the state its docket disclosed at the policy's moment
  (petition arrival, first distribution, or the last pre-resolution
  distribution), and **every registered** frozen scoring, banding, and
  per-conference selection runs over that reconstruction — the projection is
  built once per (Term, policy, distribution parse) and shared by the versions
  pinning that parse, so versions differ in what they saw only where their
  declared parse differs, and each cell records the parse it was projected
  under. Each cell names the version that produced it, and reports
  the would-have-been selection (carve-out vs rank-fill, and where capacity
  actually bit), the band mix including `unobservable`, the
  snapshot-provenance mix, and sample-weighted **precision/recall of the
  selection against the realized grant-family outcomes**, with raw counts
  beside the weighted selection and grant figures.

  **What may be claimed.** The numbers describe the *gate* — how the
  deterministic selection rule would have behaved at a reconstructed moment —
  and its structural facts: at arrival every *observable* projection reads
  relist-0 with no conference cohort, so the rank-and-cap selects nothing and
  escalation precision is undefined (the trajectory features cannot
  distinguish petitions before the docket moves). Under a scorer that selects
  arrivals (every caption-banded version declares it), the `arrival` policy's
  cells report the draw slice and the carve-in picks instead — a separate
  cohort, never pooled into the escalation ones, and still no validation of
  any caption feature (the reconstruction carries the terminal caption; a
  declared gap).

  **Comparing two salience versions.** Cells sharing a (Term, policy) *and a
  distribution parse* are paired on one identical projection, so any
  difference between them is the scoring function; where the parses differ,
  the projections differ with them (each cell records its parse), and the
  comparison spans the scoring function together with the docket reading it
  was fitted on — but either way *not* at a matched operating point. Every version is run
  against the same `salience.floor` and the same per-conference capacity, and
  carve-outs sit above `N`, so a scorer whose score scale puts a different
  fraction above the floor selects a **differently sized set**. Raw precision
  is therefore not comparable cell to cell: two versions can differ in
  precision purely by selecting more or fewer petitions. Read the comparison
  **at matched recall**, which is the bar `docs/salience.md` pre-registers for
  a candidate scorer, using the `recall`, `selected_carve_out` and
  `selected_rank_fill` each cell publishes. A bare precision delta between
  versions is not a claim this artifact supports.

  **What may not.** Nothing here is predictor skill — no model
  ran — and nothing is ex-ante: every replayed petition had resolved before
  the replay, so the backtest-as-iteration doctrine below applies in full. A
  Term replayed before it has fully resolved censors its pending — and
  disproportionately high-salience — petitions, so read only completed Terms.
  Weighted figures use each row's `sample_weight` (inverse inclusion
  probability), and what they estimate depends on the statistic: row-wise
  quantities (the carve-out slice, the grant totals) reweight into population
  estimates, but the **rank fill is a functional of the walked sample's
  cohort** — under legacy denial weights a replayed cohort holds a thinned
  fraction of the real one, so the top-N of that subsample is not the
  population's top-N, and `capacity_bound_cohorts` can read inert where the
  real cohort would have been cut. Each cell's `largest_weighted_cohort`
  against the capacity is the check: rank-fill figures are trustworthy where
  it too sits below capacity (or on Terms walked at weight 1 throughout).
  The raw counts beside the weighted figures count walked rows; the two must
  not be mixed. Read the provenance mix before the rates: a `truncated`
  projection cannot detect an entry back-filled later but dated earlier (an
  accepted residual a `dated` snapshot does not carry), and the blind causes
  read differently under recall — `blind-no-moment` is a faithful gate miss
  (the live gate would never have cohorted it either), `blind-untrusted-cutoff`
  a reconstruction failure on a really-distributed petition, and both sit in
  recall's denominator while being unselectable. Cross-policy comparison
  within a Term is the intended reading (mind the shifting blind share);
  cross-report comparison against the cert back-test's band mix is not — the
  two select different populations at different moments.

  **The same standard binds the forward stratum.** A forward cell placed at its
  declared moment carries the same `dated`/`truncated` split, so no forward
  figure over placed cells may be published without those counts stated inline.
  The split is not cosmetic on either axis. It is **selected**: `dated` needs a
  pull that landed on the trigger day, which the live poller does for
  watchlisted and salient dockets and not for the rest, so the residual
  concentrates in the `truncated` arm rather than spreading evenly. And the two
  arms err in opposite directions — `dated` brackets the moment from below (it
  is the docket as pulled, so it can miss entries filed later the same day),
  `truncated` from above (it reconstructs to the cutoff but carries the undated
  counsel/amici blocks as at a much later pull). Pooling them averages a
  selected mixture of two different biases.

  **A third number is owed with them: the placement lag.** Provenance says how
  the snapshot was built; it does not say how old the moment was when the cell
  ran. `integrity.context_lag_days` is that number, derived off any **forward**
  cell whose harness wrote a context — the days from where the cell was placed
  (`context.cutoff`, else its `snapshot_date`) to its harness clock day — so a
  forward figure owes its distribution as it owes the provenance counts. No
  artifact and no `fedcourts` command publishes it: call
  `fedcourtsai.integrity.context_lag_days` over the committed ledger when a
  figure is read, because the obligation is on whoever publishes the figure and
  not on a renderer. The distribution travels with its own `n` and with the
  count of cells that yielded no number — a null-context cell did read a
  snapshot and the record does not say which, and a replay cell is carved out
  by design, so both are *not derivable*, never zero.

  One cell the lag does not describe: a `context.snapshot_uptake` of `unread`
  says the cell did not report reading the payload it was placed on, so its lag
  measures the age of a moment that cell may never have looked at. It is a
  handful of cells and the honest treatment is to name them beside the `n`
  rather than to drop them, since dropping cells on a predictor-reported fact
  would make the population move with predictor behaviour.

  Read it **segmented on `snapshot_provenance` and on the moment** — provenance
  alone is not enough, and the two cuts answer different questions. Provenance,
  because on the `as-stored` arm no cutoff exists and the number falls back to
  the payload's own date, where it measures pull age rather than placement. The
  moment, because lag has two mechanisms and only one of them is a scheduling
  fact. **Cohort-completion lag** is the run's cell cohort (the fan-out across
  engines for one case-event, not a conference cohort of petitions) finishing
  after the day it was placed at. **Moment pendency** is structural: a moment
  placed at an order whose disposition pends for months — the CVSG being the long one — puts every
  cell of it far behind its own cutoff no matter how promptly the cohort ran.
  Pooled, the second swamps the first and a reader reaches for a scheduling
  remedy that would not have moved the number. The moment cut also carries a
  confound to state rather than pool through. The band is a function of the
  petition, not of the moment, but the long-pendency moment is the CVSG — and a
  CVSG petition scores into the top bands by that fact alone. So wherever the
  long-lag cells are the CVSG ones, they are also the high-band ones, and since
  the band is the key each cell's base-rate anchor is chosen on
  (`prefix_est_grant_rate`), *"high-lag cells score differently"* and
  *"high-band cells score differently"* are the same sentence. Neither is
  separable from the other on a ledger where they coincide; check whether they
  do before conditioning on either, and say which you found.

  It is **not** a staleness measure and must not be read as one:
  `--max-snapshot-age-days` bounds the *payload*'s age on the latest pull,
  before any cut, while a `truncated` cell's own `snapshot_date` **is** its
  cutoff, so a cell built from a same-day pull can carry weeks of lag with no
  stale byte in it. Nor is it a defect to be driven to zero. The
  cohort-completion half is the price of cohort comparability — all engines of
  a cell cohort must read one information set, so a cohort completed late is
  completed at the cutoff it opened with, not re-frozen — and the pendency half
  is the moment being what it is.

  **On the interim arrival moment, segment on `cut_kind` as well**, because
  there the cutoff is not the boundary. A day cannot express that moment — an
  application can be submitted, referred and disposed of inside one — so its
  snapshot stops at the entry that opened the event (`cut_kind`
  `arrival-position`, `cut_anchor_index` beside it) rather than at the end of the
  cutoff's day. Two obligations follow. An interim arrival cell never carries
  `cut_kind` `date` — that moment either takes the anchor bound or refuses — so
  the split the freeze record registers is `cut_kind` **absent** (a cell
  provisioned before the field existed, its `cutoff` non-null) against
  `arrival-position`, and a figure pooling the two arms is pooling two
  information sets on the shape where they differ most, the same-day-disposed
  application. The null arm is readable as the old rule only restricted to
  interim arrival events; elsewhere a null `cut_kind` merely means no moment
  fixed a cutoff or the cell predates the field. And the bound carries a
  **membership rule**: a row whose opening entry cannot be located in its
  snapshot is refused rather than provisioned on the date rule, so those cells
  never exist and no board's exclusion block can show them. `fedcourts
  arrival-cut-ledger` is the surface that counts them, split by resolution status
  and same-day disposition — the split is owed with any interim arrival figure,
  because unanchorable, terse and summarily-disposed-of are a plausible single
  shape, and a membership rule dropping rows correlated with the outcome has to
  be measured rather than assumed harmless. Read its cause split before drawing
  anything from the headline: `refused_stale_stamp` is any disagreement between
  `events.opened_at` and the submission entry the payload carries — in practice
  the stamp having drifted back to docketing between arrival-backfill sweeps, so
  a corpus freshness reading — while only `refused_no_submission_entry` is a
  property of the docket.
  And read the rate over `scope_pending_rows`, the in-scope undisposed-of slice
  the forward lane actually mints cells for; `pending_rows` pools in the
  out-of-scope kinds the matrix drops (`scope_rows` and `kind_counts` carry
  that split), and the whole-population rate additionally pools in decided
  rows no forward cell is ever provisioned for.

  The price is paid in the claim rather than in the input, and on one part of
  the claim only. The **disposition** is unaffected: a forward-stratum cell's
  event was by construction unresolved through the day before its harness clock
  (`classify_stratum` puts a same-day resolution in the retrospective stratum,
  and `forward_claim_breach` catches a record that says otherwise), so even a
  long-lagged cell is still ex ante on the outcome. What a lagged cell can
  observe is the *intervening docket* — it retrieves without restriction, so at
  weeks of lag an **increment** claim (a relist landing, a CVSG arriving, the
  amicus wave) can be read off a docket that moved since the cutoff, where a
  same-day cell's is a forecast.

  So the obligation binds the placed moments' increment totals, per stratum —
  which on the published surfaces means the unranked `stages` blocks and the
  non-baseline cert moments, never `claim-scores.json`, whose single moment is
  unplaced by construction. Those cells wear one stratum label and one
  provenance label while holding different information sets, and pooling them
  without the lag beside them pools observation with forecast.
- `statpack.json` / `statpack.md` — a corpus base-rate **statpack** (an independent
  published artifact): two cert-era populations side by side, plus the
  interim-docket and merits stage sections described below. The labeled full-corpus
  overview (cases by court, SCOTUS by decade era — the frozen bulk import
  included) gives composition context. The **live/historical-slice cert
  statistics** are what predictor and evaluator cells anchor on: disposition
  base rates computed over rows the supremecourt.gov channel wrote, each row
  counted `sample_weight` times so denials the earlier sampled walk kept at a
  higher weight do not bias them — the **modern discretionary-cert cut** (the calibration
  anchor, undiluted by merits-era labels), grant/deny by originating circuit,
  by relist count, by CVSG status, by **capital-case marking** over the same
  paid scored segment (whose `unmarked` bucket is an upper bound — read its rule
  below), and by **salience
  band** (the
  active scorer's frozen grant-likelihood tier over the paid scored segment), plus a
  by-originating-court reader table that names state courts. A coverage block
  states the pack's own denominators, and the per-Term array carries each
  October Term's cursor-derived filings census by fee class (paid/IFP),
  walk-complete flags, weighted estimates, grants, pace-to-grant, and the
  per-salience-band **segment base rate** in two forms — over the petitions that
  *ended* in a band, and over every petition that ever *reached* it (the risk
  set). A prediction carrying a frozen prediction-time band is scored against the
  second, since that is the population it was in when it ran; one that froze **no
  band at all** falls back to the first, which matches the terminal band it has
  to be grouped by. The fallback keys on the absence of a frozen band, never on a
  version mismatch: a frozen band whose salience version does not resolve against
  the pack yields no baseline at all, since relabelling it terminal would pair a
  risk-set population with a terminal rate. Under a scorer whose order interleaves a fixed-at-filing class
  among the trajectory tiers (the caption-banded versions' `federal`/`state`),
  "ever reached it" is read along each petition's own **reachable ladder**
  rather than along the band order: a federal petition was `federal` the day it
  was docketed and enters no weaker band's risk set, a state one climbs
  `state` → `high` and enters none of `federal`'s, `elevated`'s or
  `baseline`'s, and a private one enters neither caption band. So the class
  floors (`federal`, `state`, `baseline`) **partition** the scored segment
  instead of nesting into one another, and each band's risk-set rate is the rate
  its own reachable population faced — the weakest band's bracketed figure is
  the private class's own grant rate, not the whole segment's. A class floor's
  denominator is that class alone, so it is far smaller than the order prefix
  it replaces, and the caption floors are thin enough that the realized-Term
  floor above bites on them. The bracketed
  figures a committed pack carries are only ever as current as the
  `metrics-refresh` that rendered them, so read them against the pack's own
  vintage. Pooled strictly-prior-Term, as the recorded skill score is, both
  are leakage-safe; the board's realized-Term column reads the risk-set one off
  the case's **own** Term instead, which is deliberately not leakage-safe and is
  fenced accordingly where it is described (see the leaderboard bullet above). A skill score is
  only comparable within one basis, which `Evaluation.base_rate_basis` records
  alongside `Evaluation.base_rate_salience_version` — the version the band was
  read under, the other half of the same harness-stamped record, since two
  bases agreeing under different scorer versions are not one comparison. Both
  describe the surface a time-masked replay cell self-selects pre-cutoff
  Terms from. `fedcourts statpack` produces both the machine JSON and a
  rendered Markdown document — a
  deterministic, offline roll-up of the corpus — empty
  (zero counts, empty sections) until a corpus is present.

  The pack also carries a **stage axis** beside the cert sections: an
  **interim-docket section** (`interim`), present only once the corpus holds
  application rows (`YYAnnn` dockets — stays, injunctions, vacaturs, and the
  time-extension requests that dominate the docket), and omitted entirely —
  not emitted as null — while it does not; the merits section below joins by
  the same rule on its own feed. What it publishes,
  pack-level and per application-Term year: counts by parsed ask (extension /
  substantive / unknown, with never-parsed rows kept apart as a visible
  coverage gap), and — over the **substantive slice only** — the resolved and
  granted counts, a raw grant rate (resolved = a machine-matched interim
  disposition, so an unmatched resolution stays visibly unresolved rather than
  entering the denominator; withdrawn/dismissed resolutions count as
  ungranted), and the escalation-signal counts (response requested, referred
  to the Court, amicus on file — max-latched ending states, not
  as-at-prediction values, and no rate here conditions on them). **What may be claimed
  from it:** the pack-level counts and grant rate are *descriptive* facts about
  the accumulated cohort, nothing more — the pack-level rate is **not** a base
  rate for any cell, because it contains that cell's own Term. The scored
  interim baseline is built from the **per-Term rows** instead: the substantive
  slice pooled over application-Terms strictly before the case's own, and only
  where that pooled sample clears the per-pool floor pre-registered in
  [`docs/salience.md`](../docs/salience.md); below the floor a cell carries no
  baseline and no substitute. Either way the rate is comparable to nothing the cert sections publish (a
  different population resolving on a different standard, unweighted where the
  cert cuts are denial-reweighted). Extensions are counted so the docket's
  administrative dominance stays visible, but they never pool into any rate.
  The section carries no salience version, because it is not a salience-band
  product; the per-Term rows share the cert tables' replay self-selection
  rule (anchor strictly before the case's own docket Term,
  `record/context.json`'s `decided_before`).

  **The arrival cohort's claim rule** (the caption-banded scorers'
  `cert@arrival` cells — the active `sal-v4`, and earlier versions' cells beside
  it). The
  cohort is two selection rules with grant rates an order of magnitude apart —
  the unbiased random slice and the federal-petitioner carve-in — and the
  leaderboard's per-moment block pools them mechanically, so that block's
  pooled accuracy and mean Brier are **not claimable** without the per-rule
  cut; per-band skill stays honest (the band separates the two populations,
  `federal` vs the slice's mix). Only the random slice's skill transfers to
  live prospective use: it alone is selection-bias-free, and each of its cells
  is scored against its own caption class's arrival floor — the
  class-partitioned reached rate, since under the reachable ladder no single
  published figure is the unconditional paid-arrival rate — so the slice's
  pooled skill is a mixture over class floors. And no arrival cell
  minted before the first statpack rendered after its salience version was
  registered carries any baseline at all (the version-pinned pool's designed
  `None`) — its skill column is empty, not zero, and supports no claim.

  The second stage section is the **merits section** (`merits`), present only
  once a corpus row carries a parsed `merits_judgment` (the
  `backfill-merits-judgments` pass reading merits-bound cases' stored terminal
  entries), and omitted entirely — not emitted as null — while none does. What
  it publishes, pack-level and per grant-Term year (the October Term
  certiorari was granted in — a grant-date-keyed axis that does **not** align
  with the cert tables' docket-number Terms, since a petition docketed in Term
  T is routinely granted in T+1; Terms with no parsed judgment are omitted
  from the rendered table): the granted-cohort count, the `cert_order_excluded`
  count — the rows the pool guard removed, which are *not* part of that
  cohort — and the parsed count
  beside it (the backfill's own coverage — read `granted − parsed` as an upper
  bound blending still-pending cases, genuine parse gaps, and the proceedings
  that ended with no disposition to parse, so a recent
  Term's thin parse is mostly pendency), the six-way judgment distribution
  (affirmed / reversed /
  vacated / affirmed-in-part / DIG / equally divided), and the **disturbed
  rate** — reversed + vacated + affirmed-in-part over parsed, raw `n` beside
  it, with the two non-merits exits (DIG, equally divided) counted as
  undisturbed because both leave the judgment below standing. The population is
  the grants that open a merits proceeding — the same rule that mints the event
  a merits forecast is made on — so GVRs and summary reversals, whose
  disposition rides in the cert order itself, are absent: their vacaturs are
  cert-stage facts, already counted in the cert sections, and would otherwise
  count as disturbed judgments in cases no one forecast at the merits stage.
  The exclusion reads the row's cert disposition label and, where the label
  cannot be trusted, the grant→judgment gap: a parsed judgment dated on or
  before its own grant is excluded label-independently and counted in
  `cert_order_excluded` instead of the cohort. A parsed judgment carrying **no**
  date cannot be gap-tested at all, so that row stays in the cohort as a
  coverage gap and only its judgment leaves the parsed slice. Either way every
  parsed judgment in the cohort provably postdates its grant.
  **What may be
  claimed from it:** the counts are *descriptive* facts about the parsed
  cohort, and the per-Term **`disturbed_rate`** rows are the committed feed of
  the **registered merits Brier baseline**
  (`pipeline.base_rates.merits_base_rate` pools them across grant Terms strictly
  before a case's; `docs/decision-model.md` registers the design, denominator
  included: the two procedural exits sit in it as undisturbed). A merits skill
  claim exists only under that pooled strictly-prior baseline — never against a
  single Term's rate, the pack-level `disturbed_rate`, or any
  substitute — and only where the pool clears the baseline's stated minimum
  sample. The parsed slice
  is selected on parseability under **two** writers — a stored snapshot whose
  terminal entry matches the deterministic shapes, or a live poll of a granted
  docket, which reaches only rotation-eligible dockets and so covers recent
  Terms better than old ones — so quote the `parsed`/`granted` coverage beside
  any figure, and read a cross-Term coverage gradient as a writer artifact
  before reading it as docket history. It is unweighted and comparable to nothing the cert sections
  publish; DIGs and equally divided affirmances count as **undisturbed** and
  stay in the scored pool on that footing — the baseline's denominator counts
  them the same way, so scored population and baseline population remain the
  same population (the `procedural` stratum is keyed on mootness practice,
  which no merits outcome carries). The
  section carries no salience version, and the per-Term rows share the cert
  tables' replay self-selection rule (anchor strictly before the case's own
  docket Term, `record/context.json`'s `decided_before`).

- `docket.json` / `docket.md` — the **court-facing docket pack**: facts about the
  dockets themselves, for a reader with no interest in whether this project's
  models are any good. Composition by court and by decade era; then, over the
  live/historical slice of modern discretionary-cert petitions, the disposition
  split, the originating circuit, the relist count, the CVSG status, the paid/IFP
  fee class, a capital-case marking cut,
  `fedcourts docket` runs, and a reader table that names the state courts a
  petition came from;
  then a per-Term census of docketed filings against ingestion, grant rate, grants
  observed, and pace to grant. `fedcourts docket` produces both files.

  **It carries no prediction claim, by contract** — no accuracy, no ranking, no
  Brier, and no salience band. The band is the line: it is a statement about which
  petitions this project chooses to predict, so it belongs to `statpack.*` and
  never here. That exclusion is what makes the pack citable on its own terms.

  Read it the same way as the statpack's live-slice cuts: every section states its
  own scope, and every rate repeats its denominator. **Every cert cut is
  denial-reweighted** — including the by-originating-court table, which is the
  statpack's raw reader cut recomputed as an estimate, because it is the only
  place a state court appears and an unweighted rate over the walker's frame
  inflates the grant family several-fold. A reweighted denominator is written
  `est. n=` and a raw one `n=`, because the first estimates a population and the
  second counts rows; a breakdown row carries no raw view of its own, so a small `est. n=`
  is weaker evidence than it looks; the per-Term census is the exception and
  prints the observed `ingested (rows)` beside the estimate.
  `(none)` and `(unknown)` buckets are rendered rather than dropped, so a coverage
  gap is never hidden inside a rate — `(unknown)` on the relist and CVSG cuts means
  *not yet parsed*, not *did not happen*. The **capital-case cut** carries the
  same shape of caveat one step further, and its inline scope note says so: the
  flag is latched from
  supremecourt.gov's own `bCapitalCase` field OR-ed with the
  `*** CAPITAL CASE ***` annotation it appends to the docket number, and no
  other channel serves either reading, so `last_live_polled` is that column's
  coverage sentinel and an unpolled row would bucket `(unknown)` — none will,
  since both packs' capital cuts are live-slice scoped, which *is* that stamp.
  Inside the slice the stamp records an attempted poll rather than an ingested
  payload, so `unmarked` means *no channel that wrote this row read either
  signal* — silence, not a denial. Read `unmarked` as an upper bound:
  contamination runs one way, into that bucket, so it can only shrink an
  observed gap between the two, never widen it. That bounds the *comparison*,
  not the capital rate itself, which is a floor only if the rows a poll did
  reach are outcome-representative of the rows it did not. And the cut is
  **marginal**: it says what the two populations are, never what the marking
  adds over the relist, CVSG and band cuts beside it — a claim only a
  conditional comparison can support. What the petitions are about — the
  `qp-topic-v0` claim taxonomy of `docs/qp-topic.md` — renders as its own cut of
  primary labels the next time `fedcourts docket` runs over a gate-passing labels
  artifact, always beside the labeler that produced it, that labeler's agreement
  with the reference rater against the rate a constant labeler scores (agreement,
  **not** accuracy), the labels that vocabulary cannot yet measure, and the inline
  scope string it requires — which says in the same breath that no reweighting
  recovers the docket, so that cut's `est. n=` is the one denominator here that
  rescales a QP-bearing stream rather than estimating a docket population. The
  labeled rows are a **partial frame** — the labeling accrues one batch a run —
  so that scope string also names what the gap between labeled and in-scope rows
  is made of. How many of those rows carry a questions-presented text at all is
  the count that separates the two halves of that gap, and only the extract that
  cut a batch can take it: where the newest batch's ledger entry carries it, the
  string states the labeled share of the QP-bearing frame and measures the
  reference block's over-representation, both as the labels artifact's own
  figures at **that batch's** corpus vintage rather than the pack's (the frame
  grows with every pull, so the two are different ratios and are never divided
  into one). Because that growth is one-directional while the labeled count moves
  only when a batch lands, each figure states which way it errs against the frame
  as it now stands — the share a ceiling, the factor a floor — so neither reads
  as a measurement of this blob. Where the ledger carries no count, the string
  says the split is unrecorded and bounds the over-representation from above; and
  two states of the table itself outrank a frame, since the factor describes the
  table's mix: no drawn row at all publishes an unbounded factor, and a table
  whose own rows are all labeled over a frame labeled out publishes no factor. Each bucket also prints the rows on
  hand behind it, and its reference-sourced share of them, because a
  denial-reweighted `est. n=` runs above the rows read and the thinnest buckets
  here rest on a handful. The committed copy of the document names the missing
  distribution among its gaps until someone runs `fedcourts docket` where the
  corpus is pulled — it is on demand, on no schedule. The document names the other statistics it
  cannot yet compute the same way (summary reversals, which have a disposition
  label no resolver mints — `Outcome.disposition_route` marks the class on a
  resolving grant, but that marker feeds no published cut, so the pack's
  `summary-reversal` count stays zero while such orders sit inside `granted`;
  justice-level statistics, which need a per-justice vote record) so a
  citation is never read as a claim that the figure is zero.

- `big-cases.json` / `big-cases.md` — the **case-centric big-case board**: one
  row per predicted case, carrying each predictor's current `big_case_score`
  and the mean across the predictors that gave one, ranked by mean descending,
  then `n` descending, then `case_id`. It
  answers which cases the panel thinks matter and where the models disagree —
  a question none of the other big-case surfaces answers, because each of those
  measures something about the *models*. It is the board a public site
  highlights, which is why the JSON carries its reading rules in a `provenance`
  block rather than leaving them here: a figure travels without the document
  that explains it. `fedcourts big-cases` produces both files, from `data/`
  alone.

  **A stakes read is neither scored nor ranked**, so nothing here is a
  forecast, an accuracy, a calibration or an ordering of predictors, and the
  mean says nothing about how likely a case is to be granted (a case can be
  denied yet high-stakes, or granted yet narrow). For the same reason the board
  reads the ledger directly: neither the forward-claim exclusion nor the
  leakage exclusion applies, so a leakage-suspected cell the scored boards drop
  is still a row's read here. That is the same carve-out the leaderboard's
  `big_case` and `evaluator_agreement` views take, on the same grounds, and it
  is a caveat that has to travel with any number quoted from the board.

  **The collapse: the moment first, then the predictors on it.** A row is one
  **moment** of a case and every predictor's read of that moment, so the reads
  the mean pools are answers to the same question. The case's current moment
  (`moment` on the row, with `moment_opened_at` beside it) is chosen from the
  **docket** rather than from run times — with the one fallback below, where the
  docket gives no date at all: the newest **predicted** event by its
  `opened_at`, ties broken by the docket's stage progression — the petition's
  arrival, then its distribution, then the interim application's arrival, the
  response requested on it and the response filed, then the CVSG, then the
  merits moments — and then by event id, so a date collision never inverts the
  order a case is actually walked in; an event whose definition records no
  `opened_at` is ordered by the **day** of its first prediction's harness clock,
  which therefore falls through to the same tie-break. One exception the
  pre-registration records
  ([docs/freeze-record.md](../docs/freeze-record.md)): the cert petition
  baseline's `opened_at` is **docketing**, while the moment it declares is the
  distribution, so on those rows `moment_opened_at` is the day the petition
  reached the docket rather than the day its moment arrived — it is ordered on
  anyway, because the distribution has no date in committed data and docketing
  is still a docket fact that moves only when the docket does. A re-predict of
  an older moment therefore cannot move a case's moment, and only a newly
  predicted moment can. "Newest" is over the events the panel was **asked**
  about, so a row lags the docket wherever no cell has been dispatched on a
  newer event. Each predictor's
  read is then its **newest run on that moment**, newest by the harness-written
  cell clock (the process stamp, else `created_at`) rather than by directory
  name, with run id breaking a tie. A predictor with no run on that moment is
  excluded from `n` and from the mean exactly as a declared no view is — never
  carried over from an older moment — and its earlier read stays under its own
  event as history, never averaged.

  **The coverage consequence, which is the price of the collapse.** Where a
  fresh moment has been minted for some predictors and not others — an engine
  losing cells to capacity, or a forward cell refused because its provisioned
  snapshot exceeded the predict lane's staleness bound — the row shows the
  newest moment at a
  **small `n`** rather than a fuller `n` on a stage the docket has left behind.
  That is the honest reading: the alternative, "the moment most predictors have
  reached", shows a stale stage to keep `n` high and moves when coverage
  changes rather than when the docket does. The previous moment's fuller panel
  is in the row's per-event entries, which a site can render as history. A case
  whose current moment drew only declining reads is off the board entirely,
  counted in `cases_without_score`, rather than having an earlier moment's
  scores promoted back into a current read.

  **Three collapses, never differenced.** (1) The leaderboard's `big_case`
  block reads a case as the **mean over its moments** before correlating it
  with the evaluator panel — bigness is a property of the case, so its moments
  are not independent observations there. (2) A **row** here is the newest
  moment the panel has been asked about, and each predictor's newest run on it.
  (3) An
  **event entry** here is each predictor's newest run on *that* event, which is
  how an earlier moment stays visible as history. Each answers a different
  question over a different population, so a figure from one is never
  differenced against a figure from another — and the leaderboard's is narrower
  on axes this board does not share: cells a judge has graded on either build,
  and the frozen partition on the default `all` build, which the `frozen`
  comparison build shares instead. The artifact's own
  `leaderboard_divergence` string is worded for the build it ships on.

  **Denominators.** `n` sits beside every mean and is the count of predictors
  that gave a number. A newest run declaring **no view** — the prompt asks for
  a score or an explicit `null` carrying a one-line rationale — leaves that
  predictor out of `n` and out of the mean; it is never imputed and never
  counted as a zero, which would fabricate a panel opinion. A row with `n < 3`
  is ranked with the rest and flagged by its own `n` rather than split into a
  second table: the flag is the denominator, and a reader who quotes a mean
  without it has quoted a different number — the more so under the moment-first
  collapse, where a freshly minted moment can leave `n = 1` while the board's own
  roster (`predictors`, itself scope-dependent) holds more. `score_range` sits
  beside `n` for the same reason — a mean of 0.5 over two 0.5s and a mean of 0.5
  over 0.1 and 0.9 are not the same observation. `moment` is the third such flag,
  and the collapse sharpens rather than settles what it guards: each row is one moment,
  so a row's mean **is** comparable across its own predictors, but two rows on
  different moments are not comparable to each other and the `#` column orders
  across moments anyway. The panel reads stakes systematically higher at later
  moments, so a row's position reflects which question its panel answered as
  well as how big its case is.

  **Population.** Every case in the committed ledger carrying at least one
  **in-scope** scored read on its current moment, pending and decided alike,
  with a status
  per row derived from `outcome.json` presence on its predicted events and the
  realized disposition on each event that has one. `status` is the **case's**
  grain, not the moment's — the one such figure on an otherwise moment-scoped
  row, so a case can read `resolved` on an earlier event while its `moment` is
  still pending. Two counts sit beside `cases` and are never added together:
  `cases_without_score` is the predicted cases whose in-scope reads carry no
  number — a panel that declined — and `cases_out_of_scope` is the cases no run
  of which is in `process_scope`, which is this build refusing to read them. The
  test is ordered — out of scope wins where both would hold, since a case with no
  in-scope run cannot be observed to have declined — so a filtered build's
  `cases_without_score` counts in-scope decliners alone. On the default `all`
  build the second count is zero. The list is the
  predictions', never the corpus's, so the board describes what the panel was
  asked about and is **not** a sample of the docket or of any conference.
  Display is by caption — the `event.yaml` title of the case's current moment,
  whose event id `caption_event_id` repeats so the rule is checkable against the
  row — because there is no docket number in committed data; `case_id` is the
  identifier.

  **Process scope, and why the default is version-blind.** `process_scope` says
  which process versions a **current read** may come from. The default is
  `all`: every committed run is eligible, shakedown, pre-freeze,
  retired-digest and unstamped cells included, because the board is a census of
  what the panel said rather than a measurement of how well it said it, and a
  stakes read resolves against nothing for a partition to protect.
  `fedcourts big-cases --process-scope frozen` builds the **comparison** board,
  admitting only runs whose harness stamp is in the blessed digest set and was
  written at or after the freeze instant — the predicate the performance boards
  scope on. On that build a pre-freeze, retired-digest, shakedown or unstamped
  run is **history** under its event, never a current read, never in `n` and
  never in a mean; the scope is applied before the moment choice, so such a run
  cannot move a case's moment either. The per-event entries are unfiltered on
  both settings, and both publish `process_scope` and the `frozen_process`
  record they key on.

  **What the frozen build holds out, which is why it is not the default.** It
  does not thin the board evenly. A **resolved** case is never re-predicted, so
  one whose reads all predate the freeze can never be refilled into scope — a
  case first predicted after the freeze stays in scope through its own
  resolution. The re-predict rule (`REPREDICT_MOMENTS` in `pipeline/pull.py`)
  re-owes only the cert distribution, the CVSG and the three interim moments, so
  a case sitting at a cert **arrival** moment or at either **merits** moment is
  never refilled however long it waits. Those are a floor rather than the whole
  of it: a pending case at a moment the rule does re-owe can still sit outside,
  because a distribution is re-owed only while a conference is still ahead of it
  and because a re-owed cell has to be minted and land before it counts.

  Measured over the ledger at `64e8568b7`, the frozen build **removes 76 of the
  193 rows** — including the whole of the `all` board's top 20, since the frozen
  board's rank 1 is the `all` board's rank 21 — and **`cases_out_of_scope` reads
  78**, not 76: it also absorbs the two predicted cases that were already off the
  `all` board for carrying no score, which at `frozen` have no in-scope run at
  all, so `cases_without_score` there reads 0 rather than 2. What survives
  carries no merits moment and no cert-arrival moment at all. It is a
  live-cert-and-interim slice of a selected population: a legitimate thing to
  look at, and the wrong thing to publish as the census. The board states the
  hold-out in its own `population` and `version_scope` provenance strings.

  **No count, mean, rate or spread statistic is differenced across a scope
  change.** A row's own mean and `n` move when one predictor's read falls outside
  the scope, and every denominator moves at once, so a coverage rate that rises
  on the frozen build rises by construction — the older cells the rate's
  numerator was missing are exactly the cells the scope removed (`missing_reads`
  goes 21 → 0 over the ledger at `64e8568b7`). That is never the pre-registered
  coverage rise [docs/freeze-record.md](../docs/freeze-record.md) describes.

  **No time series.** The predict prompt's amendment making `big_case_score`
  required with an explicit null escape changed which cells carry a read
  ([docs/freeze-record.md](../docs/freeze-record.md)), so scores elicited
  before and after it are two populations. The board therefore publishes no
  trend and no history, and a movement across that boundary is not a
  measurement of anything. On the `frozen` comparison build every current read
  post-dates that amendment, since the freeze instant does, so there the
  boundary bites on the per-event history rather than on the rows — and no
  trend is published there either, because a read elicited under one ask is not
  a revision of one elicited under another. Nor is a movement between two
  consecutive daily builds: a row's mean, `n` and rank also move when its
  `moment` does, which is the docket advancing and the whole panel switching
  question at once, not a predictor changing its mind.

  Like the other roll-ups here it is byte-stable and stamps neither a clock nor
  a commit: the vintage of a board is the commit that wrote it. The daily
  `big-cases` job of `run-analytics` keeps it current, so an unchanged ledger
  opens no PR.

These files are deterministic, offline roll-ups that start empty (zero counts)
until their input lands — the evaluations ledger for the leaderboard, the
predictions ledger for the big-case board, a corpus
with outcome labels for the back-test, statpack, and docket pack. All are small
and worth reading
in a diff, so they are git-tracked rather than pushed to the corpus remote like
the corpus blob.

**Statpack directions not built.** The published stat packs
(SCOTUSblog / Empirical SCOTUS) carry whole families of statistics this
project's docket-first corpus cannot compute yet, kept here as named
directions rather than silent gaps: justice-level statistics (frequency in
the majority, agreement matrices, opinion authorship — need per-justice vote
data, e.g. a Supreme Court Database import), amicus-brief counts per petition
(need docket-entry parsing beyond the proceedings), oral-argument statistics
(need transcript data), and a merits circuit scorecard (affirm/reverse by
court below — the parsed merits judgments carry no cut by originating court).

**What may be claimed from an agreement rate.** A `qp-topic-v0` labeling run
(`data/qp-topics/qp-topics.json`, `docs/qp-topic.md`) produces one instrument
this document does not otherwise carry, and it is not a skill number: it is
**agreement with the v0 reference raters, never accuracy**. Reference
error and labeler error cannot be separated — least of all on the boundary
labels, which is where the disagreement lives — and the reference rater was
itself an agent session, so agreement with a labeler of the same model family
partly measures shared convention rather than correctness. Three rules travel
with the figure. **Always with its `n`, and always beside the floor** a constant
labeler would score on the same entries — the largest reference class's share:
about 23% over the full 353-entry set, ~26% on the supplement's own mix. The
rate alone is unreadable, and only the distance
above the floor is anything a labeler did. **Per-label rates only at or above
the support floor** — five of the sixteen labels have fewer than 10 reference
examples, and under the floor a label is published as a raw count, not a rate.
**A pooled rate is not a per-stream one**: the founding reference block
contains every QP-bearing grant and 40 of 855 denials, so that block's rate
certifies the grant stream only. The **stratified supplement** (164 texts — adding 100
of the remaining 815 QP-bearing denials, which brings the set to 140 of 855,
plus 44 of 87 GVR and 20 of 83 dismissed) is the block a denial-heavy cut's
quality is conditioned on, and every batch **covers** it: the first cleared all
353 entries of both blocks with none uncovered, which is the coverage condition
a published cut waited on. It is not a rate for the supplement — a pooled figure
is the same however the disagreements fall between the blocks — so the pooled
rate still certifies the grant stream, and the denial/IFP stream that dominates
any reweighted cut is measured at review rather than by the artifact, which
carries the pooled figure only. The deterministic shadow rules'
disagreement count is a regression trip-wire on one labeler's movement between
runs, not a second measurement — its *level* is uninterpretable off the
reference set. **The artifact accrues and the headline rate does not**: the
labeling frame outruns one dispatch, so the file is the union of many batches
while its top-level `agreement` is the most recent batch's alone. A rate quoted
from that file therefore certifies the batch that produced it, not the labels
beside it; the per-batch `batches` ledger carries each run's own `agree`/`n`,
and a claim over the whole file has to say which batches it is reading. No topic label enters a claim score, a leaderboard rank, or any
denominator here; a labeling run describes the corpus and commits a predictor to
nothing.

**What may be claimed from the party census.** `fedcourts party-census`
(`pipeline.party`, [docs/cli.md](../docs/cli.md)) annotates every unweighted
live-slice row from its caption — `federal_party` and `state_party` as none /
petitioner / respondent / both, the administration a federal party's date falls
in, and a president's surname appearing as a party — and prints the counts. It
is descriptive corpus structure, not a performance instrument: no annotation
enters a claim score, a leaderboard rank, or any denominator here, and the
census publishes **counts only**. A grant rate by government-party status is a
different artifact with its own scope string and denial reweighting; computing
one from these cells would inherit every caveat below without carrying them.
Six rules travel with any figure quoted from it, and the first two are the ones
that invert a conclusion when they are skipped. **No cross-administration reading
without holding the docket stratum fixed.** The windows hold very different
mixes of paid cert, IFP cert and applications — on the blob pulled 2026-09-08
(newest stored snapshot 2026-07-13), the `filed` frame runs 91% paid under
`trump-45` and 31% paid under `trump-47`, which carries 1,949 application rows
against `trump-45`'s none — and the federal-respondent rate differs sharply
between the strata, so the pooled share climbs 22.8% → 23.4% → 33.5% across the
windows while the paid-cert share is flat at 21.4% → 22.3% → 21.7%. The window's
*size* is not the confound; its *composition* is. Both the numerator
(`federal_by_administration`) and the denominator (`frame_by_administration`)
are therefore keyed on the stratum, and only a stratum-matched share is
readable across windows — the paid-cert stratum being the one captured whole in
every window, since the excluded one-in-ten sampled denial block is entirely
IFP and covers OT2017–OT2024, leaving the two newest Terms of a frame that runs
to OT2026 with no exclusion at all. **And one stratum is not rescued by holding
it fixed**: because the exclusion *is* the IFP stratum, the older windows'
`ifp-cert` cells are the complement of a systematic sample — frame coverage of
the estimated IFP stratum runs about 3.6% in each of the two older windows
against 74% in the newest — so no `ifp-cert` series may be read across windows
until this census gains reweighted cuts. **Always with the date convention and
the rule version**, both stamped on the artifact (`as_of_field`,
`rule_version`): a petition filed under one administration is routinely
resolved under the next, so two cuts are comparable only where both stamps
agree — and with the corpus vintage the census prints beside them
(`latest_pull`, `latest_snapshot`), since every count here is a corpus-state
reading. **A `resolved` cut's newest window is right-censored**: a pending
petition has no resolution date, so it leaves its window for the unattributed
cell (`pending` is the size of that mass — 1,364 rows on the same blob, all but
one of them filed under the newest administration), and the newest window's
`resolved` count is a floor, never a total. That `pending` and `undated`
coincide exactly under `resolved` is a **measured** fact about this blob, not a
structural one: the two are counted separately so that a dated row carrying no
label — a divergence — reads as the counters working rather than as a bug.
**The administration is the date's, not the caption's** — official-capacity
captions auto-substitute on a transition and the stored caption is
as-of-last-pull, so nothing here reads a party's *name* for attribution, and a
federal party may be a court or an agency the executive does not speak for, so
the label names who held office rather than asserting the administration was
the litigant. **`named_president` is a
name match, not an identification, and not a personal-capacity flag on its
own**: it fires on official-capacity captions too (they name the president),
so the personal-capacity family is the flag together with `federal_party`
`none`; a private litigant of the same surname fires it, measurably — over all
140 matches on the same blob, 14 (10%) do not name the president: 7 of 8 `Bush`
and all 6 `Clinton` are namesakes or a non-president of that surname, against
93 of 94 for `Trump`, 30 of 30 for `Biden` and 2 of 2 for `Obama`, so the error
concentrates almost entirely in surnames whose presidencies predate the live
slice. Two limits close the list. Every `n` counts **docket rows, not
disputes**: one dispute routinely holds an application row and a petition row,
and a re-docketed case appears more than once. And the caption is the last
limit — a styled caption (`In re`, `Ex parte`) has one party and is annotated
from it, and an anonymized or initialized IFP caption carries no classifiable
party at all, so `none` means "no sovereign the caption names", never "no
sovereign".

**What may be claimed from the tool-usage rollup.** `fedcourts tool-usage`
publishes call counts, per-engine result observability, per-cell cost, and a
call-volume-against-Brier table. The counts are facts about the pipeline and
carry no process scope; the Brier column is a **grade** and carries one —
blessed processes only by default, `all` under `--all-versions`, stamped in
`process_scope` and printed beside the table, because a grade with no scope
beside it is not readable. It is an **ops view, not a scored board**: it shares
the boards' process scope and their one-grading-per-judge collapse, but it does
not apply the forward-claim or leakage exclusions and it keys its `mode` on
the harness's own `retrieval_log.json` record rather than on the derived
stratum, so its
population is a superset of the leaderboard's and a figure that differs from a
board figure is two populations rather than an error in either. Nothing is
pooled across modes or across forecast moments, in the table or in the
coefficient.

**No correlation between retrieval and accuracy may be claimed.** A rank
correlation is published only for a (mode, stage, moment) population that clears
`tool_usage.TOOL_USAGE_CORRELATION_MIN_CELLS`, a floor declared in code ahead of
any coefficient rather than chosen once one is in view; below it the value is
**withheld**, not merely unreported, and the surface prints denominators and an
under-powered verdict. Above the floor it stays **descriptive, never causal**:
engines are pooled within a row, so the coefficient carries every difference
between them — prompt, model, sandbox — and a cell calls more tools partly
*because* its case is hard. Brier is a loss, so the negative sign is the one
that would mean more calls beside better forecasts; a cell whose log hit the
per-log call cap is right-censored on the call axis, and the count of those is
published beside the coefficient.

**A result-observability rate is two states, not three.** A captured
`result_digest` proves the result side was recorded and non-empty; a null covers
an empty result *and* a result the engine's transcript never carried. The
per-call `result_capture` marker separates those two, but only the logs
captured since it existed carry it; on the rest it reads null — capture-unknown,
a third state again, and a ledger-wide rate pools both kinds. So the rate
is a floor on how much
of the answer side is observable, never a hit rate, and its denominator is every
call including builtins. An engine with no captured MCP result anywhere has its
per-tool dead-end rows **withheld** rather than printed as 100%, and where they
are printed they are an upper bound.

**For a code-mode engine, a call count counts call sites in program text.** Its
calls — the manifest tools, and the engine's own builtins beside them, which is
where such a program does most of its work — are written inside a freeform
builtin call's program and lifted
from that source, so what `calls` and the offered-vs-called table's *called in*
report is how many times a tool is *named* in the programs, not how many times
it ran: a site inside a loop counts once however many times the loop turned, a
site in an untaken branch or a comment counts though it never ran, and a call
reached through an alias or a computed name is not counted at all. It is
therefore neither a floor nor a bound on invocations. The claim it supports —
and the one the offered-vs-called cut needs — is *the program asked for these
tools*. It is not an execution trace, and no per-call rate should be built on it.

**A raw call total is not one row per invocation for every engine.** A
code-mode engine reaches everything from inside a freeform builtin
call, and the log carries both: the builtin call's own row and a lifted row per
call the program made, manifest or builtin (`RetrievalCall.call_source`). So a
program making three manifest calls and six shell reads contributes ten rows —
and the builtin term dominates in practice, since a program calls its shell
many times more often than it calls the manifest. Any figure denominated
on *every* call — the result-observability rate above, the call axis of the
call-volume-against-Brier table — counts the wrapper beside the calls it
wrapped, for that engine only. Three readings follow. Gate on the MCP predicate
wherever the question is about manifest use, which the offered-vs-called cuts
and every throttle figure already do. Do not read a code-mode engine's call
*volume* beside another engine's as a behavioural difference: part of the gap
is one call shape being recorded twice over, and the per-log call cap applies
to the combined rows, so such a cell is also right-censored sooner. And treat
every per-engine cut this touches — the observability rate, the mean call
counts, and which engines appear in the offered-vs-called table at all — as
**scoped to the logs that could express it**, since a lifted row exists only
where capture minted one. A code-mode engine appearing to call no manifest
tool over a stretch of the ledger is a capture fact, not a behavioural one.
Which idioms the lift matches decides how many rows a program leaves behind, so
a ledger-wide cut over a code-mode engine pools logs captured under whatever
lift each was minted with — exactly as a throttle count pools predicates, and
for the same reason: rows are written once at parse time and no committed log
is ever re-derived. That reaches the call total, the observability rate, and
`result_capture_coverage` alike, so a move in any of them across runs may be a
capture change rather than a behavioural one. Date the cut before reading it.

**What may be claimed from the throttle counts.** `result_status` on a
`RetrievalCall` marks a result the shared upstream quota refused, and the counts
built on it — the log's `throttled_calls`, the per-run note on a predict /
evaluate PR, the tool-usage rollup's per-engine cut — support exactly one claim:
*these cells retrieved less than they asked for, so do not read their coverage
beside a well-fed cell's.* Three limits bind every figure. It is a **floor**: the
predicate is anchored on the pinned MCP release's own rate-limit phrasing and
biased to miss a throttle rather than invent one, it is read only from
manifest-tool results, and a call a starved cell gave up on making leaves no row
at all. Its denominator is **observed manifest-tool conditions**, not calls, so
an engine whose transcript drops results shows an em dash rather than a clean
zero — capture-blind is not throttle-free, and the surfaces say so where the
number is printed rather than in a footnote. And the **per-engine cut is
descriptive, never comparative**: the quota is one bucket every cell of a run
draws from, so which engine's cells hit the wall records ordering and
concurrency within that run, not a property of the engine — no engine may be
ranked, differenced, or excused on it. Statuses are baked at parse time and
never recomputed, so a ledger-wide count pools whatever predicate each log was
captured under, exactly as `process_version` scopes a grade.

**Throttle coverage is uneven across engines, so the denominator is not
comparable between them.** How much of an engine's manifest use can carry a
status at all is a property of what its transcript exposes, and the three
engines differ in kind rather than by degree, and the artifact says which case a
row is in rather than the engine's name doing it. Where an engine pairs each
call with its own result, its manifest calls are observable and its figure is a
real ratio. Where the engine's telemetry logs no result payload at all, every
row is `unobserved` by construction and it can never be observed being
throttled — coverage that is **structural**, so an empty figure there is no
evidence of a clean run. The third case is a **code-mode** engine, whose
lifted rows carry `RetrievalCall.call_source: code_mode_source`: it invokes its tools —
manifest and builtin alike — from inside a freeform builtin call, and only that
call's *combined*
output is captured. No part of that output is attributable to an individual
call inside it — a single call site may run many times, and the output also
holds whatever else the program did — so every lifted row is `unobserved` by
construction, and such an engine likewise **cannot be observed being
throttled**. Its manifest calls are counted; its results are not read. Two
consequences bind any reading. A cross-engine throttle comparison is
**denominator-incomparable** on top of being descriptive — the engines differ
in what could be seen, not only in what happened, and only one of the three
supplies a real denominator at all. And the denominator moves with capture: a
log carrying no lifted rows is one capture never minted them for, not a cell
that made no manifest call, so a ledger-wide cut pools stretches with
categorically different coverage. Read a per-engine throttle number as scoped
to the logs that could express one.

**The backtest-as-iteration doctrine.** Backtests (the retrospective stratum,
the replay runs, `backtest.json`, `cert-backtest.json`,
`salience-replay.json`) are **iteration
instruments** — for tuning prompts, retrieval, and calibration — and are
**never claimable performance**; the project claims results only from genuine
forward predictions. Timing is the integrity mechanism: the prediction's
harness clock (`fedcourtsai.integrity.cell_clock` — the process stamp, else
the unstamped cell's `created_at`) against the outcome's `resolved_at`, both
committed artifacts, decides the stratum — not any restriction on what a cell
could retrieve. Replay cells run with the same tools as forward cells; the
cross-evaluator's leakage grading (the `leakage` block on each
`evaluation.json`, read off the harness-captured `retrieval_log.json`) makes
contamination of the *iteration signal* visible, and its coarse bit is what
takes a contaminated cell out of every scored figure (*The leakage exclusion*
above). Timing alone cannot: it is the control over what a cell was *placed*
to see, and a mis-provisioned cell that claims `forward` is precisely the case
where the placement is not what the record says. The two mechanisms are
complementary and neither substitutes for the other.
