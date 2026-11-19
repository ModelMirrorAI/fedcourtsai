# Retrieval Log

All lookups beyond the provisioned case inputs (`record/` and `events/evt-petition-disposition/event.yaml`) are listed below. No lookup queried the outcome, subsequent history, or external forecasts of `scotus/9026000110` (*Tedford's Tenancy, LLC v. City of New York*).

## `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9026000110" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Transfer line: none (path resolution and CLI help).
   - Result: resolved canonical case/event paths and listed structured `fedcourts query` flags.

2. `uv run fedcourts query --court scotus --docket-number 26-107`
   - Transfer line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: returned 1 row — companion petition `scotus/9026000107` (*Garnell Walls v. Prince George's County, Maryland, et al.*, `originating_court: "ca4"`, `originating_docket_number: "25-1121"`, `disposition: "denied"`, `date_cert_denied: "2026-11-09"`, `distribution_count: 2`, `has_opinion: false`, `salience_score: 0.0334`, `salience_version: "sal-v8"`).

3. `uv run fedcourts query --court scotus --citation "594 U.S. 474" --citation "588 U.S. 180" --citation "144 S. Ct. 264"`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: returned 0 rows with note that only 195 SCOTUS rows in scope carry parallel reporter citations in the `citations` column.

4. `uv run fedcourts query --court scotus --party "74 Pinehurst" --party "G-Max" --party "Community Housing Improvement" --filed-before 2026-07-01`
   - Transfer line: none (CLI argument error, Exit Code 2: `No such option: --party`).
   - Result: error message displaying valid `fedcourts query` options.

5. `uv run fedcourts query --court scotus --docket-number 22-1130`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: returned 1 row — prior New York Rent Stabilization Law takings petition `scotus/68263638` (*74 Pinehurst LLC, et al. v. New York, et al.*, `disposition: "denied"`, `date_cert_denied: "2024-02-20"`, `distribution_count: 13`, `salience_score: 0.4168`, `salience_version: "sal-v8"`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca4", case_name="Walls v. Prince George's County", fields=["caseName", "court_id", "dateFiled", "docketNumber", "cluster_id", "opinions", "snippet"], num_results=5)`
   - Result: `count: 0` (default published-status filter omitted the Fourth Circuit's unpublished per curiam opinion).

2. `mcp_courtlistener_search(type="o", court="scotus", case_name="74 Pinehurst", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions", "snippet"], num_results=5)`
   - Result: `count: 0` (default status filter omitted `Relating-to` order statements).

3. `mcp_courtlistener_search(type="o", court="scotus", q=""74 Pinehurst"", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions", "snippet"], num_results=5)`
   - Result: `count: 0` (default status filter omitted `Relating-to` order statements).

4. `mcp_courtlistener_search(type="o", court="scotus", q="Pinehurst", stat_Published=true, stat_Relating-to=true, fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions", "snippet"], num_results=5)`
   - Result: `count: 6`, including *74 Pinehurst LLC v. New York*, Nos. 22-1130 & 22-1170 (`cluster_id: 9476534`, `opinion_id: 9942065`, filed `2024-02-20`, Statement of Thomas, J., respecting the denials of certiorari).

5. `mcp_courtlistener_read_document(opinion_id=9942065)`
   - Result: full text (`2,956` chars) of Justice Thomas's February 20, 2024 statement respecting the denials of certiorari in *74 Pinehurst LLC v. New York* and *335-7 LLC v. City of New York*, noting the importance of challenges to New York City's rent-stabilization laws alongside the pleading/vehicle complications that precluded review there.

6. `mcp_courtlistener_search(type="o", court="ca4", q=""Prince George's County" Walls", stat_Published=true, stat_Unpublished=true, fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"], num_results=5)`
   - Result: `count: 40`, top match *Garnell Walls v. Prince George's County*, No. 25-1121 (`cluster_id: 10799867`, `opinion_id: 11266543`, filed `2026-02-23`, unpublished per curiam).

7. `mcp_courtlistener_read_document(opinion_id=11266543)`
   - Result: full text (`24,435` chars) of the Fourth Circuit's decision below in companion case *Garnell Walls v. Prince George's County*, No. 25-1121 (4th Cir. Feb. 23, 2026), confirming its cleaner federal Rule 12(b)(6) posture, express prudential-ripeness footnote, actual agency waiver denial, and absence of any alternative merits holding.

## Web Searches

None attempted.
