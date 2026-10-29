# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Stderr transfer line: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Returned 5 recent OT2026/OT2025 SCOTUS granted priors (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`) for general context on recent grant activity and salience/distribution structure.

## CourtListener MCP & Web Search

- No CourtListener MCP calls or web searches were attempted; the provisioned inputs (`2026-09-11.json`, `context.json`, `questions-presented.txt`, `petition.txt`, and `appendix.txt` containing the full Second Circuit and S.D.N.Y. opinions) and `metrics/statpack.md` provided complete context.
