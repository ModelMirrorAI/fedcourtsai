# Evaluator retrieval

Read the evaluation contract and schemas, all three blinded prediction/rationale/forecast/retrieval documents and harness logs, the provisioned outcome, event, context, decided docket snapshot, document manifest, questions presented, and relevant petition/appendix passages. No corpus case query, CourtListener lookup, web search, or external order/opinion retrieval was performed.

Consulted the committed metrics/statpack.md for statistical scope and version context. To assess the candidates against the historical build they actually pinned, ran:

```text
UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 PYTHONDONTWRITEBYTECODE=1 uv run fedcourts statpack-at data/cases/scotus/9026000372/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline
```

The command resolved build dedb32b153e67d254af10083c3ee247cecd56116, landed 2026-10-31T10:28:26-04:00, digest sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa; alternative_sha was null. No ranged corpus reads line was printed. Read the rebuilt statpack's relevant disposition, procedural-cut, and sal-v6 band tables. All three candidates carry that same digest. This inspected only statpack history, within the blind.
