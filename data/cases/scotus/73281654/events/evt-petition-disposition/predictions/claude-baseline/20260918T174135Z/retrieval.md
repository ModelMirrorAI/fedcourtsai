# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`, `documents/` petition, BIO and QP text, `metrics/statpack.md`):

## Corpus (`fedcourts query`, via the cell's ranged remote)

1. `uv run fedcourts query --court scotus --citation "599 U.S. 555"`
   - stderr: `ranged corpus reads: 10 GET(s), 2555904 byte(s)`
   - Result: no rows; the tool's note said only 200 SCOTUS rows carry any reporter citation, so the empty result is a coverage gap, not absence of Navajo Nation.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   - stderr: `ranged corpus reads: 46 GET(s), 12058624 byte(s)`
   - Result: ~20 recent granted SCOTUS rows (mostly substantive applications and election/immigration petitions). None topically related to Indian Tucker Act trust claims; used only as a sanity check on what a granted docket's distribution counts look like (one paid grant showed `distribution_count: 5`).

## CourtListener MCP

3. `search` type=d court=scotus q="Winnemucca Indian Colony" — 0 results (SCOTUS dockets are not in the RECAP docket search index).
4. `search` type=d court=scotus q="Indian Tucker Act" "breach of trust" "Court of Federal Claims", filed after 2019 — 0 results (same index gap).
5. `call_endpoint` dockets id=73281654 — returned the docket header: No. 25-1170, filed 2026-04-13, `date_terminated: null`. Confirms the petition is genuinely pending (forward cell is correctly provisioned).
6. `call_endpoint` docket-entries docket=73281654 — 0 entries (CourtListener holds no entries for this SCOTUS docket; the provisioned snapshot is the only docket record used).
7. `search` type=o court=cafc q="Winnemucca Indian Colony" filed after 2025-01-01 — 1 result: Winnemucca Indian Colony v. United States, No. 24-1108, filed 2025-10-16, status **Published**. Confirms the decision below is precedential.

No web searches. Nothing retrieved concerned this case's disposition, which does not yet exist.
