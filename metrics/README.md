# Metrics

Pipeline metrics: small, deterministic, git-tracked roll-ups whose reviewed
diffs track predictor and corpus quality over time. The offline gate
(`fedcourts corpus-status`) checks that the four gate-tracked artifacts —
`leaderboard.json`, `backtest.json`, `statpack.json`, `statpack.md` — exist
and are committed. Two more are committed but not gate-checked:
`cert-backtest.json`, which is maintainer-triggered, and `docket.{json,md}`,
which is regenerated on demand by `fedcourts docket`. The gate's presence check
tracks the set the weekly refresh regenerates, so an artifact outside that set
stays outside the gate:

- `backtest.json` — results of replaying predictors against historical *resolved*
  events in the corpus (outcome hidden at predict time, scored against the known
  `disposition`): per predictor, disposition accuracy, binary granted accuracy,
  and the mean Brier score of P(granted). `fedcourts backtest` produces it —
  a deterministic, offline replay over the corpus —
  empty (zero counts) until a corpus with outcome labels is present. **Labeled
  retrospective by construction** (see the stratification note below): every
  replayed event resolved long before any modern model's training cutoff, so the
  figures measure recall and calibration over known history, never foresight.

  **Each entry carries the always-deny floor and the lift over it, per court and
  overall.** Raw accuracy here is close to meaningless alone: a constant predictor
  scores its slice's base rate *exactly*, so `constant-denied` posting a high
  accuracy is arithmetic, not skill. The floor beside it is what makes the number
  readable — a lift of zero says the predictor learned nothing. One structural
  case to read differently: `prior-vote` retrieves on shared judges, and SCOTUS
  rows largely carry none, so on that court it votes the whole-history majority
  — `denied` — and its lift is ~zero *by construction* rather than by failing to
  learn. There is nothing there to retrieve on. What it still measures on SCOTUS
  is calibration: P(granted) and the Brier score.

  **Read the per-court cut, not the pooled row.** The pooled figure is dominated by
  whichever court supplies the most resolved events, and that court's floor may be
  near zero, so a pooled lift can average away a severe failure on the population
  that is actually predicted. It also mixes outcome vocabularies: `granted` means
  cert was granted on a SCOTUS row and a motion was granted on a court-of-appeals
  docket. The overall row is a reference point; the per-court rows are where floor
  and lift are comparable.

  Lift is **presentational** — entries still rank on accuracy then Brier, because
  ranking on a pooled floor that spans those vocabularies would promote an
  incomparable number to the headline. Skill against a *leakage-safe* baseline, with
  the salience adjustment, is `cert-backtest.json`'s job on the predicted
  population; this one is the broad reproducibility floor plus enough context to
  read it. One asymmetry worth knowing: this artifact is on the scheduled refresh
  and `cert-backtest.json` is maintainer-triggered because it spends tokens on
  agentic replay, so continuous skill tracking would mean scheduling a cert-scoped
  run.
- `leaderboard.json` — predictors ranked best-first from the evaluations ledger
  under `data/`: per predictor, accuracy, mean Brier score, mean vote accuracy, a
  mean reasoning-quality summary, and counts (events scored, evaluations,
  evaluators), each reported **per stratum** — the `forward` and
  `retrospective` timing blocks plus the basis-driven `procedural` block,
  never blended into one number, with only the timing strata ranked. Each entry
  also carries a `big_case` block — the predictor's `big_case_score`
  rank-agreement (Kendall's tau-b) with the evaluator panel's independent reads —
  a second, orthogonal skill dimension that never affects the ranking.
  `fedcourts leaderboard` produces it — a deterministic, offline
  roll-up — empty (`{}` plus the zero counts) until the first evaluation lands.

**Forward vs retrospective.** Snapshotting controls what a predictor can *read*,
but not what its model already *knows*: a prediction over an event that resolved
before the model's training cutoff has the outcome inside the model's weights —
the caption alone can retrieve it — so scoring it measures recall plus
calibration, not ex-ante forecasting skill. The clean structural separator is the
pre-registration standard: a cell is **forward** when the event was still
unresolved at the prediction's commit and **retrospective** when it had already
resolved (same-day ties count as retrospective, the conservative reading). The
split is deterministic and offline — the prediction's `created_at` against the
outcome's `resolved_at`, both committed artifacts (`classify_stratum` in
`fedcourtsai.leaderboard` is the single definition). Retrospective cells remain
valuable — they measure calibration and label-mapping fit — but only the forward
stratum is evidence of forecasting skill, so no headline metric may mix them.

**The procedural stratum.** A cell whose outcome was mootness practice — a
Munsingwear vacatur ("granted", but the wording tracks the Court's vacatur
practice) or a dismissal as moot — segments into a third, `procedural` stratum
regardless of timing (the outcome's `disposition_basis` marks it at
resolution). Its aggregates are reported per predictor but never enter the
ranking: scoring them as merits calls would conflate cert-worthiness
calibration with vacatur-practice prediction.

- `cert-backtest.json` — the cert-specific back-test (not on the scheduled
  refresh): predictors
  replayed over the most recently decided modern discretionary-cert petitions,
  outcome hidden behind a redacted snapshot, scored on accuracy, Brier, **lift
  over the always-deny floor** (the honest signal under cert's denial skew), and
  a P(granted) calibration view. Each entry also carries a **per-salience-band
  skill breakdown** over the paid scored segment — the mean leakage-safe segment
  base rate (each petition's own prior-Term band grant rate) and the mean Brier
  skill against it — so the back-test measures the same segment-baseline skill the
  forward stratum does, not just raw Brier. Comparable across the two strata while
  `salience.base_rate_lookback_terms` (the in-code window, shipped unbounded) and
  `statpack.markdown_terms` (what the prompts' Term table renders, 10) agree; see
  [salience.md](../docs/salience.md). A replayed predictor's pre-registered
  **big-case-score distribution** (coverage + mean/min/max stakes) rides alongside
  — a distribution, not a grade, since the replay has no independent evaluator to
  rank against. Produced by the maintainer-triggered
  `run-backtest` workflow — a real-engine replay spends tokens, so it never
  runs on a schedule — and labeled retrospective like `backtest.json`. A run
  is an explicit maintainer action: apply the `run:backtest` label to an
  issue (the real engines, default set size) or dispatch the workflow with
  `engine`/`limit` parameters (~one predict cell per petition per routable
  predictor; `engine: stub` is a free dry run). The refreshed report lands as
  a **reviewed, never auto-merged** PR. Only petitions holding a snapshot
  replay; the report names what it skips. `fedcourts cert-backtest` remains
  runnable locally with the engine CLIs authenticated.
- `statpack.json` / `statpack.md` — a corpus base-rate **statpack** (an independent
  published artifact), two populations side by side. The labeled full-corpus
  overview (cases by court, SCOTUS by decade era — the frozen bulk import
  included) gives composition context. The **live/historical-slice cert
  statistics** are what predictor and evaluator cells anchor on: disposition
  base rates computed over rows the supremecourt.gov channel wrote, each row
  counted `sample_weight` times so the historical walker's denial sampling
  does not bias them — the **modern discretionary-cert cut** (the calibration
  anchor, undiluted by merits-era labels), grant/deny by originating circuit,
  by relist count, by CVSG status, and by **salience band** (the frozen
  `sal-v1` grant-likelihood tier over the paid scored segment), plus a
  by-originating-court reader table that names state courts. A coverage block
  states the pack's own denominators, and the per-Term array carries each
  October Term's cursor-derived filings census by fee class (paid/IFP),
  walk-complete flags, weighted estimates, grants, pace-to-grant, and the
  per-salience-band **segment base rate** (the leakage-safe grant rate the
  predict prompt is designed to anchor on and the evaluator will score skill
  against) — the surface a time-masked replay cell self-selects pre-cutoff
  Terms from. `fedcourts statpack` produces both the machine JSON and a
  rendered Markdown document — a
  deterministic, offline roll-up of the corpus — empty
  (zero counts, empty sections) until a corpus is present.

- `docket.json` / `docket.md` — the **court-facing docket pack**: facts about the
  dockets themselves, for a reader with no interest in whether this project's
  models are any good. Composition by court and by decade era; then, over the
  live/historical slice of modern discretionary-cert petitions, the disposition
  split, the originating circuit, the relist count, the CVSG status, the paid/IFP
  fee class, and a reader table that names the state courts a petition came from;
  then a per-Term census of docketed filings against ingestion, grant rate, grants
  observed, and pace to grant. `fedcourts docket` produces both files.

  **It carries no prediction claim, by contract** — no accuracy, no ranking, no
  Brier, and no salience band. The band is the line: it is a statement about which
  petitions this project chooses to predict, so it belongs to `statpack.*` and
  never here. That exclusion is what makes the pack citable on its own terms.

  Read it the same way as the statpack's live-slice cuts: every section states its
  own scope, and every rate repeats its denominator. **Every cert cut is
  denial-reweighted** — including the by-originating-court table, which is the
  statpack's raw reader cut recomputed as an estimate, because it is the only
  place a state court appears and an unweighted rate over the walker's frame
  inflates the grant family several-fold. A reweighted denominator is written
  `est. n=` and a raw one `n=`, because the first estimates a population and the
  second counts rows; a breakdown row carries no raw view of its own, so a small `est. n=`
  is weaker evidence than it looks; the per-Term census is the exception and
  prints the observed `ingested (rows)` beside the estimate.
  `(none)` and `(unknown)` buckets are rendered rather than dropped, so a coverage
  gap is never hidden inside a rate — `(unknown)` on the relist and CVSG cuts means
  *not yet parsed*, not *did not happen*. The document names the statistics it
  cannot yet compute (what the petitions are about, which needs a claim taxonomy
  that does not exist; summary reversals, which the disposition vocabulary has no
  label for; justice-level statistics, which need a per-justice vote record) so a
  citation is never read as a claim that the figure is zero.

These files are deterministic, offline roll-ups that start empty (zero counts)
until their input lands — the evaluations ledger for the leaderboard, a corpus
with outcome labels for the back-test, statpack, and docket pack. All are small
and worth reading
in a diff, so they are git-tracked rather than pushed to the corpus remote like
the corpus blob.

**Statpack directions not built.** The published stat packs
(SCOTUSblog / Empirical SCOTUS) carry whole families of statistics this
project's docket-first corpus cannot compute yet, kept here as named
directions rather than silent gaps: justice-level statistics (frequency in
the majority, agreement matrices, opinion authorship — need per-justice vote
data, e.g. a Supreme Court Database import), amicus-brief counts per petition
(need docket-entry parsing beyond the proceedings), oral-argument statistics
(need transcript data), and a merits circuit scorecard (affirm/reverse by
court below — needs judgment-entry parsing on decided merits cases).

**The backtest-as-iteration doctrine.** Backtests (the retrospective stratum,
the replay runs, `backtest.json`, `cert-backtest.json`) are **iteration
instruments** — for tuning prompts, retrieval, and calibration — and are
**never claimable performance**; the project claims results only from genuine
forward predictions. Timing is the integrity mechanism: the prediction's git
commit timestamp against the outcome's `resolved_at`, both content-addressed
committed artifacts, decides the stratum — not any restriction on what a cell
could retrieve. Replay cells run with the same tools as forward cells; the
cross-evaluator's leakage grading (the `leakage` block on each
`evaluation.json`, read off the harness-captured `retrieval_log.json`) exists
so contamination of the *iteration signal* is visible, not to police a claim
that is structurally never made.
