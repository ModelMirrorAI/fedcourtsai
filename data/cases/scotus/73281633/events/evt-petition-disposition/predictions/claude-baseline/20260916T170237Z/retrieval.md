# Retrieval log

Forward cell; retrieval unrestricted. Nothing retrieved concerned this case's
disposition, which does not yet exist (conference set for 2026-09-28).

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned recent granted SCOTUS rows (substantive applications and a few
   cert grants); none topically similar to a commercial-speech petition.
   Used only to confirm the shape of recent grants, not as analog priors.
2. `uv run fedcourts query --court scotus --era 2020s`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned recent resolved SCOTUS rows, again structurally rather than
   topically matched; not relied on.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Modern cert petitions by originating circuit" (ca2 row),
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "Cert petitions by salience band",
  "SCOTUS cert petitions by Term", and "Segment base rate by salience band
  (sal-v4)" (pooled the `baseline` bracketed `reached` figures for OT2017
  through OT2024).

## CourtListener MCP lookups

1. `get_endpoint_item` on `dockets`, item `73281633`, fields id, case_name,
   docket_number, court_id, date_filed, date_terminated, date_modified,
   date_last_filing, nature_of_suit, cause. Result: not terminated;
   `date_modified` 2026-07-01, consistent with the snapshot (no post-snapshot
   movement).
2. `search` type `o`, court `scotus`, q `"Central Hudson" "commercial
   speech"`, filed after 2023-06-01. Result: two entries for *Chiles v.
   Salazar* (No. 24-539, decided 2026-03-31), nothing else. Used to check
   for a possible intervening decision / GVR hook; concluded there is none.
3. `search` type `d`, court `scotus`, q `"Central Hudson"`, filed after
   2025-06-01. Result: no dockets. Used to check for a companion or hold
   candidate on the Court's docket; found none.

## Web searches

None.
