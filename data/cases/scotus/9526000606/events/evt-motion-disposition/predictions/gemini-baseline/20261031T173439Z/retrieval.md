# Retrieval Log

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000606" --event "evt-motion-disposition" --role predictor`
   - Resolved `case_id` (`scotus/9526000606`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Inspected available structured filters for corpus queries.
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Returned 10 resolved 2020s SCOTUS priors, including recent OT2026 substantive applications (`26A499`, `26A535`, `26A532`, `26A512`, `26A555`, `26A556`, `26A416`).
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   - Returned 10 resolved 2020s SCOTUS granted priors (`26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`).
5. `uv run fedcourts query --court ca3 --era 2020s --limit 5`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 5 resolved 2020s Third Circuit rows (`ca3/73565864`, `ca3/70915819`, `ca3/72291266`, `ca3/71870978`, `ca3/73472106`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca3", docket_number="25-2933", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id", "absolute_url"])`
   - Returned 0 results (search index did not match `docket_number="25-2933"` with `court="ca3"`).
2. `mcp_courtlistener_search(type="r", court="ca3", docket_number="25-2933", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id", "absolute_url"])`
   - Returned 0 results.
3. `mcp_courtlistener_search(type="o", case_name="Gina Silva", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id", "absolute_url"])`
   - Returned 1 unrelated 2001 MDL opinion (`00-4109`).
4. `mcp_courtlistener_search(type="d", case_name="Gina Silva", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id", "absolute_url"])`
   - Returned 15 unrelated bankruptcy dockets.
5. `mcp_courtlistener_search(type="o", docket_number="25-2933", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id", "absolute_url"])`
   - Returned 0 results.
6. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "ca3", "docket_number": "25-2933", "fields": ["id", "case_name", "docket_number", "date_filed", "date_terminated"]})`
   - Returned Third Circuit docket `id: 73588758`, *Gina Silva v. Attorney General United States of America*, `docket_number: "25-2933"`.
7. `mcp_courtlistener_search(type="r", court="njd", party_name="Gina Silva")`
   - Returned 2 unrelated District of New Jersey MDL dockets (`2:17-md-02789`).
8. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=73588758)`
   - Retrieved full docket metadata for CA3 No. 25-2933 (`id: 73588758`, `appeal_from_str: "Agency"`, linked cluster `10918957`).
9. `mcp_courtlistener_call_endpoint(endpoint_id="clusters", query={"docket": 73588758, "fields": ["id", "case_name", "date_filed", "judges", "sub_opinions", "precedential_status", "disposition", "nature_of_suit"]})`
   - Returned cluster `id: 10918957`, *Gina Silva v. Attorney General United States of America*, `date_filed: "2026-07-08"`, `precedential_status: "Unpublished"`, `sub_opinions: [".../opinions/11386492/"]`.
10. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 73588758, "fields": ["id", "date_filed", "entry_number", "description"]})`
    - Returned 0 docket entries (opinion-ingested appellate docket).
11. `mcp_courtlistener_read_document(opinion_id=11386492)`
    - Retrieved the full text (9,725 chars) of the Third Circuit's July 8, 2026 non-precedential per curiam opinion in *Gina Paola Silva; Gustavo Alfonso Medina Acosta; M.M.S. v. Attorney General United States of America*, No. 25-2933 (Agency Nos. A240-844-470, A240-844-471, A240-844-472), denying the petition for review.

## 3. Web Searches

None.
