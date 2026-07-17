# Retrieval log — claude-baseline / 20260717T180352Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-07-17.json`,
`record/documents/questions-presented.txt`, `record/documents/petition.txt`,
`record/documents/documents.json`, `record/context.json`):

## Corpus base rates (committed statpack)

- Read `metrics/statpack.md` — anchored on "Modern discretionary-cert
  petitions by disposition", the relist-count and CVSG signal cuts, the
  originating-circuit cut (ca3), and the per-Term table. The committed
  statpack carries no "Segment base rate by salience band" section in this
  revision, so the relist/CVSG buckets served as the signal-magnitude
  calibration instead.
- Read `metrics/statpack.json` (`terms[].classes`) for the per-fee-class
  detail: paid-petition grant rates 5.4% (T2025), 6.9% (T2024), 8.0% (T2023),
  vs ~1% IFP.

## Corpus query (fedcourts CLI, via the local corpus service)

- `uv run fedcourts query --court scotus --disposition granted --limit 8`
  - stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
  - Returned 8 granted 2020s SCOTUS rows, but with empty captions and no
    resolution dates — not informative beyond the statpack, so I did not
    pursue further filtered queries (`--citation`/`--topic` are sparse on
    SCOTUS rows per the prompt's coverage notes).

## CourtListener MCP

- `search(type=d, court=scotus, docket_number=25-6344)` — 0 results.
- `search(type=d, court=scotus, case_name=Tovar)` — 0 results.
- `call_endpoint(dockets, {court: scotus, docket_number: 25-6344})` — found
  docket 73282036, *Ralph Kevin Tovar v. United States* (CA11, filed
  2025-12-11): `date_terminated`, `date_cert_granted`, `date_cert_denied` all
  null (record last modified 2026-05-18). Used as forward signal that the
  companion petition raising the same question is still pending/held. This
  lookup concerned the companion case only, never this case's own outcome.

## Web searches

None.
