# Retrieval log — claude-baseline, scotus/73281043, evt-brief-judgment, run 20261005T153213Z

Forward cell; retrieval unrestricted. Nothing retrieved contained a disposition
of this case (argument is set for November 4, 2026).

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition granted --limit 8`
   - stderr: `ranged corpus reads: 11 GET(s), 2686976 byte(s)`
   - Returned eight recently granted SCOTUS rows (none doctrinally related);
     used only to confirm the surface works. No `--full` hydration.

## CourtListener MCP

1. `search` (opinions, court ca5, filed after 2019-01-01):
   `"Dexter Johnson" Atkins "previously unavailable"` — returned *In re Dexter
   Johnson* (19-20552, 2019-08-15) and *Johnson v. Davis (In re Johnson)*,
   935 F.3d 284 (2019-08-14). Not read in full.
2. `search` (opinions, court ca5, docket number `23-70002`) — no results.
3. `search` (opinions, court ca5, filed after 2025-01-01):
   `Johnson Guerrero Cathey "previously unavailable" 2244(b)(2)(A)` — returned
   only *Busby v. Guerrero* (26-70004, 2026-05-11), unrelated; not read.
4. `search` (opinions, court ca5, case name `Johnson v. Guerrero`, filed after
   2025-01-01) — no results.
5. `search` (opinions, court ca11):
   `Bowles "new rule" "previously unavailable" DSM-5 Atkins` — returned *In re
   Gary Ray Bowles*, 935 F.3d 1210 (2019) and *In re John Ruthell Henry*,
   757 F.3d 1151 (2014). Not read in full.

## Web

None. The Solicitor General's amicus brief and the Fifth Circuit's 2025
opinion were not fetched.

## Subagents

Three local subagents read the provisioned documents only (petition and BIO;
petitioner's merits brief; respondent's merits brief) and returned summaries.
They made no external retrievals.
