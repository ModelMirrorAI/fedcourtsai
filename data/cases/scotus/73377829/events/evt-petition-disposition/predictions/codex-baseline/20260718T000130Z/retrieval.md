# Retrieval beyond the provisioned inputs

## Corpus priors

- `fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - `ranged corpus reads: 146 GET(s), 38273024 byte(s)`
  - Returned five recent grant-side SCOTUS priors. They were used only as broad procedural priors because none was a close subject-matter analogue.
- `fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
  - `ranged corpus reads: 205 GET(s), 53608448 byte(s)`
  - Returned five recent denial-side SCOTUS priors, including two Fourth Circuit matters. They were used only as broad procedural priors.
- `metrics/statpack.md` and `metrics/statpack.json`
  - Consulted the modern discretionary-cert, originating-circuit, relist, CVSG, Term, and paid-fee-class cuts.

## CourtListener MCP

All searches were limited to opinions filed before July 18, 2026. No search sought this petition's disposition or subsequent history, and no outcome-revealing material surfaced.

- Opinion search: `"Employment Dispute Resolution Plan" judiciary due process` (10 results). Relevant results included *Semper*, the 2022 *Strickland* appeal, *In re Levenson*, and *Dotson v. Griesa*.
- Opinion search: `("judiciary employees" OR "judicial employees") Title VII "EDR Plan"` (10-result request). Relevant results included the two provisioned lower-court *Strickland* opinions, *Golinski*, and *Dotson*.
- Opinion search: `"Dotson v. Griesa"` (5 results). Used to identify the reported Second Circuit authority and its CourtListener opinion record.
- Opinion search: `"Semper v. Gomez" OR "Semper v. United States"` (8-result request). The request was throttled and returned no usable results.
- Opinion search: `"In re Levenson" OR "In re Golinski"` (8 results). Used to identify the Ninth Circuit EDR authorities and short result snippets.
- Full-text opinion-item requests for CourtListener opinion IDs 789247 (*Dotson*), 1345538 (*Golinski*), 1227304 (*Levenson*), and 808128 (*Semper*) were throttled and returned no opinion text.
- A later full-text retry for opinion ID 789247 was also throttled and returned no opinion text.

The successful search results helped confirm the narrow EDR precedent set. Because full-text retrieval was throttled, substantive analysis of those cases came from the provisioned petition and its appended lower-court opinion.
