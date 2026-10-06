# Retrieval log

Mode: `forward` (pending petition; conference of 10/9/2026 not yet held as of the snapshot). Retrieval unrestricted; nothing surfaced this petition's disposition.

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation '563 U.S. 51' --citation '489 U.S. 378' --citation '520 U.S. 397'`
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   Result: no rows; the tool printed its `note:` that only 200 scotus rows carry any reporter citation, so this is the known coverage gap, not absence of Connick/Canton/Brown.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 25 GET(s), 6422528 byte(s)`
   Result: 8 recency-ranked granted rows (25-1131, 25-1349, 26-104, and five 26A applications). Used only to confirm the shape of recent grants (distribution counts 0-2); not topical to Monell.

Base rates: `metrics/statpack.md` sections "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "by CVSG status", "Segment base rate by salience band (sal-v4)".

## CourtListener MCP

3. `search` type=d court=scotus docket_number=25-1389 → 0 results.
4. `search` type=d court=scotus docket_number=25-1323 → 0 results.
5. `call_endpoint dockets` court=scotus docket_number=25-1389 → docket id 73500291, "Richard Hershey v. City of Bossier City, Louisiana", filed 2026-06-16, not terminated.
6. `call_endpoint docket-entries` docket=73500291 → 0 entries (CourtListener holds no entries for the companion docket).

## Web

7. WebSearch `"Bossier City" Hershey Supreme Court certiorari relist Monell 25-1323` → supremecourt.gov filing PDFs for 25-1323 and 25-1389, the CA5 opinion PDF, two commentary pages on the Fifth Circuit decision. No disposition.
8. WebSearch `"Relist Watch" October 2026 Bossier City Hershey` → nothing relevant.
9. WebSearch `"25-1389" Hershey "Bossier City" Supreme Court docket "DISTRIBUTED for Conference"` → supremecourt.gov docket page and SCOTUSblog case page for 25-1389.
10. WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1389.html` → companion docket: petition filed Jun 12 2026, ~15 amicus briefs Jul 14-16, BIO Aug 17, reply Sep 1, DISTRIBUTED for Conference of 9/28/2026 (Sep 2), DISTRIBUTED for Conference of 10/9/2026 (Oct 5). Decisive forward signal: the pair moves together.
11. WebFetch `https://www.scotusblog.com/cases/hershey-v-city-of-bossier-city/` → companion's issue (Hope v. Pelzer beyond the Eighth Amendment), status pending, amicus roster summary.

Total: 2 corpus queries, 4 MCP calls, 5 web calls.
