# Retrieval log

## Corpus (read-only, via the cell's corpus service)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned recent granted rows (election-law stay applications and a few OT2025 cert grants); none topically similar to a Monell contracted-medical-care question. Used only as a sanity check on what the corpus holds; no prior shaped the number.

## CourtListener MCP

1. `search` (type `o`, court `ca4`, q `Swink "Southern Health Partners"`): one result, cluster 10740455, *Juliana Swink v. Southern Health Partners Incorporated*, No. 21-2183, filed 2025-11-20, status Published. Confirms the decision below is published.
2. `search` (type `d`, court `scotus`, docket_number `25-1091`): zero results in the RECAP docket index.
3. `get_endpoint_item` (`dockets`, id 73281376): docket 25-1091, `date_filed` 2026-03-17, `date_terminated` null, `date_modified` 2026-07-24. No filings or entries beyond the provisioned snapshot; the case is undecided.

## Web

No web searches.

## Statpack

`metrics/statpack.md`: modern discretionary-cert disposition table, originating-circuit cut (ca4), relist-count and CVSG cuts (paid scored segment), SCOTUS cert petitions by Term, and the sal-v4 segment base rate by salience band (Terms 2017-2024 pooled for the `elevated` bracketed `reached` figure).
