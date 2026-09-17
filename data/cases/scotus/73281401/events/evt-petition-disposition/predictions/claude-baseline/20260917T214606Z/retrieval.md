# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --limit 12 --citation "471 U.S. 1"`
   `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`
   Returned no rows; printed the note that only 200 of 590940 scotus rows carry citation data (the column holds a case's own reporter cites, not a cases-citing-Garner graph).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   Returned 8 recency-ranked granted rows (four OT2026 applications and four OT2025 petitions with distribution counts 3, 5, 17, 22). Shape only; nothing case-specific.

## CourtListener MCP

3. `search` (opinions, ca10) for `Fuqua "Santa Fe County Sheriff"` — located cluster 10730332, *Fuqua v. Santa Fe County Sheriff's Office*, No. 24-2152, filed 2025-11-04, status Published.
4. `search` (opinions, ca3/ca5/ca6/ca7/ca8/ca10/ca11, filed after 2022) for `"motion to dismiss" video "blatantly contradicts" "qualified immunity" "12(b)(6)"` — 0 results.
5. `get_endpoint_item` dockets 73281401 — confirmed docket 25-1108, filed 2026-03-23, not terminated, last modified 2026-07-29 (no entries beyond the snapshot).
6. `search` (dockets, scotus) for `"Cuervo" Sorenson` — 0 results.
7. `call_endpoint` opinions, cluster 10730332 — one combined opinion, id 11196917, 36 pages.
8. `search` (dockets, scotus) for `Chrestman OR "City of Southfield" OR "Johnson v. City of Atlanta" OR Saalim` — 0 results (no cert petition from the other side of the split located).
9. `search` (opinions, scotus, filed after 2019) for `"qualified immunity" "motion to dismiss" video "clearly established"` — 0 results.
10. `search_document` on opinion 11196917 for `blatantly contradict` — 9 matches; confirmed the majority's alternative holding at slip op. 15 that even under the Sixth Circuit rule the videos do not blatantly contradict the complaint, and the dissent's contrary reading.
11. `search_document` on opinion 11196917 for `Sixth Circuit` — 7 matches; the majority's distinctions of *Bailey*, *Saalim*, *Chrestman*.
12. `search_document` on opinion 11196917 for `dissenting` — 1 match; confirmed Judge Tymkovich's dissent beginning at slip op. 29.

## Web searches

None.

## Committed base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `elevated` reached rate over OT2017-OT2024).
