# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. Relevant estimates were: modern CVSG petitions, 27.1% granted (59 resolved); Term 2025 paid petitions, 5.4% granted; modern petitions from the Ninth Circuit, 3.0% granted; and all Term 2025 petitions, 2.5% granted.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation '596 U.S. 832' --limit 8 --corpus-backend ranged`
- Result: failed before producing results because the remote corpus endpoint could not be resolved. It printed no `ranged corpus reads: ...` line, so no corpus priors were consulted.

## CourtListener MCP

- Searched opinions in the Second, Third, and Fourth Circuits for `"intergovernmental immunity" "federal contractor" state regulation`; results included *United States v. Virginia*, 139 F.3d 984 (4th Cir. 1998).
- Searched for *CoreCivic Inc. v. Governor of New Jersey* and confirmed the July 22, 2025 Third Circuit opinion.
- Searched for *GEO Group, Inc. v. Menocal* and confirmed the February 25, 2026 Supreme Court opinion.
- Retrieved the *Menocal* opinion text. Its syllabus states that Yearsley supplies a merits defense, not immunity from suit, and the opinion rejects transferring sovereign immunity to government agents merely because they perform government work.

No search sought this case's disposition or post-snapshot docket history.
