# Retrieval Log

All lookups executed beyond the provisioned case inputs (`record/` and `event.yaml`) and committed base-rate table (`metrics/statpack.md`) are logged below. No queries were run for *Almonor v. United States* (No. 26-163 / `scotus/9026000163`) or its disposition.

## 1. Local / Ranged Corpus CLI Lookups (`fedcourts query`)

1. **Command:** `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - **Read stats line:** `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - **Result:** Returned 10 recent resolved 2020s SCOTUS rows (confirming corpus connectivity, `sal-v9` salience metadata, and recent OT2026 cert/application resolutions through November 2026).

2. **Command:** `uv run fedcourts query --court scotus --citation "225 U.S. 347" --citation "328 U.S. 750" --citation "543 U.S. 209" --limit 10`
   - **Read stats line:** `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Result:** Returned 0 rows along with CLI note explaining that `--citation` matches a row's own parallel reporter citations rather than a citing-cases graph (`note: citations filter: only 195 row(s) in scope (scotus) carry any reporter citation at all...`).

*(Helper commands also run: `uv run fedcourts paths --court scotus --docket 9026000163 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help`.)*

## 2. CourtListener MCP Lookups

1. **`mcp_courtlistener_search`** (`type="o"`, `court="scotus"`, `case_name="Abouammo v. United States"`, `num_results=5`, `fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions", "judge"]`)
   - **Result:** Returned 2 clusters for *Abouammo v. United States* (decided `2026-06-11`, opinion by Justice Kagan, including revised combined slip opinion `opinion_id=11343328`, `cluster_id=10875833`).

2. **`mcp_courtlistener_read_document`** (`opinion_id=11343328`)
   - **Result:** Returned full slip opinion text (`31,815` chars) of *Abouammo v. United States*, No. 25-5146 (decided June 11, 2026; revised June 16, 2026). Confirmed the decision was unanimous (`9-0`) with no separate concurrences, cited *Whitfield v. United States*, 543 U.S. 209, 218 (2005), for conspiracy overt-act venue, rejected mens-rea/contemplated-effects venue inquiries, and reserved statutory venue schemes in footnote 3.

3. **`mcp_courtlistener_search`** (`type="o"`, `court="scotus"`, `q=""Tang Yuk" OR "Svoboda" OR ("conspiracy" AND "venue" AND "foreseeable")"`, `num_results=10`, `fields=["caseName", "citation", "dateFiled", "cluster_id", "judge", "snippet"]`)
   - **Result:** Returned 18 total matches (first 10 shown, with a warning that `snippet` is not a top-level field on opinion search), including *Kirk Tang Yuk v. United States*, 139 S. Ct. 342 (`2018-10-09`, `judge=""`), confirming an unadorned denial of certiorari without separate opinions.

4. **`mcp_courtlistener_search`** (`type="o"`, `court="scotus"`, `q=""Iossifov" OR ("Renteria" AND "139 S. Ct. 1326") OR ("Ebersole" AND "546 U.S. 1139")"`, `num_results=10`, `fields=["caseName", "citation", "dateFiled", "cluster_id", "judge", "opinions"]`)
   - **Result:** Returned 1 match, *Ebersole v. United States*, 546 U.S. 1139 (`2006-01-17`, `judge=""`, snippet `"C. A. 4th Cir. Certiorari denied."`), confirming no separate opinions accompanied the cert denials on this split.
