# Retrieval log

## Corpus lookups (`fedcourts`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation '431 U.S. 720'`
   stderr: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`
   Result: empty; `note:` line reported the citation column is sparse
   (200 of 590940 scotus rows) and matches a case's own cites only.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   stderr: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   Result: 15 recent granted rows (shape only; no antitrust analogue surfaced).

Base rates: committed `metrics/statpack.md` — modern cert by disposition,
relist-count and CVSG cuts (paid scored segment), by-Term table, and the
"Segment base rate by salience band (sal-v4)" table (pooled elevated
`reached` over OT2017–OT2024).

## CourtListener MCP

3. `search` type=d court=scotus q="Academy of Allergy" Amerigroup — 0 results.
4. `search` type=d court=scotus party_name=Amerigroup — 0 results.
5. `search` type=o q="Academy of Allergy" Amerigroup "Illinois Brick" — 2 Sixth
   Circuit clusters (No. 24-5153; opinions dated 2025-10-10 and 2026-01-13).
6. `search` type=d court=scotus case_name="Academy of Allergy" — 0 results.
7. `search` type=o q="Mosaic Health" Sanofi 340B — 2 Second Circuit clusters
   (No. 24-598; 2025-08-06 original and 2025-10-15 amended opinion).
8. `search` type=d court=scotus docket_number=25-1388 — 0 results
   (CourtListener's SCOTUS docket coverage did not carry it).

## Web

9. WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1388.html`
   — companion petition United Biologics v. Amerigroup Tennessee: docketed
   June 16, 2026; BIO filed Aug 17, 2026; reply and `DISTRIBUTED for
   Conference of 9/28/2026` on Sep 2, 2026. No CVSG, no disposition.
10. WebSearch "AstraZeneca v. Mosaic Health 25-1070 certiorari Illinois Brick
    340B petition Supreme Court" — surfaced the SCOTUSblog case page, the
    Chamber's case page, the amicus PDF, and the docket; nothing beyond
    "distributed for conference on 9/28/2026" about this case's status, and
    no disposition (none exists yet).

Nothing retrieved concerned this case's own disposition.
