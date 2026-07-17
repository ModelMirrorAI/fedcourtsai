# Retrieval log — scotus/73281381, run 20260717T000329Z

Mode: `forward` (retrieval unrestricted; nothing outcome-revealing exists yet).

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "598 U.S. 631" --limit 8`
   — 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --citation "516 U.S. 442" --limit 8`
   — 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
3. `uv run fedcourts query --court scotus --topic takings --limit 8`
   — 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`

No similar resolved priors surfaced; priors context came from the committed
statpack instead.

## Base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  originating-circuit, relist-count, CVSG, and per-Term tables.
- `metrics/statpack.json` — per-Term per-fee-class detail (paid grant rate:
  5.4% Term 2025, 6.9% Term 2024, 8.0% Term 2023).

## CourtListener MCP lookups

1. `search(type=d, court=scotus, q="Hadley v. City of South Bend")` — 0 results
   (SCOTUS dockets not in RECAP search index).
2. `search(type=d, court=scotus, docket_number=25-1158)` — 0 results.
3. `search(type=d, court=scotus, docket_number=25-1163)` — 0 results.
4. `call_endpoint(dockets, court=scotus, docket_number=25-1158)` — *Amy Hadley
   v. City of South Bend, Indiana*, docket id 73281642, filed 2026-04-08,
   `date_terminated: null` (petition still pending).
5. `call_endpoint(docket-entries, docket=73281642)` — 0 rows (entries not
   exposed for scraped SCOTUS dockets).
6. `call_endpoint(dockets, court=scotus, docket_number=25-1163)` — *Carlos Pena
   v. City of Los Angeles, California*, docket id 73281647, filed 2026-04-09,
   `date_terminated: null` (petition still pending).

These companion-petition status checks are forward-mode signal about related
litigation; no lookup touched this case's own (nonexistent) disposition.

## Web searches

None.
