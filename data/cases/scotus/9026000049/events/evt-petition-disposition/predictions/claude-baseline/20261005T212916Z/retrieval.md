# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
  stderr: `ranged corpus reads: 35 GET(s), 9043968 byte(s)`
  Returned 15 recent granted SCOTUS rows (mostly 2026 grants and substantive applications); no subject filter isolates immigration-preemption petitions, so these did not shape the forecast.
- `uv run fedcourts open-events --court scotus` piped through a grep for Texas / immigration / Uthmeier / Drummond / Las Americas / El Paso / reentry: no matching open events printed (no transfer line is printed by `open-events`).
- Base rates: the committed `metrics/statpack.md`, sections "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP (forward mode, 10 calls)

1. `search` opinions, court ca5, q `"United States v. Texas" SB4 preemption en banc`, filed after 2025-01-01: one hit, United States v. State of Texas, No. 24-50149, filed 2026-04-24 (cluster 10847941).
2. `search` opinions, q `"Padres Unidos" Drummond OR "Florida Immigrant Coalition" Uthmeier`, filed after 2025-01-01: no results.
3. `search` opinions, q `"Iowa Migrant Movement for Justice"`: one hit, the Eighth Circuit opinion of 2025-10-23 (cluster 10709610), which is the decision under review and already in the petition appendix; not opened.
4. `get_endpoint_item` clusters 10847941: sub-opinion 11315316, no syllabus.
5. `search` opinions, court ca11, q on Florida Immigrant Coalition / Uthmeier / SB 4-C, filed after 2025-10-01: no results.
6. `search` opinions, court ca10, q on Drummond / Padres Unidos / HB 4156, filed after 2026-01-01: six unrelated Drummond cases, none the Oklahoma immigration appeal.
7. `search` dockets, court scotus, q on Las Americas / El Paso County / Florida Immigrant Coalition / Padres Unidos / Uthmeier, filed after 2025-06-01: no results.
8. `read_document` opinion 11315316, chunk 0 of 77 (6000 chars): the en banc Fifth Circuit (Smith, J.) vacated the SB4 preliminary injunction for lack of standing without reaching preemption.
9. `search` opinions, court ca10, docket number 25-6080: no results.
10. `search` opinions, court ca11, docket number 25-11469: no results.

No web searches. Nothing retrieved concerned this petition's own disposition; the petition is distributed for the 10/9/2026 conference and undecided as of this snapshot.
