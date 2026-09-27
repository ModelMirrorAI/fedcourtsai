# Retrieval record

## Local sources beyond the provisioned record

- Read the interim-docket section of metrics/statpack.md and the corresponding terms in metrics/statpack.json. Computed the 2016–2025 pool with jq: 31 grants / 296 resolved = 0.10472972972972973. No same-Term rate was used.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json`: 96ebdd342, 2026-09-26T12:03:37Z. This dates the committed artifact, not its underlying corpus refresh.
- Attempted `uv run fedcourts corpus-info` with the uv cache redirected to /tmp. It failed because the service backend has no client-side connection. It returned no corpus records, vintage, or ranged-read transfer line. No `fedcourts query` or `open-events` lookup was made.
- Used `fedcourts paths` to resolve the cell paths. Its first invocation failed because the default uv cache was read-only; the invocation with a /tmp cache succeeded. Read the task contract and output schemas. These were administrative/validation reads, not case retrieval.

## Web attempts: no results supplied

The following web calls returned no usable content, snippets, or sources; none informed the forecast:

1. Search queries `site.supremecourt.gov 22A184 Yeshiva September 14 2022 application denied` and `site.supremecourt.gov Hollingsworth Perry stay reasonable probability fair prospect 2010`.
2. Search query `Yeshiva University YU Pride Alliance 22A184 Supreme Court September 14 2022 pdf`.
3. Attempted opening of `https://www.supremecourt.gov/opinions/21pdf/22a184_new_0971.pdf`.

These concerned general preexisting precedent, not the target application.

## CourtListener MCP

1. Opinion search: query `"Yeshiva" "Pride"`, court `scotus`, filed_before `2026-09-24`, num_results 3. Returned zero results; no comparator opinion read.
2. Opinion search: citation `556 U.S. 418`, num_results 1. Returned Nken v. Holder, April 22, 2009, opinion 145884. Used for general stay principles only.
3. Opinion-text search: opinion_id 145884, query `four factors`, snippet_size 1200. Read the returned excerpts around reporter pages 426 and 434. No target-case facts were returned.

No target-case docket lookup, outcome lookup, bulk prior query, or later case coverage was sought or read.
