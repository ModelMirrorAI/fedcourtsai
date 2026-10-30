# Retrieval Log

## 1. Provisioned Case Record & Local Artifacts Read
- `data/cases/scotus/9026000022/events/evt-order-call-for-response-disposition/event.yaml`: Read event metadata (`stage: cert`, `moment: response-requested`, `opened_at: '2026-08-26'`).
- `data/cases/scotus/9026000022/record/context.json`: Read conditioning context (`band: "state"`, `salience_version: "sal-v4"`, `cutoff: "2026-08-27"`, `distribution_count: 1`, `cvsg_date: null`, `mode: "forward"`).
- `data/cases/scotus/9026000022/record/snapshots/2026-08-27.json`: Read docket snapshot showing docketing on July 7, 2026, waiver on July 24, 2026, distribution on August 5, 2026 for the September 28, 2026 conference, and response requested on August 26, 2026.
- `data/cases/scotus/9026000022/record/documents/documents.json`, `questions-presented.txt`, and `petition.txt`: Read the Question Presented, the Petition for a Writ of Certiorari, and the appended Ninth Circuit majority opinion (Judges Christen and Bade) and dissent (Judge VanDyke), as well as the District Court of Guam order denying Rule 60(b)(5) relief.
- `metrics/statpack.md` and `metrics/statpack.json`: Read strictly-prior Term base rates (OT2017–OT2025) for the `state` salience band under `sal-v4` (risk-set grant rate of 24.41% across 426 resolved petitions; terminal `state` grant rate of 20.40%) and the paid grant-family cert-order summary disposition share (~35.4%–35.5%).

## 2. Corpus Queries (`uv run fedcourts query`)
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`: Retrieved recent 2020s SCOTUS granted priors (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`) to inspect recent grant trajectories and salience scores.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`: Retrieved recent 2020s SCOTUS denied priors (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`).
- `uv run fedcourts query --court scotus --citation "597 U.S. 215" --limit 5` and `uv run fedcourts query --court scotus --judge VanDyke --limit 5`: Checked for overlap on *Dobbs* citation or Judge VanDyke (no SCOTUS rows returned, as expected since SCOTUS rows do not populate lower-court panel judges or citing-case graphs).

## 3. External Tool Calls (CourtListener MCP)
- `mcp_courtlistener_search` (`type="o"`, `court="ca9"`, `case_name="Guam Society of Obstetricians v. Moylan"`): Attempted to query the Ninth Circuit opinion record on CourtListener; received HTTP 429 rate-limit error (`Request was throttled. Rate limit exceeded: 1400/day`). No retry was needed because the full text of the Ninth Circuit majority and dissenting opinions and the District Court order are already reproduced in the provisioned `petition.txt` appendix.
