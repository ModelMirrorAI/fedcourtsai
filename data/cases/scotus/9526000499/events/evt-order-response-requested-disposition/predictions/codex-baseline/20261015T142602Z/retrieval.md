# Retrieval record

## Local materials beyond the provisioned case record

- Read the task contract and prediction/tooling/flags schemas for artifact requirements.
- Read `metrics/statpack.md`, specifically the interim application section, and the matching `interim.terms` values in `metrics/statpack.json`. Pooled Terms 2016–2025: 53 grants / 549 substantive resolutions. No corpus `query` or `open-events` call was made; no ranged-corpus transfer line was produced.
- Ran `uv run fedcourts paths --court scotus --docket 9526000499 --event evt-order-response-requested-disposition --role predictor`. The initial attempt could not write the default uv cache; retrying with the cache redirected to `/tmp/uv-cache` succeeded. This resolved paths only, not docket facts or outcomes.

## Web attempts

These calls returned no usable visible results or document text and contributed no evidence:

1. Searches: `site.supremecourt.gov opinions Coinbase Bielski 2023 22-105 stay` and `site.uscode.house.gov 28 1447 c State court may thereupon proceed`.
2. Searches: `Coinbase Bielski 22-105 supremecourt.gov 2023 opinion` and `28 USC 1447 c State court may thereupon proceed uscode`.
3. Open: `https://www.supremecourt.gov/opinions/22pdf/22-105_5536.pdf`.

## CourtListener MCP

1. `search(type="o", case_name="Coinbase v. Bielski", filed_before="2026-10-15", num_results=3)`. Returned the 2023 Supreme Court decision and a Ninth Circuit decision. Selected Supreme Court opinion ID `10516266`, citation 599 U.S. 736, decided June 23, 2023. Search query ID: `5586a26e`.
2. `search_document(opinion_id=10516266, query="entire case", snippet_size=1100)`. Read the majority's forum-question rationale and related dissent excerpts. Used as general legal context, not evidence about the target application's disposition.
3. `search(type="o", citation="139 F.4th 763", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Located *People of the State of California v. Express Scripts, Inc.*, decided June 2, 2025, opinion ID `11063199`. Search query ID: `9858c221`.
4. `read_document(opinion_id=11063199, chunk_index=0, chunk_size=20000)`. Read the available opening portion of the Ninth Circuit opinion addressing automatic versus discretionary stays in federal-officer-removal litigation. This independently supports the existence of the applicant's described Ninth Circuit position; it does not verify all the other circuits' recent decisions.
5. `search(type="o", q='"Western Airlines" "demonstrably wrong"', court="scotus", filed_before="2026-10-15", num_results=3, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Returned *Western Airlines* (1987), a 2013 stay-vacatur concurrence, and *Alabama Association of Realtors* (2021). Search query ID: `f384b0fa`.
6. `read_document(opinion_id=111855)`. Requested *Western Airlines*, 480 U.S. 1301; the visible return was truncated. Used this older decision for the standard governing intervention against appellate interim relief.
7. `search_document(opinion_id=111855, query="demonstrably", snippet_size=1600)`. Read the complete relevant passage discussing serious irreparable injury and demonstrable error in applying accepted standards.

No search sought this application's outcome or subsequent history. No current target-case docket, evaluation, prior prediction, or outcome artifact was read. The application itself mentions other proceedings; those pre-decision references were treated as applicant-supplied context, not independently updated.
