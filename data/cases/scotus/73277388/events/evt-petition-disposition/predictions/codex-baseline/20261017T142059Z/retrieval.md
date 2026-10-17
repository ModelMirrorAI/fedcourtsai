# Retrieval log

## Provisioned inputs

Read this cell's event definition, context, October 10, 2026 snapshot, document manifest, questions presented, and substantive petition text. Did not read any outcome, other predictor output, case summary, or labeling-measurement artifact.

## Committed general reference material

- Read the required instructions and output schemas, and used `uv run fedcourts paths --court scotus --docket 73277388 --event evt-petition-disposition --role predictor` to resolve paths. The initial command failed because the default uv cache was read-only; rerunning with a temporary writable cache succeeded.
- Read `metrics/statpack.md`: modern discretionary-cert disposition/circuit context, paid-segment relist and CVSG cuts, and the sal-v4 per-Term reached-rate table. Used `metrics/statpack.json` for exact prior-Term baseline pooling. The calculation was `sum(prefix_est_grant_rate * prefix_weighted_resolved) / sum(prefix_weighted_resolved)` for baseline segments in Terms 2017-2024, yielding `593 / 11580 = 0.05120898100172712`.
- Ran `git log -1 --format='%cs %h' -- metrics/statpack.md` to identify the checked-out pack's file vintage: October 13, 2026, commit cf9ae960e. Did not inspect any case-history diff.
- Read path/serialization helper definitions for output handling and the statistical-review checklist for the baseline's denominator and leakage conventions.

## External legal context only

1. Web search: `site.supremecourt.gov opinions 2016 Kindred Nursing Clark 16-32 equal treatment arbitration consideration`. Returned no usable results.
2. Web open: `https://www.supremecourt.gov/opinions/16pdf/16-32_o7jp.pdf`. Returned no usable content.
3. CourtListener MCP `search(type="o", citation="581 U.S. 246", num_results=2)`. Returned Kindred Nursing Centers v. Clark, decided May 15, 2017, including combined opinion 4168363 and lead opinion 8138126. Used only that historical authority's metadata, not later citing cases.
4. CourtListener MCP `search_document(opinion_id=4168363, query="formation", snippet_size=800)`. Read the relevant snippets about FAA equal treatment at contract formation, including the discussion on slip pages 7-9. This verified general legal context for the provisioned petition's theory.

No `fedcourts query` or `open-events` calls; no ranged-corpus-read transfer lines were emitted. No lookup sought this case's outcome or the subsequent history of its companion petition. No outcome exposure occurred.
