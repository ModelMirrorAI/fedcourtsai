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

This document registers the baselines, the side-coding method two of them
need, and the reading rule. What is built today, and what each remaining piece
owes, is at the end.

## The four baselines

1. **Majority alignment.** Every participating Justice of the conservative bloc
   votes with the judgment and every other participating Justice dissents,
   whichever side wins. It predicts no outcome, so it has no Brier score. It
   needs no case coding, and it is the paper's rule, so the figures it yields
   compare directly with theirs.
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
before Justice Barrett they are the five of their day, Kennedy among them. The
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

- **When.** At grant, one agent pass reads only the record as it stands. It
  records which party argues the conservative position and a score `s` in
  [0, 1] for how conservative the outcome will be.
- **How it is committed.** The pass is committed like a prediction and never
  revised. It is stored as its own baseline predictor and kept for analytics.
- **Past Terms.** OT2022–OT2025 grants are coded by the same pass, run on each
  case's record as of grant time (replay mode). The agent may know those
  outcomes from training, so every past-Term score carries a
  **contamination-risk** flag, and any fit on them is labeled as possibly
  optimistic. The clean check, a fit on scores recorded at grant time only, is
  reported separately once a full Term of them exists: OT2027 is the first
  Term that can be scored out of sample on it.

## The readings

Every reading is over the **participating bench**: everyone but a Justice
recorded as `recused` or `did-not-participate`. That denominator is the same
for every predictor on a decision, so no predictor chooses it.

- **Justice accuracy.** The fraction of participating Justices whose side the
  forecast called. A side is with the judgment (`majority` or
  `concur-in-judgment`) or in dissent. A vote in part on each side
  (`concur-in-part-dissent-in-part`) has neither side, so it is a miss for
  every baseline, none of which predicts one.
- **Exact split.** Whether the predicted count with the judgment and in dissent
  is the realized one, with no vote in part.
- **Full coalition.** Whether the predicted set of Justices with the judgment
  is the realized set, with no vote in part.
- **Outcome**, for baseline 3 only: the Brier score of P(the conservative side
  prevails) against the coded side's result.

**Reading rule.** A model's merits vote figure is read as lift over the
strongest baseline on the same reading and the same decisions, never alone.
On the corpus's own record (below), unanimity is the stronger coding-free
baseline on all three vote readings, so it is the floor a vote forecast has to
clear before its accuracy says anything about the case. Majority alignment is
reported beside it because it is the paper's rule and the shape the paper's
models overpredict.

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
read-only readout over the corpus's merits lineups.

Owed, in order:

- **The side-coding pass.** Its prompt, the run mode that executes it at grant
  and in replay over OT2022–OT2025, and where its records live in the ledger,
  with the contamination-risk flag on every replay record.
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
