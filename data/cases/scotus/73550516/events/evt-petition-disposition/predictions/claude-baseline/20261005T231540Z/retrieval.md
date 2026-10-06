# Retrieval log

Forward-mode cell; retrieval unrestricted. Roughly 25 calls in total, at the
advisory budget.

## Corpus tooling (`fedcourts`)

1. `uv run fedcourts query --court scotus --text "..." --limit 8` — refused
   (`query` takes no free-text filter). No transfer line.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   — `ranged corpus reads: 27 GET(s), 6946816 byte(s)`. Six recent grants
   returned; used only as a sanity check on row shape, not as priors.
3. `uv run fedcourts open-events --court scotus` — usage error (`--docket`
   required). No transfer line.
4. `uv run fedcourts open-events --court scotus --docket 73500284` (the lead
   case, *Indian Harbor v. Town of Vinton*) — printed
   `evt-petition-disposition`, i.e. the lead petition is in the corpus and its
   disposition event is still open. `open-events` prints no transfer line.
5. `uv run fedcourts query --court scotus --include-open --era 2020s --limit 3000`
   — refused (limit must be ≤ 500). No transfer line.
6. `uv run fedcourts query --court scotus --include-open --era 2020s --limit 500`
   — run twice (once grepping for the lead case, once counting rows);
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache; the second
   run's stderr was discarded). The lead case was not among the 500 rows
   returned.
7. Base rates: the committed `metrics/statpack.md` — the modern
   discretionary-cert section, the originating-circuit, relist-count and CVSG
   cuts, and the per-Term "Segment base rate by salience band (sal-v4)" table
   (OT2017–OT2024 `baseline` bracketed `reached` rates pooled).

## CourtListener MCP

1. `search` type=d court=scotus q="Town of Vinton" — 0 results.
2. `call_endpoint` docket-entries docket=73550516 — 0 results (SCOTUS
   scraper dockets carry no entries in CourtListener).
3. `search` type=d court=scotus q="Indian Harbor" — 0 results.
4. `get_endpoint_item` dockets 73550516 — confirmed this case
   (No. 25-1427, filed 2026-06-29, last modified 2026-08-17).
5. `search` type=o court=ca5 q="Town of Vinton" "Indian Harbor" arbitration —
   3 results: *Town of Vinton v. Indian Harbor* (2025-12-08), *Police Jury v.
   Indian Harbor* (2026-01-27), *Transportation Consultants v. Certain
   Underwriters* (2026-09-03).
6. `search` type=d court=scotus q="Apex Hospitality" — 0 results.
7. `call_endpoint` dockets with a `case_name__icontains` filter — validation
   error (no such filter).
8. `read_document` opinion 11215982 — the Fifth Circuit's *Town of Vinton*
   opinion, read in full.
9. `get_endpoint_schema` dockets — to find a usable filter (none by name).
10. `read_document` opinion 11433675 chunks 0–1 — *Transportation
    Consultants* (CA5, 2026-09-03), which notes the insurers preserving the
    *Town of Vinton* question for further review.
11. `call_endpoint` dockets court=scotus date_filed range (two windows) — HTTP
    400 (range syntax rejected).
12. `call_endpoint` dockets court=scotus date_filed gte/lte 2026-06-08..16 and
    2026-06-17..26 — listings of June 2026 SCOTUS dockets.
13. `get_more_results` on the first window — second page.
14. `call_endpoint` dockets docket_number = 25-1375, 25-1383, 25-1384,
    25-1395 — found the lead case: *Indian Harbor Insurance Company v. Town of
    Vinton, Louisiana*, No. 25-1383, docket 73500284, filed 2026-06-15, last
    modified 2026-09-09.
15. `call_endpoint` docket-entries docket=73500284 — 0 results.

## Web fetches (engine WebFetch)

1. `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1383.html`
   — the lead case's public docket: extension applications (25A1099); petition
   filed 2026-06-11; waiver 2026-07-02; distributed 2026-07-08 for 9/28/2026;
   amicus briefs 2026-07-10 (APCIA) and 2026-07-15 (Dr. Crina Baltag et al.);
   response requested 2026-07-27; brief in opposition 2026-08-26; reply
   2026-09-09. No disposition shown.
2. `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1427.html`
   (this case) — fetched twice; the tool returned empty page content both
   times, so nothing beyond the provisioned snapshot was learned about this
   docket.

Nothing retrieved disclosed the outcome of this petition or of the lead case.
Nothing under `data/qp-topics/` was read.
