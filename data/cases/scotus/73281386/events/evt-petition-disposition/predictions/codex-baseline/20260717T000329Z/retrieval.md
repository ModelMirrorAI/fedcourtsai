# Retrieval

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Attempted `uv run fedcourts query --court scotus --citation '542 U.S. 367' --limit 10 --corpus-backend ranged`. The lookup failed before returning results because the configured corpus remote could not be resolved; consequently it printed no `ranged corpus reads: …` line.
- CourtListener MCP opinion search: Supreme Court opinions with citation `542 U.S. 367`, filed before 2026-07-17. It returned *Cheney v. United States District Court for District of Columbia*, 542 U.S. 367 (2004).
- CourtListener MCP opinion search: `"discovery order" "writ of mandamus" Executive Branch`, restricted to Supreme Court opinions filed before 2026-07-17. It returned five results; the relevant lead result was *Cheney*, 542 U.S. 367 (2004). No search targeted this case, its disposition, or its subsequent history.
