# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36% granted).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation '599 U.S. 555' --limit 5 --corpus-backend ranged`
- Result: failed before returning priors because the runner could not resolve the corpus storage endpoint. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `tribal reserved water third-party diversion fiduciary duty money damages`; consulted the returned pre-disposition authorities, particularly *Hopi Tribe v. United States*, 782 F.3d 662 (Fed. Cir. 2015), and *Ute Indian Tribe of the Uintah & Ouray Indian Reservation v. United States*, 99 F.4th 1353 (Fed. Cir. 2024).
- Citation search for `99 F.4th 1353` to identify the canonical *Ute Indian Tribe* opinion.
- Opinion endpoint lookup for CourtListener opinion ID 9968358 to inspect the *Ute Indian Tribe* court's source-of-law analysis and disposition of new-water versus existing-infrastructure claims.

No web search was used.
