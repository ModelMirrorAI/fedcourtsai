# Retrieval

- No corpus query, CourtListener lookup or web search.
- `uv run fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` — rebuilt the statpack in force when the candidates ran (build `7bcde3b105cb`, landed 2026-10-28, digest `sha256:84feb679…`, no alternative). All three candidates share the same snapshot date and salience version, so this one build served for grading each one's base-rate figures.
- Read the committed `metrics/statpack.md` only to confirm it has since been refreshed (sal-v8 table) and differs from that build.
- Read the provisioned `record/documents/petition.txt` and `record/snapshots/2026-11-16.json` to spot-check candidates' record facts.
