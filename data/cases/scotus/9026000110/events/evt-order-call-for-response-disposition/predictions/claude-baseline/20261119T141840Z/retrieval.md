# Retrieval log

Beyond the provisioned inputs:

1. `metrics/statpack.md` — read the salience-band table (sal-v8), the segment base rate by band, and the paid-segment relist-count, CVSG-status and amicus-count cuts.
2. `uv run fedcourts query --help` — usage text.
3. `uv run fedcourts query --court scotus --docket-number 26-107` — returned the Walls v. Prince George's County row (vided-amicus companion): distribution_count 2, disposition `denied`, date_cert_denied 2026-11-09. stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
4. `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` — rejected as a usage error (`Unknown era 'roberts'`); not re-issued, since the band anchor and statpack cuts already supplied the base rates.
5. `uv run fedcourts query --court scotus --docket-number 26-107` and `... --docket-number 26-110` (re-run with stderr discarded to print selected fields) — 26-107 as above; 26-110 row shows this petition still open: distribution_count 1, no disposition, last_live_polled 2026-11-19. Transfer lines not captured on this re-run.

No CourtListener MCP calls and no web searches were made.
