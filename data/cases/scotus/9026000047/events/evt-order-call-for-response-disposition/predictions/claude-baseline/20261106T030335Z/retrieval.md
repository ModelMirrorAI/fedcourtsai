# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` returned a usage message and no rows (I re-issued it without `--era`).
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`
  - stderr: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
  - It returned 5 recent GVR rows (e.g. Monsanto v. Dennis, Burford German Funding). I used them only as a shape check that OT2026 GVRs are being recorded.
- I read `metrics/statpack.md` sections: modern cert by disposition; relist, CVSG and amicus cuts; salience band; and the sal-v7 segment table.
- I made no CourtListener MCP calls and no web searches.
