# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 27 GET(s), 6946816 byte(s)`
   Returned eight recently resolved OT2025/OT2026 grants (mostly federal-government petitions and emergency applications); no CVSG filter exists, so this informed shape only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Returned five October 5, 2026 denials with one or two distributions and no CVSG.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", and "Segment base rate by salience band (sal-v4)" pooled over OT2017 to OT2024 for the `high` band.

## CourtListener MCP (7 calls)

1. `search` type `d`, court `scotus`, case_name "Cantero Bank of America": 0 results.
2. `search` type `d`, court `scotus`, q "Cantero": 0 results.
3. `call_endpoint` `dockets`, court `scotus`, docket_number `25-1004`: one hit, Citizens Bank, N.A. v. John Conti (id 73281044, filed 2026-02-23).
4. `call_endpoint` `docket-entries`, docket 73281044: 0 results (SCOTUS dockets carry no entries on CourtListener).
5. `get_endpoint_item` `dockets` 73281044: not terminated; date_modified 2026-10-05.
6. `call_endpoint` `dockets` with a case_name__icontains filter for Cantero: rejected by the endpoint schema.
7. `call_endpoint` `dockets` with a case_name filter for Cantero: rejected by the endpoint schema.

No web searches. Nothing about this petition's own disposition was sought or seen.
