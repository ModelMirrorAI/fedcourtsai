# Retrieval

## Corpus

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 8`
  - Returned no rows and emitted no transfer-statistics line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8 --corpus-backend service`
  - `ranged corpus reads: 133 GET(s), 34865152 byte(s)`
  - Consulted as broad modern grant priors. The eight returned grants were filed in 2024–2026 and had three or more conference distributions; they were not subject-matter matches.

## Committed base rates

- `metrics/statpack.md`: modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- `metrics/statpack.json`: 2025 Term fee-class detail, including the estimated paid-petition grant rate.

## CourtListener MCP

All searches excluded material filed after May 27, 2026 and were directed to general doctrine or lower-court precedent, not this petition's disposition.

- Opinions search: `Remmer extraneous information overwhelming evidence prejudice jury deliberations` across the federal courts of appeals. Returned three results.
- Opinions search: `"need not conclude that the verdict" "would have been different" jury tampering`. Returned *United States v. Morrison*, *United States v. Dutkel*, and *United States v. Henley*.
- Opinions search: `"volume of incriminating evidence" extraneous information prejudice`. Returned eight results, including *United States v. Lloyd* and *State v. Soto*.
- Opinions search: `"overwhelming evidence" "extraneous information" Remmer jury`. Returned results including *United States v. Scull*, *United States v. Lloyd*, and the already-provisioned Sixth Circuit decision in *United States v. Maund*.
- Supreme Court opinions search: `Remmer juror extraneous information prejudice`. Returned *Dietz v. Bouldin*, *Rushen v. Spain*, and *Remmer v. United States*.

No general web search was used.
