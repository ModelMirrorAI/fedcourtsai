# Retrieval Log (`scotus/9026000648` — `evt-petition-arrival-disposition`)

Mode: `forward` (`DECIDED_BEFORE` unset; `cutoff` in `context.json` = `2026-11-18` for arrival conditioning only). Consistent with the prompt rules, no query sought this case's own disposition, post-docketing history, or any third-party forecast of this case.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000648" --event "evt-petition-arrival-disposition" --role predictor`
   - Stderr `ranged corpus reads`: none.
   - Returned resolved case/corpus/event paths (`scotus/9026000648`, `corpus/corpus.db`, `event.yaml`).
2. `uv run fedcourts query --help`
   - Stderr `ranged corpus reads`: none.
   - Returned CLI option documentation for `fedcourts query`.
3. `uv run fedcourts open-events --help`
   - Stderr `ranged corpus reads`: none.
   - Returned CLI option documentation for `fedcourts open-events`.
4. `uv run fedcourts query --court scotus --q "Energy Policy and Conservation Act" --limit 20`
   - Failed (exit code 2): `No such option: --q` (`fedcourts query` is a structured filter and does not accept free-text search flags). Stderr `ranged corpus reads`: none.
5. `uv run fedcourts query --court scotus --q "6297" --limit 20`
   - Failed (exit code 2): `No such option: --q`. Stderr `ranged corpus reads`: none.
6. `uv run fedcourts query --court scotus --counsel "Sarah O'Beirne Jorgensen" --limit 20`
   - Failed (exit code 2): `No such option: --counsel`. Stderr `ranged corpus reads`: none.
7. `uv run fedcourts query --court scotus --citation "146 S. Ct. 2705" --limit 5`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (`note:` explained only 195 SCOTUS rows carry reporter citations and `--citation` matches a case's own parallel cites rather than cited authorities).
8. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
   - Stderr: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   - Returned 12 recent 2020s granted SCOTUS rows (including OT2026 cert grants `25-944`, `26-239`, `25-1408`, `26-12`, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`, and substantive applications), confirming `sal-v8` scoring metadata, `distribution_count` conventions, and current Solicitor General (`D. John Sauer`) filings.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="American Gas Association v. Department of Energy", fields=["caseName", "docketNumber", "dateFiled", "citation", "snippet"], num_results=5)`
   - `query_id`: `a2a76587` — `count: 0`, `results: []`.
2. `mcp_courtlistener_search(type="r", court="cadc", docket_number="26-7050", fields=["caseName", "docketNumber", "dateFiled", "docket_id"], num_results=5)`
   - `query_id`: `dd5b828c` — `count: 1`: matched `National Association of Home Builders of the Unit v. DC`, D.C. Cir. No. `26-7050`, `dateFiled: "2026-04-20"`, `docket_id: 73213442`.
3. `mcp_courtlistener_search(type="d", court="scotus", case_name="Rinnai America", fields=["caseName", "docketNumber", "dateFiled", "docket_id"], num_results=5)`
   - `query_id`: `a10cb2e1` — `count: 0`, `results: []` (confirmed no companion SCOTUS cert docket in *Rinnai America Corp. v. South Coast AQMD* yet).
4. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=73213442, fields=["id", "case_name", "date_filed", "date_terminated", "panel_str"])`
   - Returned `{"id": 73213442, "panel_str": "FYP, BNG, ARR", "date_filed": "2026-04-20", "date_terminated": null, "case_name": "National Association of Home Builders of the Unit v. DC"}` — confirming the D.C. Circuit EPCA preemption appeal argued September 8, 2026 before Judges Pan, Garcia, and Randolph remains pending undecided.
5. `mcp_courtlistener_search(type="o", court="scotus", q=""American Gas Association" "Department of Energy"", fields=["caseName", "docketNumber", "dateFiled", "citation", "snippet"], num_results=5)`
   - `query_id`: `1304d4b8` — `count: 0`, `results: []`.
6. `mcp_courtlistener_search(type="o", court=["cadc", "ca4", "ca7", "ca9", "ca10"], q=""6297(c)"", filed_after="2024-01-01", fields=["caseName", "court_id", "docketNumber", "dateFiled", "citation", "snippet"], num_results=10)`
   - `query_id`: `f0995371` — `count: 0`, `results: []`.
7. `mcp_courtlistener_search(type="o", court=["cadc", "ca4", "ca7", "ca9", "ca10"], q=""6297" "Energy Policy and Conservation Act"", filed_after="2024-01-01", fields=["caseName", "court_id", "docketNumber", "dateFiled", "citation", "snippet"], num_results=10)`
   - `query_id`: `28cda975` — `count: 0`, `results: []`.
8. `mcp_courtlistener_search(type="o", court="scotus", q=""6297" "Energy Policy and Conservation Act"", fields=["caseName", "docketNumber", "dateFiled", "citation", "snippet"], num_results=10)`
   - `query_id`: `52a62951` — `count: 0`, `results: []`.
9. `mcp_courtlistener_search(type="o", court="scotus", q=""Energy Policy and Conservation Act"", fields=["caseName", "docketNumber", "dateFiled", "citation", "snippet"], num_results=10)`
   - `query_id`: `8bdd5fc9` — `count: 17`: returned historical SCOTUS opinions mentioning EPCA (*Tully v. Mobil Oil Corp.*, *Puerto Rico Dep't of Consumer Affairs v. Isla Petroleum Corp.*, *Massachusetts v. EPA*, etc.), confirming SCOTUS has never issued a merits opinion construing EPCA's appliance preemption provision, 42 U.S.C. § 6297(c).

## 3. Web Searches

None attempted.
