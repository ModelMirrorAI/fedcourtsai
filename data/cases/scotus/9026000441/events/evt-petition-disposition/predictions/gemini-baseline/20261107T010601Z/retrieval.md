# Retrieval Log

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000441 --event evt-petition-disposition --role predictor`
   - Output: resolved `case_id scotus/9026000441`, `corpus corpus/corpus.db`, `event data/cases/scotus/9026000441/events/evt-petition-disposition/event.yaml`.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Returned 5 resolved SCOTUS priors with `disposition: "denied"` from the 2020s era.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer line: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Returned 5 resolved SCOTUS priors with `disposition: "granted"` from the 2020s era (including recent OT2026 grants `26-12`, `26-204`, and `25-1103`).
4. `uv run fedcourts query --court scotus --judge "Brent Evan Newton" --include-open --limit 10`
   - Transfer line: `ranged corpus reads: 687 GET(s), 179896320 byte(s)`
   - Returned 0 rows (`--judge` searches judicial authors rather than counsel).
5. `uv run fedcourts query --court scotus --docket-number 26-441`
   - Transfer line: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Returned the open corpus row for `scotus/9026000441` (*Christopher Rydberg v. United States*, `docket_number: "26-441"`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", q=""health care benefit program" "FECA" OR "Federal Employees' Compensation Act" "24(b)"")`
   - Returned 44 opinion results, including Fifth Circuit and other circuit decisions applying 18 U.S.C. § 24(b) (*e.g.*, *United States v. Terry Anderson*, *United States v. Richard Plato*, *United States v. Lamarre*).
2. `mcp_courtlistener_search(type="o", q=""Nourian" "Rydberg"")`
   - Returned 0 results in the CourtListener opinion index.
3. `mcp_courtlistener_search_document(opinion_id=[4584991, 10477247], query="health care benefit program")`
   - Returned `HTTP 429: Rate limit exceeded: 25/min`. Degraded gracefully to the provisioned record and local corpus tools per the prompt contract.
4. `mcp_courtlistener_search(type="o", q=""Federal Employees' Compensation Act" "1347" OR "24(b)"")`
   - Returned `HTTP 429: Rate limit exceeded: 25/min`. Degraded gracefully to the provisioned record and local corpus tools per the prompt contract.

## 3. Web Searches

None attempted.
