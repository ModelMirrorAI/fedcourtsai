# Retrieval record

## Local inputs and aggregate context

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas.
- Read this case's provisioned event, context, snapshot `2026-10-05.json`, document manifest, questions presented, and relevant petition/opposition sections. These are baseline inputs, not new case retrieval.
- Read the modern-cert, originating-circuit, paid relist, paid CVSG, and sal-v4 segment sections of `metrics/statpack.md`; used `metrics/statpack.json` to compute the exact baseline reached pool for displayed Terms 2017–2024: 593 / 11,580.
- Ran `uv run fedcourts paths --court scotus --docket 73500284 --event evt-petition-disposition --role predictor`. The initial attempt failed because the default uv cache was read-only; repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This resolves paths, not corpus priors. The evaluator-only outcome was not opened.
- No `fedcourts query` or `open-events` calls, no corpus blob pull, and no ranged-corpus transfer lines.

## Web attempts

1. Searched `site.supremecourt.gov opinions 2019 GE Energy Outokumpu 18-1048 which body of law equitable estoppel`. The tool returned no usable content.
2. Attempted to open `https://www.supremecourt.gov/opinions/19pdf/18-1048_8mjp.pdf`. The tool returned no usable content. No proposition rests on that attempted URL.

Neither attempt searched for the target petition's disposition. CourtListener supplied the historical authority instead.

## CourtListener MCP

1. `search(type="o", citation="590 U.S. 432", num_results=1)`: returned *GE Energy*, decided June 1, 2020, cluster 4757656, including lead opinion 9889180.
2. `search_document(opinion_id=9889180, query="which body", snippet_size=900)`: verified the concluding passage leaving the governing law and availability of equitable estoppel for remand.
3. `search(type="o", citation="3 F.4th 1166", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])`: returned *Setty*, decided July 7, 2021, opinion 4701830.
4. `read_document(opinion_id=4701830)`: returned the opinion and dissent; the displayed full response was truncated.
5. `search_document(opinion_id=4701830, query="federal substantive", snippet_size=1000)`: supplied focused excerpts confirming the majority's federal-claims formulation and dissenting disagreement. These excerpts, not an assumption that every part of the truncated full response was visible, support the discussion.

No current docket lookup, target-case opinion search, subsequent-history search, or outcome material was consulted. No content under `data/qp-topics/` was read. A repository status listing showed pre-existing deletions there; it did not expose artifact content or case membership and was not used as predictive evidence.
