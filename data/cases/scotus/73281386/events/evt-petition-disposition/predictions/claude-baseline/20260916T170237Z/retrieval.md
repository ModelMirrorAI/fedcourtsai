# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "542 U.S. 367" --limit 3`
   `ranged corpus reads: 1357 GET(s), 355532800 byte(s)`
   No rows. CLI note: citations filter covers 200 of 590880 scotus rows; empty result is a coverage gap, not a non-match.
2. `uv run fedcourts query --court scotus --citation "583 U.S. 29" --limit 3`
   `ranged corpus reads: 1352 GET(s), 354222080 byte(s)`
   No rows; same coverage note.
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   Eight recent granted rows (election-law and Second Amendment petitions, several substantive applications). None analogous to this case; not used beyond confirming the CLI worked.

## CourtListener MCP (forward mode)

4. `get_endpoint_item dockets 73281386` (fields: id, case_name, docket_number, court_id, date_filed, date_terminated, date_last_filing, date_modified). Result: docket 25-1103, filed 2026-03-20, `date_terminated: null`, `date_modified` 2026-07-08. Consistent with the provisioned snapshot; no later activity.
5. `search type=d court=dcd q="Citizens for Responsibility and Ethics" "DOGE"` (5 results). Located the underlying district-court docket 1:25-cv-00511 (CourtListener docket 69658871), not terminated.
6. `call_endpoint docket-entries docket=69658871 date_filed__gte=2025-12-01` (15 results requested). Zero entries returned; read as thin RECAP coverage plus the stay, not as evidence about the case.

## Base rates

`metrics/statpack.md` (committed): "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (`cadc` row), "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (baseline and federal columns, OT2017-OT2024 pooled).

No web searches. Nothing under `data/qp-topics/` was read.
