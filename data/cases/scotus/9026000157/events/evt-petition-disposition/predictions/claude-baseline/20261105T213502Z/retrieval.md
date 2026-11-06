# Retrieval log

- Read `metrics/statpack.md` (relist-count, CVSG, amicus-count cuts; sal-v7 band table) as committed base-rate context.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (`modern` is not
  in the `--era` vocabulary; the command printed help).
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
  - Returned recent OT2026 grants and applications (e.g., 26-12, 26-204, 25-1103), none on church autonomy. Used only as general context.
- No CourtListener MCP or web lookups.
