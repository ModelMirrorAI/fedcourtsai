# Retrieval log

Beyond the provisioned inputs (snapshot `2026-10-08.json`, `context.json`, `documents/application.txt`), this cell consulted:

## Corpus

- `uv run fedcourts query --court scotus --include-applications --limit 15`
  stderr: `ranged corpus reads: 4 GET(s), 983040 byte(s)`
  Returned recent OT2026 application rows (mostly extension grants and a few denied substantive capital applications); used only as a shape check on recent application activity.
- Committed `metrics/statpack.md`, "The interim docket (applications)" section, for the pooled strictly-prior base rate (Terms 2024–2025: 31 granted / 301 resolved).

## CourtListener MCP

- `search` (type `o`, court `ca6`, filed after 2026-01-01, query `"Wagner" detention "Bail Reform Act" de novo`) → United States v. Kyle Wagner, cluster 10946076, filed 2026-08-12, No. 26-1294.
- `get_endpoint_item` clusters/10946076 → judges Norris, Bloomekatz, Hermandorfer; published; sub-opinion 11413661.
- `read_document` opinion 11413661, chunks 0–2 and 6–8 (majority on standard of review and conditions of release; opening of the Bloomekatz dissent).

## Web

- WebSearch: `Wagner v. United States 26A446 stay application Supreme Court Kavanaugh pretrial detention` → SCOTUSblog case page and the Court's docket pages.
- WebFetch: https://www.supremecourt.gov/docket/docketfiles/html/public/26A446.html (docket unchanged from the snapshot; no disposition).
- WebFetch: https://www.supremecourt.gov/docket/docketfiles/html/public/26-391.html (cert docket: petition filed 2026-09-18, motion to expedite 2026-09-29, SG waiver 2026-10-02, distributed for the 2026-11-06 conference).
- WebFetch: https://www.scotusblog.com/cases/wagner-v-united-states/ (case page; no disposition).
- WebFetch: the SG's response in opposition PDF (26A446, filed 2026-10-08) and the applicant's letter PDF (filed 2026-10-06); both were extracted to text locally with pypdf because the fetch returned raw PDF bytes.

No search surfaced this application's disposition; the cell is correctly provisioned as forward.
