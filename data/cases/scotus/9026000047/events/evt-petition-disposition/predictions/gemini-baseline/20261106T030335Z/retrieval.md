---
model: gemini-4-argon
---

# Retrieval Log

## 1. Corpus Prior Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1358" --limit 5`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Purpose: Check corpus citation index for *Flowers Foods, Inc. v. Brock*, 146 S. Ct. 1358 (2026). Returned 0 rows (parallel citations column sparsely populated; note advised looking up by docket or CourtListener MCP).

2. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   - Purpose: Retrieve recent 2020s SCOTUS GVR dispositions to inspect distribution counts, CFR patterns, and post-merits GVR practice in OT2025/OT2026.

3. `uv run fedcourts query --court scotus --docket-number 24-935 --full`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Purpose: Retrieve the full corpus record for *Flowers Foods, Inc., et al. v. Angelo Brock* (No. 24-935, `scotus/72487215`), confirming cert grant date (`2025-10-20`), merits decision date (`2026-05-28`), judgment (`affirmed`), and counsel/amici (including Jennifer Dale Bennett as respondent's counsel of record and Amazon.com, Inc. as amicus).

4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Retrieve recent OT2026 plenary grants to compare amicus participation, originating courts, and distribution counts.

5. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 40`
   - Transfer: `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
   - Purpose: Check June–October 2026 GVR dispositions to see whether any trailing FAA Section 1 petitions were GVR'd following *Flowers Foods v. Brock* (decided May 28, 2026).

6. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026-06-20 --limit 15`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Purpose: Check early June 2026 GVR orders (June 1 and June 8, 2026 order lists immediately following *Flowers Foods v. Brock*); confirmed no FAA Section 1 petitions were GVR'd in the wake of *Brock*.

## 2. External Legal Research (CourtListener MCP)

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"Flowers Foods" Brock'`)
   - Located *Flowers Foods, Inc. v. Brock*, No. 24-935, `cluster_id=10865526`, `opinion_id=11332974`, decided May 28, 2026.

2. `mcp_courtlistener_read_document` (`opinion_id=11332974`)
   - Read the full slip opinion of *Flowers Foods, Inc. v. Brock*, 608 U.S. ___, 146 S. Ct. 1358 (2026) (Gorsuch, J., for a unanimous Court), including Part II's discussion (slip op. 7–8) of unpreserved arguments and citations to *Rittmann v. Amazon.com, Inc.*, 971 F.3d 904, 916 (9th Cir. 2020).

3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2026-05-28"`, `q='"Flowers Foods" OR "24-935"'`)
   - Confirmed no subsequent Supreme Court opinions or GVR orders cited *Flowers Foods v. Brock*.

4. `mcp_courtlistener_search` (`type="o"`, `filed_after="2026-05-28"`, `q='"Flowers Foods" Brock'`)
   - Identified lower-court opinions citing *Flowers Foods v. Brock* after May 28, 2026, including *Betanco v. Living Spaces Furniture, LLC* (Cal. Ct. App. June 25, 2026, No. A169754), *Doss v. Tesla, Inc.* (Cal. Ct. App. June 11, 2026, No. A173210), and *Orr v. USDC for the Central District of California* (9th Cir. June 9, 2026, No. 25-2330).

5. `mcp_courtlistener_search` (`type="o"`, `filed_after="2026-05-28"`, `q='"Flowers Foods" Brock (Orr OR Betanco)'`)
   - Retrieved opinion IDs for *Betanco* (`11348006`) and *Orr* (`11339958`).

6. `mcp_courtlistener_search_document` (`opinion_id=[11348006, 11339958]`, `query="Brock"`) & `mcp_courtlistener_search_document` (`opinion_id=11348006`, `query="Flowers"`)
   - Located excerpts in *Betanco* and *Orr* discussing *Flowers Foods v. Brock*.

7. `mcp_courtlistener_read_document` (`opinion_id=11348006`, `chunk_index=3`)
   - Read the California Court of Appeal's analysis in *Betanco v. Living Spaces Furniture, LLC* (First Appellate District, June 25, 2026), confirming that after supplemental briefing on *Brock*, the California Court of Appeal held that *Brock* reinforces *Rittmann* and *Carmona Mendoza* and rejected the argument that goods ordered after arriving at an in-state warehouse are categorically outside FAA Section 1.

8. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `filed_after="2026-01-01"`, `q='"Flowers Foods" OR "Amazon Logistics" OR "Living Spaces" OR "Domino's" OR "Cintas"'`) & `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2026-05-28"`, `filed_before="2026-07-15"`)
   - Verified June 2026 SCOTUS opinions and dockets.
