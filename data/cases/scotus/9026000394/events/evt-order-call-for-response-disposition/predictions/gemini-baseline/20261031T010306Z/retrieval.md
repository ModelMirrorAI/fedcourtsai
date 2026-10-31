# Retrieval Log

## 1. Corpus CLI (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1013`
   - Stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned `scotus/73281060`, *Official Committee of Asbestos Claimants of Bestwall LLC v. Bestwall LLC*, No. 25-1013 (originating from CA4 No. 24-1493), cert. denied `2026-06-01` after 1 distribution.
2. `uv run fedcourts query --court scotus --docket-number 23-675`
   - Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned `scotus/72482019`, *Official Committee of Asbestos Claimants v. Bestwall LLC, et al.*, No. 23-675 (originating from CA4 Nos. 22-1127, 22-1135), cert. denied `2024-05-13` after 1 distribution.
3. `uv run fedcourts query --court scotus --docket-number 23-702`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/72482323`, *Sander L. Esserman, in His Official Capacity as Future Claims Representative v. Bestwall LLC, et al.*, No. 23-702 (originating from CA4 Nos. 22-1127, 22-1135), cert. denied `2024-05-13` after 1 distribution.
4. `uv run fedcourts query --court scotus --judge Niemeyer --judge King --limit 10`
   - Stderr: `ranged corpus reads: 651 GET(s), 170393600 byte(s)`
   - Result: Empty (0 rows returned; CA4 panel judges are not populated on SCOTUS corpus rows).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(court="ca4", q=""Bestwall LLC" 148 F.4th 233", type="o")`
   - Result: Returned 1 match (`Michael Herlihy v. DBMP, LLC`, opinion cluster 10792806, which cites `Bestwall LLC`, 148 F.4th 233). Did not read the opinion via CourtListener as it is already provisioned in `record/documents/appendix.txt`.
2. `mcp_courtlistener_search(court="ca4", docket_number="24-1493", fields=["caseName", "dateFiled", "docketNumber", "opinions"], type="o")`
   - Result: Returned *Bestwall LLC v. Official Committee of Asbestos Claimants*, No. 24-1493, decided `2025-08-01` (opinion ID `11113487`, 148 F.4th 233).
3. `mcp_courtlistener_search_document(opinion_id=11113487, query="subject matter jurisdiction")`
   - Result: Returned 2 snippets from the Fourth Circuit's August 1, 2025 *Bestwall* opinion (`11113487`).
4. `mcp_courtlistener_read_document(opinion_id=11113487, chunk_index=0, chunk_size=6000)`
   - Result: Read chunk 0 of `11113487` (*Bestwall LLC v. Official Committee of Asbestos Claimants*, 148 F.4th 233 (4th Cir. 2025)), confirming the panel (King, Agee, Quattlebaum) and holding on constitutional subject-matter jurisdiction over solvent debtors.
5. `mcp_courtlistener_read_document(opinion_id=11113487, chunk_index=[3, 4], chunk_size=6000)`
   - Result: Read chunks 3–4 of `11113487`, reviewing the procedural history of *Bestwall*'s bad-faith dismissal motions under *Carolin Corp. v. Miller* and the Fourth Circuit's prior denial of interlocutory review.

## 3. Web Searches

None attempted.
