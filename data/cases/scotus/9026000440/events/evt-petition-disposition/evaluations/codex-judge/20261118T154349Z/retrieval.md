No corpus queries, CourtListener MCP lookups, or web searches were performed by this evaluator. Case evidence came only from the provisioned outcome, docket snapshot, petition and appendix, and the blinded candidates' staged files.

Local statpack provenance checks (no corpus transfer):

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000440/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000440/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000440/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three commands succeeded and selected build `7bcde3b105cb212283905eda17b827efc188e80c`, landed `2026-10-28T13:56:30-04:00`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with `alternative_sha: null`. These commands read only statpack history and print no `ranged corpus reads` line. I read the reconstructed sal-v4 table and its scope notes, plus the circuit/relist/amicus sections, to assess the candidates against the build available at prediction time. I also inspected current statpack metadata; its changed build was not substituted for the historical one. No case or prediction history was consulted.
