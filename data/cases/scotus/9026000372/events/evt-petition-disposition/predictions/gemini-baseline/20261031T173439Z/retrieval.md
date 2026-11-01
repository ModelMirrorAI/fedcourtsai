# Retrieval Log

## Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 24-20`
   - Transfer line: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned `scotus/69830688` (*Miriam Fuld, et al. v. Palestine Liberation Organization, et al.*, No. 24-20), granted December 6, 2024, decided June 20, 2025 (`merits_judgment: reversed`).
2. `uv run fedcourts query --court scotus --docket-number 26A141`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9526000141` (*Palestine Liberation Organization, et al. Applicants v. Mark I. Sokolow, et al.*, No. 26A141), substantive stay application filed July 30, 2026 and denied August 3, 2026 (`response_requested: false`, `referred_to_court: false`, `disposition: denied`).
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 5 recent resolved SCOTUS rows from the 2020s era (`26A499`, `26A535`, `26A532`, `26A555`, `26A556`).
4. `uv run fedcourts query --court scotus --docket-number 24-151`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72483856` (*United States v. Palestine Liberation Organization, et al.*, No. 24-151), companion merits case to *Fuld*, granted December 6, 2024 and reversed June 20, 2025.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Fuld v. Palestine Liberation Organization"`)
   - Result: Returned 2 cluster hits for *Fuld v. Palestine Liberation Organization*, 606 U.S. 1, 145 S. Ct. 2090 (decided June 20, 2025), `cluster_id: 10614322` (`opinion_id: 11080910`) and `cluster_id: 10776827` (`opinion_id: 11243414`).
2. `mcp_courtlistener_read_document` (`opinion_id=11080910`, `chunk_index=0`, `chunk_size=8000`)
   - Result: Read first 8,000 characters of the *Fuld* slip opinion syllabus, confirming *Waldman et al. v. Palestine Liberation Organization et al.* was decided together with *Fuld* and *United States v. PLO* (No. 24-151).
3. `mcp_courtlistener_read_document` (`opinion_id=11080910`, `chunk_index=1`, `chunk_size=8000`)
   - Result: Read second chunk of the *Fuld* syllabus, confirming the 9–0 judgment (Roberts, C.J., for 7 Justices; Thomas, J., concurring in the judgment, joined by Gorsuch, J., as to Part II) reversing 82 F.4th 64 (*Waldman III*) and 82 F.4th 74 (*Fuld*).
4. `mcp_courtlistener_search_document` (`opinion_id=11080910`, `query="Waldman"`)
   - Result: Returned 13 matches in *Fuld* discussing the *Waldman*/*Sokolow* procedural history and reversing 82 F.4th 64.
5. `mcp_courtlistener_search_document` (`opinion_id=11080910`, `query="mandate"`)
   - Result: Returned 1 match in *Fuld* recounting the *Sokolow* plaintiffs' motion in the Second Circuit to recall the mandate.

## Web Searches

- None attempted.
