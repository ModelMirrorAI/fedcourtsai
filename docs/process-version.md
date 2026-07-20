# Process versioning: which predictions count toward the headline

Predictions committed during the July/August shakedown are real, timestamped
forward calls — irreplaceable forward-stratum data — but they ran under a process
still being corrected. The headline metrics must reflect only the **frozen,
correct** process, without deleting the shakedown runs (a wipe reads as hiding
results, not rigor). This is the same doctrine as [`sal-v1`](salience.md): a
process change is a **new version**, never an in-place edit, so any past ranking
always replays against the process that produced it.

## What a "process" is, and how it is identified

The process behind one predictor cell is its **prompt template plus its resolved
registry config** — the engine, the resolved model (the registry override, else
the engine default), and the pinned MCP tool manifest. The harness stamps each
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

The digest excludes documentation that does not change behaviour — the actor's
`description` and the MCP manifest `description` are comments, not process inputs,
so editing one does not re-version anything.

## The stamp is the harness's word, not the agent's

The agent writes `prediction.json` / `evaluation.json`; a post-agent step
(`fedcourts stamp-cell`, in both `run-predict` and `run-evaluate`, before
`validate`) reads that file and injects the `ProcessVersion` derived from the
registry. So a cell's version is what the harness resolved at run time, exactly
as `usage.json` records the engine's own log rather than trusting the agent — a
compromised or hallucinating agent cannot fake its process version.

The stamp step is deterministic and local, so unlike the best-effort log
captures beside it, it is **must-succeed**: a missing artifact (a no-output cell)
is a clean no-op, but a registry/prompt inconsistency fails the cell rather than
shipping an unstamped-but-frozen-looking prediction. An evaluate cell scores every
predictor, so the evaluator stamp covers all of its `evaluation.json`.

## Three states: shakedown → not-yet-frozen → frozen

`FROZEN_PROCESS_DIGESTS` (in `fedcourtsai.process_version`) is the blessed set —
the digests whose cells count toward the headline. Everything keys off it:

- **Shakedown** — a cell written before the stamp existed carries no
  `process_version`. It is never frozen (an absent stamp cannot be in the set),
  so the whole shakedown ledger drops out of the headline for free — no backfill,
  no deletion.
- **Not-yet-frozen** — a stamped cell whose digest has not been blessed. The
  freeze is a **future** event; until it happens, `FROZEN_PROCESS_DIGESTS` is
  empty and *no* digest is frozen. During this window the frozen headline is
  legitimately **empty** — "no frozen-process evaluations yet" — which the
  leaderboard, the ops dashboard, and the weekly digest all say in as many words,
  rather than showing a bare `0` that reads as a regression.
- **Frozen** — a stamped cell whose digest is in the blessed set.

## What defaults to frozen, and what stays version-blind

The frozen filter lives at the one shared producer both surfaces read
(`store.iter_stratified_evaluations`, `frozen_only=True` by default), so the
leaderboard headline and the ops dashboard's scored figures can never disagree —
they each pass one boolean. Both CLIs take `--all-versions` for the pooled
shakedown view. The filter partitions on the **prediction's** stamp: the
competitor being ranked is the predictor.

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

The freeze is a deliberate, reviewable **one-line commit**, run when the process
is settled and the first frozen predictions are about to land:

1. Read the current digests: `fedcourts process-digest --all` prints the label,
   role, id, and digest of every enabled predictor and evaluator.
2. Paste the digest(s) to bless into `FROZEN_PROCESS_DIGESTS` in
   `src/fedcourtsai/process_version.py`.
3. Commit. Because the digest excludes `pipeline_sha`, the blessed set survives
   unrelated pipeline commits — predict/evaluate can resume at a newer HEAD and
   still match.
4. Record that commit as the cutover in [milestones.md](milestones.md).

From that commit forward, the first long-conference prediction lands under the
stamped, frozen process and the headline fills in. When the process later changes
materially, bump `CURRENT_PROCESS_LABEL` to `proc-v2`; the old `proc-v1` cells
keep their stamp and remain replayable against the process that produced them,
never overwritten.

## A note on local runs

The local `cascade` / `local-cascade` path produces cells but does **not** run the
`stamp-cell` step (that is a workflow step, not part of the runner). So a local
cascade's cells are unstamped and appear only under `--all-versions`. This is
intended: the frozen headline is the production tournament, not a developer's
local exercise.
