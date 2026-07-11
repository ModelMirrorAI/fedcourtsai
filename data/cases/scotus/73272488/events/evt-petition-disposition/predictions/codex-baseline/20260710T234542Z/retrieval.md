# Retrieval

- Consulted `metrics/statpack.md` for SCOTUS disposition base rates, recent Terms, and originating-circuit data. The modern discretionary-cert section specified by the prediction prompt was not present; recent Terms also had no resolved cases in the committed artifact. I did not use the blended percentages as a quantitative cert anchor.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10 --corpus-backend ranged`. The remote corpus host could not be resolved, so the command returned no priors and printed no `ranged corpus reads: ...` line.
- Attempted a CourtListener Opinions search for `"general Rule 29 motion" sufficiency preservation de novo plain error`, restricted to filings before July 10, 2026, requesting ten results. The MCP session store was unavailable, so the lookup returned no results.
- No web searches were consulted.
