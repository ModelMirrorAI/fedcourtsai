# Retrieval

- Consulted `metrics/statpack.md`, "The interim docket (applications)." For this OT2026 cell, the strictly prior OT2024 and OT2025 substantive resolved rows total 31 grants in 296 resolutions (10.5%).
- CourtListener MCP search: RECAP, Fourth Circuit docket `26-1785`. Returned *Sherrod Brown v. FCC*, filed June 22, 2026.
- CourtListener MCP search: Fourth Circuit opinions for `Brown FCC`, January 1 through August 31, 2026. Returned the published August 25, 2026 opinion, cluster 10958634.
- CourtListener MCP cluster lookup for 10958634 requesting an invalid `opinions` field. The server rejected the request and identified `sub_opinions` as the correct field; no substantive material was returned.
- CourtListener MCP cluster lookup for 10958634 with valid limited fields. Returned opinion id 11426239.
- CourtListener MCP document read for opinion 11426239, chunks 0-3. Consulted the caption, posture, panel disposition, statutory issue, and the majority's jurisdictional analysis.
- CourtListener MCP document search within opinion 11426239 for `WILKINSON, Circuit Judge, dissenting`. Located the dissent at page 40.
- CourtListener MCP document read for opinion 11426239, chunks 11-13 and 20-21. Consulted the end of the majority opinion and the dissent's jurisdictional, statutory, and First Amendment analysis.
- CourtListener MCP search for Supreme Court opinions named *National Republican Senatorial Committee v. Federal Election Commission*, January 1 through August 31, 2026. No result.
- CourtListener MCP citation search for `146 S. Ct. 2404`. No result.
- Corpus lookup: `fedcourts query --court scotus --era 2020s --include-applications --limit 20`.
  - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - Used only to inspect the recent application stream and escalation shape; most returned matters were inapposite extensions.

No web search was used.
