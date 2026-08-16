# Retrieval log

Beyond the provisioned inputs (snapshot, petition.txt, questions-presented.txt,
event.yaml, context.json) and the committed `metrics/statpack.md` /
`docs/salience.md`:

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --limit 8 --corpus-backend service`
  — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned
  recency-ranked recent SCOTUS rows (capital-case and application dockets),
  nothing similar to this case; not used for the number.

## CourtListener MCP

- `search` (opinions, court=scotus): `"attorney general" disqualification
  prosecutor "due process" Guam OR territory` — top results are unrelated
  criminal-procedure cases (Uttecht, Padilla, J.D.B., Stincer,
  Gonzalez-Lopez); no SCOTUS precedent line on summary disqualification of a
  prosecuting office. Supports the no-conflict read.
- `search` (opinions, all courts, newest first): `Moylan "attorney general of
  Guam"` — surfaced Guam Society of Obstetricians v. Moylan (CA9 2026),
  In re Application of the People of Guam (Guam 2024), Raidoo v. Moylan
  (CA9 2023), and Limtiaco v. Camacho (SCOTUS 2007) — confirming grants from
  the Supreme Court of Guam are rare but not unprecedented. Context only.

No web searches. No lookups touching this case's own disposition (the petition
is pending; response due 2026-08-26).
