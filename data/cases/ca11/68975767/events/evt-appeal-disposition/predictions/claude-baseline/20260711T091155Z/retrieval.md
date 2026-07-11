# Retrieval log — claude-baseline, ca11/68975767, 20260711T091155Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-07-11.json`,
`event.yaml`, `record/context.json`):

## Corpus lookups (`fedcourts` CLI, ranged backend)

1. `uv run fedcourts query --court ca11 --topic "3840 Trademark" --corpus-backend ranged --limit 8`
   — no matching priors returned.
   `ranged corpus reads: 99 GET(s), 25952256 byte(s)`
2. `uv run fedcourts query --court ca11 --limit 10 --corpus-backend ranged`
   — 10 historical ca11 rows, dispositions mostly `other` (one `denied`).
   `ranged corpus reads: 45 GET(s), 11796480 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md` (by-court cut: ca11 resolved
  base rate other 95.6% / denied 2.2% / granted 2.2%).

## CourtListener MCP

None. The snapshot shows the appeal was decided ("Opinion Issued",
2024-09-24), so any live docket or opinion lookup on this case would have
revealed the outcome; retrieval on this case was deliberately skipped under
the never-retrieve-the-outcome rule (see flags.json).

## Web searches

None.
