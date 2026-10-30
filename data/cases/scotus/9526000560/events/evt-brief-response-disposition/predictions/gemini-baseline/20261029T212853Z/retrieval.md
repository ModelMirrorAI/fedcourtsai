# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. **Command:**
   ```bash
   uv run fedcourts query --court scotus --docket-number 26A124 --limit 5 && uv run fedcourts query --court scotus --docket-number 26A308 --limit 5 && uv run fedcourts query --court scotus --docket-number 26A203 --limit 5
   ```
   - **Transfer stderr lines:**
     - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Result:** Returned corpus records for three OT2026 Solicitor General stay applications cited in the briefs: *Trump v. California* (`26A124`, `disposition: "granted"`, `referred_to_court: true`, `response_requested: true`), *Department of Homeland Security v. League of Women Voters* (`26A308`, `disposition: "granted"`, `referred_to_court: true`, `response_requested: true`), and *National Park Service v. National Trust for Historic Preservation* (`26A203`, `disposition: "granted"`, `referred_to_court: true`, `response_requested: true`).

2. **Command:**
   ```bash
   uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15
   ```
   - **Transfer stderr line:**
     - `ranged corpus reads: 19 GET(s), 4915200 byte(s)`
   - **Result:** Returned 15 recent granted SCOTUS cases and applications in the 2020s era, including *Scanlan v. Coalition for Open Democracy* (`26A512`, `granted`), *FCC v. Brown* (`26A476`, `granted`), *Nelsen v. Pike* (`26A428`, `granted`), *DHS v. D.V.D.* (`26A406`, `granted`), *DHS v. League of Women Voters* (`26A308`, `granted`), and *People Not Politicians v. Onder* (`26A388`, `granted`).

3. **Command:**
   ```bash
   uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 15
   ```
   - **Transfer stderr line:**
     - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Result:** Returned 15 recent denied SCOTUS cases and applications in the 2020s era, including *Louisiana v. Devon Energy Production Co.* (`26A499`, `denied`), *Trump v. Kingdom* (`26A416`, `denied`), and several unreferred private applications (`26A535`, `26A532`, `26A555`, `26A556`, `26A545`, `26A524`, `26A530`, `26A536`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Center for Biological Diversity v. McAleenan"`, `num_results=5`): Returned 0 matches under exact case name filter.
2. `mcp_courtlistener_search` (`type="o"`, `case_name="In re Border Infrastructure Environmental Litigation"`, `num_results=5`): Returned 0 matches under exact case name filter.
3. `mcp_courtlistener_search` (`type="o"`, `q=""404 F. Supp. 3d 218" OR "915 F.3d 1213" OR "511 U.S. 462""`, `num_results=5`): Returned 227 matches, including *Border Infrastructure Envtl. Litig. v. U.S. Dep't of Homeland Sec.*, 915 F.3d 1213 (`cluster_id: 9022988`), *Center for Biological Diversity v. Burgum* (`cluster_id: 10948560`, D. Ariz. Aug. 4, 2026), *North American Butterfly Ass'n v. Wolf*, 977 F.3d 1244 (`cluster_id: 4407512`), and *Center for Biological Diversity v. McAleenan* (`cluster_id: 4448302`).
4. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 10948560}`): Returned `opinion_id: 11416147`.
5. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 9022988}`): Returned `opinion_id: 9016225` (McKeown majority) and `9016226` (Callahan dissent).
6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Learning Resources v. Trump"`, `num_results=5`): Returned *Learning Resources, Inc. v. Trump* (`cluster_id: 10799354`, decided Feb. 20, 2026).
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2026-08-01"`, `num_results=15`): Returned 6 recent OT2026 SCOTUS opinions on emergency applications: *FCC v. Brown* (`cluster_id: 11034117`, Oct. 14, 2026), *DHS v. League of Women Voters* (`cluster_id: 10983722`, Sept. 25, 2026), *People Not Politicians v. Onder* (`cluster_id: 10983725`, Sept. 25, 2026), *Noem v. Vasquez Perdomo* (`cluster_id: 10968087`, Sept. 8, 2026), *National Park Service v. National Trust for Historic Preservation* (`cluster_id: 10963060`, Aug. 31, 2026), and *Trump v. California* (`cluster_id: 10956828`, Aug. 24, 2026).
8. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 10963060}`): Returned `opinion_id: 11430669` (*National Park Service v. National Trust*).
9. `mcp_courtlistener_read_document` (`opinion_id=11416147`, `chunk_index=0`): Read chunk 0 of *Center for Biological Diversity v. Burgum* (D. Ariz. Aug. 4, 2026) regarding the Tucson 5 border-wall project on the Tohono O'odham Nation Reservation.
10. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 10799354}`): Returned `opinion_id: 11266028` (*Learning Resources, Inc. v. Trump*).
11. `mcp_courtlistener_read_document` (`opinion_id=11430669`, `chunk_index=0`, `1`, `2`): Read the *per curiam* opinion and Justice Jackson's dissent in *National Park Service v. National Trust for Historic Preservation* (26A203, Aug. 31, 2026).
12. `mcp_courtlistener_search_document` (`opinion_id=11266028`, `query="major questions"`): Searched *Learning Resources, Inc. v. Trump* for its discussion of the major questions doctrine.
13. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 10983722}`): Returned `opinion_id: 11451385` (*DHS v. League of Women Voters*).
14. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 10956828}`): Returned `opinion_id: 11424433` (*Trump v. California*).
15. `mcp_courtlistener_read_document` (`opinion_id=11451385`, `chunk_index=0`, `1`): Read Justice Sotomayor's dissent from the grant of stay in *DHS v. League of Women Voters* (26A308, Sept. 25, 2026).
16. `mcp_courtlistener_read_document` (`opinion_id=11424433`, `chunk_index=0`): First call returned a transient upstream 500 error; retry succeeded and returned chunk 0 of *Trump v. California* (26A124).
17. `mcp_courtlistener_read_document` (`opinion_id=9016225`, `chunk_index=0`, `[1,2]`, `[3,4]`, `[5,6]`): Read the Ninth Circuit's opinion in *In re Border Infrastructure Environmental Litigation*, 915 F.3d 1213 (9th Cir. 2019), analyzing IIRIRA § 102(a), § 102(b), and § 102(c).
18. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 11034117}`): Returned `opinion_id: 11501811` (*FCC v. Brown*).
19. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Donald J. Trump v. Alishea Sophia Kingdom"`): Returned 0 opinion matches (order without separate opinion).
20. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Scanlan v. Coalition for Open Democracy"`): Returned 0 opinion matches (order without separate opinion).
21. `mcp_courtlistener_read_document` (`opinion_id=11501811`, `chunk_index=0`, `1`): Read the *per curiam* stay order in *FCC v. Brown* (26A476, Oct. 14, 2026).
22. `mcp_courtlistener_read_document` (`opinion_id=11416147`, `chunk_index=[1,2,3]`): Read chunks 1–3 of *Center for Biological Diversity v. Burgum* (D. Ariz. Aug. 4, 2026).
23. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 4407512}`): Returned `opinion_id: 4184765` (unrelated Third Circuit case that cited 915 F.3d 1213).
24. `mcp_courtlistener_read_document` (`opinion_id=4184765`, `chunk_index=[0,1]`): Confirmed `4184765` was an unrelated bankruptcy case.
25. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 4448302}`): Returned `opinion_id: 4225555`.
26. `mcp_courtlistener_read_document` (`opinion_id=4225555`, `chunk_index=[0,1]`): Confirmed `4225555` was an unrelated state case.
27. `mcp_courtlistener_search` (`type="o"`, `citation="404 F. Supp. 3d 218"`): Returned 0 matches under reporter citation filter.
28. `mcp_courtlistener_search` (`type="o"`, `q=""McAleenan" AND "IIRIRA" AND "102(c)""`, `num_results=5`): Returned 12 matches, including *Center for Biological Diversity v. Trump*, 453 F. Supp. 3d 11 (`cluster_id: 4795622`, D.D.C. 2020) and *North American Butterfly Ass'n v. Wolf*, 977 F.3d 1244 (`cluster_id: 4862141`, D.C. Cir. 2020).
29. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 4795622}`): Returned `opinion_id: 4575969` (*Center for Biological Diversity v. Trump*, 453 F. Supp. 3d 11).
30. `mcp_courtlistener_read_document` (`opinion_id=4575969`, `chunk_index=[0,1]`, `[2,3]`, `[6,7]`, `[8,9]`, `[10,11]`): Read Judge Trevor McFadden's opinion in *Center for Biological Diversity v. Trump*, 453 F. Supp. 3d 11 (D.D.C. 2020), analyzing IIRIRA § 102(a), § 102(c)(1), § 102(c)(2)(A), *Dalton v. Specter*, and *Center for Biological Diversity v. McAleenan*, 404 F. Supp. 3d 218 (D.D.C. 2019).
31. `mcp_courtlistener_search` (`type="r"`, `case_name="Friends of the Ruidosa Church v. Mullin"`, `num_results=5`): Returned W.D. Tex. RECAP docket `3:26-cv-01099` (*Friends of the Ruidosa Church v. Mullin et al.*).
32. `mcp_courtlistener_search` (`type="o"`, `case_name="Friends of the Ruidosa Church v. Mullin"`, `num_results=5`): Returned 0 published opinions in the opinion index.
33. `mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, `query={"court": "txwd", "docket_number": "3:26-cv-01099"}`): Returned `docket_id: 73199706`.
34. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 73199706, "order_by": "-entry_number"}`, `num_results=30`): Returned docket entries for `3:26-cv-01099`, including ECF No. 65 (Oct. 2, 2026 Order Granting Motion for Preliminary Injunction), ECF No. 72 (Oct. 14, 2026 Memorandum Opinion), and ECF No. 78 (Oct. 20, 2026 Order Denying Motion to Stay Preliminary Injunction).
35. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 73199706, "date_filed__gte": "2026-10-01"}`) and `mcp_courtlistener_read_document` (`recap_document_id=497310911`, `498070832`): Returned HTTP 429 (`Rate limit exceeded: 1400/day`). Proceeded on the provisioned `application.txt` and `application-response.txt` filings and the opinions already retrieved.
