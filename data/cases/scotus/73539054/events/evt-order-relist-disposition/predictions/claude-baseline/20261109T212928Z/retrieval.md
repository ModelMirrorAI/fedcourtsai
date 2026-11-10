# Retrieval

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` returned a usage message and no rows. I re-issued it without `--era`.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` returned `ranged corpus reads: 37 GET(s), 9699328 byte(s)` and 5 recent GVR rows (Roybal, Harrington, Cid, Burford German Funding, Roofing Designs). None was relevant beyond general shape.
- Web search: "FCC v. AT&T Supreme Court 2026 decision Seventh Amendment forfeiture dissent". It confirmed the June 4, 2026 decision, 8-1 for the FCC, with Thomas dissenting (Daily Signal, Faegre Drinker, CRS LSB11440). This is precedent that predates the snapshot, not this case's outcome.
- Read `metrics/statpack.md`: the relist, CVSG, and amicus cuts and the sal-v8 band table.
- I made no CourtListener MCP calls.
