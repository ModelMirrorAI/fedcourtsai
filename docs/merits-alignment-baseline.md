# The merits alignment baselines

A merits vote forecast means little until it beats the forecast a lay reader
could make without reading the case: "the Court splits along its usual
ideological lines", or "the Court agrees". Stillwell & Harrington, *Predicting
the Court* (SSRN 7096518), scored four language models on 58 argued OT2025
cases and found that much of their Justice-level accuracy was the Court's
ordinary alignment rather than case-specific analysis. Their ideology baseline
scored 69.5% Justice-level accuracy against the models' 72.2–80.3%. The models
predicted a 6–3 split in 62–91% of cases, against a realized 31%, while 43% of
the decisions were unanimous. So this repository scores its merits forecasts
beside four baselines, each labeled as a baseline wherever it appears.

This document specifies the baselines, the side-coding method two of them
need, and the reading rule; they are registered once their dated
[freeze-record.md](freeze-record.md) entry lands (*What is built*, below). What is built today, and what each remaining piece
owes, is at the end.

## The four baselines

1. **Majority alignment.** Every participating Justice of the conservative bloc
   votes with the judgment and every other participating Justice dissents,
   whichever side wins. It predicts no outcome, so it has no Brier score. It
   needs no case coding, and it is the paper's rule, applied here to a
   different population of decisions (*The record*, below).
2. **Unanimity.** Every participating Justice votes with the judgment: 9–0.
   It also predicts no outcome. It is the floor for the exact split and the
   full coalition.
3. **Score outcome.** P(the conservative side prevails) is the case's
   alignment score `s`, and `s > 0.5` is the implied call. It is Brier-scored.
   A calibrated variant applies a monotone transform of `s` fitted on past
   Terms.
4. **Score votes.** Each Justice carries a fixed position from a published
   ideal-point ordering, and one spread parameter `k` maps `s` to each
   Justice's vote: a small `k` gives 9–0, a large `k` gives the ideological
   6–3, and the splits fall in between. It is reported twice: out of sample,
   with `k` and the outcome transform fitted on past Terms only; and in sample,
   fitted on the scored Term itself, as a labeled ceiling that no forecast
   could have used.

No baseline predicts unanimity of reasoning or the grounds of decision, and
each is scored only on the claims it makes.

### The conservative bloc

The bloc is a fixed rule, not an estimate: **the Justices appointed by a
Republican president.** On the OT2025 bench those are the six the paper's rule
names (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett). On the benches
before Justice Barrett they are the five of their day (Kennedy among them
through OT2017). The
rule needs no data beyond the roster, and a Justice it would misplace on some
axis stays where it puts them, since moving one would be a judgment made after
seeing the votes. `pipeline.alignment_baseline.CONSERVATIVE_BLOC` and
`OTHER_BLOC` carry it, and a test holds the two to partitioning every Justice
in `pipeline.justices.SERVICE`, so a new appointment that misses the module
fails the suite rather than reading as a dissent.

### The side coding

Baselines 3 and 4 need, for each case, which side is the conservative position
and how conservative the outcome will be. That coding is a judgment, and it is
where much of a baseline's apparent skill could hide, so it is made once and
recorded before the decision:

- **What it reads.** One agent pass, the side coder
  (`.github/prompts/alignment-side-code.md`), reads each granted case as it
  stood on the grant date and nothing else: the caption, the petitioner as
  captioned, the court below, the grant date and the stored questions
  presented. The caption and petitioner are the corpus's as of its latest
  pull, so a party substituted after the grant shows under its new name, a
  timing difference rather than an outcome. The run mode that executes the
  coder (`run-analytics` `alignment-side-code`, below) denies it every
  retrieval tool and moves the committed record out of its tree, so a code
  cannot rest on a filing, a docket, an outcome or a search the extract does
  not hold.
- **What it records.** Which party, petitioner or respondent, argues the
  conservative position; the score `s` in [0, 1], read as P(the conservative
  side prevails); a `valence` (`clear`, `weak` or `none`) saying how clearly
  the case divides on ideological lines, kept for analytics and read by no
  baseline's fit; and a one-sentence note. The conservative side follows one
  stated principle: the position the Justices appointed by Republican
  presidents would be expected to take if the Court divided along its usual
  lines, the same line the majority-alignment bloc draws. The prompt lists
  where that principle points, row by row (criminal procedure, religion,
  speech, firearms, discrimination, abortion, economic regulation, agencies and
  the executive, unions, federalism and remedies, immigration, elections), with
  a fallback for a question no row decides. It is the repository's own guide,
  not the Supreme Court Database's decision-direction coding, which places a
  civil-liberties claimant on the liberal side and so reverses the modern
  alignment on free exercise, compelled speech and firearms. A side is always
  called, even on a case with no valence.
- **What the score is graded against.** The conservative side prevails where
  the judgment below is disturbed and that side is the petitioner, or left
  standing and that side is the respondent, on the merits binary
  [decision-model.md](decision-model.md) declares: a reversal, a vacatur and
  an affirmance in part are disturbed, and a DIG and an equally divided
  affirmance are not. A terminated case has no judgment and is not graded.
- **How it is committed.** Each code lands in
  `data/merits-alignment/alignment-side-codes.json` (`AlignmentSideCodes`)
  and is never revised: `fedcourts alignment-side-codes` refuses a run that
  would replace a committed code. That guard is in the publish step; `validate
  data` checks the file's schema but not its history, so a hand edit of a
  landed entry is caught only by review of the data PR that makes it. The grant date, mode, contamination flag,
  model, run and day are stamped by the harness from the extract and the run,
  never taken from the coder.
- **Which cases.** The frame is every SCOTUS cert grant that opened a merits
  proceeding and did not ride the cert order, granted in OT2021 or later, on
  the live slice (`pipeline.alignment_side`). Starting at OT2021 covers every
  case decided from OT2022 on, since a case is decided in its grant Term or
  the next. A case with no stored questions presented has nothing to code from
  and is counted, not guessed at.
- **Past Terms.** A case already decided when its extract is cut is coded in
  **replay** mode. The coder is not told which cases those are, and is told
  not to recall outcomes, but it may know them from training, so every replay
  code carries the **contamination-risk** flag and any fit on them is labeled
  as possibly optimistic. A case still undecided when cut is coded in
  **forward** mode. Undecided is not the same as grant-time, since a forward
  code made after argument may read what the argument said, so the clean
  check reads only **clean** codes (`pipeline.alignment_side.is_clean`):
  forward codes made within `CLEAN_LAG_DAYS` (30) of their grant and before
  their case's argument, which an expedited case can hold inside the lag. A replay case decided after the coder's training cutoff is
  plausibly uncontaminated, but it keeps the flag: the cutoff is not recorded
  per code, and a fit that relied on it would rest on an unverified claim.
  The clean check is a fit on clean codes only, reported separately. Codes
  begin after OT2026 opened, so OT2026's early grants cannot be clean, and the
  first full Term of clean codes is the OT2027 grants, most of them decided in
  OT2028. A clean out-of-sample reading fits on those and is scored on the
  OT2028 grants, if the run has coded every grant within the lag throughout.
- **Valence in the fits.** The fits of the outcome transform and of `k` pool
  every code, `none` included, because the baselines read every case; every
  fit is also reported split by valence, so a `k` pulled toward 9–0 by
  forced calls on cases with no ideological content is visible beside the
  `clear` cases' own.

On the production corpus whose newest pull is 2026-10-31, the frame holds 331
grants, 29 of them with no stored questions presented, so a first run codes
302 cases: 267 in replay and 35 forward. That fits one run, whose extract is
capped at `CODE_ROW_CEILING` rows (400), earliest grants first.

```bash
uv run fedcourts alignment-side-extract --out <outside the checkout>/extract.json \
  --modes-out <outside the checkout>/modes.json
```

## The readings

Every reading is over the **participating bench**: everyone but a Justice
recorded as `recused` or `did-not-participate`. That denominator is the same
for every predictor on a decision, so no predictor chooses it.

- **Justice accuracy.** The fraction of participating Justices whose side the
  forecast called. A side is with the judgment (`majority` or
  `concur-in-judgment`) or in dissent. A vote in part on each side
  (`concur-in-part-dissent-in-part`) has neither side, so it is a miss for
  every baseline, none of which predicts one. A model that predicts a vote in
  part is read the same way: its call has neither side, so it is a miss
  whatever the Justice did, and the reading stays symmetric between model and
  baseline.
- **Exact split.** Whether the predicted count with the judgment and in dissent
  is the realized one, with no vote in part. It ignores who is on which side,
  so majority alignment is credited for a 6–3 in which three conservatives
  dissent: an exact split is not evidence of alignment.
- **Full coalition.** Whether the predicted set of Justices with the judgment
  is the realized set, with no vote in part.
- **Outcome**, for baseline 3 only: the Brier score of P(the conservative side
  prevails) against the coded side's result.

**Reading rule.** A model's merits vote figure is read as lift over the
strongest baseline on the same reading and the same decisions, never alone.
Lift is the paired difference, model minus baseline, over exactly the
decisions the model is scored on, in percentage points. Which baseline is
strongest is recomputed on those decisions each time, not carried over from
another population. Any interval on a lift is clustered by decision: a
decision's nine votes are correlated, so 2,589 Justice votes are about 289
clusters, not 2,589 independent trials, and one Term is roughly 50–60
decisions, so a lift of a few points is not evidence of skill on its own. On
the corpus's own record (below), unanimity is the stronger coding-free
baseline on all three vote readings. Majority alignment is
reported beside it because it is the paper's rule and the shape the paper's
models overpredict.

The readout below pools every complete lineup unconditionally. That is a
description of the record, not yet a floor in the sense
[decision-model.md](decision-model.md) requires (*the floor must be
conditioned the way the predictor is conditioned*): the floor a model's figure
is read against is computed on the model's own scored decisions, which is
part of *Scoring beside the models*, below.

Justice accuracy here is side-level, as the paper scores it. The leaderboard's
`mean_vote_accuracy` (`pipeline.evaluate.bench_vote_accuracy`) instead matches
the vote value exactly, so a concurrence in the judgment predicted as
`majority` is a miss there and a hit here. The floor the leaderboard reads its
figure against has to be computed under its own rule, on its own scored cells
(*What remains owed*).

## The record, on the corpus's merits lineups

`fedcourts merits-alignment-baseline` scores baselines 1 and 2 over every
complete merits lineup (`pipeline.merits_lineups`) in a range of Terms: signed
decisions whose writings seat the whole bench on a filled bench row. Per
curiams and decisions the syllabus grammar could not seat are left out, which
is selection rather than missing at random, so each Term's figure travels with
how many of its documents it covers. It reads the corpus, writes nothing, and
no cell, score or board reads it.

```bash
uv run fedcourts merits-alignment-baseline --first-term 2020 --last-term 2025
```

Run on the production corpus whose newest pull is 2026-10-31 (the newest
stored snapshot row is 2026-07-13), over 289 of 345 documents from OT2020 to
OT2025, pooled:

| Baseline | Justice accuracy | Exact split | Full coalition |
|---|---|---|---|
| Majority alignment | 65.4% (1,693 / 2,589) | 24.9% (72 / 289) | 14.5% (42 / 289) |
| Unanimity | 82.2% (2,129 / 2,589) | 42.2% (122 / 289) | 42.2% (122 / 289) |

On OT2025 alone, 51 of 70 documents, majority alignment scores 67.5% Justice
accuracy and 22 of the 51 decisions (43.1%) were unanimous. The paper's 69.5%
and 43% are over its own 58 argued cases, a different population from the
corpus's complete lineups, and it does not say how it treats a vote in part;
the two are close, not the same measurement. These figures are a snapshot of a
command's output on one corpus vintage: re-run the command for current ones.

## What is built, and what remains owed

Built: baselines 1 and 2, the bloc rule, the three vote readings, and the
read-only readout over the corpus's merits lineups; and, for the side coding,
the coder's prompt, the extract (`fedcourts alignment-side-extract`), the
committed artifact and its append-only publish step (`fedcourts
alignment-side-codes`), and the run mode that executes them.

The run mode is `run-analytics` `alignment-side-code`, the topic-labeling
lane's third frame ([pipeline.md](pipeline.md)), dispatched or on a weekly
Thursday cron, so each week's grants are coded inside `CLEAN_LAG_DAYS`. The
coder holds no shell, no delegation and no retrieval tool, and the committed
record (`data/`, `metrics/`) is out of its tree while it runs. The modes
sidecar reaches the coding job only after the agent has exited, and the
publish step checks the extract against the digest the extract job recorded
before it stamps a grant date from it. Each round waits on the review hold,
priced at the side coder's provisional rate
(`planning_rates.SIDE_CODE_RATES_USD_PER_ROW`), and every run's spend lands in
the labeling lane's spend ledger. The codes reach `main` as a reviewed PR on
the fixed branch `merits-alignment/side-codes`, so the first run's 302 codes
are read by a maintainer before any fit reads them.

Owed, in order:

- **The first run.** A rehearsal from `staging`, which publishes nothing,
  then the production run on `main`; its spend record re-anchors the
  provisional rate.
- **Baselines 3 and 4.** The ideal-point source and its terms of use
  (`docs/data-sources.md`), the outcome transform and the fit of `k`, each with
  a `stats-reviewer` pass on the fit and the reading rule.
- **Scoring beside the models.** Baseline records at the same merits moments
  as the models, scored in the leaderboard's merits blocks under the
  leaderboard's own vote rule and labeled as baselines, which also discharges
  the naive floor for `mean_vote_accuracy` that
  [release-ot2026-merits.md](release-ot2026-merits.md) owes. A change to the
  shape of a committed record the public site reads needs its matching site
  PR.
- **Registration.** A dated entry in [freeze-record.md](freeze-record.md)
  before the first merits block that scores a baseline.
