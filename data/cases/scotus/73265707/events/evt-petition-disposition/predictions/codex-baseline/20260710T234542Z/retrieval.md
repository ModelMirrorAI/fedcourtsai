# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`. It reports that among 296 resolved SCOTUS petitions in the corpus, 1.4% were granted, 4.4% denied, 15.9% dismissed, and 78.4% labeled other. The modern discretionary-cert section described by the prediction prompt was not present, so these figures were used only as a loose calibration check.

## Corpus lookup

- Command: `.venv/bin/fedcourts query --court scotus --era 2020s --limit 12 --corpus-backend ranged`
- Result: failed because the remote corpus host could not be resolved. No priors were returned, no ranged GET completed, and no `ranged corpus reads: ...` line was emitted.

## CourtListener MCP lookup

- Searched opinions for `"Morgan v. Sundance" arbitration waiver mandamus`, limited to filings before July 10, 2026, requesting five compact results.
- Result: the MCP lookup failed because its session store was unavailable; no results were returned.

No web searches were performed.
