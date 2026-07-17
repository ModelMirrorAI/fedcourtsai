CourtListener MCP server searches:
- `search` for "Karina Sigalovskaya"
- `call_endpoint` for `opinions` with id `11128175` to read the Second Circuit opinion (`Sigalovskaya v. Braden`).

Corpus tooling:
- `uv run fedcourts query --court ca2 --topic "Bivens"` (stderr: `ranged corpus reads: 74 GET(s), 19398656 byte(s)`)

Statpack:
- Read base rates from `metrics/statpack.md`