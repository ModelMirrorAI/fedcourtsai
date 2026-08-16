# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, and the three `record/documents/` texts — the
questions-presented, the petition, and the brief-in-opposition file, which
also bundles the respondent's August 2026 merits brief):

- Committed base rates: `metrics/statpack.md`, "The merits docket (granted
  cases)" section — pooled the per-Term `disturbed`/`parsed` counts over grant
  Terms 2015–2024 (rendered rows 2017–2024): 359/515 = 69.7%.
- Corpus query (one call, no useful rows returned):
  - Command: `uv run fedcourts query --court scotus --citation "598 U.S. 729" --limit 5`
  - stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  - stderr note: citation column sparse (161 of 590,339 rows in scope carry
    citation data); empty result reflects missing data, not no match. No
    priors were used from this call.
- No CourtListener MCP lookups and no web searches were made.
