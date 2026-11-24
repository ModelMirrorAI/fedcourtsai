# Retrieval log

- `uv run fedcourts query --help` — read the flags.
- `uv run fedcourts query --court scotus --disposition gvr --limit 8` — eight recent GVR priors (e.g. Nos. 25-1421, 26-5528, 26-5123, 25-7569). stderr: `ranged corpus reads: 42 GET(s), 10878976 byte(s)`. Used only for the general shape of GVRs; nothing case-specific.
- `metrics/statpack.md` — read the federal band row and the salience-band caption.
- No CourtListener MCP calls and no web searches. I did not look up the lead case's docket (No. 26-104); what I say about it comes from the staged petition and decision below.
