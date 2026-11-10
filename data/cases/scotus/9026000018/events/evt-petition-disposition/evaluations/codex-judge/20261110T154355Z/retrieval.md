# Evaluation retrieval record

No external case-fact retrieval, corpus query/open-events call, CourtListener lookup, or web search was performed. Case facts and forecast grading use only the provisioned outcome, resolved docket snapshot, case documents, frozen candidate contexts, and blinded candidate documents and retrieval logs.

For prediction-time base-rate provenance, ran these permitted local statpack-history helpers:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000018/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000018/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000018/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each resolved the prediction run `20261005T231540Z` to build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed `2026-09-28T08:12:04-04:00`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, with `alternative_sha: null`. No ranged-corpus transfer line was printed. Reviewed the historical statpack's sal-v4 state risk-set table and terminal relist/CVSG cuts solely to assess candidates' use of those statistics. Baseline and skill fields remain the harness's.

Local output validation uses the committed JSON schemas and the corresponding Evaluation model; it is not substantive retrieval. No predictor identity lookup, prediction-history inspection, or outcome-labeling-artifact read was performed.
