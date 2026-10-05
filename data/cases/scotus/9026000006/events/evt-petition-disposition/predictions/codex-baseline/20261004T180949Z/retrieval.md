# Retrieval log

- Read the committed metrics/statpack.md modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and sal-v4 per-Term segment table. Used baseline reached rates from Terms 2017–2025 only; pooled the displayed rounded rates with their denominators locally. No corpus query or open-events call was made, so there is no ranged-corpus transfer line.
- Web search query: `site.supremecourt.gov Rule 10 certiorari compelling reasons misapplication properly stated rule law`. The tool returned no usable result or source text.
- Web open attempt: official Supreme Court `2023RulesoftheCourt.pdf` under its `ctrules` directory. The tool returned no usable result or source text. No legal proposition was adopted from either failed attempt.
- No CourtListener MCP lookup, case-specific web search, outcome retrieval, or subsequent-history lookup was performed.
- Local contract support: read AGENTS.md, the predict prompt, and prediction/tooling/flags schemas. Resolved the cell path with `uv run fedcourts paths --court scotus --docket 9026000006 --event evt-petition-disposition --role predictor`; the first attempt hit a read-only default cache, and the retry used a temporary writable cache. These were not substantive corpus retrievals.
