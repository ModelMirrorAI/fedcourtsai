# Retrieval log

## Provisioned inputs

- Read the event definition, context, October 8 snapshot, document manifest, and the application argument with relevant appendix opinions and orders. No other prediction, evaluation, or realized outcome was read.
- Read the prediction prompt and schemas to determine the output contract.

## Additional local context

- Read `metrics/statpack.md`, especially the interim-docket scope, per-Term counts, and coverage caveats. Inspected only the top-level key names of `metrics/statpack.json`; no case-level information was retrieved from it. Computed the eligible rate as `(17+18+18)/(226+196+127)` = 0.0965391621129326.
- Ran `uv run fedcourts paths --court scotus --docket 9526000477 --event evt-motion-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; reran successfully with a writable temporary cache. This resolves paths, not case outcomes.
- No `fedcourts query` or `open-events` calls were made. No ranged corpus reads were issued, and no transfer diagnostic applies.

## Web attempts

- Searched for `site.supremecourt.gov Hollingsworth Perry 558 183 190 stay reasonable probability fair prospect` and `site.uscode.house.gov 47 USC 155 applications review shall pass upon objective three months`. The web tool returned no usable content.
- Attempted to open the official U.S. Code page for 47 U.S.C. 155 using its preliminary-edition section locator. The tool returned no usable content. No legal proposition is based on this unsuccessful retrieval.
- No query named the present case, sought its disposition, or sought its subsequent history.

## CourtListener MCP

1. `search(type="o", citation="558 U.S. 183", num_results=1)` returned *Hollingsworth v. Perry*, decided January 13, 2010, cluster 1747, including lead opinion 9413203.
2. `search_document(opinion_id=9413203, query="reasonable probability", snippet_size=900)` returned the stay standard at page 190. Used to corroborate the general standard quoted in the provisioned application; not used as an empirical case-matched prior.

The earlier September 4 intervention was encountered only as pre-application background in the provisioned filing and appendix. It is a different order, not the target application's disposition.
