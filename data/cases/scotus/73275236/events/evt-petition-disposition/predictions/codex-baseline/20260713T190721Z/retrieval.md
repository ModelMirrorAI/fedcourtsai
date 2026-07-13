# Retrieval

- Consulted `metrics/statpack.md` and the 2025 Term paid-fee detail in `metrics/statpack.json` for modern discretionary-cert, Fourth Circuit, CVSG, Term, and fee-class base rates.
- Attempted corpus lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation 'Klehr v. A.O. Smith Corp.' --limit 8 --corpus-backend ranged`. The command failed before any ranged read because the corpus-store hostname could not be resolved; it printed no `ranged corpus reads` line and returned no priors.
- CourtListener MCP opinion search: Supreme Court opinions matching `"fraudulent concealment" antitrust statute limitations`, limited to case name, citation, court, filing date, status, and URL. The seven results included *Klehr v. A. O. Smith Corp.*, 521 U.S. 179 (1997), and *Greyhound Corp. v. Mt. Hood Stages, Inc.*, 437 U.S. 322 (1978). This was used only as general legal context, not to seek this case's disposition.
- No REST fallback or web search was used.
