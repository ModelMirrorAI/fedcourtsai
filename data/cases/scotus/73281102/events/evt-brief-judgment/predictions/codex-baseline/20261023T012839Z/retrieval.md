# Retrieval log

## Committed general context

- Read the merits-only section of `metrics/statpack.md` and its caption; no cert-band rates were used. A local `uv run python -c` command parsed only that section and summed the eligible 2017–2024 rows in the 2015–2024 window: 539 grants, 516 parsed judgments, 360 disturbed; 360/516 = 0.6976744186. No live corpus lookup was made and no ranged-read transfer line was emitted.

## General legal verification attempts

These requests concerned only statutory text and a different, older precedent. None sought Maxwell's disposition, subsequent history, or decision coverage.

1. Web search queries: `site.uscode.house.gov 28 USC 2241 custody violation Constitution laws treaties` and `site.supremecourt.gov Jones Hendrix 2023 execution sentence place confinement 2241`. The tool returned no usable results.
2. Web open attempt: the House U.S. Code page for title 28, § 2241, requested with `req=granuleid:USC-prelim-title28-section2241`, `num=0`, `edition=prelim`. The tool returned no usable page text. No legal proposition is attributed to this failed request.
3. CourtListener MCP `search(type="o", citation="599 U.S. 465", num_results=1)`: returned metadata for Jones v. Hendrix, decided June 22, 2023, docket 21-857, opinion ID 10516269, cluster 10049669. The metadata alone was not treated as verification of the briefs' doctrinal characterization.
4. CourtListener MCP `search_document(opinion_id=10516269, query="place or manner", snippet_size=1300)`: returned HTTP 429, with no opinion-text excerpt. Degraded to the provisioned record; no direct REST fallback, credential access, or case-outcome search.

## Local contract and tooling reads

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction/tooling/flags schemas, and relevant path, serialization, and prediction-model definitions. Ran `fedcourts paths --court scotus --docket 73281102 --event evt-brief-judgment --role predictor`; the CLI withheld the evaluator-only outcome path. The first `uv` invocation could not write its default cache; rerunning with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. These are infrastructure checks, not external case evidence.

The case inputs consulted were confined to the provisioned record and this cell's event definition. No prior prediction, evaluator output, outcome artifact, current case docket, or labeling-measurement artifact was consulted.
