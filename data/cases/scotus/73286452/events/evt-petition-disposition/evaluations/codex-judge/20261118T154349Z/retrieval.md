Read the provisioned evaluation contract and schemas, event and outcome, all three blinded prediction/rationale/forecast/retrieval pairs and captured retrieval logs, the case context and November 16 snapshot, and relevant provisioned questions-presented, petition and opposition passages. Read the committed metrics/statpack.md for context. No CourtListener MCP calls, web searches or corpus query/open-events lookups were made by this evaluator.

To check candidates against the statpack available when they ran, executed these local history reconstructions with UV_CACHE_DIR=/tmp/uv-cache, UV_NO_SYNC=1 and PYTHONDONTWRITEBYTECODE=1:

- `uv run fedcourts statpack-at data/cases/scotus/73286452/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/73286452/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/73286452/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

Each succeeded and selected build 73762050f49cd68912e89c864e25a792e498b45a (landed 2026-09-14T08:42:59-04:00), digest sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8, with no alternative build. These commands printed no ranged-corpus-read line; they reconstruct statpack history rather than query the corpus. Read the reconstructed sal-v4 tables and corresponding JSON to verify the historical arithmetic and descriptive cuts. All three reconstructed JSON files are byte-identical. No numerical baseline was independently written to the evaluations.
