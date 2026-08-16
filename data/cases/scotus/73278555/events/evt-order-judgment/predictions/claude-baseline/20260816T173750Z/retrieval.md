# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --caption "ERISA" --limit 8` — errored
  (`--caption` is not an option); not retried. No `ranged corpus reads` line was
  printed. No corpus priors were pulled for this cell.
- Base rates: read the committed `metrics/statpack.md`, "The merits docket
  (granted cases)" section (pooled 2017–2024 disturbed rate, 359/515 ≈ 69.7%).

## Web searches (engine-surfaced; forward mode, retrieval unrestricted)

- `Anderson v. Intel Supreme Court 25-498 United States amicus brief merits "meaningful benchmark"`
  — established that the United States filed a respondent-side merits amicus
  (July 9, 2026) and that DOL backs Intel (PLANSPONSOR; justice.gov OSG brief
  page; SCOTUSblog case page).
- `Parker-Hannifin v. Johnson 24-1030 Supreme Court solicitor general brief cert Anderson Intel granted denied`
  — established that the SG's CVSG brief in the companion petition (filed
  2025-12-09) recommended a grant and supported the plan-sponsor side (Mayer
  Brown client alert; supremecourt.gov brief PDF), and that Parker-Hannifin
  remains pending/held.

Neither search sought or surfaced this case's own disposition — the judgment
does not yet exist (argument is set for 2026-10-06).

## CourtListener MCP

None used.
