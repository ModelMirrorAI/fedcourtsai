# Retrieval log

1. `uv run fedcourts query --help` (twice, to read the flags). No corpus read.
2. `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 8` returned 8 recent denied SCOTUS rows (two applications, six cert petitions), none specific to this case. stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`.
3. `curl https://www.supremecourt.gov/RSS/Cases/JSON/26-502.json`: the Court's docket JSON for the linked cert petition (No. 26-502). Returned the petition's entries through 16 Nov 2026 (petition filed 28 Aug 2026, sealing motion granted 13 Oct, waiver by Minor Child E.O.D., the stay application entry). No disposition shown.
4. Read `metrics/statpack.md`, section "The interim docket (applications)" and its applicant-class table.

No CourtListener MCP calls and no web searches.
