# Retrieval Log

## Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000457 --event evt-petition-disposition --role predictor`
   - No ranged corpus reads (local path resolution).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - `ranged corpus reads: 24 GET(s), 6291456 byte(s)`

3. `uv run fedcourts query --court scotus --include-open --era 2020s --limit 20`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`

## Committed Base-Rate & Docket Artifacts Consulted

- `metrics/statpack.md` (modern discretionary-cert base rates, originating circuit `ca5`, relist count and CVSG cuts in the paid scored segment, and `sal-v4` segment base rates by salience band across OT2017–OT2025)
- `metrics/docket.md` (SCOTUS docket-level disposition cuts)
- `metrics/big-cases.md` (OT2026 salience and pending 340B CVSG context in `scotus/73281354`, *AstraZeneca Pharmaceuticals LP v. Mosaic Health, Inc.*)

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="d", court="scotus", q='"340B" OR "AbbVie" OR "Novartis"')` — 0 results.
2. `mcp_courtlistener_search(type="o", case_name="AbbVie v. Fitch", fields=["caseName", "court_id", "dateFiled", "docketNumber", "citation"])` — 1 result (`AbbVie v. Fitch`, `ca5`, No. 24-60375, filed 2025-09-16).
3. `mcp_courtlistener_search(type="o", case_name="AbbVie v. Murrill", fields=["caseName", "court_id", "dateFiled", "docketNumber", "citation"])` — 0 results.
4. `mcp_courtlistener_search(type="o", case_name="AbbVie", fields=["caseName", "court_id", "dateFiled", "docketNumber", "citation"])` — 42 results (confirming circuit-level `AbbVie` opinions).
5. `mcp_courtlistener_search(type="o", case_name="Novartis v. Hanaway", fields=["caseName", "court_id", "dateFiled", "docketNumber", "citation"])` — 1 result (`Novartis Pharmaceuticals Corp. v. Catherine L. Hanaway`, `ca8`, No. 25-1619, filed 2026-07-01).
6. `mcp_courtlistener_search(type="o", case_name="McCuskey", fields=["caseName", "court_id", "dateFiled", "docketNumber", "citation"])` — 35 results.

## Web Searches

- None.
