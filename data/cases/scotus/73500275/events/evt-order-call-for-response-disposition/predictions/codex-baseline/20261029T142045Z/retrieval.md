# Retrieval record

## Local supporting material beyond the provisioned case record

- Read AGENTS.md, .github/prompts/predict.md, prediction/agent-tooling/agent-flags
  schemas, and the path/serialization helpers to follow the output contract.
- Read metrics/statpack.md: modern discretionary-cert dispositions, paid scored
  segment relist/CVSG/amicus cuts, and the sal-v4 per-Term band risk-set table.
- Read metrics/statpack.json to inspect its structure and pool only the
  baseline reached counts for Terms 2017-2024: 607 / 11,599 = 5.2332%.
- Attempted `uv run fedcourts paths --court scotus --docket 73500275 --event
  evt-order-call-for-response-disposition --role predictor`. It failed before
  executing because uv's default cache was read-only. Repeated with
  `UV_CACHE_DIR=/tmp/fedcourts-uv-cache`; the command succeeded and returned
  the case, corpus, and event paths, with the outcome explicitly withheld.
- No `fedcourts query` or `open-events` call was made; there is no ranged
  corpus-read transfer line to report. The path resolver is not a corpus query.

## External attempts

1. `web.run` search query: `site.supremecourt.gov opinions 2024 Macquarie
   Infrastructure Moab Partners 22-1165`. The tool returned no usable result
   content. This was a historical-precedent lookup, not an ON24 search.
2. `web.run` open: official Supreme Court opinion path
   `/opinions/23pdf/22-1165_10n2.pdf` on supremecourt.gov. The tool returned
   no usable document content; no proposition was taken from it.
3. CourtListener MCP `search(type="o", citation="601 U.S. 257",
   num_results=2)`. Returned HTTP 429: daily rate limit exceeded, with
   availability estimated in 13,137 seconds. No case result or opinion text
   was returned. No direct REST fallback was attempted.

The forecast therefore rests on the provisioned pre-disposition record and
the committed base-rate pack. No ON24 outcome, later history, another cell's
forecast, or topic-labeling artifact was sought or read.
