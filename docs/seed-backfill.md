# Contract: bulk seed-backfill (`run-seed` #7)

The interface between the three halves of the bulk historical backfill, so they
can be built independently and wired together without rework:

- **Python (`run:dev`)** — the `fedcourts seed-backfill` command + cursor model.
- **YAML (local)** — the `run-seed` workflow that calls it and handles git/DVC.
- **DVC/CI** — the `dvc pull → add → push` flow around the command.

Design context: [data-pipeline.md](data-pipeline.md) §Seed and §Pull. Seed is
**deterministic, no agent, no API secret** — it loads the public CourtListener
**bulk** snapshot (not the REST API) into the unified corpus, one chunk per run,
daily until complete, then a quarterly reconciliation pass.

## 1. `fedcourts seed-backfill` — the command (Python, `run:dev`)

One invocation processes the **next chunk** and returns. It is the only piece
that knows the bulk format; it never touches git, DVC, or GitHub.

```
fedcourts seed-backfill [--max-cases N] [--report PATH]
```

**Reads**
- `config/tracking.yaml` → `courts:` — the courts to backfill.
- `config/seed-progress.yaml` → the cursor (created on first run if absent).
- `seed.max_cases_per_run` (config) — default chunk size; `--max-cases` overrides.
- The current CourtListener **bulk** snapshot (public S3/HTTP; **no API token**).

**Does**
1. Load (or initialize) the cursor.
2. If the live snapshot id differs from the cursor's, start a **reconciliation**
   pass for the new snapshot (still chunked).
3. For the next court(s) with remaining work: stream the bulk rows, skip those
   already consumed (per the cursor offset), take up to `max_cases`, normalize
   each through the shared ingestion core (`fedcourtsai.pipeline.ingest`, bulk-CSV
   path → `CorpusRow`) and `corpus.upsert_rows` into `corpus/corpus.db`.
4. Advance the cursor; write the report.

**Writes (only these two paths)**
- `corpus/corpus.db` — the SQLite blob (DVC-managed; the workflow handles DVC).
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
3. `fedcourts seed-backfill --report seed-report.json` — mutate the blob + cursor.
4. `dvc add corpus/corpus.db` — refresh the `corpus/corpus.db.dvc` pointer.
5. `dvc push` — upload the new blob to S3.
6. Commit **`corpus/corpus.db.dvc` + `config/seed-progress.yaml`** directly to the
   default branch (pointer + cursor only; the blob never enters git). Seed and pull
   share the `corpus-write` concurrency lock and both commit straight to the default
   branch, so each run builds on the latest pointer — see the corpus-writer
   coordination model in [data-pipeline.md](data-pipeline.md).
7. Comment progress on the tracking issue from `seed-report.json`.

## 4. Triggers & the tracking issue (workflow, local)

```yaml
on:
  schedule:    [{ cron: "23 6 * * *" }]   # daily, staggered from run-pull (07:17)
  workflow_dispatch:
  issues:      { types: [labeled] }        # gate: label.name == 'run:seed'
concurrency: { group: corpus-write, cancel-in-progress: false }  # shared with run-pull
```

- **One** long-lived `run:seed` **tracking issue** is open at a time (opened from
  `.github/ISSUE_TEMPLATE/seed.yml` *after #7 merges*). The label both starts the
  first run and marks the issue to comment on.
- `schedule`/`workflow_dispatch` runs have no triggering issue, so resolve it:
  `gh issue list --label run:seed --state open --json number --jq '.[0].number'`.
  Comment each run; on `complete: true` post a final summary (a maintainer closes
  it). Convention: never more than one open `run:seed` issue.
- Job permissions: `contents: write` (commit pointer+cursor to the default branch),
  `issues: write` (comment), `id-token: write` (AWS OIDC for DVC). App token minted
  with contents/issues write.

## Build order

1. **[run:dev]** §1 + §2 — the command, cursor model, schema, validate registration,
   fully typed with tests. Lands first (the workflow can't call a missing command).
2. **[local]** §3 + §4 — rewrite `run-seed.yml` to this design (replacing the
   single-docket workflow), verified with `zizmor`.

This contract is independent of #23 (single-docket CLI reconciliation) — it adds a
new bulk command and path — so it can proceed in parallel.
