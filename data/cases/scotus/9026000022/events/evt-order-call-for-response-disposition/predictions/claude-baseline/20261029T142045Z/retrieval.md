# Retrieval log

- WebFetch `https://www.supremecourt.gov/RSS/Cases/JSON/26-22.json`: the Court's live docket.
  Post-cutoff entries are only extension motions; responses are due Nov 24, 2026 for all
  respondents. There is no disposition.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 8`: refused
  as a usage error (no `--era modern` value / `--limit` usage); help text printed.
- `uv run fedcourts query --court scotus --disposition gvr --limit 8`:
  `ranged corpus reads: 35 GET(s), 9175040 byte(s)`. It returned recent unrelated GVRs
  (e.g. Monsanto v. Dennis, Garcia v. Hobbs) and was not used in the number.
- Read the committed `metrics/statpack.md` for base rates.
- No CourtListener MCP calls.
