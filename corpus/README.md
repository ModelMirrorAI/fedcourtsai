# Historical corpus (DVC-tracked)

The **packed historical tier** of the two-tier store described in
[../docs/data-pipeline.md](../docs/data-pipeline.md). The active, curated
prediction targets live as reviewable YAML/JSON under `data/cases/`; the
historical *mass* (millions of resolved dockets across SCOTUS + the 13 courts of
appeals) is packed here instead, because per-case files would choke git.

## Layout

```
corpus/
  shards/                 # Parquet shards, one per court (DVC-managed, gitignored)
    scotus.parquet
    ca9.parquet
    ...
  shards.dvc              # DVC pointer committed to git (created by `dvc add shards`)
  README.md               # this file
  .gitignore              # keeps the data blobs out of git
```

- **Format:** Parquet shards, sharded by court id. Columnar Parquet keeps the
  labeled corpus compact and queryable for back-testing and retrieval. (A single
  SQLite database is the documented fallback if cross-court queries dominate.)
- **Versioning:** the shards are tracked with **DVC** — data in the remote, the
  `shards.dvc` pointer plus the [seed cursor](../config/seed-progress.yaml) in
  git. The corpus is rebuildable from a fresh clone via `dvc pull`.
- **Row schema:** `fedcourtsai.schemas.CorpusRow` (exported to
  [`schemas/corpus_row.schema.json`](../schemas/corpus_row.schema.json)). Each row
  is normalized and **labeled** (`disposition`), so the corpus doubles as a
  back-test set and a retrieval index.

## Working with the corpus

```bash
uv sync --extra dvc                 # install the dvc[s3] toolchain
dvc pull                            # fetch shards from the remote
# ... seed writes / appends corpus/shards/<court>.parquet ...
dvc add corpus/shards               # refresh the pointer after a backfill chunk
dvc push                            # upload blobs to the remote
git add corpus/shards.dvc config/seed-progress.yaml
```

The remote and its credential-free OIDC wiring are documented in
[../SECURITY.md](../SECURITY.md) and [../docs/data-pipeline.md](../docs/data-pipeline.md).
