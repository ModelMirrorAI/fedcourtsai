# Retrieval log — claude-judge, 20260902T185700Z

Beyond the provisioned inputs (event.yaml, outcome.json, the blinded candidate
directories, record/context.json, record/snapshots/2026-08-31.json):

## Committed base rates

- `metrics/statpack.md`, "The interim docket (applications)" — grepped for the
  section, then read it in full (caption plus per-Term table). Used to state
  the strictly-prior pool a reader of the stamped rate should expect (Terms
  2025 + 2024: 296 resolved / 31 granted ≈ 10.5%, clearing the 50-resolved
  floor) and to check each candidate's quoted baseline.

## Corpus

- `uv run fedcourts query --help` only, to see whether the query surface could
  expose the superseded 2026-08-29 snapshot two candidates were provisioned
  (it exposes case rows, not snapshot history). **No query was executed** — no
  `ranged corpus reads` line to record.

## CourtListener MCP

- None.

## Web searches

- None. This case's own disposition was read only from the committed
  `outcome.json` and the committed 2026-08-31 snapshot.
