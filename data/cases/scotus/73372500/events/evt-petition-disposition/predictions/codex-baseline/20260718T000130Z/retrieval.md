# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025-Term paid-petition estimate.

## Corpus lookup

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
  - `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  - Returned recent grant-side priors used only for qualitative comparison of CVSG and distribution-count signals.

## CourtListener MCP

- Opinion search for `"substantive due process" zoning "ultra vires"`, limited to filings before May 15, 2026. The search returned 174 results; the leading results were mostly state and trial-court decisions and did not materially change the forecast.
- Opinion search for `(“Cine SK8” OR “Hillcrest Property”) AND “substantive due process”`, limited to filings before May 15, 2026. The first attempt received an HTTP 429 throttle response advising a three-second retry.
- Retried the same opinion search successfully. It returned 49 results and confirmed the cited Second Circuit decision, *Cine SK8, Inc. v. Town of Henrietta*, 507 F.3d 778 (2007), and Eleventh Circuit decision, *Hillcrest Property, LLP v. Pasco County*, 915 F.3d 1292 (2019).

No web searches were used.
