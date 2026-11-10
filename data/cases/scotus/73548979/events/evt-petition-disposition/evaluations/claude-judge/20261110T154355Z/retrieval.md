# Retrieval (claude-judge, run 20261110T154355Z)

- Read the provisioned inputs: event.yaml, outcome.json, record/context.json, record/snapshots/2026-11-09.json (proceedings list), record/documents/questions-presented.txt, and each candidate's staged prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md and retrieval_log.json under record/blinded/.
- `uv run fedcourts statpack-at data/cases/scotus/73548979/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` → build 886549a3ac32 (landed 2026-10-13, alternative_sha null). Read its sal-v4 segment-by-salience-band table to check the candidates' anchor figures. All three candidates ran on 2026-10-14, after this build landed.
- No `fedcourts query` / `open-events` calls (so no `ranged corpus reads` line), no CourtListener MCP calls, and no web searches.
