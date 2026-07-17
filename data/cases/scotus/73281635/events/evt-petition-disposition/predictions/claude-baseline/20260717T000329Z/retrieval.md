# Retrieval log — scotus/73281635 evt-petition-disposition (claude-baseline, 20260717T000329Z)

Beyond the provisioned snapshot and documents:

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "515 U.S. 189" --citation "486 U.S. 330" --limit 6`
  → 0 rows (the corpus citation index carries mostly historical merits
  opinions; no prejudgment-interest cert priors surfaced).
  stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
- Committed `metrics/statpack.md` (no live corpus call): modern
  discretionary-cert disposition base rates, originating-circuit table
  (ca7 ≈ 2.0% granted), relist-count and CVSG buckets, per-Term rates. The
  statpack currently carries no salience-band table, so I anchored on the
  disposition/relist/CVSG cuts directly.

## CourtListener MCP

- `call_endpoint` `dockets` `{"id": 73281635}` → confirmed the petition is
  still pending as of this run (`date_cert_granted`/`date_cert_denied`/
  `date_terminated` all null; docket 25-1146, appeal from ca7 No. 24-1674,
  judgment 2025-11-06, rehearing denied 2025-12-30). No outcome information
  existed to leak (forward cell).

## Web searches

None.
