# Retrieval Log

## 1. Local Corpus CLI (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000098" --event "evt-petition-disposition" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`

*(Note: Exploratory invocations of `fedcourts query` with free-text/unsupported flags exited with usage help and performed 0 corpus reads.)*

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="r"`, `case_name="Public Interest Legal Foundation v. Nago"`) — Located district court RECAP docket (`1:23-cv-00389`, D. Haw.) and prior filings.
2. `mcp_courtlistener_search` (`type="o"`, `q=""20507(i)(1)" "statewide""`) — Located recent circuit and district court opinions interpreting 52 U.S.C. § 20507(i)(1), including *Wisconsin Voter Alliance v. Secord* (7th Cir. 2026), *United States v. Benson* (6th Cir. 2026), *Public Interest Legal Foundation, Inc. v. Knapp* (4th Cir. 2025), *Public Interest Legal Foundation, Inc. v. Bellows* (1st Cir. 2024), and *Public Interest Legal Foundation v. Benson* (6th Cir. 2025).
3. `mcp_courtlistener_read_document` (`opinion_id=11421360`, chunks 0–3) — Read Seventh Circuit opinion in *Wisconsin Voter Alliance v. Secord* (No. 25-1102, decided July 1, 2026).
4. `mcp_courtlistener_read_document` (`opinion_id=11347238`, chunks 0–5) — Read Sixth Circuit opinion in *United States v. Benson* (No. 26-1225, decided May 27, 2026).
5. `mcp_courtlistener_read_document` (`opinion_id=11242441`, chunks 0–2) — Read Fourth Circuit opinion in *Public Interest Legal Foundation, Inc. v. Knapp* (No. 25-1152, decided Oct. 17, 2025).
6. `mcp_courtlistener_read_document` (`opinion_id=11408389`, chunks 0–1) — Read Central District of California order in *United States v. Weber* (decided June 26, 2026).
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Public Interest Legal Foundation"` / `"Voter Reference Foundation"` / `"Bellows"`) — Checked for SCOTUS opinions.
8. `mcp_courtlistener_read_document` (`opinion_id=9929645`, chunks 0–1) — Read First Circuit opinion in *Public Interest Legal Foundation, Inc. v. Bellows*, 92 F.4th 36 (1st Cir. 2024).
9. `mcp_courtlistener_search` (`type="o"`, `case_name="Voter Reference Foundation v. Torrez"`) and `mcp_courtlistener_read_document` (`opinion_id=11208775`, chunks 0–6) — Read Tenth Circuit opinion in *Voter Reference Foundation, LLC v. Torrez*, 160 F.4th 1068 (10th Cir. 2025).
10. `mcp_courtlistener_read_document` (`opinion_id=11001484`, chunks 0–3, 6–9) — Read Sixth Circuit opinion in *Public Interest Legal Foundation v. Benson*, 136 F.4th 613 (6th Cir. 2025).
11. `mcp_courtlistener_search` (`type="o"`, `citation="136 F.4th 456"`) and `mcp_courtlistener_search` (`type="o"`, `court="ca3"`, `case_name="Secretary Commonwealth of Pennsylvania"`) — Located Third Circuit opinion in *Public Interest Legal Foundation v. Secretary Commonwealth of Pennsylvania*, 136 F.4th 456 (3d Cir. 2025).
12. `mcp_courtlistener_read_document` (`opinion_id=10869827`, chunk 0; `opinion_id=10869828`, chunks 0–3) — Read Third Circuit opinion in *Public Interest Legal Foundation v. Secretary Commonwealth of Pennsylvania*, 136 F.4th 456 (3d Cir. 2025).
13. `mcp_courtlistener_read_document` (`opinion_id=11417488`, chunks 0–1; `opinion_id=11461188`, chunk 0) — Inspected additional search hits from query 2.
14. `mcp_courtlistener_search` (`type="r"`, `case_name="Public Interest Legal Foundation v. Benson"` / `"Voter Reference Foundation v. Torrez"` / `"Public Interest Legal Foundation v. Secretary Commonwealth of Pennsylvania"` / `"Public Interest Legal Foundation v. Bellows"` / `"Public Interest Legal Foundation v. Knapp"`) — Checked appellate and district RECAP dockets for certiorari notices and subsequent history.
15. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=67167399` and `docket=67633227`) and (`endpoint_id="dockets"`, `court="ca3"`, `docket_number="23-1590"`) — Checked Third and First Circuit docket entries for cert filings.
16. `mcp_courtlistener_search` (`type="r"`, `q=""25-379" "Public Interest Legal Foundation""`) and `mcp_courtlistener_read_document` (`recap_document_id=474158548`, chunk 0; `recap_document_id=474158549`, chunk 0) — Confirmed that certiorari was denied on March 2, 2026 in *Public Interest Legal Foundation v. Secretary of the Commonwealth of Pennsylvania*, No. 25-379, 2026 WL 568366 (U.S. Mar. 2, 2026), and in *Public Interest Legal Foundation v. Benson*, No. 25-437 (U.S. Mar. 2, 2026).
17. `mcp_courtlistener_search` (`type="o"` / `type="r"`, `q=""Public Interest Legal Foundation" "Bellows" "cert. denied""` and `""Voter Reference Foundation" "Torrez""`) — Checked subsequent history of *Bellows* and *Torrez*.
