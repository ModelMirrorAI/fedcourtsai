# Retrieval

- Consulted `metrics/statpack.md`, including “Modern discretionary-cert petitions by disposition,” “Cert petitions by relist count (paid scored segment),” “Cert petitions by CVSG status (paid scored segment),” “Cert petitions by salience band,” and “Segment base rate by salience band (sal-v3).” No corpus query was run.
- CourtListener MCP opinion search with `court=ca2` and `docket_number=25-3141`, limited to case metadata. The service returned HTTP 429 (daily rate limit exceeded), so no result informed the prediction and no REST fallback was attempted.
