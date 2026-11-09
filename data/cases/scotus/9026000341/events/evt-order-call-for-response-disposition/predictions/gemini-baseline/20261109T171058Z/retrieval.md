# Retrieval Log

## 1. Local Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1403" --limit 5`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

2. `uv run fedcourts query --court scotus --citation "591 U.S. 71" --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Result: 10 rows (recent 2020s SCOTUS granted petitions and applications, including `scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`).

4. `uv run fedcourts query --court scotus --party "Sripetch" --limit 5`
   - Transfer line: none (CLI usage error: `No such option: --party`; re-issued with `--docket-number` below).

5. `uv run fedcourts query --court scotus --docket-number "25-466" --full`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: 1 row (`scotus/73215957`, *Ongkaruck Sripetch v. Securities and Exchange Commission*, No. 25-466, cert granted 2026-01-09, merits decided 2026-06-04, `merits_judgment: "affirmed"`).

6. `uv run fedcourts query --court scotus --judge "Tjoflat" --limit 10`
   - Transfer line: `ranged corpus reads: 715 GET(s), 187432960 byte(s)`
   - Result: 0 rows.

7. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: 10 rows (recent 2020s SCOTUS GVR dispositions).

## 2. CourtListener MCP Server Calls

1. `mcp_courtlistener_search_document(opinion_id=10775540, query="TJOFLAT")`
   - Result: 0 matches (`total_chars: 3517`; revealed that `10775540` in `documents.json` was the cluster ID rather than the combined opinion ID in the Eleventh Circuit case).

2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Sripetch v. SEC", filed_before="2026-10-23")`
   - Result: 1 match (`cluster_id: 10870059`, `opinion_id: 11337516`, *Sripetch v. SEC*, No. 25-466, decided June 4, 2026).

3. `mcp_courtlistener_search(type="o", court="ca11", case_name="Spartan Securities", filed_before="2026-10-23")`
   - Result: 1 match (`cluster_id: 10775540`, `opinion_id: 11242127`, *U.S. Securities and Exchange Commission v. Spartan Securities Group, Ltd.*, No. 22-13129, decided Jan. 16, 2026).

4. `mcp_courtlistener_read_document(opinion_id=11337516)`
   - Result: Full slip opinion of *Sripetch v. SEC*, 608 U.S. ___, 146 S. Ct. 1403 (June 4, 2026) (`total_chars: 72765`), including Justice Gorsuch's opinion for the unanimous Court and Justice Thomas's concurrence.

5. `mcp_courtlistener_search_document(opinion_id=11242127, query="TJOFLAT")`
   - Result: 73 matches across the 487,215-character Eleventh Circuit slip opinion (`opinion_id=11242127`), locating Judge Tjoflat's dissent starting on slip opinion page 81.

6. `mcp_courtlistener_read_document(opinion_id=11242127, chunk_index=19, chunk_size=8000)`
   - Result: Read chunk 19 (pages 66–69 of the slip opinion) covering the Eleventh Circuit majority's § 78u(d)(7) and equitable disgorgement analysis.

7. `mcp_courtlistener_read_document(opinion_id=11242127, chunk_index=[58, 59, 60], chunk_size=8000)`
   - Result: Read chunks 58–60 (pages 203–211 of the slip opinion), covering the end of the SEC complaint attached as the appendix to Judge Tjoflat's dissent.

8. `mcp_courtlistener_search_document(opinion_id=11242127, query="disgorgement")`
   - Result: 74 matches across `opinion_id=11242127`.

9. `mcp_courtlistener_read_document(opinion_id=11242127, chunk_index=[20, 21, 22, 23, 46, 47, 48, 49, 50], chunk_size=8000)`
   - Result: Read chunks 20–23 (pages 69–82 of the slip opinion, covering Part 2 of the majority's disgorgement analysis, the remedies affirmance, and the opening of Judge Tjoflat's dissent) and chunks 46–50 (part of the dissent's appendix).

10. `mcp_courtlistener_read_document(opinion_id=11242127, chunk_index=[42, 43, 44], chunk_size=8000)`
    - Result: Read chunks 42–44 (pages 141–151 of the slip opinion), covering the conclusion of Judge Tjoflat's dissent.

11. `mcp_courtlistener_search(type="o", q="Sripetch", filed_before="2026-10-23")`
    - Result: 5 matches (*Sripetch v. SEC* in SCOTUS and CA9, *SEC v. Barry* in CA9, and two Seventh Circuit opinions in *Bad River Band v. Enbridge Energy*), confirming no post-*Sripetch* circuit split on Treasury disgorgement.
