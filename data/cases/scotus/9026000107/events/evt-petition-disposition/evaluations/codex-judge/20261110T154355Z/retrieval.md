# Retrieval record

No corpus query, CourtListener MCP lookup, web search, or external case-material retrieval was performed. Case grading uses only the provisioned event, outcome, blinded candidates and logs, docket snapshot, questions presented, and opposition excerpts. No opinion or writing slot was staged.

For placement-era calibration review, I ran these permitted statpack-history reconstructions (with `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache`; no installation):

- `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each returned build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed `2026-09-28T08:12:04-04:00`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, `alternative_sha=null`. I read the recovered sal-v4 table and its risk-set instructions. These commands consult statpack history only, not prediction history; they emit no ranged-corpus transfer line. No baseline was independently pooled or substituted for the harness stamp.
