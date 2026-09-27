# Retrieval log — scotus/9026000302, evt-petition-arrival-disposition, claude-baseline, 20260927T182226Z

## Corpus tooling (read-only, via the cell's corpus service)
1. `uv run fedcourts query --court scotus --court cafc --limit 8`
   → `ranged corpus reads: 6 GET(s), 1572864 byte(s)` — returned recent CAFC rows
   (no disposition data; the second `--court` overrode the first). Shape only.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6`
   → `ranged corpus reads: 10 GET(s), 2490368 byte(s)` — recent granted SCOTUS
   rows, all substantive applications; no row bearing on the question presented.
3. `uv run fedcourts paths --court scotus --docket 9026000302 --event evt-petition-arrival-disposition --role predictor`
   (path resolution; no transfer line).

Base rates: the committed `metrics/statpack.md` — "Modern discretionary-cert
petitions by disposition", "by originating circuit" (cafc row), "by relist count",
"by CVSG status", "Cert petitions by salience band", and "Segment base rate by
salience band (sal-v4)" (pooled the `baseline` bracketed `reached` rate over
OT2017–OT2025: 0.0501, n = 12,720).

## CourtListener MCP
4. `search` type=d court=scotus q=`"incentive award" OR "service award" "class representative"` → 0 results.
5. `search` type=d court=scotus docket_number=26-302 → 0 results.
6. `call_endpoint dockets` court=scotus docket_number=25-1411 → 1 row: *Eric Alan Isaacson v. Maribel Moses*, docket id 73522552, filed 2026-06-23, not terminated.
7. `call_endpoint dockets` court=scotus docket_number=26-302 → 0 rows.
8. `search` type=o court=scotus q=`"NPAS Solutions"` → 0 results.
9. `search` type=o court=cafc q=`"National Veterans Legal Services Program" "incentive"` filed_after 2026-01-01 → 1 result: *Nvlsp v. United States*, cluster 10811621, 2026-03-20, Published.
10. `call_endpoint docket-entries` docket=73522552 → 0 entries.
11. `call_endpoint dockets` case_name__icontains=NPAS → validation error (unsupported filter).
12. `call_endpoint dockets` case_name__icontains=Isaacson → validation error (unsupported filter).
13. `get_endpoint_item clusters 10811621` → panel/judges empty, Published, one sub-opinion 11278373.
14. `search` type=d court=scotus case_name=Isaacson → 0 results.
15. `search` type=d court=scotus case_name=NPAS → 0 results.
16. `get_endpoint_item opinions 11278373` → author_str empty, type combined, 26 pages.

## Web fetches (supremecourt.gov public docket JSON and one filing; CourtListener page)
17. `https://www.supremecourt.gov/rss/cases/JSON/25-1411.json` — companion petition
    *Isaacson v. Moses* (2d Cir. No. 24-2979), paid, docketed 2026-06-23: waivers
    2026-07-14 and 2026-07-21; distributed for the 2026-09-28 conference on
    2026-08-05; **Response Requested 2026-08-19** (due 2026-09-18); extension to
    2026-10-19 granted for all respondents 2026-09-18; BIOs of both respondents
    and a Chamber of Commerce amicus filed 2026-09-18. (Fetched twice with
    different prompts; same cached page.)
18. `https://www.supremecourt.gov/rss/cases/JSON/26-302.json` — this docket, later
    than the snapshot (forward mode): 2026-09-23 "Waiver of right of respondent
    Federal Party to respond filed." No disposition.
19. `https://www.supremecourt.gov/rss/cases/JSON/22-389.json` — *Johnson v. Dickenson*
    (the CA11 *NPAS* case): distributed 2022-12-28, rescheduled/redistributed
    through four conferences with supplemental briefs, **denied 2023-04-17**.
20. `https://www.courtlistener.com/opinion/10811621/nvlsp-v-united-states/` — page
    returned no readable text.
21. `https://www.supremecourt.gov/DocketPDF/25/25-1411/424943/20260918173020657_25-1411%20Brief.pdf`
    — the Chamber amicus; the fetch saved the PDF and I extracted its cover
    locally: "IN SUPPORT OF PETITIONER" (Dechert LLP; Steven A. Engel, counsel of
    record; U.S. Chamber Litigation Center).

Nothing retrieved disclosed a disposition of No. 26-302. Roughly 21 retrieval
calls in total, within the advisory budget.
