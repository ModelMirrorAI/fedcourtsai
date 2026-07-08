# Retrieval Log

No corpus query, CourtListener MCP lookup, or web search was used.

Consulted local committed base-rate context:

- `metrics/statpack.md`
- `metrics/statpack.json`

Relevant base-rate extracts used:

- SCOTUS resolved petition dispositions in the statpack: 296 resolved, with granted share 0.0135.
- SCOTUS petitions with no originating court in the statpack: 287 resolved, with granted share 0.0139.
- Term 1992 in the statpack: 3 resolved labeled rows, all `other`; this was treated as too small to drive the prediction.

No ranged corpus read lines were produced because no `fedcourts query` or `fedcourts open-events` command was run.
