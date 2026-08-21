# Retrieval

- Consulted the committed `metrics/statpack.md` and `metrics/statpack.json` for the paid scored-segment CVSG and relist cuts and the prior-Term `sal-v3` high-band risk-set anchor. These are committed base-rate artifacts, not `fedcourts query` calls.
- CourtListener MCP RECAP search: court `scotus`, docket number `25-590`; returned no results.
- CourtListener MCP opinion search: `Aramark surcharge ERISA 502(a)(3)`, court `ca5`, filed after 2025-01-01; returned *Aramark Services v. Aetna Life Insurance Co.*, cluster 10761003.
- CourtListener MCP cluster lookup for 10761003: one request failed because two requested date fields were unavailable; a narrowed request returned docket 69183199 and the December 18, 2025 panel-opinion metadata.
- CourtListener MCP docket-schema and docket-item lookups for docket 69183199: showed a July 23, 2026 latest filing.
- CourtListener MCP docket-entry lookups for docket 69183199: showed that rehearing en banc was granted and the panel opinion vacated on April 28, 2026, with en banc argument calendared for September 24, 2026.

No `fedcourts query` or `fedcourts open-events` corpus lookup was used.
