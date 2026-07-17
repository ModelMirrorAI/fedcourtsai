# Retrieval

## Corpus tooling

- Attempted `uv run fedcourts query --court scotus --citation 'United States v. Munsingwear, Inc., 340 U.S. 36 (1950)' --limit 10` (with the runner package cache redirected to `/tmp`). The ranged corpus remote could not be resolved, so the command returned no priors and printed no `ranged corpus reads` line.
- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”

## CourtListener MCP

- Opinion search in SCOTUS for `"Munsingwear" AND vacatur AND moot`, limited to filings before July 17, 2026. It returned 12 results, including *Acheson Hotels, LLC v. Laufer*, *Arizona v. City and County of San Francisco*, *Azar v. Garza*, *Camreta v. Greene*, *Alvarez v. Smith*, and *U.S. Bancorp Mortgage Co. v. Bonner Mall Partnership*.
- Opinion search in SCOTUS for `"vacated and remanded" AND "dismiss" AND "moot"`, limited to January 1, 2015 through July 16, 2026. It returned 11 results, including *Acheson Hotels*, *Department of Education v. Brown*, and *MOAC Mall Holdings LLC v. Transform Holdco LLC*.
- Opinion search for *Tennessee v. Kennedy*, limited to filings before July 17, 2026. It returned no result.
- Opinion search in SCOTUS for `"supervised release" AND "Munsingwear"`, limited to filings before July 17, 2026. It returned no result.
- Opinion search in SCOTUS for `"voluntary action" AND vacatur AND mootness`, limited to filings before July 17, 2026. It returned six results, including *Acheson Hotels*, *Azar v. Garza*, *Alvarez v. Smith*, and *U.S. Bancorp*.
- Attempted a focused opinion-item fetch using an identifier surfaced by search. The returned item was unrelated to the search result, so it was discarded and did not inform the prediction.

No web search was used. No lookup sought this petition's disposition or post-snapshot docket history.
