# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially "Modern discretionary-cert petitions by disposition," "Cert petitions by relist count," "Cert petitions by CVSG status," and "SCOTUS cert petitions by Term."
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36% grant rate).

## Corpus lookup

- `uv run fedcourts query --court scotus --era 2020s --limit 10`
  - `ranged corpus reads: 429 GET(s), 112394240 byte(s)`
  - Used only as general contemporary procedural priors; the query did not seek or return this case.

## CourtListener MCP

- Searched opinions filed from August 29, 2025 through July 17, 2026 for `"Excessive Fines Clause" forfeiture "gravity"` to identify potentially relevant intervening authority.
- Searched opinions filed from May 1 through June 25, 2026 for `Bajakajian`; this surfaced *Pung v. Isabella County*, No. 25-95 (U.S. June 23, 2026).
- Searched specifically for the *Pung* SCOTUS record to identify the opinion and its metadata.
- Retrieved CourtListener opinion 11346051 for *Pung*. The syllabus and opinion state that a fairly conducted tax sale does not require fair-market-value compensation under the Excessive Fines Clause; the decision did not replace *Bajakajian*'s proportionality rule for punitive criminal forfeitures.

No web search was used.
