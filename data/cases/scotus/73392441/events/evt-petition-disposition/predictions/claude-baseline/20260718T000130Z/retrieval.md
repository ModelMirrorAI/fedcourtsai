# Retrieval log — scotus/73392441 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Beyond the provisioned inputs (snapshot, questions-presented.txt, petition.txt)
and the committed `metrics/statpack.md`:

1. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   - Purpose: a spot check of recent resolved SCOTUS priors (distribution/relist
     patterns around grants vs. denials). Returned a mix of granted (multiple
     relists/distributions, high salience) and denied/dismissed rows;
     consistent with the statpack's relist-count signal.

No CourtListener MCP lookups were made — the provisioned snapshot is dated
2026-07-17 (one day old) and carries the full supremecourt.gov docket state.
No web searches. The case's own outcome was not sought or encountered
(forward cell; the petition awaits the September 28, 2026 conference).
