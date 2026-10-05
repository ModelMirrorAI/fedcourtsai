# Retrieval record

## Local inputs and base rates

- Read the provisioned case-level snapshot `record/snapshots/2026-10-05.json`, context, document manifest, questions presented, and selected petition sections, together with this event's definition. No other predictor's output or outcome file was read.
- Consulted the committed `metrics/statpack.md`: modern discretionary-cert dispositions; originating circuit; paid-segment relist/CVSG cuts; and the sal-v4 per-Term reached-band table. Used a local Python calculation to pool the displayed 2017–2025 baseline reached rates, yielding approximately 0.0501089 over n=12,720. No remote corpus refresh or individual-case query was performed.
- Ran `uv run fedcourts paths --court scotus --docket 9026000208 --event evt-petition-disposition --role predictor`. The first attempt failed at the default cache location; a retry with the uv cache pointed to temporary storage succeeded. This is a path resolver, not a corpus lookup.
- No `fedcourts query` or `open-events` calls were made; consequently there are no ranged-corpus-transfer stderr lines to report.

## External background-law retrieval

1. Web search query: `site.supremecourt.gov Riley California 2014 13-132 opinion pdf warrant cell phone`. The tool returned no usable content. No target-case disposition was sought or surfaced.
2. CourtListener MCP `search`: type `o`, citation `934 F.3d 1002`, one result. Returned United States v. Miguel Cano, decided August 16, 2019; opinion ID 4426344, cluster path `/opinion/4649091/united-states-v-miguel-cano/`.
3. CourtListener MCP `search_document`: opinion 4426344, literal query `We hold`, context size 1,400. Read three excerpts, including the manual/forensic distinction and the digital-contraband limit. Used those holdings to test the petition's characterization of the split. This is another case's preexisting decision, not this petition's outcome.
4. Web open attempt: `https://www.supremecourt.gov/opinions/13pdf/13-132_8l9c.pdf`. The tool returned no usable content; no independently retrieved Riley text informed the forecast.
5. CourtListener MCP `search`: type `o`, citation `573 U.S. 373`, one result. Returned Alexander v. Alexander, 573 F. Supp. 373 (1983), rather than Riley, plus a warning that `opinions.id` was not a valid returned field. Disregarded the unrelated result; did not read its opinion.
6. CourtListener MCP `search`: type `o`, case name `Riley v. California`, court `scotus`, filed after `2014-06-24` and before `2014-06-26`, one result requested. Returned zero results. Stopped retrieval and relied on the petition's Riley discussion.

No search requested this case's present disposition, later history, or decision coverage. No outcome-revealing material concerning this event was encountered.
