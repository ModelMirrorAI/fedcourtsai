# Seed-backfill (the `run-seed` workflow's `bulk` mode)

> This page covers the **frozen** CourtListener bulk-CSV mode, kept as the
> replica-timeline fallback and reached via the `run:seed` label or dispatch
> mode=bulk. `run-seed`'s schedule and default dispatch mode run the live-channel
> **past-Term cert loader** (`fedcourts seed-live-terms`) instead — same
> checkpointed-loop shape, different source; see
> [live-sources.md](live-sources.md) and the pivot section of
> [data-pipeline.md](data-pipeline.md).

Bulk historical backfill: how the corpus is loaded with the existing backlog of
cases. It has three parts that fit together —

- **The command (`fedcourts seed-backfill`)** — loads one chunk of bulk data and
  advances a cursor; it never touches git, DVC, or GitHub.
- **The `run-seed` workflow** — calls the command in a loop and handles git/DVC.
- **The DVC-in-CI flow** — the `dvc pull → add → push` cycle around each chunk.

Design context: [data-pipeline.md](data-pipeline.md) §Seed and §Pull. Seed is
**deterministic, no agent, no API secret** — it loads the public CourtListener
**bulk** snapshot (not the REST API) into the unified corpus. The `run-seed`
workflow stages the snapshot once, then **loops** the command over it — loading a
chunk and checkpointing (DVC push + commit) after each — overnight until
complete. (A quarterly reconciliation against fresh bulk snapshots returns only
if the frozen bulk mode is revived, e.g. a replica-timeline slip.)

## 1. `fedcourts seed-backfill` — the command

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

## 2. `config/seed-progress.yaml` — the cursor

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

A `SeedProgress` pydantic model backs the file, and `schemas/seed_progress.schema.json`
is exported from it (`fedcourts export-schemas`). The validator keys on filename via
`FILENAME_MODELS`, mapping `seed-progress.yaml → SeedProgress`, so the cursor is
validated like every other artifact rather than silently skipped.

## 3. The DVC-in-CI flow

DVC is an operational tool, not a runtime dependency. In CI it is run via `uvx
--from 'dvc[s3]' dvc …`; locally it comes from the optional `data` dependency
group (`uv run dvc …`). The remote URL is injected from the runner env into the
gitignored `.dvc/config.local` before any transfer (see
[SECURITY.md](../SECURITY.md)).

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
   stays schema-valid). The PR carries only the flag — no corpus. Deduped: skip if
   `completed: true` is already on the default branch or a completion PR for the
   snapshot is open.

## 4. Triggers & the tracking issue

```yaml
on:
  schedule:    [{ cron: "23 0 * * 0" }]   # weekly — runs the past-Term cert LOADER, not this bulk mode
  workflow_dispatch:                       # inputs.mode: live-terms (default) | bulk
  issues:      { types: [labeled] }        # gate: label.name == 'run:seed' → the frozen bulk mode below
concurrency: { group: corpus-write, cancel-in-progress: false }  # shared with run-pull
```

- **One** long-lived `run:seed` **tracking issue** is open at a time. A maintainer
  opens it (there is no public form — operating the pipeline is maintainer-only)
  with the body below, then applies the `run:seed` label, which both starts the
  first run and marks the issue to comment on. The job first verifies the labeler
  has write access (see [SECURITY.md](../SECURITY.md) → *Label triggers*) before
  doing anything. The per-court checklist matters: each run flips `- [ ] <court>`
  to `- [x] <court>` for every court it finishes, so keep that exact shape.

  ```markdown
  Long-lived tracker for the seed phase. `run-seed` loads the historical backlog
  from CourtListener bulk data (no REST API budget), runs on each `run:seed`
  label or dispatch until complete,
  comments progress here after each chunk, and commits each chunk's corpus pointer
  + cursor to the default branch. When every court is loaded it opens a completion
  PR that flips the cursor's `completed` flag; merging that PR closes this issue.

  Bulk snapshot in use: <e.g. 2026-Q2>

  Per-court backfill progress (checked off as each court's history fully loads):
  - [ ] scotus
  - [ ] ca1
  - [ ] ca2
  - [ ] ca3
  - [ ] ca4
  - [ ] ca5
  - [ ] ca6
  - [ ] ca7
  - [ ] ca8
  - [ ] ca9
  - [ ] ca10
  - [ ] ca11
  - [ ] cadc
  - [ ] cafc
  ```
- `schedule`/`workflow_dispatch` runs have no triggering issue, so they resolve it:
  `gh issue list --label run:seed --state open --json number --jq '.[0].number'`.
  Each run comments; on `complete: true` it posts a final summary and opens the
  completion PR (step 5) whose merge **closes the tracker**. Never more than one
  open `run:seed` issue.
- Job permissions: `contents: write` (commit pointer+cursor to the default branch),
  `issues: write` (comment), `pull-requests: write` (open the completion PR),
  `id-token: write` (AWS OIDC for DVC). App token minted with
  contents/issues/pull-requests write.
