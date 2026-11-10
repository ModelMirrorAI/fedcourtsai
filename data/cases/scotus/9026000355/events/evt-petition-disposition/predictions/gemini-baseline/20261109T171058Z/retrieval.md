# Retrieval Log

## 1. Corpus Tooling (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000355" --event "evt-petition-disposition" --role predictor`
   - Resolved `case_id: scotus/9026000355`, `corpus: corpus/corpus.db`, and `event: data/cases/scotus/9026000355/events/evt-petition-disposition/event.yaml`.
2. `uv run fedcourts query --help`
   - Inspected structured filter options for corpus retrieval.
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Returned 10 recent resolved OT2026 SCOTUS cert petitions (`26-18`, `26-55`, `26-85`, `26-87`, `26-107`, `26-115`, `26-119`, `26-167`, `26-175`, `26-222`), all denied on 2026-11-09 after 1 or 2 distributions.

## 2. CourtListener MCP Server Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="CrowdStrike"`, `num_results=10`, `fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "status"]`)
   - Returned 1 published opinion (`GoSecure v. CrowdStrike`, 2026 Tex. Bus. 13, 2026-03-13), confirming no other appellate opinions arising from the July 2024 CrowdStrike outage are indexed in the opinion database.
2. `mcp_courtlistener_search` (`type="o"`, `q=""41713(b)(1)" AND "service""`, `num_results=10`, `fields=["caseName", "court", "dateFiled", "docketNumber", "citation"]`)
   - Returned 407 matching opinions interpreting 49 U.S.C. § 41713(b)(1) "service" preemption (top 10 shown, including *Delta Air Lines, Inc. v. Iuliano*, *Campbell Clegg v. American Airlines, Inc.*, *Air Evac EMS v. Sullivan*, and *Watson v. Air Methods Corp.*), confirming no recent circuit split on third-party software vendor preemption under the Airline Deregulation Act.
