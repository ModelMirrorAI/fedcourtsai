# Retrieval log

- `uv run fedcourts query --help` — read the flags.
- `uv run fedcourts query --court scotus --disposition denied --limit 5` — stderr: `ranged corpus reads: 8 GET(s), 2031616 byte(s)`. Returned five recent denied SCOTUS rows (Pavatt v. Oklahoma, two Schultz applications, Jesenik v. United States); none related to this case, not used in the number.
- Read committed `metrics/statpack.md` (salience-band table sal-v8, originating-court cut for cafc).
- No CourtListener MCP calls, no web searches.
