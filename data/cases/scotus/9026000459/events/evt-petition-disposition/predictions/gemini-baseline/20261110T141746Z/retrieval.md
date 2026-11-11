# Retrieval Log: `scotus/9026000459` (`evt-petition-disposition`)

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "608 U.S. 391" --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Check corpus priors for `608 U.S. 391` (*Pitchford v. Cain*). Returned 0 rows from the local/service citation column; used CourtListener MCP to read the full opinion.

2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Inspect recent OT2026 SCOTUS GVR dispositions (e.g., `scotus/73278467`, `scotus/73500249`, `scotus/9026005123`, `scotus/73317900`, `scotus/73500268`) and their conference distribution counts (`distribution_count` typically 2–3, or IFP criminal companion holds).

3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Inspect recent OT2026 SCOTUS cert grants (e.g., `scotus/73520108`, `scotus/9026000012`, `scotus/9026000204`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`) and verify their distribution counts (`2` to `5` distributions prior to grant).

4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Inspect recent OT2026 SCOTUS cert denials (`scotus/73500344`, `scotus/73500351`, `scotus/9026000018`, `scotus/9026000055`, `scotus/9026000085`, `scotus/9026000087`), including first-distribution denials from the Fifth Circuit where the United States waived or did not file a response.

## 2. CourtListener MCP Queries

1. `mcp_courtlistener_search(type="o", case_name="Pitchford v. Cain", num_results=5)`
   - Purpose: Locate the Supreme Court's May 28, 2026 decision in *Pitchford v. Cain*, No. 24-7351 (`cluster_id: 10865525`, `opinion_id: 11332973`), and the underlying Fifth Circuit decisions (`124 F.4th 958`, `126 F.4th 422`).

2. `mcp_courtlistener_search(type="o", q='"Pitchford v. Cain" Batson', num_results=10)`
   - Purpose: Identify subsequent federal appellate and state decisions citing *Pitchford v. Cain* on *Batson* step three, including *Salters v. N.Y.C. Transit Auth.* (`cluster_id: 10942142`, 2d Cir. Aug. 7, 2026).

3. `mcp_courtlistener_read_document(opinion_id=11332973, chunk_index=0)` and `mcp_courtlistener_read_document(opinion_id=11332973, chunk_index=[1, 2])`
   - Purpose: Read the syllabus and majority opinion of Justice Kavanaugh in *Pitchford v. Cain*, 608 U.S. 391 (2026), to verify its exact holding (unreasonable state-court finding of waiver under AEDPA where the trial judge twice cut off defense counsel and omitted *Batson* step three) and compare it to petitioner Grace's GVR argument.

4. `mcp_courtlistener_search(type="o", q='"Salters" "New York City Transit" Batson', num_results=5)`
   - Purpose: Retrieve opinion metadata (`opinion_id: 11409725`) for *Salters v. N.Y.C. Transit Auth.* (2d Cir. Aug. 7, 2026), cited in Grace's petition at 11–12.

5. `mcp_courtlistener_search_document(opinion_id=11409725, query="Pitchford")` and `mcp_courtlistener_search_document(opinion_id=11409725, query="remand")`
   - Purpose: Verify how the Second Circuit majority and Judge Menashi's dissent in *Salters* applied *Pitchford v. Cain* and *Batson* step three.
