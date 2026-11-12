# Retrieval Log

## `fedcourts` CLI Calls

1. Path resolution and CLI help (no corpus transfer):
   - `uv run fedcourts paths --court "scotus" --docket "9026000624" --event "evt-petition-arrival-disposition" --role predictor`
   - `uv run fedcourts query --help`

2. Prior petition in this same litigation (`No. 25-640`):
   - Command: `uv run fedcourts query --court scotus --docket-number 25-640`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned: 1 row (`scotus/73279475`, *Randall Williams, et al. v. Charleston County Sheriff's Office, et al.*, filed `2025-12-03`, `distribution_count: 2`, `disposition: "gvr"`, `date_cert_granted: "2026-03-23"`).

3. Recent 2020s SCOTUS GVR priors:
   - Command: `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
   - Returned: 10 GVR rows from October–November 2026 (`25-442`, `25-1348`, `26-5123`, `25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-901`, `25-918`).

4. Invalid flag attempt (`--party` is not a `fedcourts query` option):
   - Command: `uv run fedcourts query --court scotus --party "Sheriff" --era 2020s --limit 15`
   - Result: Failed (exit code 2, `No such option: --party`; no corpus read).

5. *Galette v. New Jersey Transit Corp.* docket prior (`No. 24-1021`):
   - Command: `uv run fedcourts query --court scotus --docket-number 24-1021`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/72143460`, *Cedric Galette v. New Jersey Transit Corporation*, granted `2025-07-03`, `merits_decided: "2026-03-04"`, `merits_judgment: "reversed"`, `cvsg_date: null`).

6. GVR orders on or before March 23, 2026:
   - Command: `uv run fedcourts query --court scotus --disposition gvr --decided-before 2026-03-24 --limit 10`
   - Stderr: `note: replay cutoff 2026-03-24 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term` and `ranged corpus reads: 54 GET(s), 14155776 byte(s)`
   - Returned: 10 GVR rows up to `2026-03-23` (including `scotus/73279475`, `25-640`).

7. 2020s SCOTUS summary-reversal priors:
   - Command: `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 1132 GET(s), 296484864 byte(s)`
   - Returned: 0 rows.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Galette v. New Jersey Transit"`, `num_results=5`):
   - Returned 1 result: *Galette v. New Jersey Transit Corp.*, `cluster_id=10803604`, `opinion_id=11270334`, `dateFiled="2026-03-04"`, `docketNumber="24-1021"`.

2. `mcp_courtlistener_search` (`type="o"`, `q='"Galette" "New Jersey Transit"'`):
   - Returned 12 results citing or deciding *Galette*, including *Pennsylvania Game Commission v. Thomas E Proctor Heirs Trust* (`opinion_id=11405374`, 3d Cir. `2026-07-31`), *Nilsen v. University of Washington* (`opinion_id=11414911`, 9th Cir. `2026-08-13`), and *Gannon v. Texas Dept of Trans* (`opinion_id=11341842`, 5th Cir. `2026-06-12`).

3. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 68399001, "fields": ["entry_number", "date_filed", "description"]}`, `num_results=30`):
   - Returned the 30 most recent docket entries in Fourth Circuit No. `24-1238` up to `2026-08-11`, confirming the post-GVR supplemental briefing order (`2026-04-28`) and supplemental briefs (`2026-05-19`, `2026-05-20`), and confirming that entries 64, 65, 73, and 76 (`2026-07-15` to `2026-08-11`) have blank `description` strings in RECAP.

4. `mcp_courtlistener_read_document` (`opinion_id=11270334`, `chunk_index=[0, 1, 2, 3]`, `chunk_size=8000`):
   - Read chunks 0–3 of *Galette v. New Jersey Transit Corp.* (syllabus and opening sections).

5. `mcp_courtlistener_search_document` (`opinion_id=[11405374, 11414911]`, `query="Galette"`, `snippet_size=600`):
   - Returned 20 snippets (of 45 matches) from *Proctor Heirs* (3d Cir.) and 20 snippets (of 25 matches) from *Nilsen* (9th Cir.) showing how both circuits integrated *Galette* into their existing arm-of-the-state tests.

6. `mcp_courtlistener_search` (`type="o"`, `court="ca11"`, `docket_number="25-12737"`):
   - Returned 0 results (checking unpublished Eleventh Circuit decision *Wright* cited in Petition's Table of Authorities).

7. `mcp_courtlistener_read_document` (`opinion_id=11270334`, `chunk_index=[4, 5, 6, 7]`, `chunk_size=8000`):
   - Read chunks 4–7 of *Galette v. New Jersey Transit Corp.* (including slip op. pp. 11–14 and Footnote 5 reserving unincorporated entities).

8. `mcp_courtlistener_search_document` (`opinion_id=11341842`, `query="Galette"`, `snippet_size=600`):
   - Returned 1 snippet from *Gannon v. Texas Dept of Trans* (5th Cir.).

9. `mcp_courtlistener_search` (`type="o"`, `q='"Wright" "Galette" "State Attorney"'`):
   - Returned 0 results.

10. `mcp_courtlistener_search` (`type="o"`, `court="ca10"`, `docket_number="23-1135"`):
    - Returned 2 results (*Griffith v. El Paso County, Colorado*, 139 F.4th 1183, `opinion_id=10802107`), checking whether the recent GVR in `25-442` involved county sheriff arm-of-the-state immunity.

11. `mcp_courtlistener_search` (`type="o"`, `court="ca7"`, `docket_number="23-2277"`):
    - Returned 1 result (*Randall Martin v. Robert Goldsmith*, `opinion_id=11234146`), checking recent GVR `25-1348`.

12. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="25-442"`):
    - Returned 0 results.

13. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `q='"Cromer v. Brown" "arm of the state"'`):
    - Returned 6 results, led by *Cromer v. Brown*, 88 F.3d 1315 (4th Cir. 1996) (`opinion_id=721462`).

14. `mcp_courtlistener_search_document` (`opinion_id=[10802107, 721462]`, `query="arm of the state"`, `snippet_size=500`):
    - Returned 0 matches in *Griffith* (confirming `25-442` was unrelated) and 8 matches in *Cromer v. Brown* (reviewing *Cromer*'s holding on South Carolina sheriffs and the State Insurance Reserve Fund).

## Web Searches

- None attempted.
