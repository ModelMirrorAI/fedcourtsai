# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "600 U.S. 447" --limit 3`
   `ranged corpus reads: 10 GET(s), 2555904 byte(s)`
   Returned no rows; the CLI printed a `note:` that the citation column is sparsely populated on SCOTUS rows.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   Returned eight recent granted SCOTUS rows (mostly emergency applications and unrelated cert grants); none topically similar, not used for the number.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (anchored on the `elevated` bracketed `reached` rate pooled over Terms 2017 to 2024).

## CourtListener MCP

1. `search` type `d`, court `scotus`, q `"undue hardship" Groff "Title VII"`, filed after 2025-01-01: 0 results.
2. `search` type `o`, court `ca9`, q `Petersen "Snohomish Regional Fire"`: found the published Ninth Circuit opinion (cluster 10664661, filed 2025-09-02) and *Williams v. Legacy Health* (2026-05-06).
3. `get_endpoint_item` `clusters` 10664661: confirmed `precedential_status: Published`; judges field empty.
4. `search` type `d`, court `scotus`, q for Rodrique / Kluge / Brownsburg / Southern Ohio Medical / Atlantic City / Muscatine, filed after 2025-01-01: 0 results (RECAP's SCOTUS docket coverage is thin; could not confirm companion petitions).
5. `search` type `o`, circuits ca1 to cadc, q on post-Groff undue-hardship opinions filed after 2025-09-02: 0 results.
6. `search` type `o`, court `ca9`, q `"Williams v. Legacy Health"`: surfaced three published Ninth Circuit religious-accommodation opinions from 2026 (*Williams v. Legacy Health*, *Brown v. Alaska Airlines*, *Lewis-Williams v. BART*); titles only, not read.
7. `search` type `o`, court `ca9`, q `Petersen "Snohomish Regional Fire"` with panel fields: panel names not populated.
8. `search` type `o`, court `ca9`, q `"Petersen" "undue hardship" "Title VII" vaccin`, filed after 2025-09-03: two follow-on Ninth Circuit opinions (titles only).

No web searches. Nothing retrieved disclosed this petition's disposition.
