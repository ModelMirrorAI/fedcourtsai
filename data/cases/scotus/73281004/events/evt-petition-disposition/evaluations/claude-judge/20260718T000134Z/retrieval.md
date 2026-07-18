# Retrieval log — scotus/73281004 / evt-petition-disposition / claude-judge / 20260718T000134Z

- Committed `metrics/statpack.md` and `metrics/statpack.json`: read the per-Term
  cert table and checked the per-Term salience segments for the segment base
  rate. Every Term's `segments` list is empty, so no prior-Term band rate exists
  and `segment_base_rate` / `brier_skill_score` are omitted on all three
  evaluations (matching `fedcourtsai.pipeline.evaluate.segment_base_rate`,
  which returns None when nothing in the band resolved).
- No `fedcourts query` / `open-events` corpus lookups (no `ranged corpus
  reads:` lines to report), no CourtListener MCP lookups, and no web searches.
  All scoring inputs came from the provisioned cell files, the committed
  statpack, and the repository's pipeline code.
