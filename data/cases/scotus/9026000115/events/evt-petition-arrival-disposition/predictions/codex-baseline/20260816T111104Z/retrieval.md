# Retrieval

- Consulted the committed `metrics/statpack.md` and `metrics/statpack.json` for the sal-v3 prior-Term arrival risk-set rate, the Fourth Circuit cut, and the conditional cert-order-disposition rate.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '600 U.S. 447' --era 2020s --limit 3 --full`. The corpus service returned no output before the attempt was stopped; no `ranged corpus reads:` line was printed.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '595 U.S. 87' --era 2020s --limit 3 --full`. The corpus service returned no output and the command was interrupted; no `ranged corpus reads:` line was printed.
- Attempted a CourtListener MCP opinions search, limited to material filed before July 24, 2026, for decisions discussing *Groff v. DeJoy*, COVID-19 vaccination, and undue hardship. CourtListener returned HTTP 429 (daily rate limit exceeded), so no search result informed the prediction.
- No web search was used.
