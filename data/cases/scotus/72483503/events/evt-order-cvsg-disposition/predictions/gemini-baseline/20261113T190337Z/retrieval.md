# Retrieval Log

All lookups beyond the provisioned inputs (`data/cases/scotus/72483503/record/`, `event.yaml`, `metrics/statpack.md`, and `schemas/*.json`) are recorded below. No queries were made for *Parker-Hannifin Corp. v. Johnson* (No. 24-1030) post-cutoff docket history, filings, or disposition, and no web searches were performed.

## 1. `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "72483503" --event "evt-order-cvsg-disposition" --role predictor`
   - Local path resolution only (no corpus transfer).
2. `uv run fedcourts query --help` (invoked twice while inspecting CLI flags)
   - Help output only (no corpus transfer).
3. `uv run fedcourts query --court scotus --citation "595 U.S. 170" --citation "145 S. Ct. 1020" --decided-before 2025-07-01`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (printed note that reporter citations are sparsely populated on live-ingested SCOTUS rows and recommended `--court` / `--disposition` / `--era` for priors and CourtListener MCP for known-case cites).
4. `uv run fedcourts query --court scotus --docket-number 23-1007 --decided-before 2025-07-01`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: 1 row returned (`scotus/69566662`, *Casey Cunningham, et al. v. Cornell University, et al.*, No. 23-1007, cert granted `2024-10-04`, merits decided `2025-04-17`, reversed).
5. `uv run fedcourts query --court scotus --docket-number 24-620 --decided-before 2025-07-01`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 0 rows returned under `--decided-before 2025-07-01` (*Pizarro v. Home Depot, Inc.*, cited as pending in the petition at p. 22; docket of the clock's own Term or unresolved by cutoff excluded).
6. `uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025-07-01 --limit 15`
   - Transfer: `ranged corpus reads: 103 GET(s), 26935296 byte(s)`
   - Result: 15 rows of granted SCOTUS petitions/applications resolved on or before `2025-06-30`, including CVSG grants `24-171` (*Cox Communications*), `24-345` (*FS Credit Opportunities*), `23-1209` (*M & K Employee Solutions*, ERISA MPPAA withdrawal liability), and `23-1197` (*Landor*), showing post-CVSG conference distributions (`distribution_count` 2–3).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2025-07-01 --limit 10`
   - Transfer: `ranged corpus reads: 90 GET(s), 23527424 byte(s)`
   - Result: 10 rows of denied SCOTUS petitions resolved on `2025-06-30`, including CVSG denials `23-1213` (*Mulready v. PCMA*) and `23-1360` (*Fiehler v. Mecklenburg*), likewise confirming post-CVSG conference distributions.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Cunningham v. Cornell University", filed_before="2025-07-01", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Result: `count: 0` (CourtListener indexed `"University"` as `"Univ."`).
2. `mcp_courtlistener_search(type="o", court="ca9", case_name="Anderson v. Intel", filed_before="2025-07-01", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Result: `count: 1` — *Winston Anderson v. Intel Corporation Investment Policy Committee*, `137 F.4th 1015`, No. 22-16268, filed `2025-05-22` (`cluster_id: 10589949`, `opinion_id: 11056537`).
3. `mcp_courtlistener_search(type="o", court="scotus", q='"Cunningham" "Cornell" ERISA', filed_before="2025-07-01", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Result: `count: 2` — *Cunningham v. Cornell Univ.*, `604 U.S. 693`, `145 S. Ct. 1020`, No. 23-1007, filed `2025-04-17` (`opinion_id: 10847067` and preliminary print `11243443`).
4. `mcp_courtlistener_search_document(opinion_id=11056537, query="Parker-Hannifin", snippet_size=400)`
   - Result: `match_count: 0` in *Anderson v. Intel*.
5. `mcp_courtlistener_search_document(opinion_id=11056537, query="meaningful benchmark", snippet_size=400)`
   - Result: `match_count: 10` (10 excerpts returned from Judge Miller's majority opinion and Judge Berzon's concurrence on the role of "meaningful benchmark" comparators in ERISA duty-of-prudence claims).
6. `mcp_courtlistener_search_document(opinion_id=11056537, query="Johnson", snippet_size=400)`
   - Result: `match_count: 0` in *Anderson v. Intel*.
7. `mcp_courtlistener_search_document(opinion_id=10847067, query="motion to dismiss", snippet_size=500)`
   - Result: `match_count: 6` in *Cunningham v. Cornell Univ.* (majority discussion of Rule 12(b)(6) safeguards and Justice Alito's concurrence on ERISA discovery costs).
8. `mcp_courtlistener_search_document(opinion_id=10847067, query="Alito", snippet_size=500)`
   - Result: `match_count: 5` confirming Justice Alito's concurrence joined by Justices Thomas and Kavanaugh.
9. `mcp_courtlistener_search(type="o", court="ca6", case_name="England v. DENSO", filed_before="2025-07-01", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Result: `count: 1` — *Martha England v. DENSO Int'l Am. Inc.*, `136 F.4th 632`, No. 24-1360, filed `2025-05-06` (`cluster_id: 10534897`, `opinion_id: 11001485`).
10. `mcp_courtlistener_search_document(opinion_id=11001485, query="Parker-Hannifin", snippet_size=500)`
    - Result: `match_count: 3` showing the Sixth Circuit citing *Johnson v. Parker-Hannifin Corp.*, 122 F.4th 205, 216 (6th Cir. 2024), alongside *Forman* and *Smith v. CommonSpirit Health* for the rule that financial-metric imprudence claims usually require a "meaningful benchmark."

## 3. Web Searches

None attempted.
