# Retrieval log — scotus/73389313, evt-petition-disposition, claude-baseline, 20260718T000130Z

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  — stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`. Pulled recent
  granted priors to see what a granted 2020s petition's docket signals look like
  (multiple distributions/relists, represented parties, salience-selected rows) —
  this case matches none of them.
- Committed `metrics/statpack.md` and `metrics/statpack.json` (per-Term
  per-fee-class detail) — base-rate anchors: modern-cert disposition split,
  relist-count cut, CVSG cut, originating-circuit cut, Term 2025 paid/IFP grant
  rates. No corpus transfer (committed files).

## CourtListener MCP

- `search` (type `d`, q "Farr v. Grant", courts ca8+wdmo+mowd) — rejected:
  `wdmo` is not a valid court id (validation error, no data returned).
- `search` (type `d`, q "Farr Grant", courts ca8+mowd) — found the underlying
  district case: *Farr v. Grant*, W.D. Mo. 4:24-cv-00439 (docket 68910257),
  cause 42:1983, nature of suit "440 Civil Rights: Other", filed 2024-07-01,
  terminated 2024-12-16.
- `search` (type `r`, docket 4:24-cv-00439, q "dismiss") — returned the docket
  shell only; no entry text (fields not in that index).
- `call_endpoint` (`docket-entries`, docket 68910257, newest first, 15 rows) —
  confirmed the procedural history: Rule 12(b)(6)/jurisdiction dismissal orders
  (entry 78, 2024-12-16), reconsideration denied 2025-05-19, Eighth Circuit
  No. 25-1525 affirmed 2025-10-10, all predating the snapshot. No information
  about the cert petition's disposition was sought or surfaced.

## Web searches

None.
