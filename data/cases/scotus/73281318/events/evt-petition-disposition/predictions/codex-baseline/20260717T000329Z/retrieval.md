# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition rates, relist and CVSG cuts, originating-court cuts, and the 2025 Term row.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.3649956% granted).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation '547 U.S. 398' --era 2020s --limit 8`
- Result: failed before returning any priors because the runner could not resolve the corpus-store host. No `ranged corpus reads: ...` line was produced.

## CourtListener MCP

- Searched Supreme Court opinions filed before 2026-07-17 for `"emergency aid" "Brigham City"`, requesting case name, filing date, citation, and URL metadata. The results included *Brigham City v. Stuart*, *Case v. Montana*, *Michigan v. Fisher*, *Caniglia v. Strom*, and related Fourth Amendment decisions. This was a precedent search only; I did not search for this petition's disposition.

No web searches were used.
