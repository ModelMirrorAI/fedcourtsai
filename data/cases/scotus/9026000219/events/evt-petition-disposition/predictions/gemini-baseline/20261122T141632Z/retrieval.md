# Retrieval Log

## Corpus Lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "468 U.S. 897" --limit 10`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty result with coverage note explaining that `--citation` matches a row's own parallel reporter citations (populated on 195 SCOTUS rows) rather than a cases-citing-authority graph.

2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9830400 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS certiorari petitions and interim applications (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`), confirming typical distribution counts, counsel profiles, and salience characteristics of granted OT2026 cases.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", q=""Court of Appeals for the Armed Forces" OR "1259(3)"", filed_before="2026-08-01", num_results=10, fields=["caseName", "dateFiled", "citation", "docketNumber", "snippet"])`
   - Result: `count: 99` (`query_id: "f3a44baf"`, with a `missing_fields` warning noting `snippet` is not a field on opinion search results); returned 10 SCOTUS orders and decisions reviewing CAAF cases, including *United States v. Briggs*, 592 U.S. 69 (2020), *Ortiz v. United States*, *Dalmazzi v. United States*, *Cox v. United States*, and certiorari denials (*Voorhees*, *McDonald*, *Camacho*, *Richards*, *Abdirahman*, *Kelly*).

2. `mcp_courtlistener_search(type="o", court="scotus", q=""Court of Appeals for the Armed Forces"", stat_Published=true, filed_after="2018-01-01", filed_before="2026-08-01", num_results=15, fields=["caseName", "dateFiled", "citation", "docketNumber"])`
   - Result: `count: 29` (`query_id: "f91b9959"`); returned 15 published SCOTUS entries from 2018–2026 referencing CAAF, confirming that merits grants since *Ortiz* (2018) were consolidated Solicitor General petitions (*United States v. Briggs* and *United States v. Collins*) while servicemember petitions (*Voorhees*, *Larrabee*, *McDonald*, *Hutchins*, *Cooper*, *Hale*, *King*, *Livingstone*) were denied.

## Web Searches

- None attempted.
