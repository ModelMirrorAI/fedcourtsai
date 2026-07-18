# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, Term, and paid/IFP cuts.

## Corpus lookup

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
  - `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  - Used as a compact set of recent grant-side priors; the results showed distribution counts and signals such as CVSG status, government participation, counsel, and companion litigation.

## CourtListener MCP lookups

- Opinions search for `"Lo-Ji Sales" "judicial immunity" arrest judge` across the Third, Fourth, Fifth, Sixth, and Eighth Circuits: throttled (HTTP 429); no result was used.
- Opinions search for `"Lo-Ji Sales" "judicial immunity" arrest` across the same circuits: returned no results.
- Case-name search for *Gibson v. Goldston*: throttled (HTTP 429); no result was used.
- Case-name search for *Rockett v. Eighmy*: returned the published Eighth Circuit decision, 71 F.4th 665 (June 22, 2023), docket 21-3903.
- Case-name search for *Zorn v. Linton* in the Supreme Court: throttled (HTTP 429); no result was used.

No web search was used, and no lookup sought this case's disposition or subsequent history.
