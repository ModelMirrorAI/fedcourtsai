# Retrieval

## Committed base-rate context

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist-count, CVSG-status, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term's paid-petition estimate (5.36%).

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 8`
  - `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
  - Returned eight recent resolved SCOTUS matters. I used them only as weak procedural priors about conference-distribution counts and grant selection; their substantive issues were not treated as comparable to this petition.

## CourtListener MCP lookups

- Opinions search for `Napue plain error false testimony closing argument prosecutor capitalize`, limited to opinions filed before July 19, 2026. The results included *People v. Smith* and other false-testimony decisions but did not reveal a cleaner conflict than the authorities collected in the petition.
- Opinions search for `Rule 702 harmless error no gatekeeping appellate court credentials experience`, limited to opinions filed before July 19, 2026. The results included *United States v. Ruvalcaba-Garcia* and other gatekeeping decisions but did not materially strengthen the asserted split.
- Exact SCOTUS opinion search for *Glossip v. Oklahoma*, filed in 2025 through July 18, 2026. This confirmed the February 25, 2025 decision at 604 U.S. 226.

No web searches were used. I did not search for this petition's disposition or subsequent history.
