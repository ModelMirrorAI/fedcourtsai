# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. Attempted command (failed due to unrecognized `--resolved-only` flag):
   - Command: `uv run fedcourts query --court scotus --resolved-only --decided-before 2026-11-04 --originating-court ca10 --limit 10`
   - Result: Exit code 2 (`No such option: --resolved-only`).

2. Executed corpus query for resolved SCOTUS granted priors before `2026-11-04`:
   - Command: `uv run fedcourts query --court scotus --disposition granted --decided-before 2026-11-04 --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Result: Returned 10 granted SCOTUS rows resolved or granted before `2026-11-04`.

## CourtListener MCP Lookups

- None attempted.

## Web Searches

- None attempted.
