# Retrieval beyond the provisioned inputs

## Committed base rates

- Read `metrics/statpack.md` and `metrics/statpack.json`, focusing on modern discretionary-cert disposition, originating-circuit, relist, CVSG, Term, and fee-class rates.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '600 U.S. 447' --limit 10 --corpus-backend ranged`
  - Result: failed before returning priors because the corpus remote host could not be resolved (`EndpointConnectionError`). No `ranged corpus reads: ...` line was emitted because no ranged read completed.

## CourtListener MCP

- Opinion search for `"reasonable concern" "undue hardship" Groff`, filed after June 29, 2023. Result: the pre-decision Ninth Circuit opinion in *Petersen*.
- Opinion search for *Petersen v. Snohomish Regional Fire and Rescue*, Ninth Circuit, filed September 1–3, 2025. Result: docket 24-1044 and opinion ID 11131248.
- Opinion endpoint lookup for ID 11131248. Consulted the opinion's full text, including its treatment of actual versus hypothetical hardship and the record evidence supporting summary judgment.
- Opinion search for `"actual hardship" "reasonable" "Groff" "religious accommodation"`, filed after January 1, 2024. Result: no matches.
- Opinion search for `Kluge Brownsburg Smith Atlantic City Naylor Muscatine`, filed after January 1, 2025. Result: no matches because the combined query was too restrictive.
- Opinion search for *Kluge v. Brownsburg Community School Corporation*, Seventh Circuit, filed after January 1, 2025. Result: the August 5, 2025 majority and dissent, opinion IDs 11114663 and 11114662.
- Opinion search for *Smith v. City of Atlantic City*, Third Circuit, filed after January 1, 2025. Result: 138 F.4th 759, opinion ID 11062247.
- Opinion search for *Naylor v. County of Muscatine*, Eighth Circuit, filed after January 1, 2025. Result: opinion ID 11123223.
- Opinion search for *Henry v. Southern Ohio Medical Center*, Sixth Circuit, filed after January 1, 2025. Result: no match.
- Opinion search for *Rodrique v. Hearst Communications*, First Circuit, filed after January 1, 2024. Result: 126 F.4th 85, opinion ID 10783507.
- Opinion endpoint lookups for IDs 11062247 (*Smith*), 11123223 (*Naylor*), 10783507 (*Rodrique*), and 11114663 (*Kluge*). Consulted passages concerning good faith, actual hardship, reasonable reliance, and summary judgment.

No web searches were used. No search sought this petition's disposition or post-disposition history.
