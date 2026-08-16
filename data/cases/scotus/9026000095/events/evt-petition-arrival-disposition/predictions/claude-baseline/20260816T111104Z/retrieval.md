# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, `record/documents/petition.txt`,
`questions-presented.txt`, `documents.json`) and the committed
`metrics/statpack.md`:

- `uv run fedcourts query --court scotus --era modern "judicial disqualification recusal due process bias state court"`
  — errored (the command takes no free-text argument; structured filters
  only). No `ranged corpus reads` line was printed (no query executed).
- `uv run fedcourts query --help` — read the filter surface; concluded none of
  the available filters (`--court`/`--topic`/`--judge`/`--citation`)
  discriminates usefully for this petition (SCOTUS rows carry no topic; a
  citation query is a known-case lookup, not a similar-petitions search), so
  no corpus priors were pulled.
- No CourtListener MCP lookups and no web searches were made.

Base rates used: the committed statpack's "Segment base rate by salience band
(sal-v3)" table (baseline band, bracketed `reached` figures pooled over
OT2017–OT2025: 6.55%, n≈13,163), the relist-count and CVSG cuts (paid scored
segment), and the modern-cert disposition split for the GVR share of the grant
family.
