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

**The public page.** [release-ot2026-public-summary.md](release-ot2026-public-summary.md)
is the reader-facing layer: it copies its figures from this document once filled,
adds none of its own, and yields to this document on any disagreement.

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

**Sensitivity lines.** Some figures carry a sensitivity line beside them: the
same figure recomputed with one disclosed departure from the registered
computation. A sensitivity line is a disclosure, never a result. The registered
figure is the headline, every rank and claim is read off it alone, and the line
shows how far that one departure would move it. Each line varies one thing
against the registered figure; lines are never stacked into a second headline.
Their placeholders name the **release sensitivity command**, a read-only
analysis over the committed gradings, the statpack builds and the corpus that
prints each sensitivity block beside the registered headline it varies, with the
corpus vintage, the ledger commit and every statpack build it read:

```bash
uv run fedcourts release-sensitivity --registered-at 2026-09-15 \
  --grant-list 2026-10-01 > sensitivity.json
jq '.ledger, .corpus, .payloads_read, .fill_statpack, .conference_fallbacks' sensitivity.json
jq '.registered_headline.matches_committed_board' sensitivity.json  # must be true
```

It rebuilds the frozen board exactly as `fedcourts leaderboard` does, so
`registered_headline.figures` is the board's own cert arms, keyed
`<stage>@<moment>` (`cert@distribution` is the ranked board, `cert@cvsg` the
CVSG arm), and `matches_committed_board` says whether the committed
`metrics/leaderboard.json` is that board. Each block under `.blocks` carries
its figures in the same shape, each with its own `n`. It is run from the same
checkout and corpus as the fill export (section 8, step 2), with full git
history (the anchor block reads the statpack each grading's checkout carried)
and the content store wired (the other two read the stored live snapshots), so
its figures and the board's are read off one ledger.

## 1. The counted population

**State.** Which cells the write-up counts, and why every other cell in `data/`
is outside it. The population is the `proc-v8` **full** freeze: the six blessed
digests in `FROZEN_PROCESS_DIGESTS` — three predictors and three evaluators —
with the counting instant `FROZEN_SINCE = 2026-09-16T00:26:04Z`. A cell counts
only if its **prediction's** stamp carries a blessed digest with `stamped_at` at
or after that instant, and the grading evaluation's own harness stamp is at or
after it too. In the code's terms that is `proc-v8`'s three open counting
windows in `COUNTING_WINDOWS`, one per predictor digest, each opening at that
instant; while they are the only windows, the two readings select the same
cells. The write-up states the per-digest census of the conference
cohort, not a stamped/unstamped split: an unstamped cell is shakedown by
construction, and a stamped cell under a de-counted digest is shakedown as well.

**Evidence.**

```bash
uv run fedcourts process-digest --all         # the live tree's digests
uv run fedcourts corpus-info                  # the vintage every count is read at
```

That command prints what the **current** tree resolves, which is only the
check being made when it is compared against `FROZEN_PROCESS_DIGESTS`; on a
tree that has moved past the freeze commit a difference means something moved,
not that the freeze is wrong. Say which comparison was run.

Cohort completeness is read off the cohort cut section 5 builds, against the
plan:

```bash
uv run fedcourts conference-set --counted --registered-at 2026-09-15 > cut.json
jq '.conference_fallbacks' cut.json           # fallbacks: must be 0
uv run fedcourts predict-plan > plan.json
jq -n --slurpfile cut cut.json --slurpfile plan plan.json '
  [$cut[0].events[] | select(.registered) | "\(.case_id) \(.event_id)"] as $cohort
  | {minted: [$plan[0].would_mint[] | "\(.court)/\(.docket) \(.event_id)"],
     withheld: [$plan[0].withheld_stranded[] | "\(.case_id) \(.event_id)"],
     deferred_cases: $plan[0].deferred_by_cap.cases}
  | {minted: [.minted[] | select(. as $k | $cohort | index($k))],
     withheld: [.withheld[] | select(. as $k | $cohort | index($k))],
     deferred_cases: [.deferred_cases[]
       | select(. as $c | $cohort | map(startswith($c + " ")) | any)]}'
                                              # owed: every list empty
jq '[.events[] | select(.registered) | select(.predictors | length < 3)
  | {case_id, event_id, predictors, status}]' cut.json   # short of the full grid
```

The plan's own `would_mint_cells` is backlog-wide, so during the write-up window
it counts cells owed on later conferences and rarely reads 0. The *owed* command
narrows the plan to the cohort's own events — matched on case **and** event, so
a later event on a cohort case does not count — across the cells this round
would mint, the cells the stranded guard withheld, and the cases the volume cap
deferred (case grain, which is all the plan records for them). The *short of
the full grid* command lists every cohort event with fewer than three counted
predictors, including a registered event no engine produced a counted cell for,
which the cut lists with no predictors and the status `unforecast` rather than
leaving out. Such an event has an incomplete grid, and the complete-grid rule
in the prose below applies to it. Neither result is guaranteed to be empty: the
distribution moment closes with the conference, but the CVSG and interim
moments do not, and an event the registered rule re-owed but no engine ever
forecast stays short for good.

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
digests, and its `windows` must list exactly the three `proc-v8` predictor
windows opening at that instant with null `closes`; a `since` naming any other
instant means the board was built against a
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
> committed cohort the freeze de-counted — cert distribution and CVSG moments plus
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
> side is not comparable with one computed on the de-counted side, and any rise
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

The board carries the six frozen digests, not the digests the counted gradings
were actually stamped under, so the evaluator-set check reads the fill export's
gradings table (section 8, step 2), where `counted` and `process_digest` sit on
every row:

```bash
python3 -c 'import csv, collections, sys
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["counted"] == "true"]
print(len(rows), collections.Counter((r["evaluator_id"], r["process_digest"]) for r in rows))' \
  <fill-dir>/gradings.csv
```

One digest per evaluator means one evaluator set graded the list; a second
digest under any evaluator is the protocol boundary the state above names.

‹the two exclusion counts and their per-predictor split — from
`metrics/leaderboard.json` after the refresh in section 3 — and the distinct
evaluator digests over the counted gradings, from the command above›

## 3. Calibration against the registered base rates

**State.** How the cohort's forecasts compare with the baseline they were
anchored on, on the per-band cut, at a stated corpus vintage and against a
stated statpack build.

The anchor is the **registered segment base rate by salience band** under the
active scorer — the risk-set (`reached`) rate pooled over
`base_rate_lookback_terms` excluding the cell's own Term, which is what the
predict prompt anchors on and what the evaluator scores skill against. "Own
Term" is the **docket-number** Term the prediction froze (`context.term`), not
the Term the conference sits in, so the anchor is a function of the docket Term:
a `25-` petition decided at the OT2026 long conference pools the Terms before
OT2025. Skill is computed against the `segment_base_rate` each grading records,
which is the evaluator's own pooling of that window's statpack rows. It is
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
BAND='{events_scored, evaluations, mean_depth: (if .events_scored > 0 then .evaluations / .events_scored else null end), accuracy_events_scored, event_accuracy, event_always_deny_accuracy, event_accuracy_lift, accuracy, accuracy_scored, always_deny_accuracy, accuracy_lift, population_brier_skill_score, skill_scored, grants_expected, grants_expected_scored, grants_realized_expected_scored, grants_realized}'
jq ".entries[] | {predictor_id, evaluators, by_band: ((.by_band // {}) | map_values($BAND))}" metrics/leaderboard.json
jq ".stages[\"cert@cvsg\"].entries[]? | {predictor_id, evaluators, by_band: ((.by_band // {}) | map_values($BAND))}" metrics/leaderboard.json
jq '.complete_grid_by_band, .stages["cert@cvsg"].complete_grid_by_band' metrics/leaderboard.json
# the pooled per-band anchors, per docket Term (risk_set is the frozen-band anchor)
uv run fedcourts segment-anchors --term 2025 --term 2026
sed -n '/Segment base rate by salience band/,/^## /p' metrics/statpack.md   # per-Term rows behind them
```

`segment-anchors` pools through the scorer's own pooler over the committed
pack, under the configured lookback, and prints each anchor with the Terms it
pooled and its weighted `n`. The cohort's cert cells froze docket Terms 2025
and 2026 only, so those two `--term` values cover it. If the board or a
grading names another Term, add it.

**Prose.**

> Every figure below is built at `process_scope: "frozen"`. The `--all-versions`
> board exists and is a diagnostic view; nothing from it is quoted here.
>
> The baseline is the registered per-band risk-set rate under the active
> salience scorer, pooled over the Terms before each petition's own **docket**
> Term. About 108 of the 110 registered cert/distribution events, and all 10
> CVSG events, were docketed in OT2025. For those petitions the committed pack
> gives 5.12% baseline, 17.22% elevated, 34.97% high, 72.93% federal and 22.70%
> state, pooled over OT2017–OT2024. The pack starts at OT2017, so the ten-Term
> lookback reaches back eight Terms here. These count the whole grant family,
> GVRs included, and they are the skill anchor. Petitions docketed in OT2026
> pool OT2017–OT2025 instead: 5.02% / 16.89% / 35.51% / 70.79% / 23.63%.
> Those apply to OT2026 dockets only. Their pool includes the OT2025 row, which
> is still resolving, so they move with each pack build and are quoted with
> the build.
> Each grading's skill is computed against the rate it records, which is the
> evaluator's own pooling of the statpack's prior-Term rows. Judges differ in
> the fourth decimal: pooling the table's rounded rows gives 0.17238 elevated,
> the pack's exact counts 0.17224.
>
> That recorded rate is the judge's transcription, not a harness stamp, and the
> registered computation scores skill against it as recorded. The board's only
> check on it is self-consistency — the recorded rate, Brier and skill agree
> with one another — and nothing compares the rate with the pool it was read
> from. So the write-up measures the transcription instead of assuming it: for
> each judge, over the graded cert cells behind the board's skill figures, the
> deviation of every recorded `segment_base_rate` from the exact pool
> `fedcourts segment-anchors` computes for the scored prediction's docket Term
> and band, given as the largest and the mean relative deviation and the count
> above 1%. The exact pool is computed from the statpack build the grading
> itself read — the pack committed when it was graded — not from the pack at
> fill time: the OT2026-docket pool includes a still-resolving Term and moves
> with each build, so a fill-time pool would fold build drift into what is
> reported as transcription. Beside each headline skill figure sits a
> sensitivity line with skill recomputed against that exact pool. The
> registered figure stays the headline; the line shows how much of it the
> transcription could account for.
> The complements of these rates are grant-family denial shares, not
> exact-match always-deny floors, and no lift in this write-up is measured
> against them. Taking the OT2025-docket rates for all 110 events, the
> cohort's band-mix-implied grant rate is about 10.2% over the 110
> cert/distribution events — about 18.2% over the selected subset (n = 39) and
> 5.9% over the declined remainder (n = 71) — and about 12.3% over all 120
> cert-stage events once the CVSG arm is folded in. The two OT2026 dockets move
> the 110-event figure by under a hundredth of a point. The freeze record's
> correction entry carries these figures; the 2026-09-15 entry's ~10.1%,
> ~12.2%, ~17.8% and ~5.8% were computed on the OT2026-docket rates. A
> whole-docket cert rate of 1–3% is the wrong anchor for this cohort and is
> not used as one anywhere in this write-up.
>
> Every figure is read on the **per-band cut**, never as a single pooled row,
> and each number travels with four things in its own sentence: the band's `n`,
> the always-deny floor, the **lift over that floor**, and the stratum. The
> floor a lift is measured against is the one **realized on the same cells** —
> what a constant `denied` call scored, under the exact-match rule, on exactly
> the petitions the accuracy covers — while the registered band rates above
> stay the skill anchor and are shown beside it, never subtracted from. An
> accuracy near its band's floor is the floor, not performance — a predictor
> that denies everything scores the denial rate — so accuracy is never
> published without its floor beside it, and never without its denominator.
> The band figures are **per petition**: `event_accuracy`,
> `event_always_deny_accuracy` and `event_accuracy_lift` count each event once
> over `accuracy_events_scored`. The grading-weighted `accuracy` /
> `always_deny_accuracy` pair is weighted by panel depth, which varies by
> design, and is shown only beside the band's mean depth (its `evaluations`
> over its `events_scored`), never in place of the per-petition figures. A
> skill figure travels with `skill_scored`,
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
the per-petition `event_accuracy` over `accuracy_events_scored`, with the
**realized** always-deny floor `event_always_deny_accuracy` and the lift over
it, `event_accuracy_lift`; beside them the grading-weighted `accuracy` with
`accuracy_scored` (gradings), `always_deny_accuracy` and `accuracy_lift`, and
the band's mean panel depth, `evaluations / events_scored` (the entry's
`evaluators` is the panel size, not per-event depth); population Brier skill
(a ratio of sums), `population_brier_skill_score`, with `skill_scored`; and
`grants_realized_expected_scored` against `grants_expected` over the same
`grants_expected_scored` events; and per band the complete-grid count,
`complete_grid_by_band[band]` on the board (and on the `cert@cvsg` stage block
for that arm). The grant comparison carries its censoring
caveat in its own sentence: relisted and held petitions are still pending and
grant more often than the ones already decided, so while they pend realized
runs below expected, and a shortfall is not yet evidence of miscalibration.
Each band's anchor stays the skill anchor and is shown beside its row, named
by docket Term: 5.12% / 17.22% / 34.97% / 72.93% / 22.70% for OT2025 dockets
and the OT2026-docket pool 5.02% / 16.89% / 35.51% / 70.79% / 23.63% for
OT2026 dockets, each re-read off the refreshed pack, with the row's count of scored
events per docket Term (the scored predictions' `context.term`) beside them.
Post-freeze additions graded onto the board are mostly OT2026 dockets, so a
row's docket-Term mix is counted at release time, never assumed.
Their complements are grant-family
denial shares, not exact-match floors, and are not the floor the lift is
measured against. The `(none)` key holds cells that froze no band, froze a
band with no version, or carry no band facts, and is reported as its own row,
never folded into a band›

‹the per-band grant-family rates (the skill anchor) per docket Term, as the
refreshed pack pools them — the `risk_set` figures from `fedcourts
segment-anchors --term 2025 --term 2026`, each with its pooled Terms and
weighted `n`, re-read rather than quoted from an earlier build. Reconcile them
against the figures quoted in [metrics/README.md](../metrics/README.md) and
the freeze record's correction entry for this cohort's anchor
([freeze-record.md](freeze-record.md)), and state which docket Term each quoted
rate is for›

‹the transcription spread, per judge and per docket Term, over the same
skill-scored cert cells the sensitivity line below recomputes, and separately
over the registered cohort's graded cert cells: the cell count, how many
recorded the exact pool, the largest and the mean relative deviation of the
recorded `segment_base_rate` from the exact pool of the statpack build the
grading read, and how many cells deviate by more than 1% — re-measured over
the full graded set at fill time, from `release-sensitivity`'s
`.blocks.exact_pool_anchor.transcription_spread` — its
`skill_scored_cert_cells` and `registered_cohort_graded_cert_cells`, each
`by_judge` with `by_docket_term` inside, reading `cells`, `exact` (equal to
six decimals), `faithful_rounding` (equal to the exact pool rounded to the
recorded rate's own decimals; judges record from four decimals up),
`max_relative_deviation`, `mean_relative_deviation` and `over_one_percent`,
with the builds read in `.blocks.exact_pool_anchor.statpack_builds`; the cohort's `unanchored` list and
the block's `recorded_retained` list must both be empty (each entry carries
its `reason`; "build not readable" usually means the clone lacks the grading's
`pipeline_sha`, so fetch it and re-run)›

**Sensitivity lines beside the headline.** Three sensitivity lines travel with
the per-band figures above, each in the sentence that carries its registered
figure and each with its own `n`. The first is this section's; the other two
are disclosed with the cohort in section 5.

‹per predictor and per band, population skill recomputed with each cert
grading's baseline taken from the exact pool of the statpack build it read
instead of its recorded `segment_base_rate`, beside the registered `population_brier_skill_score` and
over the same `skill_scored` cells — from `release-sensitivity`'s
`.blocks.exact_pool_anchor.figures`, beside `.registered_headline.figures`›

‹per predictor and per band, `event_accuracy`, `event_accuracy_lift` and
population skill with the extraordinary-writ petitions section 5 names removed
— every one on the board, in the cohort or not —
each with its reduced `n`, beside the registered figures — from
`release-sensitivity`'s `.blocks.rule_20_excluded.figures`, beside
`.registered_headline.figures`›

‹per predictor and per band, every board-wide figure in this section —
accuracy, floor, lift, skill, the grant comparison, `complete_grid_by_band`,
and each engine's `events_scored` in *Comparing the engines* below —
recomputed without the events section 5 names as first forecast after their
conference, each with its reduced `n`, beside the registered figures — from
`release-sensitivity`'s `.blocks.post_conference_first_forecasts_excluded.figures`,
beside `.registered_headline.figures`›

**A post-hoc benchmark, labelled as one.** One figure in this section is
neither registered nor a sensitivity line: Brier skill against each block's own
**in-sample grant rate** (`population_in_sample_skill_score`), defined after
the conference's outcomes were known. It scores every grading against the
share of granted outcomes among the block's own scored events, the case being
scored included, so it nets out the block's level and nothing finer — at
uniform panel depth it is (resolution − reliability) / uncertainty in the Murphy
decomposition against that rate — and no forecaster could have known its
baseline. The pooled `forward` figure spans the salience bands, so it credits
separating the bands as well as separating cases within one; the within-band
reading is the `by_band` cell, where it is defined. It is read off the same
refreshed board:

```bash
jq '.entries[] | {predictor_id, forward: (.forward | {in_sample_events_scored, in_sample_grant_rate, population_in_sample_skill_score, in_sample_skill_scored}), by_band: ((.by_band // {}) | map_values({in_sample_events_scored, in_sample_grant_rate, population_in_sample_skill_score, in_sample_skill_scored}))}' metrics/leaderboard.json
```

(`release-sensitivity` carries the same figures under
`.post_hoc_in_sample_benchmark.figures`, outside the registered headline.)

> Beside the registered figures we report one benchmark chosen after the
> outcomes were known: skill against the grant rate the scored petitions
> themselves realized. It is hindsight by construction — its baseline contains
> every scored petition's outcome, including the one being scored — so it
> ranks nothing, carries no claim, and is not the measure this release
> pre-registered; the prior-Term skill above is. It answers a narrower
> question: against the grant rate these petitions actually realized, how well
> did each engine separate the ones that were granted from those that were
> not? Over all bands together that separation includes telling the bands
> apart, which the salience gate already does in part; within a single band it
> is case-level separation alone. It is undefined in any band where no scored
> petition was granted, and where it is defined the few granted petitions set
> its scale, so each figure is given with its count of grants.

‹per predictor, over the forward stratum of the ranked board, the in-sample
benchmark — `population_in_sample_skill_score` with `in_sample_skill_scored`,
and in the same sentence its grant count as "k grants of n events"
(`in_sample_grant_rate` × `in_sample_events_scored`), noting that GVRs and
summary reversals count as grants — and per band where it is defined, as the
within-band reading; every row labelled post-hoc and placed after the
registered prior-Term figure it sits beside, never before it; predictors set
side by side only where their `in_sample_events_scored` agree; from the `jq`
line above›

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
entry's `evaluators`; and the population's own `events_scored` union. For the
run-order disclosure: the cohort's predict and evaluate runs and their per-job
start times (`gh run list`, `gh run view <id> --json jobs`), the `run_id` in
each prediction's ledger path, and the harness-stamped `context` on each
prediction.

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
> Per band, engines are compared only over that band's **complete grid** —
> the board's `complete_grid_by_band`, the forward petitions in the band on
> which every engine carries an accuracy-scored grading. The grid is a count,
> not a population any figure is computed over, so a per-band ordering is read
> only where every engine's `by_band[band].accuracy_events_scored` equals the
> band's grid count: equal counts over a set contained in each engine's own is
> the same petitions. Anywhere else no per-band ordering is read. An engine with
> no forward accuracy-scored cell in a band leaves that band with no grid, and
> the missing key reads as that.
>
> The engines did not run under identical conditions. Every predict and
> evaluate run that forecast or graded this cohort — confirmed run by run below
> — listed its cells engine by engine in registry order — claude, then codex,
> then gemini — and the runner started cells in list order, as the start
> windows below show. So within a run gemini's forecasts started last —
> in the largest runs ‹the longest gap between claude's and gemini's first cell
> starts, from the start-window figures below› after claude's — behind the other
> two engines' spend of the shared retrieval quota, and later against the docket.
> How often that quota turned each engine's cells away cannot be measured
> across engines from the harness's retrieval logs. Gemini's logs carry no call
> result at all, and codex's carry results for its direct calls but not for the
> calls its programs make, so neither engine's refusals can be counted, and no
> per-engine incidence is reported. Nor is any figure recomputed without the
> cells a refusal may have reached, because dropping them would leave each
> engine's figures over a different event set. The direction of the effect
> on the ranking is unknown — a later docket gives a forward forecast more to go
> on, a refused retrieval less — and nothing in the ranking adjusts for it, so
> the cohort cannot separate an engine's skill from its slot, and every
> cross-engine difference here is read with that in mind. The evaluate runs ran
> the judges in the same order, so gemini-judge graded last; every judge grades
> every predictor blind, so that slot is shared by all predictors under one
> judge and bears on comparisons *between judges*, not on the predictor
> ranking. Start order within a run is not the only timing difference: a cell
> that failed and was re-minted ran in a later run against a later docket, and
> each engine's failure rate sets its share of such late cells, so that share is
> reported per engine below rather than assumed equal. From the next cohort the
> fan-out is to interleave the engines in a keyed order per run and event, so
> that no engine holds a fixed slot; this cohort's runs are the registry-order
> ones confirmed below.
>
> The ranking is on N-unweighted point estimates over a cohort whose band mix
> implies roughly a dozen grants. A one- or two-event difference reorders it.
> The order is therefore reported as locating a difference between the engines,
> not as measuring one.

‹each engine's `events_scored`, complete-grid `n`, per-stratum evaluations and
panel depth, and per band each engine's `accuracy_events_scored` beside
`complete_grid_by_band` — from `metrics/leaderboard.json`›

‹confirmation that every predict and evaluate run carrying a counted cohort
cell or grading ran under registry order, before the interleaved fan-out
reached production — from `gh run list --workflow run-predict.yml` /
`run-evaluate.yml` against the merge time of the promotion carrying it; if any
cohort run postdates it, name those runs and restate the paragraph above
separately for the runs on each side›

‹in the cohort's largest predict and evaluate runs, the first and last cell
start per engine, and how long after claude's first cell gemini's first cell
started — from `gh run view <id> --json jobs` (`startedAt` per job)›

‹per engine, the share of its cohort predictions whose `run_id` is later than
the earliest sibling engine's `run_id` on the same event — from the
`predictions/<predictor>/<run_id>/` paths under each cohort event — beside the
`attempt.json` counts in *Engine losses stay owed*, and each engine's
distribution of snapshot as-of date against run date, from the stamped
`context` on its predictions›

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
uv run fedcourts conference-set --counted --registered-at 2026-09-15 > cut.json
jq '.conference_fallbacks' cut.json                # fallbacks: must be 0
jq '[.totals[] | select(.registered)] | group_by([.stage, .moment, .band])
  | map({stage: .[0].stage, moment: .[0].moment, band: .[0].band,
         events: (map(.events) | add), scored: (map(.scored) | add),
         resolved_unscored: (map(.resolved_unscored) | add),
         pending: (map(.pending) | add), unforecast: (map(.unforecast) | add)})' \
  cut.json                                         # registered: by arm and band
jq '[.events[] | select(.registered and .moment == "distribution")
  | select(.conference != .conference_at_registration
           or .current_conference != .conference_at_registration)
  | {case_id, docket_number, conference_at_registration, conference,
     current_conference, bands, status,
     moved: (if .predictors == [] then "no counted cell"
             elif .conference == "mixed" then "between its cells"
             elif .conference != .conference_at_registration then "before the cut"
             else "after the cut" end)}]' cut.json  # moved
jq '[.events[] | select(.registered and .conference == "mixed") | {case_id, cells}]' \
  cut.json                                         # split cells
jq '[.events[] | select(.registered | not) | select(.moment == "distribution")]
  | group_by(.conference) | map({conference: .[0].conference, events: length})' \
  cut.json                                         # outside the registered rule
jq '.events_scored, .entries[].events_scored' metrics/leaderboard.json
```

`conference-set --counted --registered-at` gives both sides of the
reconciliation in one reading. Its population is every **counted** event — one
with a counted cell: the run a counted grading names, else a predictor's staged
(newest resolvable) run when it is its predictor's counted forecast of the
event — together with every
**registered** event, counted or not. For each it gives the conference the
petition was distributed for at its counted cells' cut, the conference it was
distributed for on the registration day, the current corpus column, the band the
cells froze, the counted and scored predictors, and a status: `scored`
(resolved, every counted predictor graded), `resolved_unscored` (resolved, a
grading not yet landed or excluded), `pending` (no outcome yet), or `unforecast`
(no counted cell at all — attrition, never an ungraded forecast). Its totals are
per (registered, conference, stage, moment, band), the four statuses summing to
the events; the *registered* command folds the conference away to give the
table per arm and band. The JSON names the corpus vintage and digest it was read
at.

**The cohort is selected by `registered`, never by a conference.** The flag
reconstructs the registered rule's membership as at the registration day: an
event at a re-predict moment that held a de-counted or unstamped cell by that day,
had no outcome before it, and — at the distribution moment — was distributed
for a conference still ahead. 2026-09-15 is that day because the census in the
freeze record was read from a blob pulled 2026-09-14 against a ledger whose tip
is dated 2026-09-15, so the reconstruction admits docket entries filed through
09-14 and de-counted cells made through 09-15. It reconstructs the **rule**, so its
per-arm counts are checked against the rule's census in the freeze record —
123 events: 110 cert/distribution, 10 cert/cvsg and **3** interim/arrival —
not against the 122 the deriver minted, which held one interim event back; the
prose below carries both figures, and which interim events were forecast is
named from the rows. Any other difference is named event by event. The census
blob is named in the freeze record, and a re-read against it settles a
difference exactly.

Membership is fixed at registration, so a registered petition stays in the
denominator whatever happened to it afterwards, and the *moved* command names
each one whose conference changed: before its counted cut (it was forecast
against the later conference, and the band its cell froze may differ from the
registered one), after the cut (it was forecast against this conference but did
not go to it, or was relisted from it, and is pending until the Court acts),
between its own cells (the *split cells* command shows which), or never forecast
at all. Each is reported inside the registered count, with the move named,
rather than dropped. Selecting by the cut conference instead would make
membership turn on whether a re-forecast ran before or after a reschedule,
which is pipeline timing, and a reschedule is itself a salience signal, so
dropping on it is selection on a signal correlated with the outcome. A CVSG
cell is cut at the invitation and an interim cell names no conference, so
neither arm is compared this way.

The cut is read with `fallbacks` at 0. Run it where the content store is wired
(a dev checkout's read-only role serves it): both conferences are reconstructed
from each case's live payload, and on a payload-free index with no store every
reading falls back to the current `distributed_for_conference` column, which
moves on every relist and reschedule. Each event's `payload_date` says how fresh
that case's payload was, since the corpus-wide vintage does not: a `pending`
status on a case whose payload predates the order list means "no outcome as of
that payload", and is named as such or refreshed by the pull lane before the
fill.

The reconciliation then reads, per arm: the registered table; the cut's
registered count and band mix by the band the counted cells froze, with each
band difference named from the *moved* rows; the scored, resolved-unscored,
pending and unforecast split, which sums to the arm; and, beside it and never
inside it, the counted events the registered rule did not cover (the *outside
the registered rule* command) — forecasts the frozen process made first, which
are later backlog rather than cohort. Within those, the reconciliation names
the **post-conference first forecasts**: board events whose first forward cell
postdates the conference that actually considered the petition. That is the
conference that sat on it — a later distribution or a reschedule moves it, and a
call for response entered before the conference sat takes the petition off it —
never the current `distributed_for_conference` column. The subset is defined
from committed data and the corpus, as the earliest harness-minted `run_id`
among an event's forward cells in the board's frozen process scope against
that conference, never the agent-written `created_at`; a cell run on the day
the conference sat counts as after it. Because the board scores each
predictor's newest cell rather than its first, the release sensitivity command
also checks every `cert@distribution` board cell whose *scored* run, for any
predictor, postdates its considering conference, and names any that falls
outside the subset (`scored_after_conference_outside_subset`); it lists the
subset itself (`subset`). The first forward cell is the earliest among the
counted cells (the frozen scope's event-aware rule), so neither a de-counted
cell nor a later window's cell the rule does not count is ever the first,
and "none registered" is a confirmation the command's `registered` count
makes, not a property of the rule. The conference is the one the petition was
distributed for as at the run, read off the petition's own distribution
entries and never an ancillary paper's ("Motion … DISTRIBUTED for Conference
of …"), so a relist entered before the run moves it to the next conference,
which is still ahead, and the cell is a forecast at the relist moment rather
than after the petition's last consideration. A docket entry reading
"Rescheduled." or "Response Requested." filed between the distribution and the
conference day, that day included, takes the petition off it. A run's day is
its `run_id`'s UTC day, the Court's own day for any run after 04:00 UTC (05:00
in winter). Where the stored payload predates the conference day, whether such
an entry was filed cannot be read, and the event is listed under `unreadable`
rather than placed; that list is empty before the count is quoted.

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
> baseline, 1 federal, 1 state — with 10 cert/cvsg events, all high band, and 3
> interim/arrival events beside them, of which 2 were minted when the cohort was
> registered and the third was held back.
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
>
> The registered cohort contains petitions that are not petitions for
> certiorari. Two of its cert/distribution events — No. 25-1315
> (`scotus/73500218`) and No. 25-1252 (`scotus/73299074`) — are petitions for
> a writ of mandamus, an extraordinary writ under the Court's Rule 20. They are
> docketed in the same form as a cert petition, so scope admitted them, they
> drew a salience band, and they are graded against the pooled cert base rate
> of that band like every other cert event. They stay in the cohort and are
> scored as registered. But the Court grants an extraordinary writ far more
> rarely than certiorari, so the cert anchor overstates their prior. Per-event
> skill on such a petition swings widely: a forecast near zero earns large
> positive skill against the band's rate, and a forecast of a few percent can
> earn large negative skill. The registered population skill is a ratio of sums
> over the band, so one denial moves it far less, and how far is what the
> sensitivity line shows: each headline accuracy and skill figure carries one
> with them removed (section 3). They are
> identified by the docket's opening entry — a petition for a writ of
> mandamus, prohibition or habeas corpus — not by docket form, and any further
> such petition that reading finds on the board, in the cohort or not, is named
> here too.
>
> The board is wider than the cohort, and part of what it holds was forecast
> late. Some events whose first forward cell postdates the conference that
> considered the petition are on the frozen board as registered: the counting
> rule admits them, so they stay. The registered cut already excludes them
> from the cohort. Their cells were made after that conference had sat and
> after the 2026-10-01 grant list had issued, and a petition still undisposed
> after the grant list is very unlikely to have been granted from that
> conference, so those forecasts were made with information a forecast at the
> conference could not have had. Wherever any of them is graded, every
> board-wide figure in section 3 carries a sensitivity line without them;
> while none is graded, the lines would equal their headlines and are omitted,
> and the reconciliation says so.

‹the graded cohort's size and composition, reconciled against the registered
table above, with any delta explained — from `conference-set --counted
--registered-at 2026-09-15`'s registered totals and per-event rows, with the
vintage it was read at, and `metrics/leaderboard.json`'s `events_scored`›

‹the re-measured band mix, if any tick of the drain did not run — from the same
cut's registered per-band totals›

‹the cohort's extraordinary-writ petitions, each by docket number and case id
with the band its cells froze, its outcome and each engine's forecast — from
the cut's per-event rows, with the identification by opening entry from
`release-sensitivity`'s `.blocks.rule_20_excluded.identified` (each case's
`opening_entry`, its events and whether each is `registered`), with
`not_certiorari_not_rule_20` and `unclassified` both empty; the two named
above, and any further one it finds›

‹the post-conference first forecasts, re-counted at fill time: how many board
events, on which conference, how many resolved and how many graded, each named
by case id with its first forward cell's date and the conference that
considered it; confirmation that none is registered; and confirmation that
every one's first forward cell postdates the 2026-10-01 grant list, naming
any that does not with its date and restating the paragraph above for it —
from `release-sensitivity`'s `.blocks.post_conference_first_forecasts_excluded`
(`events`, `by_conference`, `resolved`, `graded`, `registered`, each `subset`
row's `first_forward_run_id` and `considering_conference`, and
`not_after_grant_list`, which names any first cell not after the grant list;
the grant list is read against `grant_list_conference` only), with the
vintage it read (`.corpus`, and `.payloads_read` for the stored dockets the
block actually read); if none is graded
(`lines_equal_headline: true`), say that the section 3 lines without them are
omitted because they would equal their headlines›

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
on a `main` commit whose tree carries both the published metrics refresh and the
filled write-ups — this document and its public page. The refresh lands on
`main` directly as a reviewed pull request while the filled documents arrive by
promotion, so that is the promotion merge landing the documents, after the
refresh.

The public page's per-case values are copied from the dataset export, and the
page must be filled before the tag it is archived under exists. So the export
is built twice — once at the refresh to fill from, and once at the candidate
commit to archive — and the tag is minted only once the two agree on everything
the documents quote. Every step is the maintainer's, in this order:

1. **Refresh.** The metrics refresh lands on `main`. The merge commit that
   lands its pull request — the *refresh commit* — is the one this document's
   figures are read from; the pull request branch's own commit is not on
   `main`'s first-parent line and fails the manifest check below.
2. **Fill export.** From a full-history checkout of the refresh commit with the
   corpus pulled (`fedcourts corpus-pull`), since the docket numbers are read
   from it:

   ```bash
   git fetch origin main
   git switch --detach <refresh-commit>
   uv run fedcourts export --out <fill-dir>
   ```

   The manifest must show `source_dirty: false`, the refresh commit as
   `source_commit`, `source_on_main_first_parent: true` (the commit is on
   `main`'s first-parent line, which is what makes each `ledger_commit` the
   prediction's landing on `main`), `ledger_commits: "git"`,
   `docket_numbers: "corpus"` and `counts.predictions_without_ledger_commit: 0`.
   This is a full export, not a dry run: `uv run fedcourts export --out <dir>
   --all-versions` is the dry run on shakedown data, and no figure is quoted
   from a dry-run bundle, whose commits date a file's arrival on whatever line
   was checked out.
3. **Reserve the dataset DOI.** Open the dataset deposit as a Zenodo draft and
   reserve its DOI, which the public page cites for the figures.
4. **Fill and promote.** Fill both documents from the refresh and the fill
   export, resolve the section 7 pass, and promote them. The promotion merge is
   the *candidate commit*.
5. **Check the candidate.** Build the export again from a full-history checkout
   of the candidate (after `git fetch origin main`, so the first-parent check
   sees the merge), into a fresh directory, with the same manifest checks and
   the candidate as `source_commit`. Then compare it with what the documents
   were filled from, and regenerate the boards under the candidate's code:

   ```bash
   git diff --exit-code --stat <refresh-commit> <candidate-commit> -- \
     metrics/leaderboard.json metrics/claim-scores.json \
     metrics/statpack.json metrics/statpack.md
   diff <fill-dir>/predictions.csv <candidate-dir>/predictions.csv
   diff <fill-dir>/gradings.csv <candidate-dir>/gradings.csv
   uv run fedcourts leaderboard && uv run fedcourts claim-scores
   git diff --exit-code -- metrics/leaderboard.json metrics/claim-scores.json
   ```

   Both metrics diffs must be empty: the first shows no newer refresh landed,
   the second that the code the tag archives reproduces the boards it quotes.
   Every line the table diffs show must be a row outside the cohort section 5
   registers — for instance, a forecast or grading for a later conference. A
   grading that lands on a cohort prediction changes that prediction's own row
   too, so it cannot hide in the gradings table alone. A moved metrics file, or
   a changed, added or removed cohort row, means an input the documents quote
   changed after they were filled: re-fill from the candidate's tree and build,
   which then stand in for the refresh commit and the fill export, promote
   again, and check the new candidate.
6. **Tag.** Only once both documents' placeholder greps return nothing and the
   section 7 pass is resolved, since the `results/` namespace blocks update and
   deletion:

   ```bash
   git tag -a results/ot2026-longconf -m "OT2026 long-conference cert release" <candidate-commit>
   git push origin results/ot2026-longconf
   ```

7. **The software record.** The tag is published as a GitHub Release, and
   Zenodo's GitHub integration archives the repository at that tag as a new
   version of the project's software record, with its own version DOI. That
   record is the code that produced the figures, and Zenodo does not archive
   files attached to the Release.
8. **The dataset record.** The candidate's build from step 5 is the export
   built from the tagged commit — its manifest already names it — and it is
   uploaded to the reserved draft and published as a separate **dataset**
   record under CC BY 4.0, linked to the software record's version DOI as a
   supplement to it, with its own version DOI under the dataset's concept DOI.
   It holds the data only (what it may carry is set in
   [data-sources.md](data-sources.md), *What we redistribute*), its manifest
   names the tagged commit and each file's checksum, and a published deposit's
   files cannot be replaced, which is what gives the data a timestamped copy
   held outside GitHub. The export is deterministic: a rebuild from the tag in
   its locked environment (`uv sync --locked`), against a corpus blob carrying
   the same docket numbers, reproduces those checksums. The same
   files may also be attached to the GitHub Release for convenience; the Zenodo
   deposit is the copy of record, and the manifest's checksums show the two are
   identical.

The software record is cited by its **concept** DOI, which exists from the
first archived Release, beside the tag name, which pins the exact code; its
version DOI is minted only after the tag and is not needed on the page.
