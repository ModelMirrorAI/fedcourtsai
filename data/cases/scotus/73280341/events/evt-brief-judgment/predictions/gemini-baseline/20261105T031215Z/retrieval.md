# Retrieval Log

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --help`
   - Inspected CLI options before running structured filter queries.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Returned 10 recent 2020s granted SCOTUS rows for context on current Term dockets.

## 2. CourtListener MCP Server Calls

1. `mcp_courtlistener_search` (`type="o"`, `citation="607 U.S. 492"`) — returned 1 unrelated historical match (*Choctaw Nation v. United States*, 317 U.S. 607) because 2026 slip opinions do not yet have bound U.S. Reports page citations indexed in the `citation` field.
2. `mcp_courtlistener_search` (`type="o"`, `citation="607 U.S. 71"`) — returned 23 unrelated matches for the same reason.
3. `mcp_courtlistener_search` (`type="o"`, `citation="146 S. Ct. 1114"`) — returned 3 unrelated matches.
4. `mcp_courtlistener_search` (`type="o"`, `citation="161 F.4th 604"`) — returned 0 matches under the citation filter.
5. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Mirabelli v. Bonta"`) — returned 1 match: *Mirabelli v. Bonta*, cluster_id `10802600`, opinion_id `11269328` (decided March 2, 2026).
6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Bost v. Illinois"`) — returned 2 matches: *Bost v. Illinois Bd. of Elections*, cluster_ids `10774569` (opinion_id `11241154`) and `10774341` (opinion_id `11240921`, decided January 14, 2026).
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="First Choice Women"`) — returned 1 match: *First Choice Women's Resource Centers, Inc. v. Davenport*, cluster_id `10850133`, opinion_id `11317513` (decided April 29, 2026).
8. `mcp_courtlistener_search` (`type="o"`, `court="ca9"`, `case_name="International Partners for Ethical Care"`) — returned 2 matches: the Ninth Circuit panel opinion (`cluster_id: 10641209`, `opinion_id: 11107796`, filed July 25, 2025) and the Ninth Circuit order denying rehearing en banc with the dissents of Judges VanDyke and Tung (`cluster_id: 10748300`, `opinion_id: 11214880`, filed December 5, 2025).
9. `mcp_courtlistener_read_document` (`opinion_id=11269328`, `chunk_index=[0, 1, 2]`) — read the per curiam opinion, Justice Barrett's concurrence, and the start of Justice Kagan's dissent in *Mirabelli v. Bonta* (2026).
10. `mcp_courtlistener_read_document` (`opinion_id=11241154`, `chunk_index=0`) — returned `"No text is available for this document"` on the revision notice cluster for *Bost*.
11. `mcp_courtlistener_read_document` (`opinion_id=11317513`, `chunk_index=0`) — read the syllabus of *First Choice Women's Resource Centers, Inc. v. Davenport* (2026).
12. `mcp_courtlistener_read_document` (`opinion_id=11214880`, `chunk_index=[0, 1, 2, 3]`) — read the order denying rehearing en banc and Judge VanDyke's dissent in *International Partners for Ethical Care Inc. v. Ferguson* (9th Cir. Dec. 5, 2025).
13. `mcp_courtlistener_read_document` (`opinion_id=11269328`, `chunk_index=[3, 4, 5]`) — read the remainder of *Mirabelli v. Bonta* (2026).
14. `mcp_courtlistener_read_document` (`opinion_id=11240921`, `chunk_index=0`) — read the syllabus of *Bost v. Illinois State Board of Elections* (2026).
15. `mcp_courtlistener_read_document` (`opinion_id=11317513`, `chunk_index=1`) — read the vote lineup and opening of Justice Gorsuch's opinion in *First Choice Women's Resource Centers, Inc. v. Davenport* (2026).
16. `mcp_courtlistener_read_document` (`opinion_id=11214880`, `chunk_index=[4, 5, 6, 7, 8]`) — read the remainder of Judge VanDyke's dissent and the entirety of Judge Tung's dissent from the denial of rehearing en banc in *International Partners for Ethical Care Inc. v. Ferguson* (9th Cir. Dec. 5, 2025), including the portions cut by the 150 KB cap in `record/documents/petition.txt`.
17. `mcp_courtlistener_read_document` (`opinion_id=11240921`, `chunk_index=1`) — read the vote lineup and opening of Chief Justice Roberts's opinion in *Bost v. Illinois State Board of Elections* (2026).
18. `mcp_courtlistener_read_document` (`opinion_id=11240921`, `chunk_index=[7, 8, 9, 10]`) — read Justice Jackson's dissent (joined by Justice Sotomayor) in *Bost v. Illinois State Board of Elections* (2026).
19. `mcp_courtlistener_read_document` (`opinion_id=11240921`, `chunk_index=[5, 6]`) — read Justice Barrett's concurrence in the judgment (joined by Justice Kagan) in *Bost v. Illinois State Board of Elections* (2026).

## 3. Web Searches

None.
