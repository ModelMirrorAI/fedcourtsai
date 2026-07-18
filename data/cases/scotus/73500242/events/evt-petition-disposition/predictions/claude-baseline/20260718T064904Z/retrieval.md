# Retrieval log — scotus/73500242, evt-petition-disposition, claude-baseline, 20260718T064904Z

Beyond the provisioned inputs (snapshot, `questions-presented.txt`,
`petition.txt`, `documents.json`, `record/context.json`):

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  "Modern cert petitions by originating circuit" (ca5: granted 4.8%),
  "Cert petitions by relist count" (0 relists: granted 0.8%),
  "Cert petitions by CVSG status", "SCOTUS cert petitions by Term".
- `metrics/statpack.json` — Term-2025 per-fee-class detail (paid: est. grant
  rate 5.4%; IFP: 1.1%).

## Corpus lookups (`fedcourts query`)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  — sampled recent granted petitions to compare grant-side signals (counsel,
  distribution counts, amici) against this case.
  stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
- One malformed invocation (an unsupported `--query` free-text flag) errored at
  argument parsing; no corpus read occurred.

## CourtListener MCP

- None. The provisioned snapshot is dated today (2026-07-18) and already
  reflects the July 15 distribution; no live lookup was needed.

## Web searches

- None.
