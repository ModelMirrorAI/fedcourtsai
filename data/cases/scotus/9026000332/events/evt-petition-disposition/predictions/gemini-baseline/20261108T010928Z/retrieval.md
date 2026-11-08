# Retrieval Log

## 1. Corpus Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-199`
   - Stderr: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Returned `scotus/9026000199`, *Horseracing Integrity and Safety Authority, Incorporated, et al. v. National Horsemen's Benevolent and Protective Association, et al.* (lead petition filed 2026-08-17 from CA5 No. 23-10520).
2. `uv run fedcourts query --court scotus --docket-number 26-201`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9026000201`, *Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.* (lead petition filed 2026-08-17 from CA5 No. 23-10520).
3. `uv run fedcourts query --court scotus --docket-number 26-332`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9026000332`, *Gulf Coast Racing LLC., et al. v. Horseracing Integrity and Safety Authority, Incorporated, et al.* (this docket; filed 2026-09-11, distributed for Conference of 2026-12-04).
4. `uv run fedcourts query --court scotus --docket-number 26-335`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9026000335`, *Texas, et al. v. Jerry Black, et al.* (companion cross-petition filed 2026-09-14, distributed for Conference of 2026-12-04).
5. `uv run fedcourts query --court scotus --docket-number 26-430`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9026000430`, *National Horsemen's Benevolent and Protective Association, et al. v. Horseracing Integrity and Safety Authority, Incorporated, et al.* (companion cross-petition filed 2026-09-30, distributed for Conference of 2026-12-04).
6. `uv run fedcourts query --court scotus --docket-number 25-1325`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/73500226`, *Oklahoma v. United States* (Sixth Circuit HISA petition filed 2026-05-29, distributed for Conference of 2026-10-09).
7. `uv run fedcourts query --court scotus --docket-number 24-429`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72484140`, *FTC v. National Horsemen's Benevolent and Protective Ass'n* (OT2024 lead petition; `disposition: "gvr"` on 2025-06-30 after 3 distributions).
8. `uv run fedcourts query --court scotus --docket-number 24-433`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/72484144`, *HISA v. National Horsemen's Benevolent and Protective Ass'n* (OT2024 lead petition; `disposition: "gvr"` on 2025-06-30 after 3 distributions).
9. `uv run fedcourts query --court scotus --docket-number 24-465`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/72484176`, *Texas v. Black* (OT2024 cross-petition; `disposition: "gvr"` on 2025-06-30 after 3 distributions).
10. `uv run fedcourts query --court scotus --docket-number 24-472`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Returned `scotus/72484185`, *National Horsemen's Benevolent and Protective Ass'n v. HISA* (OT2024 cross-petition; `disposition: "gvr"` on 2025-06-30 after 3 distributions).
11. `uv run fedcourts query --court scotus --docket-number 24-489`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Returned `scotus/72484202`, *Gulf Coast Racing, L.L.C., et al. v. HISA* (OT2024 cross-petition by same petitioners; `disposition: "gvr"` on 2025-06-30 after 3 distributions).
12. `uv run fedcourts query --court scotus --docket-number 24-696`, `24-665`, `24-700`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`, `1 GET(s), 262144 byte(s)`, `0 GET(s), 0 byte(s)`
    - Result: Checked unrelated OT2024 dockets while verifying docket numbers.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Horseracing Integrity")`
   - Result: `0` results.
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Oklahoma v. United States")`
   - Result: Rate-limited (HTTP 429; 25/min).
3. `mcp_courtlistener_search(type="o", court="ca5", case_name="National Horsemen")`
   - Result: Rate-limited on first simultaneous call; succeeded on retry, returning `National Horsemen's Benevolent v. Black`, 53 F.4th 869 (5th Cir. 2022) (`cluster_id: 8515308`).
4. `mcp_courtlistener_search(type="o", citation="107 F.4th 415")`
   - Result: Returned `Natl Horsemen's Benevolent v. Black`, 107 F.4th 415 (5th Cir. July 5, 2024) (`cluster_id: 9997933`, `opinion_id: 10464534`).
5. `mcp_courtlistener_search(type="o", case_name="Walmsley v. Federal Trade Commission")`
   - Result: `0` results.
6. `mcp_courtlistener_search_document(opinion_id=10464534, query="Appointments Clause")`
   - Result: Returned 18 snippets from `107 F.4th 415` covering the Fifth Circuit's Appointments Clause analysis (Part III.D of *Horsemen's II*).
7. `mcp_courtlistener_read_document(opinion_id=10464534, chunk_index=[8, 9, 10, 11, 12, 13])`
   - Result: Returned the full text of the Fifth Circuit's opinion in `107 F.4th 415` from page 24 to page 39 (including the private nondelegation enforcement analysis, the Due Process analysis, the Appointments Clause / *Lebron* analysis in Part III.D, and the anti-commandeering standing analysis in Part III.E, which had been omitted from the appendix in `petition.txt` due to the 150,000-character pipeline cap).
8. `mcp_courtlistener_search(type="o", citation="163 F.4th 294")`
   - Result: `0` results (the June 11, 2026 Fifth Circuit remand opinion is fully reproduced in Appendix A of `petition.txt`).
9. `mcp_courtlistener_search(type="o", citation="606 U.S. 656")`
   - Result: Returned `FCC v. Consumers' Research`, 606 U.S. 656 (June 27, 2025) (`cluster_id: 10776820`, `opinion_id: 11243407`).
10. `mcp_courtlistener_search_document(opinion_id=11243407, query="private nondelegation")` and `query="Appointments Clause"`
    - Result: Returned 7 matches for "private nondelegation" and 1 match for "Appointments Clause" in `FCC v. Consumers' Research`.
11. `mcp_courtlistener_read_document(opinion_id=11243407, chunk_index=[13, 14, 15])`
    - Result: Read Parts III and IV of `FCC v. Consumers' Research`, 606 U.S. at 691–698, analyzing the private nondelegation doctrine under *Carter Coal* and *Sunshine Anthracite* and rejecting the Fifth Circuit's "combination" theory.
