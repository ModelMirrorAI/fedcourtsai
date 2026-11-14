# Retrieval log

- No `fedcourts query` or `open-events` lookup, no CourtListener MCP lookup, no web search.
- `uv run fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` returned build `a14b36a1e190` (landed 2026-10-12, `alternative_sha` null). I read its sal-v4 band table to check the candidates' base-rate use. All three candidates share the same run id, so the one build covers them.
- Otherwise only the provisioned inputs: `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-11-13.json`, `record/documents/` (questions presented; greps of the petition and cert reply), and each candidate's staged files.
