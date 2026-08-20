# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --include-applications --limit 8` —
  recency-ranked rows were dominated by time-extension applications and one
  denied pro se substantive application; not useful as priors, so the
  statpack's substantive slice stayed the quantitative anchor.
  Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.

## Committed repo inputs beyond the provisioned cell

- `metrics/statpack.md` — "The interim docket (applications)" section: pooled
  strictly-prior baseline 30/225 ≈ 13.3% for a Term-2026 application
  (Term 2025: 16/178; Term 2024: 14/47), clearing the 50-resolved floor.
- `data/cases/scotus/9526000124/.../predictions/claude-baseline/20260816T173750Z/prediction.json`
  — read for field conventions; it revealed the companion federal application
  in the same matter (pending as of its 2026-08-16 snapshot, six amicus
  briefs, response requested). Used as forward signal; disclosed in
  `flags.json`.

## CourtListener MCP

All docket-entry queries were time-bounded to on/before 2026-07-29 to avoid
surfacing this application's own disposition.

1. `search` (type `d`, court `ca1`, docket 26-1774) — identified the
   originating case: *State of California v. Trump*, CA1 26-1774, nature of
   suit "Voting", filed 2026-07-02.
2. `search` (type `r`, court `ca1`, docket 26-1774, entries before
   2026-07-30) — returned docket shell only; superseded by the next call.
3. `call_endpoint` (`docket-entries`, docket 73568304, `date_filed__lte`
   2026-07-29) — CA1 entries: notice of appeal by federal defendants (7/2),
   final judgment + memorandum in the supplemental record (entries 207–208),
   federal defendants' emergency stay motion (7/7), twelve intervenor states'
   emergency stay motion (7/10), consolidation with 26-1779, oppositions and
   amicus filings.
4. `get_more_results` (same query) — the July 25 order: panel of Gelpí,
   Rikelman, and Dunlap (concurring in part, dissenting in part) denied both
   stay motions; amicus leave granted.

No web searches. No retrieval of either SCOTUS application docket's
post-cutoff state.
