# Retrieval and supporting checks

## Provisioned inputs and committed context

Read AGENTS.md, `.github/prompts/predict.md`, prediction/tooling schemas, the event definition, `record/context.json`, `record/snapshots/2026-07-29.json`, the document manifest, questions presented, and the petition including the reproduced Third Circuit opinion. Read the modern-cert, paid-segment relist/CVSG/amicus, and sal-v4 per-Term sections of `metrics/statpack.md`; used the corresponding JSON fields to calculate the prior-Term baseline risk-set pool. These are supplied repository context, not a live corpus refresh. No other prediction, evaluation, outcome file, or topic-label artifact was read.

## Corpus and CLI attempts

1. `uv run fedcourts paths --court scotus --docket 73500260 --event evt-order-call-for-response-disposition --role predictor` initially failed because the default uv cache directory was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`. The command identified the case and event paths and did not expose an outcome.
2. `uv run fedcourts query --help` initially failed for the same cache reason. Retried successfully with the cache override; later repeated with `COLUMNS=160` to inspect the structured filters. These help calls performed no corpus retrieval.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2025 --limit 3` succeeded.

   `ranged corpus reads: 73 GET(s), 18939904 byte(s)`

   Returned RiseandShine Corporation v. PepsiCo (24-1016), Devin Chaney v. United States (24-6543), and Monsanto Company v. Durnell (24-1068), all from earlier docket-number Terms. Their returned grant dates extend into 2026: the Term-based filter is not an exact decision-date cutoff. I did not use these generic examples as as-of-July comparators, frequency estimates, or doctrinal evidence. No opinion bodies were requested and none of the rows concerned this cell's petition.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info --help` succeeded. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed because the service backend has no client-side connection and only query/open-events forwarding is supported. No corpus vintage was obtained; no credential discovery or alternative remote access was attempted.

## External authority attempts

5. Web search: `site.supremecourt.gov opinions Sprint Communications Jacobs 571 69 Younger 2013`. The tool returned no usable result or source text.
6. Web search: `Sprint Communications Inc v Jacobs 571 U.S. 69 opinion pdf 2013`. The tool again returned no usable result or source text.
7. Web open of the govinfo U.S. Reports PDF for Sprint, identified by package `USREPORTS-571` and file `USREPORTS-571-69.pdf`. The tool returned no usable text or source. It did not reveal anything about the TitleMax petition.
8. CourtListener MCP `search(type="o", citation="571 U.S. 69", num_results=1)` returned HTTP 429, daily rate limit 1,400, with approximately 6,666 seconds until availability. Did not retry or use a REST fallback. No opinion or result snippet was obtained.

These attempts concern general abstention precedent, not this petition's disposition. No live lookup of the case's Supreme Court status, later history, or related petition's subsequent status was attempted. The forecast rests on the provisioned pre-decision record and committed statpack.
