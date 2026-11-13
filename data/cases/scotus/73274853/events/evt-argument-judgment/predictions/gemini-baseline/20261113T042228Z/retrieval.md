# Retrieval Log (`scotus/73274853`, `evt-argument-judgment`)

All consultations beyond the provisioned inputs under `data/cases/scotus/73274853/record/` and `events/evt-argument-judgment/event.yaml` are logged below, including failed CLI invocations and committed workspace reference tables. No lookup sought this case's own outcome, subsequent history, or any external forecast.

## 1. Corpus CLI Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73274853" --event "evt-argument-judgment" --role predictor` (plus `uv run fedcourts query --help`)
   - Resolved cell paths (`case_id scotus/73274853`, `corpus corpus/corpus.db`, `event .../event.yaml`) and inspected CLI flags.
2. `uv run fedcourts query --court scotus --citation "594 U.S. 482" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows with note explaining that only 195 SCOTUS rows in scope carry parallel reporter citations (*PennEast Pipeline Co. v. New Jersey* was not among those 195 rows).
3. `uv run fedcourts query --court scotus --era roberts --disposition granted --limit 10`
   - Failed (`Exit Code: 2`): `Unknown era 'roberts'; an era is one decade token` (printed decade-token help).
4. `uv run fedcourts open-events --court scotus --stage merits`
   - Failed (`Exit Code: 2`): `No such option: --stage`.
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr transfer line: `ranged corpus reads: 39 GET(s), 10158080 byte(s)`
   - Returned 10 recent 2020s granted SCOTUS rows (`26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`), confirming corpus connectivity and recent OT2026 grant context.
6. `uv run fedcourts open-events --help && uv run fedcourts open-events --court scotus`
   - Failed (`Exit Code: 2` on the second command): `open-events` requires naming a single case via `--docket` or `--docket-number`.

## 2. CourtListener MCP Lookups (Cited Precedents Only)

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Hencely v. Fluor", fields=["caseName", "dateFiled", "citation", "judge", "cluster_id", "opinions"], num_results=5)`
   - Returned 1 result: *Hencely v. Fluor Corp.*, No. 24-924, decided `2026-04-22`, cluster `10846666`, opinion `11314033`, authored by Justice Clarence Thomas (cited repeatedly by Petitioners' counsel at oral argument).
2. `mcp_courtlistener_read_document(opinion_id=11314033, chunk_index=0, chunk_size=5000)`
   - Read chunk 0 (Syllabus, pp. 1–2) of *Hencely v. Fluor Corp.*, confirming its *Boyle* / FTCA combatant-activities contractor-preemption holding and Justice Thomas's authorship.
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="PennEast Pipeline Co. v. New Jersey", fields=["caseName", "dateFiled", "citation", "judge", "cluster_id"], num_results=5)`
   - Returned 1 result: *PennEast Pipeline Co. v. New Jersey*, `594 U.S. 482` (`2021-06-29`), cluster `4895709`, authored by Chief Justice John G. Roberts.
4. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=4895709, fields=["case_name", "date_filed", "judges", "sub_opinions"])`
   - Returned cluster metadata and sub-opinion URL (`opinion_id=4699488`) for *PennEast*.
5. `mcp_courtlistener_read_document(opinion_id=4699488, chunk_index=0, chunk_size=4000)`
   - Read chunk 0 (Syllabus, pp. 1–2) of *PennEast Pipeline Co. v. New Jersey*, confirming its holding that 15 U.S.C. § 717f(h) delegates the federal eminent-domain power to FERC certificate holders.

## 3. Committed Workspace Reference Files Consulted

- `metrics/statpack.md` and `metrics/statpack.json` (read-only Python aggregation over `merits`, `justice_votes`, and `authorship` strictly before `grant_term = 2025`, i.e., `OT2017`–`OT2024` for merits disturbed rate and `OT2020`–`OT2024` for per-Justice votes and authorship).
- `data/schedule/term-calendar.json` and `data/schedule/schedule.json` (checked OT2026 conference and upcoming argument calendar context).
- `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`.

## 4. Web Searches

- None.
