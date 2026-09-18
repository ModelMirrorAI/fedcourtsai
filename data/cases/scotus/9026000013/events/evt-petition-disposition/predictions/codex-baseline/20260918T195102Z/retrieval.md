# Retrieval record

## Provisioned material

Read the event definition, September 18, 2026 snapshot, context, document manifest, questions presented, the petition's substantive argument and selected available appendix passages, and the complete brief in opposition. No other prediction or outcome file was opened. File-path discovery listed earlier prediction filenames but their contents were not read.

## Committed aggregate context

- Consulted `metrics/statpack.md`: modern cert, originating circuit, paid relist/CVSG/capital cuts, and the sal-v4 prior-Term risk-set table. Used `metrics/statpack.json` for exact baseline reached rates and denominators, not case-level membership.
- Calculation: select Terms 2017 through 2025 with salience version sal-v4, take each baseline segment's `prefix_weighted_resolved` and `prefix_est_grant_rate`, and pool denominator-weighted rates. Result: 638 / 12,720 = 0.05015723270440252.
- `git log -1 --format='%h %cI' -- metrics/statpack.json` returned `55121cdb8 2026-09-14T11:02:00Z`; this identifies commit vintage only.
- No `fedcourts query` or `open-events` lookup was made, and no ranged-corpus transfer line was emitted. `fedcourts paths --court scotus --docket 9026000013 --event evt-petition-disposition --role predictor` resolved paths without retrieving a docket. The first attempt failed on a read-only default uv cache; retry with a writable temporary cache succeeded.

## CourtListener MCP

1. `search(type="o", citation="389 U.S. 90", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])`: returned Federal Express Corp. v. Holowecki (2008), not the requested authority. Disregarded that unrelated historical result; did not open its opinion.
2. `search(type="o", q='caseName:"Will v. United States"', court="scotus", filed_after="1967-01-01", filed_before="1967-12-31", num_results=3, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])`: located Will, 389 U.S. 90 (November 13, 1967), combined opinion 107539, plus the earlier cert order. Used only the 389 U.S. 90 opinion.
3. `search_document(opinion_id=107539, query="do not decide", snippet_size=1100)`: located discussion and footnotes about the unresolved jurisdictional question and abuse-of-discretion ground.
4. `search_document(opinion_id=107539, query="under what circumstances", snippet_size=1300)`: verified the reservation at page 98 concerning procedural orders not effectively dismissing a prosecution. Also returned a later historical passage concerning La Buy. No search targeted the present petition, its disposition, or later history.

## Web attempts

- Search query: `site.supremecourt.gov "Rule 10" "Considerations Governing Review"`. The tool returned no usable result or source text.
- Attempted to open `https://www.supremecourt.gov/ctrules/2023RulesoftheCourt.pdf`. The tool returned no usable content. I do not claim to have verified the current rulebook from this attempt, and no substantive forecast rests on it.

All externally retrieved substantive authority used in the forecast predates the provisioned snapshot. No target-case outcome material was surfaced.
