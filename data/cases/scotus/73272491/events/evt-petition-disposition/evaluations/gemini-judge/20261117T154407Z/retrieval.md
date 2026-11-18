# Evaluator retrieval log

- Reconstructed the prediction-time statpack (`run_id = 20261017T142059Z`, build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`) from local git history via:
  - `uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - `uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - `uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- No `fedcourts query` or `fedcourts open-events` corpus lookups, no CourtListener MCP calls, and no web searches beyond the provisioned inputs.
