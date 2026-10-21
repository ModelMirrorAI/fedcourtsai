# Release write-up: the OT2026 merits docket

This document is the skeleton and evidence plan for the project's first merits
release. [milestones.md](milestones.md) calls it Release 3, the end-of-Term
retrospective, due once the OT2026 merits docket resolves (about June–July
2027). It defines when the release is done. It is written before any merits
outcome exists, so the claims are bounded by the process rather than by what
the numbers turn out to be.

It follows the conventions of the long-conference write-up,
[release-ot2026-long-conference.md](release-ot2026-long-conference.md) (*How to
read this document* there):

- each section says **State**, **Evidence** and **Prose**;
- every unfilled figure is a placeholder wrapped in single guillemets (U+2039
  and U+203A), and the sentence carrying it names the command that fills it;
- no placeholder is ever replaced by an estimate.

One difference: some of the evidence a merits release needs has no command
yet. Each such item is marked **Owed** in place, and *Owed before publication*
at the end collects them. The draft is not publishable while either check
below returns anything:

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

**Why the end of the Term, not mid-Term.** A merits figure needs decided merits
cases, and the Court decides most argued cases between January and June.
Release 2 (mid-Term) carries the cert leaderboard, the salience ranking and the
big-case scores. Its merits content is limited to this plan and the coverage
census in section 1. Any earlier merits evidence is retrospective and reported
apart (section 6).

## 1. The counted population

**State.** Which plenary grants the release covers, and what became of every
other one. The population is every OT2025 and OT2026 grant that opens a
merits proceeding, counted per grant Term:

- **Plenary grants.** The total is ‹plenary grants›.
- **Forecast.** ‹forecast› carry a committed merits prediction.
- **No prediction.** Every remaining grant is listed with its status, so
  none is missing without notice.

A grant whose judgment rode the cert order (a GVR, or a summary disposition
under a `granted` label) is a cert-stage fact. It is counted apart, never
silently dropped.

**Evidence.** The census, at the refresh commit with the corpus pulled:

```bash
uv run fedcourts merits-coverage --first-term 2025 --last-term 2026 > merits-coverage.json
```

It gives every plenary grant one status:

| Status | Meaning |
|---|---|
| `forecast` | Counted, subject to the process scope below. |
| `owed` | An open event awaiting a round. At publication this should be zero. |
| `out_of_scope` | The predict-scope reason is named. |
| `terminated` | The case ended without a decision. |
| `decided_unforecast` | Decided before the forward stream reached it. |
| `stale` | Pending past the stale-grant bound. |
| `no_event` | A hole. |
| `not_forecastable` | A hole. |

The command exits non-zero on any hole, and every hole is named in the
write-up.

**Prose (settled).**

- **The forward window.** The forward merits stream mints an event when it
  detects a grant. OT2025 grants made before the stream existed show as
  `decided_unforecast` with no merits event. They are outside the forecast
  population by construction, and the write-up states their count instead of
  folding them in.
- **IFP grants.** In-forma-pauperis grants are forecast from the scope change
  recorded in [freeze-record.md](freeze-record.md) (the IFP scope rule stops
  at a merits grant). Merits cells made before that change are paid-only.
- **Original jurisdiction.** Original-jurisdiction cases are outside predict
  scope, even when argued.
- **Consolidated dockets.** These count once per docket, so one opinion can
  score several cells. The write-up reports n per docket **and** per argued
  case. **Owed:** a per-argued-case aggregation of the merits figures (a
  consolidation key on the census and on the board).

**State, continued: the process scope.** Within the forecast set, a cell
counts only under the frozen process in force when the counted window opens:
‹process version and counting instant from `FROZEN_SINCE` / `COUNTING_WINDOWS`›.

Cells from earlier freezes are outside the count. Some cells were provisioned
with no snapshot cutoff, and those are never pooled with cut cells
([freeze-record.md](freeze-record.md) records the boundary).

The census of counted versus excluded merits cells per digest is
‹per-digest census›, from the leaderboard's frozen-scope build. **Owed:** a
merits stage block on the leaderboard (section 2), which is what prints that
census.

## 2. The headline: judgment disturbed

**State.** The registered merits claim is the probability that the Court
disturbs the judgment below: reverses, vacates, or reverses in part. Each
counted cell is scored by Brier on that binary. Skill is measured against the
pooled strictly-prior merits base rate (`merits_base_rate`), which is defined
only where at least `MERITS_BASE_RATE_MIN_PARSED` parsed judgments pool
([decision-model.md](decision-model.md)).

Per predictor, the write-up states:

- n;
- mean Brier;
- skill against that rate;
- accuracy on the exact-match judgment axis (`judgment_correct`).

A dismissal as improvidently granted, and an equally divided affirmance, score
as *undisturbed*. Both leave the judgment below standing, and both sit in the
baseline's denominator.

**Evidence.** The baseline: the merits section of `metrics/statpack.json` at
the refresh commit. Its pool is ‹parsed› parsed judgments, with a disturbed
rate of ‹disturbed_rate› over grant Terms ‹first›–‹last›, and
‹cert_order_excluded› order-riding rows removed. The per-cell scores: the
`stamp-cell` Brier and skill on each graded merits evaluation.

**Owed:**
- the leaderboard's `merits@grant` and `merits@briefed` stage blocks, with a
  reading rule in [metrics/README.md](../metrics/README.md) that says whether
  the merits board is ranked;
- `claim-scores` coverage of the `merits-v1` claim set, which today rolls up
  cert's first moment only.

**Prose (settled).** A merits Brier is not comparable to a cert Brier. The two
binaries have different base rates: about seven in ten merits judgments are
disturbed, against a cert grant rate near one in a hundred. Only the skill
against each stage's own baseline is read across stages, and then only as
direction, never as rank.

## 3. The baseline and the smoothing rule

**State.** Three things about the baseline every skill figure is measured
against:

- the pool it was computed from;
- the lookback window;
- the smoothing rule.

**Prose (settled).** The pooled merits baseline rests on hundreds of parsed
judgments. At that size its estimation error is a few ten-thousandths of a
Brier point per claim, well below the per-Term drift of the rate itself. So
the headline does not depend on smoothing.

Smoothing matters for any cut whose pool falls toward the floor of 30: one
grant Term, one fee class, or one originating court. There the expected error
is about `π(1−π)/n ≈ 0.007` per claim
([outcome-decomposition.md](outcome-decomposition.md)), the same order as the
drift.

**Owed:** the smoothing rule, registered in
[freeze-record.md](freeze-record.md) before the first counted merits outcome
resolves. The candidate is a beta-binomial shrinkage of each strictly-prior
pool toward the pooled all-Term rate, with a fixed pseudo-count. Then a cut's
rate moves to the pooled one as its pool shrinks, and leaves it as the pool
grows. Until the rule is registered, a merits cut below the pooled baseline
is published as coverage, never as evidence of skill.

## 4. Votes

**State.** Per-Justice vote accuracy (`mean_vote_accuracy`) for each
predictor. It is scored over complete whole-bench records only, and gated on
the judgment ([decision-model.md](decision-model.md)). The write-up states:

- the scored count ‹vote cells scored›;
- the number of decided cases without a complete record ‹incomplete›;
- the reason each one is incomplete.

**Evidence.** The opinions vote source stamps merits outcomes through the
`opinion-votes` pass on `run-repair`. The maintainer runs it as a dry run, then
as an apply bounded by the dry run's count, after each opinion day of the Term
(*Maintenance passes* in [data-pipeline.md](data-pipeline.md)):

```bash
gh workflow run run-repair.yml --ref main \
  -f repair=opinion-votes -f repair_mode=dry-run
gh workflow run run-repair.yml --ref main \
  -f repair=opinion-votes -f repair_mode=apply -f repair_bound=<would stamp N>
```

`fedcourts granted-noted-check` cross-checks the stamped Terms.

**Prose (settled).** Vote split, margin and authorship are pre-registered as
outcomes only. They are not in the declared claim set and are not scored.

## 5. Merits cases that end without a decision

**State.** How many forecast merits events ended without a disposition:

- a voluntary dismissal;
- dismissal as moot;
- abatement;
- a grant the Court vacated.

For each one, what happened to its cells. A termination never scores as
*undisturbed*, because nothing was decided about the judgment below.

**Owed:** a terminal record for a terminated merits event, so that its cells
are de-counted visibly rather than left on an open event forever. The census
in section 1 counts the terminations; the record decides what the board does
with their cells.

## 6. Retrospective evidence

**State.** Any score from replaying decided cases is retrospective. It is
reported in its own section, stratified apart, and never pooled with forward
skill (`classify_stratum`). The models may know those outcomes, so a replay
score bounds nothing about forward skill.

**Owed:** a merits replay arm on `run-backtest`, covering OT2025's argued
cases first, priced in [budget.md](budget.md) before its first run. If it has
not run by publication, this section says so and carries no figure.

## 7. The `stats-reviewer` pass

**State.** The same pass as the long-conference write-up's section 7, run on
the filled draft. Every figure is checked against the command that produced
it, at the refresh commit.

## 8. The publishing tag

**State.** That the published figures correspond to an exact commit on
`main`. The machinery is the long-conference write-up's section 8, unchanged:

1. A metrics refresh lands on `main`.
2. A fill export is built at the refresh commit.
3. The dataset DOI is reserved.
4. The filled documents are promoted.
5. The candidate export is rebuilt and checked against the fill export.
6. The maintainer pushes a `results/<slug>` tag.
7. A [releases.json](releases.json) entry names the release.

**Owed:** a reader-facing public summary for this release, following the
long-conference public page, and its `releases.json` entry.

## Owed before publication

Each item below needs building, or registering, before the draft can be
filled.

| Item | Section |
|---|---|
| Leaderboard merits stage blocks, with a reading rule | 2 |
| `claim-scores` coverage of `merits-v1` | 2 |
| Per-argued-case aggregation for consolidated dockets | 1 |
| Smoothing rule, registered before the first counted outcome | 3 |
| Terminal record for terminated merits events | 5 |
| Merits replay arm (optional; section 6 can state its absence) | 6 |
| Public summary and `releases.json` entry | 8 |
