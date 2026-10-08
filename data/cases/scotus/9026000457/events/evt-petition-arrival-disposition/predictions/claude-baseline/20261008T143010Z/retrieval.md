# Retrieval log

Beyond the provisioned inputs (snapshot `2026-10-08.json`, `context.json`,
`documents.json`, `petition.txt`, `questions-presented.txt`, `event.yaml`) and
the committed `metrics/statpack.md`:

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — `ranged corpus reads: 28 GET(s), 7274496 byte(s)`. Eight recent grants
   (OT2026 grants and substantive applications); used only as a sanity check
   on what the corpus carries for this Term, not as priors for this case.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 600`
   and the same with `--include-open` — refused by the service (`limit` must be
   ≤ 500); no transfer line.
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 500`
   — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Filtered
   locally for 340B-related captions (McClain, AbbVie, Novartis, PhRMA,
   AstraZeneca, Murrill, Fitch, Hanaway, Sanofi): no matches in the 500 most
   recent denied rows.
4. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 500`
   — `ranged corpus reads: 0 GET(s), 0 byte(s)`. Same caption filter: no
   matches (no companion 340B petition is yet in the corpus).

## CourtListener MCP

5. `search` (opinions): `340B "contract pharmacy" preemption`, filed after
   2024-01-01 — 8 results: CA5 *PhRMA v. Murrill* (2026-02-09 and the
   2026-07-06 superseding opinion), CA8 *Novartis v. Hanaway* (2026-07-01),
   CA4 *PhRMA v. McCuskey* / *AbbVie v. McCuskey* / *Novartis v. McCuskey*
   (2026-03-31, since vacated by the en banc grant), CA5 *AbbVie v. Fitch*
   (2025-09-16), CA8 *PhRMA v. McClain*, 95 F.4th 1136 (2024-03-12). Used
   to confirm the dates and courts the petition cites; opinion bodies not read.
6. `search` (dockets, scotus): `340B` — 0 results.
7. `search` (dockets, scotus): manufacturer/respondent names — 0 results.
8. `search` (RECAP, scotus): `"340B"` — 0 results. CourtListener's SCOTUS
   docket coverage did not reach these petitions.

## Web searches (engine-surfaced)

9. "PhRMA v. McClain Supreme Court docket 340B certiorari denied December
   2024 conference" — confirmed No. 24-118: petition filed 2024-07-31,
   distributed 2024-11-19 for the 2024-12-06 conference, denied 2024-12-09
   (one conference, no CVSG). Sources: scotusblog.com case page;
   supremecourt.gov DocketPDF entries for 24-118.
10. "AbbVie v. Murrill petition for certiorari 340B Louisiana Supreme Court
    2026" — found application No. 26A356: Justice Sotomayor extended PhRMA's
    time to petition from the Fifth Circuit's Louisiana decision to
    2026-11-03. Sources: supremecourt.gov DocketPDF 26A356; Mealey's.
11. "Fourth Circuit en banc PhRMA v. McCuskey 340B West Virginia argument
    2026" — confirmed rehearing en banc granted 2026-05-28, argument to be
    scheduled. Sources: Jackson Kelly health-law note; Drug & Device Law blog.

None of these surfaced this petition's own disposition.
