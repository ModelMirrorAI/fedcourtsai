# Retrieval record

## Local reference material and infrastructure

- Read the prediction contract, prediction schema, tooling and flags schemas, event definition, and the case-level provisioned snapshot, context, document inventory, questions presented, transcript, argument features, and selected substantive portions of the merits briefs, petitioner's reply, United States merits amicus, appendix, decision below, and lower-court docket summary. These were provisioned inputs, not external case retrieval.
- Read only the merits and per-Justice merits sections of `metrics/statpack.md`, the corresponding explanatory sections of `metrics/README.md`, and the corresponding `merits` and `justice_votes` objects in `metrics/statpack.json`. Used local arithmetic to pool the permitted strictly prior-Term counts. No cert salience-band rates were used.
- Attempted `uv run fedcourts paths --court scotus --docket 73278422 --event evt-argument-judgment --role predictor`. It failed before resolving paths because the default uv cache directory was read-only.
- Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 73278422 --event evt-argument-judgment --role predictor`. It succeeded and reported the case, corpus, and event paths, with the outcome explicitly evaluator-only. I did not open an outcome or query the corpus. Neither paths invocation printed a `ranged corpus reads:` line.

## External precedent lookup attempts

These attempts concerned general precedent, not this case's outcome or anyone else's forecast. The web tool returned no usable source content for any of them; none supplied evidence used in the prediction.

1. One `web.run` search call with two queries: `site.supremecourt.gov opinions 21pdf Egbert Boule 21-147` and `site.supremecourt.gov opinions 24pdf Goldey Fields 24-809`. No usable search results were returned.
2. One `web.run` open attempt for `https://www.supremecourt.gov/opinions/21pdf/21-147_g31h.pdf`. No usable document content was returned.
3. One `web.run` open attempt for `https://www.supremecourt.gov/docket/docketfiles/html/public/24-809.html`. No usable docket content was returned. This is a precedent's docket, not the forecast case's docket.

No CourtListener MCP calls, `fedcourts query` calls, or `open-events` calls were made. No other cell's prediction, evaluation, or outcome was consulted. The cell validation command is recorded as a validation action, not a substantive lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/73278422/events/evt-argument-judgment/predictions/codex-baseline/20261113T042228Z`.
