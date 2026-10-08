# Retrieval log

## Supplied inputs

Read the event definition, case-level snapshot `2026-10-08.json`, context, document manifest, questions presented, and the entire supplied petition text. No other predictor output, outcome artifact, case summary, or QP-labeling artifact was read.

## Additional context

- Read `metrics/statpack.md`: modern-cert disposition and originating-circuit cuts, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table.
- Read `metrics/statpack.json` for the exact baseline reached rates and weighted resolved denominators in Terms 2017–2025. Computed the weighted pool locally with `jq`: 638 / 12,720 = 0.05015723270440252. No live corpus freshness or case-specific state was inferred from this aggregate artifact.
- Attempted a web search for `site.supremecourt.gov Rule 10 rarely granted erroneous factual findings misapplication properly stated rule law certiorari`. The tool returned no readable search result.
- Attempted twice to open the Supreme Court's official filing-and-rules guidance page (`supremecourt.gov`, path `/filingandrules/rules_guidance.aspx`). Both tool responses contained no readable content. No external legal text was used, and no case outcome appeared.

## Tooling and contract reads

Read `AGENTS.md`, the prediction prompt, prediction/flags/tooling schemas, and the path and serialization helpers. Ran `fedcourts paths --court scotus --docket 9026000464 --event evt-petition-arrival-disposition --role predictor`; the initial `uv` invocation could not access its default cache, and retrying with a writable temporary cache succeeded. These were path resolution and contract checks, not corpus retrieval.

No `fedcourts query` or `open-events` calls, CourtListener MCP lookups, or opinion-body retrievals were made. There are consequently no ranged-corpus transfer lines to report.
