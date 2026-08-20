# Retrieval log — claude-baseline, 26A139, run 20260820T181919Z

## Corpus lookups (`fedcourts`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-applications --limit 8`
   — `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Recency-ranked
   application priors; mostly extensions.
2. `uv run fedcourts query --court scotus --include-applications --limit 500`
   — `ranged corpus reads: 36 GET(s), 9437184 byte(s)`. Aggregated locally
   (this case's own row excluded before reading): 46 resolved substantive
   priors, 0 granted; response-requested subset 0/7; referred subset 0/16;
   amicus>0 subset 0/6.
3. `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 300`
   — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. 0 granted substantive
   rows surfaced within the ranked window.
4. `uv run fedcourts corpus-info` — errored in this cell (expects a local
   blob; the cell reads through the corpus service). Vintage stated instead
   from the query rows' `last_live_polled` stamps (2026-08-19/2026-08-20).

## Committed base rates

- `metrics/statpack.md`, "The interim docket (applications)" section — pooled
  strictly-prior substantive grant rate 30/225 ≈ 13.3% (OT2025 16/178 +
  OT2024 14/47), clearing the 50-resolved floor.

## CourtListener MCP lookups

1. `search` (dockets, ca1, docket_number 26-1774) — identified the underlying
   case: *State of California v. Trump*, CA1, nature of suit "Voting", filed
   2026-07-02.
2. `docket-entries` for CA1 docket 73568304 (most recent 30 entries) — the
   July 25, 2026 panel order denying the federal defendants' and twelve
   intervening states' stay motions (Gelpí, Rikelman, Dunlap concurring in
   part and dissenting in part), party alignment, and briefing posture. All
   retrieved material predates or is contemporaneous with the snapshot cutoff
   except routine post-cutoff appearance notices, which carry no outcome
   information about the application.
3. `search` (dockets, scotus, q="California", filed 2026-07-25..2026-08-04,
   fields restricted to caseName/docketNumber/dateFiled) — checked for a
   companion federal-government application; 0 results (CourtListener's SCOTUS
   application-docket coverage is sparse, so this is non-confirmation, not
   absence).

## Repository reads (claim semantics, not case facts)

- `src/fedcourtsai/pipeline/interim_signals.py` — the amicus counter
  (`amicus curiae`, singular-only), the referral pattern
  (`referred to the Court`), and the disposition matchers, read to state the
  increment claims against the exact signals that resolve them.

No web searches. No lookup of this application's own disposition or any
post-cutoff development in it was made.
