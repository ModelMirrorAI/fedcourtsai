# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-09-17.json`, `record/context.json`, `record/documents/*`) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned recency-ranked substantive applications and 2025-Term cert dockets (Missouri redistricting, NRCC v. Brown, National Park Service, Trump v. California, Jouppi v. Alaska, Viramontes, Grant v. Higgins, Grand v. University Heights); nothing on juror bias or state habeas. Not used beyond confirming the corpus service was reachable.
2. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Same character of results (applications and recent denials); not used.

## CourtListener MCP lookups

3. `get_endpoint_item` dockets/73500216 — confirmed docket 25-1316, filed 2026-05-28, `date_terminated` null.
4. `call_endpoint` docket-entries for docket 73500216 — 0 entries in CourtListener.
5. `search` type=o, court=scotus, q=`"implied bias" juror`, filed after 2015-01-01 — 0 results (no recent SCOTUS opinion on the doctrine surfaced).

## Web

6. Fetched `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1316.html` (forward mode; this case's own docket). Four entries, identical to the snapshot: extension application (Apr 1), petition filed with response due June 29 (Apr 1), extension granted (Apr 8), distributed for the 9/28/2026 conference (Jul 15). No waiver, no brief in opposition, no response requested, no respondent counsel listed. Nothing outcome-revealing: the conference postdates today.

No `data/qp-topics/` paths were read.
