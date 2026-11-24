# Retrieval Log

Beyond the provisioned case record under `data/cases/scotus/9026000572/` and the repository's committed `metrics/statpack.md` / `metrics/statpack.json` and `data/schedule/schedule.json`, I performed the following corpus and CourtListener MCP lookups (no web searches were performed, and no lookups targeted the disposition or external forecasts of `scotus/9026000572`):

## 1. Corpus CLI (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-104`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned lead case `scotus/9026000104` (*Philip L. Rhoney, Acting Director of the Buffalo Field Office of U.S. Immigration and Customs Enforcement v. Ricardo Aparecido Barbosa da Cunha*, No. 26-104, from CA2 No. 25-3141), confirming `disposition: "granted"`, `date_cert_granted: "2026-10-01"`, `distributed_for_conference: "2026-09-28"`, `distribution_count: 1`.
2. `uv run fedcourts query --court scotus --docket-number 25-1415`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned companion government petition `scotus/73529868` (*Matthew Putra, Director of the Detroit Field Office of U.S. Immigration and Customs Enforcement v. Juan Manuel Lopez-Campos*, No. 25-1415, from CA6), open (`disposition: null`), distributed once for the `2026-09-28` conference (held pending No. 26-104).
3. `uv run fedcourts query --court scotus --docket-number 26-43`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned cross-split private petition `scotus/9026000043` (*Victor Buenrostro-Mendez, et al. v. Todd Blanche, Attorney General, et al.*, No. 26-43, from CA5), open (`disposition: null`), distributed once for the `2026-09-28` conference (held pending No. 26-104).
4. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - Transfer: `ranged corpus reads: 29 GET(s), 7471104 byte(s)`
   - Result: Returned 5 recent OT2026 GVR rows (`25-1421`, `26-5528`, `25-442`, `25-1348`, `26-5123`) illustrating distribution counts (`1`–`3`) and `gvr` disposition coding.
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 5 recent OT2026 `granted` rows (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`).

## 2. CourtListener MCP Server

1. `mcp_courtlistener_search(type="o", q='"1225(b)(2)(A)" "applicant for admission"', filed_after="2026-01-01", order_by="dateFiled desc", num_results=20, fields=["caseName", "court_id", "dateFiled", "citation", "docketNumber", "judge", "cluster_id"])`
   - Result: Returned 20 circuit-level opinions (`count: 20`, `query_id: "e1c54c49"`), mapping the 2026 circuit split across CA1 (*Guerrero Orellana*), CA2 (*Barbosa Da Cunha*, cluster `10983473`), CA3 (*Buele Morocho*), CA4 (*Rivera*, *Lopez Garcia*), CA5 (*Sosnava Rodriguez*), CA6 (*Sanchez Alvarez*), CA7 (*Cirrus Rojas*, *Castanon Nava*), CA8 (*Avila*), and CA9 (*Rodriguez Vazquez*).
2. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10983473, fields=["id", "case_name", "date_filed", "judges", "sub_opinions", "docket_id"])`
   - Result: Returned cluster metadata for *Barbosa Da Cunha v. Freden* (`docket_id: 72281778`, `date_filed: "2026-09-25"`, `sub_opinions: [".../opinions/11451136/"]`).
3. `mcp_courtlistener_read_document(opinion_id=11451136, chunk_index=0, chunk_size=8000)`
   - Result: Returned `{"doc_type": "opinion", "doc_id": 11451136, "error": "No text is available for this document."}`. (Proceeded using the detailed discussion of *Barbosa da Cunha*, 175 F.4th 61 (2d Cir. 2026), in the provisioned Seventh Circuit opinion and SG petition.)
4. `mcp_courtlistener_search(type="o", q='"Buenrostro-Mendez"', filed_after="2026-01-01", num_results=10, fields=["caseName", "court_id", "dateFiled", "docketNumber", "judge", "cluster_id"])`
   - Result: Returned 10 opinions citing *Buenrostro-Mendez* (`count: 20`, `query_id: "dec0c55c"`), confirming the cross-circuit alignment (`Avila` CA8, `Castanon Nava` CA7, `Sosnava Rodriguez` CA5, `Rodriguez Vazquez` CA9, `Guerrero Orellana` CA1, `Rojas` CA7).
