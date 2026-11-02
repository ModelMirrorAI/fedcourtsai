# Retrieval Log (`scotus/9526000602`, `evt-motion-disposition`)

## 1. Corpus Queries (`fedcourts query`)

1. **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - **Transfer stderr line:** `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - **Returned rows:** 5 resolved SCOTUS denied priors from the 2020s era (`scotus/9526000499` / `26A499` *Louisiana v. Devon Energy Production Co.*; `scotus/9526000535` / `26A535` *Griffin v. Isaac*; `scotus/9526000532` / `26A532` *Monte v. United States*; `scotus/9526000555` / `26A555` *Schultz v. BOKF, N.A.*; `scotus/9526000556` / `26A556` *Wiggan v. Interinsurance Exchange of the Automobile Club*).

2. **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - **Transfer stderr line:** `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   - **Returned rows:** 5 resolved SCOTUS granted priors from the 2020s era (`scotus/9526000512` / `26A512` *Scanlan v. Coalition for Open Democracy*; `scotus/9026000012` / `26-12` *Association for Education Fairness v. Montgomery County Board of Education*; `scotus/9026000204` / `26-204` *Department of Justice v. McNutt*; `scotus/9526000476` / `26A476` *FCC v. Brown*; `scotus/73281386` / `25-1103` *U.S. DOGE Service v. U.S. District Court for the District of Columbia*).

## 2. CourtListener MCP Lookups

1. **`mcp_courtlistener_search` (`type="r"`, `court="flsd"`, `docket_number="26-cv-25796"`):**
   - Returned 1 match: `U.S. Bank National Association v. Nichloson`, Docket No. `1:26-cv-25796` (S.D. Fla., `docket_id: 74695787`, filed `2026-08-25`).

2. **`mcp_courtlistener_search` (`type="r"`, `party_name="Nichloson"`):**
   - Returned 8 RECAP dockets involving Micahiel Nichloson in Florida federal district and bankruptcy courts, including `U.S. Bank National Association v. Nichloson`, No. `1:26-cv-25796` (S.D. Fla., `docket_id: 74695787`), a subsequent removal `U.S. Bank National Association v. Nichloson`, No. `1:26-cv-27288` (S.D. Fla., `docket_id: 74975029`, filed `2026-10-15`), `Nichloson v. Reid`, No. `1:26-cv-24577` (S.D. Fla., `docket_id: 73571025`), and Chapter 7 bankruptcy case `Micahiel Isaac Nichloson`, No. `26-21210` (Bankr. S.D. Fla., `docket_id: 74688891`, filed `2026-08-24`).

3. **`mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 74695787, "fields": ["id", "entry_number", "date_filed", "description", "recap_documents"]}`, `num_results=30`):**
   - Returned 22 docket entries for `1:26-cv-25796` (S.D. Fla.), showing Notice of Removal (ECF No. 1, Aug. 25, 2026), Order Remanding Case to State Court (ECF No. 10, Aug. 26, 2026), Order on Motion for Recusal and Motion to Vacate (Aug. 27, 2026), Notice of Appeal and Motion to Stay (ECF Nos. 15, 17, Sept. 16, 2026), and Order on Motion to Stay (ECF No. 22, Sept. 30, 2026).

4. **`mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 74975029, "fields": ["id", "entry_number", "date_filed", "description", "recap_documents"]}`, `num_results=20`):**
   - Returned 5 docket entries for the second removal `1:26-cv-27288` (S.D. Fla.), showing Notice of Removal (ECF No. 1, Oct. 16, 2026), IFP motion (ECF No. 3, Oct. 16, 2026), and Amended Notice of Removal (ECF No. 5, Oct. 20, 2026).

5. **`mcp_courtlistener_search` (`type="r"`, `court="ca11"`, `party_name="Nichloson"`):**
   - Returned 0 results.

6. **`mcp_courtlistener_search` (`type="o"`, `q="Nichloson"`):**
   - Returned 0 opinion results.

## 3. Web Searches

- None attempted.
