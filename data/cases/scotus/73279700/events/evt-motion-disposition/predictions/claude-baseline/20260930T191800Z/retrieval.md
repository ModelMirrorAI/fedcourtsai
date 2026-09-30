# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-applications --limit 15`
   — `ranged corpus reads: 4 GET(s), 917504 byte(s)`. Recency-ranked application
   rows; used only to learn the row shape.
2. `uv run fedcourts query --court scotus --include-applications --limit 400`
   — `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Tallied locally: 70
   substantive applications; pro se applicants 0/16 granted, counseled 7/52 granted,
   2 withdrawn; 6/6 applications naming a court as respondent denied.

## Committed base rates

- `metrics/statpack.md`, "The interim docket (applications)": Term 2024 row (70
  resolved substantive, 14 granted, 20.0%, 972 unparsed) as the strictly-prior pool
  for an application-Term 2025 cell; Term 2025 row read for ladder shape only.

## CourtListener MCP

1. `search` type=r court=ca9 docket_number=25-2374 — 0 results.
2. `search` type=d court=[ca9, azd] party_name="Allen Watkins" — 3 results, all
   multi-plaintiff MDL dockets in azd (Bard catheter/IVC filter, McIntire v.
   Motorola); not identifiable as this applicant's matter.
3. `search` type=r court=[ca9, azd] q="Watkins" AND "25-2374" — 0 results.
4. `search` type=d court=ca9 q=Watkins filed_after=2025-01-01 — 46 dockets; none
   numbered 25-2374. Neighbouring numbers (e.g. 25-2330, Orr v. United States
   District Court for the Central District of California, filed 2025-04-11) place
   25-2374 in April 2025 among mandamus petitions against district courts.

No web searches. Nothing about this application's own disposition was sought or seen.
