# Retrieval log

Mode `forward`; no `DECIDED_BEFORE` clock. Nothing retrieved concerned this
application's own disposition.

## Committed base rates

- `metrics/statpack.md`, section "The interim docket (applications)": per-Term
  substantive resolved/granted counts, pooled over Terms 2024-2025 for the
  strictly-prior anchor (31/296 = 10.5%).

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 25`
   `ranged corpus reads: 7 GET(s), 1703936 byte(s)`
2. `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 25`
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --include-applications --limit 60`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
4. `uv run fedcourts query --court scotus --include-applications --limit 400`
   `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   Filtered locally to `application_kind == "substantive"` (69 resolved rows)
   and cross-tabbed by `response_requested`, `referred_to_court`, and
   Solicitor General as applicant.

## CourtListener MCP lookups

1. `search` type `d`, q "Kingdom v. Trump", courts `cadc`, `dcd`: located the
   D.D.C. docket 1:25-cv-00691 (Judge Lamberth).
2. `search` type `d`, q "Kingdom", court `cadc`: located D.C. Circuit dockets
   26-5181, 26-5236, 26-5310.
3. `call_endpoint` `docket-entries` for CADC docket 73520260 (No. 26-5236),
   newest 15 entries: September 18, 2026 per curiam order denying the stay
   (Walker, J., would grant); September 22, 2026 briefing schedule (appellant
   brief November 2, appellee December 2, reply December 23).
4. `call_endpoint` `docket-entries` for CADC docket 74732221 (No. 26-5310),
   all 6 entries: consolidation with 26-5236 and the same orders.

## Web searches

None.
