# Retrieval log

Beyond the provisioned inputs:

1. `uv run fedcourts query --help` — read the filter surface.
2. `uv run fedcourts query --court scotus --docket-number 25-1360` — stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Returned the open row for *Brumley v. Roake* (CA5 No. 24-30706): `distribution_count` 3, `distributed_for_conference` 2026-12-11, no CVSG, no disposition.
3. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — failed with a usage error (`modern` is not an era token); returned no rows. Not re-issued.
4. Read `metrics/statpack.md`: salience-band table (sal-v9), relist-count, CVSG and amicus-count cuts (paid scored segment).
5. Web search: "Stinson v. Fayetteville School District Eighth Circuit Ten Commandments decision" — returned coverage of the district court's permanent injunction (March 2026) and of the Sept. 22, 2026 Eighth Circuit argument; no Eighth Circuit decision found. No forecast of this case surfaced.
6. Web fetch of the Court's docket page for No. 25-1360 (supremecourt.gov) — 13 entries: petition May 21, 2026; waiver July 6; distributed for Sept. 28 conference; response requested July 28; BIO Oct. 19; distributed for Dec. 4 conference Nov. 4; rescheduled Nov. 5; distributed for Dec. 11 conference Nov. 24.

No CourtListener MCP calls were made.
