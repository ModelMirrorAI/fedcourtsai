# Retrieval log

- Reconstructed the statpack build in force at each candidate's prediction run (`20261015T142602Z`) using `uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for `codex-baseline`, `gemini-baseline`, and `claude-baseline` (resolved to `build_sha` `886549a3ac32bdba039691b6d2ca7dc57bb72561`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`).
- Read the committed `metrics/statpack.md` header to confirm that the checkout's current statpack postdates the build in force when the candidates ran.
- No `fedcourts query` or `open-events` corpus lookups, CourtListener MCP calls, or web searches were performed beyond the provisioned inputs and `statpack-at`.
