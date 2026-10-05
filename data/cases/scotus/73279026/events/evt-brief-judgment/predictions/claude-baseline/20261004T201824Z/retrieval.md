# Retrieval log

Mode: `forward` (retrieval unrestricted; nothing about this case's disposition exists yet, and none was sought or seen).

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "593 U.S. 522" --citation "596 U.S. 767" --citation "591 U.S. 464" --citation "582 U.S. 449" --citation "597 U.S. 507"` (an attempt to pull Fulton, Carson, Espinoza, Trinity Lutheran and Kennedy as resolved priors)
   - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - stderr note: the citation column is populated on only 200 SCOTUS rows; no rows returned. Not retried.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted` (looking for recent granted dockets carrying a merits judgment)
   - stderr: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   - Returned recency-ranked Term-2025/2026 cert and application dockets, all with `merits_judgment: None`; not useful as merits priors. No further corpus queries.

## CourtListener MCP lookups

3. `search` type `o`, court `ca10`, q `"St. Mary Catholic Parish" Roy preschool` — 0 results.
4. `search` type `o`, case_name `St. Mary Catholic Parish v. Roy` — 0 results.
5. `search` type `o`, court `ca10`, q `"universal preschool" "equal opportunity" Catholic "Free Exercise"`, filed after 2025-06-01 — 0 results.

The Tenth Circuit opinion was not retrievable through the MCP server under these queries; the lower-court reasoning was taken from the two provisioned merits briefs instead.

## Web searches

None.

## Base rates

`metrics/statpack.md`, section "The merits docket (granted cases)": grant Terms 2017–2024 pooled (the strictly-prior window for a Term-2025 grant that the table renders), 360 disturbed of 516 parsed, 69.8%.
