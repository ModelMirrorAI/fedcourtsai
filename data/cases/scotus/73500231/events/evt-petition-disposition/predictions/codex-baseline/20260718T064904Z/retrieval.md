# Retrieval

## Corpus and base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, and 2025 Term fee-class rates.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 8`
  - `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
  - The results were generic recent SCOTUS dispositions rather than close analogues and were given little weight.

## CourtListener MCP

- Opinion search for `"Lawlor v. National Screen Service Corp."` in the Supreme Court collection; then fetched opinion 105314 to inspect the Court's claim-preclusion analysis.
- Citation search for `351 U.S. 513`; the search was noisy and was not relied on.
- Opinion search for `"Parr v. United States"` in the Supreme Court collection; then fetched opinion 105416 to inspect its appellate-finality holding.
- Opinion search for `"Ashbourne v. Hansberry"`, citation `894 F.3d 298`, in the D.C. Circuit collection; then fetched opinion 4289979 to inspect its claim-preclusion rule.

No web searches were used.
