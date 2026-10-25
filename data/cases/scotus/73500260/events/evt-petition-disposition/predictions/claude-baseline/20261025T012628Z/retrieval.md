# Retrieval

- `uv run fedcourts query --court scotus --text "Younger abstention important state interest NOPSI" --limit 5` — rejected (`--text` is not a valid flag); no results and no `ranged corpus reads` line printed. Not retried.
- CourtListener MCP `search` (type `d`, q `"TMX Finance Corporate Services" Spicher`) — 4 district-court dockets (N.D. Tex., S.D. Ga., D.S.C., M.D. Pa.); no Supreme Court docket for the companion petition.
- Committed `metrics/statpack.md` (salience-band table, relist and CVSG cuts).
