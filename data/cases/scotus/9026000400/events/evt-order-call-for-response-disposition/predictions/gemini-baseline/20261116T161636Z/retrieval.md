# Retrieval Log — `scotus/9026000400` (`evt-order-call-for-response-disposition`)

All external lookups beyond the provisioned case inputs (`data/cases/scotus/9026000400/record/`, `event.yaml`, `metrics/statpack.md`, and `schemas/`) are logged below. No queries were made for this case's own Supreme Court disposition or for any third-party or project forecasts.

## 1. `fedcourts` CLI Lookups

1. **Path resolution and query CLI help**
   - Command: `uv run fedcourts paths --court "scotus" --docket "9026000400" --event "evt-order-call-for-response-disposition" --role predictor && uv run fedcourts query --help`
   - Corpus reads: none (`paths` and `--help` metadata only).
   - Returned: Canonical cell `case_id`, `corpus`, and `event` paths, plus available `fedcourts query` filter options.

2. **Recent 2020s SCOTUS granted cases (priors and OT2026 merits docket check)**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 40 GET(s), 10420224 byte(s)`
   - Returned: 10 recent OT2026 granted SCOTUS dockets (7 cert grants including `25-944` *Robinhood Markets v. Sodha*, `26-239` *Mullin v. RAICES*, `25-1408` *Goldman Sachs Bank USA v. Brown*, `26-12` *Association for Education Fairness v. Montgomery County Board of Education*, `26-204` *Department of Justice v. McNutt*, `25-1103` *U.S. DOGE Service v. U.S. District Court*, and `25-7026` *Berry v. United States*, plus 3 interim applications). Used as calibration priors and to verify whether any recent OT2026 business grant involved Rule 23 class certification.

3. **Citation lookup test in corpus for *Labcorp v. Davis***
   - Command: `uv run fedcourts query --court scotus --citation "605 U.S. 327"`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned: 0 rows, with CLI note explaining that only 195 `scotus` rows carry reporter parallel citations in that column and advising CourtListener MCP for known-citation lookups.

4. **Recent 2020s SCOTUS denied cert petitions (priors)**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 10 recent OT2026 denied SCOTUS cert petitions (`25-1238`, `25-1240`, `25-1303`, `25-1324`, `25-7485`, `25-7562`, `26-4`, `26-62`, `26-100`, `26-120`), illustrating routine denials among paid petitions carrying multiple distributions and multiple amicus briefs.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Laboratory Corp. v. Davis", fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions", "docketNumber"])`
   - Returned: 2 clusters (`10776843` and `10599006`) for *Laboratory Corp. of America Holdings v. Davis*, 605 U.S. 327 (June 5, 2025), No. 24-304 (`opinion_id=11243430`).

2. `mcp_courtlistener_read_document(opinion_id=11243430)`
   - Returned: Full text (20,185 chars) of *Laboratory Corp. of America Holdings v. Davis*, 605 U.S. 327 (2025) — per curiam dismissal of writ as improvidently granted (8–1), with Justice Kavanaugh dissenting alone on the Rule 23(b)(3) uninjured-class-members issue and detailing the superseding class-certification order procedural snag.

3. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-06-06", q='"Olean Wholesale" OR "uninjured class members" OR "Davidson v. Kimberly-Clark" OR "Comcast Corp. v. Behrend"', fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id"])`
   - Returned: 1 result — *Mirabelli v. Bonta*, No. 25A810 (`cluster_id=10802600`, filed 2026-03-02). Confirmed no SCOTUS merits opinion since *Labcorp* has resolved *Olean*, *Davidson*, or *Comcast*.

4. `mcp_courtlistener_search(type="o", court=["ca1","ca2","ca3","ca4","ca5","ca6","ca7","ca8","ca9","ca10","ca11","cadc"], filed_after="2025-06-06", q='"Laboratory Corp. of America Holdings v. Davis" OR "605 U.S. 327"', num_results=15, fields=["caseName", "court_id", "citation", "dateFiled", "docketNumber"])`
   - Returned: 0 exact-phrase matches under that string spelling.

5. `mcp_courtlistener_search(type="o", court="scotus", q='"Speerly" OR "Nutramax" OR "Noohi" OR "DZ Reserve" OR "Spurlock" OR "Rosenwald"', fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Returned: 47 historical/unrelated surname hits (e.g., *Toll Bros., Inc. v. Noohi*, 570 U.S. 946 (2013)); confirmed no recent SCOTUS opinion or Separate writing on the 2024–2026 class-action circuit decisions cited in the petition.

6. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10802600, fields=["id", "case_name", "date_filed", "docket_id", "sub_opinions"])` and `mcp_courtlistener_search_document(opinion_id=11269328, query="Rule 23")`
   - Returned: Cluster metadata and 1 snippet from *Mirabelli v. Bonta* (`opinion_id=11269328`), an emergency application vacating a stay as to parent plaintiffs; unrelated to the consumer class-action questions here.

7. `mcp_courtlistener_search(type="o", court="ca9", q='"Falcone" "Nestle"', fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id"])`
   - Returned: 0 results (consistent with the Ninth Circuit's decision in `24-7707` being an unpublished memorandum reproduced in full in `record/documents/appendix.txt`).

8. `mcp_courtlistener_search(type="o", court=["ca4", "ca6"], filed_after="2025-01-01", q='"Speerly" OR "Spurlock" OR "Boeing"', fields=["caseName", "court_id", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Returned: 11 opinions, including en banc *Dennis Speerly v. General Motors, LLC*, 143 F.4th 306 (6th Cir. June 27, 2025) (`cluster_id=10618994`), and subsequent Sixth Circuit Rule 23 decisions applying *Speerly*.

9. `mcp_courtlistener_search(type="o", court=["ca4", "ca9"], q='"Sodha" OR "Marcus by Goldman Sachs" OR "Wexford Health Sources" OR "General Treasurer"', fields=["caseName", "court_id", "citation", "dateFiled", "docketNumber", "cluster_id"])`
   - Returned: 10 opinions, including *Sodha v. Golubowski*, No. 24-1036 (9th Cir. Aug. 29, 2025) (`cluster_id=10663157`), the Ninth Circuit decision underlying newly granted SCOTUS No. 25-944 (*Robinhood Markets v. Sodha*).

10. `mcp_courtlistener_search(type="o", court="ca4", docket_number="25-1439", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "snippet"])`
    - Returned: 1 opinion — *Goldman Sachs Bank USA v. Rhea Brown*, No. 25-1439 (4th Cir. Mar. 18, 2026) (`cluster_id=10811292`), underlying newly granted SCOTUS No. 25-1408.

11. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10663157, fields=["id", "case_name", "date_filed", "sub_opinions"])`, `mcp_courtlistener_search_document(opinion_id=11129744, query="Rule 23")`, `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10811292, fields=["id", "case_name", "sub_opinions"])`, and `mcp_courtlistener_search_document(opinion_id=11278043, query="Rule 23")`
    - Returned: 0 matches for `"Rule 23"` in both *Sodha v. Golubowski* (`opinion_id=11129744`) and *Goldman Sachs Bank USA v. Rhea Brown* (`opinion_id=11278043`), confirming neither newly granted OT2026 business case involves Rule 23 class certification.

## 3. Web Searches
None.
