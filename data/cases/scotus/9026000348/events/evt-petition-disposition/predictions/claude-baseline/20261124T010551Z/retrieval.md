# Retrieval log

- `metrics/statpack.md` (committed): relist, CVSG, amicus-count cuts and the salience band table.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` — returned 5 recent GVR rows (generic sample; not used in the number). stderr: `ranged corpus reads: 34 GET(s), 8781824 byte(s)`.
- `uv run fedcourts query --help` (twice; one piped through a grep that errored on its pattern, no output used).
- `curl https://www.supremecourt.gov/RSS/Cases/JSON/26-304.json` — live docket of United States v. Jackson (the petition this one asks to be held for): BIO Nov. 2, reply Nov. 17, distributed for Conference of 12/4/2026.
- `curl https://www.supremecourt.gov/RSS/Cases/JSON/26-348.json` — this case's live docket; matches the snapshot (last entry: distributed for Conference of 12/4/2026).
- `ls data/cases/scotus/9026000304` — listed directory names only (`events`, `summaries`); nothing inside was opened.
- No CourtListener MCP calls and no web searches.
