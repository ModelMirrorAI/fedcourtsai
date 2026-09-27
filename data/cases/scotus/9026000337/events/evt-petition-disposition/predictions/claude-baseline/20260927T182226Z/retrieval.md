# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-27.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `documents/documents.json`, the event definition, the committed `metrics/statpack.md`, and the schemas):

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   stderr: `ranged corpus reads: 11 GET(s), 2752512 byte(s)`
   Returned five OT2025 substantive applications/grants (election-law and federal-party matters). Not substantively similar; used only to confirm the query surface worked.
2. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Returned five recent OT2025 denials (pro se and IFP-type matters). Not substantively similar.

## CourtListener MCP (`mcp__courtlistener__search`, type `o`)

3. Query `"known loss" "guaranteed issue" "long-term care"` — 0 results. Consistent with the petition's claim that no reported decision applies the known-loss doctrine to guaranteed-issue LTC coverage.
4. Query `"postclaims underwriting" OR "post-claims underwriting" "long-term care" Iowa` — 399 hits, the first page dominated by Iowa workers'-compensation cases naming the Iowa Long Term Care Risk Management Association; nothing on point. Not pursued further.

No web searches. No lookup of this docket's own current state or disposition.
