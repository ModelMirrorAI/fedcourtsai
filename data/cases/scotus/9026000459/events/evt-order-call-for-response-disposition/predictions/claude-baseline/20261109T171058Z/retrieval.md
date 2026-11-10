# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: usage error (unknown era token). No rows.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`: 5 recent GVR rows (e.g. Cid v. United States), used only as context on the GVR route.
  - `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
- WebSearch "Pitchford v. Cain Supreme Court decision Batson 2026": confirmed Pitchford (No. 24-7351) was argued Mar 31, 2026 and decided May 28, 2026, 5-4, opinion by Justice Kavanaugh, holding that the defense must have an opportunity to rebut the stated race-neutral reasons. Sources: Wikipedia, UNC SOG blog, SCOTUSblog. This predates the snapshot and is legitimate forward signal. Nothing about this case's disposition surfaced.
- No CourtListener MCP calls.
