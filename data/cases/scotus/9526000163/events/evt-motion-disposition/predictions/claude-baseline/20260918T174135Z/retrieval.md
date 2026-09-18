# Retrieval log

## Corpus (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --include-applications --limit 25`
   stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   Recency-ranked SCOTUS application priors; dominated by extension applications.
2. `uv run fedcourts query --court scotus --include-applications --limit 300`
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Post-filtered locally to `application_kind == "substantive"`: 49 rows (44 denied, 4 granted, 1 withdrawn).

## Committed base rates

- `metrics/statpack.md`, section "The interim docket (applications)": pooled Terms 2024–2025 (the only parsed Terms strictly before Term 2026), 31 granted / 296 resolved.

## CourtListener MCP server

1. `search` type `d`, court `ca5`, docket_number `26-30022` — located the Fifth Circuit docket (CourtListener docket id 73507998; filed 2026-01-20, terminated 2026-02-26, nature of suit "Other Civil Rights").
2. `search` type `d`, q `Gilmore Walmart`, Fifth Circuit district courts — no relevant hit.
3. `search` type `o`, q `Gilmore Walmart`, ca5 and Texas district courts, filed after 2023 — no results.
4. `call_endpoint` `docket-entries`, docket 73507998, ordered by date — 40 of 46 entries read (through 2026-05-18). Not paged further.
5. `search` type `d`, case_name `Gilmore v. Walmart`, Louisiana/Texas/Arkansas district courts — no results.

All retrieved material predates the 2026-07-23 snapshot. I did not search for the Supreme Court application docket 26A163 or for this application's disposition.

## Web searches

None.
