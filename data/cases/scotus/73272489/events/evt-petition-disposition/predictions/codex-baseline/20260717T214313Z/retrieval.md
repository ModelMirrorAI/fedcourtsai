# Retrieval

## Committed base-rate context

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit and originating-court cuts, relist count, CVSG status, and the per-Term table.
- Consulted `metrics/statpack.json` for 2025-Term paid-filing detail (estimated grant rate 5.36%). These are committed files, so no ranged-read transfer line applies.

## Corpus tooling

- Consulted `uv run fedcourts query --help` for the supported filters.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 148 GET(s), 38731776 byte(s)`
  - Returned five recent granted SCOTUS petitions for general calibration; none was treated as a close factual match.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 198 GET(s), 51838976 byte(s)`
  - Returned five recent denied SCOTUS petitions for general calibration; none was treated as a close factual match.

## CourtListener MCP

- Opinion search: `court=scotus`, query `"state law" "due process" evidentiary ruling civil trial`, ordered by relevance, five results. The results were general due-process opinions and provided no close analogue.
- Opinion search: `court=scotus`, query `"Federal Rules of Evidence" "state court"`, ordered by relevance, five results. The results included *Smith v. Arizona*, *General Electric Co. v. Joiner*, *Jaffee v. Redmond*, and *Daubert v. Merrell Dow Pharmaceuticals, Inc.*; they were used only as background orientation, not as case-specific outcome evidence.

No web search was used. No lookup sought this case's disposition, later history, or current docket state.
