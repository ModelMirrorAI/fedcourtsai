# Process versioning: which predictions count toward the headline

Predictions committed during the July/August shakedown are real, timestamped
forward calls — irreplaceable forward-stratum data — but they ran under a process
still being corrected. The headline metrics must reflect only the **frozen,
correct** process, without deleting the shakedown runs (a wipe reads as hiding
results, not rigor). This is the same doctrine as [`sal-v1`](salience.md): a
process change is a **new version**, never an in-place edit, so any past ranking
always replays against the process that produced it.

## What a "process" is, and how it is identified

The process behind one predictor cell is its **prompt template plus the resolved
configuration it ran under** — the engine, the resolved model (the registry
override, else the engine default), the pinned MCP tool manifest, and the
engine's retrieval surface (what a cell can reach beyond the snapshot: the open
web, and for codex the subprocess-network grant). A cell that can reach the open
web answers from a different information set than one that cannot, so the
surface is a process input as much as the model is. The harness stamps each
`prediction.json` / `evaluation.json` with a `ProcessVersion` carrying:

- **`digest`** — a `sha256:` content hash of exactly those inputs (the prompt file
  bytes plus the canonical resolved config). This is the identity that matters:
  the frozen/shakedown partition keys on the digest, so a silent prompt or config
  change is automatically a distinct version. Two predictors that share a prompt
  but differ in model are different processes — different digests.
- **`label`** — a human-readable name (`proc-v1`), sugar for a digest. Never the
  partition key: two different processes cannot hide behind one label, because
  the digest gives them away.
- **`pipeline_sha`** — the checkout commit, as provenance only. It is deliberately
  **not** part of the digest: the commit changes on every unrelated pipeline edit,
  and folding it in would break the frozen set every time predict/evaluate resume
  at a newer HEAD. The digest captures what *defines* the process; the sha records
  which commit *ran* it.
- **`stamped_at`** — when the harness stamped the cell (UTC, timezone-aware).
  Provenance, and — with the digest — the frozen/alpha partition's time key:
  the digest says *which* process ran, the stamp says whether it ran at or
  after the freeze instant. The runner clock is the witness that a run
  postdated the commitment — acceptable because the agent cannot write this
  field, and bounded independently by the workflow run's own timestamps and
  the data commit's date on `main`. A naive value has no defined order
  against the instant and reads as pre-freeze.

The digest excludes documentation that does not change behaviour — the actor's
`description` and the MCP manifest `description` are comments, not process inputs,
so editing one does not re-version anything.

### Harness code is outside the digest, and one case of that has teeth

Everything the harness *does* around the agent rides `pipeline_sha`, not the
digest — deliberately, since otherwise the frozen set would break on every
unrelated pipeline edit. Usually that is harmless: a change to how usage is
totalled or how a log is captured does not change what the agent was answering
from.

**Blind grading is the exception worth naming.** The evaluate cell stages each
prediction under an opaque alias with its identity masked
(`fedcourtsai.blinding`, `docs/outcome-decomposition.md`), and *what gets masked*
is a property of that code, not of the prompt or the registry. So changing the
masking surface — staging a file that was dropped, dropping one that was staged,
widening or narrowing the scrub — changes the evaluator's **information set**
under an unchanged digest. Two evaluations can carry the same digest and have
been formed from different inputs, which is exactly what the digest exists to
rule out.

The discipline that follows, since the mechanism cannot enforce it: treat a
change to the masking surface as a process change even though nothing
re-versions. Land it with the prompt edit that describes it — the prompt bytes
*are* hashed, so a masking change stated in the prompt moves every evaluator
digest and the boundary becomes visible in the data. A masking change made
silently, without a prompt edit, leaves no boundary at all and is the one shape
to avoid; if it is unavoidable, it belongs in a `label` bump and in the freeze
record, not in a commit message alone.

One case the discipline does **not** cover, because it is not a code edit at
all: the scrub reads the live registries and one candidate is staged per
registered predictor, so **adding or retiring a predictor changes every
evaluator's information set** — a different scrub-term set and a different number
of candidates — while moving no evaluator digest, since an evaluator's canonical
config carries no predictor list. That is a routine operation with no boundary
behind it. Until the masking surface is folded into the evaluator's canonical
config (which would make it a partition key rather than an honour system), a
registry change that alters the candidate set belongs in the freeze record beside
the masking changes.

The **scoring baseline** is a third member of this list, and the only one with
no data-visible boundary at all. Skill numbers are computed against the
salience-band base rates, and the lookback window that builds them
(`base_rate_lookback_terms` in `config/tracking.yaml`) sits in no actor's
canonical config and is recorded in no artifact field — moving it re-bases
every forward skill number and every backtest per-band skill at once, under
unchanged digests. (The salience *version* does have a boundary:
`context.salience_version` and the pack's `base_rate_salience_version` make a
`sal-v2` cut visible in the data.) The pre-registered baseline is therefore
the whole tree at the `prereg/<label>` tag — lookback window included — and a
later window change belongs in the freeze record beside the masking changes,
never in a commit message alone.

## The stamp is the harness's word, not the agent's

The agent writes `prediction.json` / `evaluation.json`; a post-agent step
(`fedcourts stamp-cell`, in both `run-predict` and `run-evaluate`, before
`validate`) reads that file and injects the `ProcessVersion` derived from the
registry. So a cell's version is what the harness resolved at run time, exactly
as `usage.json` records the engine's own log rather than trusting the agent — a
compromised or hallucinating agent cannot fake its process version. The same
clock discipline reaches past the freeze: the forward/retrospective stratum
boundary keys on the cell's harness clock (`fedcourtsai.integrity.cell_clock`
— the stamp's `stamped_at`; an unstamped **shakedown** cell falls back to its
agent-written `created_at`, safe exactly because an unstamped cell can never
be frozen), so no pre-registration boundary anywhere rests on a clock the
agent controls.

The stamp step is deterministic and local, so unlike the best-effort log
captures beside it, it is **must-succeed**: a missing artifact (a no-output cell)
is a clean no-op, but a registry/prompt inconsistency fails the cell rather than
shipping an unstamped-but-frozen-looking prediction, as does an evaluation
recording a `risk_set` base-rate basis whose salience version does not resolve —
a basis is only readable beside the version it was banded under. An evaluate cell
scores every predictor, so the evaluator stamp covers all of its
`evaluation.json`.

**On an evaluate cell the stamp runs after un-aliasing, and the order is not
interchangeable.** The stamp joins each evaluation to the prediction it scored on
the `predictor_id` field, so under a blind-grading alias the join simply misses
and the cell's `claim_scores` block is *silently* absent rather than wrong —
`base_rate_salience_version` too, except where the evaluation records a
`risk_set` basis, which fails the stamp rather than losing its version half. So
`fedcourts unblind-evaluations` runs first, then `stamp-cell`, then `validate` —
whose `check_evaluation_targets` resolves the same join and is the loud backstop
for an alias that survived.

## Three states: shakedown → not-yet-frozen → frozen

`FROZEN_PROCESS_DIGESTS` (in `fedcourtsai.process_version`) is the blessed set —
the digests whose cells count toward the headline. Everything keys off it:

- **Shakedown** — a cell written before the stamp existed carries no
  `process_version`. It is never frozen (an absent stamp cannot be in the set),
  so the whole shakedown ledger drops out of the headline for free — no backfill,
  no deletion.
- **Not-yet-frozen** — a stamped cell whose digest has not been blessed, or a
  stamped cell whose stamp *precedes* the freeze instant, whatever its digest.
  Until a stamped cell's digest is blessed *and* its stamp is at or after the
  freeze instant, the frozen headline is legitimately **empty** — "no
  frozen-process evaluations yet" — which the leaderboard, the ops dashboard,
  and the weekly digest all say in as many words, rather than showing a bare
  `0` that reads as a regression.
- **Frozen** — a stamped cell whose digest is in the blessed set **and** whose
  stamp is at or after `FROZEN_SINCE`, the freeze instant set in the same
  commit that fills the set. The digest is a pure content hash — it says
  *which* process ran, never *when* — so without the instant, a shakedown run
  of the very bytes later blessed would read as frozen retroactively.
  Pre-registration means the commitment preceded the run; the time cutoff is
  what says so.

## What defaults to frozen, and what stays version-blind

The frozen filter lives at the one shared producer both surfaces read
(`store.stratify`, `frozen_only=True` by default — the boards call it directly
so the scored cells and the `forward_claim` exclusion record come from one
pass; `iter_stratified_evaluations` is its thin cells-only wrapper), so the
leaderboard headline and the ops dashboard's scored figures can never disagree —
they each pass one boolean. Both CLIs take `--all-versions` for the pooled
shakedown view. The filter partitions on the **prediction's** stamp — the
competitor being ranked is the predictor — and additionally requires the
evaluation's own harness stamp to be at or after the freeze instant (its
digest is recorded but not enforced), so a shakedown grading cannot ride a
frozen re-run of its event into the headline.

Two things stay all-versions on purpose, because they are diagnostics, not the
headline:

- The **prediction census** (`ledger_cell_counts` — how many predictions and
  events the funnel has) counts everything committed. A frozen scope showing many
  predictions but zero frozen evaluations is the honest shakedown state, and the
  dashboard labels that divergence rather than hiding it.
- The **leakage digest** counts every evaluation carrying a leakage grade,
  frozen or not. Shakedown contamination is exactly what it exists to surface, so
  scoping it to frozen-only would blank it during the window it matters most —
  the same posture as the flags and tooling digests beside it.

The generic back-test is process-independent (it replays reference baselines, not
the tournament predictors), so it carries no process version.

## Freezing: the cutover procedure

The freeze centers on a deliberate, reviewable **two-constant commit**, made
when the process is settled and the first frozen predictions are about to
land; recording and tagging that commit complete the procedure:

0. Confirm no stamped cell already carries a digest you are about to bless:
   `git fetch origin main && git grep -l '"process_version": {' origin/main --
   data/cases | wc -l` must be 0 — the object form, because a rewritten cell
   can carry a `"process_version": null` key without a stamp, and `main`,
   because data commits land there directly and never ride `staging`. Any
   cell it finds must be listed in the freeze record as
   pre-registration-excluded. The `FROZEN_SINCE` cutoff mechanically excludes
   any such cell stamped *before* the instant; a cell stamped at or after it
   is possible only if the carrying promotion slips past the instant, and is
   caught by step 4's gap check. Either way this step keeps the freeze record
   honest about their existence — and it must be **re-run at promotion
   time**, since cells land continuously and the authoring-time check can go
   stale.
1. Read the current digests: `fedcourts process-digest --all` prints the label,
   role, id, and digest of every enabled predictor and evaluator.
2. Paste the digest(s) to bless into `FROZEN_PROCESS_DIGESTS` in
   `src/fedcourtsai/process_version.py`, and set `FROZEN_SINCE` beside it —
   a test pins that the two move together. The instant must be **at or after
   the moment the commitment becomes immutable on `main`** (the promotion
   merge that will carry this commit) and before the first run you intend to
   count; between that merge and the instant nothing runs, so choosing it
   generously late errs conservative, while an instant before the merge would
   bless runs made while the constant was still editable. The promotion date
   is a forecast at this step — guess late.
3. Commit. Because the digest excludes `pipeline_sha`, the blessed set survives
   unrelated pipeline commits — predict/evaluate can resume at a newer HEAD and
   still match.
4. Once the promotion carrying the commit lands on `main`, **verify the
   instant before minting anything immutable**: the literal in the file must
   be at or after the promotion merge's date
   (`git log -1 --format=%cI <promotion merge>`). If the guess came in early,
   bump the constant in a follow-up promotion **before** tagging — the
   `prereg/` namespace blocks update and deletion, so a tag minted over a bad
   instant burns the label. On a slip, also confirm no stamped cell carries a
   `stamped_at` in the gap between the instant and the carrying merge: such a
   cell would read as frozen although it ran while the constant was still
   editable, and the retroactive-blessing tripwire only catches the opposite
   direction (blessed digest, pre-instant stamp) — bump past any it finds. Only then record the commit as the cutover in
   [milestones.md](milestones.md) and tag it `prereg/<label>`
   (e.g. `prereg/proc-v1`): an annotated tag in the `prereg/` namespace the
   *Tags* section of [pipeline.md](pipeline.md) describes, protected against
   update and deletion so the freeze point stays findable and immovable. The
   after-the-fact auditor's check is the same comparison, against the
   promotion that carried the freeze commit to `main`:
   `git log -1 --format=%cI promotion/<YYYY-MM-DD>` — the literal in the file
   must be at or after that date. Name the tag pointing at the **carrying
   merge itself** (a same-day second batch carries a `-2` suffix, and the
   bare date resolves to the earlier, weaker comparison). (`prereg/<label>`'s own tagger date is not
   the witness: the tag is minted after this check, so it may legitimately
   fall on either side of a correctly chosen instant.)

From that commit forward, the first long-conference prediction lands under the
stamped, frozen process and the headline fills in. When the process later changes
materially, bump `CURRENT_PROCESS_LABEL` to the next label; the old label's cells
keep their stamp and remain replayable against the process that produced them,
never overwritten.

**Re-freezing before the prior instant has any cells** is a supersession, not
an extension: the new two-constant commit *replaces* the retired label's
digests in `FROZEN_PROCESS_DIGESTS` (the set holds one blessed process per
actor, and `is_frozen` is a membership filter, so keeping the old predictor
digests would bless two processes at once). The procedure above runs in full
for the new label — including step 0's grep, which is what proves the
supersession de-blesses nothing — and the freeze record in
[milestones.md](milestones.md) must state the count of cells ever stamped
under the superseded label (zero, or listed). The superseded `prereg/` tag
stays: the namespace blocks deletion, and the tag remains the honest record
that the label was registered and then superseded before any cell ran under
it. Its headline is legitimately empty forever.

## A note on local runs

The local `cascade` / `local-cascade` path produces cells but does **not** run the
`stamp-cell` step (that is a workflow step, not part of the runner). So a local
cascade's cells are unstamped and appear only under `--all-versions`. This is
intended: the frozen headline is the production tournament, not a developer's
local exercise.
