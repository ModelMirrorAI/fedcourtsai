# Retrieval

- CourtListener MCP opinion search: `q=\"Americans for Citizen Voting\" Michigan`, 10-result limit. No results (`query_id: 5d2a6766`).
- CourtListener MCP opinion search: `docket_number=170595`, `q=Michigan`, 10-result limit. No results (`query_id: 58027b39`).
- CourtListener MCP opinion search: `q=\"citizen voting\" Michigan`, 20-result limit. It returned general election-law opinions but not the case-specific lower-court proceeding (`query_id: 8f056b22`); none supplied case-specific facts used in the forecast.
- Supreme Court docket PDF linked in the provisioned snapshot: `ACVM Emergency App for an Injunction Pending Appeal.pdf` (43 pages, filed August 31, 2026). Consulted for the requested relief, alleged injury, procedural posture, and applicants' due-process and equal-protection theories.
- `metrics/statpack.md`, “The interim docket (applications).” Used the strictly-prior OT2024 and OT2025 substantive-application counts and the descriptive escalation-signal counts.

No `fedcourts query` or `fedcourts open-events` lookup was used.
