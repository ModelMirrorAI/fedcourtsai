# Retrieval log (forward cell; retrieval unrestricted)

## Corpus (`fedcourts`, service backend)

1. `uv run fedcourts paths --court scotus --docket 9026000002 --event evt-petition-disposition --role predictor` (path resolution; no transfer line).
2. `uv run fedcourts query --court scotus --citation "590 U.S. 432"` → `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; empty result with the `note:` line that only 200 scotus rows carry citations.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` → `ranged corpus reads: 25 GET(s), 6422528 byte(s)`; eight recent granted rows (immigration, RLUIPA, emergency applications), none topically related.
4. `uv run fedcourts query --court scotus --include-open --era 2020s --limit 600` → refused by the service (`limit` must be ≤ 500); no transfer line.
5. `uv run fedcourts query --court scotus --include-open --era 2020s --limit 500` → `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache); scanned 500 rows by caption for Vinton / Indian Harbor / Independent Specialty / Lower Cameron / Calcasieu / Lloyd's: no companion petition found (two unrelated "Lloyd" IFP rows).

## Committed base rates

- `metrics/statpack.md`: modern discretionary-cert disposition table; originating-circuit cut (ca5); relist-count, CVSG and salience-band cuts; per-Term table; "Segment base rate by salience band (sal-v4)" (baseline column, bracketed `reached`, OT2017–OT2025 pooled).

## CourtListener MCP

6. `search` type=d court=scotus docket_number="26-2" → 0 results.
7. `search` type=d court=scotus q="Town of Vinton" → 0 results.
8. `search` type=d court=scotus q="Indian Harbor" filed_after=2025-01-01 → 0 results.
9. `search` type=d q="Indian Harbor Insurance" "Vinton" filed_after=2025-06-01 (no court filter) → 0 results.

## Web (engine WebSearch / WebFetch)

10. WebSearch: `"Indian Harbor Insurance" "Town of Vinton" Supreme Court petition certiorari 2026` → identified lead docket No. 25-1383 and application 25A1099.
11. WebSearch: `"Independent Specialty Insurance" "Lower Cameron Hospital Service District" supreme court 26-2` → only the district-court order; no SCOTUS disposition.
12. WebFetch `supremecourt.gov/docket/docketfiles/html/public/25-1383.html` (twice: full entries, then latest entry + document links). Last entry 2026-09-09 (reply filed); response requested 2026-07-27; two amicus briefs.
13. WebFetch `.../public/26-2.html` → identical to the provisioned snapshot (last entry 2026-08-14).
14. WebFetch `.../public/26-53.html` → *Indian Harbor v. One Lakeside Plaza*, distributed 2026-08-26 for 9/28, "Rescheduled" 2026-08-27.
15. WebFetch `.../public/25A1218.html` → extension application linked to 26-53.
16. WebFetch `supremecourt.gov/orders/ordersofthecourt/26` (twice) → only the 2026-10-05 order list listed.
17. WebFetch `supremecourt.gov/orders/courtorders/100526zor_2a34.pdf` (text extracted locally with pypdf) → no mention of 25-1383, 26-53, 26-2, Indian Harbor, Vinton, Lakeside or Lower Cameron in any section.
18. WebFetch the 25-1383 petition, brief in opposition and reply PDFs (text extracted locally) → QP, split characterization (4–1 claimed; 4–2 per the reply after *Kim v. Jump Trading*, 7th Cir. Aug. 13, 2026), the BIO's no-split and vehicle arguments.
19. WebSearch: `Supreme Court grants certiorari October 2 2026 long conference new cases granted` → SCOTUSblog: three grants on 2026-10-02 (Rhoney v. Barbosa da Cunha, Missionaries of St. John the Baptist v. Frederic, and one more); not the cluster.
20. WebSearch: `"25-1383" OR "Indian Harbor" "Vinton" Supreme Court relist OR conference OR "call for the views" October 2026` → nothing on the SCOTUS docket beyond the Fifth Circuit case.

No outcome for No. 26-2 surfaced in any of the above.
