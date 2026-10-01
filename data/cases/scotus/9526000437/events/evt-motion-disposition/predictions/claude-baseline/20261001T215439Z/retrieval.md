# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition granted --include-applications --limit 15`
   `ranged corpus reads: 5 GET(s), 1310720 byte(s)` — mostly time-extension letters; used only to learn the row shape.
2. `uv run fedcourts query --court scotus --disposition denied --limit 40`
   `ranged corpus reads: 8 GET(s), 2097152 byte(s)` — filtered client-side to `application_kind == "substantive"`: 39 denied substantive applications, Terms 2025–2026, with response-requested / referral / amicus flags.
3. `uv run fedcourts query --court scotus --disposition granted --limit 40`
   `ranged corpus reads: 38 GET(s), 9961472 byte(s)` — filtered to substantive: 14 granted substantive applications, Terms 2025–2026.
4. `uv run fedcourts query --court scotus --limit 1` (key listing only; stderr not recorded).

No `--decided-before` (forward cell, `decided_before: null`). No `--full`.

## Base rates

`metrics/statpack.md`, section "The interim docket (applications)": pooled Terms 2016–2025 substantive resolved 296, granted 31 (10.5%); clears the floor of 50.

## CourtListener MCP (forward mode, unrestricted)

1. `search` type `r`, `party_name: Valov` — 21 hits, none this applicant (other surnames / other people).
2. `search` type `r`, `q: "Nikolay Valov" OR "Nikolay M. Valov" OR "Nikolay Mihaylov Valov"` — 0 hits.
3. `search` type `o`, `q: Valov`, courts va / vactapp / ca4 / vaed / vawd / scotus — 0 hits.
4. `search` type `d`, court `scotus`, `q: Valov` — 0 hits (the 26A437 application docket is not on CourtListener).

No web searches.
