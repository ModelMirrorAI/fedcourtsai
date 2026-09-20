# Milestones

Where the project is, and what each increment of funding buys. The scaling
plan is four milestones taken in order, each with the annual funding level the
project needs to reach **before committing to it**. Dollar figures are rough
planning estimates built on the rates in [budget.md](budget.md); the ledger
re-measures them as each step lands. (The project's accountable forecasts are
its committed predictions, not this planning document.)

## Where things stand

The pipeline runs end to end at the **bootstrapping** level
([budget.md](budget.md)): three predictors (Anthropic, OpenAI, Google), each
cross-evaluated by three judges, forecasting a salience-ranked slice of the
paid SCOTUS cert docket and every interim and merits event downstream of it.
The dated record of process-version freezes is
[freeze-record.md](freeze-record.md).

Public releases are anchored to the Court's calendar, so predictions publish
*before* outcomes exist and are scored *as* they arrive:

- **Release 1 — the OT2026 long conference (late Sept–Oct 2026).** Cert
  predictions committed before the conference, scored against the opening
  order list ([release-ot2026-long-conference.md](release-ot2026-long-conference.md)).
- **Release 2 — mid-Term (~January 2027).** First populated leaderboard, plus
  the pre-registered salience ranking and big-case scores.
- **Release 3 — end-of-Term retrospective (~June–July 2027).** The full merits
  docket resolves; the first complete Term of calibration and cost data.

None of the releases depends on the funding below. Funding changes how much of
the docket, how many moments, and how many models each release covers.

## The scaling plan

| Milestone | Model API / yr (cumulative) | Other / yr | **Funding needed / yr** |
|---|---:|---:|---:|
| Today — bootstrapping | ≈$15K (of the $24K envelope) | $7K | **≈$31K** |
| 1. More prediction events | ≈$20K (of the $24K envelope) | $7K | **≈$31K** |
| 2. All paid cases | ≈$40K | $28K | **≈$68K** |
| 3. Seven model developers | ≈$60K | $28K | **≈$88K** |
| 4. Prompt lenses | up to $120K | $28K | **≈$148K** |

Every column is cumulative: each row is the whole project's annual run rate
at that milestone, not the increment over the row above. The first two rows
sit inside the bootstrapping envelope, so their funding figure is that
envelope rather than the sum of the row. Other spend is assumed to step from the
bootstrapping to the scaling level at milestone 2, when volume starts to grow.

The order is deliberate. New moments are cheap and raise the value of every
case already covered, so they come first. Coverage comes before more models
because the project's claims are coverage claims, and every later predictor
multiplies over the events this step buys. New developers come before prompt
variants because a baseline for each model has to exist before a variant of it
means anything.

### 1. More prediction events — within bootstrapping (≈$31K / yr)

Add the moments where a case's information set materially changes, starting
with the one the public cares about most:

- **Post-oral-argument** — every argued case, after the transcript is out
  (~60 events a Term). First to be built.
- **SG brief after a CVSG** — the Solicitor General's recommendation (~20).
- **Late-Term authorship elimination** — a fixed calendar date on which every
  still-undecided argued case is re-forecast, once the pattern of who has
  written from each sitting is visible (~25).
- **Relist re-forecast** and **call for response** — the strongest public
  cert-stage signals; volumes to be counted from the statpack before
  committing.

These add a few hundred events at most, mainly on the low-volume merits track,
so the cost is engineering rather than inference: each moment is a
pre-registered population with its own base rate, and new inputs (argument
transcripts) move the registered process version.

### 2. All paid cases — ≈$68K / yr

Raise the salience gate's capacity until every paid SCOTUS petition not
removed by a deterministic filter (such as the in-forma-pauperis exclusion) is
forecast at every moment, and widen the interim reserve to the full stream of
substantive applications. Roughly 2,100–2,500 events a Term, up from
~850–1,100. At this point salience stops being a spend control and survives
as the public, pre-registered ranking.

### 3. Seven model developers — ≈$88K / yr

Add a baseline predictor for four more developers — **xAI, Moonshot, Meta, and
Alibaba** — each running its most capable model inside its own coding harness
(Grok Build, Kimi Code, Muse Code, Qwen Code), the same way the current three
run. Same prompt, same retrieval tools, so the comparison is like for like.
The new models are inexpensive to run; most of the added cost is three judges
grading four more predictions per event, a margin the first new predictor's
fan-out will measure. New predictors are not judges: the evaluator panel
stays at three.

### 4. Prompt lenses — up to ≈$148K / yr

Field three **prompt-lens variants** that instruct a model to reason from one
perspective — **legal/doctrinal, political, economic** — and let the
tournament rank them against the baselines. This tests, prospectively and on a
public ledger, the oldest argument about the Court: whether law or politics
better predicts what it does. Each lens partitions from its parent under its
own process version, so any difference in score is attributable to the prompt
alone. Lenses run on a subset of models sized to the remaining budget (about
three models at full coverage), reaching the **scaling** scenario in
[budget.md](budget.md).

Other ways to spend at this stage, several of them nearly free, to be weighed
against the lenses when the milestone opens:

- **Aggregate predictors** — mean, median, and extremized ensembles of the
  baselines, plus a base-rate floor, committed at prediction time (≈$0).
- **Resampling** — the same predictor run repeatedly on a fixed stratum, to
  measure the within-model noise floor any leaderboard gap must clear.
- **Smaller sibling models** from each developer — does general capability
  track forecasting skill within a family?
- **Retrieval ablations** — closed-book or no-CourtListener variants, which
  double as a contamination probe.
- **Open-harness twins** — each model re-run inside one shared open-source
  harness, separating the model's contribution from its vendor harness's.
