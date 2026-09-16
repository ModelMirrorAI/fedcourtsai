# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --limit 40`
   `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   Filtered locally for NLRB captions; the caption field on these rows is `case_name`, so the first pass matched only one row (NP Red Rock v. NLRB, denied).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 60`
   `ranged corpus reads: 48 GET(s), 12582912 byte(s)`
   Used to learn the row shape; no NLRB grants in the top 60.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 100`
   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   No NLRB-captioned grants; Department of Labor v. Sun Valley Orchards (ca3, granted, 2 distributions) was the nearest labor-agency prior.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 100`
   `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   NLRB priors: NP Red Rock LLC v. NLRB (cadc, denied 2026-09-04, 0 relists); CEMEx Construction Materials Pacific v. NLRB (ca9, denied 2026-07-27, 0 relists).
5. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 100`
   `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   NLRB GVRs: Hospital Menonita de Guayama v. NLRB (cadc, 1 distribution); United Natural Foods v. NLRB (ca5, 2 distributions).

## CourtListener MCP

- `search type=d court=scotus q="National Labor Relations Board" Macy's` → 0 results.
- `search type=d court=scotus docket_number=25-627` → 0 results.
- `search type=d court=scotus q="Macy's National Labor Relations Board" filed_after=2025-06-01` → 0 results.
  CourtListener's SCOTUS docket coverage did not surface No. 25-627; the Macy's denial date (June 15, 2026) is taken from both briefs in opposition instead.

## Web fetch (engine tool)

- Fetched `https://www.supremecourt.gov/DocketPDF/25/25-1192/413475/20260617131955975_PGPublishing_opp.pdf` (the federal respondent's brief in opposition, linked from the snapshot's June 17, 2026 docket entry) and extracted its text locally with pypdf. This brief was not among the provisioned documents; see `flags.json`.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (ca3 row), "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", and "Segment base rate by salience band (sal-v4)" (baseline column, OT2017–OT2024 pooled).
