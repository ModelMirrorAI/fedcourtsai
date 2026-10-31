# Retrieval log

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`: usage error, so I re-issued it without `--era`.
- `uv run fedcourts query --court scotus --disposition denied --limit 5`: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`. Returned recent paid denials, several of them pro se (e.g., Griffin v. Isaac, Schultz v. BOKF, Wiggan v. Interinsurance Exchange).
- Read the committed `metrics/statpack.md` relist-count cut (paid scored segment).
- No CourtListener MCP or web lookups.
