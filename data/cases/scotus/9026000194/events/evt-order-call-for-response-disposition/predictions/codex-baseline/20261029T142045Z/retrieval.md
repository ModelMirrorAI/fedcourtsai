# Retrieval record

No search sought this case's disposition, later docket, or subsequent history. No other prediction or evaluation, outcome record, or QP-topic artifact was read.

## Committed general context

- Read metrics/statpack.md: modern cert dispositions, originating circuits, paid relist/CVSG/amicus cuts, prior-Term sal-v4 reached-band table, and its scope cautions. Inspected metrics/statpack.json keys and Term structures, then used jq to pool baseline prefix_weighted_resolved and prefix_est_grant_rate for 2017–2025: 660 / 12,913 = 0.0511112832. These are committed estimates; no live corpus prior was retrieved.
- A read-only calibration subagent consulted the authorized stable prompt, statistical review checklist, and statpack, independently recovering the same anchor and reviewing the supplied proposed probabilities. It had no data-tree, outcome, other-cell, or network access for its assignment.

## Attempted external retrieval

1. Web search, one tool call with two queries: `site.uscode.house.gov 11 USC 544 trustee rights powers creditor` and `site.govinfo.gov Caplin Marine Midland 406 U.S. 416`. The tool returned no usable result or source text. No factual content was obtained.
2. Web open: `https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title11-section544&num=0&edition=prelim`. Again no usable response or source text was returned. The statutory text relied on is instead the provisioned petition's statutory-provision section.
3. CourtListener MCP search: `type=o`, `citation="816 F.2d 1222"`, `num_results=1`, fields caseName/citation/dateFiled/opinions/absolute_url, to check the older Ozark precedent without searching this case. Failed with HTTP 429, daily rate limit exceeded. No opinion content was retrieved. No REST fallback or credential search was attempted.
4. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts corpus-info`. Failed: the service backend has no client-side connection; query/open-events use the corpus query service. No corpus vintage or case content was returned. No `ranged corpus reads` line was printed.

No `fedcourts query` or `open-events` lookup was attempted. Local schema, path, and serialization inspections and the final validation are implementation checks rather than legal retrieval. The first `uv run fedcourts paths --court scotus --docket 9026000194 --event evt-order-call-for-response-disposition --role predictor` attempt failed because the default uv cache was read-only; retrying with UV_CACHE_DIR under /tmp succeeded.
