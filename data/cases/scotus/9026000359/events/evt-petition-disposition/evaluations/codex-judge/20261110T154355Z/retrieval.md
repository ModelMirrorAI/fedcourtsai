# Evaluation retrieval record

Read the evaluation prompt and output schemas, then the provisioned event, outcome, context, resolved docket snapshot, blinded prediction/rationale/forecast/retrieval documents and all three captured logs. Consulted the questions-presented file and relevant petition and appendix passages to assess the analyses. No case fact was retrieved externally, and no unstaged order or opinion was fetched.

Inspected the committed metrics/statpack.md only for scope and version context. Assessed candidate base-rate use against the prediction-time build reconstructed by these commands:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000359/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000359/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000359/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each returned build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed October 13, 2026, with digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde` and no alternative build. Read that build's relevant sal-v4 table and checked codex-baseline's stated prior-Term numerator and denominator against its JSON. No new evaluator baseline was assigned. These commands read statpack history only and emitted no ranged-corpus-read line.

No `fedcourts query` or `open-events` lookup, CourtListener MCP lookup, or evaluator web search was made. The web queries discussed in codex-baseline's evaluation belong to its staged historical log, not evaluator retrieval.
