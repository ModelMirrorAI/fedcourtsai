# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025-Term paid-petition estimate (5.36%).

## Corpus lookup

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation 'Merit Management Group, LP v. FTI Consulting, Inc.' --limit 10`
- Result: failed before returning any priors because the runner could not resolve the remote corpus-store hostname. No `ranged corpus reads: …` line was printed.

## CourtListener MCP

- Opinion search, filed before 2026-07-16: `"11 U.S.C. § 561(d)" AND "Chapter 15" NOT Fairfield` (10-result limit). One result: *Lawrence v. TPG Capital Management, L.P. (In re Hellas Telecommunications (Luxembourg) II SCA)*, 526 B.R. 499 (Bankr. S.D.N.Y. 2015), filed March 9, 2015.
- Opinion search, filed before 2026-07-16: `"Section 561(d)" AND bankruptcy NOT Fairfield` (20-result limit). The same single result was returned.

No web searches were performed. No search sought or revealed this case's Supreme Court disposition.
