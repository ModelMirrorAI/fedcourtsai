# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” relist count, CVSG status, originating circuit, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36%).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation '86 M.J. 8' --limit 10`
- Result: failed before returning priors because DNS resolution for the ranged corpus store failed. No `ranged corpus reads: …` line was produced.

## CourtListener MCP

- Searched opinions by citation `86 M.J. 8`; no result was returned.
- Searched opinions for `"indorsement" "Article 66(d)(2)"`; results were not relevant to the military-law question.
- Searched CAAF opinions for *United States v. Johnson* with `firearm indorsement`; found the June 24, 2025 published opinion, CourtListener cluster 10616309.
- Repeated that search with restricted metadata fields to identify the opinion record (opinion 11082897).
- Retrieved opinion 11082897 from the opinions endpoint. It confirmed the majority’s holding that Article 66(d)(2) does not authorize correction of the § 922 indication and Judge Johnson’s separate concern about when judgment is entered.

No web searches were used.
