# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json` for modern cert-petition, 2025 Term paid-filing, originating-circuit, relist, and CVSG base rates.
- CourtListener MCP opinion search: `case_name="Watson v. Mlodzik"`, `court=ca7`, `filed_before=2025-10-01` — no results.
- CourtListener MCP opinion search: `q="\"Wis. Stat. § 939.48(3)\" self-defense negligent handling"`, `filed_before=2026-07-18` — HTTP 429 daily-rate-limit response; no results used.
- CourtListener MCP opinion search: `q="\"24-2498\" Watson Mlodzik"`, `court=ca7`, `filed_before=2025-10-01` — HTTP 429 daily-rate-limit response; no results used.

No `fedcourts query` or `fedcourts open-events` lookup was used.
