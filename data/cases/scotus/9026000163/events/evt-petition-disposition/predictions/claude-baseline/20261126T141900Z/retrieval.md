# Retrieval log

- Read `metrics/statpack.md` (salience-band table, relist-count cut).
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` — failed with a usage error (printed help text; no rows).
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` — returned 5 recent GVR rows (Casarez v. Irigoyen Farms; Huffman v. United States; Roybal v. Griffith; Harrington v. Martin; Cid v. United States). `ranged corpus reads: 34 GET(s), 8912896 byte(s)`. None bears on the venue question; not used beyond confirming GVRs in federal criminal cases occur.
- No CourtListener MCP calls and no web searches.
