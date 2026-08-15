# Milestones

Where the project stands and what it is aiming at, anchored to the Supreme
Court's term calendar so public "releases" land when the Court is producing the
events worth predicting. It is a sequence, not a set of dated commitments: the
external anchors — the long conference, the end of term — are fixed; the
internal ordering is load-bearing; the specific timing is a working estimate,
shared for transparency. (The project's accountable forecasts are its
committed predictions, which are evaluated against real outcomes — not this
planning document.)

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

The machinery for the first release is running:

- **Ingestion is live on all three channels.** The daily historical Term
  walker grows per-Term coverage of decided petitions (supremecourt.gov, no
  API budget) for the statpack's per-Term base rates and the cert back-test
  set; the supremecourt.gov live channel owns SCOTUS freshness budget-free
  (discovery, the conference watchlist, outcomes, filed-document text); pull's
  daily CourtListener windows do targeted enrichment under the held membership
  tier.
- **The corpus split is on in production**: the writers keep a payload-free
  index and mirror bulk payloads to the per-case content store, and forward
  cells provision from the store (see
  [data-pipeline.md](data-pipeline.md)).
- **Prediction scope is gated and live**: SCOTUS dockets only, with the shared
  deterministic exclusions — see the prediction scope in
  [data-pipeline.md](data-pipeline.md) and the SCOTUS-docket gate in
  [budget.md](budget.md).
- **The cascade runs on its real triggers**: live cases flow through
  `run:predict` → `run:evaluate`, producing valid ledger artifacts, with
  per-run cost measured from the engines' own logs (`usage.json`, the spend
  roll-up on the ops dashboard) and data validation surfacing as data-health.
- **Predictor vetting is the cert back-test**: the maintainer-triggered
  `run-backtest` workflow replays predictors over decided petitions (outcomes
  hidden) — iteration signal for prompts, retrieval, and calibration, never
  claimable performance.
- **The forward record begins with the OT2026 cert cycle.** The ledger holds
  SCOTUS events and realized outcomes; forward predictions and their
  evaluations accumulate from here, so the published record is consistent with
  the current design end to end.

### The process-version freeze (cutover marker)

The freeze is the cutover that separates the shakedown from the frozen forward
record — the milestone this file marks. What a process version is, which states
it passes through, and how the freeze is performed all belong to
[process-version.md](process-version.md#freezing-the-cutover-procedure);
each freeze commit is recorded here.

- Freeze commit: `84b421168` (tagged **`prereg/proc-v1`**) — blesses the six
  proc-v1 digests (three predictors, three evaluators) and sets the freeze
  instant `2026-08-15T00:00:00Z`. Carried to `main` by the promotion tagged
  `promotion/2026-08-12-2` (merged `2026-08-12T14:20:51Z`, before the
  instant — the auditor's check of the cutover procedure above). Zero stamped
  cells existed when the freeze landed on `main`, so nothing is listed as
  pre-registration-excluded; everything earlier is the unstamped
  alpha/shakedown ledger. **Superseded by proc-v2 below with zero cells ever
  stamped under it** (step 0's grep on both branches: 0), so its headline is
  legitimately empty forever; the tag stays as the record that the label was
  registered, then superseded before any cell ran.
- Freeze commit: `04411f166` — the sal-v2 activation commit as amended before
  the tag by the merits-baseline accuracy fix (#1157), which is where the
  blessed set lives, tagged **`prereg/proc-v2`**. Carried to `main` by the
  promotion tagged **`promotion/2026-08-13`** (merge commit `260e8a64a`, merged
  `2026-08-13T19:10:14Z`, before the freeze instant — the auditor's check of
  the cutover procedure). Step 0's stamped-cell grep on both branches at the
  promotion: 0. It re-blesses the
  three predictor digests the predict prompt's third cert moment (the arrival
  cell) moved, and sets the freeze instant `2026-08-16T00:00:00Z`. The
  activation commit flips
  the active salience scorer to `sal-v2`; its caption-census freeze record
  (caption-v1, pooled federal 0.708 vs private 0.054 over OT2017–24, 8/8
  complete Terms) is quoted in the activation PR with the corpus sha it ran
  over. The scored window opens at the first post-promotion metrics refresh,
  not at the flip — a sal-v2 cell minted before the refreshed statpack has no
  published baseline (`docs/salience.md`). The evaluator digests carried by
  the freeze are proc-v1's grading process plus one pre-tag accuracy fix in
  the evaluate prompt's merits note (the harness merits baseline's third pool
  guard — the null-provenance refusal in `merits_base_rate` — a
  scoring-baseline change with no boundary of its own; the prompt edit
  beside it gives it one, the discipline `docs/process-version.md`
  prescribes); zero cells were ever stamped
  under any interim digest set.

- **`sal-v3` registered and activated (caption-v2 carve-in), 2026-08-15.** No
  freeze commit belongs to this entry: the salience version sits outside the
  process digest (`pipeline_sha` is not an input), carries its own
  data-visible boundary (`context.salience_version`), and the flip re-blesses
  nothing. The registration commit (`be774099c`) adds the `caption-v2` rule
  and the `sal-v3` scorer with `sal-v2` still active; the activation commit
  flips the one constant. Its caption-census freeze record, quoted here
  because the census artifact is deliberately uncommitted: `caption-v2` over
  corpus `e665971350fbc5d2729e424c6fd6d0f2b927b59253922cccb60f6dd1fe276469`,
  scored segment OT2017–24, pooled federal 133/181 (0.7348) against
  `caption-v1`'s 114/161 (0.7081), private 0.0524 against 0.0540, per-Term
  federal `n` 17/23/26/41/11/19/29/15 (OT2017–24; right-censored OT2025 21)
  against v1's 16/20/22/39/9/17/22/15, per-Term lift 9.1×–17.7×, 20 rows
  across 16 distinct captions migrating `private`→`federal` in the complete
  Terms (plus 2 in OT2025), one-directional by construction — and because the
  recovered captions were surfaced partly by a grant-ranked residual scan
  (19 of the 20 migrated rows are grants), the pooled-rate rise and the lift
  rise are **not** evidence for the widening; the evidence of record is the
  migrated captions' outcome-free precision (no false positive among the 20
  migrated complete-Term rows) and the pre-registered per-Term replication
  shape, with the incremental class's forward rate estimable only by an
  out-of-sample re-census once frozen-window Terms accrue. The scored window
  opens at the first post-promotion metrics refresh, as it did for `sal-v2`.

- Freeze commit: `8d256a32f`, to be tagged **`prereg/proc-v3`**. Carried to
  `main` by the promotion tagged `promotion/<FILL: YYYY-MM-DD>` (merge commit
  `<FILL: sha>`, merged `<FILL: instant>`) — the auditor's comparison of the
  cutover procedure is that date against the freeze instant, and it is a **hard
  gate before the tag is minted**, not a note: the `prereg/` namespace blocks
  update and deletion, so a tag over a bad instant burns the label. It blesses
  the six proc-v3 digests (three predictors, three evaluators) and keeps the
  freeze instant at `2026-08-16T00:00:00Z`, deliberately unmoved from proc-v2's.
  Holding it is safe in the direction that matters — proc-v2 has zero stamped
  *predictions* and the enforced filter is prediction-side, so re-using the
  instant blesses nothing retroactively — but it is the **tight** direction
  rather than the generous one the procedure asks for, which is why the gate
  above is stated as a gate. If the promotion merges after the instant, bump the
  constant in a follow-up promotion before tagging, and confirm no stamped cell
  carries a `stamped_at` in the gap.

  **Step 0's stamped-cell grep against `origin/main`: 27, all
  pre-registration-excluded.** Every one is an **evaluation** — no prediction
  carries a stamp at all — over three cert events
  (`scotus/73129750`, `scotus/73275185`, `scotus/73275187`, each
  `evt-petition-disposition`), three evaluators (`claude-judge`, `codex-judge`,
  `gemini-judge`) × three predictors, all labelled `proc-v2` and all stamped
  between `2026-08-14T03:41:05Z` and `2026-08-14T03:47:47Z`. Every stamp
  precedes the freeze instant, so `is_frozen`'s time cutoff excludes them
  mechanically, and **zero cells were ever counted under proc-v2**: its headline
  is legitimately empty forever, and its tag stays as the record that the label
  was registered and then superseded. The grep must be **re-run at promotion
  time** — cells land on `main` continuously, so the count can move.

  What moved every digest is the prompt pair: `.github/prompts/predict.md`
  elicits `cert-v2`'s five claims (the two additions in the conditional forms
  their resolvers score), `interim-v1`'s four, and `semantic-v1`'s two
  propositions on a merits cell, and anchors an interim cell on the registered
  scored base rate; `.github/prompts/evaluate.md` keys the base-rate basis on
  the frozen `salience_version`, reads the merits and interim rate/skill pair as
  harness-stamped, scopes `vote_accuracy` to merits cells, and carries the
  semantic grading protocol.

  Riding the same promotion, and named here because each changes what is
  measured **without moving a digest** — the discipline
  [process-version.md](process-version.md) prescribes for exactly this class:

  - the **vote-scoring stage gate** (`pipeline.moments.scores_votes`), which
    changes what is scored under an unchanged digest by denying vote scoring off
    the merits stage by default;
  - the **blinding masking surface**, widened by the new `MODEL_RATES` keys that
    `blinding.identity_terms` reads — a change to every evaluator's information
    set with no digest of its own;
  - the **claim-set declarations** `cert-v2`, `interim-v1` and `semantic-v1`,
    which are tables rather than prompt bytes or actor config;
  - the **harness skill stamp**, which moves `brier_score`,
    `segment_base_rate`, and `brier_skill_score` off the evaluator and onto
    `stamp-cell` on the merits and interim stages — a change to *who computes a
    scored number*, which the scoring-baseline rule puts in this list;
  - the **`sal-v3` activation**, whose own entry is above; it carries a
    data-visible boundary of its own (`context.salience_version`), so it is
    listed here for completeness rather than because it is invisible.

## The near-term target: the OT2026 long-conference cert release

The first public release aims at the **September 2026 long conference**. Before
the Court meets (~late Sept), the pipeline predicts cert outcomes for the
petitions up for that conference; once the opening order list drops (~early
Oct), the realized grants/denies evaluate those predictions. The deliverable is
a blog post / short article — *"We predicted the long conference — here's how
we did"* — with the calibration numbers attached, compared against the
statpack's per-Term cert base rates. It is small, datable, and end-to-end, and
it defines the scope cleanly: the petitions on that conference list are SCOTUS
dockets, exactly the gate the budget sizes for its **bootstrapping** state
([budget.md](budget.md)).

## Following the cohort through the term

The cert release is the entry point, not the end. The ~year that follows is the
richest evaluation set and the real runway, so the sequence after it is what the
project is actually building toward.

- **Follow the granted cohort through the term.** Each cert grant opens a stream
  of downstream events on its SCOTUS docket — emergency / interim-docket
  applications, merits argument, the decision, and the per-justice votes —
  predicted and evaluated as they land. The predict/evaluate loop runs on the
  daily cadence across the OT2026 argument season, and a first leaderboard
  (`metrics/`) ranks predictors on resolved events (Brier and **Brier skill over
  the segment base rate**, accuracy, vote accuracy, reasoning quality), with
  mid-term updates riding the Oct–June grant cadence. This is the ~year of runway
  and the largest evaluation set the project accumulates.
- **The salience / big-case board as a public artifact.** Two pre-registered,
  datable releases land **distinct from the cert calibration numbers**: the
  deterministic **salience ranking** ("the petitions worth forecasting, ranked,
  *before* the conference sat") and the models' **big-case scores** ("how big we
  called them, *before* the term played out"). Both answer the post-hoc *"big
  case"* critique — the git timestamps prove the calls preceded the outcomes — and
  the big-case score adds a **second skill dimension** to the leaderboard: a model
  can read significance well while calling grant/deny only modestly, or the reverse.
- **End-of-term retrospective (~June 2027).** As the term's ~60–70 merits
  decisions land, predictions and evaluations across the full cohort publish as a
  retrospective accuracy report — the **capstone of the year's cohort-follow**, and
  the first full term of cost and calibration data.
- **Get funded at all — model-agnostic, tied to `N`.** Inference dominates the
  budget, so the near-term play is **bootstrapping** on credit programs (Anthropic
  startup credits primary, AWS Activate the runner-up) to run the cert release. The
  milestone proper is a first **external funding event** — a grant, an academic
  collaboration, or a first B2B pilot — that lifts the budget from bootstrapping to
  **initial funding** ([budget.md](budget.md)) and, mechanically, **raises `N`**:
  deepening the salience-ranked slice from the long-conference batch toward most of
  a cert term.
- **The ~1-year decision point.** With a term of cost and calibration data in
  hand, an explicit pivot: academic collaboration, B2B legal-analytics, or holding
  as a public-artifact project. Sustained external support here is the
  **well-funded** state ([budget.md](budget.md)), where `N` can approach the full
  cert gate and the **scope** call opens up — widen past the SCOTUS-docket gate
  toward the originating courts of appeals or a rotating appeals sample, or hold
  the gate as the durable scope. Options kept open until the data is in.

**Housekeeping, in parallel:** verify the S3 egress projections against the split
stores ([budget.md](budget.md)); unify the index's transport onto the same boto3
pattern as the content store; finish re-anchoring the budget once evaluate-side
per-run cost is measured (the predict side now is).

## Beyond a year — the automated-research goal

The long-run aim is a harness that proposes new predictor designs, registers
them in the registry, and lets `run-predict` / `run-evaluate` run the
tournament that ranks them. Nothing in the data or control flow has to change
for it — a predictor is just an id, an engine, and a prompt — so it is
sequenced after the loop and the leaderboard are proven, and after back-testing
gives a cheap way to screen candidates before they spend live budget.

**Partnership-gated architecture: Free Law Project.** Several ingestion
upgrades wait on an established relationship (and, for some, funding) with
Free Law Project rather than on engineering:

- **Database replication** — a hosted Postgres replica under FLP's replication
  agreement consolidates the ingestion upstreams: full field coverage,
  continuously current, no request caps (see *The planned end-state* in
  [data-pipeline.md](data-pipeline.md)).
- **Webhooks** — CourtListener's docket-alert webhooks could replace polling
  for liveness (relevant mainly if the scope ever widens past SCOTUS, whose
  own site the live channel already polls without limits).
- **Opinion bodies from the replica** — would obviate storing opinion text in
  the content store and close out the remaining opinion-body read path.

The corpus boundary and everything downstream of ingestion are unchanged by
design under all of these.
