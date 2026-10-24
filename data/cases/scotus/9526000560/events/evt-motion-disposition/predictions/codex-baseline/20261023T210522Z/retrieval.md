# Retrieval

- Read the committed `metrics/statpack.md` interim-docket section and cross-checked its per-Term counts against `metrics/statpack.json`. Computed the strictly-prior 2016–2025 pool locally: 51 grants / 547 resolved substantive applications.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` solely to establish vintage. It failed because the configured service backend has no client-side connection; no corpus rows or outcomes were returned. No `fedcourts query` or `open-events` call was made, and there is no ranged-transfer line to report.
- General-authority web searches: `site.govinfo.gov 8 USC 1103 note waive all legal requirements constitutional certiorari` and `site.supremecourt.gov Dalton Specter 511 U.S. 462 472 statutory authority constitutional`. The web tool returned no usable content. An attempted open of the GovInfo United States Reports PDF for Dalton likewise returned no content. No case-specific web query was made.
- CourtListener MCP `search(type="o", citation="511 U.S. 462", num_results=1)` identified Dalton v. Specter, decided May 23, 1994, opinion 1087960.
- CourtListener MCP `search_document(opinion_id=1087960, query="constitutional", snippet_size=250)` supplied opinion excerpts distinguishing statutory-authority claims from constitutional claims. Used only that general proposition, without verbatim quotation.

No retrieval sought the target application's disposition or subsequent history. All case-specific evidence came from the provisioned arrival record and application.
