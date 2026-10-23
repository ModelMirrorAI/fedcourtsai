# Retrieval Log — `scotus/73277583` (`evt-brief-judgment`)

## 1. Corpus CLI Lookups
- None (`used_corpus_query: false`). Base rates were taken directly from the committed `metrics/statpack.md`.

## 2. CourtListener MCP Lookups
1. `mcp_courtlistener_search(type="o", court="ca5", case_name="United States v. Vargas", fields=["caseName", "dateFiled", "citation", "cluster_id"], num_results=5)` — Returned `United States v. Vargas`, 74 F.4th 673 (5th Cir. 2023-07-24) (`cluster_id: 9415425`), confirming the citation and date of the Fifth Circuit en banc precedent applied below.
2. `mcp_courtlistener_search(type="o", court="ca5", case_name="United States v. Martin", fields=["caseName", "dateFiled", "citation", "cluster_id"], num_results=5)` — Throttled (HTTP 429 rate limit); degraded gracefully and relied on the provisioned briefs and appendix.

## 3. Web Searches
- None.
