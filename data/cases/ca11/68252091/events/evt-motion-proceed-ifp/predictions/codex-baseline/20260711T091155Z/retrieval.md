# Retrieval

## Corpus and base rates

- Consulted `metrics/statpack.md`, including the overall and Eleventh Circuit disposition summaries. The Eleventh Circuit figures cover only 45 resolved cases across mixed event types and are not an IFP-motion base rate.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court ca11 --era 2020s --limit 20 --corpus-backend ranged`. The command failed before producing results because the corpus remote hostname could not be resolved. It printed no `ranged corpus reads: …` line.

## CourtListener MCP

The following lookups returned no substantive case information:

- Searched Eleventh Circuit opinions filed before February 1, 2024 for `mandamus "in forma pauperis" frivolous`; the MCP server reported that its session store was unavailable.
- Searched opinions filed before February 1, 2024 for `"Angela DeBose"`; the MCP server reported that its session store was unavailable.
- Requested the `dockets` endpoint schema and then attempted to query the Northern District of Florida docket `4:22-cv-00439`. The schema request succeeded, but the first query was rejected because a requested relationship was not a valid output field and the corrected query failed because the session store was unavailable.
- Requested the `docket-entries` endpoint schema while assessing whether pre-event entries from the originating case could be queried. No docket-entry query was made because the endpoint does not expose a description-text filter and result-bearing calls required the unavailable session store.

No web search was used, and no information about this case's disposition or subsequent history was sought or encountered.
