# Retrieval record

All case-specific evidence came from the provisioned October 30, 2026 record. No lookup sought No. 26-435's disposition, later docket, or another cell's output. No outcome-revealing material about this petition was encountered.

## Committed reference material

- Read the modern-cert, originating-circuit, paid-segment relist/CVSG/amicus, and `sal-v4` risk-set sections of `metrics/statpack.md`.
- Read corresponding entries in `metrics/statpack.json`; a `jq` calculation pooled OT2017–OT2025 baseline `prefix_weighted_resolved` and `prefix_est_grant_rate`, giving 660 / 12,913 = 0.0511112832. Excluded OT2026. These are committed-pack estimates, not a newly refreshed corpus measurement.

## Corpus calls

1. Read `uv run fedcourts query --help` before attempting retrieval.
2. Attempted `uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 4`. Refused because `modern` is not a supported decade token. Returned usage and the allowed era vocabulary; no rows and no transfer line.
3. Corrected to `uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`. Returned Google LLC v. VirtaMove, No. 25-1230; Hastings College Conservation Committee v. California, No. 25-1231; and Ryan O'Donnell v. City of Chicago, No. 25-1098, all with October 19, 2026 denial dates. These are other petitions, before this forward cell's date. Used only as a limited procedural check, not substantive analogies or an estimated base rate. No opinion bodies requested.

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

## Web call

4. Attempted a general search: `site.supremecourt.gov opinions 2023 Loper Bright factfinding substantial evidence agency independent judgment 603 369`. The web tool returned no usable result. It supplied no evidence and contained no search for this petition. Turned to CourtListener primary authorities.

## CourtListener MCP calls

5. `search(type="o", citation="603 U.S. 369", num_results=2, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`: returned Loper Bright Enterprises v. Raimondo, decided June 28, 2024, including opinion 10452863 and another representation of the same decision.
6. `search_document(opinion_id=10452863, query="factfinding", snippet_size=500)`: returned the majority's distinction between independent legal interpretation and deferential review of agency factfinding, including the discussion on opinion-of-the-Court page 14. Used to assess the appended panel order's factual rationale. No text about this petition was requested.
7. `search(type="o", citation="303 F.3d 896", num_results=1, fields=["caseName", "dateFiled", "absolute_url", "id"])`: returned Multimedia KSDK, Inc. v. NLRB, September 10, 2002. The response warned that `id` was unavailable; its opinion path identified cluster 3029656.
8. `get_endpoint_item(endpoint_id="clusters", item_id=3029656, fields=["sub_opinions", "case_name", "date_filed"])`: identified opinion 3029656 and alternative sub-opinions.
9. `read_document(opinion_id=3029656)`: returned the en banc Eighth Circuit opinion, including majority and dissent; the long response was display-truncated. Its opening describes denial of enforcement based on an improper legal standard, not a universal occupational rule.
10. `search_document(opinion_id=3029656, query="collaboration", snippet_size=450)`: located the collaboration discussion; the snippets were in the dissent, so I did not treat them as majority holdings.
11. `read_document(opinion_id=3029656, chunk_index=1, chunk_size=8000)`: read the majority's substantial-evidence standard and its rejection, under Kentucky River, of categorically excluding professional/technical judgment. Used this directly to assess the claimed split.

## Operational notes

The first prescribed `uv run fedcourts paths --court scotus --docket 9026000435 --event evt-petition-disposition --role predictor` failed because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`; subsequent uv commands used the same temporary cache. Path resolution, CLI help, schema reads, and validation are operational checks, not retrieval of outcomes.
