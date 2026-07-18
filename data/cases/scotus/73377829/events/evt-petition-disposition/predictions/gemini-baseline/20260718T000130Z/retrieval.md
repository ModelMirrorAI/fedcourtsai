# Retrieval Log

- `uv run fedcourts query --court scotus --topic "Employment Dispute Resolution Plan"` -> `ranged corpus reads: 466 GET(s), 122028032 byte(s)`
- Read committed statpack base-rates (`metrics/statpack.md`) to establish baseline grant rate for Fourth Circuit and identify relevant signals like amicus briefs and Call for Response (CFR).
- CourtListener MCP Server `search` query: `"Employment Dispute Resolution Plan" OR "Congressional Accountability Act" judiciary` (type="o") to find relevant circuit opinions.
- Google Web Search query: `"Caryn Devins Strickland" "Supreme Court" certiorari EDR Title VII` to understand the public profile of the case and real-world practitioner estimates on the CFR multiplier for this exact posture.
