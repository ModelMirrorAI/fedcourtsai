# Retrieval log

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`
   - Transfer: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`.
   - Returned three granted priors on docket-number Terms before 2026, including rows with October 13, 2026 grant dates. This is a forward cell; the explicitly added year mask is not a claim that every returned proceeding predates the September baseline. The cases were not close doctrinal matches, were not this petition, and supplied no substantive adjustment to the forecast.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 19-1261 --decided-before 2026 --limit 1 --full`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
   - Returned *Trent Michael Taylor v. Robert Riojas*, case `scotus/18596711`, with November 2, 2020 grant-family disposition and four distributions. `has_opinion` was false and `opinion_text` null. The full-body request therefore produced no legal text. No inference about summary-disposition frequency was drawn from this single row.

## CourtListener MCP

- `search(type="o", case_name="Baxter v. Bracey", court="scotus", filed_before="2021-01-01", num_results=3, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`
  - HTTP 429: daily rate limit exceeded; the server reported availability in 5,408 seconds. No case text or results were returned. Continued with the provisioned inputs and corpus service; no REST fallback attempted.

## Web attempts

- Search: `site.supremecourt.gov opinions Taylor Riojas 2020 qualified immunity obvious constitutional violation`.
- Search: `Taylor v. Riojas 2020 Supreme Court 19-1261 per curiam`.
- Both tool calls returned no usable output or source text. Neither sought this petition's outcome, and no web material informed the forecast.

## Committed reference material and operational reads

- Read the applicable instructions and the prediction, agent-tooling, and agent-flags schemas.
- Read `metrics/statpack.md` modern-cert, circuit, relist, CVSG, amicus, and sal-v4 per-Term band sections. Used `metrics/statpack.json` to pool the nine displayed strictly prior Terms, yielding 660 / 12,913 = 0.0511112832 for the baseline reached population. These are committed-pack estimates, not a fresh remote-corpus measurement.
- Ran `fedcourts paths --court scotus --docket 9026000180 --event evt-order-call-for-response-disposition --role predictor`. Its initial invocation failed because the default uv cache was read-only; rerunning with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. No case outcome was displayed.
- Read `fedcourts query --help`, `fedcourts validate --help`, and relevant path/serialization helper definitions. Read the nonsecret `DECIDED_BEFORE` value, which was unset; context also identifies forward mode.
- The provisioned snapshot, context, document manifest, questions presented, petition argument, and attached appellate opinion are the main case-specific evidence. No current docket page, later filing, other forecast, evaluation, or outcome file was read.
