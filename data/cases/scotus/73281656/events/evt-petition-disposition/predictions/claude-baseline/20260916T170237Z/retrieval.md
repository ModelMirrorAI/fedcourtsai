# Retrieval log

Beyond the provisioned snapshot, context, event definition, and the three
provisioned documents, I consulted:

## Committed base rates
- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "Cert petitions by relist count / by CVSG status / by capital-case marking
  (paid scored segment)", "Cert petitions by salience band", "Petitions by
  originating court", "SCOTUS cert petitions by Term", and "Segment base rate
  by salience band (sal-v4)".

## Corpus tooling
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 8 "<free text>"`
  — rejected (the command takes no free-text argument); no transfer line.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  — stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned four
  recent granted interim applications and Jouppi v. Alaska (25-246); low
  relevance to this cell, used only to confirm the tooling worked.

## CourtListener MCP
1. `search` (type `o`, court `sc`, filed after 2025-10-01, q: Lindsey v. State
   Strickland prejudice mitigation "proposed order") — found cluster 10731109,
   Lindsey v. State, S.C., Nov 5, 2025, docket 2019-001271.
2. `search` (type `r`, court `scd`, q: Lindsey v. Anderson, filed after
   2026-01-01) — found docket 72259244, No. 2:26-cv-00560, 28 U.S.C. § 2254
   petition with stay of execution.
3. `call_endpoint` `docket-entries` for docket 72259244 (15 newest) — May 15,
   2026 text order granting an indefinite stay of execution under § 2251(a)(1)
   pending the habeas case; respondents did not object.
4. `call_endpoint` `opinions` for cluster 10731109 (plain text) — searched the
   text for "cumulative", "in conjunction", "in isolation", "Thornell",
   "we hold", and the Strickland prejudice standard; read those excerpts only.

## Web search
- WebSearch: "Marion Lindsey South Carolina death row execution date 2026" —
  no execution date for this petitioner surfaced; results concerned other
  South Carolina inmates and a general profile page. Nothing about this
  petition's disposition was seen.
