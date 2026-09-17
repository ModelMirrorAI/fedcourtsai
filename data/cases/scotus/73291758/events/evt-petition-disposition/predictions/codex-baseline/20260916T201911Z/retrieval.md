# Retrieval record

No lookup targeted this case's disposition, subsequent history, current docket, or reporting about its decision. No outcome material was encountered.

## Local context

- Read metrics/statpack.md: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and sal-v4 per-Term segment table. Read corresponding metadata and Term segment fields in metrics/statpack.json. Computed the baseline reached pool for all rendered Terms 2017–2024 using the JSON's unrounded rates and weighted denominators: 593 / 11,580 = 0.0512089810. No live corpus query or open-events lookup was used; no ranged-corpus-read line was emitted.
- Ran `uv run fedcourts paths --court scotus --docket 73291758 --event evt-petition-disposition --role predictor`. The initial invocation failed because its default cache directory was read-only; rerunning with the cache under /tmp succeeded. This command resolves paths and retrieves no case outcome.
- Read the prompt, schemas, and path/serialization helpers for the file contract. Read only this cell's provisioned case input files, not another predictor's artifacts or outcome files.

## General-law lookups

1. Web search queries: `site.supremecourt.gov Rule 10 writ certiorari erroneous factual findings misapplication properly stated rule` and `site.supremecourt.gov opinions 2023 Rahimi credible threat physical safety temporarily disarmed`. The web tool returned no usable result content.
2. Two web-open attempts for the official rules guidance page, `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`, likewise returned no usable content. No factual inference was drawn from these empty responses.
3. CourtListener MCP search: type `o`, query `caseName:"United States v. Rahimi"`, court `scotus`, filed_before `2025-01-01`, num_results `2`. Returned the June 21, 2024 decision, 602 U.S. 680, including opinion ID 10145945. Only the historical decision's identity and substance were used, not its current citation counts.
4. CourtListener MCP search_document: opinion_id `10145945`, query `credible threat`, snippet_size `500`. Read excerpts on the temporary-disarmament holding, judicial threat findings, statutory prerequisites, and the limits on what was decided. This was general precedent, not litigation involving this cell's parties. No REST calls to CourtListener were made.
5. Attempted direct retrieval of the official general rules PDF, `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`, using curl piped to pdftotext. Text extraction failed because pdftotext was unavailable. Then used urllib and pypdf in memory to retrieve and extract the same PDF, once for Rule 10's opening and once for its continuation. Read official printed pp. 5–6, including the discretionary-review standard and factual-error limitation. No downloaded file was persisted. This was a public court rules document, not an alternative CourtListener access path or a lookup of this case.

The browser failures did not prevent use of the provided filings, the committed statistical context, MCP precedent excerpts, or the public rules text. No live corpus freshness was established; the statpack's underlying refresh vintage is not supplied by its metadata.
