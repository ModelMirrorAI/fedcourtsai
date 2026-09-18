# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`, `documents/questions-presented.txt`, `documents/petition.txt`, `documents/brief-in-opposition.txt`, `documents.json`) and the committed `metrics/statpack.md` (modern-cert disposition, relist-count, CVSG, salience-band, per-Term, and sal-v4 segment-band sections), I consulted:

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "563 U.S. 983" --citation "583 U.S. 1052" --citation "541 U.S. 960" --citation "525 U.S. 1070" --citation "520 U.S. 1118"`
   - Purpose: known-case lookup of the cert denials the petition cites in earlier judicial-speech discipline cases (Siefert, Neely, Dunleavy, Broadman, Broadbelt).
   - Result: no rows; the tool printed a `note:` that only 200 of 590,940 in-scope rows carry citation data (a coverage gap, not "no such case").
   - stderr: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   - Purpose: a look at recent granted SCOTUS priors for shape; none were topically comparable (no text filter exists), so nothing from this query moved the forecast.
   - stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`

## CourtListener MCP

3. `call_endpoint dockets` for docket id 73281699 (fields: id, case_name, docket_number, date_filed, date_terminated, date_modified). Result: No. 25-1215, filed 2026-04-24, `date_terminated` null, last modified 2026-08-03. Confirms the docket has not moved past the provisioned snapshot and the petition is undecided.
4. `call_endpoint docket-entries` for docket 73281699. Result: 0 entries indexed (RECAP holds no entry rows for this SCOTUS docket).
5. `search` (type `d`, court `scotus`, filed after 2015-01-01) for judicial-conduct / judicial-discipline First Amendment dockets. Result: 0 hits.

No web searches. No material postdating the snapshot was found, and nothing outcome-revealing surfaced.
