# Retrieval beyond the provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, Fifth Circuit origin, relist-count, CVSG, and per-Term tables.
- Consulted the 2025 Term paid-petition detail in `metrics/statpack.json` (estimated paid grant rate 5.36%). The current artifacts did not contain the salience-band table referenced by the predictor prompt.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
  - Returned five recent grant priors. I used them only as qualitative procedural comparators (distribution count, counsel, CVSG, and court of origin), not as subject-matter matches.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 204 GET(s), 53477376 byte(s)`
  - Returned five recent denial priors. I used them on the same limited basis.

## CourtListener MCP

All opinion searches were restricted to material filed before May 26, 2026, and did not search for this petition or its disposition.

- Opinion search: `"markedly hostile" "1981" restaurant` (28 results; reviewed the first 10 metadata results, including *Keck v. Graham Hotel Systems, Inc.* and *Lizardo v. Denny's, Inc.*).
- Case-name searches for *Hager v. Brinker Texas*, *Eddy v. Waffle House*, and *Christian v. Wal-Mart Stores* to identify the controlling and asserted conflict authorities.
- Cluster metadata lookups for *Hager* (cluster 9506378), *Keck* (1470786), *Lizardo* (775405), and *Christian* (773564), including filing date, published status, citations, and linked opinion identifiers.
- Opinion-text lookups for *Hager* (opinion 9972991) and *Keck* (opinion 1470786). These confirmed that *Hager* involved an alleged denial of further restaurant service followed by departure, while *Keck* applied the markedly-hostile framework to failure to consummate a wedding-services contract.

No general web search was used.
