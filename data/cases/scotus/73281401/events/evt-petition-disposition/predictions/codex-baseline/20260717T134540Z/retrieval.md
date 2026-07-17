# Retrieval beyond the provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist, CVSG, and per-Term sections.
- Consulted the 2025 paid-petition detail in `metrics/statpack.json` (estimated grant rate 5.36%).

## Corpus prior queries

Each command failed because the ranged corpus host could not be resolved. No result rows or `ranged corpus reads: …` line were produced.

- `uv run fedcourts query --court scotus --era 2020s --citation "550 U.S. 372" --limit 8`
- `uv run fedcourts query --court scotus --era 2020s --citation "471 U.S. 1" --limit 8`
- `uv run fedcourts query --court scotus --era 2020s --citation "580 U.S. 73" --limit 8`

## CourtListener MCP

- Opinion search for `"blatantly contradicts" video "motion to dismiss"` in the Sixth, Tenth, and Eleventh Circuits: no results.
- Case-name searches for *Bell v. City of Southfield*, *Johnson v. City of Atlanta*, and *Chrestman v. Metropolitan Government of Nashville*: confirmed published *Bell*, 37 F.4th 362 (6th Cir. 2022), and *Johnson*, 107 F.4th 1292 (11th Cir. 2024); the *Chrestman* query returned no result.
- Citation searches for 37 F.4th 362 and 107 F.4th 1292: confirmed the same authorities and their CourtListener opinion records.
- Phrase searches for video/blatant-contradiction authorities in the Sixth, Tenth, and Eleventh Circuits: surfaced *Bell* and three Tenth Circuit decisions, including the provisioned lower-court opinion and *Estate of Richard Ward v. Lucero* (June 10, 2026). No petition disposition or other post-snapshot information was sought or surfaced.
- Retrieved the CourtListener cluster schema, the limited cluster record for *Estate of Ward*, and its published opinion text. The decision involved summary judgment, held the video did not utterly discredit the plaintiff's account, and was used only as pre-snapshot context on recurrence and procedural posture.

No general web search was used.
