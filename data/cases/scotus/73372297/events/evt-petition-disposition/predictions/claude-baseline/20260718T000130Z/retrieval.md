# Retrieval log — scotus/73372297, run 20260718T000130Z

Mode: `forward` (pending petition; conference set for 2026-09-28).

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --era modern --limit 8`
   - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   - Returned no rows (era filter mismatch); superseded by the next call.
2. `uv run fedcourts query --court scotus --limit 8`
   - stderr: `ranged corpus reads: 430 GET(s), 112590848 byte(s)`
   - Returned 8 recent resolved SCOTUS priors (used as a sanity check on
     current-Term grant/deny patterns; the query surface has no
     originating-court filter, so CAFC-specific anchoring came from the
     statpack instead).

## Base rates

- Committed `metrics/statpack.md`: modern discretionary-cert disposition
  table, originating-circuit cut (cafc: granted 3.0%), relist-count cut
  (0 relists: granted 0.8%), CVSG cut, per-Term table (OT2024/OT2025).
- Committed `metrics/statpack.json`: per-Term fee-class detail (OT2025 paid
  grant ~5.4% vs IFP ~1.1%; OT2024 paid ~6.9% vs IFP ~0.9%).

## CourtListener MCP lookups

1. `search(type=o, court=cafc, docket_number=2025-1769)` — 0 results.
2. `search(type=o, court=cafc, q="25-1769")` — 0 results.
   - The Federal Circuit decision below (nonprecedential, anonymized Jane Doe
     vaccine appeal) is not in CourtListener's opinion index; the petition's
     own account of the decision was used instead.

No web searches. Nothing outcome-revealing surfaced (the petition is pending;
no disposition exists).
