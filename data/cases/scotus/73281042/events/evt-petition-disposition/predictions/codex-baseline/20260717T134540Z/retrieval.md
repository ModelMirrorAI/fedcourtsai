# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. Relevant estimates were: modern discretionary-cert petitions (367 granted, 11,115 denied, 230 dismissed); 2025 Term paid petitions (5.36% granted); petitions without a CVSG (3.0% granted); and CVSG petitions (27.1% granted).

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '530 U.S. 640' --limit 10`
  - The lookup failed before producing results because the runner could not resolve the remote corpus endpoint. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP lookups

- Opinions search by citation `530 U.S. 640` (3 results requested): located *Boy Scouts of America v. Dale*, Supreme Court of the United States, filed June 28, 2000.
- Opinions search by citation `103 F.4th 765` (3 results requested): located *American Alliance for Equal Rights v. Fearless Fund Management, LLC*, Eleventh Circuit, filed June 3, 2024.
- Opinions search for `expressive association antidiscrimination leadership Dale Runyon`, limited to filings before July 17, 2026 (5 results requested): returned six matches, led by *Dale*, plus less directly relevant authorities.
- Opinions search by citation `468 U.S. 609` (3 results requested): located *Roberts v. United States Jaycees*, Supreme Court of the United States, filed July 3, 1984.
- Opinions search by citation `167 F.4th 86` (3 results requested): returned no match.

No web searches were used.
