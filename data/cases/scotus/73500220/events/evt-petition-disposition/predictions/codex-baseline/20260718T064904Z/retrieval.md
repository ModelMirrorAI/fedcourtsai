# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, Term 2025, and paid-fee-class rates.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 8`
  - Returned no rows.
  - No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search: `"collateral consequences" Padilla "Sixth Amendment"`, limited to filings before July 18, 2026 (10 results). The results included *Padilla v. Kentucky*, 559 U.S. 356 (2010); *Chaidez v. United States*, 568 U.S. 342 (2013); *Farhane v. United States*, 77 F.4th 123 (2d Cir. 2023); *United States v. Johnson*, 272 F. Supp. 3d 728 (D. Md. 2017); and the provisioned Third Circuit opinion in *Nita Patel v. United States* (Oct. 17, 2025). This was used only to check the predecision doctrinal landscape.

No web searches were used, and no lookup sought this petition's disposition or subsequent history.
