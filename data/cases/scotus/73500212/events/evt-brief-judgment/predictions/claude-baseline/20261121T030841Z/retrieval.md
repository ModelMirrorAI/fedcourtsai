# Retrieval log

- `uv run fedcourts query --help` (usage text only).
- `uv run fedcourts query --court scotus --citation "587 U.S. 554" --limit 3` — stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; a `note:` line said only 195 SCOTUS rows carry a reporter citation. Returned the row for Taggart v. Lorenzen (scotus/15006766). Metadata only, no `--full`.
- `uv run fedcourts query --court scotus --disposition reversed --era roberts --limit 3` — usage error (unknown disposition `reversed`; era must be a decade token). Nothing returned; not retried.
- `metrics/statpack.md`, "The merits docket (granted cases)" and "Per-Justice merits votes" sections (committed file).
- No CourtListener MCP calls and no web searches.
