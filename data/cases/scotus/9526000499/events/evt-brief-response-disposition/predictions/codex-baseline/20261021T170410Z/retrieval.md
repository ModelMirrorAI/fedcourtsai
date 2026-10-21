# Retrieval

- Read the committed metrics/statpack.md interim-docket section. Pooled only application Terms 2016–2025 for the Term 2026 baseline; no live corpus query or open-events call was made, so there is no ranged-corpus transfer line.
- Read schemas/prediction.schema.json, schemas/agent_tooling.schema.json, schemas/agent_flags.schema.json, and local paths, serialization, and claim-declaration code for artifact-contract checks. Used `uv run fedcourts paths --court scotus --docket 9526000499 --event evt-brief-response-disposition --role predictor`; the first invocation encountered an unwritable cache and the retry with a writable temporary cache succeeded.
- Used `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed baseline artifact's vintage: ac757d745, October 19, 2026. This does not establish remote corpus freshness.
- Generic web search: `site.supremecourt.gov "vacate a stay" "demonstrably wrong"`. The tool returned no usable content.
- Generic historical legal-source open attempt: `https://supreme.justia.com/cases/federal/us/424/1301/`. The tool returned no usable content. No proposition was derived from either web attempt.
- No CourtListener MCP lookup, live case-specific search, target outcome lookup, or subsequent-history retrieval was performed.

The provisioned response itself reports related-case certiorari denials predating the snapshot. Those reports informed the forecast as disclosed in reasoning.md and flags.json; they were not external retrievals and do not reveal this application's outcome.
