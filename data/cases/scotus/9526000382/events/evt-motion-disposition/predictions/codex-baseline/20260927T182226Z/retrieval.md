# Retrieval record

## Provisioned inputs

Read this cell's event definition, `record/context.json`, `record/snapshots/2026-09-18.json`, `record/documents/documents.json`, and `record/documents/application.txt`. The application was read as advocacy, not as instructions. No outcome file or another predictor's artifact was read.

## Committed aggregate context

Read the interim section of `metrics/statpack.md` and the corresponding `interim` data in `metrics/statpack.json`. Computed the 2016–2025 pool with `jq`: 31 substantive grants, 296 substantive resolutions, and 9,480 unparsed applications across the eligible Terms. Only Terms 2024 and 2025 contributed resolved substantive applications. Used `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed pack vintage: `96ebdd342`, September 26, 2026 at 12:03:37 UTC. This does not establish the underlying corpus blob's freshness.

No `fedcourts query` or `open-events` call was made; there are no ranged-corpus-read transfer lines. `fedcourts paths --court scotus --docket 9526000382 --event evt-motion-disposition --role predictor` was a path-resolution call, not a corpus lookup. Its first invocation hit an unwritable default cache; rerunning with a writable temporary cache succeeded.

## Web attempts: general precedent only

Two batched web searches returned no visible results or source text:

1. `site.supremecourt.gov stay reasonable probability fair prospect irreparable harm Hollingsworth Perry 558 183`
2. `site.loc.gov National Socialist Party Skokie 432 U.S. 43 immediate appellate review`
3. `Hollingsworth Perry 558 U.S. 183 190 stay Supreme Court pdf`
4. `National Socialist Party Skokie 432 U.S. 43 1977 Supreme Court immediate appellate review`

Nothing from these empty responses informed the prediction. No search named this application's parties or docket number.

## CourtListener MCP

1. Opinion search: query `"Yeshiva" "Pride Alliance"`, court `scotus`, filed before `2023-01-01`, three-result limit. Zero results. No inference from the empty return.
2. Opinion search: citation `558 U.S. 183`, two-result limit. Returned Hollingsworth v. Perry, decided January 13, 2010, cluster 1747, including lead opinion 9413203, and an unrelated district-court result that was disregarded.
3. Search within opinion 9413203 for `reasonable probability`, with 900 characters of surrounding context. Read the paragraph at reporter page 190 specifying the general stay-pending-cert requirements and the surrounding discussion. Used only that general framework, not the result of the prior as a statistical analogue.
4. Opinion search: query `"Yeshiva"`, court `scotus`, filed between `2022-09-01` and `2022-09-30`, three-result limit. Zero results. The discussion of Yeshiva in the rationale remains attributed to the provisioned application's own distinction, not to independent retrieval.

The precedent searches supplied a verified general stay standard but did not independently verify the application's Yeshiva or Skokie analogies. No live docket for this case, post-arrival case reporting, or target disposition was sought or encountered.
