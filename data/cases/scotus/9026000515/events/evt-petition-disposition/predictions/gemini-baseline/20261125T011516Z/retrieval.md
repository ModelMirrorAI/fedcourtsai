# Retrieval Log

Mode: `forward` (`snapshot_date: 2026-11-25`, no replay clock). All retrieval stayed strictly on corpus priors and pre-petition lower-court proceedings (`uscfc`, `cafc`, `ca10`); no queries sought or surfaced any disposition or third-party forecast of SCOTUS No. 26-515.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000515" --event "evt-petition-disposition" --role predictor`
   - Resolved cell paths (`case_id: scotus/9026000515`, `event: data/cases/scotus/9026000515/events/evt-petition-disposition/event.yaml`). No transfer line.
2. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 7 GET(s), 1769472 byte(s)`
   - Returned 10 recent 2020s SCOTUS resolved priors (mostly denials under `sal-v9`).
3. `uv run fedcourts query --court scotus --citation "496 U.S. 128" --citation "439 U.S. 128" --limit 5`
   - Transfer stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows with CLI note explaining that `--citation` matches a row's own parallel reporter citations rather than cited-authority graphs.
4. `uv run fedcourts query --court scotus --judge "Taranto" --era 2020s --limit 10`
   - Failed after 180s with sidecar read timeout: `corpus service at http://127.0.0.1:8377 timed out after 180s — a slow corpus read, not a dead sidecar: ReadTimeout('timed out')` (no `ranged corpus reads` line printed).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Debra Jones v. United States"`, `court=["cafc", "uscfc"]`, `num_results=15`)
   - Failed with HTTP 429 rate-limit error (`Rate limit exceeded: 25/min. Expected available in 6 seconds.`).
2. `mcp_courtlistener_search` (`type="o"`, `case_name="Debra Jones v. United States"`, `court=["cafc", "uscfc"]`, `num_results=15`) — retry
   - Succeeded (`query_id: 79a7e053`, `count: 0`) because lower-court captions use `Jones v. United States`.
3. `mcp_courtlistener_search` (`type="o"`, `q='"Todd Murray" AND "spoliation"'`, `court=["cafc", "uscfc"]`, `num_results=10`)
   - Succeeded (`query_id: b38595ce`, `count: 3`); returned earlier published opinions in the litigation (`122 Fed. Cl. 490` (2015), `846 F.3d 1343` (Fed. Cir. 2017), etc.) and confirmed CFC docket `13-227L` (`1:13-cv-00227`).
4. `mcp_courtlistener_search` (`type="o"`, `case_name="Jones v. United States"`, `court=["cafc", "uscfc"]`, `filed_after="2022-01-01"`, `num_results=10`)
   - Succeeded (`query_id: ca6cdb96`, `count: 1`, unrelated `Kenneth Michael Jones v. United States`, No. 19-316).
5. `mcp_courtlistener_search` (`type="r"`, `court="uscfc"`, `docket_number="1:13-cv-00227"`, `entry_date_filed_after="2023-03-01"`, `entry_date_filed_before="2023-04-15"`, `num_results=10`)
   - Succeeded (`query_id: 3e4572fd`, `count: 1`); located RECAP document `id: 265550302` (`docket_id: 7503339`, ECF No. 209, filed `2023-03-29`, Judge Hertling's 54-page unreported opinion *Jones VI*, `is_available: true`).
6. `mcp_courtlistener_search` (`type="r"`, `court="cafc"`, `docket_number="24-2053"`, `num_results=5`)
   - Succeeded (`query_id: 389b7a65`, `count: 1`, `docket_id: 69786960`); returned non-available 2025 appendix filings.
7. `mcp_courtlistener_search_document` (`recap_document_id=265550302`, `query="Fourth Amendment"`, `snippet_size=500`)
   - Succeeded (`17` matches across `184,835` chars); located the CFC's Fourth Amendment "control" and plain-view analysis in *Jones VI*.
8. `mcp_courtlistener_search_document` (`recap_document_id=265550302`, `query="Rakas"`, `snippet_size=500`)
   - Succeeded (`1` match at position `149,809`); located Judge Hertling's exact *Rakas v. Illinois*, 439 U.S. 128, 143 n.12 (1978), discussion on Chief Jensen's possession of the .40 Glock (omitted from `record/documents/appendix.txt` due to the 150,000-character pipeline cap).
9. `mcp_courtlistener_read_document` (`recap_document_id=265550302`, `chunk_index=[18, 19, 20, 21, 22]`, `chunk_size=8000`)
   - Succeeded (`total_chunks: 24`); read pages 42–54 of *Jones VI* covering Officer Norton's clothing and the .40 Glock.
10. `mcp_courtlistener_read_document` (`recap_document_id=265550302`, `chunk_index=19`, `chunk_size=8000`)
    - Succeeded; read full uncompressed text of chunk 19 (pages 44–47 of *Jones VI*), confirming citations to *Byrd v. United States*, *Hicks*, *Soldal*, *Texas v. Brown*, and *Ute V*, 790 F.3d 1000 (10th Cir. 2015).
11. `mcp_courtlistener_search` (`type="o"`, `case_name="Jones v. Norton"`, `court="ca10"`, `num_results=5`)
    - Succeeded (`query_id: bde67751`, `count: 4`); verified that the Tenth Circuit panel in the related § 1983 appeal *Jones v. Norton*, 809 F.3d 564 (10th Cir. 2015), was Judges Briscoe, McKay, and Bacharach (confirming Justice Gorsuch did not sit on *Jones v. Norton* and has no recusal trigger here).

## 3. Web Searches
- None attempted.
