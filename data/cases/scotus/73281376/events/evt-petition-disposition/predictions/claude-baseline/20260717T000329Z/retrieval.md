# Retrieval log — scotus/73281376, evt-petition-disposition, claude-baseline, 20260717T000329Z

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "436 U.S. 658" --citation "475 U.S. 469" --citation "485 U.S. 112" --limit 8`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - Result: no rows returned.
2. `uv run fedcourts query --court scotus --citation "436 U.S. 658" --limit 8`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - Result: no rows returned.

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Modern cert petitions by originating circuit" (ca4 row), "Cert
  petitions by relist count", "Cert petitions by CVSG status", and the per-Term
  table (Term 2025 row).

## CourtListener MCP lookups

1. `call_endpoint` on `dockets` with `id=73281376` (fields: id, case_name,
   docket_number, date_filed, date_terminated, date_last_filing) — confirmed the
   docket is still pending (`date_terminated: null`). Forward-mode check only; no
   outcome information existed or was sought.

## Web searches

None.
