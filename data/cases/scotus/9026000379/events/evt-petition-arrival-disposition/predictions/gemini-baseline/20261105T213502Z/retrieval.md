# Retrieval Log: `scotus/9026000379` (`evt-petition-arrival-disposition`)

## 1. Mode and Cutoff Compliance
- **Mode:** `forward` (`context.json`: `"mode": "forward"`, `"cutoff": "2026-09-22"`).
- **Compliance:** Per `.github/prompts/predict.md`, in `forward` mode (a genuinely pending case), external retrieval is unrestricted because the disposition outcome does not yet exist; `cutoff` (`2026-09-22`) bounds only the provisioned arrival baseline (`snapshots/2026-09-21.json`).

## 2. CLI Path Resolution and Help Calls
1. `uv run fedcourts paths --court "scotus" --docket "9026000379" --event "evt-petition-arrival-disposition" --role predictor`
   - Resolved `case_id: scotus/9026000379`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/9026000379/events/evt-petition-arrival-disposition/event.yaml`.
2. `uv run fedcourts query --help`
   - Read CLI options and structured filter documentation.

## 3. Corpus Queries (`uv run fedcourts query`)
Every `fedcourts query` call attempted (including failed/refused ones that were re-issued) and its stderr transfer line:

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent granted SCOTUS rows in the 2020s era, including `scotus/9026000104` (*Rhoney v. Barbosa da Cunha*, No. 26-104), `scotus/9026000204` (*DOJ v. McNutt*, No. 26-204), `scotus/73500246` (*Blanche v. Ozurumba*, No. 25-1343), and `scotus/73281386` (*U.S. DOGE Service v. U.S. District Court*, No. 25-1103).

2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Returned 10 recent SCOTUS GVR rows in the 2020s era, including `scotus/9026000048` (*Mullin v. National TPS Alliance*, No. 26-48).

3. `uv run fedcourts query --court scotus --docket-number 26-379`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned the corpus row for `scotus/9026000379` (*Kenneth Genalo, et al. v. D. C.*, No. 26-379), showing counsel (`D. John Sauer`, `Jessica N. Coffrin-St. Julien`, `Eric Harris Wessan` for amicus `Iowa, et al.`), `originating_court: "ca2"`, `originating_docket_number: "26-1396"`, and `disposition: null` as of `last_live_polled: "2026-11-05"`.

4. `uv run fedcourts query --court scotus --docket-number 26-104`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9026000104` (*Rhoney v. Barbosa da Cunha*, No. 26-104, granted Oct. 1, 2026).

5. `uv run fedcourts query --court scotus --include-open --limit 30`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 30 recent SCOTUS rows.

6. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 100 | grep -i -E "Sauer|Genalo|Immigration|ICE|1226|Bondi|Blanche|Noem|Mullin|Rhoney|Black"`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Filtered 100 recent SCOTUS rows for Solicitor General and immigration-related cases.

7. `uv run fedcourts query --court scotus --docket-number 25-886`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/73280386` (*Kenneth Genalo, Director of the New York Field Office of U.S. Immigration and Customs Enforcement, et al. v. Carol Williams Black, et al.*, No. 25-886), showing `date_filed: "2026-01-28"`, `date_cert_granted: "2026-06-15"`, `merits_brief_filed: "2026-08-31"`, `merits_terminated: "voluntary-dismissal"`, and 14 amicus counsel entries.

8. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 100 --citation "103 F.4th 133" --citation "583 U.S. 281" --citation "538 U.S. 510"`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned `note:` explaining that `citations` holds a case's own parallel cites rather than a citing-cases graph.

9. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 500 | grep '"disposition":null' | grep "D. John Sauer"`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 0 matching lines within the first 500 `date_decided`-ordered rows.

10. `uv run fedcourts query --court scotus --after 2026-08-01 --include-open --limit 500` (failed usage error: `No such option: --after (Possible options: --era)`).

11. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 2000` (failed validation error: `limit` must be `<= 500`).

12. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 500 | grep "D. John Sauer" | grep '"role":"petitioner"'`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned SCOTUS rows in the top 500 involving D. John Sauer.

13. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 500 | grep -E '"attorney":"D. John Sauer","counsel_of_record":true,"party":"[^"]*","role":"petitioner"'`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned resolved SG petitioner rows in the top 500 (5 granted/GVR, 2 denied).

## 4. CourtListener MCP Lookups
Every CourtListener MCP tool call attempted and what came back:

1. `mcp_courtlistener_search(type="o", court="ca2", docket_number="26-1396")` -> 0 opinion results.
2. `mcp_courtlistener_search(type="r", court="ca2", docket_number="26-1396")` -> 1 RECAP docket result: *C. v. Noem*, No. 26-1396 (`docket_id: 73412762`, filed `2026-05-20`).
3. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=73412762, fields=[... "originating_court_information"])` -> validation error on field name `originating_court_information`; re-issued with `original_court_info`.
4. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 73412762, ...})` -> returned all 21 docket entries (Entries 1–22, May 20, 2026 to Sept. 22, 2026) in *C. v. Noem*, 2d Cir. No. 26-1396, including the Sept. 2, 2026 government motion for summary affirmance and Sept. 21, 2026 Supreme Court certiorari filing.
5. `mcp_courtlistener_search(type="o", party_name="Genalo", q='...')` -> validation error (`party_name` not valid for `type="o"`).
6. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=73412762, fields=[... "original_court_info", ...])` -> returned full docket metadata for 2d Cir. No. 26-1396.
7. `mcp_courtlistener_search(type="r", party_name="Genalo", q="Arteta")` -> 126 RECAP results for SDNY habeas cases involving Kenneth Genalo and Paul Arteta.
8. `mcp_courtlistener_search(type="o", q='"D. C." "Genalo" OR "D.C." "Genalo"')` -> 1 opinion result (*Barbosa Da Cunha v. Freden*, 2d Cir. No. 25-3141).
9. `mcp_courtlistener_search(type="o", docket_number="25-3141")` -> 3 opinion cluster results in *Barbosa Da Cunha v. Freden*, 2d Cir. No. 25-3141 (`opinion_ids: 11316346, 11451136`).
10. `mcp_courtlistener_search(type="r", court="nysd", atty_name="Coffrin-St. Julien")` -> 9 SDNY RECAP results, identifying the underlying district court habeas docket: *C. v. Noem*, No. 1:26-cv-01833-PAE (`docket_id: 72370811`, filed Mar. 5, 2026, assigned to Judge Paul A. Engelmayer).
11. `mcp_courtlistener_search(type="r", court="nysd", q='"D.C." OR "D. C." Genalo "March 20, 2026" OR "03/20/2026"')` -> 385 RECAP results.
12. `mcp_courtlistener_read_document(opinion_id=11316346)` and `mcp_courtlistener_read_document(opinion_id=11451136)` -> returned `"No text is available for this document"` on the opinion endpoint (read via RECAP document instead).
13. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 72370811, ...})` -> returned all 21 docket entries in *C. v. Noem*, No. 1:26-cv-01833-PAE (S.D.N.Y.), including the full text of Judge Engelmayer's March 20, 2026 Opinion and Order (`recap_document_id: 473020076`, *D.C. v. Noem*, 2026 WL 794162) and the March 30–31, 2026 status letters confirming D.C.'s release on bond.
14. `mcp_courtlistener_search(type="o", q='"26-cv-1833" OR "26 Civ. 1833" OR "26-cv-01833" OR "26 Civ. 01833"')` -> 0 results on opinion index.
15. `mcp_courtlistener_search(type="r", q='"Barbosa da Cunha" OR "25-3141"')` -> returned RECAP docket for *Barbosa da Cunha v. Freden*, 2d Cir. No. 25-3141 (`docket_id: 72053152`).
16. `mcp_courtlistener_search(type="r", court="scotus", docket_number="26-379")` -> 0 results on CourtListener SCOTUS RECAP index.
17. `mcp_courtlistener_read_document(recap_document_id=495062413, chunk_index=0)` -> read Judge Menashi's Sept. 25, 2026 dissent from denial of rehearing en banc in *Barbosa da Cunha v. Freden*, 2d Cir. No. 25-3141.
18. `mcp_courtlistener_search(type="r", court="ca2", q='"summary affirmance" "Black v. Decker" OR "1226(c)"')` -> 86 results, including *C. v. Noem* (No. 26-1396) and *Jules v. Rhoney* (No. 26-1559).
19. `mcp_courtlistener_search(type="r", q='"26-379" "Genalo" OR "Genalo v. D. C." OR "Genalo v. D.C."')` -> 623 results; top results were *Peters v. Raycraft* (6th Cir. No. 26-1562), *Jaimes v. King* (6th Cir. Nos. 26-1283/26-1821), and *Rodriguez v. Bondi* (9th Cir. No. 20-55770).
20. `mcp_courtlistener_read_document(recap_document_id=497682219)` -> read Oct. 14, 2026 Status Report in *Peters v. Raycraft*, 6th Cir. No. 26-1562.
21. `mcp_courtlistener_read_document(recap_document_id=500364921)` -> read Nov. 5, 2026 DOJ Motion to Hold Appeals in Abeyance Pending *Genalo v. D.C.*, No. 26-379, in *Jaimes v. King*, 6th Cir. Nos. 26-1283/26-1821.
22. `mcp_courtlistener_read_document(recap_document_id=498346281, chunk_index=0)` and `(chunk_index=1)` -> read Oct. 22, 2026 Motion to Stay Appellate Proceedings Pending *Genalo v. D.C.*, No. 26-379, in *Rodriguez v. Bondi*, 9th Cir. No. 20-55770.
23. `mcp_courtlistener_read_document(recap_document_id=499993913)` -> read Nov. 2, 2026 DOJ Response in Support of Staying Appellate Proceedings in *Rodriguez v. Bondi*, 9th Cir. No. 20-55770.
24. `mcp_courtlistener_read_document(recap_document_id=492313478)`, `(493860368)`, `(493990944)`, `(494192837)`, `(494446624)` -> returned `"No text is available for this document"` (unfetched 2d Cir. filings in No. 26-1396).
25. `mcp_courtlistener_search(type="r", court="ca2", docket_number="26-1559")` -> 1 result: *Jules v. Rhoney*, 2d Cir. No. 26-1559 (`docket_id: 75011589`).
26. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 75011589, ...})` -> returned docket entries in *Jules v. Rhoney*, 2d Cir. No. 26-1559.
27. `mcp_courtlistener_search(type="r", q='"Genalo v. D.C." OR "Genalo v. D. C."')` -> 4 results matching exact phrase (*Peters v. Raycraft*, *Jaimes v. King*, *Rodriguez v. Bondi*).
28. `mcp_courtlistener_search(type="r", q='"26-1559" "Jules" OR "Marich v. Jules" OR "Rhoney v. Jules"')` -> 43 results.
29. `mcp_courtlistener_search(type="o", q='"Genalo v. D.C." OR "Genalo v. D. C."')` -> 0 opinion results.
30. `mcp_courtlistener_read_document(recap_document_id=493992347)` and `(494192839)` -> returned `"No text is available for this document"`.
31. `mcp_courtlistener_read_document(recap_document_id=474129250)` and `(474277127)` -> returned `"No text is available for this document"` (full text was already included in the `docket-entries` response for `docket_id: 72370811`).
