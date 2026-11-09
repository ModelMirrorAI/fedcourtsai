# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5`
  — `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Returned recent OT2026 denied
  applications (Guardado v. Florida, Lopez Jaime v. Blanche, Taylor v. Weber);
  shape context only.
- Read `metrics/statpack.md`, "The interim docket (applications)" and
  "Substantive applications by applicant class".
- WebFetch: supremecourt.gov docket page for 26A658 — only the Nov 2, 2026
  submission entry; docketed Nov 6, 2026; lower court listed as BAP 10th Cir.
  (26-2404); applicant self-represented.
- No CourtListener MCP calls.
