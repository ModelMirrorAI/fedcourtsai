# Retrieval

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --citation '362 U.S. 257' --citation '462 U.S. 213' --citation '541 U.S. 36' --citation '590 U.S. 83' --limit 10 --corpus-backend ranged`
  - Failed before returning results because the runner could not resolve the corpus remote's host. It printed no `ranged corpus reads: ...` line, so no completed corpus transfer is reportable.

## Base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition grant estimate (5.36%).

## CourtListener MCP

All searches were limited to pre-decision case law and did not seek this petition's disposition.

- Opinion search: `"Jones v. United States" "Oath or affirmation" hearsay warrant` (filed before 2026-07-17). This located the established warrant-hearsay line and later courts applying it.
- Opinion search: `"firsthand knowledge" "Warrant Clause" Jones hearsay` (filed before 2026-07-17). This returned *United States v. Tiem Trinh*, 665 F.3d 1 (1st Cir. 2011), and *United States v. John Martin*, 615 F.2d 318 (5th Cir. 1980).
- Supreme Court opinion search: `"362 U.S. 257" hearsay warrant` (filed before 2026-07-17, newest first). Results included *Illinois v. Gates*, *Franks v. Delaware*, *United States v. Leon*, and the earlier informant-warrant cases; no recent Supreme Court merits development appeared in the returned set.
- Case-name search for *United States v. Tiem Trinh* and an opinion-endpoint lookup for opinion 619334. The opinion applied the conventional *Gates* and *Leon* framework to an informant-supported warrant.
- Opinion search: `"witness with firsthand knowledge" "Oath or affirmation"` (filed before 2026-07-17). It returned no results.
