# Retrieval log — ca10/69180294 evt-appeal-disposition (claude-baseline, 20260711T091155Z)

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court ca10 --corpus-backend ranged --limit 10`
   — `ranged corpus reads: 38 GET(s), 9961472 byte(s)`.
   Returned 10 generic ca10 priors (dispositions overwhelmingly `other`, one
   `denied`); metadata/summaries visibly noisy, used only directionally.
2. `uv run fedcourts query --court ca10 --topic "Social Security" --corpus-backend ranged --limit 5`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`. No results.
3. `uv run fedcourts query --topic "864 SSID Title XVI" --corpus-backend ranged --limit 5`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`. No results.

## Base rates

- Read the committed `metrics/statpack.md` (overall and by-court cuts; ca10
  row: 34 resolved — other 88.2%, denied 11.8%).

## CourtListener MCP

- Attempted `call_endpoint` (docket-entries for docket 69180294, pre-decision
  entries only) and `search` (RECAP metadata for the same docket). Both calls
  failed with a server-side error (`REDIS_URL is not set; cannot access
  session store`); the server was unusable this run, so no CourtListener data
  informed the prediction. No call sought the case's outcome, and none was
  attempted against the linked opinion cluster.

## Web

- No web searches.
