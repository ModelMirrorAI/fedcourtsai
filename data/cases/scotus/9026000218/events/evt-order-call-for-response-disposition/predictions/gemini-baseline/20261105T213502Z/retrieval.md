# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS rows (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).
2. `uv run fedcourts query --court scotus --docket-number "25-1"`
   - Transfer stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Result: Returned `scotus/73110505`, *James Skinner v. Louisiana* (No. 25-1), originating from the Supreme Court of Louisiana (`2024-KP-00142`), `distribution_count: 9`, `disposition: "denied"` on `2026-03-30`, showing overlapping counsel/amici (Jorge Benjamin Aguinaga for Louisiana; Innocence Network, Cato Institute, Two Louisiana Prisoners, Law Professors).
3. `uv run fedcourts query --court scotus --citation "577 U.S. 385" --citation "565 U.S. 73" --limit 5`
   - Transfer stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Empty result with coverage note explaining that `--citation` only matches a row's own reporter citations on ~200 SCOTUS rows.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent OT2026 denied SCOTUS rows.
5. `uv run fedcourts query --court scotus --docket-number "22-77"`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/67123792`, *David Brown v. Louisiana* (No. 22-77), `capital_case: true`, `distribution_count: 7`, `disposition: "denied"` on `2023-04-03`.
6. `uv run fedcourts query --court scotus --docket-number "25-51"`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72187113`, *Christopher Klein, Superintendent, Department of Detention Facilities for Anne Arundel County, et al. v. Charles Brandon Martin* (No. 25-51), `distribution_count: 11`, `disposition: "granted"` and `merits_judgment: "reversed"` on `2026-01-26`.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Klein v. Martin", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 1 match (`cluster_id: 10779476`, `opinion_id: 11246089`, No. 25-51, decided `2026-01-26`).
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Skinner v. Louisiana", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 5 historical matches from 1968–1969 (`393 U.S. 473`, etc.).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Robinson v. Louisiana", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 5 matches (`137 S. Ct. 328` (2016) and older cases).
4. `mcp_courtlistener_read_document(opinion_id=11246089)`
   - Result: Full text (31,498 chars) of *Klein v. Martin*, 607 U.S. ___ (Jan. 26, 2026) (per curiam).
5. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2023-01-01", q=""Brady v. Maryland" Louisiana", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 1 match (*Glossip v. Oklahoma*, `604 U.S. 226`, decided `2025-02-25`).
6. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-01-01", q=""Skinner v. Louisiana" OR "Robinson v. Louisiana" OR "25-1"", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 4 matches (unrelated opinions matching `"25-1"`).
7. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2022-01-01", q=""Brown v. Louisiana" OR "Skinner v. Louisiana" OR "Darrell Robinson" OR "Robinson v. Vannoy"", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 0 matches.
8. `mcp_courtlistener_search(type="d", court="scotus", atty_name="Jorge Benjamin Aguinaga", fields=["caseName", "docketNumber", "dateFiled", "dateTerminated"])`
   - Result: 0 matches.
9. `mcp_courtlistener_search(type="d", court="scotus", atty_name="Jo-Ann Tamila Sagar", fields=["caseName", "docketNumber", "dateFiled", "dateTerminated"])`
   - Result: 0 matches.
10. `mcp_courtlistener_search(type="o", court="scotus", citation="143 S. Ct. 886", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
    - Result: 0 matches.
