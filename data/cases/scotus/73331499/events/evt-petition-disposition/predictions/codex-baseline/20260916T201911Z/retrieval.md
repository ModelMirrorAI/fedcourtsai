# Retrieval log

## Local inputs and general context

- Read AGENTS.md, the prediction prompt, prediction/flags/tooling schemas, the cell event definition, case-level context, September 16 snapshot, document manifest, QP extract, and petition text. No outcome file or other predictor output was read.
- Consulted `metrics/statpack.md`: modern discretionary-cert population, paid-segment relist/CVSG cuts, and the sal-v4 reached-band Term table. Computed the prior-Term baseline pool in Python, using only 2017–2024 rows: weighted denominator 11580, approximate weighted rate 0.0512025. No `fedcourts query`, `open-events`, or live corpus lookup was used, so there is no ranged-corpus transfer line.
- Ran `uv run fedcourts paths --court scotus --docket 73331499 --event evt-petition-disposition --role predictor`. The default cache was read-only; retry with a writable temporary cache succeeded. The command exposed no outcome content. Read path/ID/serialization helpers and schema definitions for output construction and validation only.

## Web searches

Two search calls, each containing two queries, returned no usable source text:

1. `State v Belt 179 P.3d 443 2008 DNA warrant unique profile`
2. `United States v Davis 690 F.3d 226 2012 DNA victim clothing search`
3. `site.jud.ct.gov "State v. Police" "273" "2022"`
4. `site.courts.state.md.us Raynor 2014 DNA 69a13`

No web result was used as substantive evidence.

## CourtListener MCP

1. Opinion search, citation `273 A.3d 211`, limit 1: returned an unrelated New Jersey case. Disregarded it.
2. Opinion search, `caseName:"State v. Police"`, limit 3: identified the Connecticut Supreme Court decision dated May 10, 2022, 343 Conn. 274, cluster 6466656; unrelated results disregarded.
3. `search_document`, opinion 6338767, literal `must contain`, context 900: no text available.
4. `search_document`, alternate opinion 11297773, literal `must contain`, context 900: read the holding's DNA-profile identification/statistical-rarity requirement, with surrounding discussion. Used to corroborate petition pages 15–16.
5. Opinion search, `caseName:"State v. Belt"`, court `kan`, limit 2: identified the March 28, 2008 decision, 179 P.3d 443 / 285 Kan. 949, opinion 2635856. Did not use the unrelated 2016 case.
6. `search_document`, opinion 2635856, literal `neither`, context 1400: read excerpts describing absent unique profiles, external FBI records, and the warrant/affidavit particularity analysis. Used to assess the specificity of the asserted conflict.

These were searches for general pre-existing authorities, not for Williams's disposition, subsequent litigation, or decision coverage. No outcome-revealing material about this cell surfaced.
