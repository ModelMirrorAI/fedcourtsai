# Retrieval log — scotus/73389781, run 20260718T000130Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, and
brief-in-opposition texts), this cell consulted:

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — sampled the profile of recent granted petitions (elite Supreme Court
   counsel, multiple conference distributions) as a contrast with this
   petition's zero-relist, small-firm, no-amicus profile.
   stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`

   (An earlier invocation with an unsupported `--text` option errored at
   argument parsing and performed no corpus read.)

2. Committed base rates: `metrics/statpack.md` (modern discretionary-cert
   disposition split, relist-count and CVSG cuts, per-Term table) and
   `metrics/statpack.json` (Term 2025 per-fee-class detail: paid ≈ 5.4% grant,
   IFP ≈ 1.1%).

## CourtListener MCP

None. The provisioned snapshot was fetched 2026-07-17 (the day before this
run) and already reflects the July 8, 2026 distribution for the September 28,
2026 conference, so no live docket lookup was needed.

## Web searches

None.
