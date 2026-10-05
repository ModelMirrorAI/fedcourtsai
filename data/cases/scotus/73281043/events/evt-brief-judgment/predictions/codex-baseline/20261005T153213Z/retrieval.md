# Retrieval log

## Local inputs and aggregate context

- Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction schema, and the tooling schema. Inspected the path and serialization helpers solely to comply with artifact-writing conventions.
- Ran `uv run fedcourts paths --court scotus --docket 73281043 --event evt-brief-judgment --role predictor`. The first attempt failed because the default uv cache was read-only; rerunning with a temporary writable cache succeeded. No outcome was read.
- Read the provisioned event, context, September 19 snapshot, document manifest, questions presented, selected portions of both merits briefs, the petition opening, and the BIO opposition argument. No other predictor's output or later case record was read.
- Consulted the committed `metrics/statpack.md` merits table and metadata/key structure in `metrics/statpack.json`. Used only grant Terms 2015–2024 for the baseline, with parsed rows available for 2017–2024. No `fedcourts query` or `open-events` call was made; no ranged-corpus transfer line was produced.

## Generic web attempts

- Searched `site.law.cornell.edu/uscode/text/28/2244` and `site.supremecourt.gov opinions 2022 Jones Hendrix 21-857 pdf` in one web call. The tool returned no usable result content.
- Attempted to open the Cornell page for 28 U.S.C. Section 2244. The tool returned no usable content. No proposition relies on that attempted retrieval.

## CourtListener MCP: historical context only

1. `search(type="o", case_name="Jones v. Hendrix", court="scotus", filed_before="2023-12-31", num_results=3)`. Returned the June 22, 2023 decision, 599 U.S. 465, including combined opinion ID 10516269. No search for the target case was made.
2. `search_document(opinion_id=10516269, query="Thomas, J., delivered", snippet_size=800)`. Verified the six-Justice majority and the three dissenters in that prior decision.
3. `search_document(opinion_id=10516269, query="two—and only two", snippet_size=1000)`. Read the majority's enumerated-gateways discussion at 599 U.S. 477–78.

These retrievals supplied general preexisting habeas context only. No target-case disposition, later history, or outcome commentary was requested or surfaced.
