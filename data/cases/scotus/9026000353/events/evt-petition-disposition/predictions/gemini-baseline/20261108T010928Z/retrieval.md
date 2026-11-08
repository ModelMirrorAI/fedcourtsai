# Retrieval Log

## 1. Corpus Lookups (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1246`
   - Stderr transfer line: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Returned 1 row (`scotus/73292081`, *Richard Vasquez v. Eric Guerrero, Director, Texas Department of Criminal Justice, Correctional Institutions Division*, docket `25-1246`, filed `2026-05-04`, `distributed_for_conference: "2026-12-04"`, `distribution_count: 3`).
2. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
   - Stderr transfer line: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Result: Returned 10 recent resolved SCOTUS rows from the 2020s era.
3. `uv run fedcourts query --court scotus --judge Haynes --judge Engelhardt --judge Wilson --limit 10`
   - Stderr transfer line: `ranged corpus reads: 699 GET(s), 183107584 byte(s)`
   - Result: Returned 0 rows (live-channel SCOTUS rows do not populate lower-court panel judges).
4. `uv run fedcourts query --court scotus --counsel "Thomas M. Farrell" --counsel "Gwendolyn S. Vindell" --limit 10`
   - Result: Failed with CLI usage error (`No such option: --counsel`).
5. `uv run fedcourts query --court scotus --disposition denied --decided-before 2026-11-08 --limit 25`
   - Stderr transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: Returned 25 resolved SCOTUS rows decided before `2026-11-08`, including recent cert denials (`scotus/9026005865`, `scotus/73265705`, `scotus/73266074`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `case_name="Vasquez v. Guerrero"`)
   - Result: 0 matches.
2. `mcp_courtlistener_search` (`type="o"`, `citation="142 S. Ct. 2576"`)
   - Result: 1 match (*Claassen v. United States*, 1891 LEXIS cite match).
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Storey v. Lumpkin"`)
   - Result: 0 matches.
4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Bernard v. United States"`)
   - Result: 26 matches, including *Bernard v. United States* (2020).
5. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""second or successive" Brady Panetti"`)
   - Result: 1 match (*Johnson v. Bredesen*, 558 U.S. 1067 (2009)).
6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Bowe v. United States"`)
   - Result: 11 matches, including *Bowe v. United States*, `cluster_id: 10772450`, decided `2026-01-09` (No. 24-5438).
7. `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `q=""second or successive" Brady "2244(b)""`)
   - Result: 22 matches, including *Storey v. Lumpkin*, `cluster_id: 4906045`, decided `2021-08-06` (No. 20-70014).
8. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 10772450, "fields": ["id", "type", "author_str"]}`)
   - Result: Returned `opinion_id: 11239035`.
9. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 4906045, "fields": ["id", "type", "author_str"]}`)
   - Result: Returned `opinion_id: 4709824`.
10. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Storey v. Lumpkin""`)
    - Result: 0 matches.
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""second or successive" "2244(b)" Brady"`)
    - Result: 19 matches, including *Gonzalez v. Crosby*, 545 U.S. 524 (2005), and *Panetti v. Quarterman*, 551 U.S. 930 (2007).
12. `mcp_courtlistener_search_document` (`opinion_id=11239035`, `query="2244(b)(3)(E)"`)
    - Result: 65 matches in *Bowe v. United States* (2026), confirming the Court's holding that § 2244(b)(3)(E) bars certiorari review of circuit authorization denials for state prisoners under § 2244, whereas federal prisoners under § 2255(h) were not covered by that cross-reference.
13. `mcp_courtlistener_read_document` (`opinion_id=4709824`)
    - Result: Read full text of the Fifth Circuit's opinion in *Storey v. Lumpkin* (No. 20-70014, Aug. 6, 2021), holding that under Fifth Circuit precedent (*In re Will*, *Blackman v. Davis*), *Panetti* does not exempt second-in-time *Brady* and *Napue* claims from 28 U.S.C. § 2244(b).
