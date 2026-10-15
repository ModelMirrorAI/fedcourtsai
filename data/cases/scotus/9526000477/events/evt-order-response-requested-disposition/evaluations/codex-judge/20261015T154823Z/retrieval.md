# Retrieval record

Read the evaluation contract and schemas; the event and outcome; the provisioned evaluator context, October 14 snapshot, and document manifest; relevant portions of the provisioned application and its appended opinions; and all three blinded candidates' prediction, rationale, forecast, retrieval note, and captured retrieval log.

Additional local reference: `metrics/statpack.md`, especially its interim-applications section and prior-Term table. Inspected the top-level interim keys and timing metadata in `metrics/statpack.json`. These reads assessed the candidates' baseline method; no evaluator-pooled baseline or skill value is supplied. No current corpus freshness claim is made.

Local operational reads included `fedcourtsai.paths`, `fedcourtsai.ids`, and `fedcourtsai.serialize`; these were not case retrievals. Output validation uses the committed JSON schemas and checks alias/path consistency and score arithmetic.

No corpus query or open-events call, CourtListener lookup, external web search, or external opinion retrieval was made by this evaluator. Accordingly there are no ranged-corpus-read transfer lines. Searches and lookups mentioned in the candidate evaluations are observations of the staged candidate logs, not new retrieval by this evaluator.
