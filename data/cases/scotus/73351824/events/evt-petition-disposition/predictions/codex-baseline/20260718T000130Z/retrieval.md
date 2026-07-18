# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. Relevant anchors were the 5.4% estimated grant rate for paid Term 2025 petitions, the 0.8% grant rate in the broad zero-relist bucket, and the 3.0% grant rate for petitions without a CVSG.
- Ran `uv run fedcourts query --court scotus --era 2020s --limit 8` (with a runner-local writable package cache). Transfer report: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`. The results supplied recent resolved SCOTUS priors and confirmed that multiple high-salience petitions are still denied; they were not close topical matches and received little weight.
- Attempted one CourtListener MCP opinion search for post-*Brackeen* ICWA equal-protection and standing decisions. It returned `HTTP 429` (daily rate limit; retry window approximately 59 seconds), so it supplied no substantive results and no direct REST fallback was attempted.
- No web search was used.
