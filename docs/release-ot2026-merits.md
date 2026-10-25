# Release write-up: the OT2026 merits docket

This document is the skeleton and evidence plan for the merits part of the
project's end-of-Term release. [milestones.md](milestones.md) calls that
release Release 3, the end-of-Term retrospective, once the OT2026 merits
docket resolves (about June–July 2027). The release's cert retrospective has
its own sections and is outside this document. This document defines when
the merits part is done. It is written before any merits outcome exists, so
the claims are bounded by the process rather than by what the numbers turn
out to be.

It follows the conventions of the long-conference write-up,
[release-ot2026-long-conference.md](release-ot2026-long-conference.md) (*How to
read this document* there):

- each section says **State**, **Evidence** and **Prose**;
- every unfilled figure is a placeholder wrapped in single guillemets (U+2039
  and U+203A), and the sentence carrying it names the command that fills it;
- no placeholder is ever replaced by an estimate.

One difference: some of the evidence a merits release needs has no command or
registration yet. Each such item is marked **Owed** in place, and *Owed before
publication* at the end collects them. An item that may be resolved by
stating its absence says so, and stating the absence clears it. The draft is
not publishable while either check below returns anything:

```bash
grep -n "$(printf '‹')" docs/release-ot2026-merits.md
grep -n '\*\*Owed' docs/release-ot2026-merits.md
```

**Written by AI.** This document was drafted by Claude (Anthropic), working in
Claude Code under the maintainer's direction, from the merits design in
[decision-model.md](decision-model.md) and
[outcome-decomposition.md](outcome-decomposition.md) and from read-only
censuses of the corpus and the ledger.

**Who runs what.** Every dispatch named below is the maintainer's. A read-only
command can be run from any checkout with the corpus pulled, or read in place
with `--corpus-backend ranged`.

**Timing.** A merits figure needs decided merits cases, and the Court decides
most argued cases between January and June. Before the end of the Term, the
only merits evidence is retrospective (section 7). What, if anything, of the
merits stream an earlier release carries is the maintainer's call, and this
document does not presume it.

## 1. The covered population

**State.** Which plenary grants the release covers, and what became of every
other one. The population is every OT2025 and OT2026 grant that opens a
merits proceeding, keyed to the October Term of its grant date. For each grant
Term the write-up states:

- the total number of plenary grants, ‹plenary grants›;
- how many carry a committed merits prediction, ‹forecast›;
- every other grant, listed with its status, so that none is missing without
  notice.

A grant whose judgment rode the cert order (a GVR, or a summary disposition
under a `granted` label) is a cert-stage fact. It is counted apart as
`order_riding`, never silently dropped.

**Evidence.** The census, run at the refresh commit with the corpus pulled:

```bash
uv run fedcourts merits-coverage --first-term 2025 --last-term 2026 > merits-coverage.json
```

It gives every plenary grant exactly one status. The table lists them in the
order the census tests them, and the first match wins:

| Status | Meaning |
|---|---|
| `forecast` | A committed merits prediction exists. |
| `terminated` | The case ended without a decision (section 6). |
| `decided_unforecast` | Decided before the forward stream reached it. |
| `stale` | Still pending on the record after the stale-grant bound. |
| `out_of_scope` | Refused by predict scope; the reason is named. |
| `no_event` | Pending and in scope, but no open merits event. A **hole**. |
| `owed` | An open event waiting for its first round. |
| `not_forecastable` | Has an open event, but the merits admission refuses it. A **hole**. |

The command exits 3 when it finds a hole. The write-up names every hole.
Grants still `owed` at publication are listed with their grant dates.

**Prose (settled).**

- **The forward window.** The forward merits stream mints an event when it
  detects a grant. OT2025 grants made before the stream existed show as
  `decided_unforecast` with no merits event. They are outside the forecast
  population by construction. The write-up states their count rather than
  folding them in.
- **IFP grants.** In-forma-pauperis grants are forecast from the scope change
  recorded in [freeze-record.md](freeze-record.md) (the IFP scope rule stops
  at a merits grant). Merits cells made before that change are paid-only, so
  the population behind the cells changes at that date. The write-up states
  how many counted cells fall on each side of the change.
- **Original jurisdiction.** Original-jurisdiction cases are outside predict
  scope, even when argued.
- **Consolidated dockets.** These count once per docket, so one opinion can
  score several cells. **Owed:** a per-argued-case aggregation of the merits
  figures, so the write-up can state n per docket and per argued case.
- **Decided versus covered.** Grants are keyed by grant Term, and a late
  OT2026 grant is argued the next Term. Every scored figure below is therefore
  stated over the decided cases, ‹decided›, with the undecided remainder
  named.

## 2. The counted cells

**State.** Which cells the scored figures count. Counting is per window, the
rule in `process_version.py` (*Counting is per window*):

- A blessing opens a counting window for each predictor digest.
- A cell counts when its digest has a window containing its stamp.
- Where one predictor holds cells from several windows on one event, only the
  earliest still-counting window's cell counts.
- A successor closes a window without de-counting it. Only a dated revocation
  de-counts.

The write-up lists the windows in force at the refresh commit,
‹`COUNTING_WINDOWS` labels and instants›. For each moment and each predictor,
it gives the census of counted versus uncounted merits cells, ‹per-window
census›. Cells provisioned with no snapshot cutoff are never pooled with cut
cells ([freeze-record.md](freeze-record.md) records the boundary).

**Owed:** a per-window census within a leaderboard stage block. A stage block
carries per-entry `windows` today, but no process-scope census of the cells
it excludes.

## 3. The headline: judgment disturbed, per moment

**State.** The registered merits claim is the probability that the Court
disturbs the judgment below: reverses, vacates, or reverses in part. Each
counted cell is scored by Brier on that binary. Skill is measured against the
pooled strictly-prior merits base rate (`merits_base_rate`), which is defined
only where at least `MERITS_BASE_RATE_MIN_PARSED` parsed judgments pool
([decision-model.md](decision-model.md)).

The headline is stated **per moment**, because `merits@grant` and
`merits@briefed` are separate populations and a skill figure means something
only within one. For each moment and each predictor, the write-up states:

- n, the number of counted cells;
- mean Brier;
- skill against the base rate.

It also states accuracy on the exact-match judgment axis (`judgment_correct`),
beside a stated naive floor: the most common judgment in the strictly-prior
pool, conditioned the way the predictor is. A dismissal as improvidently
granted and an equally divided affirmance score as *undisturbed*, because
both leave the judgment below standing, and both sit in the baseline's
denominator.

**Evidence.**

- *The baseline:* the merits section of `metrics/statpack.json` at the refresh
  commit. Its pool is ‹parsed› parsed judgments, with a disturbed rate of
  ‹disturbed_rate›, over grant Terms ‹first›–‹last›, with
  ‹cert_order_excluded› order-riding rows removed.
- *Per-cell scores:* the `stamp-cell` Brier and skill on each graded merits
  evaluation.
- *The per-moment figures:* the leaderboard's `merits@grant` and
  `merits@briefed` stage blocks. The leaderboard keys its non-cert stages
  `<stage>@<moment>`, so these blocks appear once a merits evaluation exists.

**Owed:**

- a reading rule for the merits stage blocks in
  [metrics/README.md](../metrics/README.md), saying what may be read from
  them and that they are never ranked;
- a merits accuracy floor. The board's floor is cert-only today;
- `claim-scores` coverage of the merits claim sets, `merits-v1` and
  `merits-v2` (whose authorship rows are reported beside the binary claim and
  enter no total). `claim-scores` rolls
  up only cert's first moment today.

**Prose (settled).** A merits figure is never compared with a cert figure.
The two stages answer different questions against different baselines, and
the leaderboard keeps every `stage@moment` population apart.

## 4. Calibration and the engines compared

**State.** Two analyses:

- **Calibration** of each predictor's P(disturbed) per moment, the merits
  analog of the long-conference write-up's section 3: binned forecasts
  against realized rates.
- **A paired comparison** of the engines at equal coverage, which cancels the
  baseline term ([outcome-decomposition.md](outcome-decomposition.md), *Why
  the difference form*). This is the comparison that carries a skill claim
  between engines.

The write-up also states which grants each engine covered and which it did
not.

**Owed:** the command that prints merits calibration and the paired
equal-coverage comparison. Until it exists, this section states its absence.

## 5. The baseline and the smoothing rule

**State.** The pool behind every skill figure, the lookback window, and the
smoothing rule if one applies.

**Prose (settled).** The pooled merits baseline rests on hundreds of parsed
judgments. At that size its estimation error, about `π(1−π)/n`, is a few
ten-thousandths of a Brier point per claim. That is well below the per-Term
drift of the rate itself, so the pooled headline does not depend on smoothing.
`merits_base_rate` has no fee-class, Term or originating-court cut today. A
smoothing rule becomes owed only if the release publishes a figure scored
against such a cut, whose pool can fall toward the floor of 30. There the
error is about `0.007` per claim
([outcome-decomposition.md](outcome-decomposition.md)), the same order as the
drift.

If the release publishes a cut, the smoothing rule is registered in
[freeze-record.md](freeze-record.md) before the first counted merits outcome
resolves. It must keep the strictly-prior rule: a cut's rate can shrink only
toward a strictly-prior pool. It must also settle the tension with the
conditioned-floor rule, since shrinking a cut toward a coarser rate unconditions
it. Choosing the rule and its strength is the maintainer's pre-registration.
Until a rule is registered, a cut's figure is published as coverage, never as
evidence of skill.

## 6. Votes, and cases that end without a decision

**State.** Per-Justice vote accuracy (`mean_vote_accuracy`) for each
predictor. It is scored only on the merits moments and only over complete
whole-bench records ([decision-model.md](decision-model.md)). That population
is the signed, parsed opinions that agree with the Granted & Noted list, and a
consolidated case enters the mean once per docket. The write-up states:

- the scored count, ‹vote cells scored›;
- the decided cases without a complete record, ‹incomplete›, each with its
  reason;
- the naive floor the accuracy is read against (for example, every Justice
  voting with the predicted majority), with the lift over it.

**Evidence.** The opinions vote source stamps merits outcomes through the
`opinion-votes` pass on `run-repair`. The maintainer runs it after each
opinion day of the Term: a dry run first, then an apply bounded by the dry
run's count (*Maintenance passes* in [data-pipeline.md](data-pipeline.md)):

```bash
gh workflow run run-repair.yml --ref main \
  -f repair=opinion-votes -f repair_mode=dry-run
gh workflow run run-repair.yml --ref main \
  -f repair=opinion-votes -f repair_mode=apply -f repair_bound=<would stamp N>
```

`fedcourts granted-noted-check` cross-checks the stamped Terms.

**Owed:** the stated naive floor for `mean_vote_accuracy`.

**Terminations.** The write-up also covers the forecast merits events that
ended without a disposition: a voluntary dismissal, dismissal as moot,
abatement, or a grant the Court vacated. It states how many there were and
what happened to their cells. A termination never scores as *undisturbed*.

**Owed:** a terminal record for a terminated merits event, so its cells are
de-counted visibly rather than left on an open event.

**Prose (settled).** Vote split and margin are pre-registered as outcomes
only. Authorship is declared as distribution claims under a set version no
moment names yet. None of the three is scored.

## 7. Retrospective evidence

**State.** Any score from replaying decided cases is retrospective. It is
reported in its own section, stratified apart (`classify_stratum`), and never
pooled with forward skill. The models may already know those outcomes, so a
replay score bounds nothing about forward skill.

**Owed:** either a merits replay arm on `run-backtest`, covering OT2025's
argued cases first and priced in [budget.md](budget.md) before its first run,
or a statement here that none ran.

## 8. Cost

**State.** What the merits stream cost over the Term, per moment and per
engine, from the committed `usage.json` records, ‹merits spend›. Also stated:
the per-cell rate the budget planned against.

## 9. The `stats-reviewer` pass

**State.** The same pass as the long-conference write-up's section 7, run on
the filled draft. Every figure is checked against the command that produced
it, at the refresh commit.

## 10. The publishing tag

**State.** That the published figures correspond to an exact commit on `main`.
The tag follows the long-conference write-up's section 8:

- a refresh commit;
- a fill export, built twice and checked;
- reserved DOIs for the software and dataset records;
- the filled documents promoted;
- a `results/<slug>` tag pushed by the maintainer;
- the archive records published.

The [releases.json](releases.json) entry rides the release's own pull request,
per *The release manifest* in [pipeline.md](pipeline.md).

The long-conference candidate check compares a registered cohort, its
per-protocol entries and its claim-score diffs. The merits counterparts of
these depend on sections 2 and 3.

**Owed:** a reader-facing public summary for this release, in the shape of the
long-conference public page.

## Owed before publication

| Item | Section |
|---|---|
| Per-argued-case aggregation for consolidated dockets | 1 |
| Per-window census within a leaderboard stage block | 2 |
| Merits stage reading rule, accuracy floor and merits claim-score coverage | 3 |
| Merits calibration and the paired equal-coverage comparison (or a stated absence) | 4 |
| Smoothing rule, only if a cut is published | 5 |
| Naive floor for `mean_vote_accuracy` | 6 |
| Terminal record for terminated merits events | 6 |
| Merits replay arm (or a stated absence) | 7 |
| Public summary | 10 |
