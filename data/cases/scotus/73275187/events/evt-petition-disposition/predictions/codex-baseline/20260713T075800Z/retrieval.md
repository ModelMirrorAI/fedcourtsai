# Retrieval log

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition” and “SCOTUS cert petitions by Term.” The resolved live/historical slice reports 92.6% denied, 4.9% granted, and 2.5% dismissed for modern discretionary-cert petitions.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation '524 U.S. 321' --citation '586 U.S. 146' --limit 10 --corpus-backend ranged`
- Purpose: retrieve recent resolved SCOTUS priors sharing the petition’s principal Excessive Fines Clause authorities.
- Result: no priors were returned. The ranged backend failed on DNS resolution for the corpus object store. No `ranged corpus reads: ...` line was produced.

## CourtListener MCP

- Searched SCOTUS opinions filed June 1–25, 2026 for `"Excessive Fines Clause" OR Bajakajian`; found *Pung v. Isabella County*, No. 25-95, decided June 23, 2026.
- Searched *Pung v. Isabella County* by case name to obtain its docket number, cluster metadata, and combined-opinion identifier.
- Retrieved CourtListener opinion item 11346051 to review the *Pung* syllabus and opinion, particularly its Excessive Fines Clause holding.
- Searched SCOTUS opinions for `Pung "grossly disproportional"`; no result was returned.
- Searched SCOTUS opinions for `Pung "in part to punish"`; confirmed the relevant *Pung* result.

No web searches or direct REST fallback calls were used.
