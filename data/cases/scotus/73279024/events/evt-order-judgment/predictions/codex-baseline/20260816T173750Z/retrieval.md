# Retrieval

Beyond the provisioned inputs, I consulted `metrics/statpack.md` and `metrics/statpack.json` for the registered merits base rate.

CourtListener MCP searches attempted:

- Opinions search: `128 F.4th 1089` (lower-court opinion).
- Opinions search: `Bennett v. Spear 520 U.S. 154`.
- Opinions search: `Seven County Infrastructure Coalition v. Eagle County 605 U.S. 168`.
- Opinions search: `Karst final agency action NEPA permit`, restricted to filings before March 9, 2026.

All four CourtListener searches returned HTTP 429 rate-limit errors and supplied no results.

Corpus lookups attempted:

- `fedcourts query --court scotus --citation '520 U.S. 154' --limit 1 --full`
- `fedcourts query --court scotus --citation '578 U.S. 590' --limit 1 --full`
- `fedcourts query --court scotus --citation '505 U.S. 788' --limit 1 --full`
- `fedcourts query --court scotus --citation '520 U.S. 154' --limit 1`
- `fedcourts query --court scotus --citation '520 U.S. 154' --limit 3 --full`
- `fedcourts query --court scotus --citation '542 U.S. 55' --limit 3 --full`
- `fedcourts query --court scotus --citation '426 U.S. 776' --limit 3 --full`
- `fedcourts query --court scotus --citation '578 U.S. 590' --limit 3 --full`

The corpus commands returned no usable rows and printed no `ranged corpus reads` line.

General web searches attempted to identify a potentially relevant precedent referred to only as “Karst”: DuckDuckGo, Google, Bing, Google Scholar, Case.law, and Justia searches combining `Karst` with `final agency action`, `APA`, `EPA`, or `Environmental Education Protection`. These returned bot challenges, boilerplate, or irrelevant geology results. No proposition from them informed the forecast, and no “Karst” precedent is cited here.
