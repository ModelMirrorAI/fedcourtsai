# Retrieval log

## Committed context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid scored-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table. Computed the approximately 35.49% prior-Term high-band anchor from Terms 2017–2025 using a local Python calculation. Read only the top-level key inventory, schema version, and coverage-key inventory of `metrics/statpack.json`; these expose no case outcomes.
- No `fedcourts query`, `open-events`, `stats`, or corpus pull was performed. There is no ranged-corpus transfer line to report.

## Web attempts

1. `web.run` search query: `site.uscode.house.gov 42 USC 9607 natural resources restore replace acquire equivalent`. No usable result content returned.
2. `web.run` open request: `https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title42-section9607`. No usable page content returned.

These were general statutory checks, not searches for the present case. Neither supplied evidence or outcome information.

## CourtListener MCP: historical authorities only

1. `search(type="o", citation="880 F.2d 432", num_results=1, fields=["caseName", "dateFiled", "absolute_url", "opinions", "citation"])`. Returned *Ohio v. United States Department of Interior*, July 14, 1989; selected opinion ID 7858699. Query ID: `1d89e90f`. Did not paginate the duplicate citation results.
2. `search_document(opinion_id=7858699, query="passive", snippet_size=900)`. Read one matching passage concerning recognition of option and existence values, corresponding to 880 F.2d at 464.
3. `search_document(opinion_id=7858699, query="purely private", snippet_size=650)`. Read four overlapping passages about the statute's treatment of privately owned resources, corresponding to 880 F.2d at 460.
4. `search(type="o", citation="467 F.3d 1223", num_results=1, fields=["caseName", "dateFiled", "absolute_url", "opinions", "citation"])`. Returned *State of New Mexico v. General Electric*, October 31, 2006, opinion ID 168319. Query ID: `b2695f82`.
5. `search_document(opinion_id=168319, query="interim", snippet_size=850)`. Read three passages about interim lost-use recovery, including the restoration/replacement discussion at page 1245 and footnote 39 at pages 1250–51.

These were narrow primary-source checks of the asserted split, not full-opinion reads. No lookup targeted Teck's current petition, its disposition, or its subsequent history. No current-petition outcome material surfaced.

## Local contract and operational reads

Read `AGENTS.md`, the predict prompt, applicable output schemas, and this cell's event, context, dated snapshot, document manifest, questions presented, and substantive excerpts of the petition and opposition. Searched only those two provisioned briefs for relevant arguments. Used the predictor-role paths command to confirm the event location. Its initial invocation failed on a read-only default cache; retrying with a temporary writable cache succeeded. No repository code or input data was changed.
