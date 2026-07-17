# Retrieval

## Corpus tooling

- Attempted `uv run fedcourts query --court scotus --topic 'Rehabilitation Act independent contractor' --limit 8` (with the runner's disposable `uv` cache redirected to `/tmp`). The lookup failed because the ranged corpus remote hostname could not be resolved. It returned no prior rows and emitted no `ranged corpus reads: ...` summary.
- Consulted `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and per-Term sections, and `metrics/statpack.json` for the 2025 paid-petition rate.

## CourtListener MCP

- `search` for opinions matching `"independent contractor" "Rehabilitation Act"`, limited to filings before 2026-07-17. This returned, among other results, the published *Flynn*, *Fleming*, *Smith v. CSRA*, and Arkansas decisions.
- `get_endpoint_item` for cluster 5065415, identifying *Tina Smith v. CSRA*, 12 F.4th 396 (4th Cir. 2021), and its sub-opinion.
- `get_endpoint_item` for opinion 4880796, the *Smith* opinion. It involved a distinguishable federal-contractor setting and was not used as a square split authority.
- `search` for *Thiersaint* with `"independent contractor" "Section 504"`; no results were returned.
- `search` for `Flynn Fleming Wojewski "independent contractor"`, limited to filings before 2026-07-17. It returned *Flynn* and the decision below.
- `get_endpoint_item` for cluster 10807794, identifying the published decision below, 2026 Ark. 53, and its sub-opinion.
- `get_endpoint_item` for opinion 11274535, the full March 12, 2026 Arkansas opinion. It confirmed the majority's split analysis, its retaliation-specific distinction of *Flynn*, and the partial dissent.

No search sought this case's disposition or post-snapshot history.
