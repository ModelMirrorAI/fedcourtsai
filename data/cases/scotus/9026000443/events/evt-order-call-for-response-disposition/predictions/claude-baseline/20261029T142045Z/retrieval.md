# Retrieval log

Corpus:
- `uv run fedcourts query --court scotus --docket-number 26-360` — `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Open; distributed for 11/6/2026; originating ca6; ERISA Industry Committee as amicus.
- `uv run fedcourts query --court scotus --docket-number 26-387` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Open; same posture; ca6.
- `uv run fedcourts query --court scotus --docket-number 26-443` — `ranged corpus reads: 0 GET(s), 0 byte(s)`. This docket's own row (no disposition).
- The same three queries re-run once more to print selected fields (stderr suppressed; same rows).

Web (supremecourt.gov live dockets, forward mode):
- 26-360: waiver 9/24, distributed 10/14, ERIC amicus 10/16, response requested 10/19, response extension granted to 12/18/2026.
- 26-387: same pattern; response requested 10/19; respondents' extension motion 10/28.
- 26-443: response requested 10/19; respondents' extension motion submitted 10/27. No disposition.

Committed base rates: `metrics/statpack.md` (salience band table, relist/CVSG/circuit cuts).
No CourtListener MCP calls.
