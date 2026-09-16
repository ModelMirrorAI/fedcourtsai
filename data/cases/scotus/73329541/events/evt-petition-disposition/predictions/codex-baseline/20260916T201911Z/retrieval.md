# Retrieval log

## Local material beyond the provisioned record

- Read the task contract, applicable repository instructions, and the prediction/tooling/flags schemas.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit excerpt, paid-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table. Heading searches also surfaced other stage headings and aggregate rows; those stages were not used as anchors.
- Inspected `metrics/statpack.json` structure and pooled only baseline risk sets in displayed Terms 2017–2024: sum of `prefix_est_grant_rate * prefix_weighted_resolved` = 593; sum of `prefix_weighted_resolved` = 11,580; ratio = 0.05120898100172712. No case-level corpus query was made.
- `uv run fedcourts paths --court scotus --docket 73329541 --event evt-petition-disposition --role predictor` initially failed at the default uv cache. The same command with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This is path resolution, not corpus retrieval; there was no ranged-read transfer line.
- Used shell file inspection, UTC clock, and working-tree status for execution checks. No outcome file or labeling-artifact content was opened.

## Web attempts

All returned no visible content or sources; none supplied evidence:

1. Search: `site.supremecourt.gov opinions 24-5438 Bowe January 9 2026`.
2. Search in the same call: `site.ca10.uscourts.gov Dulworth Evans 442 1265 2006 2244`.
3. Search: `site.supremecourt.gov "Bowe" "2026" "opinion"`.
4. Attempted open of the Supreme Court Bowe opinion PDF, path `/opinions/25pdf/24-5438_o7kq.pdf`.

## CourtListener MCP

1. `search(type="o", citation="442 F.3d 1265", num_results=1)`, requesting case name, date, opinions, citation and path: returned Dulworth v. Evans, April 4, 2006, opinion 167281.
2. `read_document(opinion_id=167281)`: returned the opinion, with display truncation. Used its habeas/COA framework and subsequently requested the split passage explicitly.
3. `search(type="o", case_name="Bowe v. United States", court="scotus", num_results=3)`, requesting the same metadata: returned the January 9, 2026 decision, opinion 11239035, and two unrelated 2003 entries. Only the 2026 opinion informed the forecast.
4. `read_document(opinion_id=11239035, chunk_index=[0,1], chunk_size=7000)`: introductory facts and syllabus explaining both statutory holdings. Did not read the whole opinion or dissent.
5. `search_document(opinion_id=167281, query="Cox", snippet_size=1700)`: verified the split, the section 2241/2254 classification distinction, and the custody-based rationale at 442 F.3d 1267–68.

No lookup targeted this cell's own disposition or subsequent history. No `fedcourts query` or `open-events` call was made, so no ranged corpus-read lines were generated.
