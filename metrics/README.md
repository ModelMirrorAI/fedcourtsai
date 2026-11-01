# Metrics

Pipeline metrics: small, deterministic, git-tracked roll-ups whose reviewed
diffs track predictor and corpus quality over time.

**Process scope: frozen vs alpha.** Every claimable figure here about
*predictor performance* is scoped to the **frozen** process partition
([docs/process-version.md](../docs/process-version.md)): a cell counts toward
a frozen-scope performance artifact only if its **prediction's**
`process_version` stamp lies in a **counting window** (`COUNTING_WINDOWS`: one
per blessing of a predictor digest, from the counting instant of the label that
blessed it until a successor's closes it) that no revocation de-counted, and
is its predictor's counted forecast of the event — the earliest window's, where
the predictor holds cells from several — the partition keys on the prediction
because the predictor is the competitor being ranked; the evaluator's own
digest is recorded and never enforced for counting — *and* the evaluation's
own harness stamp is at or after the instant that opened that prediction's
window (the stamp, never the agent-written `created_at`: the boundary rests
only on clocks the agent cannot write), each instant set in the
pre-registration commit a `prereg/<label>` tag marks. A **closed** window's
cells keep counting under the label that opened them; a successor de-counts
nothing. Everything else in `data/` is the **alpha/shakedown ledger** — cells
written before the stamp existed (they carry no `process_version` at all; the
absent stamp is the marker), or run or graded before their window opened, or
stamped under the predictor digests of a label before `proc-v8`: a
**declared-shakedown cohort**, de-counted when its label was superseded,
whose period is describable as a beta only because its declaration — a dated
entry in the freeze record — preceded the outcomes of the claim window it
governs (the declaration itself states any slice whose own outcomes had
already resolved). A window's cells are otherwise de-counted only by a
**revocation** for a defect, on its own dated entry
([docs/process-version.md](../docs/process-version.md)); a single event whose
outcome describes another petition is **voided** on its own dated entry (*The
voided-event exclusion*, below). Alpha cells stay
committed with their timestamps, but they are **excluded from every
frozen-scope performance artifact and from any claimed performance result** —
they exercised the pipeline while the process was still moving, and nothing
about them was pre-registered. `leaderboard.json` and `claim-scores.json`
publish which scope they were built under as `process_scope` (`"frozen"` or
`"all"`); an `"all"` build — the `--all-versions` CLI toggle — is a
diagnostic view, never a results surface.

**The registered reading pools windows.** The registered rule, declared in the freeze record ahead of its
implementation, makes a predictor's **default figure its forward track
record**: every counted cell in every window no revocation de-counted, still
one counted forecast per (predictor, event), the earliest window's, so pooling
adds and drops no cell, and computes the figure over the pooled cells exactly
as over one window's, never as an average of window figures. It treats a
`predictor_id` as one forecaster whose process evolves, model changes included,
and its figure as that forecaster's record, not a property of its current
process or model: `claude-baseline`'s `proc-v8` (`claude-fable-5-1`) and
`proc-v9` (`claude-opus-5-5`) windows are one pooled record, as are
`codex-baseline`'s `proc-v8` (`gpt-6-astra`) and `proc-v10` (`gpt-6.1-sol`)
windows and `gemini-baseline`'s `proc-v8` (`gemini-3.1-pro-preview`) and
`proc-v10` (`gemini-4-argon`) windows. Each counted
forecast was registered before its outcome existed and no later window can
replace it, so the pooled record is out-of-sample however the process changed.
No Term or trailing bound applies; a bounded figure is a cut. Under that rule:

- each pooled figure states its **composition**, each window it pools by label
  with its `n`, and the per-(predictor, window) figure is the **by-protocol
  cut** published beside it — a comparison over different events (a
  successor's are those the closed window did not reach), never a measurement
  that a change helped;
- **engines are compared over paired events** — the events on which every
  compared engine holds a counted cell, from whichever windows — because each
  engine's pooled event set drifts with its own history; the complete grid
  becomes that paired-event figure with no window restriction, the board's
  paired set is the intersection over every engine it ranks, and a rank is
  read off it, never off pooled entries over differing event sets;
- a harness boundary the freeze record dates under an unchanged digest (the
  predict-cell hide is one) cuts nothing out, but the pooled and paired
  figures carry each engine's `n` on either side of it;
- an engine CLI update under an unchanged digest is composition in the same
  way: it cuts nothing out, each cell's `usage.json` records the
  `engine_version` its binary reported, and a by-version cut is a comparison
  over different events; a cell recorded before the field existed, or one
  carrying an `engine_version_discrepancy`, has an unknown version, never a
  guessed one;
- every figure computed from an evaluator's judgment — `mean_reasoning_quality`,
  the `big_case` and judge-validation tau-b, `evaluator_agreement`, the
  semantic grades — lists each evaluator digest it spans with its `n`; its
  per-rubric reading (on the board, `reasoning_quality_rubrics` and
  `by_signature`) is the claimable figure, and a value pooled across rubrics
  is coverage;
- pooling windows licenses **no other pooling**: stratum, stage and moment,
  salience band and version, scoring baseline, claim-set version and every
  other registered boundary still cut the pooled figure;
- **revocation** stays the only de-count of a window's cells, and a
  **void** the only de-count of a single event's (*The voided-event
  exclusion*, below), each on its own dated entry stating the defect;
- `release-sensitivity` and `semantic-summary` pool with the breakdown rather
  than refuse.

**Every frozen-scope surface is built to that rule, and the leaderboard's
per-rubric readings are too.**
On the leaderboard and each of its stage blocks:

- each entry is the predictor's pooled record, with its composition as
  `windows` — each window by label and opening instant, with its `n` in
  gradings — listed even when it pools one window;
- the per-(predictor, window) entries ride beside them as `by_protocol`, never
  ranked;
- `paired` is the paired-event figure. Its engines are every predictor holding
  a counting window neither closed nor revoked and at least one counted forward
  cell graded with both an accuracy and a Brier score; its events are those
  every one of them holds such a cell on, from any window, with no band
  condition. Each engine's aggregate is taken over its qualifying gradings on
  those events, beside its `unpaired_events` (its pairing loss). Each paired
  event is filed under the band of its earliest qualifying cell by harness
  clock, and `band_mismatches` counts the paired events whose engines' cells
  carry different band keys;
- the board's `rank` is read off `paired` — forward accuracy, then forward mean
  Brier, then `predictor_id` — and printed on each entry beside its
  `paired_events`. The figures a rank rests on are that engine's
  `paired.entries[].forward`, never its entry's own `forward`, which spans
  events no other engine shares; a rank is quoted with `paired.events`, and with
  each engine's `paired.entries[].forward.evaluations` beside it, since the
  paired events fix the event set and not the panel depth. A predictor outside
  the paired set, a retired one or one with no qualifying cell, is listed
  unranked, and an empty paired set ranks nobody. The stage blocks carry the
  same paired figure, unranked;
- each pooled entry, and each engine in `paired`, lists as `boundaries` every
  registered harness boundary (`process_version.HARNESS_BOUNDARIES`) that falls
  inside its cells' span (its carrying commit's time between their earliest and
  latest harness clock) and has cells on both sides of it or any cell with no
  `pipeline_sha`, with `before` and `after` counted over every cell the
  boundary's predictors and mode admit, and `unstamped`, the cells with no
  `pipeline_sha`, on neither side. A cell's
  side is the conditioning entries' ancestry test: after where the carrying
  commit is an ancestor of, or equal to, its `pipeline_sha`. `scope` prints
  the cells the change can reach (`self-represented dockets`, `granted
  dockets`, `all`, `replay cells`) and is never a filter, since a docket's
  representation or grant state at a cell's moment lives only in the corpus:
  for a docket-scoped change, and for one marked `gradual` (it reached the
  corpus by back-fill), `after` is an upper bound on the cells that read it.
  Boundaries with no cell built between them print identical counts: on the
  `proc-v8` board the eight dated inside its cells all read 91 before and 6
  after for every engine, which is one split, not eight, and it coincides with
  when the cells were made (the six are the post-conference first forecasts),
  so it separates no change's effect from prediction timing;
- each pooled entry (over its forward cells), and each engine in `paired`,
  lists as `self_provisioning` its cells by whether their logs show a fetch of
  a court filing outside the provisioned document set, and each paired figure
  carries `common_record`, the paired events on which no engine's log shows
  one (*What may be claimed from `self_provisioned_fetches`* below). Neither is
  a rank key.

**Units.**

- **Composition.** A composition's `windows[].n` counts gradings, or reads, so
  a three-judge panel puts three into it per cell. That holds on an entry, on
  a paired engine and on a pooled `big_case`. An entry's `windows` sums across
  its strata, forward, retrospective and procedural together, so it can exceed
  any one stratum's `evaluations`. A claim-score entry counts its
  block-carrying gradings.
- **Cross-predictor figures.** A judge validation's or `evaluator_agreement`'s
  `windows` counts only the cells or reads that entered a pair or point.
- **Boundaries.** A boundary's `before`, `after` and `unstamped` count cells,
  one per (case, event) per engine.
- **Self-provisioning.** `self_provisioning` counts cells, one per (case,
  event, predictor); a `common_record` engine's `forward.evaluations` counts
  gradings, like the paired figure's.

**Judge-dependent figures list their rubrics, and the leaderboard's carry
per-rubric readings.** These figures list `rubrics`, the (evaluator, evaluate
digest) pairs they draw on, each with its `n`:

- a pooled `big_case`, over the reads its panel means use;
- `evaluator_agreement`, over every read behind an evaluator's leave-one-out
  points, its own and its peers';
- the claim scores' judge validation, over the grades that formed a pair;
- each ops score row's reasoning-quality quantiles, over the grades they are
  taken over;
- a semantic census, over its block-carrying gradings.

On the leaderboard the readings ride beside the pooled value:

- **`mean_reasoning_quality`**, a per-judge figure, is read per (evaluator,
  digest) in each stratum's `reasoning_quality_rubrics`: each rubric with its
  `n` in graded gradings, the evaluate label that blessed its digest as
  `labels`, and the mean over that rubric's grades alone. Judges grade on
  different scales, so the pooled cross-judge mean compares across predictors
  only while their per-rubric `n` match, as they do while every judge grades
  every cell.
- **`big_case` and `evaluator_agreement`**, panel figures, are read per rubric
  signature in `by_signature`. A point's pairs are the (evaluator, digest)
  pairs of every read behind it: for `big_case`, every panel read across the
  case's moments; for a leave-one-out point, the judge's reads and its peers'
  on the case. The signatures read are the maximal sets those pairs form,
  one digest per evaluator, each named by the evaluate labels that blessed its
  digests, and a point joins every signature holding all of its pairs. So a
  case only part of a panel read stays with the panel it was read under.
- **Overlapping readings are not independent.** A point read only under
  digests two signatures share sits in both readings, so two readings may
  share points: never difference them as independent figures, and do not
  expect their `cases` to sum to the pooled count. Check each pair's `n`
  before quoting a reading, since a single case read under a new digest can
  form a maximal signature whose distinguishing pair has `n` 1.
- **Set-aside points are not a random loss.** A point holding one evaluator
  under two digests joins no reading; it is counted in
  `mixed_signature_points` and stays in the pooled value. Such points
  concentrate in cases read at several moments, which are the granted ones,
  so after a digest move a reading covers a population short of exactly the
  higher-stakes cases. Read each reading's `cases` against the figure's own
  count.

The per-rubric reading is the claimable figure. Every judge's evaluate digest
moved at `proc-v9`, `claude-judge`'s with its model, and `codex-judge`'s and
`gemini-judge`'s moved again with their models at `proc-v10`, so a pooled
value spanning more than one digest of one evaluator mixes judge rubrics: it
is coverage, never a claimable figure or a comparison. A `rubrics` list
naming one evaluator twice is the sign. The claim judge-validation tau-b, the ops reasoning-quality
quantiles and the semantic per-grader agreement list their rubrics but carry
no per-rubric reading yet, so there a pooled value spanning two digests of an
evaluator has no claimable form. The signature rule is registered in
`docs/freeze-record.md` (2026-10-12).

**The other surfaces take the same shape.**

- **Claim scores.** `claim-scores.json`'s `entries` are each predictor's pooled
  record with its `windows`, counted in block-carrying gradings; `by_protocol`
  is the per-(predictor, window) cut, named by `process_window`.
- **Ops report.** Its `predictor_scores` rows pool the same way, listing each
  row's windows, and `predictor_scores_by_protocol` carries the cut. The
  rendered report draws the cut as its own *By protocol* table only where some
  predictor's record spans two windows, since otherwise every cut row repeats
  its pooled row.
- **Tool usage.** Its `segments` are pooled per engine, mode, stage and
  moment, each listing the (predictor, window) series behind its cells with
  their cell counts. `segments_by_protocol` is the per-window cut.

**Two windows of one predictor share no event** — a predictor holds one counted
forecast per event, the earliest window's — so a cut's rows cover disjoint
events, and a rise across a window boundary is not a measurement of
improvement.

A figure keyed on something other than the forecaster is the record across the
series it pools. These are:

- the claim scores' judge validation;
- the board's `evaluator_agreement`, which compares graders and pools the
  predictors' windows by design;
- the ops calibration block;
- a tool-usage coefficient row;
- a semantic census.

Each lists every (predictor, window) series it pools, with its `n`, as `windows`
beside the pooled value, a single series included, and is never a rank key.
Every artifact carries the whole registry in `frozen_process.windows`, each
window naming its predictor.

`release-sensitivity` and `semantic-summary` pool rather than refuse.

- **`release-sensitivity`** rebuilds the board with the stratify pass's
  windows. Each arm projects the pooled entries with their `windows`, the
  paired figure, and the cut as `by_protocol`, keyed `<predictor>@<window>`.
  Its release is `proc-v8` inside `proc-v8`'s window. Once a later window's
  cell is graded, a pooled entry is no longer the release figure. A per-entry
  release figure is then read off the cut's `proc-v8` entries. The paired
  figure (events, band filing, ranks) and each block's counters
  (`board_cells_removed`, `graded_members`, `lines_equal_headline`, the
  statpack builds, the transcription spread, each arm's `events_scored`) have
  no per-window cut, so they are read only from a run at the refresh commit
  the release pins.
- **`semantic-summary`** states the census's `windows` and `rubrics`, and
  prints the composition on its census line in the withheld state too.

**One prediction per predictor per event, and re-predicting a live event is a
registered rule.** A predictor may hold several committed runs on one event —
a re-queue after a failed cell, or a deliberate re-forecast — and the board
reads exactly one of them: the run the grading evaluation's harness-stamped
`prediction_run_id` names, falling back to the predictor's **newest** run where
that field is absent or the run it names is not on disk. So the staged and scored cell is the
newest one, and an earlier run is history that no figure counts twice. That is within one
counting window: where a predictor holds cells from several windows on an event, the
earliest window's cell counts, and a later window's is neither counted nor staged for
grading in its place.

That matters because a de-count — the cells of a label before `proc-v8`, or of a
revoked window — reaches cells on events that have **not yet resolved**. Those
events would otherwise be consumed for nothing: graded on resolution, then
dropped from this scope, leaving the frozen board with no population at all.
The predict backlog therefore **re-owes** a cell on a still-forward event at a
still-open moment whose whole committed cohort is de-counted
([docs/pipeline.md](../docs/pipeline.md)), so the cell that is eventually
graded was produced under a counted process. A supersession re-owes nothing: a
closed window's cells still count, so its events stay covered. Two readings this does
**not** license. It is not a re-grade: nothing about an existing evaluation
moves, and `superseded_gradings` is untouched. And a rise in any figure across
the re-predict boundary is **not** a measurement of model improvement — the two
sides are different processes on different information sets, which is the whole
reason the partition exists. Nor is the resulting board a sample of the docket
or even of its own conference: the first frozen cert population is **n = 110
cert/distribution events, all distributed for 2026-09-28** (70 baseline, 37
elevated, 1 high, 1 federal, 1 state), with 10 cert/cvsg (all high band) and 2
interim events beside it. It spans bands — the salience funding line does not
cut it, because the re-predict rule re-owes a wholly de-counted cohort on a
declined case too — but it is **110 of the 180 in-scope petitions** distributed
for that conference (557 distributed in all), being the previously-predicted
residue of earlier funded rounds, and so is selected **upward on band**: 63.6%
baseline against the in-scope conference's 76.7%. Read it on the **per-band
cut**, never as a pooled row, against the registered sal-v4 segment base rates.
Each is the risk-set band rate pooled over the statpack Terms strictly before
the scored prediction's **docket-number** Term (`context.term`), within
`salience.base_rate_lookback_terms`, the family the evaluator scores skill
against (`metrics/statpack.md`'s *Segment base rate by salience band*, not its
terminal composition table). The cohort is overwhelmingly OT2025 dockets,
anchored on the OT2017–OT2024 pool: 5.12% baseline / 17.22% elevated / 34.97%
high / 72.93% federal / 22.70% state. Its few OT2026 dockets pool
OT2017–OT2025: 5.02% / 16.89% / 35.51% / 70.79% / 23.63%, which move with each
pack build while OT2025 resolves.
`uv run fedcourts segment-anchors --term 2025 --term 2026` prints both off the
committed pack, with each band's `n` and pooled Terms. Those rates are the
skill anchor. Their complements are grant-family denial shares,
not the exact-match always-deny floor a lift is measured against: that floor is
realized on the scored cells themselves (`always_deny_accuracy`, below). Its
high band is **n = 1 on cert/distribution and n = 10 on
cert/cvsg**, which do not pool with each other, and none of it pools with any
`"all"`-scope board. That paragraph travels with the number rather than sitting
a section away, because it is the number's population.

And a third reading the boundary does not license: **a cohort complete on the
board is not the same as a cohort complete in fact.** The rule's moment gate
closes with the conference, so a cell that fails on the last tick before it
cannot be re-minted afterwards, leaving an event with some engines counted and
some de-counted — per-predictor cells over *different event sets*, which the
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
which the weekly metrics refresh regenerates beside the statpack, `big-cases.{json,md}`,
which the daily `big-cases` lane keeps current on its own cadence,
`updates/<YYYY-Www>.md`, to which the weekly `public-updates` lane adds each
missing week, and
`salience-replay.json`, produced on demand by the free, deterministic
`fedcourts salience-replay` (locally, or via the `run-backtest` dispatch's
`replay: salience-gate` mode, landing as a reviewed PR),
`merits-backtest.json`, which only a `run-backtest` dispatch in `replay: merits`
mode writes, as a reviewed PR, and
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

  **SCOTUS is also cut by docket class** (`docket_classes`): `cert` (the
  Term-prefixed petition form the cert stage predicts), `application` (an
  interim application in any spelling) and `other` (original, miscellaneous,
  pre-1925 or unparseable numbers), read off the docket number. The court row mixes them,
  and the mix is not stable: cert petitions are overwhelmingly denied while
  applications are mostly granted — an application's `granted` is the relief
  asked, not cert — so an application back-fill moves the court row's floor
  with nothing about any predictor changed. The `cert` row is the floor over
  every modern cert petition, IFP included; the floor over the salience-gated
  population the cert stage predicts is `cert-backtest.json`'s.

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
  board's own. The vote mean averages only cells whose outcome carries a
  complete vote record, each scored over that record's whole sitting bench
  (recomputed at build, not read off the evaluator), with `vote_cells_scored`
  beside it as its denominator; it covers the decisions a vote source read
  completely and its writer admitted — signed opinions whose lineup parsed and
  whose date, lead author and separate writers the Court's Granted & Noted list
  agrees with, on an outcome resolved the day the opinion is dated — which is
  expected to under-represent fractured lineups, not every merits decision. A
  consolidated case enters once for each of its dockets that carries a scored
  cell. The
  **accuracy** column is the mean of each cell's `correct`,
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
  against. That coherence check is what guards every **cert** cell the stamp
  does not own, because those are the only cells whose numbers are the
  evaluator's arithmetic at all: on a **merits** or **interim** cell
  whose `event.yaml` names its stage, `stamp-cell` writes all three together —
  `brier_score` recomputed from the scored prediction's probability and the
  committed outcome, `segment_base_rate` pooled from the statpack, and the
  ratio over them — so they agree by construction and there is no hand-computed
  number left to catch. Reproducing from the record is not the same as being
  right, which is why the numerator is stamped too rather than checked: a skill
  derived from an unverified Brier would satisfy the coherence check and still
  publish the wrong number. The cert numbers are the evaluator's only where a
  judgment remains. From `proc-v9` on, a cert grading whose scored prediction
  froze a band takes all three from `stamp-cell` too: the frozen band, its
  salience version and its docket Term leave no population to choose, so the
  anchor is the scorer's own risk-set pool (the figure `fedcourts
  segment-anchors` prints), read from the statpack build the grading names in
  `base_rate_statpack_digest`, under the window recorded in
  `base_rate_lookback_terms`. The board drops, whatever its build, a `proc-v9`
  cert cell recording a `risk_set` basis that names no build or window; it
  re-pools the anchor only where its own statpack is the same build, and drops
  a cell whose recorded rate does not reproduce;
  where the build differs (a refresh since the grading) the stamped rate
  stands. From `proc-v15` on the build is pinned at provisioning: a cert cell
  that froze a band also freezes its anchor in `context.cert_anchor` — the
  same pool over the statpack in force when the forecast was placed, with that
  build's digest and the window — and the stamp copies it, so a metrics
  refresh landing between forecast and grading does not move the anchor. The
  stamp copies it only once verified against harness-side inputs: it must
  name the newest revision of `metrics/statpack.json` committed at or before
  the predict cell's run id, record the lookback window `config/tracking.yaml`
  names at that commit, and re-pool to the frozen rate; otherwise the anchor
  and skill are cleared with a warning, and the stamp's summary counts the
  refusals. The board then holds such a grading to its pin
  whatever its own build: one that records the pinned build, window and rate
  is accepted, one that disagrees with its pin is dropped. A grading that
  pools the statpack checked out at grading — an earlier label's, or one whose
  cell was provisioned without `cert_anchor` — carries no pin, and the
  committed board is built straight after a statpack refresh, so for it the
  re-pool stands down for nearly every cell: it verifies an off-cycle build,
  and what holds the committed figure is the stamp itself. A re-grade keeps
  the anchor it was first stamped with. An
  earlier label's cert grading keeps the evaluator's transcription, held by
  the coherence check alone, and so does a cert cell on the terminal fallback
  (no frozen band) graded before `proc-v17`. From `proc-v17` the stamp writes
  the terminal fallback's record too, pooled over the terminal band in the
  evaluate cell's own provisioned record. That band is in no committed
  record, so the board does not re-pool it, and the coherence check is what
  holds it there as well.

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
  union, so equal cardinality is equal set — and an entry **below** it covers
  a subset. A pooled entry spans every window of its predictor, so one union
  denominates every entry. The rank does not rest on equal coverage: it is
  read over the paired events (`paired`, below), which are the same events
  for every ranked engine by construction, and each engine's `unpaired_events`
  is what that costs it. Never sum the **entries** to recover that union: two
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
  population, naming each short entry and its coverage — so the hazard does
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
  constants in force at build time — the blessed digest set, the freeze
  instant and the counting windows — so *what was blessed* is readable from the
  artifact rather than by resolving the build's commit back to
  `fedcourtsai.process_version`. The digest list pools predictors and
  evaluators and is not a filter; the enforced membership rule is `windows`,
  one per blessing of a predictor digest, which keeps a closed window's digest
  counting after it leaves the blessed set. The digest list also
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
  `base_rate_basis` is the evaluator's own field (except on a cert cell the
  stamp owns, from `proc-v9` on) and inclusion is therefore a convention
  rather than a construction — so the decomposition is a statement
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

  **A third skill figure is a post-hoc descriptive benchmark, not a member of
  the pair.** `population_in_sample_skill_score` scores each block against its
  own **sample climatology**: the constant `in_sample_grant_rate`, `c`, is the
  share of granted outcomes among the block's own scored events — the
  `in_sample_events_scored` distinct events of the gradings carrying a Brier
  score and cert outcome facts, each event counted once however many judges
  graded it — and every such grading's reference Brier is `(c − y)²`.
  Aggregated as the same ratio of sums, over `in_sample_skill_scored`
  gradings: on a cert block whose cells all carry facts that is
  `mean_brier_score`'s own population, wider than the realized-Term column's,
  because none of that column's qualifying rules (the `risk_set` basis, the
  Term's band under a matching version, the minimum resolved count) bear on a
  rate read off the scored outcomes themselves. `y` and `c` are on the Brier's
  own binary target, `actual_granted`, so a `granted-in-part` outcome counts as
  a grant here; elsewhere `c` is the grant-family share.

  What it measures follows from the Murphy decomposition of the Brier score,
  `BS = reliability − resolution + uncertainty`, where the uncertainty term is
  `c(1 − c)` — which, wherever every event carries the same number of
  gradings, is exactly the mean reference Brier above. There, and with
  forecasts grouped at their distinct values, the figure therefore **equals
  `(resolution − reliability) / uncertainty`** against the block's own base
  rate. (Grouped into a decile binning instead, as the cert back-test's
  calibration view uses, reliability and resolution pick up within-bin
  terms and the equality is not reproduced.) Where panel depth varies by event
  it holds only approximately: `c` counts events while the sum runs over
  gradings. Either way a forecaster reporting `c` itself scores exactly 0.

  It nets out **the block's level and nothing finer**, the scored case's own
  outcome included — so it is not a within-band discrimination measure
  wherever a block pools bands. The salience gate selects bands for their very
  different grant rates, and one `c` over a pooled block credits a predictor
  for separating the bands as well as for separating cases inside them. A
  forecaster that knew only each band's realized rate and told no two cases
  in a band apart would score well above 0 on a pooled block. The pooled
  `forward` figure therefore reads as discrimination within the block,
  *between-band separation included*, net of miscalibration against the
  block's own rate; the within-band reading is the `by_band` cell, each with
  its own `c`, and only where that cell is defined.

  No forecaster could have reported `c`: the rate exists only once every scored
  event has resolved, and it contains the case being scored. It is
  **hindsight by construction** and post-hoc rather than pre-registered — so it
  is never a rank key, never a headline, never pooled with or differenced from
  either other skill figure, and never read as in-season evidence.

  It differs from both members of the pair in its baseline, not its formula.
  The **prior-Term** figure scores against the strictly-prior pooled band rate:
  leakage-safe, knowable when the forecast ran, the primary outcome measure and
  the only one that may rank. The **realized-Term** figure scores against the
  band's rate over the case's whole Term — a far larger population than the
  scored events — leave-one-out, so the case never sits in its own baseline,
  and read at the committed pack's term-to-date vintage, so mid-Term it carries
  the grant-depletion bias above. The in-sample figure uses neither the band nor
  the Term: its rate is the block's own scored events, the case included, read
  off the committed outcomes with no vintage and no minimum. So a `by_band`
  cell gets its own `c` over that band's scored events, and a block whose
  events are all denied (or all granted) has `c` of 0 (or 1), every reference
  Brier 0 and the ratio undefined: the skill is null with
  `in_sample_skill_scored` 0 while `in_sample_grant_rate` still reads the
  level. On a cohort with a handful of grants a degenerate rate is most bands,
  and where the rate is not degenerate the denominator is dominated by the
  grant events — each contributes `(1 − c)²` against a denial's `c²`, so the
  grants carry a share `1 − c` of it. Its scale is set almost entirely by those
  few grants: every unit of Brier, on a grant or on a denial, is measured
  against about that many grants' worth of uncertainty, and the figure moves
  by large steps when one more resolves. So each figure is quoted with its
  grant count — `k` grants of `in_sample_events_scored` events, `c` counting
  GVRs, summary reversals and partial grants as grants — and two predictors'
  figures sit side by side only where their `in_sample_events_scored` agree,
  since a different `c` is a different baseline.

  The skill is also null, with the rate still published, wherever any of the
  block's gradings carries a stamped Brier that no longer reproduces from its
  scored prediction against the committed outcome — a Brier taken against an
  outcome since superseded, the same unpaired shape that leaves the realized
  floor null.

  Every **cert** stratum block also carries the **realized always-deny floor**
  on its own cells. `always_deny_accuracy` scores a constant `denied` call over
  exactly the gradings `accuracy` averages — the `accuracy_scored` cells, one
  per judge, under the same exact-match rule `correct` uses — so a GVR, a
  partial grant or a summary reversal is a miss for it, just as it is for a
  `granted` call. `accuracy_lift` is `accuracy - always_deny_accuracy`, a
  paired difference over the identical cells. Both are averaged over
  **gradings**, so they are weighted by panel depth, and depth varies by
  design; the **per-petition** reading counts each event once:
  `event_accuracy`, `event_always_deny_accuracy` and `event_accuracy_lift` over
  `accuracy_events_scored` events, and that is the published per-band reading.
  The `event_*` fields are null where a block's gradings of one event
  disagree on `correct`.

  The grant counts are **grant-family** counts — granted, GVR and summary
  reversal, the family the band rates count, so `granted-in-part` is out.
  `grants_expected` sums, once per event, the registered strictly-prior segment
  base rate the prior-Term skill column scores that event against, over
  `grants_expected_scored` events; `grants_realized_expected_scored` counts the
  grant-family events among exactly those events, and those two are the pair
  to compare. `grants_realized` is the unrestricted audit count over every
  accuracy-scored event and is not compared with `grants_expected`. While
  relisted or held petitions are still pending, realized runs below expected:
  those petitions grant more often and have not resolved yet.

  None of this is the registered historical figure per band. The registered
  band rates of the cell's frozen salience version are the **skill anchor**:
  each band's risk-set rate pooled
  over the statpack Terms strictly before the cell's docket-number Term, within
  `salience.base_rate_lookback_terms`, so
  the figure depends on the docket Term. For the `sal-v4` cells the board holds
  before the `sal-v6` activation, on the committed pack that is 5.21%
  baseline / 17.40% elevated / 35.44% high / 75.82% federal / 22.82% state for
  an OT2025 docket and 5.09% / 17.00% / 35.69% / 73.30% / 23.52% for an OT2026
  one (`uv run fedcourts segment-anchors --term 2025 --term 2026
  --salience-version sal-v4`; the bare command pools the active `sal-v6`). A band row
  that mixes docket Terms states its count per docket Term beside the anchors.
  Their complements are grant-family denial shares, not exact-match floors, so
  they are not comparable with `always_deny_accuracy`, and no lift is measured
  against them.

  Eight of these fields are cert-only, null off the cert stage (where
  `denied` is not the null call): the two floors (`always_deny_accuracy`,
  `event_always_deny_accuracy`), the two lifts (`accuracy_lift`,
  `event_accuracy_lift`) and the four grant counts. All eight are also null on
  a block where any accuracy-scored cell lacks band/outcome facts (a cert cell
  with no readable scored prediction). The two floors and two lifts are
  further null where any accuracy-scored cell's stamped `correct` no longer
  reproduces against the committed outcome: that grading was paired with an
  outcome since corrected, and a floor read off the current outcome beside it
  would be unpaired. `accuracy_events_scored` and `event_accuracy` need no
  facts and are filled on every stage. None of these fields is a rank key.

  Each cert entry's forward stratum is also cut **by salience band**: `by_band`
  maps `<salience_version>/<band>` to an ordinary stratum block over the same
  cells as `forward` — after the run collapse and both exclusions, with the
  same skill terms. The key is the band the **scored prediction froze** in its
  `context`, never the corpus's current band, which only strengthens as a
  petition is relisted or a CVSG lands and so would sort a forecast by its own
  future. The single `(none)` key holds every cell that froze no band, froze a
  band with no version, or carries no band facts at all, so the blocks'
  `evaluations` sum to the forward stratum's. The cut appears on the ranked
  entries and on the later cert moments' stage entries (`cert@cvsg`), never on
  another stage, and is omitted while no forward cert cell carries band facts.
  Beside it, the board and every stage block carry `paired`, the paired-event
  figure: the events on which every engine in its set holds a counted forward
  cell graded with both an accuracy and a Brier score, from any window. Pairing
  ignores the band — no rank key uses a band anchor — so on the cert board and
  the `cert@cvsg` block each paired event is filed under the band of its
  earliest qualifying cell by harness clock (`paired.by_band`), and
  `band_mismatches` counts the paired events whose engines' cells froze
  different band keys; those cluster where a band rose between the engines'
  runs, so they lean to the higher-grant events. A paired event none of whose
  cells carries band facts files under `(none)`, so the filing sums to
  `paired.events`. Each engine in `paired` carries `by_band`: its paired
  gradings aggregated under that one filing, so every engine's figure in a band
  is over the same events by construction. **A per-band ordering is read off
  `paired.entries[].by_band` only** — never off an entry's own `by_band`, which
  files each cell under the band it froze and spans that engine's events
  alone. None of the band filing ranks anything: this is where the per-band
  reading the frozen cohort requires is copied from. On the `proc-v8` board
  the reading the long-conference release made still holds: no band mismatch
  and no unpaired event, so each engine's own per-band figures and its paired
  ones are the same numbers.

  The same forward stratum is also cut **by link**: `by_link` files each cell
  under `linked` where the scored prediction's frozen `context.vide_links`
  names at least one docket the Court links as `Vide` (a cross-petition, a
  companion, or the petition the docket is held for), `unlinked` where it
  names none, and `(none)` where the prediction froze no list. It is built
  exactly as `by_band` is, over the same cells and skill terms, so the blocks'
  `evaluations` sum to the forward stratum's, and it appears on each entry,
  each `by_protocol` entry and each cert stage entry — never in `paired`. The key is the link list the cell's payload carried, never the
  corpus's current one, so a link the Court added after the forecast does not
  move it. A forecast on a linked docket may be derivative of the other
  docket's course, which is why it is shown apart. But the cut is
  **descriptive**. `linked` is a different population: a held petition's
  grant-side mass is mostly a hold-then-GVR route, and the band anchor its
  skill terms are scored against was pooled over the band as a whole, not for
  linked dockets. The cut also pools across bands. So `linked` against
  `unlinked` is not a like-for-like comparison of forecast quality. The
  `linked` block is small (about one open queued docket in twenty links
  another), and no figure on it is read without its `evaluations`. Each block
  spans one engine's own events, with no pairing, so no ordering of engines
  within a key is read off it. It is never a rank key, and `release-sensitivity`
  does not project it. Predictions made before the context carried the list file under
  `(none)`.

  Each engine in `paired` carries its aggregate over its qualifying gradings on
  the paired events, the windows those gradings come from with their `n` in
  gradings, and its `unpaired_events`. An event whose cells come from a closed window and the
  successor that closed it pairs like any other. The selection disclosures a
  successor's freeze-record entry makes — the split-event count and each
  engine's counted events holding a failed or missing earlier-window attempt —
  are over every counted cell, graded or not, and come from `fedcourts
  successor-disclosures`, not from this figure.

  The ranked board is the **cert stage's first declared moment** (see the stage
  axis note below); every other population — a later cert moment included —
  reports in its own unranked `stages` block. Each entry
  also carries a `big_case` block — the predictor's `big_case_score`
  rank-agreement (Kendall's tau-b) with the evaluator panel's own reads —
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
  events moves a long way on one disagreement. `events` counts **cases**, one
  leave-one-out point per case, despite its name.

  **The panel is only as wide as the reads on each case.** On a case exactly two
  evaluators read, each one's peer mean is the other's read, so the two
  leave-one-out points on it are one comparison counted under both judges. A
  judge that records few `big_case` reads leaves most of the other two judges'
  cases in that shape, and their two figures then approach one two-judge
  statistic printed twice rather than two independent checks. Compare the
  evaluators' `events` before quoting their figures side by side, and quote
  the panel's width with any figure taken from this map.

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

  The panel's reads are **not blind to the scores they are compared against**.
  The score is a field of the `prediction.json` the judge must read to grade,
  and the blinded view does not mask it (`fedcourtsai.blinding.mask_prediction`).
  The prompt tells a judge the scores are in front of it and asks it to form its
  read from the case itself without anchoring on them; nothing enforces that. A
  judge records one stakes read per candidate, beside that candidate's own score
  and rationale, and a predictor's panel is built only from the reads recorded
  beside its predictions. Anchoring therefore pulls each predictor's panel toward
  that predictor's own number. It inflates every predictor's tau, but not by the
  same amount — most for whichever predictor's score and rationale judges defer
  to — so the comparison *between* predictors is affected as well as the level.
  Read a `big_case` tau as an **upper bound** on how far a predictor's stakes read
  tracks an independent panel, never as evidence that it does. The bound
  assumes residual anchoring pulls a read *toward* the score. The prompt tells a
  judge that a read echoing a predictor's score carries no information, and a
  judge that over-corrects away from the score pushes agreement down instead;
  nothing in the record separates the two, so the bound is a reading rule, not
  a measured property.

  How strongly judges anchor depends on the evaluate prompt, so a tau is
  comparable only within one evaluator digest. The board does not split on it:
  its scope is `graded_in_window`, which records the evaluator digest but does
  not count by it, so a tau whose reads straddle a change to the evaluate prompt
  mixes two anchoring regimes and compares to neither. `evaluator_agreement` is
  exposed the same way: judges anchored on the same candidate's score agree with
  each other partly for that reason, so a high figure there is an upper bound
  too.

  `fedcourts leaderboard` produces the board — a deterministic, offline roll-up of the
  ledger and the committed `statpack.json` — empty (`{}` plus the zero counts)
  until the first evaluation lands.
- `claim-scores.json` — the mechanical claim-score surface: every
  harness-computed `claim_scores` block in the evaluations ledger (minus any
  forward-claim breaching cell and any leakage-suspected one — both exclusions
  apply to every scored surface), rolled up per predictor **per stratum** and
  published beside the leaderboard.
  `fedcourts claim-scores` produces it, deterministic and offline, defaulting
  to the same frozen process scope as the board. Its population is the cert
  stage's first moment only (below). Membership is by stage and moment, never
  by set version: those cells carry the cert stage's declarations (the
  `cert-v*` sets, listed per stratum in `declared_set_versions`), and a later
  cert moment's or another stage's block sits outside the surface whatever it
  declares. Where no committed
  `claim_scores` block reaches that scope *and* that population, it renders
  its honest suppressed state: zero counts, every
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
  other two stages declare their own sets (`interim-v3` on every interim
  moment, `merits-v2` on every merits moment), a non-cert cell's block sits
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
  there demotes them to coverage figures. That holds for an authorship
  version beside its predecessor too (`cert-v3` beside `cert-v2`): the binary
  claims are the same, but the two declarations were asked under different
  prompts. The authorship rows (`ClaimScoreBlock.distributions`) are not on
  this surface; they ride the block and enter no total. Retrospective aggregates are
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
  is counted separately. That is almost always the availability mask at work
  — a property of the record, never of the predictor — but one mask reads when
  the cell ran rather than what it froze: the increment claims' run-timing
  mask (`ClaimScore.mask_reason: signal-before-run`), which follows when the
  cell ran (its poll, else its harness clock) and so is a property of the run,
  still never of the predictor's number.

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

**`not-ingested` on a newly decided case is bounded by a grading-timing rule.**
The evaluate lane holds a decided merits event for up to 14 days after its
outcome resolves while the case's corpus row carries no opinion body, and grades
it the moment one lands ([pipeline.md](../docs/pipeline.md#the-evaluate-queue-is-level-triggered-too));
a DIG, an equally divided affirmance, and a row enrichment cannot walk are never
held, since no body will come. For a merits grading made after the promotion
that carried the hold, `not-ingested` ordinarily reads *the body did not reach
the corpus within two weeks of the decision*; a round that could not read the
presence bit grades unheld, and the artifact does not record which applied. The
bucket also holds events that were never held (body-less judgments and rows
enrichment cannot walk), and the artifact does not record which reading applies
to a given grading. The
ground itself remains the grader's word, not a harness fact. The hold begins at
that promotion's merge, which the freeze-record entry dated 2026-10-16 records.
The ledger held no merits grading at all when that entry was written (0), so
every merits grading it gains after the merge sits on the hold's side. The hold moves only when a decided event is
first graded, never what it is graded against.

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

**The voided-event exclusion.** An event whose committed outcome records a
different petition than the one it was opened on — the Court re-docketed its
number, or the ingest attached another docket's disposition — is **voided**:
registered in `src/fedcourtsai/voided_events.json`, a code-owned file a void
reaches only through a maintainer-merged PR, beside the dated freeze-record
entry that states its defect. The admissibility rule is
[docs/process-version.md](../docs/process-version.md)'s *Voiding an event*: the
outcome-describes-another-case ground alone, shown from stored docket payloads
without reference to the outcome or any grading, with the voided gradings'
scores published and every already-graded event the docket-identity detector
flags voided whatever it scored. Its gradings leave **every rank key, scored
aggregate, stratum, window composition and export count**: `store.stratify`
drops them after the run collapse (so a re-grade of one still counts in
`superseded_gradings`) and before anything else counts them, so they are in
neither the `forward_claim` nor the `leakage_exclusion` denominator; unlike those
two rules, the `big_case` and `evaluator_agreement` views drop them too, because
a stakes read of a voided event was taken across two petitions filed under one
id. It changes membership, never value: no committed file is edited. Each board
and the ops report carry a `voided_events` block — the shared pass's dropped
count, the events, and per predictor the count, the hits (`correct: 1`) and the
mean Brier score of what was dropped — omitted where nothing in scope is voided,
and the export marks each such grading `excluded_reason: voided` and its
prediction `voided` with the outcome columns null. The docket-identity
detector (`pipeline.redocket`) refuses at attribution: outcome detection never
writes an outcome to a moment opened under another petition than its row now
names, so such a moment is never graded and needs no void. It leaves every
scored figure without appearing in any `voided_events` block, and surfaces
instead on the unrecorded queue and, once the corpus closes it, as a
`redocketed` no-outcome residue. Only an event graded before the detector, and
flagged by it, needs a void. The scan of the committed ledger and of every
predicted case's stored snapshots, at the vintage the freeze-record entry of
2026-10-17 states, flagged only the event already voided. A void is not a corrected outcome:
`stamp-cell --regrade` re-scores an event against its true outcome, and a voided
event has none at that docket number.

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

**The set-aside, and its sensitivity reading.** A cell every rule above kept,
but whose record **cannot show it was made before its outcome was public**, is
set aside from the default figures (`fedcourtsai.set_aside`, applied by the same
`store.stratify` pass). Unlike the three exclusions it is not "an observation of
nothing" — the cell may be a genuine forecast — so it is **put back in a
sensitivity figure published beside each default it moved**: the board's
`set_aside` block counts the set-aside gradings by reason, by predictor and by
event, over that board's own population (on `claim-scores.json`, cert's first
moment only), and `set_aside_sensitivity` carries, for each (population,
predictor, stratum) a set-aside moved, the **pooled entry's** figure
recomputed by the same code with the set-aside gradings counted — on the
leaderboard the pooled entry's stratum (and, where a ranked-board cell was set
aside, the paired figure the ranks are read off), on `claim-scores.json` the
cert-stage claim stratum. The `by_protocol`, `by_band` and `by_link` cuts are
default-only, and so are `claim-scores.json`'s judge-agreement pairs
(`forward_agreement`): none carries a sensitivity line, so a per-window,
per-band, per-link or judge-agreement figure is read without the set-aside cells. The default is
the headline; a sensitivity line is a disclosure, never a rank key, and never
stacked with another departure. Each reason is a dated freeze-record entry.
Three cell-grain reasons exist, and one claim-grain reason (below):

- **`interim-decision-day`** — a forward interim cell whose harness clock,
  dated in Court time (America/New_York, the clock `resolved_at` is dated in),
  falls on or after its outcome's `resolved_at`, unless the harness's
  `usage.json` `pre_mint_poll.state` reads `open`. An application can be
  decided within hours and `resolved_at` has no time of day, so only the
  pre-mint poll can show such a cell began first; a cell with no poll, or one
  reading `unavailable`, is set aside. Computed from the committed ledger
  alone. A line counting these cells back is retrospective, unclaimable
  iteration signal, read beside its always-deny floor like any other. Because
  a same-day tie already reads retrospective on the harness
  clock's UTC day and a later day already breaches the forward claim, these
  cells reach no forward figure under either rule; what the set-aside moves is
  the retrospective stratum of the interim stage blocks, where a cell that
  claimed forward and retrieved unrestricted on a decision day would otherwise
  sit as iteration signal. An open poll does not move a same-day cell into the
  forward stratum: the stratum boundary is unchanged.
- **`post-conference-first-forecast`** — every cell on a cert distribution
  event whose first forward frozen-scope cell (by harness `run_id`) ran on or
  after the day the conference that **actually considered** the petition sat
  (`cert_signals.considering_conference` reads `sat`: a reschedule or a call
  for response entered before the conference removes it, and a relist moves
  it to the next conference only where the relist was docketed by the first
  cell's run day — `cert_signals.relisted_past`, a date-dependent carve-out the
  census counts). The reading needs the petition's docket entries, which live in
  the corpus, so these events are **listed** in
  `src/fedcourtsai/set_aside_events.json` from a corpus census
  (`scripts/checks/post_conference_census.py`, which also reports any census
  event the list lacks), keeping the boards offline and deterministic. An
  undisposed petition after its grant list is almost always denied on the next
  order list, so these cells sit in the forward stratum forecasting an answer
  the grant list has largely implied, and their removal is plausibly outcome-correlated — which is why the
  reading with them counted is published beside the default rather than
  withheld. The fan-out does not mint such a cell
  (`store.distribution_conference_considered`). The list is complete only as
  of its last census: a row the census later finds owed is appended with its
  own dated freeze-record entry, and the list is closed once the census reports
  no owed row with the guard live.
- **`pre-distribution-mint`** — every cell on a cert distribution event whose
  forward frozen-scope distribution-moment cells were minted when the docket
  carried a distribution by their run day but none of the petition itself,
  only an ancillary paper's (a motion for leave under a linked M-number, a
  sealing motion), so `store.petition_distributed` read false of the
  petition: the cells forecast from a moment the petition had not reached.
  The reading needs the docket entries, so these events are **listed** in the
  same file, each row naming the run minted before the petition's
  distribution. The fan-out mints no such cell; it waits for the petition's
  own distribution (`store.petition_distributed`). A row sets aside every
  cell on its event, and no later cell is minted on it for a predictor that
  already holds a counted one.

**`increment-run-day`**, the claim grain. One claim inside a cell is set aside
and the cell stays counted: a resolved `cvsg-increment`,
`response-requested-increment` or `referral-increment` claim on a forward cell
whose run the record cannot order against the signal
(`set_aside.claim_set_aside_reason`) — either the pre-mint poll read the signal
absent and the post-run poll read it present, so it landed while the cell ran,
or, with no usable pre-mint poll, the signal's committed docket date is the
cell's run day in Court time. Either way the claim may be a forecast or an
observation. One the pre-mint poll read present, or, unpolled, dated before
the run, is not set aside but masked by the scorer (`ClaimScore.mask_reason`,
docs/outcome-decomposition.md); one the pre-mint poll read absent and the
post-run poll did not read present stays a forecast. The mask applies at stamp
time: a block stamped without it keeps its resolution, neither masked nor set
aside, until `stamp-cell --regrade` re-stamps it. On
`claim-scores.json` the set-aside claims' scores leave every default figure —
block totals, per-claim means and the judge validation's pairs — and the board
publishes `claim_set_aside`, counted in **claim units** (a prediction's claim
once, with the gradings carrying it and how many of the claims carry a score
beside it), and `claim_set_aside_sensitivity`, one line per (reason, predictor,
stratum) recomputed with **that reason's** claims counted back and nothing
else. The board's population is cert's first moment, where only
`cvsg-increment` can be reached, and while that claim has no baseline its
set-aside moves no figure; the two interim claims sit on no claim surface yet,
so their set-aside is recorded in the pass (`StratifiedRun.claim_set_aside`)
and moves nothing published. Each sensitivity line also counts the
`scored_claims` it puts back: zero means its figure equals the default — the
claims are set aside, and none of them moved anything. No committed artifact
dates a referral, so the rule cannot reach a `referral-increment` claim on any
cell without a usable pre-mint poll reading of the referral: a poll carrying no
`signals`, one that recorded no reading of the referral (an `unavailable`
poll, a docket with no proceedings, a failed signal reading), or no
`usage.json` at all. Such claims must not enter any scored figure without a
corpus-dated reading (`interim_signals.referral_date`). `relist-increment` and
`amicus-increment` are outside the rule: the post-conference set-aside above
brackets a relist, and the amicus count has no single signal date (the
2026-10-16 freeze-record entry states both, and their residuals).

`set_aside.excluded` is counted after the three exclusions, so a grading those
rules dropped is never counted here. On the leaderboard it is stage-blind and
never netted against a stage-scoped total; on `claim-scores.json` it covers
cert's first moment only, the board's own population. The published Release 1 artifacts are built without the
set-aside (`release-sensitivity`, the cohort cut and the dataset export pass
`apply_set_aside=False`), so re-running them reproduces what was published;
the release's own post-conference sensitivity line is that population read the
other way round.

**The procedural stratum.** A cell whose outcome was mootness practice — a
Munsingwear vacatur ("granted", but the wording tracks the Court's vacatur
practice) or a dismissal as moot — segments into a third, `procedural` stratum
regardless of timing (the outcome's `disposition_basis` marks it at
resolution). Its aggregates are reported per predictor but never enter the
ranking: scoring them as merits calls would conflate cert-worthiness
calibration with vacatur-practice prediction. An interim cell whose scored
prediction takes the finer interim reading (`proc-v17` on) is not scored at
all when its application was dismissed or denied as moot: its Brier,
`correct` and skill are null, so it lands in this stratum with no score.

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
(`pipeline.base_rates.interim_base_rate`) — over the finer counts
(`finer_granted` / `finer_resolved`) for a cell whose scored prediction takes
the finer interim reading, each cell's baseline paired with the binary its
Brier was taken against, and a pooled figure spanning the change naming both
windows in its composition; from the OT2027 application Term, the three Terms
before the cell's own over the widened ask vocabulary
(`base_rates.INTERIM_LOOKBACK_TERMS`, `docs/salience.md`) — subject to its own per-pool floor and
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
a merits proceeding while the forecast side further excludes
consolidated-out-of-scope and date-inconsistent rows, a small residue now
that the guard removes the (mostly IFP) stale-labeled vacaturs. IFP grants are
on both sides: the Tier-0 IFP rule stops at the grant. The two
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
the two residues above. A termination of either kind leaves the residue once a
judgment parses on its docket: the write of a parsed judgment (the backfill's,
or the live poll's) clears the termination in the same write, one-way, and the
row then meets the pool's admission like any other parse, gap guard included.
Neither is folded into the judgment vocabulary,
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
publishes. The post-hoc in-sample benchmark is null there too, with
`in_sample_grant_rate` null and both its counts zero: only a cert cell carries
the outcome facts it reads.

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

- `merits-backtest.json` — the merits back-test (`fedcourts merits-backtest`,
  not regenerated by the weekly metrics refresh): predictors replayed over
  decided argued cases at the merits grant and briefed moments, scored on
  P(disturbed). **Retrospective, never claimable**: every judgment was public
  before the run, so a cell can recall it. Its Brier skill is measured against
  an as-of base rate (lead dockets argued in the cell's Term or the three before
  and decided before its cutoff), not the forward `merits_base_rate`, so no
  figure here is set beside a forward merits figure. Read each moment with its
  `events_scored` and per-Term counts, and read what the briefed moment adds
  (the briefs and the months of docket beside them) only from an entry's
  `paired` block: the fences drop cells per moment, so the two moments' full
  sets are different cases. Pairing fixes the case mix, not the selection:
  `fenced`, `lost_cells` and each Term's `excluded_disturbed` say what was not
  scored, and whether a case is fenced or set aside can track its outcome, so
  every set here, the paired one and the baseline pool included, is a selected
  one. Read `brier_skill` against `baselined_brier_score`, not
  `mean_brier_score`, and `accuracy` against `majority_accuracy`. Its
  `exposure_candidates` count reads the cert back-test's disclosure bit, so
  it compares only across runs read under one rule, as that bit's own
  reading rule below says.

- `cert-backtest.json` — the cert-specific back-test (not regenerated by the
  weekly metrics refresh): predictors
  replayed over decided modern discretionary-cert petitions,
  outcome hidden behind a redacted snapshot, scored on accuracy, Brier, **lift
  over the always-deny floor** (the honest signal under cert's denial skew), and
  a P(granted) calibration view. **The headline is the granted-or-not axis**:
  `granted_accuracy`, its floor `always_not_granted_accuracy` (the set's
  not-granted share, which is what always-deny scores there) and
  `granted_lift_over_always_denied`, which the board ranks by, the review PR
  headlines and the weekly digest's floor leads with. A GVR is granted on that
  axis and a party dismissal or withdrawal is not, so a Rule 46 dismissal a
  forecaster called denied is a correct call, as it is for always-deny. That is
  the target a cert forecast is asked to call and the Brier score scores; no
  forecaster is asked to call a dismissal, and the draw does not exclude one,
  since dropping petitions by outcome would choose the sample by its labels.
  The exact-disposition `accuracy`, `always_denied_accuracy` and
  `lift_over_always_denied` stay in the report as a secondary reading, on which
  a dismissal is a miss for every forecaster, the floor included. A report
  without `always_not_granted_accuracy` is ranked by the disposition lift, and
  its surfaces say so ("on exact disposition"). The report names the scorer whose bands
  segment it (`salience_version`): a band label means something only under the
  function that assigned it, so a per-band figure is not comparable with one
  produced under another version. Each entry also carries a **per-salience-band
  skill breakdown** over the paid scored segment — the mean leakage-safe segment
  base rate (each petition's own prior-Term band grant rate) and the Brier
  skill against it — so the back-test measures the same segment-baseline skill the
  forward stratum does, not just raw Brier. The skill is given two ways, over
  the same petitions, and **`pooled_brier_skill` is the one to read**: the
  ratio of sums, one minus the band's summed Brier over the summed Brier of
  forecasting each petition's base rate, which scores the band as one
  forecaster — the estimator the forward stratum's population skill uses (*Both
  columns aggregate as a ratio of sums*, above), so it is the band figure
  comparable with it. `mean_brier_skill` is the mean of the per-petition
  ratios, the estimator that section rejects: a denied petition in a low-rate
  band has a reference Brier near zero (at a 1% rate, 0.0001), so a forecast a
  few points off it scores a ratio in the tens of negative units and one such
  petition can pull the mean below zero while the pooled skill is positive. It
  stays in the report only so the band reading is continuous with reports
  written before the pooled figure, which carry it alone and cannot be
  re-pooled (the report keeps no per-petition band data): **the pooled band
  series starts with the first report that carries it**, and a pooled value
  is never read against an older report's mean. At the pinned draw a band
  holds a handful of petitions at most, so neither figure is more than a
  count of how its few
  forecasts sat against their base rates. The pooled figure is comparable
  with the forward stratum's while
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
  top lines are not comparable. **How the set was drawn** is `provenance.draw`.
  Without `--spread` it is `recency-head`, the most recently decided `limit`
  petitions — a small limit lands on the last order lists, whose grant and
  dismissal share is far above the population's, so its floor is not the
  population's floor. `--spread` is `vintage-keyed-hash-v1`: every petition in
  the population is ranked by `sha256("<salt>|<key>|<case_id>")`, the salt fixed
  in code and recorded beside the key, the key being the blob's newest
  `last_pulled` stamp, and the set is the top `limit` of that order. Nothing
  about an outcome, a decision date or a conference feeds the rank, so the set
  is a simple random sample of the **eligible** population — on an engine
  replay, the replayable one, whose limits come next: its expected denial
  share is the eligible population's, each of that population's conferences
  and Terms holds a share in proportion to its size, and a never-distributed
  petition (no `distributed_for_conference`) enters at its own small share,
  with no slot set aside for it. The walk order is recomputable from the
  block's salt and key; the set also needs the blob and, on a replay, the
  content store's snapshot coverage at run time, so the same blob and
  dispatch draw the same set while that coverage holds still. A newer blob
  re-keys the draw, so consecutive fortnights are fresh samples rather than one
  set replayed. On an engine replay the walk passes over every petition it
  cannot replay (`draw.passed_over` counts them) and keeps going, so the set is
  a random sample of the **replayable** population, not of the whole one. The
  two differ, and not at random: snapshot coverage is not outcome-neutral
  (likely because a granted docket keeps moving and keeps being fetched), and
  it reaches back only a few Terms, so the replayable
  population's denial share can sit well below the whole population's — read
  a replayed set's floor against the replayable population's, not the
  statpack's. At ten petitions the floor is
  still noisy around that expectation (a binomial standard deviation of
  about 15 points at a floor near 70%), so one fortnight's floor says little alone. A report whose `draw`
  is null names no rule, so how its set was drawn cannot be read off it. Two
  config values ride the block for the same
  reason, because they move the population and the baselines under an *identical*
  dispatch: `salience_floor` (what `--scope selected` means) and
  `base_rate_lookback_terms` (what every `segment_base_rate`, and so every
  band's `pooled_brier_skill` and `mean_brier_skill`, is scored against — it sits in no process digest, so
  without it here a per-band comparison across two reports is not one).
  `dropped_predictors` names the predictors lost at run time (no registered
  runner, a missing CLI binary, or every one of its cells lost — the ids
  carry no cause, which the run log states) as against the deliberate
  `skip_engines` opt-out, since a board silently short one engine is not the
  three-engine comparison it looks like. `lost_cells` is the per-cell
  counterpart: a (petition, predictor) cell that produced no score, with its
  reason — `missing`, `invalid`, `wrote-outside-work-root` (the cell ran and
  what came back was absent, malformed, or written outside the work root),
  `engine-failed` (the engine failed for that cell — a non-zero exit, or a
  zero-exit turn whose result reported a fault — and wrote nothing to read),
  `quota-exhausted` (the engine's own quota was spent, so that cell failed and
  the engine's remaining cells were recorded lost without being attempted,
  every further invocation being a paid-for certainty of the same failure — so
  exactly one of an engine's `quota-exhausted` cells was a model call and the
  rest were not, which is why the count is a coverage figure and not an attempt
  count), or `harness-error` (the harness itself raised something no engine
  fault explains while running or reading that cell or an earlier one of its
  engine, so that engine's lane stopped and its remaining cells were recorded
  lost without being attempted, while the other engines ran on — the same
  coverage-not-attempts reading). Read the whole-predictor drops apart here: a
  predictor dropped because its engine's quota ran out, or because its lane
  stopped on a harness fault, carries a `lost_cells` entry for every petition
  (the tail under that reason), while one dropped for a missing CLI binary carries
  entries only for the cells it had already lost — its remaining ones were
  never attempted and
  are not counted as losses, so a shortfall with no entries behind it is that
  case. It is a reading
  rule, not bookkeeping — a predictor short *some* cells is scored, and its
  lift floored, over the petitions that came back, so its `events_scored` is
  below the set and its top line is not measured over the same sample as an
  entry that lost none; one short every cell has no entry at all and is in
  `dropped_predictors` instead. **A `quota-exhausted` or `harness-error`
  truncation is not a scattered subsample**: each engine walks the petitions in
  the dispatched order, and once its allowance trips or its lane stops every
  later cell of that engine is lost, so
  what survives is the *prefix* of that order — under `--spread` a prefix of
  the hash order, itself a random subsample of the draw whose composition
  differs from the full set by sampling noise alone (large at these sizes),
  otherwise the most recent decisions — a differently composed slice, not
  merely a smaller one: its denial share (so its floor), its band mix (so its
  `segment_base_rate` and per-band skill) and the `provisioning` mix that
  applies to it all follow from the prefix rather than from the dispatched
  population. Losses to `engine-failed`, `missing`, `invalid` or
  `wrote-outside-work-root` (and the single cell that raised a
  `harness-error`) are scattered rather than prefix-shaped and may track a
  petition's difficulty; either way the short entry is scored over a smaller
  set against its own floor. `lost_cells` names the
  case ids, so reconstruct the surviving set before reading such an entry's
  numbers, and do not compare it with a full entry even as a listing.
  The board keeps a short entry below every full one whatever its lift —
  dropping a petition a predictor would have got wrong raises the figure — so
  `rank` orders comparably only within one `events_scored`, and the rows below
  the full ones are a listing rather than a ranking. **No leakage exclusion
  applies to this board.** The back-test runs no evaluator, so the leakage
  bit that takes a graded ledger cell out of every scored figure (*The
  leakage exclusion*, above) is never set here, and the only exposure
  evidence a replay has is what each cell said about itself in `flags.json`.
  That is recorded, not acted on: `provenance.disclosures` lists every
  replayed cell that left one in the work root — scored or lost, since a lost
  cell's note can explain its loss — with each note's category, severity and
  an `outcome_exposure_candidate` bit, and `provenance.disclosure_tally`
  counts, per predictor on the board and over its scored cells, how many were
  read, flagged, unreadable, and candidates. The bit is a triage highlighter,
  not a judgment: a note filed under `leakage-disclosure` is a candidate
  whatever its wording, and a note under any other category is a candidate
  when some clause of it — split at sentence and clause punctuation (commas
  included) and before *but*, *although*, *though*, *however*, *yet* and *whereas* — carries an
  exposure cue (leak, contaminat…, outcome-revealing, surfaced, encountered,
  saw, seen, reveal, exposed or exposure, snippet, unsuitable, show or
  showed, found, included), an outcome term (outcome, disposition, granted,
  denied, granting, denying, GVR, order list, grant language, grant order,
  "cert was") and no negator (no, not, none, nothing, never, neither, nor,
  without, cannot, *-n't*). It over-calls on a retrieved prior's disposition
  and on a `leakage-disclosure` note that reports nothing surfaced, and misses a disclosure worded outside its cues, one sharing its clause
  with its own denial, and one whose cue and outcome term a comma separates —
  so **an unmarked note is not a cleared one**, and a candidate count compares
  only across runs read under one rule. That is why it changes
  nothing: a text rule deciding which cells stay scored would demote a
  predictor for its candour, unevenly across engines that write notes
  differently. So read the board with the direction stated — **a disclosed
  exposure left in the scores can only bias that predictor's accuracy and
  lift upward**, an undisclosed one is invisible here, and a cell with no
  `flags.json` said nothing, which is silence rather than a clean bill. The
  tally is read within one predictor, never as a cross-engine leakage
  comparison. The notes' text is deliberately not in the report: `metrics/`
  sits beside later replay cells, and a note naming what outcome material it
  saw is outcome text keyed by case id. It is printed to the run log as each
  cell is read (`flag from <predictor> on <case>`, credential runs redacted,
  candidates marked; `unreadable flags.json from <predictor> on <case>` for
  a note with nothing to recover). A note is read through the same
  normalisation the cell workflows apply to `flags.json`, so an
  off-vocabulary severity or category, an over-long message or a missing
  envelope field is coerced and the note read as usual; a file that cannot
  be read, does not parse as a JSON object or list, or none of whose flags
  survives that normalisation counts as unreadable. The review PR names every candidate cell — a
  lost one in a clause of its own, since it is in no figure but every
  predictor on that petition read the same provisioned inputs — and every
  unreadable note, and marks the headline itself when the headline entry has
  either. A **null** `provenance` means unknown, never offline: read
  nothing from such a report. `provisioning` counts the replayed **petitions**
  by the snapshot provenance each was given — `dated` (a snapshot the docket
  really served before the cutoff), `truncated` (a later payload with its
  post-cutoff entries removed), `blind` (no trajectory shown at all, from
  either cause: no forward moment fixed a cutoff, or truncation left a
  disposition visible and the fail-closed leakage guard withdrew the
  trajectory) — and those are three information sets, so a score over their
  union is a score over a mixture: a blind petition cannot observe its own
  relist history, which is most of what a cert forecast turns on. The
  always-deny floor is not one of the figures the information set moves — on
  either axis it is a share of the replayed set's own labels (not granted on
  the headline, denied on exact disposition). What moves it
  is **composition**: **the blind arm is outcome-selected, in either
  direction.** Both of its causes correlate with the outcome, and the
  direction is not known in advance: a docket with no pre-resolution
  distribution to show can be a petition denied without one, or one the Court
  acted on before any ordinary conference cycle, as one docketed and granted
  within days is; and a truncation that still showed a disposition is selected
  on the disposition's own docket text. So a blind arm can come out
  denial-pure, raising the pooled floor and diluting every lift, or grant-pure,
  where a predictor that calls its grant collects lift no other arm gave it.
  Neither direction is the expected one, so **read the blind arm as a count**:
  its petitions, their outcomes, and each entry's correct calls on them, never
  a rate. `provisioning_denied` gives the floor's side of that: keyed as
  `provisioning` is, a zero stated, it counts each arm's realized denials, so
  each arm's own exact-disposition floor is its count there over its count in
  `provisioning`, and the pooled floor is those arm floors weighted by arm
  size; an arm's headline floor is ``(events_scored - granted) /
  events_scored`` off a whole-set entry's `arms`. Each entry's **`arms`** gives the scores' side: per arm the entry
  scored, its `events_scored`, its `correct` calls, the arm's `denied` and
  `granted` counts (the remainder dismissed or withdrawn), its accuracy and
  lift against that arm's own floor, and its headline calls `granted_correct`.
  The arms add up — their `correct` to the entry's correct count, their
  ``correct - denied`` to its disposition lift in petitions, and their
  ``granted_correct - (events_scored - granted)`` to its headline lift, the
  bracketed figure the review PR and the digest print per arm —
  so **read which arm a pooled lift sits on before reading the lift**: a
  ten-petition lift of one petition carried by the one blind petition is a
  statement about that petition, not about the predictor's reading of a
  docket. Like the pooled floor, the floor counts are over the whole replayed
  set, so an entry short some cells is floored by neither, while its `arms`
  cover only its own scored subset. At the pinned
  draw of ten an arm can hold as few as one petition, and a floor or score over
  an arm that small is a count, not a rate: quote it as denials (or correct
  calls) over n, never as a percentage without its n. Read the mix before the
  scores, and read a shift in it between two fortnights the way you read a
  change of dispatch. Under `--spread` the mix moves every fortnight by
  sampling, since each newer blob re-keys the random draw (*How the set was
  drawn*, above), and by whatever the replayable population gained since —
  newly decided petitions and newly snapshotted ones — so a shift says to read
  the two fortnights as two independent samples, not that the draw rule
  changed. The weekly digest's cert back-test line and the review PR
  carry the outcome mix (denied, granted, dismissed or withdrawn), the same mix
  per arm, and each engine entry's per-arm score beside the figure for that
  reason — rendered by shared helpers, so the two surfaces state the same
  draw. Two things the mix does not capture.
  The first is that the day bar narrows the retrieval of every cell with a
  cutoff — the **dated and truncated** arms — and not the blind ones', so the
  arms differ in what they could *retrieve* as well as in what their
  snapshots showed — one more reason to read the mix before the scores. The
  second is the offline `prior-vote` row:
  it is masked on each non-blind cell's own cutoff day, the clock its engine cells
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
  two are scored over different sets and their floors are different floors.

  `provenance.clocks` records, per replayed petition, the arm and the two
  clock halves its cells were exported — `decided_before` (the Term) and
  `replay_cutoff` (the day, null on a blind petition) — so the clock's width
  is read from the report rather than assumed from the arm. Named petitions
  beside their arms, with the arms' outcome counts, state a named petition's
  outcome wherever its arm is pure, which includes every arm of one, and the
  draws of consecutive fortnights can overlap. So `cert-backtest` takes the
  standing report out of the working tree while the cells run and puts it
  back before writing the new one. That is a fence against an incidental
  working-tree read and nothing more: the committed copy stays reachable
  through version history, through the unmerged, force-pushed
  `metrics/cert-backtest` review branch among the full-depth checkout's refs,
  and through the public repository, which a cell's web tools can reach.

  **The clock also screens what a retrieved prior carries, not only which
  priors return.** A prior's columns are its state at the last pull, not at
  the clock, and on every prior a clocked `fedcourts query` admits — every
  query on the dated and truncated arms, which carry `REPLAY_CUTOFF`, and on
  the blind arm the queries that pass `--decided-before` as the prompt asks —
  some of them are withheld: the merits pair unless `merits_decided` clears
  every bar the clock sets; the opinion cluster (`citations`, `summary`,
  `precedential_status`, `has_opinion` and the opinion body under `--full`)
  unless the decision it records is dated before the clock by every one of
  `date_decided` and `merits_decided` the row carries; `date_decided` (on a
  granted SCOTUS prior, the termination at the merits judgment),
  `merits_brief_filed` and `distributed_for_conference` unless each one's
  own date clears the clock; and always `merits_terminated`,
  `citation_count`, the pipeline's tracking stamps (`last_pulled`,
  `last_live_polled`, `opinion_enrich_attempted_at`,
  `document_floor_probed_at`, `predict_queued_at`, `evaluate_queued_at`) and
  the party and counsel lists (`counsel`, `parties`, `attorneys`). A withheld
  column comes back at
  its no-reading value (`[]`, `null`, `false`). The lists go whole because no
  entry in them is dated and they accrue after a grant (amici,
  overwhelmingly), the same reason `redact_snapshot` strips the replayed
  petition's own party and counsel blocks; a citing count grows after any
  clock; a tracking stamp dates the pipeline's last touch of the row, after
  any clock. Under the clock an empty or null value in a withheld column means
  masked as readily as "nothing recorded" — `[]` counsel is not "no counsel
  of record" — and a cell cannot tell the two apart, so nothing may be read
  from one there. Which priors return, and in what order, the mask does not
  move, except that a `--citation` filter matches only the cites a prior
  comes back with. **The mask is still not a full as-at-clock view.** Every other
  column comes back as stored at the last pull: the caption and identity
  fields, the cert-stage dates and disposition the clock admits the row on,
  the bench (`judges`, `panel`, which the `--judge` filter and the
  prior-vote index key on, so masking them would move which priors return),
  the other live-channel signals (`distribution_count`, `cvsg_date`,
  `response_requested`, `response_requested_at`, `response_filed_at`,
  `referred_to_court`, `amicus_briefs`) and the derived salience and scope
  fields; `docs/cli.md`'s `query` row lists them by name. Read two
  consequences of what is masked. A replay cell's `query` returns no counsel
  on any prior, no citing count, and no opinion on a prior decided after the
  clock or undated, all of which an unclocked query's does, so on that surface a replay
  figure understates the same predictor's unclocked information set, as it
  does on the snapshot; the cell's open-web and CourtListener tools still
  reach a prior's current docket and opinion either way. And the mask moved
  twice, each move dated in `docs/freeze-record.md`: a report whose cells ran
  before the list mask reached `main` could retrieve priors carrying their
  full current lists, amicus entries filed after the clock included, and one
  whose cells ran before the decision-record mask reached `main` could
  retrieve a prior's post-clock opinion, citations, summary, citing count,
  termination date, merits-brief date, conference date and tracking stamps
  — post-clock facts about the priors, never about the petition itself. No
  **engine row's** series spans either boundary. The report from run
  `20261003T115301Z` (engine rows at `n=10` each, 0.700 against the 0.600
  always-deny floor on exact disposition and 0.800 against 0.700 on granted
  vs not, one petition of lift either way) ran before the decision-record mask,
  so its engine rows may not pool with a report run after it; its `prior-vote`
  (0.600) and `constant-denied` rows may. Provenance agreement cannot see them. The always-deny
  floor (a property of the labels) and the offline `prior-vote` row are
  unaffected and compare across both as before: `prior-vote` votes on
  dispositions, and passes no citation filter, so the citation gate its
  index carries for parity with `query` never runs for it.

  **The review PR's headline names a tie as one.** Entries scored over the
  whole set share one floor, so equal accuracy is equal lift; the board breaks
  such a tie by Brier only to be a total order. Where the top whole-set
  entries tie on their correct count, the headline names every one of them
  rather than a "top predictor" chosen by that tie-break; and where the
  headline entry's whole lift — every tied entry's alike — sits on one arm, it
  says which, on the headline itself.
  Below 100 petitions — a display rule, not a statistical threshold — it
  states a lift in petitions beside its percentage points, and a single
  leader's margin over the next whole-set entry in petitions: there one
  petition is worth more than a whole point, and a points figure alone hides
  that it counts a few outcomes. At the pinned ten, one petition is ten
  points.

  **The back-test measures a different process from a forward cell.** A
  **back-test** replay cell runs with no MCP server — none of the CourtListener
  sidecar tools a forward predict cell is given — and is provisioned no `documents/` — none of
  the filed-document text (petition, brief in opposition, merits briefs) a
  forward cell is given wherever any was provisioned; it gets the redacted
  docket snapshot and `context.json` — so its information set is narrower
  than the forward cell's by construction, on top of the snapshot and
  retrieval differences this section describes. A back-test figure is therefore evidence about the replayed prompt and engine
  under that reduced harness, not an estimate of the same predictor's forward
  performance, and a prompt change that works through the forward cell's tools
  or documents cannot show up here at all.

  Produced by the
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
  outcome at this size — roughly half of them for ten petitions drawn at the
  paid population's grant-family rate, though far fewer at the replayable
  population's richer mix, which is what the replayed draw samples — and there every denial-heavy
  predictor ties the floor and the ranking is not a measurement: the review PR
  withholds the top line and states the granted-side count instead, which it
  recovers from the calibration view rather than from the floor (a dismissal is
  neither denied nor granted, so `1 - floor` is a different quantity). Size
  governs the rest of the reading too: at this limit an ordering turns on one or
  two granted outcomes and a band on fewer, so read the series and each
  segment's own `events_scored`, never one fortnight's rank. Three things to hold when
  reading consecutive fortnights: they are samples of one dispatch, one salience
  floor and one lookback, which is what makes them comparable **in population**
  — one dispatch over a replayable population that grows between them;
  the report carries no process digest, so a prompt or predictor-config change
  between them is legible only from the promotion history; and a dispatched
  campaign's report is not comparable to either. The
  `provenance` block is where all of that is checked, not assumed. The
  refreshed report lands as
  a **reviewed, never auto-merged** PR. Only petitions holding a snapshot
  replay; the draw passes over the rest and the report counts them
  (`provenance.draw.passed_over`). `fedcourts cert-backtest` remains
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

  **The active `sal-v6` and the never-activated `sal-v5`.** Their cells and
  their statpack blocks cover a narrower population than every
  other version's: Rule 20 writs are outside their segment, so their
  `eligible`, recall and band pools leave them out, and a cross-version
  comparison spans that population change as well as the scoring. `sal-v6` is
  `sal-v5` with the petitioner class read through `caption-v2` rather than
  `caption-v3`, and it is the active scorer: `sal-v5` is never
  activated, because `caption-v3`'s counsel reading carries post-outcome
  information on resolved rows (a supporting United States amicus the Clerk
  lists under "Petitioner"). `sal-v5`'s statpack `alt_segments` block measures that
  leak; the replay cells do not. `sal-v5`'s replay cells measure the
  call-for-response relist rule and the writ scope but never `caption-v3`,
  since the projection carries no counsel. Either block over past Terms is
  **not that version's pool** on a pack rendered before the run-repair
  back-fill filled `distributed_after_call` and `opening_writ` on the decided
  rows: on such a pack those rows read as `sal-v4` reads them, mixed with the
  rows the live poll has re-read, and no figure from the block may be quoted
  (`docs/salience.md`, the `sal-v5` and `sal-v6` sections).

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
  pull that landed on the trigger day — and, on the `cvsg`, `sg-brief`,
  `relist`, `response-requested` and `response-filed` moments, one carrying the trigger
  entry dated on the day the event opened — which the live poller does for
  watchlisted and salient dockets and not for the rest, so the residual
  concentrates in the `truncated` arm rather than spreading evenly. And the two
  arms err in opposite directions — `dated` brackets the moment from below (it
  is the docket as pulled, so it can miss entries filed later the same day),
  `truncated` from above (it reconstructs to the cutoff but carries the undated
  counsel/amici blocks as at a much later pull). Pooling them averages a
  selected mixture of two different biases. On those trigger moments a
  cell no stored payload places is refused rather than placed, so placed-cell
  counts exclude it, and the refused count is not derivable from the ledger:
  the refusal writes no cause into the cell's status, and `collect` books it as
  an ordinary no-output cell. The `dated` arm on those moments also changes
  meaning at the carrying merge of the exact-trigger rule (before it, a pull
  from the trigger day sufficed); no context field separates the two sides, and
  the split is the stamp's `process_version.pipeline_sha` (see the freeze
  record), so a figure over that arm does not pool across it.

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
  The **pre-mint poll** carries a second membership rule of the same kind, over
  every forward interim cell rather than the arrival moment alone: a cell whose
  docket already shows its outcome when it is about to be minted is refused, so
  it never exists. The refused set is correlated with the outcome — fast
  decisions are the ones a mint arrives after, and they plausibly lean toward
  denials (unmeasured; in the committed ledger 5 of the 6 exposed applications
  were denied). The same rule thins forward cert cells too, though none of the
  394 resolved forward cert cells in the committed ledger was written on or after
  its decision date. Engines mint the same event hours apart, so a later engine
  can lose an event an earlier one kept. The run PR's per-engine pre-mint
  refusal roll-up is where those cells are counted, and it is owed beside any
  forward figure built over runs after the poll began. A refusal repeats each
  round while the corpus still shows the event pending, so de-duplicate the
  roll-up by (event, engine) before reading it as cells removed. Read any
  per-engine figure beside that engine's refusal count; only a paired
  comparison over events every engine produced absorbs the difference.
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
  same-day cell's is a forecast. Three of those increments — the CVSG, the
  response request and the referral — are read against the run itself,
  masked where the record shows the signal came first and set aside where it
  cannot order the two (`increment-run-day`, under *The set-aside, and its sensitivity reading*
  above); the relist and amicus increments are not.

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
  by relist count, by CVSG status, by **amicus-brief count** and by
  **capital-case marking** over the same
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
  the same rule on its own feed. Its unit is the **application number**, not
  the corpus row: a number the corpus stores under two or more case ids counts
  once, at its lowest-docket-id row among those the live channel observed
  (parsed or live-polled), or among all of them where none was, and the rows
  left out are counted as
  `duplicate_rows` (absent from a pack built before that rule, which counted
  rows, so absent is unknown rather than zero). What it publishes,
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
  `cert@arrival` cells — the active `sal-v6`, and earlier versions' cells beside
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

  **The call-for-response cohort's claim rule** (`cert@response-requested`
  cells, placed the day the Court called for a response to the petition). The
  cohort reports its own unranked block and never pools with another cert
  moment. Its disposition baseline is the cell's salience-band rate, and the
  cert bands do not read a called-for response, so the floor ignores the very
  signal that defines the cohort: a call is the Court's first sign that a
  petition has a reader, and a predictor that knows the call raises the grant
  odds earns skill against that floor from a known shift in the population,
  not from forecasting. So the block's skill is **not claimable** and not
  comparable to any other cert moment's until a floor conditioned on the call
  is registered; its accuracy, Brier and counts are coverage. Its
  `relist-increment` claim is masked as vacuous (the petition is all but
  certain to be distributed again once the response is in), so the block's
  claim table carries one claim fewer than every other cert block's.

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

  The **authorship section** (`authorship`, JSON only, never rendered into
  `statpack.md`) is the per-opinion record rolled up per October Term, the Term
  the opinions listing files a decision under; it is present once the record
  holds an argued decision and omitted otherwise. It counts **argued**
  decisions only, the population a merits forecast is made on: a signed
  decision whose opinion prints an argument date, and a per curiam whose corpus
  row records an argument day and no DIG (a per curiam prints no argument date,
  and one linked to no row is left out). Summary per curiams and DIGs, which
  the listing also carries, are outside it. Per Term: `decisions`,
  `per_curiam`, and `observed` (signed decisions whose bench row is filled);
  per Justice serving that Term, `decisions` decided while seated and
  `majority` delivered, then `sat` (observed decisions taken part in) and
  `separate` (of those, decisions the Justice wrote or co-wrote any writing but
  the deciding one in). The two denominators differ because the two authorship
  claims resolve over different populations. Bench rows are filled only where
  the opinion-record pass read a complete syllabus lineup, so `observed` can
  sit far below `decisions`, and a Term with none observed contributes nothing
  to the separate-writing rates. Read `observed` beside any separate-writing
  figure. It feeds the authorship claims' baselines
  (`pipeline.base_rates.majority_author_base_rate`, `separate_writing_base_rate`;
  *The authorship claims* in `docs/outcome-decomposition.md`), pooled strictly
  before the October Term of the cell's snapshot.

  The **per-Justice votes section** (`justice_votes`, rendered into
  `statpack.md` with its pairwise counts in the JSON only) is the merits
  lineups (`fedcourts merits-lineups`) rolled up per October Term of the
  opinions listing, present once the record holds a complete lineup and
  omitted otherwise. It counts **complete** lineups only: signed decisions
  whose writings seat every Justice on a filled bench row. Per curiams and
  lineups the record could not seat are in each Term's `documents` and nowhere
  else, and they are not missing at random (summary reversals, which lean
  toward disturbing, are among them). Per Term: `documents`, `complete`, and
  `judged` (complete lineups whose case row carries a plain `affirmed`,
  `reversed` or `vacated` judgment); per Justice, `sat`, `majority` (voting
  with the judgment), `in_part` (a vote in part on each side, in `sat` and on
  neither side), `disturb_eligible` and `disturb` (of the whole-side votes on a
  judged decision, those voting to disturb the judgment below); per pair,
  `both` and `agree`. Its disturb axis leaves out a DIG, an equally divided
  Court and a mixed judgment, so it is **not comparable** with the merits
  section's disturbed rate. It feeds no baseline and scores nothing: the
  merits prompt points a cell's vote block at it, pooled over the Terms
  strictly before the case's grant Term, as `fedcourts justice-priors
  --before-term` pools it.

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
  *not yet parsed*, not *did not happen*, and on the **amicus-brief cut** it
  means the live poll has not read the docket since the count was stored. That
  cut counts the amicus briefs docketed before the petition's first
  disposition entry, in `0`, `1` and `2+` buckets; it is a stakes proxy rather
  than a census (the Solicitor General's invited brief counts, a multi-filer
  brief counts once), and, like the capital cut below, marginal: it describes
  the populations, never what the count adds over the relist and CVSG cuts. The
  **capital-case cut** carries the
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
  here rest on a handful. The **emergency applications** get a cut of their
  own on the same terms from the `qp-topic-v1` application labels file, over the
  live slice's non-extension application dockets and measured against the
  application reference block. It is never pooled with the petition cut, because
  an application is labeled from its caption, docket entries and, where stored,
  its own filing rather than from questions presented, and its scope string
  counts the rows read from the docket alone, where `unclassifiable` is a rule
  rather than a finding. A **topic mix by stage** then reads both cuts as
  shares: of the labeled cert petitions, of the labeled petitions granted
  plenary review (a GVR recorded as such is left out), and of the labeled applications,
  each column a share of its own stage rather than of the docket and each with
  its own scope string. The committed copy of the document names the missing
  distribution among its gaps until someone runs `fedcourts docket` where the
  corpus is pulled — it is on demand, on no schedule. The document names the other statistics it
  cannot yet compute the same way (summary reversals, which have a disposition
  label no resolver mints — `Outcome.disposition_route` marks the class on a
  resolving grant, but that marker feeds no published cut, so the pack's
  `summary-reversal` count stays zero while such orders sit inside `granted`;
  justice-level statistics, which need a per-justice vote record) so a
  citation is never read as a claim that the figure is zero.

- `updates/<YYYY-Www>.md` — the **weekly public update history**: one file per
  ISO week with anything to show, from the email list's first send onward,
  each the `fedcourts public-update` render of that week, written by
  `fedcourts archive-public-updates` when a run first finds the week non-empty
  and never re-rendered once merged, not even for a later void or set-aside.
  The fedcourts.ai site renders it as its updates page. It is display
  material like the email: it states forecasts and outcomes side by side,
  computes no score, and no metric reads it.

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
  arrival, then its distribution, any call for a response to it and its first
  relist, then the
  interim application's arrival, the
  response requested on it and the response filed, then the CVSG and the
  Solicitor General's invited brief, then the merits moments — and then by
  event id, so a date collision never inverts the
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
  row; `case_id` is the identifier.

  **Short captions.** `short_caption` is the conventional short form of the
  caption ("Trump v. California"), for a reader scanning rows on a phone. It is
  derived by a fixed rule (`fedcourtsai.short_caption`, stated in full in the
  `short_caption_rule` provenance string): each side's first-named party; the
  United States and a state or territory as written; an organisation by its
  name less a leading "The", a parenthetical and corporate forms, or by the
  acronym the Court's own case names use for a federal agency; a person by
  surname — except that a name of exactly three full words ("Maggie Toulouse
  Oliver") stands whole, because its last two words may be one surname and the
  caption cannot say. It is **null wherever the rule is not sure** — an organisation name
  longer than six words, whose conventional short form is an acronym only a
  reader knows ("RAICES"), a person's name longer than three words or carrying
  a surname particle, where the caption cannot say where the surname starts —
  and a site falls back to the full caption. The rule reads a party whose name
  is not shaped like a person's, or that carries an alias (`dba`, `fka`, `aka`),
  as an organisation, because a whole name is never wrong where a lone word taken
  for a surname can be; it still cannot tell an organisation from a person when
  the organisation's name is two capitalised words with nothing institutional in
  them and no alias.

  **Docket numbers.** `docket_number` is the Court's own number ("26-239",
  "26A124") and `docket_url` its supremecourt.gov docket page; both are
  display-only, and the board still reads committed data alone to get them. A
  live-first case's reserved-range id is minted from its docket number and
  decodes back to it (`docket_number_source: case_id`); a CourtListener-keyed
  case takes the docket number the qp-topic labels artifact records for it
  (`qp-topics`). A CourtListener case the labeler has not reached, an
  application among them, has neither source and publishes null — its id
  carries no docket number and the board does not read the corpus. Coverage
  therefore grows with each labeling batch and with the live-first share of the
  predicted set; the `docket_rule` provenance string carries the same account.

  **Who is asking, and what each outcome does for them.** A row that reads
  "granted 30%" does not say whom a grant helps, so each row names the sides and
  says what each action open at its `moment` does for them. `asking_party` is
  the side asking the Court to act — the petitioner, applicant, appellant,
  plaintiff or movant — and `other_party` the side answering, both read from the
  caption (`fedcourtsai.asking_party`, stated in full in the `asking_rule`
  provenance string). The Court's docket names its asking side first. The board
  has no other committed copy of the docket's party labels: the structured
  petitioner and respondent titles live in the corpus, which the board does not
  read. So a caption that still carries a label ("Petitioners", "Applicants") is
  checked against its order, and one without a label is read by order alone.
  The names are the short-caption rule's, so a side has one exactly where
  `short_caption` would. `outcome_lines` holds one fixed sentence per action,
  filled with those names. The stage comes from the moment registry, as the
  row's collapse already reads it. A petition (the arrival, distribution and
  CVSG moments) gets *granted*: the Court takes up the asking side's case, and a
  grant alone decides nothing yet about who is right; and *denied*: the asking
  side's petition ends and the lower court's decision stands, which is not a
  ruling that the lower court was right. An application (the interim moments)
  gets *granted*: the asking side gets the relief requested, for now, and the
  case continues in the lower courts; and *denied*: it does not, for now, and
  things stay as the lower courts left them. A merits case gets *reversed*: the
  asking side wins, and any remaining issues go back to the lower
  court; *affirmed*: the other side wins; and *vacated*: the decision below is
  set aside and the case goes back, without the Court deciding it for either
  side. The lines state consequences only, never likelihood, and give each
  action the same weight. They never say who "wins" beyond what the action
  itself does.

  **How a line pairs with the forecast: by `side`, not by `action`.** Each line
  carries the `side` of the stage's forecast binary its action falls on. A
  petition or application forecast is P(granted): the `granted` line pairs with
  it and the `not-granted` line with its complement. The granted side also
  holds a GVR and a summary reversal, which the grant line does not describe. A
  merits forecast is P(judgment below disturbed), and there is no per-action
  merits label. `reversed` and `vacated` are both `disturbed` and pair with that
  probability together; `affirmed` is `undisturbed` and pairs with its
  complement. Neither side is one line: the mixed affirmed-in-part outcome is
  disturbed and has no line, and a dismissal as improvidently granted or an
  equally divided affirmance is undisturbed and has none either. So a site
  never puts "Apple wins" beside the merits probability as though
  that number were P(reversed).

  The three fields are null together, and `asking_declined` says why. The
  reasons are:

  - `in_re`: any "In re" caption — an extraordinary writ such as mandamus,
    prohibition or habeas — names no second side.
  - `short_form`: the short-caption rule cannot name a side, or both sides
    shorten to the same name.
  - `docket_labels`: a caption label contradicts the order, or a side is
    labeled as a cross-petitioner.
  - `original_jurisdiction`: the docket number is an original one, or the
    docket number is unknown and both sides are sovereigns (a State or the
    United States). A Term-form petition number or an application number is
    never original, so a State-against-State application is read like any
    other caption.
  - `cross_petition`: another committed case, predicted or not, names the same
    two parties in reverse order, with docket dates within a Term and a half.
    Both sides are then asking. An undated pair counts, and a pair whose other
    half is not committed is not seen.
  - `stage`: the moment registry declares no stage for the moment.
  - `no_caption`, `not_scotus` and `not_two_sided` cover the remaining shapes.

  What the rule cannot see is a named party that supports the other side, such
  as the federal government as respondent agreeing with the petitioner, or who
  stands behind a name: the names are the caption's short names, so an official
  sued in that capacity appears by surname, not as the government. The lines
  stay about the action there. The article a name takes ("the Department of
  Labor", "the FTC", but "Apple") is display-grade, not grammar-complete. Like
  the other display fields, these are never read by a predictor, an evaluator
  or a metric, and `metrics/big-cases.md` does not render them.

  **The next scheduled dates.** Like `docket_number`, `schedule` and
  `scheduled` are read from committed data outside the prediction ledger: the
  board joins them by case id from `data/schedule/schedule.json`, which the
  live poll writes from each pending public docket's entries (`fedcourts
  schedule`). `schedule` lists every date still ahead on the day the schedule
  was built, earliest first, each `{kind, date}`: `conference`, the conference
  an undecided docket's newest "DISTRIBUTED for Conference of …" entry names;
  `argument`, the day a granted case awaiting decision is set for argument,
  until an argument on or after that day is read;
  and `response_due`, the newest stated deadline for a response still owed.
  `scheduled` is its `conference` entry alone, kept for readers of the `1.3`
  board, and null where there is none. The row carries no build day, so the
  board moves only when a case's date does; a site rendering later drops a
  date that has since passed rather than show it as upcoming. A schedule moves
  on every relist, reschedule and extension, so it is display-only like the
  fields above and never a ledger record: nothing predicts, evaluates or
  scores on it. The `schedule_rule`
  provenance string states the rule in the artifact.

  **Process scope, and why the default is version-blind.** `process_scope` says
  which process versions a **current read** may come from. The default is
  `all`: every committed run is eligible, shakedown, pre-freeze,
  de-counted-digest and unstamped cells included, because the board is a census of
  what the panel said rather than a measurement of how well it said it, and a
  stakes read resolves against nothing for a partition to protect.
  `fedcourts big-cases --process-scope frozen` builds the **comparison** board,
  admitting only runs that are their predictor's counted forecast of their
  event — a harness stamp inside a counting window, the earliest window's where
  the predictor holds several — the predicate the performance boards scope on.
  On that build a pre-freeze, de-counted-digest, shakedown or unstamped
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
  a case sitting at the cert **arrival**, **sg-brief**, **relist** or
  **response-requested** moment, or
  at any **merits** moment, is never refilled however long it waits. Those are a floor rather than the whole
  of it: a pending case at a moment the rule does re-owe can still sit outside,
  because a distribution is re-owed only until the conference it was distributed
  for has considered it, and because a re-owed cell has to be minted and land before it counts.

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
different artifact — `fedcourts party-rates`, below — with its own population
rules and denial reweighting; computing one from these cells would inherit
every caveat below without carrying them.
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
from this census — the reweighted IFP rates are `party-rates`, below. **Always with the date convention and
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

**What may be claimed from the party rates.** `fedcourts party-rates`
(`pipeline.party_rates`, [docs/cli.md](../docs/cli.md)) publishes cert and
emergency-docket grant rates keyed on administration × docket stratum × the
side of the caption the federal government occupies, with `none` — the same
window and stratum, no federal party the caption names — as the comparison
cell. It is an analytics artifact: no predict or evaluate input, base rate,
claim score or leaderboard rank reads it. A rate is granted over resolved, the
binary outcome's projection (`granted_labels`; GVRs and partial grants on the
granted side), and **every share is quoted with its numerator and denominator**
— the cells hold tens of rows in exactly the places a reader most wants them
(a federal applicant's substantive asks, a federal petitioner's paid petitions),
so the pair is what tells a reader how far the share can move. Every rule the
census carries travels here too — the date convention, the rule version, the
corpus vintage, the date-not-caption attribution, rows not disputes — and
nine more are specific to rates.

- **Hold the stratum fixed, and compare against `none`, not across cells of
  different strata.** A paid-cert rate, an IFP-cert rate and an application
  rate are three populations an order of magnitude apart; the within-window,
  within-stratum `none` cell is the reference a government-party rate is read
  beside. It is a **descriptive reference, not a counterfactual**: it holds
  whatever the other litigants brought — on the application docket, mostly
  capital-stay and self-represented asks — not the same ask made by a
  non-government party.
- **The application stratum is a census only from 2025-04-18.** The live
  channel captures the application docket whole for filings from that date
  (OT2024's `24A1000` on), save a second, week-long gap at the end of OT2024:
  `24A1274`–`24A1295` are uncaptioned shell rows outside the live slice, so
  whether any of them is a federal application cannot be read from the blob. Before it, the live slice holds a selected set of
  high-profile applications — mostly the federal government's — while the
  ordinary applications of the same months sit outside it as never-polled
  shell rows; the live slice carries 35 application rows filed in July–August
  2024, then a handful a month until April 2025 (blob pulled 2026-09-28, newest
  stored snapshot 2026-07-13). So before that date a federal-applicant cell is
  nearly complete while its `none` and `respondent` comparison cells are not:
  a government-versus-`none` reading of the application stratum is cut with
  `--since 2025-04-18` (or later) and says so. **And under `--as-of filed` it
  quotes the unattributed `none` cell beside the attributed one**: 113 live
  application rows carry no filing date, overwhelmingly execution-eve capital
  stays that are almost all denied, so they drop out of the `trump-47` cell
  into the unattributed one and inflate the reference — on the same blob,
  `--since 2025-04-18` gives `trump-47` `none` 13/188 (6.9%) beside
  unattributed `none` 1/81, 14/269 (5.2%) pooled, against the federal
  applicant's 16/26. `--as-of resolved` dates those rows by their disposition
  instead and needs no such pairing. The same gap means `trump-45`
  holds no application cell at all and `biden-46` two federal-applicant
  substantive asks against the 19 applications a published count gives that
  administration: no emergency-docket rate reads across administrations on
  this corpus, and the absent cells are absences, not zeros.
- **`trump-45` does not span its administration either.** The live slice's
  earliest filing is 2017-06-27 and it holds no OT2016 docket, so a
  `trump-45` cell under `filed` covers roughly 43 of the administration's 48
  months, and fewer under `resolved`.
- **The application population is the substantive asks.** Extensions are
  granted as a matter of course and would swamp the rate, so they, the
  unreadable asks and the never-parsed applications are counted beside each
  cell as exclusions — by count only, with no labels. An unreadable ask can be
  a real emergency application (two federal applications decided by the
  replication moment below are), so a quoted rate names the exclusion counts
  beside it.
- **A partial grant of an application can carry the `denied` label.** At the
  replication moment below, two of the four federal-applicant rows labeled
  `denied` are applications the Court's own orders granted in part (`24A949`,
  `25A103`) and one was denied as moot (`24A790`). The emergency-docket rate is
  therefore a floor on "relief in whole or in part", and the per-label counts
  are what a reader re-cuts it from.
- **GVRs are grants here.** On the paid-cert federal-petitioner cells a third
  of the grants are GVRs (20 of 67 under `trump-45`, 23 of 64 under `biden-46`,
  `filed` convention, same blob); plenary grants alone are 47 of 96 and 41 of
  81. A comparison with a published "the Solicitor General wins cert about 70%
  of the time" figure has to say which of the two it is quoting.
- **The IFP rate is a weighted estimate.** The legacy one-in-ten sampled denial
  block is restored to full strength (`weighted_granted` /
  `weighted_resolved`, each row counted `sample_weight` times), and
  `grant_rate` is that pair's quotient; the raw pair beside it is the rows
  actually held. A cell with `sampled_rows` above zero is an estimate resting
  on the sample being a systematic one-in-ten draw of denials, and its raw pair
  is never quoted as a rate. `pending` stays a raw row count.
- **Without `--through`, the newest window is right-censored.** Under `filed`
  its pending rows sit outside the rate (18 of the 45 `trump-47` paid-cert
  federal-petitioner rows on the same blob), and the petitions still pending
  are disproportionately the relisted and CVSG'd ones, so a rate over what has
  resolved is not yet the window's rate. Under `resolved` the pending rows move
  to the unattributed cells. `--through` places the cut at a fixed past moment
  instead — rows filed later leave, dispositions dated later read as pending —
  which is how a published tally is compared as of its own date.
- **The rule version moves rows between cells, not only into them.** The cut
  defaults to `party-v2`: `party-v1` plus an analytics-side supplement to the
  federal class for caption shapes `caption-v2` reads as private — the
  officer-then-department caption the Department of Homeland Security's
  applications carry, the Commissioner of Social Security, and federal agencies
  named in full that the caption rules list only as initialisms or not at all.
  Per caption half the widening is one-directional by construction (153 halves
  of the census frame move from `private` to `federal` on the same blob, each
  inspected as a federal party, and none moves the other way), but per row the
  side composition moves rows out of cells too: over the rows the rates cut
  reads, 148 move `none` → `respondent`, 17 `none` → `petitioner` and one
  `respondent` → `both` — a removed NCUA board member suing individually and
  in his official capacity, whom the class reads as the government. The census stays on `party-v1` by default, so a census
  count and a rates cell are comparable only where both name the same rule.

**The counsel dimension (`--counsel-rule sg-office-v1`).** With it, every cell
is also keyed on `sg_counsel`: which side(s) the Solicitor General's office is
counsel for, read from the row's petitioner and respondent counsel entries
against a dated roster (`pipeline.counsel`, sources in
[docs/data-sources.md](../docs/data-sources.md)). The rule version names the
roster, so a cell quoted from it names `counsel_rule_version` beside the party
rule. Every figure below is from the blob pulled 2026-09-29, newest stored
snapshot 2026-07-13. Six rules travel with it.

- **Paid cert and applications only.** The index carries no counsel on all
  but about a dozen resolved IFP rows today — an ingestion gap, not a property
  of IFP dockets — so those rows read `unknown`, and an IFP cell keyed on
  `sg_counsel` holds pending rows' readings and little else; the few resolved
  IFP rows that do carry counsel are grant-enriched, one more reason no IFP
  rate is quoted by counsel side. No paid-versus-IFP comparison is drawn from
  this dimension until the gap is closed and backfilled. The application half
  inherits the application stratum's own coverage rule above: a
  counsel-keyed application cell is cut with `--since 2025-04-18` or later.
- **Counsel accrues after docketing, and the list is as of the row's last
  write.** A response or waiver adds the respondent's counsel, and the Court
  calls for a response before most grants, so a resolved docket with no
  respondent counsel is enriched in denials by construction and a pending
  docket's `none` is provisional. `--through` rewinds the docket's life, not
  its counsel list: a cut at a past moment still reads the counsel the row
  holds now, and a successor the list gained after the cut reads as the office
  on a federal party, as any late write does. A granted docket's life also
  runs a year past its grant where a denied one ends at the denial, so the
  life depends on the outcome in one direction: setting that year to zero
  moves 7 rows, all granted, out of the office cells on this blob. So
  `sg_counsel` says who the office answered for by the docket's end — a
  descriptive split beside the caption, never an arrival-time covariate or a
  predictor of the grant.
- **Read it beside `federal_party`, not instead of it.** The two disagree on a
  measured mass, and that is what the dimension is for: over the whole blob
  under `filed`, 503 paid-cert rows (475 resolved) whose caption names no
  federal party carry the office as respondent counsel (an `In re` petition, a
  court or an officer the caption rules read as private), 14 carry it as
  petitioner counsel, and 26 (21 resolved) whose caption names a federal
  respondent carry counsel but no office entry. The pending rows among them
  are provisional readings, per the rule above.
- **The dates are what make it precise.** The same roster read without dates
  counts a former Solicitor General at a firm, or a future one as a state
  solicitor general or private counsel, as the office. Scored against the
  firm/office `Title` field — which the index does not store, so only on the
  sample that carries it: the latest stored live snapshot of 1,567 OT2023–OT2025
  dockets, grant-enriched and not random, with no applications — of the 46
  petitioner-side and 597 respondent-side entries the dated rule reads as the
  office, 45 and 595 carry a Title naming it (the rest have a blank Title and
  a federal party); the undated roster reads 60 and 603, of which 46 and 595.
  That is precision. The dated rule drops 1 of the 46 petitioner-side and none
  of the 595 respondent-side entries whose Title names the office, and the one
  it drops is a Title recorded after the docket closed, naming the office the
  attorney joined later. The Title predicate (it contains "solicitor general"
  or "department of justice") is a loose proxy: it also matches state
  offices — 46 non-roster entries in the sample, New York's solicitor general
  and several state justice departments among them — which is harmless only
  because no roster entry in this window carries a state Title. The sample
  covers filings from 2023-06-30 on: the Francisco and Wall years and
  Prelogar's first two are untested against Title, and 459 of the 643 office
  readings it scores are Sauer's. Corpus-wide, the spans set aside
  156 roster entries (99 petitioner-side) on 154 live-slice dockets — all 57
  respondent-side entries and a sample of 30 petitioner-side ones inspected,
  every one a private-practice or state appearance — and the dockets read as
  the office move 401 → 302 petitioner-side and 4,760 → 4,711
  respondent-side.
- **Recall is unmeasured.** The roster names the office's leadership and one
  career deputy; an Assistant to the Solicitor General or another deputy
  signing as counsel of record is missed without trace (a deputy off the
  roster signs 2 blocks of the Title sample), and a name is matched on its
  listed spellings only.
- **A handover can flip a docket at the edge.** Some span boundaries are the
  public record of a handover rather than a date an OSG page prints, and a
  docket resolved within days of one may fall either side; a corrected date is
  a new rule label, so a published cell keeps replaying under the roster that
  produced it.

**Validation against the published administration tallies.** The
emergency-docket cell was checked against two published counts of the federal
government's applications, each cut `--as-of filed --through <the tally's
date>` on the same blob, federal applicant meaning `federal_party`
`petitioner` or `both`, and every non-extension ask counted. It validates the
federal-applicant **numerator** — how completely the corpus holds the
government's applications and how it labels their outcomes — and says nothing
about the comparison cells, whose coverage the rule above governs.

| Published figure | This corpus | Reconciliation |
|---|---|---|
| 28 applications filed by the administration from 2025-01-20 to 2025-10-01, 2 withdrawn (Ballotpedia, 2025-10-01) | 25 — 22 substantive `petitioner` rows, 2 unreadable-ask rows and 1 `both` row (`25A312`) — 2 of them withdrawn | The 3 absent (`24A885` and `24A886`, the birthright-citizenship companions, and `24A904`) are stored only as uncaptioned shell rows outside the live slice, never live-polled — inside the pre-2025-04-18 coverage gap, not misclassified |
| Of the 23 decided: 19 granted in full, 2 in part, 1 denied, 1 dismissed as moot — 19/23 = 82.6% granted in full | 16 granted, 4 `denied`, of 20 decided — 80.0% | The 4 `denied` (`24A790`, `24A831`, `24A949`, `25A103`) match the published 2 partial grants, 1 denial and 1 mootness dismissal in count and — per the Court's orders, an external check the corpus cannot reproduce — in identity; the 3 absent applications were all granted, and adding them gives 19/23. "In full" follows the published source's convention: the partial stays granted in `24A884` carry `granted` in both |
| 3 pending on 2025-10-01 | 3 pending (including `25A312`, the `both` row) | Agrees |
| 19 applications in the administration's first 20 weeks, to 2025-06-09 (Vladeck) | 16 | The same 3 absent applications all fall in the window |
| 19 applications across the whole of `biden-46`; 41 across `trump-45` (Vladeck) | 2 and 0 | Coverage: the application docket is not captured before mid-2024, and only selectively until 2025-04-18 |

The "16 granted" counts the two unreadable-ask applications (`24A884`,
`24A1203`, both `granted`), which the published cell excludes by count and
without labels — so that figure needs the rows themselves, not the artifact
alone. Under `party-v1` the first row reads 18 rather than 25: the five
Department of Homeland Security applications in the window (`24A949`,
`24A1059`, `24A1079`, `25A169`, `25A326`), the National Institutes of Health
application (`25A103`) and the DOGE Service application (`24A1122`) caption as
private under the census's rule — the measured reason the rates cut defaults
to `party-v2`. The published cell under the repository's own convention —
substantive asks only, withdrawals resolved and not granted — is 14 of 20
(70.0%) at that moment, with the 2 unreadable-ask applications excluded beside
it.

**What may be claimed from the executive success cut.** `fedcourts
executive-success` (`pipeline.executive_success`, [docs/cli.md](../docs/cli.md))
publishes the federal executive's emergency-docket record by administration
and by who filed, over the applications the scope rule `exec-action-v2`
(`pipeline.exec_action`) reads as challenging or defending a general federal
executive action. It is an analytics artifact like the party rates, and every
rule of the party rates on dates, coverage, the rule version and the corpus
vintage travels with it, save one: this cut dates a row with no docketed date
by its first proceeding, which the party rates do not. Nine more are specific
to it.

- **A rate reads in the executive's direction.** A government application on
  the granted side (in whole or in part) and a challenger's application denied
  are both the executive's win, so the `government`, `challenger` and pooled
  `all` cells share one meaning. A challenger's application granted in part is
  the executive's loss. Counting partial relief as relief is this cut's
  convention; a published tally that does not state its own is compared on
  that assumption, and the per-label counts let a reader re-cut it. A
  `challenger` cell is not comparable with a `respondent` grant rate from
  `party-rates` without inverting it, and its population is narrower.
- **The denominator is substantively decided.** Withdrawn applications and
  those dismissed or denied as moot sit beside the rate, as in the published
  tallies. An application deferred to argument has no disposition until it is
  decided, so it is `pending`, outside the rate. The default `finer` reading
  re-reads each stored denial from its latest live snapshot, because the
  stored label collapses a partial grant and a denial as moot to `denied`; an
  entry dated after `--through` is not used. Quote `reading`,
  `reread_changed`, `reread_unobservable` and `reread_after_through` beside
  the rate. Under `registered` the government's rate is understated where it
  filed, and overstated where it defended.
- **Scope is a caption rule, and its unknowns are not zeros.** The rule reads
  the caption and the Solicitor General's counsel entries, and it narrows the
  government-respondent side only: every government application is in scope
  but one. The exception, under `exec-action-v2`, is a request for leave to
  file over the word or page limit, `procedural-request`, read from the
  application's own submission entry where its stored ask is not
  substantive: granting it decides nothing, so it is out of scope on both
  sides and counted under its reason. It is read from a live snapshot, so a
  request whose row has none keeps its caption reason and is counted like
  any other. Of the 28 requests the two-rater hand check codes procedural, the
  19 the caption steps keep in scope or unknown are all set aside, and none of
  the 58 other counted applications read with them, those the replication's
  issues name, is (blob pulled 2026-10-31). Its pattern is
  "in excess of" or "exceed" the word or page limit; another phrasing is
  missed. `exec-action-v1`, still registered, counts such a grant as the
  filer's win. `unknown_scope` counts the rows it
  cannot place — a named individual with `et al.` against an officer, and rows
  only the counsel entries put on the government-respondent side — and a
  quoted figure names that count beside it. `review_rows` lists them, and every
  in-scope row, for hand review.
- **An unreadable ask is in the population.** In-scope applications whose ask
  the parser could not read are counted like any other and tallied as
  `unknown_ask`. They include granted federal applications (`24A884`,
  `24A1203`), which a substantive-only population would drop.
- **Counts before rates.** The cells hold tens of rows at most, and no
  interval is reported; a cell under about fifteen decided rows is quoted as
  its pair, not as a percentage.
- **Coverage bounds the comparison.** On the blob below the earliest in-scope
  application was filed 2023-07-10, so `biden-46` cells under `--as-of filed`
  hold 2023-07-10 to 2025-01-19 only, and `trump-45` holds none. No
  cross-administration comparison reads from that blob; one needs a blob that
  holds the back-filled earlier Terms.
- **An empty docketed date is dated by the first proceeding.** A row whose
  docket carries no docketed date has a null stored `date_filed`; the cut
  dates it by its first proceeding entry, the submission, wherever a live
  snapshot is read, for the window, the `filed` attribution and the
  controversy's first application. Each review row's `date_source` says
  which, and `filed_from_first_entry` counts the fallbacks; quote it beside
  any figure for a window that holds them. A row with neither date sits in
  the unattributed cells.
- **A controversy rate is beside the application rate, not instead of it.**
  `controversy_cells` group the in-scope applications under `controversy-v2`
  (`pipeline.controversy`): two applications are one controversy where they
  share a case below; one order decided both (read only for an application
  decided by the cut's moment); their disposing orders read alike, once
  markup and each one's own number are set aside, on one day, from one court
  below, against one leading government party; or both are government
  applications whose captions name the same leading party on each side, from
  the same court below where both name one, the later filed within 210 days
  of the earlier's decision. The groups are the connected sets. The 210 days
  sit between renewed applications in one dispute (123 and 187 days after the
  first was decided) and the nearest new dispute under an old caption (263
  days, *United States v. Texas*), so the bound is a measured choice with a
  thin margin; a renewal more than 210 days on, such as `26A406` after
  `24A1153`, is its own controversy. A controversy takes the executive's result in its last
  substantively decided application, by stored decision date, and is
  `indeterminate` where none was decided; its administration is that of its
  first-filed application dated under the cut's convention, and its filer is
  `government`, `challenger` or, where both sides filed in it, `both`.
  `controversy_unlinked` counts the grouped applications with no live
  snapshot, which can join on the caption alone; quote it beside the pairs. The rule
  joins only what the record links, so two challenges to one policy brought by
  different parties and decided apart stay two controversies, and it reads no
  policy area. A published per-policy grouping can be coarser, so a reader
  quotes `controversies`, `determinate` and `indeterminate` with the pair, and
  each review row's `controversy_id` shows the grouping.
- **A keyed controversy is a hand grouping, beside the rule's.**
  `policy_controversy_cells` count the same controversies again with the
  joins of the policy keys under `policy-key-v1` (`pipeline.policy_key`)
  added: a committed reference naming the applications that challenge or
  defend one federal policy, or that sit in one suit across courts, such as
  the travel ban, the census question or one EPA rule, whoever brought them
  and wherever they were decided. One grouper made the keys: the authoring
  session, alone, with no second rater and so no agreement figure, not blind
  to the outcome, and with the published column below in view, which joins
  related litigation the same way. A keyed pair that matches the column is
  therefore not an independent replication of it. The session grouped the
  rows the policy-area rounds labeled (OT2016 from 2017-01-20 through
  OT2024), reading the raters' notes and the public cases the dockets name,
  so a key is not reproducible from the record. The newest keyed application
  is `24A199`: no key reaches a `trump-47` row, and the keyed `trump-47`
  cells equal the rule's. A later application joins only by the rule until a
  key lists it, and adding one keeps the label, so a quoted keyed figure
  names its commit. The rule's cells stay the headline: a keyed pair is
  quoted as the rule's pair with the keyed one beside it, and
  `policy_key_joins` says how many fewer controversies the keys count. Each
  review row's `policy_controversy_id` shows the keyed grouping. A key can
  join across a transition, and its controversy takes its first dated
  application's administration, as the rule's do; a keyed application
  outside the cut's in-scope population is joined to nothing.
- **A policy area is a hand label or a measured labeler's area, and a
  per-area cell is small.** `policy_cells` count the in-scope applications
  per administration, filer and policy area under the version
  `policy_rule_version` names, at the application level. Under
  `policy-area-v2`, read once the application labeler's policy areas have
  passed their measurement against these hand labels (`docs/qp-topic.md`,
  *Policy areas*), a hand-labeled row keeps its hand label and every other
  row carries the labeler's area, which is agreement with this reference
  rather than accuracy; each cell's `labeler_rows` counts those rows and each
  review row's `policy_source` names its source, so a quoted per-area pair
  under `policy-area-v2` names its labeler count. The labeler reads the
  docket alone and may not use its knowledge of a case, so it calls `other`
  where a hand rater named the case's policy; the measurement counts that
  direction per area (`labeled_other`). A v2 cut reads the newest *passing*
  measurement, which `policy_measured_batch` names: a later refused
  measurement leaves it standing, and the labeler areas grow with every
  passing batch after it, so two v2 cuts compare only beside that batch and
  the artifact each read. Under `policy-area-v1` (`pipeline.policy_area`)
  every label is the hand set's. The hand labels are a committed reference,
  not a rule: two agent raters, each blind to the other but not to the outcome (the docket
  entries carry the orders), labeled every in-scope and unknown-scope
  application from its caption, court below and docket entries and from
  their own knowledge of a public case the docket names, so a label is not
  reproducible from the record alone. They agreed on 110 of 115 (Cohen's
  kappa 0.95, counting every miss), and the authoring session adjudicated the
  rest, not blind, every one to the second rater's label. Three of the five
  were the first rater's notes describing another row's case within four
  consecutive rows, which the notes show, so on the subject itself the raters
  disagreed on two (113 of 115). `other` is also the label of a subject the
  raters could not determine. A second round labeled 154 more rows the same
  way: the OT2017–OT2022 applications the rule reads in scope or unknown and,
  from any Term, the federal-party rows it reads out of scope. They agreed on
  146 of 154 (kappa 0.94), 76 of 77 on the rows both judged in scope (kappa
  0.98; their scope calls are hand codes, not committed), and the authoring
  session adjudicated the other 8, not blind. A third round labeled the 13
  OT2016 rows filed from 2017-01-20 that the rule reads in scope, or that
  name a federal party and ask for more than an extension of time: the two
  travel-ban stays in scope and 11 individuals' cases out. The raters agreed
  on all 13 sides and scope calls (hand codes, not committed) and on 12 of 13
  areas, and the authoring session put the one split to `other`, not blind.
  A label names a row's subject whatever its scope, so an out-of-scope row
  can carry any area. `policy_uncertain` marks the 103 of the 282 labels
  where the subject is in doubt: 26 of the first 115, where a rater was
  unsure (13 of them in scope), and 77 of the later 167, where a rater was
  unsure or the raters' areas differed. A quoted per-area pair names its
  uncertain count. An
  application neither source labels is `policy_unlabeled`, outside every
  cell, and a quoted per-area figure names that count: under
  `policy-area-v1`, every application added after the hand labels; under
  `policy-area-v2`, a policy row the labeler has not reached yet, so the
  count can rise when the cut switches version and falls as later batches
  backfill. Most cells hold a few
  rows: quote the pair.

**Hand-coded check of the scope rule.** Measured under `exec-action-v1`,
before an empty docketed date took the first proceeding's. Every federal-side application of the
`--through 2026-10-12` cut below (232 of its 828 applications: every reason
but `no-federal-party`) and a seeded sample of 60 `no-federal-party` rows (the
lowest 60 by the SHA-256 of `scope-sample-v1:` plus the docket number) were
coded in scope, out of scope or unclear by two agent raters, each blind to the
other and to the rule but not to the outcome (the docket entries carry the
orders), from the caption, court below, counsel entries and docket entries and
their own knowledge of a public case the docket names. They agreed on 263 of
292 (kappa 0.81). The authoring session adjudicated the other 29, not blind:
20 out (13 of them individuals' own cases, mostly pro se, that one rater left
unclear), 8 in, 1 unclear. It drew one line worth stating: a federal suit to
enforce an agency's reading of a statute against a state (the EMTALA suits,
`23A469`, `23A470`) is in scope, while a preemption suit against a state law
(`23A296`, `23A814`) contests no executive action and is out. The
hand codes are not committed; they are the measurement set a narrower rule's
change would commit beside it. Against them the rule agrees on 255 of 292:
196 of the 232 federal-side rows and 59 of the 60 sampled others, none of
which is in scope by hand. Of the 37 differences:

- **9 go the wrong way.** In scope by the rule, out by hand (6): the
  unnarrowed government applicant reaches a preemption suit (`23A814`), a
  bankruptcy trustee's objection (`23A87`), one person's removal (`24A949`),
  and two rows whose government side is misread (`24A407`, a state's
  application the government opposed, and `24A795`, a private suit in which
  the United States defends the statute); a state's application in a
  preemption suit reads as a challenge (`23A296`). Out by the rule, in by hand
  (3): an organization the word list does not name (`24A106`), and two federal
  suits read as prosecutions, the EMTALA enforcement suit and a challenge to a
  federal land exchange (`23A469`, `25A1008`).
- **23 of the rule's 24 unknowns resolve** (`individual-group`,
  `sg-respondent-only`): 9 in scope, among them class and group challenges to
  the Alien Enemies Act removals (`24A1007`), FERC and EPA actions (`23A485`,
  `24A199`) and self-regulatory proceedings under agency oversight (`24A287`,
  `24A808`), and 14 out.
- **5 are rows the rule places and the hand codes leave unclear.**

So the rule's in-scope reading holds on 84 of its 91 in-scope rows, and it
misses 3 of the 96 the hand codes put in scope outright, with another 9 among
its unknowns. Two side misreadings also turn a challenger's filing into a
government application (`23A712`, `24A754`, both unattributed unreadable
asks), which flips its win direction. For the `trump-47` pairs below, the hand
codes would drop `24A949` from the government's cell (a win: 26/32 on 41; the
raters split on it, so that figure rests on the adjudication) and add
`24A1007`, `24A808`, `25A1008` and `26A274` to the challenger side: 7/9 by the
cut's convention, or 8/9 reading `26A274`, an intervenor's stay that helped an
FCC action, in substance, the same direction flip as above. The
`exec-action-v1` reading is unchanged by this check; `exec-action-v2` is the
narrower rule it called for, on the procedural requests. Five of the rows this check codes in scope (`23A55`, `23A300`,
`23A712`, `24A754`, `25A327`) are only requests to file over the word or page
limit. None has a docketed date, so under `exec-action-v1`, which this check
read, they sit among the unattributed rows and in no administration's pair;
`exec-action-v2` dates them by their first proceeding and sets them out of
scope as `procedural-request`. The second policy-label
round's hand codes, not committed either, put such a request out of scope as
procedural, since its grant is no ruling on the executive action; the counts
of this check hold the five in scope.

**Replication against the published tally.** Adam Feldman's SCOTUSblog
column of 2026-10-19 ("Where the Supreme Court favors Trump on the emergency
docket – and where it doesn't") counts applications involving general federal
executive actions through 2026-10-12, and lists no rows. The figures below
are this record's measurement under `exec-action-v1` and `controversy-v1`,
before an empty docketed date took the first proceeding's; the current code
cuts under `exec-action-v2` and `controversy-v2`, so it does not reproduce
them, and a refreshed record states its own versions. Cut `--as-of filed
--through 2026-10-12` on the blob pulled 2026-10-26 (newest stored snapshot in
the index 2026-07-13; the re-read rows' own live snapshots run later):
`finer` reading, 59 stored denials re-read, 7 relabeled, 0 unobservable, 0
dated after the cut; unknown scope `biden-46` 16, `trump-47` 6, unattributed 2.
Six in-scope applications carry no administration (every one an unreadable
ask with no filing date): 5 `government`, all won, and 1 `challenger`, lost;
by controversy 4/5. Some may be `trump-47` rows, so each `trump-47` pair below
can move by up to that much.
Every grouped application has a live snapshot (`controversy_unlinked` 0). The
caption link alone makes 5 joins, all `trump-47` government pairs under one
caption (`24A1059`/`25A326`, `24A1106`/`24A1174`, `24A1153`/`26A406`,
`24A831`/`25A269`, `26A297`/`26A305`); without it the `trump-47` pair is 30/36
over 45 controversies. Every in-scope application carries a policy-area label
(`policy_unlabeled` 0). The unattributed government applications hold health
2, foreign affairs 1 and other 2, so of the per-area `trump-47` pairs below
only health can move, by up to 2.

| Published figure | This corpus | Reconciliation |
|---|---|---|
| `trump-47`: the government filed 42 core applications | 42 in-scope `government` rows (38 substantive, 4 unreadable-ask) | Totals agree; the column lists no rows, so a row-level match is not verifiable. The birthright-citizenship companions (`24A885`, `24A886`) and `24A904`, absent from the live slice in the party-rates validation above, are in it on this blob |
| `trump-47`: the government won 27 of 33 substantively decided (82%) | 27/33 | Totals agree, under this cut's partial-relief convention. Outside the rate: 4 withdrawn, 3 denied as moot (`24A790`, `25A952`, `25A999`) and 2 pending at the cut (`26A416`, `26A476`, filed 2026-09-28 and 2026-10-08, not deferrals). The 2 partial grants (`24A949`, `25A103`) are wins. Under `--reading registered` the figure is 25/36 |
| `trump-47`: 3 applications by challengers | 5 in-scope `challenger` rows, 2 unknown-scope | Scope: 4 of the 5 are employers' stays of National Labor Relations Board proceedings, which the column may not count as general executive action |
| `biden-46`: 81 applications, 18 filed by the government; 10 of 15 won | 2023-07-10 to 2025-01-19 only: 38 in-scope rows, 11 `government` (7 of 11 won) and 27 `challenger` | Coverage: the corpus holds no `biden-46` application before OT2023 |
| `trump-45`: 25 of 33 won | No rows | Coverage |
| `trump-47`: the executive won 23 of 30 determinate controversies (77%) | `controversy-v1`, every filer: 28/33 determinate (5 losses against the column's 7), 40 controversies over 47 applications, 7 indeterminate (`government` 23/28, 35 controversies over 42 applications; `challenger` 5/5) | Scope and grouping: the 5 `challenger` controversies include the 4 Labor Board stays the scope row flags (without them, 24/29). The column also joins related litigation over one policy, which `controversy-v1` does not read, and does not state how it scores a controversy with several applications. With no rows listed, neither difference can be broken down |
| `biden-46`: 29 of 39 determinate controversies; 21 of 27 challenger-initiated | 2023-07-10 to 2025-01-19 only: 17/23 every filer, `challenger` 11/13 | Coverage |
| `trump-47` government-filed immigration: 14 applications, won 11 of 12 decided | `policy-area-v1`: 13 rows (none uncertain), won 11 of 11 decided | One application short and one loss fewer; the column lists no rows, so which one is not verifiable |
| `trump-47` government-filed personnel and removal: 10 applications | 11 rows (1 uncertain), won 6 of 9 decided | One row more; the column lists no rows, so which one is not verifiable |
| `trump-47` government-filed education: won both; health: won its one decided | education 2 rows, 2 of 2; health 2 rows (1 uncertain, pending), 1 of 1 decided | Agree on the decided pairs |
| `biden-46` government-filed education: lost all 3 decided; firearms (the ghost-gun rule): won both | education 3 rows, 0 of 3; firearms 2 rows, 2 of 2 | Agree on the decided pairs |
| `biden-46` government-filed: 5 education, 5 health (all 4 decided won), 4 immigration (2 of 4 won); challenger-filed: 25 health and 23 environment and energy of 63 | 2023-07-10 to 2025-01-19 only: government 3 education, 0 health, 2 immigration (1 of 2 won); challenger 2 health and 20 environment and energy of 27 | Coverage: the vaccination-requirement, FDA and student-loan applications predate OT2023 |

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
tool over a stretch of the ledger is a capture fact, not a behavioural one —
and so is codex appearing to make no manifest call over the bare-name stretch
the throttle-coverage reading below names, whose calls are counted as
builtins.
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
real ratio. Where the engine's telemetry logs how each call ended but no
result payload, every row is `outcome_only`: its status is read from the logged
failure and its message, so a quota refusal the server raised as a tool error
is countable while a throttle note appended to a *successful* result can never
be seen — a **narrower floor** than a paired engine's, structurally. That
engine's logs captured before its rows carried the outcome read `unobserved`
and supply no denominator at all, so its figure is scoped to the later logs and
a move across that change is a capture change (`docs/freeze-record.md` dates it). The third case is a **code-mode** engine, whose
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
in what could be seen, not only in what happened, and no two of the three
supply a denominator of the same reach. And the denominator moves with capture: a
log carrying no lifted rows is one capture never minted them for, not a cell
that made no manifest call, so a ledger-wide cut pools stretches with
categorically different coverage. A further case, codex-only, is a naming
one. Codex logs written from `20260916T170237Z` until bare-name resolution
reached capture record each manifest call under its bare tool name
(`search`). Those rows count as builtins: their result condition was never
read, and the MCP counts, the offered-vs-called table and the per-actor MCP
column all miss them. So over that stretch every manifest-gated codex figure
is **unknown, not zero**, and stays so, because no committed log is
re-derived. Codex's earlier manifest rows, from `20260820` to `20260901`, are
all code-mode lifts and so `unobserved`, so they add calls but no throttle
denominator. Codex's throttle figure is therefore capture-blind until logs
captured after the resolution arrive. Its call counts are those earlier
lifted rows plus the later resolved ones, two capture regimes. A move in
either figure across the resolution is a capture change, not a behavioural
one (`docs/freeze-record.md` dates it). A third codex seam is the session one:
capture reads the cell's parent session and every subagent session it spawned,
so from the carrying merge a codex log gains the rows its subagents made, and its
call counts and manifest denominator with them; earlier logs read one rollout,
which on some cells was a subagent's (`docs/freeze-record.md` dates this too).
Read a per-engine throttle number as scoped to the logs that could express one.

**What may be claimed from `self_provisioned_fetches`: a described share and a
common-record comparison on the leaderboard, never a rank, a headline figure or
an exclusion.** The log's third summary counts the calls through which a cell
**reached outside** the provisioned `record/documents/` set for a court filing
([predicted-artifacts.md](../docs/predicted-artifacts.md)), and the run PR's
per-run note names those cells. The leaderboard reads it two ways, both
registered in [freeze-record.md](../docs/freeze-record.md) and both
descriptive:

- **`self_provisioning`**, on each pooled entry (cert and stage blocks), over
  its `forward` stratum's cells — the stratum its headline figures read — and
  on each engine in `paired`, over its paired cells: those cells by reading off
  each scored prediction's own log — `reached` (a filing fetch),
  `target_blind` (no legible filing fetch, but a fetch-tool row naming no web
  address, so one could be hidden there), `unlogged` (no readable scored
  prediction or log), out of `cells`. Cells, one per (case, event, predictor).
  Where `reached` or `target_blind` is non-zero, the figure beside it may span
  more than one information set.
- **`paired.common_record`**: the paired figure restricted to the paired
  events on which no engine's log shows a legible fetch of a court filing
  outside the provisioned set — every engine's cell reads `none`, so a reach,
  a target-blind fetch or an unread log on any engine drops the event. It says
  nothing about other retrieval, which a forward cell may do without
  restriction. It is a **selected** subset, and not neutrally: a cell reaches
  past the record where the record is short and the case contested, so the
  selection runs on behaviour that tracks the outcome and the forecast's
  uncertainty, and it drops grants and close petitions first. Read each
  engine's common-record figure against that subset's own
  `always_deny_accuracy` and `in_sample_grant_rate`, never the full paired
  set's: an accuracy equal to the always-deny floor there says the subset holds
  little to call, not that every engine called it well. It is never ranked,
  and never differenced against the paired figure.
- **The exclusion is engine-asymmetric** before the URL-first slice rule. On a
  log captured before it, every claude `WebFetch` is a prompt-only row, so
  `target_blind` drops every event on which claude fetched anything at all,
  while another engine's cell drops an event only on a legible filing fetch.
  `common_record` therefore excludes more of the events claude engaged with,
  for a reason about capture rather than behaviour. A claude cell captured
  before that rule's carrying merge keeps reading `target_blind`, so the
  `proc-v9` window holds cells under both regimes.

No rank key, headline figure or exclusion reads either, and no score is
adjusted. Four limits bind both readings, and every claim from the counts beside
them.

It is a **reach, not an acquisition**. The row is the call; whether anything
came back is `result_status`'s business, and on a shell row that is the
engine's own failure marker rather than a read of the payload. A refused fetch
counts and moved no information set, so condition on `result_status` before
reading any count as text a cell actually got — on the committed ledger that
distinction moves one engine's cell count by more than a third.

It does **not** say the record was **short** what was fetched — the manifest
that could say so is thrown away with the runner — so it counts recovery and
re-fetch alike.

It is a floor with **four** known holes, not one: a call that left no row, a
URL past the row's 500-character query cut, a hosted web search carrying a bare
filing URL (deliberately excluded, since a search is not a fetch and such a row
captures no result either way), and — on a log captured before the
fetch-target slice rule the freeze record dates — a fetch tool called with a
prompt beside its URL, whose slice there kept the prompt alone and so leaves
nothing to match. The fourth applies only to such logs: a log captured under
that rule carries the URL ahead of the prompt, and its prompted fetches are
matched like any other. The fourth is the one hole a row shows: such a fetch
names no web address, so the leaderboard counts its cell `target_blind` (read
the count off each figure's `self_provisioning`) and keeps its event out of
`common_record` rather than reading it as `none`; `reached` is a floor for an
engine until its target-blind cells are gone. The other three are not
measurable from the rows; the third of them (a bare-URL hosted search) cuts
against one engine. The fourth, shown as `target_blind`, cuts against
claude's logs captured before the rule.

And the floor is **engine-shaped**, which is adjacent to the throttle
denominator's unevenness rather than the same thing — and the difference
decides what a reader may do about it. Throttle coverage is a *denominator*
problem, so its remedy is to scope the figure to the logs that could express
one. This is a *numerator* problem: what a reach leaves in a query slice
depends on how an engine spells its tools, and there is no per-engine subset
that could express it, so no scoping recovers a comparable figure. The
per-actor split is therefore **not** a behavioural difference between engines
and must not be differenced, ranked, or read as one — which is why the note
renders it in actor order with each actor's own denominator rather than sorted
by count. The by-hand comparison it supports runs over the cells the note
**names**, and that list is capped, so on a wide run the remainder is countable
but not nameable.

**The backtest-as-iteration doctrine.** Backtests (the retrospective stratum,
the replay runs, `backtest.json`, `cert-backtest.json`,
`salience-replay.json`) are **iteration
instruments** — for tuning prompts, retrieval, and calibration — and are
**never claimable performance**; the project claims results only from genuine
forward predictions. Timing is the integrity mechanism: the prediction's
harness clock (`fedcourtsai.integrity.cell_clock` — the process stamp, else
the unstamped cell's `created_at`) against the outcome's `resolved_at`, both
committed artifacts, decides the stratum — not any restriction on what a cell
could retrieve. Replay cells run with the same tools as forward cells (the
replay clock narrows only what the corpus `query` returns, and what a returned
prior carries — the `cert-backtest.json` entry above lists the withheld
fields); the cross-evaluator's leakage grading (the `leakage` block on each
`evaluation.json`, read off the harness-captured `retrieval_log.json`) makes
contamination of the *iteration signal* visible, and its coarse bit is what
takes a contaminated cell out of every scored figure (*The leakage exclusion*
above). Timing alone cannot: it is the control over what a cell was *placed*
to see, and a mis-provisioned cell that claims `forward` is precisely the case
where the placement is not what the record says. The two mechanisms are
complementary and neither substitutes for the other. The cert back-test's
scratch-tree cells have the timing half alone: no evaluator grades them, so
the only exposure record they leave is their own `flags.json` disclosures,
which the report carries and which exclude nothing (the `cert-backtest.json`
entry above states the direction).
