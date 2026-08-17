# Retrieval

- Consulted `metrics/statpack.md`, section “The interim docket (applications),” for the strictly prior OT2024–OT2025 substantive-application pool and escalation-signal context.
- CourtListener MCP search for RECAP materials from the First Circuit docket `26-1774` (`court=ca1`, `type=r`): returned HTTP 429 rate-limit exceeded; no result content was available or used.
- Ran `uv run fedcourts query --court scotus --include-applications --limit 8` for recent SCOTUS priors. The command reported `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. The returned slice was broad and dominated by time-extension applications; it supplied no comparable merits evidence and did not drive the probability adjustment.
