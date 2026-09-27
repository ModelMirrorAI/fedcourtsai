# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

- `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 15`
  — `ranged corpus reads: 7 GET(s), 1703936 byte(s)`. Recent Term 2026
  granted applications, mostly extensions; 26A308 (DHS v. League of Women
  Voters, SG applicant, response requested, referred, 10 amici) the one
  substantive comparator.
- `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 15`
  — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Recent denials,
  all private or pro se; one SG-opposed row (26A363).
- `uv run fedcourts query --court scotus --include-applications --limit 40`
  — `ranged corpus reads: 0 GET(s), 0 byte(s)`. Filtered client-side to
  SG-filed rows.
- `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 400`
  — `ranged corpus reads: 11 GET(s), 2883584 byte(s)`. Attempt to reach the
  2025 D.V.D. application (24A1153); recency ranking surfaced only 25A
  extensions, so the row was not read.

## Committed base rates

- `metrics/statpack.md`, "The interim docket (applications)" section:
  per-Term substantive resolved/granted counts pooled over Terms 2016–2025
  (31 of 296).

## CourtListener MCP

- `search` type `d`, court `scotus`, q `"D.V.D." Homeland Security` — 0
  results (the application docket is not indexed).
- `search` type `d`, court `ca1`, q `"D.V.D." Homeland Security` — found
  CA1 dockets 25-1311, 25-1393, 25-1631, 26-1212.
- `call_endpoint` `docket-entries`, docket 72347392 (CA1 No. 26-1212),
  newest 15 entries — confirmed the September 18, 2026 published opinion and
  judgment (affirmed/remanded) and the September 23, 2026 11:36 p.m. order
  dissolving the stay pending appeal, entered about three hours after the
  emergency motion.

## Web

None.
