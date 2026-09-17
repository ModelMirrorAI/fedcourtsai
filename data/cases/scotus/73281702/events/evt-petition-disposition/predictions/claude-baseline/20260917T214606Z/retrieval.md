# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 8` — returned the eight most recent resolved SCOTUS rows (recent applications and a denied petition); nothing on point, since `query` has no topic or text filter on SCOTUS rows. stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`.
- `metrics/statpack.md` (committed): "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "Petitions by originating court (incl. state courts)", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" — the last is the anchor.

## CourtListener MCP

1. `search` type `d`, court `scotus`, q `"continuous sexual abuse" unanimous` — 0 results.
2. `search` type `o`, court `scotus`, q `"continuous sexual abuse" unanimity Ramos` — 0 results.
3. `search` type `o`, court `scotus`, q `"continuous sexual abuse" jury unanimous`, filed after 2020-04-01 — 2 results, both Rivers v. Guerrero (No. 23-1345, a successive-habeas case arising from a Texas continuous-sexual-abuse conviction), not on the unanimity question; not used.

## Web

- `WebFetch` of the reply brief linked on the snapshot's September 15, 2026 entry: `https://www.supremecourt.gov/DocketPDF/25/25-1195/424387/20260915164932677_25-1195%20Reply%20Brief.pdf`. The fetch tool could not read the PDF; I extracted its text locally from the saved file and read the nine-page reply in full.

No search sought or surfaced this case's disposition; the petition is pending for the September 28, 2026 conference.
