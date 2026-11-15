# Retrieval log

- `uv run fedcourts paths --court scotus --docket 9526000686 --event evt-motion-disposition --role predictor` — resolved paths.
- `uv run fedcourts query --help` — read flags.
- `uv run fedcourts query --court scotus --disposition granted --include-applications --limit 8` — stderr: `ranged corpus reads: 6 GET(s), 1507328 byte(s)`. Returned 8 recent rows (two non-capital granted matters and six extension applications); no usable capital stay priors.
- Read committed `metrics/statpack.md`, "The interim docket (applications)" section and its applicant-class table.
- No CourtListener MCP calls, no web searches, no live-docket fetch.
