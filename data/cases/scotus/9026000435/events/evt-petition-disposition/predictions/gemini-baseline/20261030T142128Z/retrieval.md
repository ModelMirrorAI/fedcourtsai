# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent resolved 2020s SCOTUS priors to inspect schema and recent OT 2026 dispositions.

2. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS GVR dispositions to compare procedural posture (distribution counts and party structure on GVRs).

3. `uv run fedcourts query --court scotus --docket-number 26-435`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned the corpus metadata row for `scotus/9026000435` (confirming pending status, `salience_score: 0.0308`, `distribution_count: 1`, `distributed_for_conference: "2026-11-13"`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `case_name="Nexstar Media"`)
   - Result: Returned 2 Second Circuit opinions, including the June 30, 2026 Summary Order below (`NLRB v. Nexstar Media, Inc.`, No. 24-2818) and an earlier published decision (`N.L.R.B. v. Nexstar Media Inc.`, 133 F.4th 201 (2d Cir. 2025)).

2. `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `case_name="Siren Retail"`)
   - Result: Returned 1 Second Circuit opinion (`Siren Retail Corp. v. NLRB`, No. 24-3168, decided Sept. 2, 2026), which the petition cited as pending.

3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Menonita"`)
   - Result: Returned 0 results in the SCOTUS opinion index.

4. `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `case_name="Siren Retail"`, with `cluster_id` and `opinions` fields)
   - Result: Retrieved `opinion_id: 11432337` for `Siren Retail Corp. v. NLRB` (2d Cir. Sept. 2, 2026).

5. `mcp_courtlistener_search` (`type="o"`, `court="cadc"`, `case_name="Menonita"`, with `cluster_id` and `opinions` fields)
   - Result: Retrieved 2 D.C. Circuit opinions in `Hospital Menonita de Guayama, Inc. v. NLRB`, 94 F.4th 1 (D.C. Cir. 2024), and the post-GVR remand decision (`opinion_id: 11400934`, decided July 21, 2026).

6. `mcp_courtlistener_search_document` (`opinion_id=[11432337, 11400934]`, `query="Loper Bright"`)
   - Result: Returned excerpts from `Siren Retail Corp. v. NLRB` (2d Cir. Sept. 2, 2026) confirming that the Second Circuit has now explicitly held in a published opinion that *Loper Bright* ended *Chevron* deference to the NLRB, and excerpts from `Hospital Menonita de Guayama, Inc. v. NLRB` (D.C. Cir. July 21, 2026) on remand from the Supreme Court's 2025 GVR.
