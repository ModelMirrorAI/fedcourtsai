# Retrieval

Beyond the provisioned event, snapshot, questions presented, petition, document manifest, and context, I consulted:

- `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and Term sections.
- `metrics/statpack.json`, for the Term 2025 paid-petition estimate (5.36% grant rate).
- CourtListener MCP opinion search: Supreme Court opinions filed before 2026-07-18 matching `"summary judgment" "Seventh Amendment"` (5 results; query id `62f0bf37`). The returned cases included *Perttu v. Richards*, *Tellabs, Inc. v. Makor Issues & Rights, Ltd.*, *Executive Benefits Insurance Agency v. Arkison*, and *Feltner v. Columbia Pictures Television, Inc.*
- CourtListener MCP opinion search: Supreme Court opinions filed before 2026-07-18 matching `"Seventh Amendment" "States" "not applicable"`. The server returned HTTP 429 and no results.
- CourtListener MCP opinion search: Supreme Court opinions filed before 2026-07-18 matching `"Seventh Amendment" "not applicable to the States"` (2 results; query id `eae5a2b1`). The results were *City of Monterey v. Del Monte Dunes at Monterey, Ltd.*, 526 U.S. 687 (1999), and *Adamson v. California*, 332 U.S. 46 (1947).
- CourtListener MCP opinion search by case name for *Tolan v. Cotton*, limited to Supreme Court opinions filed before 2026-07-18. The server returned HTTP 429 and no results.

No `fedcourts query` or `open-events` corpus lookup was used.
