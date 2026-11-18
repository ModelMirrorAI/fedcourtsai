Read the evaluation contract, output schemas, provisioned outcome/event, blinded predictions and their prose and captured retrieval logs, the final provisioned snapshot/context/document manifest, questions presented, and relevant passages of the provisioned petition and its bound lower-court opinion. No outside case facts were retrieved. No corpus query, open-events lookup, CourtListener MCP lookup, or web search was made by this evaluator.

Read the committed `metrics/statpack.md` for its scope and current version. Reconstructed the candidates' historical packs using the contract-authorized statpack-only history lookup:

- Initial `uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` exited 2 because the default uv cache path was read-only. Retried successfully with the temporary cache below; no package installation was requested.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three successful lookups selected build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed `2026-10-13T15:28:20-04:00`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, with `alternative_sha: null`. These commands consult statpack history, not the corpus, and emitted no `ranged corpus reads` line. Read the reconstructed sal-v4 table and checked codex-baseline's quoted numerator and denominator against the reconstructed JSON; both matched. No independent scoring baseline was written.

All three candidates' leakage assessments use their own logged forward mode and frozen October 10 context. Unobserved results were assessed from query content; null dates were never treated as proof that retrieval returned nothing.
