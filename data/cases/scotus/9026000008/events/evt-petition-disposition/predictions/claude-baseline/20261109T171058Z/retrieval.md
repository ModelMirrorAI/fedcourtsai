# Retrieval
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`. Stderr: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. It returned recent GVR rows (e.g. Cid v. United States, Monsanto v. Dennis), used only for the shape of the GVR population.
- An earlier `uv run fedcourts query --court scotus --disposition gvr --era roberts --limit 5` printed usage help (the `--era` value was not accepted), so it returned no rows.
- `uv run fedcourts query --help`.
- WebSearch (standard): "Supreme Court teacher pronouns certiorari petition 2026 Polk Montgomery County Kluge". It returned the docket PDFs, amicus pages and advocacy pages, all describing the case as pending. No disposition was found.
- Statpack: `metrics/statpack.md`, the "Segment base rate by salience band (sal-v8)" table.
- No CourtListener MCP calls.
