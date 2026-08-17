# Retrieval log

Beyond the provisioned inputs (event.yaml, record/context.json,
record/snapshots/2026-08-16.json) and the committed `metrics/statpack.md`:

1. **CourtListener MCP** — `search` (dockets, ca1, docket_number 26-1774,
   q "California v. Trump election executive order"): **failed with HTTP 429**
   (daily rate limit exceeded, 1400/day). No CourtListener data was retrieved;
   no further MCP calls attempted.
2. **Corpus** — `uv run fedcourts query --court scotus --include-applications
   --disposition granted --limit 8`
   — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.
   Returned eight recently decided granted applications, all
   `application_kind: extension` (routine time-extension grants); no
   substantive stay priors surfaced, so this informed nothing beyond
   confirming the extension-dominance the statpack caption describes.

No web searches were run. Base rates came from the committed
`metrics/statpack.md` ("The interim docket (applications)" section).
