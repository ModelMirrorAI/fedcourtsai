# Evaluator Retrieval Log (`scotus/9026000526` / `evt-petition-arrival-disposition`)

## Corpus Queries (`fedcourts`)

- None (`uv run fedcourts query` and `uv run fedcourts open-events` were not invoked).
- Local helper commands used (non-corpus):
  - `uv run fedcourts statpack-at data/cases/scotus/9026000526/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for `gemini-baseline`, `claude-baseline`, and `codex-baseline` — reconstructed prediction-time statpack build `eb6830084a187953fd58b91cb3c9125fc6775a7b` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, landed `2026-10-19T08:07:55-04:00`) to verify each candidate's `sal-v4` base-rate citations.
  - `uv run fedcourts paths --court scotus --docket 9026000526 --event evt-petition-arrival-disposition --role evaluator` — verified resolved paths for the cell.

## CourtListener MCP Lookups

1. `mcp:courtlistener:search` (`type="o"`, `court="scotus"`, `citation="601 U.S. 87"`, `num_results=3`) — verified citation and filing date (`2024-02-21`) for *McElrath v. Georgia*, 601 U.S. 87 (2024).
2. `mcp:courtlistener:search` (`type="o"`, `court="scotus"`, `citation="568 U.S. 313"`, `num_results=3`) — verified citation and filing date (`2013-02-20`) for *Evans v. Michigan*, 568 U.S. 313 (2013).
3. `mcp:courtlistener:search` (`type="o"`, `court="scotus"`, `citation="599 U.S. 236"`, `num_results=3`) — verified citation and filing date (`2023-06-15`) for *Smith v. United States*, 599 U.S. 236 (2023).
4. `mcp:courtlistener:search` (`type="o"`, `court="missctapp"`, `case_name="State v. Mitchell"`, `num_results=5`) — checked CourtListener coverage of Mississippi Court of Appeals *Mitchell* opinions (no target-case post-resolution material).
5. `mcp:courtlistener:search_document` (`opinion_id=9842021`, `query="close of all the evidence"`, `snippet_size=400`) — verified in *United States v. Scott*, 437 U.S. 82, 84 (1978), that the trial court granted respondent's preindictment-delay dismissal motion "At the close of all the evidence," confirming `codex-baseline`'s doctrinal critique of the petition's timing distinction.

## Web Searches

- None.
