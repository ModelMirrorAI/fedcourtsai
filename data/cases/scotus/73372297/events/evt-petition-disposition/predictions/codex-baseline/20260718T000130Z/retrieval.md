# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition grant estimate (5.36%).

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  - Returned five recent granted-petition priors; the records showed repeated distributions for the returned grants but no close subject-matter match.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
  - `ranged corpus reads: 201 GET(s), 52559872 byte(s)`
  - Returned five recent denied-petition priors; these were used only as general procedural comparators.

## CourtListener MCP lookups

- Opinion search in the Federal Circuit for docket `2025-1769`, limited to filings before July 18, 2026: no results.
- Opinion search in the Federal Circuit for `"Jane Doe" "Secretary of Health and Human Services"`, limited to filings before July 18, 2026: two older, unrelated results; neither informed the forecast.
- RECAP search in the Federal Circuit for docket `2025-1769`, limited to filings before July 18, 2026: no results.
- RECAP search in the Federal Circuit for docket `25-1769`, limited to filings before July 18, 2026: failed with a temporary HTTP 429 throttle and yielded no information.

No web searches were used. No lookup sought or surfaced this petition's disposition.
