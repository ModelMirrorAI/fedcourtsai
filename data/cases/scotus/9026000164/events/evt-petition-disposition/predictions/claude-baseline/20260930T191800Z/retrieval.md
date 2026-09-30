# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-30.json`, `context.json`,
`documents/questions-presented.txt`, `documents/petition.txt`,
`documents/brief-in-opposition.txt`, `documents.json`) and the committed
`metrics/statpack.md`, this cell consulted the following.

## Corpus lookups (`fedcourts query`, read-only)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 42 GET(s), 10878976 byte(s)`
   Returned 20 recent SCOTUS grants (mostly OT2025 and OT2026 rows); none
   topically similar; used for shape only.
2. `uv run fedcourts query --court scotus --citation "431 U.S. 816"`
   stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   Empty; the tool printed its coverage note (only 200 SCOTUS rows carry a
   reporter citation).
3. `uv run fedcourts query --court scotus --citation "530 U.S. 57"`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Empty; same coverage note.

## CourtListener MCP lookups

1. `search` type `r`, q `Mast Afghan child adoption`, 10 results.
   Surfaced *Baby Doe v. Joshua Mast*, CA4 No. 24-1900 (filed 2024-09-18,
   terminated 2026-04-22) and *Doe v. Mast*, W.D. Va. 3:22-cv-00049 (filed
   2022-09-02, open). Remaining hits unrelated.
2. `search` type `o`, q `Mast adoption Afghanistan "due process"`, courts
   va, vactapp, ca4, vawd, vaed. Zero results.
3. `search` type `d`, q `Genalo Black`, SCOTUS and circuit courts. Zero
   results.
4. `search` type `o`, q `Genalo`, newest first. No relevant hit.

No web searches. No lookup sought this petition's disposition, and none
surfaced one.
