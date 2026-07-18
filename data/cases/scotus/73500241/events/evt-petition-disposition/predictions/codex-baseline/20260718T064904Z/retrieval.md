# Retrieval beyond the provisioned inputs

## Corpus and base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” relist and CVSG cuts, and the 2025 Term row.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  - `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 8`
  - `ranged corpus reads: 204 GET(s), 53477376 byte(s)`

The corpus lookups supplied broad modern grant/deny comparators, including distribution counts, counsel, companion-case patterns, and salience metadata. They were used as general priors only, not to seek this case's outcome.

## CourtListener MCP

- Opinion search for `"continued retention" property "Fourth Amendment"`, limited to decisions filed before May 28, 2026. Results included *Oyoma Asinor v. District of Columbia*, 111 F.4th 1249 (D.C. Cir. 2024), *Jessop v. City of Fresno*, 936 F.3d 937 (9th Cir. 2019), and *Bell v. City of Chicago*, 835 F.3d 736 (7th Cir. 2016).
- Opinion search for `"illegal exaction" tax "Due Process" Fifth Amendment`, limited to decisions filed before May 28, 2026. Results were concentrated in the Federal Circuit and Court of Federal Claims, including *Starr International Co. v. United States*, 856 F.3d 953 (Fed. Cir. 2017).
- Exact case-name search for `Honda Lease Trust v. Malanga's Auto`, which returned no result.
- Citation search for `152 F.4th 477`, which returned no result.
- Broader opinion search for `Honda Lease Trust Malanga Auto`, limited to decisions filed before May 28, 2026. It located the published Third Circuit decision *Honda Lease Trust v. Malanga's Automotive*, filed September 15, 2025.

No web search was used, and no lookup targeted this case's disposition or subsequent history.
