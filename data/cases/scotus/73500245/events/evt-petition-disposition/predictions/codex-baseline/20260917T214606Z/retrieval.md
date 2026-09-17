# Retrieval record

- Consulted committed metrics/statpack.md: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Consulted metrics/statpack.json only for the corresponding baseline risk-set fields; pooled Terms 2017-2024, excluding the case's own Term and later Terms. The observed pool was 593 / 11,580 = 0.051208981. No live corpus refresh or corpus-wide freshness claim is made.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing review certiorari misapplication properly stated rule law`. The tool returned no usable result.
- Web opens attempted for the Supreme Court's `2023RulesoftheCourt.pdf` and `rules_guidance.aspx` under its filingandrules directory. Both returned no usable content. No retrieved authority from these attempts informed the forecast.
- No CourtListener MCP lookup, fedcourts query, or open-events call was made. No ranged-corpus-transfer line was produced.
- Operational reads included the prompt, schemas, path and serialization helpers. `uv run fedcourts paths --court scotus --docket 73500245 --event evt-petition-disposition --role predictor` succeeded after redirecting the inaccessible default uv cache to /tmp. These were contract/path checks, not case research.
- No own-case disposition, subsequent history, evaluator material, other prediction, or topic-label artifact was read.
