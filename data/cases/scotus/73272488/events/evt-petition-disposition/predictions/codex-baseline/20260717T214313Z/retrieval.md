# Retrieval beyond the provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and per-Term sections.
- Consulted `metrics/statpack.json` for the 2025 Term fee-class detail; the estimated paid-petition grant rate was 5.36%.

## Corpus lookup

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  - `ranged corpus reads: 148 GET(s), 38731776 byte(s)`
  - Returned recent grant-side priors and distribution counts, but no issue-specific comparator; I treated them as broad context only.

## CourtListener MCP lookups

- Opinion search for `"United States v. Tovar" "Rule 29"`, limited to filings before July 18, 2026. The returned results were unrelated and supplied no usable information.
- Opinion citation search for `146 F.4th 1318`, limited to filings before July 18, 2026. It returned no result.

No web searches were used. Neither lookup surfaced this case's disposition or other outcome-revealing information.
