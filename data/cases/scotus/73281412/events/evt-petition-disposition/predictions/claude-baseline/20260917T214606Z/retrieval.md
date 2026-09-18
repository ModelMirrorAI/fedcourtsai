# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`, `documents/questions-presented.txt`, `documents/petition.txt`, `documents/brief-in-opposition.txt`, `documents/documents.json`, the event definition) and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts paths --court scotus --docket 73281412 --event evt-petition-disposition --role predictor` (path resolution only).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned eight recent granted SCOTUS matters (mostly substantive applications and Second Amendment petitions) ranked by recency; none doctrinally similar to this petition. Not used in the number.

## CourtListener MCP lookups

1. `search` type `d`, court `scotus`, docket_number `25-1128` — 0 results.
2. `search` type `o`, court `ca5`, case_name `Alexander v. Taft` — two published clusters, No. 24-10663, filed 2025-07-10 and 2025-12-23, citeCount 0 each.
3. `call_endpoint` `dockets`, court `scotus`, docket_number `25-1128` — one docket, id 73281412, date_filed 2026-03-26, date_terminated null.
4. `call_endpoint` `docket-entries`, docket 73281412 — 0 entries (CourtListener carries no entry text for this SCOTUS docket).

## Web searches

None.
