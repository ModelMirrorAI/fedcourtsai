# Retrieval — claude-judge, evt-brief-response-disposition, 20260824T231401Z

- Read the committed `metrics/statpack.md`, section "The interim docket
  (applications)" (file read, no corpus service call), to describe the pool
  the harness stamp should find for this Term-2026 interim cell: Term 2025
  (16/178) + Term 2024 (14/47) = 30/225 ≈ 13.3%, clearing the 50-resolved
  floor. Used for context in `evaluation.md` only; the stamped
  `segment_base_rate` / `brier_skill_score` are the harness's.
- No `fedcourts query` / `open-events` call (no `ranged corpus reads` line to
  record), no CourtListener MCP lookup, no web search.

Everything else read was the provisioned cell input: `event.yaml`,
`outcome.json`, the blinded candidate directories, and the schemas.
