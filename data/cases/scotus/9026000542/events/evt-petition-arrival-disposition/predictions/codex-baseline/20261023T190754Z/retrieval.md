# Retrieval

- Read the committed `metrics/statpack.md`: modern discretionary-cert population, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table. Read `metrics/statpack.json` for exact baseline reached-rate denominators and rates in displayed Terms 2017–2025, then pooled them locally. These are historical committed-pack inputs, not a live corpus refresh.
- No `fedcourts query`, `open-events`, or CourtListener MCP calls were made. There are no ranged-corpus transfer lines to report.
- General web search: `site.supremecourt.gov Rules Rule 10 considerations governing review certiorari rarely granted erroneous factual findings`. The tool returned no usable results.
- Opened the official Supreme Court rules-guidance page twice through the web tool; both attempts returned no usable content. No rule text was incorporated.
- No search named this case, its parties, its docket number, its disposition, or its subsequent history. No external case-specific material was retrieved.
- Local contract/schema reads and `fedcourts paths --court scotus --docket 9026000542 --event evt-petition-arrival-disposition --role predictor` were administrative. The first paths attempt failed because the default uv cache was read-only; the successful retry used `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --frozen`.
