# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-15.json`, `record/context.json`,
`record/documents/{documents.json,questions-presented.txt,petition.txt,brief-in-opposition.txt}`,
`events/evt-petition-disposition/event.yaml`. Committed base rates: `metrics/statpack.md`
(modern discretionary-cert disposition, originating-circuit, relist-count, CVSG, capital-case
and salience-band cuts, the per-Term table, and the sal-v4 segment table).

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "600 U.S. 122"`
   stderr: `ranged corpus reads: 1357 GET(s), 355532800 byte(s)`
   Result: no rows; printed `note: citations filter: 200 of 590880 rows in scope (scotus)
   carry citation data ...` (a coverage gap, not "no such case").
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   Result: ~20 recently granted SCOTUS rows (applications and petitions), none on personal
   jurisdiction or the Commerce Clause; used only as a sanity read of the granted population.

## CourtListener MCP lookups

3. `search` (type `o`, court `scotus`, citation `600 U.S. 122`) → Mallory v. Norfolk Southern
   R. Co., cluster 9410341, opinion id 9405817 (slip opinion).
4. `search_document` (opinion 9405817, query "Commerce Clause") → footnote 3 of the opinion of
   the Court ("remains for consideration on remand") and the Alito concurrence passages
   ("good prospect ... violates the Commerce Clause"; "Norfolk Southern appears to have
   asserted a Commerce Clause claim below").

## Web fetches (forward mode; this case's own filings and a sibling docket)

5. `curl` of the petitioner's reply brief (docket entry Jul 14 2026),
   https://www.supremecourt.gov/DocketPDF/25/25-1208/416427/20260714114135771_Final%20-%20NS%20Mallory%20-%20Cert%20Reply.pdf,
   text extracted locally with pypdf (12 pages). Used for the waiver, finality, and Denver v.
   Terte rebuttals.
6. WebFetch of https://www.supremecourt.gov/docket/docketfiles/html/public/25-1046.html
   (BNSF Railway v. Lynn / Lynn v. BNSF, cited in both the petition and the BIO): petition
   filed Mar 2 2026, three amici, distributed Apr 15 for the 5/1/2026 conference, denied
   May 4 2026; no call for a response and no writing shown.

No search touched this petition's disposition; the petition is on the 9/28/2026 conference
list and undecided as of this run. Nothing under `data/qp-topics/` was read.
