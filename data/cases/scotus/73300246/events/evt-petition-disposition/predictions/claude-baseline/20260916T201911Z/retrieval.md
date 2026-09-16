# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8 --corpus-backend service`
  stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  Purpose: confirm the corpus query service was reachable and see the shape of recent SCOTUS rows. The returned rows (recent substantive applications and unrelated petitions) were not similar to this takings dispute and did not inform the number. No `--decided-before` clock applies (forward cell, `decided_before: null`).

## CourtListener MCP lookups

None. The provisioned snapshot is dated 2026-09-16 (today) and the petition is distributed for the September 28, 2026 conference, so no disposition could exist and no docket movement was expected.

## Web searches

None.
