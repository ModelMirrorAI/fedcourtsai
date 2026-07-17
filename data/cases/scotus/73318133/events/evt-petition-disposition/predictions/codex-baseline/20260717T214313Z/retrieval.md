# Retrieval beyond the provisioned inputs

## Committed base rates

- `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term sections.
- `metrics/statpack.json`, 2025 Term fee-class detail (estimated paid grant rate 5.36%; IFP grant rate 1.12%).

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 202 GET(s), 52887552 byte(s)`
  - Returned five recent denied SCOTUS petitions for broad docket-signal context.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 145 GET(s), 37945344 byte(s)`
  - Returned five recent granted SCOTUS petitions for broad docket-signal context.

## CourtListener MCP lookups

- Opinions search for `"workable and useful evidentiary tool" "McDonnell Douglas"`, limited to filings before July 18, 2026. It returned *Ames v. Ohio Department of Youth Services*, 605 U.S. 303 (2025).
- Ninth Circuit opinions search for `"California Labor Code" 6310 "McDonnell Douglas"`, limited to filings before July 18, 2026. It returned no results.
- Ninth Circuit opinions search for `"Labor Code section 6310" retaliation`, limited to filings before July 18, 2026. It returned five results, including published decisions in *Freund v. Nycomed Amersham*.

No web search was used. No lookup sought this case's disposition or subsequent history.
