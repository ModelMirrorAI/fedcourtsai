# Retrieval Log

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000568" --event "evt-petition-arrival-disposition" --role predictor`
   - Returned case, corpus, and event paths (`scotus/9026000568`, `corpus/corpus.db`, `data/cases/scotus/9026000568/events/evt-petition-arrival-disposition/event.yaml`).
2. `uv run fedcourts query --help`
   - Returned CLI flag documentation for `fedcourts query`.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Returned 10 recent granted SCOTUS rows from the 2020s era, including *Rhoney v. Barbosa da Cunha*, No. 26-104 (`scotus/9026000104`, cert. granted `2026-10-01`).
4. `uv run fedcourts query --court scotus --docket-number 26-104`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned the corpus row for lead case *Rhoney v. Barbosa da Cunha*, No. 26-104 (`scotus/9026000104`).
5. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent GVR-disposed SCOTUS rows from the 2020s era.
6. `uv run fedcourts query --court scotus --include-open --era 2020s -- limit 25` (`--include-open --era 2020s --limit 25`)
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 25 recent SCOTUS rows from the 2020s era.
7. `uv run fedcourts query --court scotus --include-open --era 2020s --attorney "D. John Sauer" --limit 20`
   - Failed with exit code 2 (`No such option: --attorney`).
8. `uv run fedcourts query --court scotus --include-open --era 2020s --originating-court ca6 --limit 10`
   - Failed with exit code 2 (`No such option: --originating-court`).
9. `for d in 26-564 26-565 26-566 26-567 26-568 26-569 26-570; do uv run fedcourts query --court scotus --docket-number $d; done`
   - Transfer lines (7 calls): `ranged corpus reads: 0 GET(s), 0 byte(s)` on each of the 7 calls.
   - Returned the corpus rows for dockets `26-564` through `26-570`.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", q='"1225(b)(2)(A)" "Yajure Hurtado"')`
   - Returned 2,340 opinion matches across federal courts addressing 8 U.S.C. § 1225(b)(2)(A) and *Matter of Yajure Hurtado*, 29 I. & N. Dec. 216 (BIA 2025).
2. `mcp_courtlistener_search(type="o", q='"Barbosa da Cunha" "1225(b)(2)(A)"')`
   - Returned 353 opinion matches citing *Barbosa da Cunha* and 8 U.S.C. § 1225(b)(2)(A).
3. `mcp_courtlistener_search(type="o", court=["ca2", "ca5", "ca7", "ca9", "ca3", "ca4", "ca6", "ca8", "ca10", "ca11", "ca1"], filed_after="2026-01-01", q='"1225(b)(2)(A)" "Yajure Hurtado"')`
   - Returned 1 appellate opinion match (*Guerrero Orellana v. Moniz*, 1st Cir., No. 25-1967, decided March 30, 2026).

## 3. Local File Inspection Note

- Ran `glob` on `data/cases/scotus/9026000104` (returned file list only; did not read any files in that directory).
