# Retrieval

## Committed base-rate material

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Consulted the Term 2025 paid-fee-class detail in `metrics/statpack.json`.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '581 U.S. 246' --citation '563 U.S. 333' --limit 5 --corpus-backend ranged` — attempted to obtain resolved SCOTUS priors sharing the petition's core FAA authorities. The lookup failed because the runner could not resolve the remote corpus-store hostname. It returned no priors and printed no `ranged corpus reads: ...` line.

## CourtListener MCP lookups

- Opinions search for `"separate consideration" arbitration FAA preempt`, limited to the First, Second, Third, Fourth, Sixth, Eighth, and Tenth Circuits through July 13, 2026 — no results.
- Opinions search for `arbitration "independent consideration" Prima Paint` through July 13, 2026 — returned 19 results; the first page included *Cheek*, *Glazer*, and other consideration decisions. Used to test the claimed conflict's legal context.
- RECAP search for Supreme Court docket `25-34` through July 13, 2026 — no results. Used to seek pre-disposition procedural context for the related *Johnson* litigation, not this case's outcome.
- Docket search for Supreme Court docket `25-34` through July 13, 2026 — no results. Same purpose.
- Fourth Circuit opinions search for `Cheek Noohi Johnson arbitration consideration` through July 13, 2026 — returned five results, including published *Johnson v. Continental Finance Co.*, 131 F.4th 169 (2025), and *Noohi v. Toll Bros.* Used to confirm the principal circuit authorities.
- Opinions search for `"131 F.4th 169"` from March 12, 2025 through July 13, 2026 — returned *Shively v. ACI Learning Holdings, LLC* and *Johnson* itself. Used to assess subsequent uptake of *Johnson*.

No web searches were used. No information about this case's eventual disposition was sought or encountered.
