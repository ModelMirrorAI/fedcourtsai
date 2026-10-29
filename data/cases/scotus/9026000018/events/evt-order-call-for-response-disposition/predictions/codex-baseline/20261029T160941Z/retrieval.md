# Retrieval log

No lookup sought this petition's Supreme Court outcome, current docket, subsequent history, or another cell's output. General legal research and the two corpus prior queries below were the only substantive external retrieval. Read-only shell operations also inspected the prompt, instructions, schemas, provisioned record, and committed statpack; a read-only sidecar analyzed only the provisioned petition and questions presented, without retrieval.

## Corpus and CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000018 --event evt-order-call-for-response-disposition --role predictor` failed because uv's default cache location was read-only. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; succeeded and resolved the case/event/corpus paths. No outcome file was read.
2. `uv run fedcourts query --help` failed for the same cache reason. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; succeeded. A later invocation of the same help command piped to `sed -n '70,155p'` inspected the structured-filter options. These were help-only, not data lookups.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '564 U.S. 431' --decided-before 2026 --limit 3` returned no rows. Its coverage note said only 200 scoped rows carried reporter citations and that an empty result more likely reflected unfilled coverage than nonexistent precedent. Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` returned U.S. DOGE Service v. United States District Court for the District of Columbia (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343). All carried October 13, 2026 grant dates and no opinion body. They are general grant-coded examples, not substantive mootness analogues, and were not used to adjust the forecast. The bare-year filter is a docket-Term mask, not an August 2026 day cutoff; this is a forward cell. Transfer line: `ranged corpus reads: 25 GET(s), 6553600 byte(s)`.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed with an unsupported-service-backend error: only query/open-events are forwarded by that backend. No corpus vintage was obtained. No fallback credential access or corpus pull was attempted.
6. Read the committed `metrics/statpack.md` modern-cert, circuit, relist, CVSG, amicus, and sal-v4 segment tables and inspected the matching JSON. A `jq` calculation pooled the nine displayed strictly-prior state risk-set rows: 104/426 = 0.24413145539906103. This is a committed-pack anchor, not a refreshed service-corpus estimate.
7. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate --help` inspected the validator contract. Validation itself is an output check, not substantive retrieval.

## CourtListener MCP

`search(type="o", citation="564 U.S. 431", num_results=2)` attempted a Turner v. Rogers precedent lookup. It failed with HTTP 429, daily rate limit exceeded, approximately 7,829 seconds until availability. No case text was returned. No REST fallback was used.

## Web calls

1. One batched `web.run` search with the queries `site.supremecourt.gov opinions "Turner" "564" "evading"` and `site.law.cornell.edu/supremecourt/text/484/305 "plenary review"` sought general preexisting mootness doctrine. Results included Honig v. Doe (Cornell LII), Nebraska Press Association v. Stuart (Cornell LII), a University of Chicago discussion of mootness, the Reclaim Idaho Supreme Court opinion PDF, and this petition's own questions-presented PDF. The last result incidentally repeated the already-provisioned 90-day timing and plenary-review questions; it disclosed no disposition or later case history and was not opened or used as new evidence. The academic discussion and unrelated case were not used as empirical anchors.
2. `web.run open` on the Cornell LII reproduction of Honig v. Doe, 484 U.S. 305 (1988), returned the opinion. Consulted only its general capable-of-repetition-yet-evading-review analysis: short duration and reasonable expectation of recurrence are separate conditions. No claim is made that Honig itself resolves this petition's PLRA vehicle. Its cited-source identity and majority pages are supplied in reasoning.md.

The external retrieval did not produce this petition's Supreme Court outcome. The cutoff was used to understand the provisioned state, not to infer an unobserved response or conference result.

## Review and output checks

The read-only sidecar subsequently reviewed this cell's own artifacts against the statistical-review checklist, the committed statpack, and the provisioned petition, without live retrieval or reading other cells. It reproduced the 104/426 prior and the conditional-route arithmetic and caught an incorrect Bellotti case attribution; that citation was corrected against petition lines 784–786. `git rev-parse HEAD:metrics/statpack.json` supplied the immutable pack identifier recorded in reasoning.md. No other prediction or evaluation was accessed through git.

`UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data` passed: 29,703 artifacts valid and 71,066 references consistent. A separate read-only Python assertion check verified the exact five cert claims, equality of the disposition and top-level probabilities, nine order-writer labels, and absence of agent-written harness context/process stamps. Validation was repeated after the citation and provenance clarifications.
