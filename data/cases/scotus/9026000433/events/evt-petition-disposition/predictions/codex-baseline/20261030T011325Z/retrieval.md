# Retrieval record

## Provisioned record

Read the event definition, October 30, 2026 case-level snapshot, context, document manifest, questions presented, petition passages addressing the issue, conflict and vehicle, and appendix passages containing the appellate majority and opening of the dissent. No outcome, other prediction, evaluation, or topic-label artifact was read.

## Corpus and local base rates

Commands below ran from the repository root. Except for the two initial cache failures, uv commands used `UV_CACHE_DIR=/tmp/uv-cache`.

1. `uv run fedcourts paths --court scotus --docket 9026000433 --event evt-petition-disposition --role predictor` — initial attempt failed because the default uv cache was read-only; retry with the temporary cache succeeded. This resolved paths only, not outcome content.
2. `uv run fedcourts query --help` — initial attempt failed on the same cache issue; retry with the temporary cache succeeded. The help was also consulted through `sed -n '85,160p'` on a subsequent invocation. No substantive corpus data were returned by these help calls.
3. `uv run fedcourts query --court scotus --era modern --disposition granted --limit 4` — rejected: `modern` is not a valid decade token. No transfer line was printed.
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3` — succeeded, returning three granted priors. Results included a substantive application and cert petitions; the output was broad, not a fact-matched precedent set. No full opinion bodies were requested. These rows did not determine the forecast.

   `ranged corpus reads: 20 GET(s), 5242880 byte(s)`

5. `uv run fedcourts corpus-info` — failed with a service-backend error explaining that the service has no client-side connection. No corpus-wide freshness stamp or transfer line was returned. No fallback direct remote access was attempted.
6. Read the committed `metrics/statpack.md`: modern cert disposition and originating-circuit sections, paid-segment relist, CVSG and amicus cuts, and the sal-v4 reached-band table. Consulted `metrics/statpack.json` to compute the exact prior-Term baseline pool with jq: restrict `term < 2026`, `salience_version == "sal-v4"`, and `band == "baseline"`; sum `prefix_weighted_resolved * prefix_est_grant_rate` and divide by summed `prefix_weighted_resolved`. Result: 660 / 12,913 = 0.0511112832. This is the committed pack's estimate; its underlying blob vintage could not be verified by the unsupported corpus-info call.

No replay clock was set; the context is forward mode. No query targeted this petition's outcome or later history.

## CourtListener MCP

1. `search(type="o", citation="133 F.4th 1305", num_results=2, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])` — located *Rachael DeMarcus v. University of South Alabama*, filed April 10, 2025, opinion ID 10842761.
2. `search_document(opinion_id=10842761, query="fundamental", snippet_size=750)` — zero matches. This literal search alone does not establish what legal test the decision applies.
3. `search_document(opinion_id=10842761, query="conscience", snippet_size=650)` — nine matches; excerpts discussed conscience-shocking conduct and qualified immunity, including resolution on clearly-established-law grounds.
4. `read_document(opinion_id=10842761, chunk_index=5, chunk_size=8000)` — read opinion pp. 17–19 in context, confirming the executive-action formulation and the independent qualified-immunity inquiry. The prior search excerpts also covered pp. 19–21. Used to assess whether the petition's cited authority necessarily resolves the immunity obstacle; not used as statistical evidence.

## Web

One `web.run` call attempted two general precedent searches:

- `site.supreme.justia.com County of Sacramento v Lewis 523 U.S. 833 executive abuse conscience`
- `site.ca11.uscourts.gov DeMarcus University South Alabama 2025 1305 conscience`

The tool returned no usable response material. No result was relied upon. Neither query sought this petition's disposition; the provisioned docket was not supplemented with a live docket or outcome lookup.

## Contract and validation tooling

Read `AGENTS.md`, the prediction prompt, prediction/tooling/flags schemas, and the repository path and serialization helpers. These are contract/format checks, not additional case evidence. Local shell inspection and jq arithmetic supplied no additional case history. Validation is performed after writing the outputs.
