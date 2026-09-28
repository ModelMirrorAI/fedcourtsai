# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-04.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era modern --limit 8 "<free text>"` — rejected with a usage error (the command takes no free-text argument). No corpus read.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   stderr: `ranged corpus reads: 11 GET(s), 2752512 byte(s)`
   Returned five recent granted SCOTUS matters (election-law and government-party dockets with amicus counts of 2–10). Not comparable to this petition; not used to move the number.
3. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Returned eight recent SCOTUS dockets including several pro se paid petitions (e.g. Banks v. Brown, Cheleden v. Florida DBPR, Givey v. Givey) with zero amicus briefs; consistent with the petition's class but no dispositions were relied on.

## CourtListener MCP

None. The lower-court decision is a summary California writ denial unlikely to be in CourtListener, and the provisioned petition text was sufficient.

## Web searches

None.
