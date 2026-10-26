# Retrieval Log

## 1. Local Corpus Queries (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9026000231 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --docket-number 25-7193 --include-open --full`
  - `ranged corpus reads: 2 GET(s), 524288 byte(s)`
  - Retrieved the corpus record for *Jesus Ramiro Gomez v. United States*, No. 25-7193 (9th Cir. en banc decision cited in the petition and below; certiorari denied May 18, 2026).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
  - `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
  - Surveyed recent OT2026/2020s granted SCOTUS cases for context on current Term grants and pending docket composition.
- `uv run fedcourts query --court scotus --docket-number 26-231 --include-open --full`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Checked the corpus metadata row for *Mario Delaine v. United States*, No. 26-231.
- `uv run fedcourts query --court scotus --docket-number 25-6076 --include-open --full`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Checked docket serial 25-6076 (*Martin Ponce Ramirez v. Leo Quiroz*).

*(Note: Four initial `fedcourts query` invocations using an unsupported `--q` flag exited with usage error code 2 and performed no corpus reads.)*

## 2. CourtListener MCP Lookups

- `mcp_courtlistener_search(type="d", court="scotus", case_name="Sheely", fields=["caseName", "docketNumber", "dateFiled"])` — checked whether a Supreme Court cert petition had been docketed in *Sheely* (0 results).
- `mcp_courtlistener_search(type="d", court="scotus", case_name="Sjodin", fields=["caseName", "docketNumber", "dateFiled"])` — checked whether a Supreme Court cert petition had been docketed in *Sjodin* (0 results).
- `mcp_courtlistener_search(type="o", court="ca11", case_name="Sheely", fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])` — located the Eleventh Circuit's published decision in *United States v. Thomas Sheely, Jr.*, No. 24-13967 (11th Cir. Aug. 13, 2026) (`opinion_id`: `11415121`, `cluster_id`: `10947535`).
- `mcp_courtlistener_search(type="o", court="ca9", case_name="Gomez", q="Borden", filed_after="2026-01-01", num_results=5)` — located the Ninth Circuit's en banc opinion in *United States v. Gomez*, No. 23-435 (9th Cir. Jan. 13, 2026) (`opinion_id`: `11240375`, `cluster_id`: `10773790`).
- `mcp_courtlistener_read_document(opinion_id=11415121)` — read the full text of *United States v. Thomas Sheely, Jr.*, No. 24-13967 (11th Cir. Aug. 13, 2026) (majority opinion by Judge Lagoa and concurring opinion by Judge Rosenbaum analyzing Fla. Stat. § 784.041(1) and *Borden v. United States*).

## 3. Web Searches

- None.
