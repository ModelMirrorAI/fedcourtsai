# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
  stderr: `ranged corpus reads: 11 GET(s), 2752512 byte(s)`
  Returned six substantive interim applications from OT2025 ranked by recency; not comparable to a cert petition and not used substantively.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (cafc row), "Cert petitions by relist count", "by CVSG status", "by salience band", and "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed `reached` figures, Terms 2017 through 2025).
- `metrics/statpack.json`: per-Term `est_grant_family_rate` for OT2023 through OT2025.

## CourtListener MCP

1. `search` type=d court=scotus q=Dreiling docket_number=26-9 — 0 results.
2. `search` type=o court=cafc case_name=Dreiling filed_after=2025-06-01 — 0 results.
3. `search` type=r court=[cafc, uscfc] party_name=Dreiling — 4 RECAP dockets in the Court of Federal Claims: 1:25-cv-02133 (filed 2025-12-17), 1:25-cv-00491 (filed 2025-03-19), 1:22-cv-00223 (2022, terminated), 1:06-vv-00441 (2006 vaccine claim, terminated). Used only to confirm the lower-court history the petition recites.
4. `search` type=d court=scotus party_name=Dreiling filed_after=2026-01-01 — 0 results.

No web searches. Nothing retrieved concerned this petition's own disposition.
