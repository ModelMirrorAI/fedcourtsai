# Retrieval Log: `scotus/73500244` (`evt-petition-disposition`)

## 1. Corpus Lookups (`fedcourts query`)

1. **`uv run fedcourts query --court scotus --docket-number 25-7371`**
   - Transfer stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned 1 row: `scotus/73338271`, *Travis McMichael v. United States*, No. 25-7371 (originating from 11th Cir. No. 22-12792, *United States v. Bryan*). Showed `date_filed: 2026-05-13`, `distributed_for_conference: 2026-10-16`, `distribution_count: 1`, `disposition: denied`, `date_cert_denied: 2026-10-19`.

2. **`uv run fedcourts query --court scotus --docket-number 25-1342`**
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: `scotus/73500244`, *Derick Irisha Brown v. United States*, No. 25-1342, confirming pre-decision metadata (`distribution_count: 3`, `salience_score: 0.4169`, `salience_version: sal-v8`).

3. **`uv run fedcourts query --court scotus --disposition granted --limit 10`**
   - Transfer stderr: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   - Returned 10 recent OT 2026 granted petitions/applications (*Goldman Sachs Bank USA v. Brown*, No. 25-1408; *Berry v. United States*, No. 25-7026; *Blanche v. Ozurumba*, No. 25-1343; *U.S. DOGE Service v. U.S. District Court*, No. 25-1103; etc.) for context on current Term grant and relist patterns.

4. **`uv run fedcourts query --court scotus --judge Luck --judge Black --judge Wilson --limit 10`**
   - Transfer stderr: `ranged corpus reads: 720 GET(s), 188612608 byte(s)`
   - Returned 0 rows.

## 2. CourtListener MCP Lookups

1. **`mcp__courtlistener__search`** (`type="o"`, `court="ca10"`, `case_name="United States v. Chavarria"`)
   - Returned 1 result: *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. June 16, 2025) (`cluster_id=10605317`, `opinion_id=11071905`).

2. **`mcp__courtlistener__search`** (`type="o"`, `court="ca11"`, `case_name="United States v. Bryan"`)
   - Returned 21 results, including *United States v. William Bryan*, 159 F.4th 1274 (11th Cir. Nov. 14, 2025) (`cluster_id=10736825`, `opinion_id=11203410`).

3. **`mcp__courtlistener__search`** (`type="d"`, `court="scotus"`, `case_name="McMichael v. United States"`)
   - Returned 0 results (CourtListener SCOTUS docket index did not have the entry; subsequently retrieved via `fedcourts query`).

4. **`mcp__courtlistener__read_document`** (`opinion_id=11071905`, `chunk_index=0`, `chunk_size=12000`)
   - Read first chunk of *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025).

5. **`mcp__courtlistener__read_document`** (`opinion_id=11071905`, `chunk_index=[1, 2, 3]`, `chunk_size=12000`)
   - Read chunks 1–3 of *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025).

6. **`mcp__courtlistener__read_document`** (`opinion_id=11071905`, `chunk_index=4`, `chunk_size=12000`)
   - Read final chunk (chunk 4) of *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025).

7. **`mcp__courtlistener__search_document`** (`opinion_id=11203410`, `query="Chavarria"`, `snippet_size=1000`)
   - Retrieved 20 matching excerpts (of 22 matches) in *United States v. Bryan*, 159 F.4th 1274 (11th Cir. 2025), covering footnote 17 of the majority opinion and Judge Calvert's partial dissent discussing *Chavarria*, *Protho*, and *Windham*.

## 3. Web Searches

- None attempted.
