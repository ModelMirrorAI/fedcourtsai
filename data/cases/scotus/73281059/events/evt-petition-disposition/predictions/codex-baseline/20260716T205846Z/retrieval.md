# Retrieval

## Corpus and base-rate lookups

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025-Term paid-petition grant estimate.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '570 U.S. 1' --limit 8`.
  - Result: failed before returning priors because the ranged corpus endpoint could not resolve.
  - No `ranged corpus reads: …` line was emitted.

## CourtListener MCP lookups

- Searched opinions for case name `Mi Familia Vota`, court `ca9`, filed before 2026-02-19, returning up to five metadata-only results. The two results were an unrelated 2020 Ninth Circuit matter and did not inform the forecast.
- Searched opinions for citation `129 F.4th 691`, returning no result.
- Searched Supreme Court opinions for citation `570 U.S. 1`, returning *Arizona v. Inter Tribal Council of Arizona, Inc.*, No. 12-71, filed June 17, 2013. This confirmed the controlling precedent identified in the provisioned filings.

No web searches were used. No lookup sought or surfaced this petition's disposition.
