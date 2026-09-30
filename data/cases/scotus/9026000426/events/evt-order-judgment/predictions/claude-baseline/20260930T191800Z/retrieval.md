# Retrieval log — claude-baseline, scotus/9026000426, evt-order-judgment, run 20260930T191800Z

Mode: `forward` (record/context.json). Retrieval unrestricted; nothing
outcome-revealing exists yet and none surfaced.

## Corpus tooling
- `uv run fedcourts paths --court scotus --docket 9026000426 --event evt-order-judgment --role predictor`
- `uv run fedcourts query --court scotus --disposition granted --include-applications --limit 8`
  - stderr: `ranged corpus reads: 4 GET(s), 917504 byte(s)`
  - Returned recency-ranked rows: this case's own row (cert granted 2026-09-29, no decision), its linked application docket 26A406 (scotus/9526000406, 2 amicus entries), and six time-extension applications. Not used beyond confirming the docket link.
- `metrics/statpack.md`, section "The merits docket (granted cases)": pooled Terms 2017–2024, 360 disturbed / 516 parsed = 69.8%.

## CourtListener MCP
- `search` (type=o, court ca1+mad, "D.V.D." "Department of Homeland Security" third-country removal, filed after 2026-01-01): 0 results.
- `search` (type=o, court ca1, "third country removal 1231(b) 1252(f)(1) declaratory FARRA", filed after 2026-09-01): 1 result — D.V.D. v. U.S. DHS, No. 26-1212, filed 2026-09-18, cluster 10976939, opinion 11444581.
- `search` (type=d, court ca1, docket_number 26-1212): docket 72347392.
- `read_document` (opinion 11444581, chunks 0–2 of 12 at 10,000 chars).
- `read_document` (opinion 11444581, chunks 3–11 of 12): full opinion read (113,859 chars).

## Web
- `WebSearch`: "Supreme Court D.V.D. third-country removals stay granted certiorari December argument September 29 2026" — results describing the 2026-09-29 order (already in the snapshot); no judgment exists.
- `WebFetch`: https://www.supremecourt.gov/DocketPDF/26/26-426/425859/20260928154306895_Opp%20Stay%20v4%20FINAL.pdf — respondents' opposition to the stay (filed 2026-09-28, in the snapshot). Returned as binary; text extracted locally with pypdf (`uv run --with pypdf`), 42 pages, read through the equities section.
- `WebFetch`: https://reason.com/volokh/2026/09/30/scotus-stays-third-party-removal-injunction-40-minutes-after-reply-filed/ — commentary on the grant order.

Not retrieved: the Government's 2026-09-29 reply in support of the application; the district court's 2026-02-25 opinion (821 F. Supp. 3d 102), which I know through the First Circuit's and the parties' descriptions.
