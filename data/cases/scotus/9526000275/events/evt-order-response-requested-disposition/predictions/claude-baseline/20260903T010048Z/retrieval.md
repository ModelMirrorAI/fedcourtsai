# Retrieval log

Beyond the provisioned inputs (snapshot 2026-09-01, `record/context.json`,
`record/documents/application.txt` + `documents.json`, `event.yaml`), I consulted:

- Committed `metrics/statpack.md`, section "The interim docket (applications)" —
  pooled the strictly-prior resolved substantive slice (Terms 2025 + 2024:
  31/296 ≈ 10.5%) as the scored baseline.
- `uv run fedcourts query --court scotus --include-applications --era 2020s --disposition granted --limit 8`
  — `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
- `uv run fedcourts query --court scotus --include-applications --era 2020s --disposition denied --limit 20`
  — `ranged corpus reads: 2 GET(s), 524288 byte(s)`

No CourtListener MCP lookups and no web searches. I deliberately made no live
retrieval about this case (26A275) or its companion Michigan Supreme Court
mandamus case (No. 170595): the requested disposition date coincides with this
run's date, so a live lookup risked surfacing the outcome itself.
