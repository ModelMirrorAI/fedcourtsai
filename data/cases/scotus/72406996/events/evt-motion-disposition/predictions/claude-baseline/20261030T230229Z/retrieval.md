# Retrieval

- `uv run fedcourts paths --court scotus --docket 72406996 --event evt-motion-disposition --role predictor` (resolved paths).
- `uv run fedcourts query --court scotus --disposition granted --decided-before 2016 --limit 5`, which returned no rows. stderr: `ranged corpus reads: 917 GET(s), 240123904 byte(s)`
- Read `metrics/statpack.md`, section "The interim docket (applications)".
- No CourtListener MCP calls and no web searches. I deliberately did not look up the linked petition 16-595, to avoid surfacing post-cutoff disposition material.
