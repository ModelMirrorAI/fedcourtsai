# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/*`, `event.yaml`) and the committed `metrics/statpack.md`:

1. `uv run fedcourts paths --court scotus --docket 73378855 --event evt-petition-disposition --role predictor` (path resolution only).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6`
   stderr: `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   Returned six recent grants: four substantive emergency applications (26A326, 26A274, 26A203, 26A124) and two cert grants (25-246 Jouppi v. Alaska, 3 distributions; 25-238 Viramontes v. Cook County, 22 distributions). Used only as contrast with this docket's single distribution, no amici, and pro se counsel.

No CourtListener MCP calls and no web searches were made.
