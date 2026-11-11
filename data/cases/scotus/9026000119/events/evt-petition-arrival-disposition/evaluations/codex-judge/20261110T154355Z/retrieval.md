# Evaluator retrieval

No external case-fact retrieval, corpus query, CourtListener MCP lookup, or web search was performed. Case evidence came only from the staged blinded predictions and logs, event, outcome, resolved snapshot, context, questions presented, and petition appendix.

Historical base-rate context was reconstructed with the contract's statpack-only helper:

- `uv run fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` initially failed because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`.
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` succeeded.

All three reconstructions selected build ab6fb84c09a602f661fc4b436c922fdc8de9c7fc, landed August 15, 2026, digest sha256:f8abdb31530370551ced5a16ef3db2ecf512b450e040799d9ec5d03b7b9f48c4, with alternative_sha null. The historical sal-v3 table was read for rationale assessment only. No scored baseline was hand-pooled or written. These local statpack-history lookups emitted no ranged-corpus-read line. No packages were installed.
