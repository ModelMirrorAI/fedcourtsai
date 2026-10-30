# Retrieval Log

## 1. Corpus CLI (`fedcourts`) Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9026000098" --event "evt-order-call-for-response-disposition" --role predictor`
   - Result: Resolved `case_id` (`scotus/9026000098`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Result: Displayed structured query flags and usage instructions.
3. `uv run fedcourts query --court scotus --decided-before 2026-08-27 --limit 20`
   - Transfer line: `ranged corpus reads: 37 GET(s), 9633792 byte(s)`
   - Result: Returned 20 resolved SCOTUS priors prior to 2026-08-27 across cert and application dockets.
4. `uv run fedcourts query --court scotus --docket-number 25-600 --decided-before 2026-08-27`
   - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned 1 resolved OT2025 cert petition (`scotus/73279045`, *Beaudoin v. Baker*, denied 2026-01-12).
5. `uv run fedcourts query --court scotus --judge "Tashima" --decided-before 2026-08-27 --limit 10`
   - Transfer line: `ranged corpus reads: 641 GET(s), 167968768 byte(s)`
   - Result: Returned 0 matching SCOTUS rows (live-channel SCOTUS rows do not populate the judge list).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `filed_before="2026-08-27"`, `q='"20507(i)" "statewide" OR "voter list" OR "Bellows" OR "Benson"'`)
   - Result: Returned 56 lower-court opinions discussing 52 U.S.C. § 20507(i), including *United States v. Benson* (6th Cir. June 24, 2026), *PILF v. Secretary Commonwealth of Pennsylvania* (3d Cir. Apr. 29, 2025), *PILF v. Benson* (6th Cir. May 6, 2025), *PILF v. Bellows* (1st Cir. Feb. 2, 2024), and recent district court decisions.
2. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `filed_before="2026-08-27"`, `q='"Public Interest Legal Foundation" OR "Voter Reference Foundation" OR "Bellows" OR "Torrez" OR "Benson"'`)
   - Result: 0 SCOTUS docket results.
3. `mcp_courtlistener_read_document` (`opinion_id=11421360`, `chunk_index=0`)
   - Result: Read chunk 0 of *PILF v. Meagan Wolfe* (W.D. Wis. Aug. 18, 2026) discussing Wisconsin's voter list fees under the NVRA.
4. `mcp_courtlistener_search_document` (`opinion_id=10879719`, `query="20507"`)
   - Result: Returned HTTP 404 because `10879719` was the `cluster_id` rather than `opinion_id` for *United States v. Benson*.
5. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10879719`, `fields=["id", "case_name", "date_filed", "sub_opinions"]`)
   - Result: Resolved `sub_opinions` to `opinion_id=11347238` for *United States v. Jocelyn Benson* (6th Cir. June 24, 2026).
6. `mcp_courtlistener_read_document` (`opinion_id=11347238`, `chunk_index=0`)
   - Result: Read chunk 0 of *United States v. Benson* (6th Cir. June 24, 2026).
7. `mcp_courtlistener_search_document` (`opinion_id=11347238`, `query="Nago"`)
   - Result: 0 matches in *United States v. Benson*.
8. `mcp_courtlistener_search_document` (`opinion_id=11347238`, `query="20507"`)
   - Result: 6 matches in *United States v. Benson* discussing 52 U.S.C. § 20507(i) and *PILF v. Bellows*.
9. `mcp_courtlistener_search` (`type="o"`, `filed_before="2026-08-27"`, `q='"Voter Reference Foundation" "Torrez"'`)
   - Result: Returned *Voter Reference Foundation v. Torrez* (10th Cir. Nov. 25, 2025, `opinion_id=11208775`).
10. `mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, with `q="Torrez"`, `q="Bellows"`, `q="Voter Reference Foundation"`)
    - Result: Failed validation error (`q` extra input not permitted on `dockets` endpoint).
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_before="2026-08-27"`, `q='"Bellows" OR "Torrez" OR "Voter Reference Foundation" OR "Public Interest Legal Foundation"'`)
    - Result: Returned unrelated SCOTUS opinions matching "Torrez" or "Bellows"; no SCOTUS opinions on the NVRA voter-list cases.
12. `mcp_courtlistener_read_document` (`opinion_id=11208775`, `chunk_index=[0, 1]`, `[2, 3]`, `[4, 5, 6]`, `[7, 8, 9, 10]`)
    - Result: Read full text of *Voter Reference Foundation, LLC v. Torrez* (10th Cir. Nov. 25, 2025), including footnote 17 confirming that New Mexico waived any argument on whether the requested voter data concerned the implementation of relevant programs and activities under § 20507(i)(1).
13. `mcp_courtlistener_read_document` (`opinion_id=11408389`, `chunk_index=0`) & `mcp_courtlistener_search_document` (`opinion_id=11408389`, `query="Nago"` and `query="20507"`)
    - Result: Read chunk 0 and snippets of *United States v. Monica H. Evans* (D.D.C. July 24, 2026) comparing Title III of the Civil Rights Act of 1960, HAVA, and NVRA § 20507(i).

## 3. Web Searches
- None.
