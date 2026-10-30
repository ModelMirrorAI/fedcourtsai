# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`
  — refused before running: `modern` is not an era token (vocabulary is decade tokens). No transfer line printed.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; returned five recent grants
  (mostly SG-filed applications/petitions), none comparable to a pro se MSPB petition.
- Read committed `metrics/statpack.md` (modern cert, originating circuit, relist, CVSG,
  salience-band and per-Term band tables).
- No CourtListener MCP calls and no web searches.
