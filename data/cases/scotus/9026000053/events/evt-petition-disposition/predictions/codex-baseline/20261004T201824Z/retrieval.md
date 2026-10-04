# Retrieval record

## Local reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling JSON schemas.
- Read relevant sections of `metrics/statpack.md`: modern discretionary cert dispositions, originating-circuit cuts, paid-segment relist and CVSG cuts, and the `sal-v4` segment table. Computed the approximate pooled baseline reached rate from all displayed Terms 2017–2025. Inspected only the top-level keys of `metrics/statpack.json` for provenance fields; no additional case-level information was read from it.
- Ran `uv run fedcourts paths --court scotus --docket 9026000053 --event evt-petition-disposition --role predictor`. The first attempt failed on the default cache's read-only location; the same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache`.
- No `fedcourts query`, `open-events`, or other live corpus lookup was made. There are no ranged-corpus transfer lines to report.

## External legal context

1. Web search: `site.supremecourt.gov opinions 2019 GE Energy Outokumpu 18-1048 which body of law governs`. No usable result was returned.
2. Web search: `GE Energy Outokumpu 2020 Supreme Court 18-1048 pdf`. No usable result was returned.
3. CourtListener MCP `search`: `type=o`, `citation=590 U.S. 432`, `num_results=1`. Returned the June 1, 2020 GE Energy decision, cluster 4757656, including lead opinion 9889180. Used only to identify the earlier precedent, not as a citing-case or subsequent-history search.
4. CourtListener MCP `search_document`: `opinion_id=9889180`, `query=which body`, `snippet_size=700`. The returned concluding passage confirms that the Court left the estoppel application and governing body of law for remand.

No lookup sought this petition's disposition or subsequent history. No independent companion-docket retrieval was made. No outcome-revealing material was encountered.
