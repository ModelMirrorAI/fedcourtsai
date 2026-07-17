# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially "Modern discretionary-cert petitions by disposition," "Cert petitions by relist count," "Cert petitions by CVSG status," and "SCOTUS cert petitions by Term."
- Consulted the 2025 paid-petition detail in `metrics/statpack.json` (estimated grant rate 5.36%).

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation 'Ramos v. Louisiana' --era 2020s --limit 8`
  - Failed because the runner could not resolve the remote corpus-store host. No `ranged corpus reads: ...` line was produced and no rows were used.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation 'Richardson v. United States' --era 2020s --limit 8`
  - Failed for the same DNS reason. No `ranged corpus reads: ...` line was produced and no rows were used.

## CourtListener MCP

- Opinion search for `"continuous sexual abuse" unanimity Richardson Ramos`, limited to filings before April 15, 2026. This returned the Texas cases discussed in the petition and *State v. Young*, among other results.
- Opinion search for `("continuous sexual abuse" OR "continuous course of sexual abuse") "jury unanimity"`, limited to filings before April 15, 2026. This was used to check for contrary authority outside the provided petition.
- Citation search for *State v. Young*, 502 P.3d 45, and retrieval of opinion record 5123789. The Hawaii Intermediate Court of Appeals upheld a materially similar continuous-sexual-assault statute under *Ramos* and collected consistent Arizona, Wisconsin, and Texas authority.

No general web searches were used. I did not search for or consult this case's disposition or subsequent history.
