# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist-count, CVSG-status, and per-Term sections.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  - Failed: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`
  - No `ranged corpus reads` line was printed and no priors were returned.
- `uv run fedcourts query --court scotus --era 2020s --limit 3 --corpus-backend service`
  - Failed with the same corpus-service timeout.
  - No `ranged corpus reads` line was printed and no priors were returned.

## CourtListener MCP lookups

- Opinion search: `"qualified immunity" "clearly established" specificity`, Supreme Court, filed after 2017-01-01. Used to identify the Court's recent specificity decisions, including *Zorn v. Linton* and the recent per curiam cases listed in the reasoning.
- Opinion search: `"fabrication of evidence" (knowingly OR reckless) "due process" qualified immunity`, filed after 2015-01-01. Used to assess whether the petition's cited mens-rea cases reflect a developed doctrinal conflict; results included *Tanner v. Walters*, *Truman v. Orem City*, and *Richards v. County of San Bernardino*.

No web searches were used. No search sought this petition's disposition or subsequent history.
