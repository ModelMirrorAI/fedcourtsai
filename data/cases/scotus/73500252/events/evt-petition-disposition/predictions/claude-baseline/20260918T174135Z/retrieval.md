# Retrieval log

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   Row-shape check on recent grants; returned mostly OT2025 interim applications and two OT2025 cert grants. Not case-matched.
2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 4`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Recent GVRs (Monsanto v. Salas / Johnson, granted 2026-06-30, etc.). Shape only.

A first attempt passed a free-text argument and was rejected by the CLI (no query executed).

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "by originating circuit", "by relist count", "by CVSG status", "by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (anchor: `elevated` bracketed reached rate pooled over Terms 2017 to 2024).

## CourtListener MCP calls

1. `search` type=d, court=scotus, q="Conti OR Cantero escrow", filed_after 2025-06-01: 0 results.
2. `get_endpoint_item` dockets id=73500252: confirmed this docket (25-1350, filed 2026-06-03, last modified 2026-08-26). No entries newer than the snapshot.
3. `call_endpoint` dockets court=scotus docket_number=25-1230: resolves to *Google LLC v. VirtaMove* (unrelated; the BIO filename's number is an artifact).
4. `call_endpoint` dockets court=scotus docket_number=25-1004: *Citizens Bank, N.A. v. John Conti*, filed 2026-02-23, last modified 2026-08-26.
5. `call_endpoint` docket-entries docket=73281044: 0 results (no entries carried for the SCOTUS *Conti* docket).
6. `call_endpoint` dockets with a `case_name__icontains` filter: rejected by the endpoint schema (no query executed).
7. `search` type=d, court=scotus, case_name="Cantero": 0 results.

No web searches. Nothing retrieved concerned this petition's own disposition.
