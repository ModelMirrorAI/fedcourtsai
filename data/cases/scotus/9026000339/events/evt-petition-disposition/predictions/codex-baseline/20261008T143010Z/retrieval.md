# Retrieval record

## Provisioned inputs

Read the event definition and the case-level snapshot `2026-10-08.json`, context, document manifest, questions presented, and petition. No opposition, appendix text, or amicus text was provisioned or retrieved. No own-case outcome or current external docket lookup was performed.

## Committed aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert disposition, originating-court, paid relist, paid CVSG, and sal-v4 segment tables. A broader heading/Term search also displayed unrelated interim and merits rows; these were not used as cert anchors.
- Read `metrics/statpack.json` for unrounded sal-v4 baseline reached rates. Selected displayed Terms 2017–2025 and summed `prefix_est_grant_rate * prefix_weighted_resolved`, divided by the sum of `prefix_weighted_resolved`: 638 / 12,720. No individual corpus cases were queried.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus-transfer line was produced.

## CourtListener MCP

1. `search(type="o", citation="348 F.3d 244", num_results=3)` returned Tango Music and an irrelevant Louisiana discovery opinion. Used only the Tango Music result.
2. `read_document(opinion_id=784045, chunk_index=0, chunk_size=6500)` supplied the beginning of Tango Music's jurisdictional analysis. Used the court's own description of the citizenship alignment and section 1332(a)(3) holding.
3. `search(type="o", case_name="Grupo Dataflux v. Atlas", court="scotus", filed_before="2004-06-01", num_results=2, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])` returned the 2004 merits decision and a 2003 certiorari order for that older precedent. That historical grant is not the outcome of this cell's case.
4. `read_document(opinion_id=9434608, chunk_index=0, chunk_size=7000)` supplied the opening of Grupo Dataflux's majority opinion. Used its time-of-filing issue and citizenship alignment. Did not read the full opinion or independently inspect its footnote 8.

## Web attempts

- Search query: `"Tango Music" "Deadquick" "348" diversity citizenship`.
- Search query: `"Leland" "De Havilland" "1993" diversity`.
- Search query: `site.supremecourt.gov opinions Grupo Dataflux 02-1689 2004`.

The web tool returned no usable result content for these requests. No web-source proposition was incorporated; the precedent checks relied on the MCP excerpts instead.

## Operational reads

Read the prediction contract, repository instructions, and prediction/tooling/flags schemas. Ran `fedcourts paths --court scotus --docket 9026000339 --event evt-petition-disposition --role predictor`; the initial uv invocation failed on a read-only cache and the retry with a temporary writable cache succeeded. These are path/schema operations, not corpus retrieval. A git status listing exposed filenames of pre-existing workspace changes only; none of those unrelated files was opened or used.
