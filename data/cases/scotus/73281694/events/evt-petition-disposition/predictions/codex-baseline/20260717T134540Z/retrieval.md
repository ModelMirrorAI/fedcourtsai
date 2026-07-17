# Retrieval

## Committed base-rate context

- Read `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” relist and CVSG cuts, and the per-Term table.
- Read the 2025-Term paid-fee detail in `metrics/statpack.json`: estimated paid-petition grant rate 5.36%.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation '600 U.S. 122' --limit 8 --corpus-backend ranged`
- Result: failed because the corpus remote hostname could not be resolved. No priors were returned and no `ranged corpus reads: ...` line was printed because the failure occurred before a remote read.

## CourtListener MCP

- Opinion search for `"dormant Commerce Clause" "general jurisdiction" registration`, limited to June 27, 2023 through July 17, 2026. Returned nine results, including *Tom James Co. v. Zurich American Insurance Co.*, *Kennedy v. Crothall Healthcare*, and the 2023 *Mallory* opinions.
- Opinion search for `"dormant Commerce Clause" Mallory consent registration` over the same period. Returned eight results and confirmed sparse indexed post-*Mallory* treatment.
- Case-name search for *Tom James Company v. Zurich American Insurance Company* to identify the lead opinion record.
- Opinion endpoint lookup for CourtListener opinion 9897232. Consulted its treatment of registration-based consent and its refusal to reach the dormant-Commerce-Clause issue because the issue was unpreserved and unnecessary.

No web searches were used.
