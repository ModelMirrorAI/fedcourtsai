# Retrieval

## Corpus and base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, especially modern cert disposition, Ninth Circuit, relist, CVSG, and 2025-Term paid-petition cuts.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 12`
  - `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  - Returned recent granted SCOTUS priors and their distribution/CVSG metadata.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --citation '595 U.S. 1' --limit 5`
  - No result or transfer-stat line was returned before the command ended; it did not inform the forecast.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 12`
  - Failed because the local corpus service timed out; no transfer-stat line was printed and it did not inform the forecast.

## CourtListener MCP

- Opinion search in the Supreme Court collection for `"qualified immunity" "clearly established" excessive force`, limited to January 1, 2015 through July 17, 2026. The results identified *Zorn v. Linton*, *City of Tahlequah v. Bond*, *Rivas-Villegas v. Cortesluna*, *City of Escondido v. Emmons*, *Kisela v. Hughes*, *White v. Pauly*, and *Mullenix v. Luna*, among other decisions.
- Case-name search for *Zorn v. Linton*, which identified docket 25-297 and the March 23, 2026 combined opinion.
- Opinion endpoint lookup for the combined *Zorn v. Linton* opinion. Consulted its discussion of fact-specific clearly established law, its summary reversal, and the three-Justice dissent.
- Pagination of the general qualified-immunity search to review older Supreme Court results through 2015.

No web search was used, and no retrieval sought this case's disposition or subsequent history.
