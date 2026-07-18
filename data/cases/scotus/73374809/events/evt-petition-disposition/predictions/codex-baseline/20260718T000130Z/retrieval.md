# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-court, relist, CVSG, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid fee-class estimate (5.36% grant rate).

## Corpus queries

- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 205 GET(s), 53608448 byte(s)`
  - Returned five recent denied SCOTUS petitions for coarse calibration; none was treated as a close factual analogue.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 146 GET(s), 38273024 byte(s)`
  - Returned five recent granted SCOTUS petitions for coarse calibration of visible grant signals.

## CourtListener MCP

- Opinion search: `"medical license" Indian reservation physician state licensing Commerce Clause`, limited to filings before July 17, 2026. Four results appeared, none directly relevant.
- SCOTUS opinion search: `"state licensing" physician reservation tribe`, limited to filings before July 17, 2026. No results appeared.

No general web search was used.
