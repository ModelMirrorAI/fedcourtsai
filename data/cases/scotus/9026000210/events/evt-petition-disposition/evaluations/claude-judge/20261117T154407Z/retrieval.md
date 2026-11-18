# Retrieval log

- Read the provisioned inputs only: `event.yaml`, `outcome.json`, `record/context.json`, the 2026-11-16 snapshot and summary, `record/documents/` (petition, brief in opposition, reply, question presented), and each `record/blinded/<alias>/` directory.
- Read the committed `metrics/statpack.md` (salience-band table) for context.
- `uv run fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` — resolved build `dedb32b153e6` (landed 2026-10-31), digest matching the `cert_anchor.statpack_digest` all three candidates carry, `alternative_sha` null. Used to check the candidates' quoted base-rate figures. No `ranged corpus reads` line (not a corpus query).
- No `fedcourts query` / `open-events`, CourtListener MCP, or web lookups.
