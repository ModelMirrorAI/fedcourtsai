# Retrieval Log

Mode: `forward` (`snapshot_date: 2026-11-27`). All lookups beyond the provisioned case record (`data/cases/scotus/9026000584/record/`) and committed `metrics/statpack.md` / `metrics/amicus-line.json` are recorded below.

## 1. Corpus CLI (`fedcourts`) Lookups

1. `uv run fedcourts query --help`
   - Inspected CLI filter flags and closed vocabularies (`no ranged corpus reads` transfer line printed).
2. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Returned 10 recent 2020s SCOTUS resolved priors to inspect schema and live-channel field population.
3. `uv run fedcourts query --court scotus --citation "576 U.S. 200" --citation "596 U.S. 243" --limit 5`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows with coverage note explaining that only 195 SCOTUS rows in scope carry parallel reporter citations.
4. `uv run fedcourts query --docket-number 25-107`
   - Usage error (`--docket-number needs --court`); no corpus reads executed. Re-issued below with `--court scotus`.
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Returned 10 recent 2020s SCOTUS cert/interim grants (e.g., *Robinhood Markets v. Sodha*, No. 25-944; *Goldman Sachs Bank USA v. Brown*, No. 25-1408).
6. `uv run fedcourts query --court scotus --docket-number 25-107 --full`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned `scotus/73274790`, *Leah Gilliam v. David Gerregano, Commissioner, Tennessee Department of Revenue, et al.*, No. 25-107 (originating from Supreme Court of Tennessee, Middle Division): filed `2025-07-29`, five amicus filers on record, `distribution_count: 2`, `cvsg_date: null`, `disposition: "denied"` on `2025-12-08`, `has_opinion: false`.
7. `uv run fedcourts amicus-line-fit --before-term 2026`
   - Exited with code 1 (`the corpus database is missing at corpus/corpus.db`); relied instead on `context.json`'s frozen `cert_amicus_line` and committed `metrics/amicus-line.json`.
8. `uv run fedcourts open-events --court scotus | head -n 30`
   - Usage message (`Name the case by exactly one of --docket and --docket-number`); no transfer line.
9. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 35`
   - Transfer: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - Checked 35 recently granted OT2025/OT2026 SCOTUS matters to verify whether any pending merits grant involves government speech (*Walker* / *Matal* / *Shurtleff*) that could trigger a hold-and-GVR; confirmed none does.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="d", court="ca7", case_name="Nichols v. Boardman", num_results=5)` (`query_id: "1140c7e9"`)
   - Returned 1 docket: *M J Nichols Company, Inc. v. Kristina Boardman*, No. 26-1043 (`docket_id: 73196733`, `dateFiled: "2026-01-12"`, `dateTerminated: null`), confirming the Seventh Circuit vanity-plate appeal remains pending.
2. `mcp_courtlistener_search(type="o", court="ca7", case_name="Nichols", filed_after="2026-09-01", num_results=5)` (`query_id: "717f6c1a"`)
   - Returned 0 opinions, confirming no Seventh Circuit decision has issued in *Nichols v. Boardman* since the September 17, 2026 oral argument.
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Gilliam v. Gerregano", num_results=5)` (`query_id: "d3a95db6"`)
   - Returned 0 SCOTUS opinions/statements under that case name.
4. `mcp_courtlistener_search(type="d", court="scotus", case_name="Gilliam v. Gerregano", num_results=5)` (`query_id: "2a98e75a"`)
   - Returned 0 RECAP dockets on SCOTUS (expected, as SCOTUS cert dockets without opinions are not in RECAP).
5. `mcp_courtlistener_search(type="o", q=""Gilliam v. Gerregano"")` (`query_id: "c10264f9"`)
   - Returned 5 opinions citing *Gilliam v. Gerregano*, topped by the decision below in this case (*Curtis Whateley v. Gerald Lackey*, CA4 No. 25-1751, `cluster_id: 10938011`, filed `2026-07-31`).
6. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 73196733, "fields": ["entry_number", "date_filed", "description"]}, num_results=30)` (`query_id: "6099fced"`)
   - Returned RECAP briefing entries (through April 15, 2026) in *M J Nichols Company, Inc. v. Kristina Boardman* (CA7 No. 26-1043).
7. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-12-05", filed_before="2025-12-15", num_results=20)` (`query_id: "83a2d673"`)
   - Returned 1 opinion/statement on the December 8, 2025 order list (*Doe v. Dynamic Physical Therapy, LLC*, No. 25-180), confirming that certiorari in *Gilliam v. Gerregano*, No. 25-107 was denied on December 8, 2025 without any published dissent or statement respecting denial.
8. `mcp_courtlistener_search(type="oa", court="ca7", docket_number="26-1043", num_results=5)` (`query_id: "f1ceebef"`)
   - Confirmed oral argument in *M J Nichols Company, Inc. v. Kristina Boardman*, No. 26-1043 (7th Cir.), took place on `2026-09-17`.

## 3. Web Searches

None attempted (avoided general web search to eliminate any risk of encountering third-party forecasts or prediction-market odds on this pending petition).
