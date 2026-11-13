# Evaluator retrieval

No corpus query, open-events call, CourtListener MCP lookup, web search, or external document retrieval was performed. Case facts were graded only against the provisioned outcome, snapshot, document metadata and selected application passages, and blinded candidate files, including every candidate's retrieval log and forecast pointer.

Local reference: consulted the committed `metrics/statpack.json` interim counts and the interim context in `metrics/statpack.md`.

Local provenance reconstruction, to check gemini-baseline's discrepant prior against the build it actually received:

`UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9526000657/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

Result: frozen digest `sha256:b122cc43052b1328321031e3615601101a1b85c7dcdc87d23e5436373b03f133`; build `f0a8cabd41e643e9a1441db9518d722d427a1768`, landed `2026-11-07T22:02:37+00:00`; `alternative_sha = null`. No `ranged corpus reads` line applies: this command reconstructs statpack history, not the case corpus. All three candidates freeze that same digest. The prior-Term pool and private/unmarked cut match the current pack and contradict gemini-baseline's quoted counts. Only statpack history was consulted; no prediction history or identity mapping was read.
