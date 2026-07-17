# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, particularly modern discretionary-cert disposition rates, originating-circuit rates, relist rates, and the 2025 Term paid-petition rate.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation '393 U.S. 503' --citation '478 U.S. 675' --era 2020s --limit 10`
- Result: failed before returning priors because the ranged corpus S3 host could not be resolved (`EndpointConnectionError`). The command printed no `ranged corpus reads: …` line.

## CourtListener MCP

- Searched opinions for `"plainly lewd" Fraser Tinker student speech`, limited to filings before July 17, 2026, requesting 10 results. The search returned *B.H. ex rel. Hawk v. Easton Area School District*, the already-known Sixth Circuit opinion in this case, and *Ryan v. Mesa Unified School District*. It confirmed the principal legal-context authorities without revealing any Supreme Court disposition.

No web search was used.
