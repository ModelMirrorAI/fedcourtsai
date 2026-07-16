# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`. Relevant figures: Term 2025 cert grant rate 2.5%; no-CVSG grant rate 3.0%; relist buckets 0 = 0.8%, 1 = 7.6%, 2 = 33.6%, and 3+ = 21.8%. The snapshot showed a long unresolved hold after one distribution rather than recorded relists, so the relist buckets were treated as context rather than a direct match.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation '494 U.S. 872' --limit 10`
  - Result: failed before returning any priors because the remote S3 hostname could not be resolved (`EndpointConnectionError`).
  - Ranged-read line: none printed because the connection failed before any corpus read.

## CourtListener MCP lookups

- Opinions search for case name `St. Mary Catholic Parish v. Roy`, limited through 2026-07-16: 0 results.
- Opinions full-text search for `St. Mary Catholic Parish Roy preschool free exercise`, limited through 2026-07-16: 4 results, none the identified related petition.
- Opinions full-text search for `"overrule Smith" "Free Exercise"`, from 2020 through 2026-07-16: 17 results, including *Fulton* and several lower-court applications; no split bearing directly on this vehicle was identified.
- Opinions full-text search for `Roy government funding preschools Smith religious school`, from 2020 through 2026-07-16: 7 results, none the identified related petition.
- Opinions full-text search for `"St. Mary Catholic Parish" OR "Universal Preschool" religious`, from 2020 through 2026-07-16: overbroad (5,241 results) and not used substantively.
- Opinions full-text search for `"face coverings" "religious services" "Free Exercise Clause"`, from 2020 through 2026-07-16: 15 results. The leading results were the already disclosed earlier Calvary Chapel litigation, *South Bay*, *Elim Romanian Pentecostal Church*, and *Tandon*; no current-petition disposition appeared.

No web searches were used. No lookup sought this case's disposition.
