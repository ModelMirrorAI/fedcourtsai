# Contract: bulk seed-backfill (`run-seed` #7)

The interface between the three halves of the bulk historical backfill, so they
can be built independently and wired together without rework:

- **Python (`run:dev`)** — the `fedcourts seed-backfill` command + cursor model.
- **YAML (local)** — the `run-seed` workflow that calls it and handles git/DVC.
- **DVC/CI** — the `dvc pull → add → push` flow around the command.

Design context: [data-pipeline.md](data-pipeline.md) §Seed and §Pull. Seed is
**deterministic, no agent, no API secret** — it loads the public CourtListener
**bulk** snapshot (not the REST API) into the unified corpus. The `run-seed`
workflow stages the snapshot once, then **loops** the command over it — loading a
chunk and checkpointing (DVC push + commit) after each — overnight until complete,
then a quarterly reconciliation pass.

## 1. `fedcourts seed-backfill` — the command (Python, `run:dev`)

One invocation processes the **next chunk** and returns. It is the only piece
that knows the bulk format; it never touches git, DVC, or GitHub.

```
fedcourts seed-backfill [--max-cases N] [--report PATH] [--staging-path PATH]
```

**Reads**
- `config/tracking.yaml` → `courts:` — the courts to backfill.
- `config/seed-progress.yaml` → the cursor (created on first run if absent).
- `seed.max_cases_per_run` (config) — the chunk size loaded per invocation;
  `--max-cases` may only lower it for a one-off run.
- `--staging-path` (optional) — persist the staged snapshot here so the next
  invocation reuses it instead of re-downloading/re-staging the GB-scale bulk
  files (the build is skipped when the snapshot id matches). The workflow loop
  points this at a runner-local path so staging is paid once per job.
- The current CourtListener **bulk** snapshot (public S3/HTTP; **no API token**).
  The command is pointed at the bulk-data **base** directory and lists the bucket
  to resolve the latest published snapshot itself; a snapshot id may be pinned to
  reproduce a specific run.

**Does**
1. Load (or initialize) the cursor.
2. If the live snapshot id differs from the cursor's, start a **reconciliation**
   pass for the new snapshot (still chunked).
3. For the next court(s) with remaining work: stream the bulk rows, skip those
   already consumed (per the cursor offset), take up to `max_cases`, normalize
   each through the shared ingestion core (`fedcourtsai.pipeline.ingest`, bulk-CSV
   path → `CorpusRow`) and `corpus.upsert_rows` into `corpus/corpus.db`. A row's
   facts span several bulk files (the docket spine in `dockets`; `disposition`,
   `summary`, `judges`, `precedential_status`, and `citation_count` in
   `opinion-clusters`; `parties` / `attorneys` name lists; and the panel's judge
   names + seniority resolved from `people-db-people`), so the source stages them
   once per snapshot into a local SQLite and serves each chunk as an indexed join —
   see the staged-join note in [data-pipeline.md](data-pipeline.md) §Seed.
4. Run the **event-definition stage** (`fedcourtsai.pipeline.events.extract_events`,
   the same one forward discovery uses) over each ingested docket and
   `corpus.upsert_events` the result, so every seeded docket carries at least its
   **baseline** predictable event (the appeal/petition disposition). Bulk rows
   rarely carry docket entries, so the richer entry-pinned events
   (`motion` / `petition` / `order`) appear only where the bulk data includes the
   entries; elsewhere the baseline stands and a later `pull` refresh enriches the
   case. This is idempotent — re-loading a snapshot during a quarterly
   reconciliation re-upserts the same events in place. An entry the classifier
   cannot place is recorded (not guessed) for a later agent reconcile and surfaced
   as a count on the report, never crashing the chunk.
5. **Hand off the discovery frontier.** When a court's backfill completes, set its
   **discovery watermark** (corpus tracking state) to the snapshot's date —
   derived from the quarter id (`2026-Q2` → `2026-06-30`, the last day CourtListener
   regenerated it). The first forward `pull` then discovers everything filed since
   the snapshot, not since today, closing the snapshot→today gap. The watermark only
   moves forward, so a later forward watermark always wins and a re-run never rewinds
   it; a snapshot id that is not a quarter label hands off nothing. See
   [data-pipeline.md](data-pipeline.md) §Discovery frontier.
6. Advance the cursor; write the report.

**Writes (only these two paths, plus corpus tracking state)**
- `corpus/corpus.db` — the SQLite blob (DVC-managed; the workflow handles DVC).
  Holds both the raw rows/events and the per-court discovery watermark above.
- `config/seed-progress.yaml` — the bumped cursor.

**Returns** — exit 0 on success; idempotent (re-running after completion loads 0).
`--report` emits progress JSON for the tracking-issue comment:

```json
{
  "snapshot": "2026-Q2",
  "complete": false,
  "loaded_this_run": 1500,
  "courts": [
    { "court": "ca9", "loaded": 12000, "total": 45000, "percent": 26.7, "complete": false }
  ]
}
```

## 2. `config/seed-progress.yaml` — the cursor (Python, `run:dev`)

Git-tracked (small, worth reading in a diff), schema-validated like every other
artifact.

```yaml
snapshot: "2026-Q2"          # bulk snapshot id currently being loaded
completed: false             # maintainer sign-off; flipped true only by the
                             # completion PR (never by the backfill). Distinct
                             # from the per-court `complete` flags below.
courts:
  ca9:
    offset: 12000            # rows consumed from this court's bulk stream
    total: 45000             # rows for this court in the snapshot (if known)
    complete: false
  scotus:
    offset: 8000
    total: 8000
    complete: true
```

- Add a `SeedProgress` pydantic model and export `schemas/seed_progress.schema.json`
  (`fedcourts export-schemas`).
- **Register it in `validate`** — the validator keys on filename via
  `FILENAME_MODELS`, so map `seed-progress.yaml → SeedProgress` or the file is
  silently skipped.

## 3. The DVC-in-CI flow (workflow, local)

No workflow pushes the corpus to S3 yet, so this establishes the pattern. DVC is
operational, run via `uvx --from 'dvc[s3]' dvc …` (not a package dependency). The
remote URL is injected from the runner env into the gitignored `.dvc/config.local`
before any transfer (see [SECURITY.md](../SECURITY.md)).

Per-run order:
1. `dvc remote add --local -d storage "<bucket url from runner env>"` — define the
   remote (no-op if already local-configured).
2. `dvc pull` — fetch the current `corpus/corpus.db` blob. **No-op on first run**
   (no pointer yet); guard accordingly.
3. **Loop until the backlog is done or a wall-clock budget runs out**, each pass:
   1. `fedcourts seed-backfill --staging-path "$RUNNER_TEMP/…" --report seed-report.json`
      — load one chunk into the blob + cursor (the first pass also stages the
      snapshot into the runner-local path; later passes reuse it).
   2. `dvc add corpus/corpus.db` → `dvc push` — refresh the `corpus/corpus.db.dvc`
      pointer and upload the new blob to S3 (blob first, so the pointer always
      resolves remotely).
   3. Commit **`corpus/corpus.db.dvc` + `config/seed-progress.yaml`** directly to
      the default branch (pointer + cursor only; the blob never enters git), with a
      rebase-retry so the push is a fast-forward. This per-chunk checkpoint bounds
      crash-loss to one chunk and lets the next run resume from the cursor. Seed and
      pull share the `corpus-write` concurrency lock and both commit straight to the
      default branch, so each run builds on the latest pointer — see the
      corpus-writer coordination model in [data-pipeline.md](data-pipeline.md).
   4. Stop when the report says `complete: true`, a chunk loads 0 cases, or the
      budget is spent.
4. Comment progress on the tracking issue from `seed-report.json` (its
   `loaded_this_run` is overwritten with the loop's running total).
5. When `seed-report.json` reports `complete: true`, open a one-time **completion
   PR** that flips the cursor's `completed` flag (through the model, so the file
   stays schema-valid) with `Closes #<tracker>` in the body. The PR carries only
   the flag — no corpus. Deduped: skip if `completed: true` is already on the
   default branch or a completion PR for the snapshot is open.

## 4. Triggers & the tracking issue (workflow, local)

```yaml
on:
  schedule:    [{ cron: "23 0 * * 0" }]   # weekly, overnight; a quarterly reconciliation ends before run-pull (07:17)
  workflow_dispatch:
  issues:      { types: [labeled] }        # gate: label.name == 'run:seed'
concurrency: { group: corpus-write, cancel-in-progress: false }  # shared with run-pull
```

- **One** long-lived `run:seed` **tracking issue** is open at a time (opened from
  `.github/ISSUE_TEMPLATE/seed.yml` *after #7 merges*). The label both starts the
  first run and marks the issue to comment on.
- `schedule`/`workflow_dispatch` runs have no triggering issue, so resolve it:
  `gh issue list --label run:seed --state open --json number --jq '.[0].number'`.
  Comment each run; on `complete: true` post a final summary and open the
  completion PR (step 5) whose merge **closes the tracker**. Convention: never
  more than one open `run:seed` issue.
- Job permissions: `contents: write` (commit pointer+cursor to the default branch),
  `issues: write` (comment), `pull-requests: write` (open the completion PR),
  `id-token: write` (AWS OIDC for DVC). App token minted with
  contents/issues/pull-requests write.

## Build order

1. **[run:dev]** §1 + §2 — the command, cursor model, schema, validate registration,
   fully typed with tests. Lands first (the workflow can't call a missing command).
2. **[local]** §3 + §4 — rewrite `run-seed.yml` to this design (replacing the
   single-docket workflow), verified with `zizmor`.

This contract is independent of #23 (single-docket CLI reconciliation) — it adds a
new bulk command and path — so it can proceed in parallel.
