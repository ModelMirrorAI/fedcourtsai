# Retrieval

No corpus query, open-events lookup, CourtListener MCP lookup, or web search was performed by this evaluator. Case facts and forecast checks use only the provisioned outcome, docket snapshot, petition, questions presented, blinded candidate documents, and harness-captured candidate retrieval logs. The committed statpack was consulted for context; historical statpack reconstruction was used to assess candidates against the build available at prediction time.

The following local history lookups read only statpack history through the contract-authorized command. Each completed successfully, selected build `7bcde3b105cb212283905eda17b827efc188e80c`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, and returned `alternative_sha: null`:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

No `ranged corpus reads` line was emitted by these history commands; they did not query the corpus. Reconstructed markdown was read from the scratch directory and the three builds were verified identical. The sal-v4 table and its strictly prior Term rows were checked without writing an independent segment baseline into an evaluation.
