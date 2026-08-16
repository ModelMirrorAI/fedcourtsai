# Retrieval

- Read the committed `metrics/statpack.md` and `metrics/statpack.json` for the sal-v3 paid-segment arrival anchor and the relist, CVSG, circuit, and disposition cuts. No corpus query was run.
- CourtListener MCP opinion search: `court=ca5`, `docket_number=24-30777`, `case_name=Scroggins`. It returned one published opinion, *Scroggins v. City of Shreveport*, filed October 17, 2025, cluster 10705997.
- A second CourtListener MCP opinion search requesting the opinion list and panel metadata returned HTTP 429 (rate limit exceeded). No further CourtListener retrieval was attempted.
