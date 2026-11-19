# Retrieval log

- Read `metrics/statpack.md`, section "The interim docket (applications)" and its applicant-class table (committed file, no network).
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 6` — stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Returned six rows (one same-week capital stay denial, Overton v. Florida; the rest unrelated applications and cert denials).
- `uv run fedcourts query --court scotus --docket-number 26-6187` — stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`. Returned the linked certiorari petition's row: docketed 2026-11-18, no distribution, no disposition.
- `uv run fedcourts query --help` (usage text only).
- No CourtListener MCP call, no web search, no fetch of the live Supreme Court docket.
