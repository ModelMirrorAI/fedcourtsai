No corpus query, open-events, CourtListener MCP lookup, or web search was performed by this evaluator. Case facts were assessed only from the provisioned event, outcome, docket snapshot, filings, and blinded candidate materials.

For base-rate context, read the committed metrics/statpack.md and reconstructed the candidates' shared historical build using:

`UV_NO_CACHE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000062/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

The command succeeded and identified build `dedb32b153e67d254af10083c3ee247cecd56116`, landed `2026-10-31T10:28:26-04:00`, digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, with `alternative_sha: null`. All three blinded predictions freeze this same digest in context.cert_anchor, so the reconstructed build supplies their common statistical context. Read its relevant circuit, relist, CVSG, amicus and sal-v6 tables. This reads only statpack history and printed no ranged corpus reads line; it was not a corpus query. No case history or identity mapping was consulted.

Local schema/model inspection and JSON-schema validation were operational checks. Candidate-reported retrievals described in the evaluations are evidence from their staged transcripts, not additional retrieval performed by this evaluator.
