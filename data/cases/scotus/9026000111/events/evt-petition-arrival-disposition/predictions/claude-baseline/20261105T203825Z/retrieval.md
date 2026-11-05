# Retrieval

- Read committed `metrics/statpack.md` (salience-band tables, sal-v7 per-Term segment table) for base rates.
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-111.html`: returned the live docket. After the snapshot it shows two response-extension motions, both granted (Aug. 18, 2026 to Sept. 23; Sept. 14, 2026 to Dec. 7, 2026). No distribution, no disposition.
- `uv run fedcourts query --docket-number 25-417` failed with a usage error (`--docket-number needs --court`). Re-issued as below.
- `uv run fedcourts query --court scotus --docket-number 25-417 --include-open` returned *Nielsen v. Watanabe* (filed 2025-10-07, disposition `granted`, 4 distributions, no merits decision on the row; the SG appears among the attorneys). Stderr: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`.
- `uv run fedcourts query --court scotus --disposition gvr --era roberts` failed with a usage error (unknown era token).
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` returned 5 recent GVR rows, several on SG-involved dockets. These are shape only, not used numerically. Stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`.
- No CourtListener MCP calls.
