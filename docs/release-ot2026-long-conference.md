# Release write-up: the OT2026 long conference

The skeleton and evidence plan for the project's first public release — the
long-conference cert write-up [milestones.md](milestones.md) calls Release 1.
It is the definition of done for the publication, written before its data
exists so the claims are bounded by the process rather than by what the numbers
turn out to be.

**Written by AI.** This document was written by AI agents: Claude (Anthropic),
working in Claude Code under the maintainer's direction. They drafted the
skeleton before the conference, then filled every figure from the commands
each section names, run at the refresh commit, with a log of each command and
its output. AI reviewer agents checked the statistics and the prose against the
code and the data (section 7), and the maintainer reviewed it before it was
published. The forecasts and gradings it reports are themselves the output of
AI models (section 1).

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

**What this fill was read from.** Every figure filled below was produced at
the refresh commit `0918fb18e74fb89adc9a0882411996400986925e` (the merge of
the metrics refresh on `main`'s first-parent line), from a checkout of that
commit with the corpus pulled. The corpus vintage throughout is `corpus-info`'s
newest pull **2026-10-09** and newest stored snapshot row **2026-07-13**
(blob sha256 `eee1ae41…e0302ce9`). The fill export (section 8, step 2)
manifest reads `source_commit` the refresh commit, `source_dirty: false`,
`source_on_main_first_parent: true`, `ledger_commits: "git"`,
`docket_numbers: "corpus"` and `predictions_without_ledger_commit: 0`, over
743 predictions (329 scored, 0 set aside) and 987 gradings (985 counted). The
release sensitivity command read the same ledger (`dirty: false`,
`on_main_first_parent: true`) and corpus blob, 208 stored payloads (none
missing, dated 2026-10-02 to 2026-10-09), the fill statpack build `3f3ca14f`,
with `conference_fallbacks` 0 and `registered_headline.matches_committed_board`
true. The cohort cut (`conference-set --counted --registered-at 2026-09-15`)
read the same vintage with `conference_fallbacks` 0.

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

**Filled at the refresh commit.** `process-digest --all` on the refresh
commit's tree prints `proc-v8` and exactly the six digests the board's
`frozen_process.digests` lists, one per predictor and evaluator — the
comparison made is the refresh tree against the board's frozen set, and it
shows nothing moved. The board's `frozen_process` reads
`since: 2026-09-16T00:26:04Z` and its `windows` are exactly the three
`proc-v8` predictor windows, each opening at that instant with null `closes`
and null `revoked_at`. Cohort completeness, read off the cut at the corpus
vintage above: the *owed* command returns three empty lists — no cohort cell
would be minted, withheld or deferred (the plan's backlog-wide
`would_mint_cells` is 9, all on later events) — and the *short of the full
grid* command returns one row, the registered interim/arrival event
`scotus/9526000273` (No. 26A273, `evt-motion-disposition`) with no counted
predictor and status `unforecast`. Every registered cert event, all 110 on
cert/distribution and all 10 on cert/cvsg, carries all three counted
predictors. The per-digest census over the refresh commit's ledger
(`data/cases`, files carrying each digest; the ledger-wide count the
pre-registration record uses, not a cohort count): claude-baseline 248,
codex-baseline 248, gemini-baseline 247; claude-judge, codex-judge and
gemini-judge 353 each; 2,284 files carry a stamped `process_version` object.
Snapshot uptake: of the ledger's 1,411 committed `prediction.json` files,
743 carry the mark (the fill export likewise carries 743 predictions), and all
743 read `snapshot_uptake: read`, none `unread`; a self-report, as stated
above.

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

The ledger at the refresh commit carries 160 `attempt.json` failure facts in
all, 40 of them from runs at or after the counting instant. On the registered
cohort's events there are 35, and every one was later made good: each cohort
cert event carries a counted cell from every predictor, each resolved one a
counted grading from every judge (section 2), and the plans owe the cohort
nothing (above, and `evaluate-plan`'s `would_mint_cells` is 0). By engine and
seam:

| Seam | Engine | On cohort events | Of which since the counting instant |
| --- | --- | --- | --- |
| predict | codex-baseline | 4 `no_output` | 4 `no_output` |
| predict | gemini-baseline | 4 `no_output`, 2 `partial`, 1 `quota` | 3 `no_output`, 2 `partial`, 1 `quota` |
| evaluate | codex-judge | 1 `died` | 1 `died` |
| evaluate | gemini-judge | 13 `died`, 7 `no_output`, 3 `partial` | 13 `died`, 7 `no_output`, 3 `partial` |

claude-baseline and claude-judge lost no cohort cell. The one pre-freeze cohort
fact is gemini-baseline's `no_output` on the CVSG event `scotus/73275236`
(run 20260820T181919Z). The 13 gemini-judge `died` facts are one run
(20261007T150255Z), whose 13 failed gemini-judge jobs are the first jobs that
run started (*Comparing the engines*, below); the codex-judge `died` fact is
the job cancelled in run 20261006T192524Z. Ledger-wide, the 160 split
predict 108 (claude-baseline 27 `died`; codex-baseline 31 `died`,
4 `no_output`, 2 `quota`; gemini-baseline 27 `died`, 11 `no_output`,
4 `partial`, 2 `quota`) and evaluate 52 (codex-judge 22 `died`, 4 `quota`;
gemini-judge 13 `died`, 8 `no_output`, 4 `partial`, 1 `quota`). No cohort
cert cell is missing, so no engine left a graded population by exhausting its
attempt cap. The one cohort event no engine forecast, 26A273 above, carries no
`attempt.json` fact: its only cells are the pre-freeze run 20260901T014205Z,
no frozen cell was minted for it, and the application resolved `withdrawn` on
2026-09-25. It is an interim event, outside every scored figure here. Read from the
committed `attempt.json` files at the refresh commit and `predict-plan` /
`evaluate-plan` at the corpus vintage above.

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

At the refresh commit, `evaluate-plan` would mint 0 cells and `validate data`
reads OK (35,899 artifacts valid, 49,319 references consistent). The board's
two exclusion blocks, both stage-blind and counted over gradings:

- `forward_claim`: policy `exclude`, `claimed_forward` 987, `excluded` **0**,
  no per-predictor entries.
- `leakage_exclusion`: `assessed` 987, `excluded` **2**, both on
  gemini-baseline — `scotus/9526000434` and `scotus/9526000437`, each an
  interim `evt-motion-disposition` cell flagged by codex-judge alone. Both are
  outside the cohort and off the cert board; each prediction stays scored
  through the two judges that did not flag it.

Over the registered cohort — the 91 scored cert/distribution events, three
predictors each graded by all three judges, 819 counted gradings — the leakage
bit is false in all 819 and null in none. `influenced_prediction` is never
`possible` or `likely`: claude-judge and codex-judge record `not_applicable`
on all 91 events for each predictor, and gemini-judge records `not_applicable`
on 63 and `none` on 28 for each predictor. `retrieved_outcome_material` is
false in 814, null (not determined by the judge) in 5, and true in none. The ops report's
uncollapsed `leakage` digest is a different population and is not differenced
against these. Board-wide, over all 873 counted cert/distribution gradings
in the fill export (the 97 board events × 3 predictors × 3 judges, the six
post-conference first forecasts included), `leakage_suspected` is false in
every one.

Evaluator set: the fill export's 985 counted gradings carry exactly one
digest per evaluator — claude-judge `sha256:fbc0e9c364d8…` (329 gradings),
codex-judge `sha256:9670e1c147a7…` (327), gemini-judge
`sha256:dbdc90647bc8…` (329) — the three `proc-v8` evaluator digests. One
evaluator set graded the list; no grading protocol boundary falls inside the
window.

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
> Term. 108 of the 110 registered cert/distribution events, and all 10
> CVSG events, were docketed in OT2025; of the 97 events the ranked board
> scores, 90 were docketed in OT2025 and 7 in OT2026 — No. 26-173 from the
> cohort and the six post-conference first forecasts section 5 names. For
> the OT2025 petitions the committed pack
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
> against them. Taking the OT2025-docket rates for all 110 registered events,
> the registered cohort's band-mix-implied grant rate is about 10.2% over its
> 110 cert/distribution events — about 18.2% over the selected subset
> (n = 39) and 5.9% over the declined remainder (n = 71) — and about 12.3%
> over all 120 cert-stage events once the CVSG arm is folded in. The cohort's
> two OT2026 dockets move the 110-event figure by under a hundredth of a
> point. Those are figures about the registered cohort, not about the scored
> board: the board's own expectation, summing one recorded band rate per
> scored event (averaged over its panel), is 9.32 grants over its 97 events
> (`grants_expected` on any entry's `forward` block), about 9.6%. The freeze
> record's
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

**The per-band cut, filled.** Ranked board `cert@distribution`, forward
stratum, `process_scope: "frozen"`, salience version `sal-v4` (the board's
`salience_versions` lists only it), at the refresh commit. Each entry scores
97 events, all forward (no retrospective or procedural block on any entry),
with a panel of 3 evaluators and a mean depth of exactly 3.0 in every band
(`evaluations / events_scored` = 201/67, 84/28, 3/1, 3/1). "Accuracy",
"floor" and "lift" below are the per-petition `event_accuracy`,
`event_always_deny_accuracy` and `event_accuracy_lift` over
`accuracy_events_scored` petitions; at uniform depth the grading-weighted
`accuracy`, `always_deny_accuracy` and `accuracy_lift` equal them exactly,
over `accuracy_scored` = 3 × that many gradings. Skill is the population
Brier skill score (a ratio of sums) over `skill_scored` gradings, against
each grading's recorded prior-Term band rate.

| Predictor | Band (sal-v4) | Petitions | Accuracy | Realized floor | Lift (pts) | Gradings | Skill (`skill_scored`) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-baseline | baseline | 67 | 100.0% | 100.0% | +0.0 | 201 | +0.502 (201) |
| claude-baseline | elevated | 28 | 96.4% | 92.9% | +3.6 | 84 | +0.396 (84) |
| claude-baseline | high | 1 | 100.0% | 0.0% | +100.0 | 3 | +0.622 (3) |
| claude-baseline | federal | 1 | 100.0% | 100.0% | +0.0 | 3 | +0.991 (3) |
| codex-baseline | baseline | 67 | 100.0% | 100.0% | +0.0 | 201 | +0.118 (201) |
| codex-baseline | elevated | 28 | 92.9% | 92.9% | +0.0 | 84 | +0.128 (84) |
| codex-baseline | high | 1 | 100.0% | 0.0% | +100.0 | 3 | +0.939 (3) |
| codex-baseline | federal | 1 | 100.0% | 100.0% | +0.0 | 3 | +0.939 (3) |
| gemini-baseline | baseline | 67 | 100.0% | 100.0% | +0.0 | 201 | −0.334 (201) |
| gemini-baseline | elevated | 28 | 85.7% | 92.9% | −7.1 | 84 | −0.596 (84) |
| gemini-baseline | high | 1 | 0.0% | 0.0% | +0.0 | 3 | −0.708 (3) |
| gemini-baseline | federal | 1 | 100.0% | 100.0% | +0.0 | 3 | +0.995 (3) |

The board carries no `state` row (the cohort's one state-band petition,
No. 25-1115, is pending) and no `(none)` key: every scored cell froze a
`sal-v4` band. The high and federal rows are one petition each and support no
claim; they are printed for completeness of the cut.

Grants per band, the same for every predictor because they count events:
baseline **0** realized against **3.42** expected over 67 events; elevated
**2** against **4.82** over 28; high **1** against **0.35** over 1; federal
**0** against **0.73** over 1 (`grants_realized_expected_scored` against
`grants_expected`, over `grants_expected_scored`). Relisted and held petitions
are still pending and grant more often than the ones already decided, so
while they pend realized runs below expected, and this shortfall is not yet
evidence of miscalibration. It does move skill in a known direction: in the
baseline band every scored petition was denied, so skill there rewards
forecasting low rather than separating grants from denials, and the pending
shortfall currently favours the lower forecaster — the baseline row's skill
is not a reading of discrimination. Complete grid (`complete_grid_by_band`): baseline
67, elevated 28, high 1, federal 1 — every engine's `accuracy_events_scored`
equals its band's grid count in every band.

Docket-Term mix of each row, from the scored predictions' `context.term`:
baseline 61 OT2025 + 6 OT2026; elevated 27 OT2025 + 1 OT2026; high and
federal 1 OT2025 each. Each row's skill anchor, by docket Term — not the
floor, and never subtracted from: for OT2025 dockets 5.12% baseline, 17.22%
elevated, 34.97% high, 72.93% federal (pool OT2017–OT2024, identical in the
graded and the refreshed pack); for OT2026 dockets the pool the counted
gradings read, statpack build `808f812e`, 5.02% baseline and 16.89% elevated
(the refreshed pack now pools 4.99% and 16.83%; see below). Their complements
are grant-family denial shares, not the exact-match floors the lift is
measured against.

**The CVSG arm has no block.** The refreshed board carries no `cert@cvsg`
stage section: all 10 registered CVSG events are pending (section 5), so
nothing on that arm is graded, and the omitted section is an empty state, not
a result of zero.

**Three grants, two kinds.** The board's three grant-family events are not
alike. Two are **GVRs** entered 2026-10-05 — No. 25-901 (`scotus/73280412`,
high band) and No. 25-918 (`scotus/73280426`, elevated), each "Judgment
VACATED and case REMANDED for further consideration in light of *Louisiana*
v. *Callais*" per its docket entry (both payloads dated 2026-10-05) — and one
is a **plenary grant**, No. 25-1131 (`scotus/73281619`, elevated), granted
2026-10-01 "limited to Question 1 presented by the petition" (payload dated
2026-10-09). Per event, with each engine's grant call at P ≥ 0.5 (the
export's `granted` column): claude-baseline called both GVRs (0.60, 0.55) and
made no false grant call; codex-baseline called No. 25-901 (0.84) and missed
No. 25-918 (0.30); gemini-baseline called none of the three (0.15, 0.25,
0.05) and made two false grant calls among denied petitions, No. 25-1208
(0.82) and No. 25-1105 (0.55). No engine put more than 0.30 on the plenary
grant (claude-baseline 0.30, codex-baseline 0.30, gemini-baseline 0.05). So
any grant-detection count on this board — and the accuracy column, whose
grant-side hits are all GVR calls — largely measures **GVR detection** on two
events that turned on one intervening decision, not the detection of plenary
review, on which the board has one event and no engine called it.

The skill anchors, re-read with `fedcourts segment-anchors --term 2025
--term 2026` (`sal-v4`, lookback 10), `risk_set` rate with weighted `n`:

| Docket Term | Pooled Terms | Statpack build | baseline | elevated | high | federal | state |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OT2025 | OT2017–OT2024 (8) | refreshed `3f3ca14f` and graded `808f812e` alike | 5.12% (11,580) | 17.22% (2,810) | 34.97% (898) | 72.93% (181) | 22.70% (392) |
| OT2026 | OT2017–OT2025 (9) | graded `808f812e` | 5.02% (12,720) | 16.89% (3,085) | 35.51% (966) | 70.79% (202) | 23.63% (419) |
| OT2026 | OT2017–OT2025 (9) | refreshed `3f3ca14f` | 4.99% (12,871) | 16.83% (3,113) | 35.57% (967) | 70.44% (203) | 23.52% (421) |

The OT2025-docket rates reconcile exactly with
[metrics/README.md](../metrics/README.md) and the freeze record's correction
entry ([freeze-record.md](freeze-record.md)): 5.12% / 17.22% / 34.97% /
72.93% / 22.70%, the anchor for 90 of the board's 97 events. The OT2026-docket
rates those two documents quote, 5.02% / 16.89% / 35.51% / 70.79% / 23.63%,
are the pool of build `808f812e` (2026-09-28), the only build any counted
cert grading read (`release-sensitivity`'s `statpack_builds`: one build, 873
gradings); the refreshed pack's OT2025 row has resolved further since, so the
same pool now reads 4.99% / 16.83% / 35.57% / 70.44% / 23.52%. The OT2026
pool applies to the board's 7 OT2026 dockets only. The `808f812e` row was
produced by running `segment-anchors` against that build's
`metrics/statpack.json`.

The transcription spread, re-measured at fill time from
`release-sensitivity`'s `.blocks.exact_pool_anchor.transcription_spread`.
Every graded cert cell read one statpack build, `808f812e` (873 gradings,
lookback 10), the cohort's `unanchored` list and the block's
`recorded_retained` list are both empty, and **no cell deviates from its exact
pool by more than 1%** on either population. "Exact" is equal to six
decimals; "faithful" is equal to the exact pool rounded to the recorded
rate's own decimals.

| Population | Judge | Docket Term | Cells | Exact | Faithful | Max rel. dev. | Mean rel. dev. | Over 1% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skill-scored cert cells | claude-judge | OT2025 | 270 | 75 | 171 | 0.092% | 0.025% | 0 |
| skill-scored cert cells | claude-judge | OT2026 | 21 | 6 | 12 | 0.114% | 0.066% | 0 |
| skill-scored cert cells | codex-judge | OT2025 | 270 | 6 | 6 | 0.080% | 0.033% | 0 |
| skill-scored cert cells | codex-judge | OT2026 | 21 | 0 | 0 | 0.098% | 0.097% | 0 |
| skill-scored cert cells | gemini-judge | OT2025 | 270 | 66 | 117 | 0.338% | 0.051% | 0 |
| skill-scored cert cells | gemini-judge | OT2026 | 21 | 6 | 3 | 0.096% | 0.069% | 0 |
| registered cohort, graded cert cells | claude-judge | OT2025 | 270 | 75 | 171 | 0.092% | 0.025% | 0 |
| registered cohort, graded cert cells | claude-judge | OT2026 | 3 | 0 | 3 | 0.070% | 0.070% | 0 |
| registered cohort, graded cert cells | codex-judge | OT2025 | 270 | 6 | 6 | 0.080% | 0.033% | 0 |
| registered cohort, graded cert cells | codex-judge | OT2026 | 3 | 0 | 0 | 0.098% | 0.098% | 0 |
| registered cohort, graded cert cells | gemini-judge | OT2025 | 270 | 66 | 117 | 0.338% | 0.051% | 0 |
| registered cohort, graded cert cells | gemini-judge | OT2026 | 3 | 3 | 3 | 0.000% | 0.000% | 0 |

Across all 873 skill-scored cells the largest relative deviation is 0.338%
(a gemini-judge grading recording 0.051036 against the exact OT2025 baseline
pool 0.051209) and the mean 0.039%; across the cohort's 819 graded cert cells,
the same maximum and a mean of 0.037%. codex-judge records the rate at full
precision as pooled from the rendered table's rounded rows (0.172379 against
the exact elevated OT2025 pool 0.172242), so it is rarely exact or faithful
while staying within 0.1% of the exact pool.

**Sensitivity lines beside the headline.** Three sensitivity lines travel with
the per-band figures above, each given below beside the registered figure it
varies (registered → sensitivity) and each with its own `n`. The first is this section's; the other two
are disclosed with the cohort in section 5.

*Sensitivity: exact-pool anchor.* Population skill with each cert grading's
baseline taken from the exact pool of build `808f812e` instead of its
recorded `segment_base_rate`, over the same `skill_scored` cells as the
registered figure (registered → sensitivity, four decimals because the
moves are in the fourth): claude-baseline baseline +0.5017 → +0.5020 (201),
elevated +0.3960 → +0.3959 (84), high +0.6218 → +0.6217 (3), federal
+0.9908 → +0.9908 (3); codex-baseline baseline +0.1177 → +0.1183 (201),
elevated +0.1281 → +0.1279 (84), high +0.9395 → +0.9395 (3), federal
+0.9391 → +0.9391 (3); gemini-baseline baseline −0.3337 → −0.3328 (201),
elevated −0.5963 → −0.5967 (84), high −0.7080 → −0.7083 (3), federal
+0.9953 → +0.9953 (3). No band's skill moves by more than 0.0009, so the
transcription accounts for none of any registered skill figure's sign or
order.

*Sensitivity: extraordinary writs removed.* With the two mandamus petitions
section 5 names removed (both baseline band, both in the cohort, 18 board
cells), only the baseline row moves: 65 petitions instead of 67, accuracy,
floor and lift unchanged at 100.0% / 100.0% / +0.0 for every engine, and
skill over 195 gradings instead of 201 — claude-baseline +0.502 → +0.487,
codex-baseline +0.118 → +0.119, gemini-baseline −0.334 → −0.375. The
elevated, high and federal rows are identical to the registered ones.

*Sensitivity: post-conference first forecasts removed.* Six of the subset
section 5 names are graded — Nos. 26-66, 26-79, 26-80, 26-95, 26-121 and
26-183, all baseline band, all denied — so this line differs from its
headline (54 board cells removed). Without them each engine's
`events_scored` is **91** instead of 97, and only the baseline row moves:
complete grid 61 instead of 67; 61 petitions, accuracy, floor and lift
unchanged at 100.0% / 100.0% / +0.0 for every engine; skill over 183
gradings instead of 201 — claude-baseline +0.502 → +0.564, codex-baseline
+0.118 → +0.130, gemini-baseline −0.334 → −0.384; grants 0 realized against
3.12 expected over 61 events instead of 3.42 over 67. The elevated, high and
federal rows, their grids and their grant comparisons are identical to the
registered ones. These 91 events are exactly the registered cohort's scored
cert/distribution events (section 5).

**A post-hoc benchmark, labelled as one.** One skill figure in this section is
neither registered nor a sensitivity line: Brier skill against each block's own
**in-sample grant rate** (`population_in_sample_skill_score`), defined after
the conference's outcomes were known. It scores every grading against the
share of granted outcomes among the block's own scored events, the case being
scored included, so it nets out the block's level and nothing finer — at
uniform panel depth, with forecasts grouped at their distinct values, it is
(resolution − reliability) / uncertainty in the Murphy decomposition against
that rate, and approximately so otherwise — and no forecaster could have known its
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
> is case-level separation alone. It is undefined in any band where every
> scored petition went the same way, all denied or all granted, and where it is
> defined the few granted petitions set
> its scale, so each figure is given with its count of grants.

*Post-hoc, not registered, ranks nothing.* Over the forward stratum of the
ranked board, after each engine's registered prior-Term skill (+0.528,
+0.364 and −0.338 over 291 gradings each — a cross-band figure quoted only as
the registered figure this benchmark sits beside; its sensitivity lines are
+0.5275 / +0.3642 / −0.3381 on the exact pool, +0.527 / +0.365 / −0.340 over
285 gradings without the extraordinary writs, and +0.531 / +0.366 / −0.340
over 273 without the post-conference first forecasts), the in-sample
benchmark reads
claude-baseline **+0.468**, codex-baseline **+0.285** and gemini-baseline
**−0.505**, each over 291 gradings (`in_sample_skill_scored`), against
**3 grants of 97 events** (`in_sample_grant_rate` 3/97); `in_sample_events_scored`
is 97 for all three, so they sit side by side. Two of the three grants are
GVRs (above), which count as grants here, as summary reversals and partial
grants would. Within a band it is defined only in **elevated**, 2 grants of
28 events (one GVR, one plenary grant), over 84 gradings each: claude-baseline
+0.304, codex-baseline −0.005, gemini-baseline −0.841, each after its
registered elevated prior-Term skill (+0.396, +0.128, −0.596). It is undefined
in baseline (0 grants of 67) and federal (0 of 1), and in high (1 grant of 1),
where every scored petition went the same way.

As context only — **not this cohort's anchor** — the statpack's whole-docket
*SCOTUS cert petitions by Term* table at the refresh commit gives an estimated
grant-family rate between 2.3% and 3.3% for each of OT2017–OT2024, 2.5% for
OT2025 and 1.3% for the still-open OT2026 (denial-reweighted estimates over
every petition docketed in the Term). That is the docket as a whole; the
cohort was selected on band, and its anchor is the per-band table above.

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
> in the five large predict runs between 50 and 67 minutes after claude's —
> behind the other
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
> The ranking is on N-unweighted point estimates over a board whose recorded
> band rates expected about nine grants (9.32 over 97 events) and on which the
> Court made three, two of them GVRs. A one- or two-event difference reorders
> it.
> The order is therefore reported as locating a difference between the engines,
> not as measuring one.

**The board's order and its denominators.** The board ranks on forward
`accuracy`, then forward mean Brier (no skill column is a rank key). The
figures in this paragraph are that cross-band rank key, quoted only to state
the order; every reading of them is per band, in the table above. At the
refresh commit: rank 1 claude-baseline, accuracy 99.0% over 291 gradings,
mean Brier 0.0159; rank 2 codex-baseline, 97.9%, 0.0214; rank 3
gemini-baseline, 94.8%, 0.0451 — against an always-deny floor of 96.9% on the
same cells (a blend of the 100% baseline floor and the 92.9% elevated one),
so lifts of +2.1, +1.0 and −2.1 points, which are two, one and minus two
petitions of 97: claude-baseline's two GVR calls (Nos. 25-901, 25-918),
codex-baseline's one (No. 25-901), and gemini-baseline's two false grant
calls (Nos. 25-1208, 25-1105) against no hit. Sensitivity lines for this key:
with the extraordinary writs removed, 98.9%, 97.9% and 94.7% against a 96.8%
floor (95 petitions); with the post-conference first forecasts removed,
98.9%, 97.8% and 94.5% against 96.7% (91 petitions, below); the order holds
under both. Each engine's
`events_scored` is 97, the population's `events_scored` union is 97, and the
complete grid is 97 (67 + 28 + 1 + 1 over the bands); each entry's only
stratum is forward, with 291 evaluations, a panel of 3 evaluators and a mean
depth of 3.0; there is no retrospective or procedural block. Per band, every
engine's `accuracy_events_scored` equals `complete_grid_by_band`: baseline 67,
elevated 28, high 1, federal 1. Coverage is therefore equal, and the
per-band orderings in the table above are read over the same petitions — but
equal coverage certifies the event set only. With the six post-conference
first forecasts removed (the sensitivity line above) each engine's
`events_scored` and the complete grid are 91.

Run order, confirmed. The interleaved, keyed engine order reached `main` in
the promotion merged 2026-10-08T21:49:48Z (`9a2dc8168`). Every run carrying a
counted cohort cell or grading predates it: the seven predict runs
20260916T170237Z, 20260916T201911Z, 20260917T181231Z, 20260917T214606Z,
20260918T174135Z, 20260918T195102Z and 20260919T192714Z (GitHub runs
35125623085, 35145755402, 35257315115, 35278393003, 35375678697, 35388105504,
35464338589), and the six evaluate runs 20261002T200745Z, 20261005T221055Z,
20261006T154811Z, 20261006T192524Z, 20261007T150255Z and 20261007T185906Z
(37058510052, 37380715565, 37490457898, 37518770477, 37641680170,
37670928809). No cohort run postdates the change, so the paragraph above
stands for all of them.

Start windows, from each run's per-job `startedAt` (UTC):

| Run | claude: first → last start (jobs) | codex: first → last | gemini: first → last | gemini first after claude first |
| --- | --- | --- | --- | --- |
| predict 20260916T170237Z | 17:04:35 → 17:34:45 (25) | 17:37:05 → 18:09:16 (25) | 18:11:51 → 18:28:45 (25) | 1 h 07 min |
| predict 20260916T201911Z | 20:44:15 → 21:08:05 (22) | 21:08:17 → 21:33:05 (24) | 21:34:01 → 21:47:26 (23) | 50 min |
| predict 20260917T181231Z | 18:15:19 → 18:37:47 (24) | 18:38:04 → 19:07:26 (24) | 19:08:32 → 19:25:40 (25) | 53 min |
| predict 20260917T214606Z | 21:48:00 → 22:16:45 (25) | 22:17:55 → 22:44:00 (25) | 22:44:28 → 23:01:32 (25) | 56 min |
| predict 20260918T174135Z | 17:45:36 → 18:10:38 (21) | 18:10:43 → 18:38:48 (23) | 18:38:57 → 18:55:00 (23) | 53 min |
| evaluate 20261005T221055Z | 22:12:31 → 22:36:42 (25) | 22:36:50 → 23:06:26 (25) | 23:06:45 → 23:23:42 (25) | 54 min |
| evaluate 20261006T154811Z | 16:37:38 → 17:03:27 (25) | 17:03:48 → 17:30:42 (25) | 17:32:00 → 17:53:19 (25) | 54 min |

In every predict run, each engine's first cell started after the previous
engine's last, claude then codex then gemini; the two smallest predict runs
(20260918T195102Z, 16 jobs; 20260919T192714Z, one gemini job) follow the same
order. Two evaluate runs carry an exception, and neither touches a counted
grading. In 20261006T192524Z one codex-judge job started at 19:26:01, two
seconds before the first claude-judge job; it is the job cancelled to release
that run, recorded as codex-judge's one cohort `died` fact, and graded nothing.
In 20261007T150255Z thirteen gemini-judge jobs started first, at 16:05:09,
and all failed (gemini-judge's 13 cohort `died` facts); that run's
gemini-judge gradings come from jobs started from 16:42:52, after codex-judge's
first job (16:23:01) and last (16:41:45). So every job that produced a counted
grading started in registry order.

Late cells and snapshot dates, over the registered cohort's 120 cert events
(360 counted cells; the counted `run_id` per predictor from the cohort cut):
the share of an engine's cohort predictions whose run is later than the
earliest sibling engine's run on the same event is claude-baseline 0 of 120,
codex-baseline 4 of 120 and gemini-baseline 5 of 120 — the re-minted cells
behind the predict-seam `attempt.json` facts in *Engine losses stay owed*
(codex 4 `no_output`; gemini 4 `no_output`, 2 `partial`, 1 `quota`, some
re-minted more than once). One of gemini-baseline's five is on a grant
event, the GVR No. 25-918 (`scotus/73280426`): its counted cell ran in
20260917T181231Z, the other two engines' in 20260916T170237Z. Snapshot as-of date (`context.snapshot_date`)
against run date: on the 110 cert/distribution events every engine's snapshot
is dated the run day or the day before — claude-baseline 73 same-day and 37
one day earlier, codex-baseline 75 and 35, gemini-baseline 71 and 39. The 10
CVSG cells per engine are placed at their invitation, 79 to 338 days before
the run, identically for all three engines.

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

No arrival figure is quoted in this write-up. The refreshed board carries no
`cert@arrival` stage section — its stage blocks are `interim@arrival`,
`interim@response-filed` and `interim@response-requested` only — because no
cert/arrival cell has resolved: the cohort cut lists 17 counted cert/arrival
events — 14 baseline band and 3 federal — all pending, none registered. With nothing graded
on the arm there is no per-rule cut to make, and the omitted section is an
empty state, not a result.

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
> considered the petition are on the frozen board, because the pre-registered
> counting rule admits them, so they stay. None of them is in the registered
> cohort; the registered cut already excludes them. Their cells were made after that conference had sat and
> after the 2026-10-01 grant list had issued, and a petition still undisposed
> after the grant list is very unlikely to have been granted from that
> conference, so those forecasts were made with information a forecast at the
> conference could not have had. Wherever any of them is graded, every
> board-wide figure in section 3 carries a sensitivity line without them;
> while none is graded, the lines would equal their headlines and are omitted,
> and the reconciliation says so.

**The reconciliation, filled.** Read off `conference-set --counted
--registered-at 2026-09-15` at the corpus vintage of this fill (newest pull
2026-10-09, newest stored snapshot 2026-07-13), `conference_fallbacks` 0.

The cut's registered count matches the rule's census arm for arm: **110**
cert/distribution, **10** cert/cvsg and **3** interim/arrival, 123 in all. By
status:

| Arm | Band (as the counted cells froze it) | Registered | Scored | Resolved, unscored | Pending | Unforecast |
| --- | --- | --- | --- | --- | --- | --- |
| cert/distribution | baseline | 69 | 61 | 0 | 8 | 0 |
| cert/distribution | elevated | 38 | 28 | 0 | 10 | 0 |
| cert/distribution | high | 1 | 1 | 0 | 0 | 0 |
| cert/distribution | federal | 1 | 1 | 0 | 0 | 0 |
| cert/distribution | state | 1 | 0 | 0 | 1 | 0 |
| cert/cvsg | high | 10 | 0 | 0 | 10 | 0 |
| interim/arrival | (no band) | 3 | 0 | 0 | 2 | 1 |

On cert/distribution, 91 registered events are scored, 19 pending, none
resolved-unscored and none unforecast. 109 of the 110 were cut against the
2026-09-28 conference and one against 2026-10-09. The cut's band mix,
69 baseline / 38 elevated / 1 high / 1 federal / 1 state, differs from the
registered table's 70 / 37 by one event. The *moved* command names 14
registered distribution events whose conference changed:

- **Before the cut, one:** No. 25-1341 (`scotus/73500243`), registered for
  2026-09-28 and forecast in run 20260917T214606Z against the 2026-10-09
  conference, its cells frozen `elevated`; it is the
  only event whose cut conference differs from its registered one, and it is
  pending. The cut does not carry each event's registered band, so the one
  band difference is read as this move rather than checked against the
  census blob.
- **After the cut, thirteen**, each forecast against 2026-09-28 and pending
  since: Nos. 25-882, 25-1062, 25-1098, 25-1187 and 25-1240 (elevated);
  25-1103, 25-1158, 25-1163, 25-1273 and 26-13 (baseline), now on the
  2026-10-09 conference; 25-1269 and 25-1314 (baseline), now on 2026-10-16;
  and 25-1115 (state), now on 2026-10-09.
- **Between its cells, or never forecast:** none on cert/distribution; the
  *split cells* command returns an empty list.

Of the 19 pending registered distribution events, the 14 above moved, and
five — Nos. 25-1070, 25-1250, 25-1350 and 25-1358 (elevated) and 25-1347
(baseline) — still carry the 2026-09-28 conference in the corpus column with
no outcome. Every pending event's payload is dated 2026-10-09 except
No. 25-1314's, dated 2026-10-02, before the opening order list: its `pending`
means "no outcome as of that payload". The 10 CVSG events are all pending,
each cut at its invitation (conferences 2025-10-10 through 2026-06-29). Of
the three interim/arrival events, the two the deriver minted at registration
were forecast — No. 25A622 (`scotus/73279700`) and No. 26A163
(`scotus/9526000163`), both pending — and the third, No. 26A273
(`scotus/9526000273`), has no counted cell (`unforecast`; its application
resolved `withdrawn` 2026-09-25).

Beside the cohort and never inside it, the cut's counted distribution events
outside the registered rule: 37 cut against the 2026-09-28 conference, 26
against 2026-10-09, 10 against 2026-10-16 and 1 against 2026-11-06. Six of
those 37 are scored — the post-conference first forecasts below — and they
are the whole difference between the cohort and the board: the ranked board's
`events_scored` is **97** for each entry and for the population, the 91
scored registered events plus those 6.

No re-measured band mix is owed. Every registered cert event carries all
three counted predictors (section 1), so the surviving cohort is the whole
registered table, not the head of a partly drained queue; the two scheduled
predict ticks cancelled in the drain window (2026-09-16 18:10Z and
2026-09-17 20:27Z) left no cert event unforecast.

**Extraordinary writs, filled.** `release-sensitivity` read the stored
opening entry of 208 cases (`cases_scanned`) and identified exactly the two
named above,
with `not_certiorari_not_rule_20` and `unclassified` both empty — no further
such petition is on the board, in the cohort or not:

| Petition | Opening entry | Band | Outcome | claude-baseline | codex-baseline | gemini-baseline |
| --- | --- | --- | --- | --- | --- | --- |
| No. 25-1252 (`scotus/73299074`) | "Petition for a writ of mandamus filed." (2026-04-24) | baseline | denied 2026-10-05 | 0.01 | 0.07 | 0.005 |
| No. 25-1315 (`scotus/73500218`) | "Petition for a writ of mandamus filed." (2026-05-20) | baseline | denied 2026-10-05 | 0.003 | 0.005 | 0.001 |

Each has one event, the registered `evt-petition-disposition` on
cert/distribution, graded by all three judges (9 gradings each); both
payloads are dated 2026-10-05. Against the OT2025 baseline pool of about
5.12%, the per-grading skill on No. 25-1252 runs from +0.96 (claude-baseline)
and +0.99 (gemini-baseline) down to −0.87 for codex-baseline's 0.07 — the
swing the prose above describes, on a petition the Court denied. Their
removal moves only the baseline row's skill (section 3's sensitivity line).

**Post-conference first forecasts, re-counted at fill time.**
`release-sensitivity`'s `.blocks.post_conference_first_forecasts_excluded`,
read at corpus newest pull 2026-10-09 / newest stored snapshot 2026-07-13
(208 stored payloads read, none missing, dated 2026-10-02 to 2026-10-09):
**16** board events, all considered at the **2026-09-28** conference;
**6 resolved and 6 graded**; **0 registered**. `unreadable` and
`scored_after_conference_outside_subset` are both empty, and
`not_after_grant_list` is empty — every first forward cell ran on or after
2026-10-03, after the 2026-10-01 grant list, so the paragraph above holds for
all 16. `lines_equal_headline` is false, so section 3 carries the lines
without them (54 board cells removed).

| Petition | Case | First forward cell (run) | Status |
| --- | --- | --- | --- |
| No. 26-66 | `scotus/9026000066` | 2026-10-04 (20261004T201824Z) | denied 2026-10-05, graded (9 cells) |
| No. 26-79 | `scotus/9026000079` | 2026-10-04 (20261004T201824Z) | denied 2026-10-05, graded (9 cells) |
| No. 26-80 | `scotus/9026000080` | 2026-10-04 (20261004T201824Z) | denied 2026-10-05, graded (9 cells) |
| No. 26-95 | `scotus/9026000095` | 2026-10-04 (20261004T201824Z) | denied 2026-10-05, graded (9 cells) |
| No. 26-121 | `scotus/9026000121` | 2026-10-04 (20261004T201824Z) | denied 2026-10-05, graded (9 cells) |
| No. 26-183 | `scotus/9026000183` | 2026-10-04 (20261004T201824Z) | denied 2026-10-05, graded (9 cells) |
| No. 25-1343 | `scotus/73500246` | 2026-10-03 (20261003T200236Z) | pending |
| No. 25-1415 | `scotus/73529868` | 2026-10-03 (20261003T200236Z) | pending |
| No. 26-130 | `scotus/9026000130` | 2026-10-05 (20261005T212916Z) | pending |
| No. 25-1246 | `scotus/73292081` | 2026-10-05 (20261005T231540Z) | pending |
| No. 25-1338 | `scotus/73500240` | 2026-10-05 (20261005T231540Z) | pending |
| No. 26-43 | `scotus/9026000043` | 2026-10-05 (20261005T231540Z) | pending |
| No. 25-1313 | `scotus/73500214` | 2026-10-06 (20261006T142731Z) | pending |
| No. 25-1388 | `scotus/73500290` | 2026-10-06 (20261006T142731Z) | pending |
| No. 26-461 | `scotus/9026000461` | 2026-10-08 (20261008T143010Z) | pending |
| No. 26-462 | `scotus/9026000462` | 2026-10-08 (20261008T143010Z) | pending |

The six graded events are all baseline band and all OT2026 dockets. Their
first forward cells ran on 2026-10-04, after the conference had sat and the
grant list had issued but the day before the 2026-10-05 order list that
denied them.

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

**Pass run 2026-10-09** over both filled documents, with every figure checked
against the saved outputs of the commands that produced it (the refresh
commit's boards, the fill export, `release-sensitivity`, the cohort cut,
`segment-anchors`, the `attempt.json` tally and the run-start reads). Verdict:
**approve with fixes**. No quoted number was found wrong. Disposition:

1. *Blocker, public page:* the headline counted the 97 board petitions while
   "every forecast … before the Court met" and the last-merge line held only
   for the 91 pre-registered ones. **Fixed:** the headline separates the 91 pre-registered from the 97 scored, those
   lines are scoped to the pre-registered set, and the six late-forecast
   petitions are named beside them.
2. *Blocker, public page:* "each run the same way" overstated section 3's
   run-order disclosure. **Fixed:** the models line now says they did not run
   under identical conditions and points to the disclosure.
3. *Recommended:* the cross-band rank key and the pooled prior-Term skill
   beside the in-sample benchmark lacked their sensitivity lines and a
   decomposition. **Fixed:** both are labelled as quoted only for the order or
   as the benchmark's registered companion, the lifts are decomposed to the
   petitions behind them, and the missing lines are added.
4. *Recommended:* in the baseline band, where every petition was denied,
   skill rewards forecasting low and the pending shortfall favours the lower
   forecaster. **Fixed:** stated in section 3's grants paragraph and on the
   public page.
5. *Recommended:* "873 graded forecasts" on the public page. **Fixed:** 873
   gradings of 291 scored forecasts.
6. *Recommended:* the public page's GVR miss rule needed the fact that the GVR
   hits were explicit GVR calls. **Fixed.**
7. *Nits:* the uptake denominator (1,411 files, 743 carrying the mark), the
   gemini-baseline late cell on No. 25-918, the sensitivity-line layout
   sentence, "G" written out as "granted", and "relisted once" softened to
   "relisted". **All fixed.**

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
