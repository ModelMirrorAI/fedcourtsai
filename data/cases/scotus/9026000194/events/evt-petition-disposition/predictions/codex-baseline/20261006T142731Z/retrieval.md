# Retrieval record

## Local material beyond the provisioned case record

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas for the contract. Searched for nested `AGENTS.md` instructions; none were returned under `data` or `.github`. No labeling artifacts or case outcome files were read.
- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition and originating-circuit cuts, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term segment table. Inspected only the top-level keys of `metrics/statpack.json`; no case-membership material was consulted.
- A local Python calculation pooled the displayed baseline-reached rates for Terms 2017–2025: weighted denominator 12,720 and approximate rate 0.050109. The approximation reflects rounded table percentages. It also calculated the broad modern-cert any-grant rate, 0.028192. No live corpus query or corpus refresh was performed; no ranged-read transfer line was emitted.
- Ran `uv run fedcourts paths --court scotus --docket 9026000194 --event evt-petition-disposition --role predictor`. The initial attempt failed because the default uv cache was read-only. Repeating with a temporary writable cache succeeded; the output withheld the evaluator-only outcome path. This was path resolution, not a corpus lookup.

## External retrieval attempts

1. `web.run` search batch with the exact queries `site.law.cornell.edu rules supremecourt rule 10 certiorari`, `site.govinfo.gov Caplin Marine Midland 406 U.S. 416`, and `site.law.cornell.edu uscode text 11 544`. No usable result content was returned in the session. No claim relies on external text from these searches.
2. `web.run` attempted to open Cornell's Supreme Court Rule 10 page. No usable content was returned. No case-specific search was performed.
3. CourtListener MCP `search(type="o", citation="816 F.2d 1222", num_results=2)`, seeking the older Ozark Restaurant opinion mentioned in the petition. The server returned HTTP 429, daily rate limit exceeded, with an indicated wait of 2,122 seconds. No opinion or search results were delivered. I did not retry, use REST, or seek credentials.

The forecast relies on the provisioned record and the committed statpack, not on independently retrieved case law. No disposition or subsequent history of this petition was sought or encountered.
