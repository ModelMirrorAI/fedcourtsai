# Retrieval log — claude-baseline, 20260816T173750Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `record/documents/` petition / brief-in-opposition /
questions-presented, `event.yaml`), I consulted:

## Committed statpack

- `metrics/statpack.md`, "The merits docket (granted cases)" — pooled the
  per-Term disturbed rates over grant Terms 2017–2024 (the strictly-prior
  window the pack holds for a Term-2025 grant): 359/515 = 69.7%. The section
  publishes an `excluded` count (67), so the rate is quotable and is the
  scored baseline.

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "541 U.S. 401" --citation
  "553 U.S. 571" --limit 5` — sought priors sharing the Court's EAJA cites
  (Scarborough, Richlin). Zero rows returned; the tool's own note reported
  the citation column sparse (161 of 590,339 scotus rows), i.e. missing data
  rather than no match. Not retried per the sparse-filter guidance.
  - `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`

## CourtListener MCP

- One `search` call (dockets, court=scotus, q="Daley Ceja" — checking the
  companion Tenth Circuit case's cert posture). Failed with HTTP 429
  (daily rate limit exhausted upstream); no results obtained, and no further
  CourtListener calls were made.

## Web searches

None.
