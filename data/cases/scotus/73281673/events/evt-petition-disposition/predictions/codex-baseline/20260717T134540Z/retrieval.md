# Retrieval

## Committed base-rate material

- Read `metrics/statpack.md`, including modern discretionary-cert disposition, relist, CVSG, originating-court, and per-Term tables.
- Read the 2025 paid-fee-class entry in `metrics/statpack.json` (estimated grant rate 5.36%).

## Corpus lookup

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic "Fourth Amendment private search CyberTip PhotoDNA" --limit 8`
- Result: failed before returning priors because the runner could not resolve the ranged corpus store's S3 hostname. No `ranged corpus reads: ...` line was printed because the connection failed before a ranged read occurred.

## CourtListener MCP lookups

- Opinion search for `("private search" AND (PhotoDNA OR CyberTip))`, limited to filings through 2026-07-17. It returned 25 matches; the first page included *Reddick*, *Bebris*, *Wilson*, *Holmes*, *Rosenschein*, and the already provisioned Wisconsin Supreme Court opinion in this case. It revealed no disposition of the cert petition.
- Citation search for `170 F.4th 134`. It returned no match.
- Case-name search for `United States v. Lowers`, limited to 2026 filings. It returned *United States v. Nico Lowers*, Fourth Circuit No. 24-4546, filed March 10, 2026.
- Expanded case-name search for `United States v. Nico Lowers`. It confirmed the same Fourth Circuit opinion and its opinion-record metadata.
- Opinion search for `United States v. Rosenschein` with `PhotoDNA "private search"`. It returned the Tenth Circuit's 2025 decision at 136 F.4th 1247.
- Follow-up *Rosenschein* search for `("human eyes" OR "virtual certainty")`. It returned no match.

No web searches were used.
