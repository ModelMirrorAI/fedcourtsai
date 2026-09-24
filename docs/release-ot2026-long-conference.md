# Release write-up: the OT2026 long conference

The skeleton and evidence plan for the project's first public release — the
long-conference cert write-up [milestones.md](milestones.md) calls Release 1.
It is the definition of done for the publication, written before its data
exists so the claims are bounded by the process rather than by what the numbers
turn out to be.

**Dates.** The conference sits 2026-09-28. The opening order list lands
~2026-10-05 and is the first realized outcome set. The write-up window is
~2026-10-05 → 10-20: evaluations drain as the order list is ingested, the
metrics refresh follows, and publication is last.

**Who runs what.** Every command below is the maintainer's, run after the order
list lands. Nothing here dispatches a workflow on an agent's behalf; the
dispatch lines are composed so a maintainer can run them verbatim.

## How to read this document

Each section carries three things: **State** — what the published write-up must
say; **Evidence** — the command or committed artifact that produces the number
or the finding; **Prose** — wording that is already settled, because it rests on
committed design rather than on unobserved data.

Every unfilled figure is a placeholder wrapped in single guillemets (U+2039 and
U+203A), and the sentence carrying it names the command that fills it. **No
placeholder is ever replaced by an estimate.** The draft is not publishable
while

```bash
grep -n "$(printf '\u2039')" docs/release-ot2026-long-conference.md
```

returns anything — the command is written with an escape so that it does not
match itself — and the same grep over the published draft is the last mechanical
check before the tag in the final section.

## 1. The counted population

**State.** Which cells the write-up counts, and why every other cell in `data/`
is outside it. The population is the `proc-v8` **full** freeze: the six blessed
digests in `FROZEN_PROCESS_DIGESTS` — three predictors and three evaluators —
with the counting instant `FROZEN_SINCE = 2026-09-16T00:26:04Z`. A cell counts
only if its **prediction's** stamp carries a blessed digest with `stamped_at` at
or after that instant, and the grading evaluation's own harness stamp is at or
after it too. The write-up states the per-digest census of the conference
cohort, not a stamped/unstamped split: an unstamped cell is shakedown by
construction, and a stamped cell under a retired digest is shakedown as well.

**Evidence.**

```bash
uv run fedcourts process-digest --all         # the live tree's digests
uv run fedcourts predict-plan | jq .counts.cell_ledger.would_mint_cells  # 0 = done
uv run fedcourts corpus-info                  # the vintage every count is read at
```

That command prints what the **current** tree resolves, which is only the
check being made when it is compared against `FROZEN_PROCESS_DIGESTS`; on a
tree that has moved past the freeze commit a difference means something moved,
not that the freeze is wrong. Say which comparison was run.

Per-digest census over the committed ledger, one digest at a time, in the form
the pre-registration record itself uses — over `origin/main`, because data
commits land there directly and never ride `staging`:

```bash
git fetch origin main
git grep -l '<digest>' origin/main -- data/cases | wc -l   # per blessed digest
git grep -l '"process_version": {' origin/main -- data/cases | wc -l  # all stamped
```

The object form on the second command is deliberate: a rewritten cell can carry
a `"process_version": null` key without a stamp.

After the metrics refresh in section 3, `metrics/leaderboard.json`'s
`frozen_process` block must read `since: 2026-09-16T00:26:04Z` beside those six
digests; a `since` naming any other instant means the board was built against a
different freeze and nothing may be quoted from it.

Cohort completeness is settled before the conference, not during the write-up
window: each predict tick parks on the review hold, and a hold is approved one
run at a time — a plan older than a day is stale (its already-predicted gate and
stranded-run guard were evaluated when it was minted) and is rejected and left
to re-derive rather than released.

Conditioning integrity for the cohort is the snapshot-uptake mark: a cell that
did not report reading its provisioned snapshot carries
`context.snapshot_uptake: unread` and a `flags.json` note beside it. It is a
self-report — `read` is the cell's own word, never verified uptake — so the
write-up reports how many counted cells carry `unread` rather than asserting
that every cell read what it was given.

**Prose.**

> The counted record for this release is the `proc-v8` process freeze. Six
> processes are blessed — one per predictor and one per evaluator — and the
> counting instant is 2026-09-16T00:26:04Z, the committed instant of the
> promotion merge that made those processes' bytes immutable on `main`. It sits
> *at* that merge in both directions, and each direction buys something. Behind
> the merge it would count cells against a commitment that was still editable
> when they ran, which is what pre-registration exists to rule out. Past the
> merge it would open a window in which a cell carries a blessed digest and
> still fails the counting rule on timing, so the backlog re-owes it and the
> event is paid for twice. At the merge, that window is zero-width.
> A prediction counts toward every figure below only if it was stamped under one
> of the three blessed **predictor** digests at or after that instant — the
> predictor is the competitor being ranked, so the predictor subset is the
> enforced membership filter and the evaluator's own digest is recorded rather
> than enforced — and only if the grading evaluation's own harness stamp is at
> or after that instant too. Everything else in the ledger
> stays committed, with its timestamps, and is excluded from every claimed
> result. Those cells exercised the pipeline while the process was still
> moving, and nothing about them was pre-registered.

> The conference cohort is re-forecast under the blessed processes by a
> registered backlog rule. The rule re-owes a cell on an event that is still
> genuinely forward, whose declared moment is still open, and whose entire
> committed cohort the freeze retired — cert distribution and CVSG moments plus
> the interim moments; a distribution is refused unless it carries a conference
> still ahead. The rule re-mints for every engine at once, so an event is never
> intended to be completed with one blessed cell standing beside de-counted
> rivals. That is the rule's intent and not a guarantee it can keep: the moment
> gate closes with the conference, and an event whose three cells are not all
> committed by then is left permanently mixed. Earlier
> cells are not edited, moved, or removed: each stays at its own run id, and the
> newest run per predictor is the one staged for grading and read by every
> board. A re-forecast supersedes; it never adds a second observation.

> Two readings that boundary does not support. A figure computed on the blessed
> side is not comparable with one computed on the retired side, and any rise
> across the boundary is **not** a measurement of model improvement — the two
> sides are different processes on different information sets, which is the
> whole reason the partition exists. And a cohort complete on the board is not
> the same as a cohort complete in fact: the rule's moment gate closes with the
> conference, so a cell that fails on the last tick before it cannot be
> re-minted afterwards. Where that leaves per-predictor cells over different
> event sets, the figure is published over the events carrying every blessed
> engine, or it prints the per-engine `n` and the complete-grid `n` beside it.

### Engine losses stay owed; they are not scored as failures

**State.** Which cells the engines did not produce, on which engine, and that
none of them is a result. No `prediction.json` or `evaluation.json` reaches the
counted ledger: output that failed validation or stopped early is routed to the
run's draft PR rather than collected, and a cell that produced nothing has
nothing to route. Either way the collect job commits one
`attempt.json` failure fact for it into the ledger, carrying the coarse triage
class the collect bucket implies — `no_output` (ran, produced nothing),
`partial` (output that failed validation or stopped early), `died` (queued but
never uploaded), overridden to `quota` where the cell's whole engine produced
zero cells that run. The backlog then re-derives the cell on the next round
until it lands or the per-cell attempt cap (`predict.max_attempts_per_cell`,
`evaluate.max_attempts_per_cell`) stops it. The count keys on cell identity
rather than process version, and is kept per (actor, event, seam), so an
exhausted cell never suppresses a sibling engine still owed the same event, and
the predict and evaluate seams count separately.

**Evidence.**

```bash
uv run fedcourts predict-plan  | jq '.counts.cell_ledger'  # what is still owed
uv run fedcourts evaluate-plan | jq '.counts.cell_ledger'
find data/cases -name attempt.json | wc -l                 # the failure facts
```

**Prose.**

> Where an engine produced no cell — a quota wall, a provider outage, a run
> that returned nothing — the cell is recorded as an attempt fact and stays
> owed: the backlog re-derives it from committed state on the next round. Such a
> cell is **not** a wrong forecast and is scored as nothing; a cell whose
> `correct` bit the harness could not compute leaves both halves of the accuracy
> fraction rather than entering it as a wrong call. It appears in this write-up
> as missing coverage, with the affected engine named, because a shorter grid on
> one engine changes the population that engine's figures are computed over. It
> never appears in an accuracy or Brier number.
>
> Where an engine leaves a graded population by exhausting its attempt cap
> rather than by design, that is stated too: the absence is attrition, and no
> evaluator-agreement or cross-engine figure may read it as a choice.

‹which engines lost which cells, and how many of each `error_class` — from the
committed `attempt.json` facts and the owed counts above›

## 2. Evaluations over the realized order list

**State.** That every counted prediction on the realized order list has been
graded by the enabled evaluators, and that the cohort's leakage findings have
been read. Which leakage surface is being read is named: the board's
`leakage_exclusion` block is the collapsed, frozen-scope, cohort-level count,
while the ops report's `leakage` digest is uncollapsed, all-versions and
window-scoped — deliberately version-blind, because surfacing shakedown
contamination is its job. The two answer different questions over different
populations and are never differenced.

Whether all grading of the list ran under one evaluator set is a **check**, not
a given: read the distinct evaluator digests off the counted gradings. If a
grading protocol boundary falls inside the window, any reasoning-quality or
evaluator-agreement figure spanning it is demoted to a coverage figure.

**Evidence.**

```bash
uv run fedcourts evaluate-plan | jq '.counts.cell_ledger.would_mint_cells'  # 0 ok
uv run fedcourts validate data                             # ledger consistency
jq '.leakage_exclusion, .forward_claim' metrics/leaderboard.json
```

The per-entry leakage grades sit on each `evaluation.json`'s `leakage` block.
The board's roll-ups are `forward_claim` (`policy`, `claimed_forward`,
`excluded`, `by_predictor`) and `leakage_exclusion` (`excluded`, `assessed`,
`by_predictor`).

**Prose.**

> Two exclusions apply to every scored figure here, and both are published with
> the numbers rather than described away from them.
>
> A cell whose record *claims* `forward` while its event had resolved strictly
> before the cell's harness clock day is not a forecast — its claim and its
> record contradict each other — and is excluded from every scored stratum under
> the registered policy. A same-day resolution is deliberately not a breach: the
> record cannot tell an honest forward cell that lost a same-day race from a
> mis-provisioned one, so the tie is read as retrospective and exclusion is kept
> for the unambiguous contradiction. The policy and the count are published in
> the board's `forward_claim` block.
>
> A cell whose grading carries the evaluators' leakage bit — true where the
> structured `leakage` block reads `influenced_prediction` as possible or likely
> — is excluded from every rank key and every scored aggregate. The bit says
> the graded prediction may have read its own outcome, which makes the cell an
> observation of no stratum. It changes membership, never value: no score is
> altered or reweighted, the cell simply is not counted. The unit is the
> grading, not the prediction, so a flag from one judge drops that judge's cell
> and leaves the prediction scored through the judges that did not flag it. A
> **null** bit means "not assessed", not "clean", which is why the published
> block carries `assessed` beside `excluded`: `excluded: 0` over a ledger of
> nulls reads as "nothing was checked".
>
> Both blocks are stage-blind and counted before the exclusion, so neither is a
> term in the board's arithmetic — `excluded` is not the missing term in
> `evaluations_total`, and `assessed` is not its denominator. They are an audit
> line about the pass. A cell both rules catch is counted in both, and the two
> counts are never summed. `superseded_gradings` reads the same way: it is not
> subtracted from any board count, and a board count plus it is not a ledger
> total.

> The per-predictor split counts **gradings, not predictions**: divide by the
> panel depth to recover predictions, and read a partial flag on one prediction
> as what it is — the panel disagreed about whether that cell read its own
> outcome, which is a question about the record that no aggregate here answers.

‹the two exclusion counts and their per-predictor split, and the distinct
evaluator digests over the counted gradings — from `metrics/leaderboard.json`
after the refresh in section 3›

## 3. Calibration against the registered base rates

**State.** How the cohort's forecasts compare with the baseline they were
anchored on, on the per-band cut, at a stated corpus vintage and against a
stated statpack build.

The anchor is the **registered segment base rate by salience band** under the
active scorer — the risk-set (`reached`) rate pooled over
`base_rate_lookback_terms` excluding the cell's own Term, which is what the
predict prompt anchors on and what the evaluator scores skill against. It is
**not** the whole-docket per-Term cert rate: that rate is wrong for this cohort
by 3–10x and may not be used for it. The per-Term section may appear as context
only, in a sentence that says it is not this cohort's anchor. The statpack's
terminal-composition table is a third vocabulary and is not the floor either.

**Evidence.** The boards must be rebuilt after the cohort's gradings land, or
every figure is quoted off a stale pack:

```bash
# maintainer dispatch, after the order list is ingested and graded
gh workflow run run-analytics.yml --ref main -f mode=metrics-refresh
```

The order inside that job is load-bearing and the dispatch does it correctly:
the statpack regenerates before the board, because the board scores its
realized-Term skill column against the committed pack. Then read the refreshed
artifacts:

```bash
jq '.process_scope, .frozen_process, .salience_versions' metrics/leaderboard.json
jq '.entries[] | {predictor_id, events_scored, evaluators}' metrics/leaderboard.json
jq '.stages' metrics/leaderboard.json                      # unranked moment blocks
# the per-band forward cut, ranked board then the CVSG arm
BAND='{events_scored, evaluations, accuracy, accuracy_scored, always_deny_accuracy, accuracy_lift, population_brier_skill_score, skill_scored, grants_realized, grants_expected, grants_expected_scored}'
jq ".entries[] | {predictor_id, evaluators, by_band: ((.by_band // {}) | map_values($BAND))}" metrics/leaderboard.json
jq ".stages[\"cert@cvsg\"].entries[]? | {predictor_id, evaluators, by_band: ((.by_band // {}) | map_values($BAND))}" metrics/leaderboard.json
sed -n '/Segment base rate by salience band/,/^## /p' metrics/statpack.md
```

**Prose.**

> Every figure below is built at `process_scope: "frozen"`. The `--all-versions`
> board exists and is a diagnostic view; nothing from it is quoted here.
>
> The baseline is the registered per-band risk-set rate under the active
> salience scorer, and the always-deny floor a figure is read against is its
> own band's. On the committed pack those floors are 94.98% baseline, 83.11%
> elevated, 64.49% high, 29.21% federal and 76.37% state, counting the whole
> grant family, GVRs included, because that is what the board scores. On that
> anchor the cohort's band-mix-implied grant rate is about 10.1% over the 110
> cert/distribution events — about 17.8% over the selected subset and 5.8% over
> the declined remainder — and about 12.2% over all 120 cert-stage events once
> the CVSG arm is folded in. A whole-docket cert rate of 1–3% is the wrong
> anchor for this cohort and is not used as one anywhere in this write-up.
>
> Every figure is read on the **per-band cut**, never as a single pooled row,
> and each number travels with four things in its own sentence: the band's `n`,
> the always-deny floor, the **lift over that floor**, and the stratum. The
> floor a lift is measured against is the one **realized on the same
> gradings** — what a constant `denied` call scored on exactly the cells the
> accuracy averages — while the registered historical floors above stay the
> skill anchor and are shown beside it, never subtracted from. An accuracy
> near its band's floor is the floor, not performance — a predictor that
> denies everything scores the denial rate — so accuracy is never published
> without its floor beside it, and never without `accuracy_scored`, which is
> its true denominator. Accuracy and the floor are averaged over gradings, one
> per judge, so they are weighted by panel depth, while a band's `n` counts
> petitions. A skill figure travels with `skill_scored`,
> which can sit far below the block's evaluation count because a cell scores
> skill only where a segment base rate exists, and the estimator is named:
> the population skill score is a ratio of sums and the mean Brier is a
> per-cell mean, and under cert's class imbalance the two are not
> interchangeable.
>
> The **high band is n = 1 on cert/distribution and n = 10 on cert/cvsg**,
> n = 11 across the cert stage, and the two moments are never pooled. The
> distribution arm is the ranked board, so a high-band claim there is a claim
> over one event; the cohort's high band actually sits in the CVSG arm, which
> reports in its own unranked block and is never blended into the ranking. The
> two interim events carry no salience-band base rate at all — an interim cell
> is scored against the interim rate with a null basis — so they sit outside
> every band figure.
>
> Two things about the pool travel with any rate quoted from it. The lookback
> window (`salience.base_rate_lookback_terms`) is a registered choice, not a
> neutral fact: per-Term high-band rates
> range widely within it and readings taken across a change to that window are
> not comparable, so the window is stated with the figure. And a statpack cert
> figure is a denial-reweighted estimate of a population rather than a count of
> rows, which the pack marks and which the sentence carrying it repeats.
>
> If the board's `salience_versions` lists more than one version, the ranked
> cells' baselines were read under two differently-gated populations: the means
> are then coverage figures, not skill, and are published as such. A cell whose
> frozen band's version does not resolve against the pack carries no baseline
> at all — its skill column is empty, not zero, and supports no claim.

‹per predictor and per band, over the forward stratum — from the `by_band`
block of each entry in `metrics/leaderboard.json` after the refresh above, and
of each `cert@cvsg` stage entry for the CVSG arm: `events_scored` (petitions);
`accuracy` with `accuracy_scored` (gradings) and the entry's `evaluators`
(panel depth); the **realized** always-deny floor `always_deny_accuracy` and
the lift over it, `accuracy_lift`; population Brier skill (a ratio of sums),
`population_brier_skill_score`, with `skill_scored`; and `grants_realized`
against `grants_expected` over `grants_expected_scored` events. The registered
historical floors (94.98% / 83.11% / 64.49% / 29.21% / 76.37%) stay the skill
anchor and are shown beside each row; they are not the floor the lift is
measured against. The `(none)` key holds cells whose prediction froze no band
and is reported as its own row, never folded into a band›

‹the per-band always-deny floors as the refreshed pack publishes them — from
`metrics/statpack.md`, *Segment base rate by salience band* — re-read rather
than quoted from an earlier build, and reconciled against the registered values
in [freeze-record.md](freeze-record.md) and
[metrics/README.md](../metrics/README.md)›

‹the whole-docket per-Term cert rate, quoted as context only and labelled as
not this cohort's anchor — from `metrics/statpack.md`, *SCOTUS cert petitions
by Term*›

Guards that decide whether a number may be quoted at all, checked before any
figure leaves this section:

- A merits or interim skill figure exists only where the pooled prior-Term
  sample clears its floor; below it there is no baseline, no skill score, and no
  substitute rate. A null skill with `skill_scored: 0` is reported as such.
- **Quote nothing from a null-guard merits section.** Where a statpack merits
  section's guard count is null, the pack predates the guard and its figures
  carry whatever contamination the guard would have removed.
- Non-cert stage blocks report the realized-Term skill null with a zero count by
  construction: only the cert segment has a salience band whose realized rate the
  pack publishes.

### Comparing the engines

**State.** What the cross-engine ranking is and is not. This is the claim the
release will be read for, so the rules travel with the board rather than behind
it.

**Evidence.** Per entry: `events_scored`, each stratum's `evaluations`, and the
entry's `evaluators`; and the population's own `events_scored` union.

**Prose.**

> The scored set is **selected, not sampled**. Grading is gated per judge and
> per event, so a prediction committed after a judge has already graded its
> event is never scored by that judge, and an engine whose cells land late
> accumulates fewer scored events than one that ran on time. Nothing in the
> ranking or either skill column adjusts for that. So every rank is published
> with each engine's `events_scored`, the complete-grid `n` beside it, each
> stratum's evaluation count and the entry's panel depth. Entries are never
> summed to recover the population's coverage: two predictors scored on one
> event are one event.
>
> Equal coverage is necessary and not sufficient. It certifies the same event
> set and nothing else: two entries at equal coverage can differ in stratum mix
> or in panel depth, and either makes the means differently weighted. A forward
> comparison is made only where both entries carry a forward block over the same
> events.
>
> The ranking is on N-unweighted point estimates over a cohort whose band mix
> implies roughly a dozen grants. A one- or two-event difference reorders it.
> The order is therefore reported as locating a difference between the engines,
> not as measuring one.

‹each engine's `events_scored`, complete-grid `n`, per-stratum evaluations and
panel depth — from `metrics/leaderboard.json`›

## 4. The salience limitation

**State.** What "the most salient petitions" may and may not mean here, under
the active scorer `sal-v4`. Two things, and they are different claims.

The **trajectory score** turns on two primary signals, relist count and CVSG,
and both are docket-acquired. A petition at arrival, or at its first
distribution, carries relist-0, and — absent a CVSG, whose own limb lands it in
`high` outright — its score cannot reach the `elevated` cutpoint; the circuit
term is a bounded nudge that can never move a band or clear the always-include
floor. So a salience claim made off the *escalation*
stream holds for the relisted / CVSG population and not for the
first-distribution bulk.

That is a limit on the score, not on the band vocabulary. Under the active
caption-banded scorer, `federal` and `state` are read off the caption, which is
fixed at filing, and both sit above `elevated`. So a petition can be banded
above elevated at arrival by **class** while no trajectory score there can
reach elevated, and the two statements are about different things.

The **arrival cohort** is not selected by that score at all. It is two named
rules — a keyed-hash draw over the case id at the registered sample rate, plus
the federal-petitioner carve-in under the active caption rule — and their
populations have grant rates an order of magnitude apart, so they report
separately, always. The leaderboard's `cert@arrival` block pools them
mechanically, so its pooled accuracy and mean Brier are **not claimable**
without the per-rule cut. Per-band skill stays honest, because the band
separates the two populations: `federal` is the carve-in class, everything else
is the draw's mix. Only the draw's skill transfers to live prospective use, and
it is a mixture over class floors rather than a single unconditional rate.

**Evidence.** `docs/salience.md` is the registered design. The version each cell
was banded under is frozen on the prediction as `context.salience_version` and
recorded on the grading as `base_rate_salience_version`, which is what makes a
cross-version reading visible after the fact.

```bash
jq '.stages' metrics/leaderboard.json                      # unranked moment blocks
uv run fedcourts caption-census --rule-version caption-v2  # the carve-in class
```

**Prose.**

> Salience here is a scored, pre-registered ranking; it is not a claim that this
> cohort is the term's most consequential petitions. The trajectory score turns
> on signals a docket acquires over time, so it says little at a petition's
> arrival: at relist-0 no score reaches the elevated cutpoint, and the circuit
> term is bounded too small to carry a petition across a boundary. Band is a
> separate matter — the federal and state classes are read off the caption at
> filing and sit above elevated — so the two are never conflated. The ranking
> claim in this write-up is about the relisted and CVSG population, which is
> what the conference cohort's forecast moments are.
>
> Selection at arrival is a separate mechanism with a separate claim rule: two
> rules, a keyed random draw and a federal-petitioner carve-in, whose grant
> rates differ by an order of magnitude. Any figure that pools them is not
> claimable, so no pooled arrival number appears here; where an arrival figure
> is quoted it is cut per rule, or read per band, and only the random draw's
> skill is described as transferring to prospective use. An arrival cell minted
> before the first statpack rendered under its salience version carries no
> baseline at all: its skill column is empty, not zero, and supports no claim.
>
> A band label means something only under the function that assigned it. Every
> banded figure names its scorer version, and no per-band figure is compared
> with one produced under another version: a non-active version's published
> baseline is that version's band rule applied over the active parse's counts,
> so a cross-version skill comparison reads through a substitution and has to
> say so.

‹the per-rule cut of any arrival figure quoted — draw subcohort vs carve-in
subcohort, read per band off `metrics/leaderboard.json`'s `cert@arrival` block›

## 5. Cohort provenance

**State.** What the counted cohort is, where it came from, and what it is not.
Its size and composition are **pre-registered** — fixed in the freeze record
before any of its outcomes existed — so they are quoted from that record, not
re-derived from the graded board. The graded composition is published beside
the registered one as a reconciliation, with any delta explained; re-deriving
the population from what got graded would quietly substitute "what was scored"
for "what was predicted", and the per-judge grading gate is exactly why those
differ.

**Evidence.** The registered table and the overhang figure are in
[freeze-record.md](freeze-record.md), in the entry registering this cohort;
[metrics/README.md](../metrics/README.md) carries the same population and its
reading rules. Those are the sources for the population — not a command. What
the commands give is the counted side, read against it:

```bash
uv run fedcourts corpus-info                       # the vintage counts are read at
uv run fedcourts predict-plan | jq '.counts.provenance'  # cases and events covered
jq '.events_scored, .entries[].events_scored' metrics/leaderboard.json
```

`fedcourts unlatch-overselected` is **not** the source for the overhang, and
running it in the write-up window would mislead: its dry run scans **pending**
cohorts only, so once the order list has resolved this conference it reports on
other, still-pending conferences and says nothing about this one. Its ledger is
a live reading available only before the conference, and it carries no
floor breakdown in any case.

The `--apply` form is a writer-lane dispatch and a recorded operational
decision. It is **not** run for this release: clearing the latch under the
active scorer would also de-select pending petitions the current distribution
parse demoted, which is a selection change the write-up has no licence to make
after the fact.

One conditional re-measurement: if any tick of the pre-conference drain did not
run, the surviving cohort is **not** a random subset of the registered table.
The drain is ordered stalest-queue-stamp first and poll recency correlates with
salience, so a partly-drained cohort is the head of a recency-ordered queue and
band-biased. In that case the band mix is re-measured at the conference and the
**re-measured** table is what every figure is read against.

**Prose.**

> The cohort is the still-forward residue of earlier funded rounds, re-forecast
> under the blessed processes. Its composition was registered before any of its
> outcomes existed: 110 cert/distribution events — 1 high, 37 elevated, 70
> baseline, 1 federal, 1 state — with 10 cert/cvsg events, all high band, and 2
> interim events beside them.
>
> It is not the conference. 557 SCOTUS petitions are distributed for the
> conference and 180 of them are in predict scope; the cohort is 110 of those
> 180 — every elevated, high and federal petition in scope, but only 70 of 138
> baseline and 1 of 3 state. It is therefore **selected upward on band**: 63.6%
> baseline against the in-scope conference's 76.7% and the distributed set's
> 87.8%, which is why its band-mix-implied grant rate runs about 1.2x the
> in-scope conference's and 1.5x the distributed set's. No figure over this
> cohort is a figure about the conference, about the docket, or about a random
> sample of either.
>
> Selection is per conference and capacity-bounded, with the long conference
> carrying double a regular conference's budget, and two things sit above that
> budget by design: CVSG petitions and anything at or above the documented
> salience floor, so a major case can never fall below the capacity line.
> Selection is additive above the budget and the latch is one-way — a selected
> case stays selected, because de-selecting it would retroactively withdraw a
> case the pipeline had already committed to forecasting — so the realized
> selection runs above capacity and the routine pass can never shrink it. The
> one command that would is a deliberate maintainer act and is not run here.
>
> **39** of the 110 cert/distribution events are on cases the current round
> selected against a long-conference capacity of 24, and the overhang is kept
> and disclosed rather than cleared. Disclosure alone does not say which way it
> moves, so: the 15 events above capacity are the **rank tail** — the
> lower-salience end of the selected set — so that subset's implied grant rate
> sits **below** what a capacity-24 selection would give. Any figure over the
> selected subset carries the denominator **n = 39** and is **not** compared
> with a capacity-N salience replay, which is a different population. A figure
> over all 110 is not a selection at all: it carries no overhang, and its
> denominator is 110.

‹the graded cohort's size and composition, reconciled against the registered
table above, with any delta explained — from `metrics/leaderboard.json`›

‹the re-measured band mix, if any tick of the drain did not run — from the
committed cells at the conference›

## 6. Scope rules: every number names its population

**State.** That each published figure carries its stratum, its stage and moment,
its process scope, and its population — in the sentence that carries the number,
not a section away. [metrics/README.md](../metrics/README.md) is the registered
contract; this section is the checklist applied to the draft.

**Evidence.** A read-through of the draft against `metrics/README.md`, plus:

```bash
jq '.process_scope, .frozen_process, .forward_claim, .leakage_exclusion' \
  metrics/leaderboard.json
jq '.process_scope' metrics/claim-scores.json
```

**Prose — the rules the draft is checked against.**

- **Stratum.** Only the **forward** stratum is evidence of forecasting skill.
  Retrospective cells measure calibration and label fit; procedural cells —
  mootness practice — are reported per predictor and never ranked. No headline
  number mixes strata, and an unstated stratum makes a census unreadable.
- **Stage and moment.** The ranked board is the cert stage's first declared
  moment. Interim, merits, later cert moments and the stage-less bucket each
  report their own unranked block, keyed `<stage>@<moment>`, and never blend.
- **Process scope.** Frozen only. The `"all"` board is diagnostic.
- **Backtests are never claimable.** Replays and the backtest artifacts are
  iteration instruments — for tuning prompts, retrieval and calibration — and
  the project claims results only from genuine forward predictions. A replay
  cell's grades are never claimable at all: its opinion is public, so the claim
  is retrievable rather than forecastable.
- **Semantic grades.** The semantic family publishes its ground split as an
  **availability** mask, never as skill, never as one pooled total, and never
  beside a mechanical claim score. Agreement is published beside every grade or
  the grade is not published.
- **QP topics.** No topic distribution may be quoted until a labels artifact
  exists. A labeling run's agreement rate is agreement with the adjudicated,
  agent-built reference set — every rater was an agent session, so it partly
  measures shared convention — never accuracy.
- **Null guards.** Any section whose guard count is null is not quoted from.
- **Empty is a state, not a zero.** A board with nothing in frozen scope renders
  its empty state and names the condition that empties it; a suppressed stratum
  carries null coefficients rather than zero-filled ones, and an omitted stage
  section is omitted rather than emitted as null. None of those supports a
  claim, and none of them is reported as a result of zero.
- **Corpus vintage.** Every corpus-derived statement names the vintage it was
  read at, from `fedcourts corpus-info`; a claim about one case quotes that
  case's own `last_pulled`.
- **Denominators.** Accuracy travels with `accuracy_scored`, its band's floor
  and the lift over it; skill travels with `skill_scored`; a rank travels with
  each engine's `events_scored`, the complete-grid `n`, the stratum's
  evaluation count and the panel depth. A per-band table without `n` is not
  reviewable and is not published.
- **Surfaces this write-up does not claim from.** The claim-score board is
  advisory and never a rank key; the board's `big_case` and
  `evaluator_agreement` views and `big-cases.json` read the ledger by their own
  path, so **neither exclusion applies to them** and a leakage-flagged cell is
  still a point there; the realized-Term skill column is ex post and never a
  rank key, and an open Term's value is grant-depleted and directional only;
  the tool-usage and retrieval figures are a declared superset whose
  denominators are not comparable across engines. Any of these that is quoted
  is quoted with its own caveat, or it is declared out of scope and left out.

## 7. The `stats-reviewer` pass

**State.** That the full figure set — not the diff — was reviewed before
publication, and what the reviewer found. This is the last check before the tag.

**Evidence.** Run the `stats-reviewer` subagent over the finished draft with its
numbers filled — the figure set **with its denominators**, since a per-band
table without `n` cannot be reviewed — and record its verdict and the
disposition of each blocker. A blocker is fixed or rebutted in writing; an
unanswered blocker is not a resolution.

‹the reviewer's verdict and the disposition of each finding›

## 8. The publishing tag

**State.** That the published figures correspond to an exact commit on `main`.

**Evidence.** Two tags precede this one in the same cycle: the promotion tag for
the batch carrying the freeze, and the annotated `prereg/proc-v8` tag that
pre-registers the blessed digests and the counting instant. The results tag goes
on the commit carrying the published metrics refresh:

```bash
git tag -a results/ot2026-longconf -m "OT2026 long-conference cert release" <sha>
git push origin results/ot2026-longconf
```

Minting it is a maintainer step, like the promotion merge it accompanies. The
`results/` namespace blocks update and deletion, so the tag is minted only once
the draft's placeholder grep in *How to read this document* returns nothing and
the `stats-reviewer` pass in section 7 is resolved.
