# Retrieval log

- Read the committed `metrics/statpack.md` interim-docket section and the corresponding `interim` fields in `metrics/statpack.json`. Used strictly prior application Terms 2016–2025; no case-level outcome rows were read.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed pack's file vintage: `808f812e9 2026-09-28T12:02:50Z`. This does not establish corpus-blob freshness.
- Web search: `site.supremecourt.gov Hollingsworth Perry 558 U.S. 183 stay reasonable probability fair prospect irreparable harm`. No visible results returned.
- Web search: `Hollingsworth Perry 558 U.S. 183 190 2010 stay reasonable probability fair prospect`. No visible results returned.
- CourtListener MCP `search`, parameters `type=o`, `citation=558 U.S. 183`, `num_results=1`. Returned HTTP 429, 300/hour rate limit, with a suggested wait of 444 seconds. No opinion text or search results were received. Proceeded without retry or REST fallback.
- No `fedcourts query` or `open-events` lookup was made; no ranged-corpus transfer line was generated. No target-case outcome, subsequent history, other predictor output, or labeling-measurement artifact was consulted.

Local setup/schema reads and `fedcourts paths --court scotus --docket 9526000446 --event evt-order-response-requested-disposition --role predictor` resolved the output contract. The first CLI attempt failed on a read-only default cache location; using a temporary writable cache allowed it to run. These were not substantive corpus lookups.
