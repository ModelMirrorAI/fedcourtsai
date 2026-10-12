# Retrieval log

## Provisioned inputs

Read the cell's event definition, context, `2026-10-03.json` snapshot, document manifest, questions presented, and portions of both merits briefs. These were provisioned inputs, not external retrieval. No outcome, other prediction, or labeling-measurement artifact was read.

## Committed context and local tools

- Read the merits section of `metrics/statpack.md` and corresponding `metrics/statpack.json` structure and rows. Pooled grant Terms 2015–2024 using `jq`: 360 disturbed, 516 parsed, 539 granted, 56 separately excluded, rate 0.6976744186046512; published rows were 2017–2024.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: `3f3ca14f4 2026-10-08T21:56:24Z`. This dates the committed artifact, not the underlying corpus pull.
- Ran `uv run fedcourts paths --court scotus --docket 73280343 --event evt-brief-judgment --role predictor`. The initial attempt failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded. No outcome path was opened.
- Read task/schema contracts and the relevant path/serialization helpers for artifact production and validation. No `fedcourts query`, `open-events`, or live corpus lookup was made; there is no ranged-transfer line to report.

## Web attempts

- `web.run` search queries: `site.govinfo.gov 8 USC 1159 2024 adjustment status alien granted asylum` and `site.supremecourt.gov opinions Henson Santander 2017 582 79 past participle`. The tool returned no usable results or content.
- `web.run` open attempt for the govinfo 2024 United States Code, title 8, section 1159 HTML page. The tool returned no usable content. No information from these attempts entered the forecast.

## CourtListener MCP

1. `search(type="o", citation="582 U.S. 79", num_results=1, filed_before="2026-10-03")`: returned Henson v. Santander Consumer USA Inc., decided June 12, 2017, cluster 4403814, opinion 4181067. Only the returned result was used; no pagination.
2. `search_document(opinion_id=4181067, query="past participles", snippet_size=1800)`: read two overlapping excerpts addressing the distinction between a past participle and a historical-event requirement, plus statutory context. Used as general interpretive precedent, not as information about this case's outcome.

No search targeted this case's disposition, subsequent history, or decision coverage. No outcome-revealing material surfaced.
