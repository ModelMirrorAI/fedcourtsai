# Retrieval beyond the provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the 2025 Term paid-fee-class detail in `metrics/statpack.json`.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
  - Initial concurrent attempt returned no rows and printed no transfer line.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 12`
  - `ranged corpus reads: 209 GET(s), 54788096 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
  - Retry: `ranged corpus reads: 150 GET(s), 39321600 byte(s)`

These structured queries had no keyword filter. I used their returned docket posture, distribution counts, CVSG status, and salience metadata only as broad structural priors, not as doctrinally similar cases.

## CourtListener MCP lookups

- Opinion search in SCOTUS for `"fair warning" due process judicial interpretation` (8 results). Relevant results included *Rogers v. Tennessee*, 532 U.S. 451 (2001), *Metrish v. Lancaster*, 569 U.S. 351 (2013), and *United States v. Lanier*, 520 U.S. 259 (1997).
- Opinion search in SCOTUS for `"unexpected and indefensible" judicial construction due process` (2 results): *Rogers v. Tennessee*, 532 U.S. 451 (2001), and *Bouie v. City of Columbia*, 378 U.S. 347 (1964).
- Opinion search in SCOTUS for `attorney discipline due process fair notice charges`; the MCP returned HTTP 429 throttling and no results.

No web search was used. I did not retrieve this case's disposition or subsequent history.
