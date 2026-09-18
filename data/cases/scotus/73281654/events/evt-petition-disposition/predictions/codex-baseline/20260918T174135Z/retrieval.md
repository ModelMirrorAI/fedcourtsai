# Retrieval record

## Provisioned inputs

Read the event definition, snapshot `2026-09-17.json`, context, document inventory, questions presented, and substantive and procedural portions of the petition and opposition. The reply is docketed but not provisioned; it was not retrieved. No outcome file or other predictor's output was read.

## Committed aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert disposition counts, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table. Pooled only displayed elevated-band rows for Terms 2017–2024. Inspected the top-level keys of `metrics/statpack.json`, but did not use additional numerical data from it.
- Ran `git log -1 --format='%cI %h' -- metrics/statpack.md`; the available pack's last modifying commit date is September 14, 2026. This does not establish the underlying corpus's pull freshness.
- Ran local arithmetic on the displayed rounded rates: reached elevated approximately 0.172379, weighted n=2810; whole modern-cert grant-family share approximately 0.028192, used only as descriptive background.
- No `fedcourts query` or `open-events` calls; no ranged corpus reads or transfer lines.

## External retrieval, in order

1. Web search: `site.supremecourt.gov opinions 2022 21-1484 Arizona Navajo June 22 2023 pdf`. The tool returned no usable result text.
2. Web open of the official precedent PDF at `https://www.supremecourt.gov/opinions/22pdf/21-1484_aplc.pdf`. The tool returned no usable content. This was an attempt to verify the 2023 precedent, not to retrieve this petition's disposition.
3. CourtListener MCP `search(type="o", citation="599 U.S. 555", num_results=1)`. Returned Arizona v. Navajo Nation, filed June 22, 2023, cluster 10049670, combined opinion 10516270. No pagination was used.
4. CourtListener MCP `search_document(opinion_id=10516270, query="interfered", snippet_size=1200)`. Returned two passages explaining the distinction between federal interference with water access and requested affirmative steps, together with the majority's specific-duty requirement.
5. CourtListener MCP `search_document(opinion_id=10516270, query="common-law trust", snippet_size=1400)`. Returned the syllabus and majority passages on textually grounded duties and the limits of importing common-law trust obligations.

The retrieved authority is Arizona v. Navajo Nation, 599 U.S. 555, 558–59, 563–66 (2023). Only the specified excerpts, not its full opinion, were consulted. The unsuccessful web calls added no information; the MCP excerpts informed the narrow doctrinal assessment in `reasoning.md`. No search sought Winnemucca's disposition, current docket, or subsequent history, and no such outcome was encountered.

## Operational calls

Read the repository contract and relevant JSON schemas. Ran `fedcourts paths --court scotus --docket 73281654 --event evt-petition-disposition --role predictor` through `uv run`; the first invocation could not initialize the default cache, and a retry using a writable temporary cache succeeded. These operational calls did not retrieve legal outcomes or corpus priors. Validation is a schema/artifact check, not substantive retrieval.
