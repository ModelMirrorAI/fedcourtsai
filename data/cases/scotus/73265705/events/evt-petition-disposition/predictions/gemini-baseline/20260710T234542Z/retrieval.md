# Retrieval Log — scotus/73265705 evt-petition-disposition (gemini-baseline, 20260710T234542Z)

## Corpus Lookups (fedcourts, ranged backend)
- `uv run fedcourts query --court scotus --corpus-backend ranged --limit 5`
  - Result: Failed with `RangedBackendError: the ranged corpus backend needs the DVC remote URL from the environment` (the private S3/DVC credentials were not passed to this YOLO mode shell). Proceeded under the degraded-upstream rule.

## CourtListener MCP Lookups
- `mcp_courtlistener_get_endpoint_item` with `endpoint_id="dockets"`, `item_id="73265705"`.
  - Returned full docket metadata showing Docket No. 25-1230, originating Federal Circuit case (2026-111), filed April 29, 2026, and a decision date of Jan 27, 2026.

## Web Searches
1. `google_web_search` with query `"Google v. VirtaMove" patent OR cert petition`
  - Returned articles and litigation blogs detailing the patent technology (containerization: US Patents 7,519,814; 7,784,058; 7,774,762), the underlying litigation transfer to the Northern District of California, and Google's mandamus challenge of the PTAB's "settled expectations" doctrine.
2. `google_web_search` with query `"25-1230" OR "Google v. VirtaMove" Supreme Court order OR conference OR granted OR denied`
  - Confirmed the current procedural status of No. 25-1230 as of July 10, 2026: pending, with the Court having requested a response on June 11/12, 2026, and the USPTO having filed a motion for an extension of time.

## Other Materials Consulted
- Committed `metrics/statpack.md` (overall base rates and court-by-court breakdown).
