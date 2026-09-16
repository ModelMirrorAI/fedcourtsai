# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  Returned five recent denied SCOTUS rows (mostly substantive applications, not cert petitions comparable to this one); used only to confirm the query surface worked. No prior from it shaped the forecast.
- An earlier invocation with a free-text argument was rejected by the CLI (it takes structured filters only) and read nothing.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (ca7 row), "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (the `baseline` column, Terms 2017 to 2024, bracketed `reached` figures).

## CourtListener MCP

1. `search` type=o, q="Watson v. Mlodzik", court=ca7, filed_after=2025-01-01: 0 results (the Seventh Circuit COA denial is not in the opinion index).
2. `search` type=d, docket_number=25-1279, court=scotus: 0 results.
3. `get_endpoint_item` dockets/73335108: returned the docket record (case name Henry L. Watson, III v. Kenya Mason, Warden; docket 25-1279; date_filed 2026-05-13; date_terminated null; date_modified 2026-06-17). Confirms the docket is open and unchanged since the snapshot's generation date.
4. `call_endpoint` docket-entries, docket=73335108: 0 results.

## Web searches

None.
