# Retrieval beyond the provisioned inputs

## Committed base rates

- Read `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and per-Term tables.
- Read the Term 2025 paid-fee detail in `metrics/statpack.json`.

## Corpus lookup

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  - The corpus sidecar timed out: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`
  - No results or `ranged corpus reads` line were returned.

## CourtListener MCP

1. Opinion search: `q=\"alternative remedy\" \"new Bivens context\"`, filed before 2026-07-18, 6 results.
2. Opinion search: `q=\"meaningfully different\" Bivens \"false arrest\"`, filed before 2026-07-18, 6 results.
3. SCOTUS opinion search: `q=Bivens`, filed from 2022-06-01 through 2026-07-17, 8 results.
4. Opinion search by case name: `Goldey v. Fields`, court `scotus`, 3 results.
5. Opinion search by case name: `Arias v. Herzon`, 3 results.
6. Opinion search by case name: `Watanabe v. Derr`, 4-result limit (2 returned).
7. Opinions endpoint item 11086520, fields `id`, `type`, and `html_with_citations` (*Goldey v. Fields*).
8. Opinions endpoint item 11121515, fields `id`, `type`, and `html_with_citations` (*Arias v. Herzon*).

The first two searches also returned the pre-petition Second Circuit opinion in this case. No search sought or surfaced a Supreme Court disposition of this petition.
