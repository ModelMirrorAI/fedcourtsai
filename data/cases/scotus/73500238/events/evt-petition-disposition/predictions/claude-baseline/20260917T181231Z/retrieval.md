# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted` — shape of recent granted priors (20 rows returned, 16 cert rows; several interim applications ranked first). stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`.
2. Same command, re-run to inspect the row field names (warm cache). stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.
3. Same command, re-run and piped through a script to check `response_filed_at` on granted cert rows (null on all 16, so the field could not measure a waiver effect) and to list "v. United States" petitioners (one: Chaney v. United States, 24-6543, 5 distributions, ca5). stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied` — returned 20 rows, none of them cert petitions after screening on `application_kind`; not used. stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (ca9 row), "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (baseline column, Terms 2017–2024, bracketed `reached` figures pooled).

## CourtListener MCP

1. `search` type=d court=scotus q="Holmes Theranos" — 0 results.
2. `search` type=d court=scotus q="Balwani OR "Elizabeth Holmes" OR "Elizabeth A. Holmes"" — 0 results (the SCOTUS docket index did not return this docket either, so the null is uninformative about a companion Holmes petition).
3. `search` type=o court=ca9 q="Balwani Theranos" — 2 results: United States v. Elizabeth Holmes, 129 F.4th 636 (Feb. 24, 2025) and United States v. Holmes, No. 23-1167 (Dec. 22, 2025, amended opinion, cluster 10763137).
4. `get_endpoint_item` clusters/10763137 — sub-opinion 11229722, published, dated 2025-12-22.
5. `call_endpoint` opinions cluster=10763137 — opinion 11229722, 55 pages, combined opinion.
6. `read_document` opinion 11229722 chunk 0 — caption, panel (Schroeder, Nguyen, R. Nelson), staff summary.
7. `search_document` opinion 11229722 "rehearing" — the order denying panel rehearing and rehearing en banc; no judge requested an en banc vote.
8. `search_document` opinion 11229722 "Napue" — Part VII: plain-error review applied because the claim was not raised at trial; duty to correct assumed without deciding; no effect on substantial rights.
9. `search_document` opinion 11229722 "gatekeep" — 0 matches.
10. `search_document` opinion 11229722 "dissent" — 0 matches.

No web searches. Nothing retrieved concerned this petition's own disposition.
