# Milestones

What the project is aiming at, anchored to the Supreme Court's term calendar so
public "releases" land when the Court is producing the events worth predicting.
It is a sequence, not a set of dated commitments: the external anchors — the
long conference, the end of term — are fixed; the internal ordering is
load-bearing; the specific timing is a working estimate, shared for
transparency. (The project's accountable forecasts are its committed
predictions, which are evaluated against real outcomes — not this planning
document.) The milestones assume the budget's **bootstrapping** state
([budget.md](budget.md)) throughout; the funded growth path is budget.md's
*Scaling plan*, not a premise of any release below.

## Why anchor to the SCOTUS calendar

The Court runs on a predictable annual cycle, and each phase generates a
different, datable supply of predictable events. Building releases around it
means predictions are published *before* the outcomes exist and evaluated *as*
they arrive — the only honest way to show calibration.

| Phase | Timing | What it supplies to predict |
|-------|--------|------------------------------|
| **Long Conference** | Last week of September | The Court clears ~2,000 cert petitions accumulated over summer — the single largest, most datable burst of cert grant/deny decisions of the year |
| **Term opens** | First Monday in October (**OT2026: Oct 5, 2026**) | Opening order list (long-conference grants/denials); argument calendar begins |
| **Grant cadence** | Order lists, most Mondays after each conference, Oct–June | Steady stream of cert decisions |
| **January "mop-up" conference** | Mid-January | Last grants that can still be argued the same term — a natural cutoff |
| **Term ends** | Late June / early July | The full merits docket resolves — ~60–70 argued cases decided, the richest evaluation set of the year |
| **Summer recess** | July–September | No new merits; time to load history, back-test, and retune |

Sources: [28 U.S.C. § 2](https://www.law.cornell.edu/uscode/text/28/2) (term start),
[SCOTUSblog: the long conference](https://www.scotusblog.com/2025/08/what-is-the-supreme-courts-long-conference/),
[Court procedures](https://www.supremecourt.gov/about/procedures.aspx).

## Where the pipeline stands

The machinery for the first release is running end to end — ingestion live on
all three channels, the corpus split on in production, the SCOTUS-gated
predict/evaluate cascade producing valid ledger artifacts with per-run cost
measured from the engines' own logs, and the cert back-test as the
never-claimable vetting loop. The dated record of the process-version freezes —
what each blessed, and the boundaries a published figure may not be pooled
across — is [freeze-record.md](freeze-record.md); this document is the forward
half.

## Release 1 — the OT2026 long-conference cert release (late Sept–Oct 2026)

The first public release. Before the Court meets at the long conference (~late
September), the pipeline predicts cert outcomes for the petitions up for that
conference; once the opening order list drops (~early October), the realized
grants and denials evaluate those predictions. The deliverable is a blog post /
short article — *"We predicted the long conference — here's how we did"* — with
the calibration numbers attached, compared against the statpack's per-Term cert
base rates.

The counted record for this release opens at the `proc-v5` predictor freeze:
promoted 2026-08-29 (`promotion/2026-08-29`), freeze instant
2026-09-05T00:00:00Z ([freeze-record.md](freeze-record.md)) — so predictions
stamped from that instant, under the blessed digests, are the release's
claimable population. It is small, datable, and end-to-end, and it defines the
scope cleanly: the petitions on that conference list are SCOTUS dockets,
exactly the gate the budget sizes for bootstrapping.

## Release 2 — the mid-term release (~January 2027)

The cert release is the entry point; the term that follows is the real runway.
Each cert grant opens a stream of downstream events on its docket —
emergency/interim applications, merits argument, the decision, the per-justice
votes — predicted and evaluated as they land, with the predict/evaluate loop
running on its daily cadence across the OT2026 argument season. The mid-term
release, timed near the January mop-up conference (the last grants arguable
this term), publishes what that cohort-follow has accumulated:

- **A first populated leaderboard** (`metrics/`) ranking predictors on resolved
  events — Brier and **Brier skill over the segment base rate**, accuracy, vote
  accuracy, reasoning quality — plus the cert-cadence calibration since the
  opening release.
- **The salience / big-case board as a public artifact.** Two pre-registered,
  datable releases, distinct from the cert calibration numbers: the
  deterministic **salience ranking** ("the petitions worth forecasting, ranked,
  *before* the conference sat") and the models' **big-case scores** ("how big
  we called them, *before* the term played out"). Both answer the post-hoc
  *"big case"* critique — the git timestamps prove the calls preceded the
  outcomes — and the big-case score adds a second skill dimension: a model can
  read significance well while calling grant/deny only modestly, or the
  reverse.

## Release 3 — the end-of-term retrospective (~June–July 2027)

As the term's ~60–70 merits decisions land, predictions and evaluations across
the full cohort publish as a retrospective accuracy report — the capstone of
the year's cohort-follow, and the first full term of cost and calibration data.
It is also the input to two decisions deliberately held until it exists: the
academic / B2B / public-artifact fork, and the scope call — widen past the
SCOTUS-docket gate toward the originating courts of appeals, or hold the gate
as the durable scope ([budget.md](budget.md), *Deferred scope, unpriced*).

## Funding

Inference dominates the budget, so the near-term play is bootstrapping on
credit programs (Anthropic startup credits primary, AWS Activate the runner-up)
to run the releases above. The milestone proper is a first **external funding
event** — a grant, an academic collaboration, or a first B2B pilot — that lifts
the budget from bootstrapping to **initial funding**. What each funding state
buys, and in what order (`N`, then richer inputs and moments, then `P`), is
budget.md's *Scaling plan*; no release above depends on it.

## Housekeeping, in parallel

- Verify the S3 egress projections against the split stores
  ([budget.md](budget.md)).
- Finish re-anchoring the budget once an evaluate-side per-run cost under the
  currently blessed grading digests is measured **at the cert stage**. The
  predict side is measured; the evaluate measurements so far are interim-stage
  only — six events under the superseded `proc-v3` digests, plus a single
  partial event under the blessed `proc-v4` ones ([budget.md](budget.md),
  *Evaluate cost*).
- Re-anchor the per-predictor grading margin at the first `P = 4` fan-out.

The last two are distinct triggers — one prices the evaluate half at today's
registry size, the other prices how that half grows when the registry does.

## Beyond a year — the automated-research goal

The long-run aim is a harness that proposes new predictor designs, registers
them in the registry, and lets `run-predict` / `run-evaluate` run the
tournament that ranks them. Nothing in the data or control flow has to change —
a predictor is just an id, an engine, and a prompt — so it is sequenced after
the loop and the leaderboard are proven, and after back-testing gives a cheap
way to screen candidates before they spend live budget. (The prompt-perspective
predictor variants in budget.md's *Scaling plan* are this goal's manual
precursor on the same seam.)

**Partnership-gated architecture: Free Law Project.** Several ingestion
upgrades wait on an established relationship (and, for some, funding) with Free
Law Project rather than on engineering: database replication (a hosted Postgres
replica under FLP's replication agreement — *The planned end-state* in
[data-pipeline.md](data-pipeline.md)), docket-alert webhooks, and opinion
bodies served from the replica. The corpus boundary and everything downstream
of ingestion are unchanged by design under all of these; budget.md carries why
two of the three are not cost-justified at the current scope.
