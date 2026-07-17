# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, especially modern discretionary-cert disposition rates, originating-circuit rates, relist and CVSG cuts, and the paid Term 2025 fee-class rate.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
  - Returned five recent grant priors; their conference distribution counts ranged from three to 22.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 197 GET(s), 51511296 byte(s)`
  - Returned five recent denial priors; each had three conference distributions.

## CourtListener MCP lookups

- Opinion search for `"intentional misuse" vehicle "substantive due process"` (10 results). The leading appellate results included *Dean v. McKinney*, *Browder v. City of Albuquerque*, and decisions from the Eighth and Sixth Circuits.
- Opinion search for `Browder Dean "qualified immunity" "police vehicle"`, limited to filings before July 17, 2026. The sole result was *Dean v. McKinney*.
- Opinion search for `Browder Lewis "police vehicle" "qualified immunity"`, limited to filings before July 17, 2026. Results included Tenth Circuit cases, *Dean*, an Eleventh Circuit vehicle case, and the provisioned lower-court opinion in this case.

No web searches were used. No search sought this petition's disposition or subsequent history.
