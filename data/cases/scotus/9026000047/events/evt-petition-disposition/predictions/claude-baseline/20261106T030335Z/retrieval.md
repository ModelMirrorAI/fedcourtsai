# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`. Stderr: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`. It returned five recent GVR priors, none on FAA §1; I used them only as general context.
- `uv run fedcourts query --docket-number 24-935` (without `--court`). It failed with a usage error saying `--docket-number` needs `--court`, and returned nothing.
- `uv run fedcourts query --court scotus --docket-number 24-935`. Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. It returned the *Flowers Foods v. Brock* docket row and confirmed it is in the corpus; I read nothing further from it.
- I read `metrics/statpack.md`: the modern-cert disposition, relist, CVSG and amicus cuts, and the sal-v7 band table.
- No CourtListener MCP calls and no web searches.
