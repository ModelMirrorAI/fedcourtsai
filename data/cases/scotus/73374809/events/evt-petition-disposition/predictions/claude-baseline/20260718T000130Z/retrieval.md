# Retrieval log — scotus/73374809 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Provisioned inputs read: the 2026-07-17 snapshot, `questions-presented.txt`,
`petition.txt` (17 pp., full), `documents.json`, `record/context.json`
(mode: forward), and the event definition.

Beyond the provisioned inputs:

1. Committed statpack `metrics/statpack.md` — modern discretionary-cert
   disposition base rates, relist-count cuts, CVSG cuts, originating-court
   (incl. state courts) cuts, and per-Term table.
2. `uv run fedcourts query --court scotus --era modern --limit 5`
   → no rows ("modern" is not a valid era value; eras are decades).
   stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   → 5 recent resolved SCOTUS priors (Oregon v. Maney, the two Monsanto
   grants, Petersen v. Doe, McCoy v. ATF). Used only as a sanity check on
   corpus coverage; none is profile-similar to a pro se state-licensing
   petition, so the statpack cuts carried the quantitative anchor.
   stderr: `ranged corpus reads: 430 GET(s), 112590848 byte(s)`

No CourtListener MCP lookups and no web searches: the cell is forward-mode
and retrieval was unrestricted, but the provisioned petition text plus the
docket snapshot were sufficient for a first-distribution, no-split, pro se
petition; nothing an external lookup could surface would move the estimate
materially.
