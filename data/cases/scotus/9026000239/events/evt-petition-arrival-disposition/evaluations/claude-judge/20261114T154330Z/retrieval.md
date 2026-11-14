# Retrieval

No corpus query, CourtListener lookup or web search.

Beyond the provisioned inputs (event.yaml, outcome.json, the 2026-11-13 docket snapshot, the staged questions presented, and the three blinded candidates):

- `uv run fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` (and the same for gemini-baseline and codex-baseline) - all three resolved to build 02dd6a20fccc (landed 2026-08-19, `alternative_sha` null). Read its sal-v3 segment table and the federal band row to check the candidates' base-rate figures. Reads statpack history only; no `ranged corpus reads` line.
