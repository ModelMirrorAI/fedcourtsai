# Retrieval Log

- `uv run fedcourts statpack-at data/cases/scotus/9026000055/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` (resolved build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`; same build resolved for `codex-baseline` and `gemini-baseline`).
- No `fedcourts query` or `fedcourts open-events` corpus lookups, no CourtListener MCP lookups, and no web searches beyond the provisioned inputs and local statpack history.
