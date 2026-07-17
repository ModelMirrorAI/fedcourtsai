# Retrieval beyond the provisioned inputs

## Committed base rates

- Read `metrics/statpack.md`, including the modern discretionary-cert, originating-court, relist, CVSG, and Term tables.
- Read the Term 2025 fee-class detail in `metrics/statpack.json`.

## Corpus lookup

- `uv run fedcourts query --court scotus --era 2020s --limit 5`
  - `ranged corpus reads: 429 GET(s), 112328704 byte(s)`
  - Returned five recent, salience-selected SCOTUS dockets. They were used only as general docket context because they were not close factual comparators.

## CourtListener MCP lookups

- Opinion search for `"order of protection" "First Amendment" harassment`, limited to filings before July 18, 2026 (five results). This established that the query surfaced mostly state, fact-specific protective-order cases and no obvious controlling split.
- Opinion search for `"Illinois Domestic Violence Act" constitutional "order of protection"`, limited to filings before July 18, 2026 (eight results). This surfaced Illinois appellate decisions but no obvious conflict warranting certiorari.
- SCOTUS opinion search for *United States v. Rahimi*, limited to filings before July 18, 2026. This confirmed the 2024 decision and citation, 602 U.S. 680.
- Opinion search for case name `Dittmer`, limited to filings before July 18, 2026 (eight results). It did not surface the petitioners' Illinois appellate opinion or any disposition of this petition.

No web searches were used.
