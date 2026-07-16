# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” the Ninth Circuit, relist, CVSG, and per-Term tables.
- Consulted the 2025 Term paid-filing detail in `metrics/statpack.json`.

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic 'compelled speech' --limit 5`
  - Failed before returning rows because the corpus remote hostname could not be resolved. No `ranged corpus reads: …` line was printed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic 'trade secrets takings' --limit 5`
  - Failed before returning rows because the corpus remote hostname could not be resolved. No `ranged corpus reads: …` line was printed.

## CourtListener MCP lookups

- Opinion search for `Ruckelshaus Monsanto "highly regulated" trade secret`, limited to filings before July 17, 2026. It returned 13 matches and metadata for eight, including *Pharmaceutical Research and Manufacturers of America v. Stolfi* (9th Cir. Aug. 26, 2025), *Maine Education Ass'n Benefits Trust v. Cioppa*, and other takings/regulatory cases. The case-specific result was the pre-snapshot lower-court opinion, not a Supreme Court disposition.
- Opinion search for `compelled speech "information asymmetries" Amestoy`, limited to filings before July 17, 2026. It returned no matches.

No web searches were used.
