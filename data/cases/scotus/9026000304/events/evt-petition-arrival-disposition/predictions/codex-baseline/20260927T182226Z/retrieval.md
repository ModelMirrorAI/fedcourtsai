# Retrieval log

- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and `sal-v4` per-Term band table.
- Read aggregate fields in `metrics/statpack.json`, including the exact federal-band reached rates and denominators. Used `jq` to pool all rendered Terms 2017-2025: 143 / 202 = 0.7079207920792079. No case-level outcomes were retrieved from the pack.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` to identify the committed pack's vintage: `96ebdd342`, September 26, 2026, 12:03:37 UTC. This does not establish remote corpus freshness.
- Web search: `site.uscode.house.gov 5 USC 3345 3347 3348 first assistant functions duties`. The tool returned no usable content.
- Web open attempted for `https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title5-section3345&num=0&edition=prelim`. The tool returned no usable content. No externally fetched statutory text was incorporated.
- No CourtListener MCP lookup, corpus `query`, or `open-events` call was made. There are no ranged-corpus-read transfer lines.
- Local contract/schema reads and `fedcourts paths` were operational checks, not additional case evidence. The initial paths command encountered a read-only default cache; retrying with a temporary cache succeeded.

Case-specific sources were solely the provisioned snapshot, context, event definition, questions presented, document manifest, and selected petition passages including the appended appellate opinion. No target-case disposition or post-decision material was sought or encountered.
