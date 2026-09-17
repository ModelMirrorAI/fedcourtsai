# Retrieval log — claude-baseline / 20260916T201911Z / scotus/73357827

Mode: `forward` (retrieval unrestricted). Nothing retrieved concerned this petition's disposition; the petition is undecided (distributed for the September 28, 2026 conference).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 12 --corpus-backend service`
  - stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
  - Returned twelve recently resolved SCOTUS rows, all September 2026 emergency applications or an IFP dismissal; no HAVA or standing-related cert priors surfaced, so the result informed nothing beyond confirming the corpus was reachable.
- `uv run fedcourts paths --court scotus --docket 73357827 --event evt-petition-disposition --role predictor` (path resolution only).
- Base rates read from the committed `metrics/statpack.md` (modern discretionary-cert disposition table, originating-circuit table, relist-count and CVSG cuts, per-Term table, and the *Segment base rate by salience band (sal-v4)* table).

## CourtListener MCP

1. `search` (opinions) `"Wisconsin Voter Alliance" HAVA`, courts ca7/wied, filed after 2025-01-01 — 0 results.
2. `search` (opinions) citation `166 F.4th 627` — 0 results (citation not yet indexed).
3. `search` (opinions) `"Wisconsin Voter Alliance"`, filed after 2025-06-01 — 6 results, including the Seventh Circuit decision below (*Wisconsin Voter Alliance v. Don M. Millis*, No. 25-1279, Feb. 10, 2026; clusters 10786799 and 10786800), the Wisconsin Supreme Court's *Wisconsin Voter Alliance v. Secord* (July 7, 2026, a records case not at issue here), and *Public Interest Legal Foundation v. Wolfe* (7th Cir. Aug. 19, 2026).
4. `read_document` opinion 11253440 — the Seventh Circuit per curiam opinion and Chief Judge Brennan's concurrence (read in full, 53,683 characters after stripping markup).
5. `read_document` opinion 11253441 — the same combined document (duplicate cluster; not separately read beyond confirming it was identical in length and opening text).
6. `search` (SCOTUS dockets) `"Help America Vote Act"`, filed after 2025-06-01 — 0 results.

## Web fetches (supremecourt.gov, documents linked from the provisioned snapshot)

- `https://www.supremecourt.gov/DocketPDF/25/25-1288/424275/20260915123704686_Supp%20Brief%209-15-26.pdf` — petitioners' Rule 15.8 supplemental brief (Sept. 15, 2026); text extracted locally and read in full.
- `https://www.supremecourt.gov/DocketPDF/25/25-1288/413407/20260616170125473_25-1288%20Amicus%20Brief.pdf` — amicus brief of Election Research Institute et al. (June 16, 2026); text extracted locally and read in full.

## Not consulted

- No prior predictions on this docket (by this predictor or others) were read.
- Nothing under `data/qp-topics/` was read.
- No general web search was run.
