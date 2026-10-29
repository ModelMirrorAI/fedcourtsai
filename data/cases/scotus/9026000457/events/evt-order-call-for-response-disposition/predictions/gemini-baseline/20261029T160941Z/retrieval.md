# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts`)

1. `uv run fedcourts open-events --court scotus --limit 30`
   - Outcome: CLI usage error (`No such option: --limit`).
2. `uv run fedcourts query --court scotus --include-open --limit 30`
   - Transfer: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Outcome: Returned 30 recent SCOTUS corpus rows (open and recently decided OT 2025/2026 petitions and applications).
3. `uv run fedcourts query --court scotus --docket-number 26-457`
   - Transfer: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Outcome: Returned the corpus row for `scotus/9026000457` (*Novartis Pharmaceuticals Corporation v. Lynn Fitch, Attorney General of Mississippi*, No. 26-457).
4. `uv run fedcourts query --court scotus --docket-number 26-34`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Outcome: Returned `scotus/9026000034` (*Catherine L. Hanaway v. Thomas L. Sanderson*, No. 26-34, denied 2026-10-19).
5. `uv run fedcourts query --court scotus --citation "563 U.S. 110" --include-open --limit 20`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Outcome: Empty result (with `note:` explaining that `--citation` matches a case's own parallel cites on the 200 populated SCOTUS rows).
6. `uv run fedcourts query --court scotus --citation "95 F.4th 1136" --include-open --limit 20`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Outcome: Empty result (`note:` on citation column coverage).
7. `uv run fedcourts query --court scotus --include-open --limit 100`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Outcome: Returned 100 recent SCOTUS rows; filtered locally for related party names.
8. `uv run fedcourts query --court scotus --docket-number 24-621`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Outcome: Returned `scotus/72010643` (*NRSC v. FEC*, No. 24-621).
9. `uv run fedcourts query --court scotus --docket-number 25-830`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Outcome: Returned `scotus/73280330` (*Kanuszewski v. Shah*, No. 25-830).
10. `uv run fedcourts query --court scotus --attorney "Jessica Lynn Ellsworth" --include-open --limit 20`
    - Outcome: CLI usage error (`No such option: --attorney`).
11. `uv run fedcourts query --court scotus --attorney "Scott Grant Stewart" --include-open --limit 20`
    - Outcome: CLI usage error (`No such option: --attorney`).
12. `uv run fedcourts query --court scotus --originating-court ca5 --include-open --limit 30`
    - Outcome: CLI usage error (`No such option: --originating-court`).
13. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 25`
    - Transfer: `ranged corpus reads: 27 GET(s), 6881280 byte(s)`
    - Outcome: Returned 25 granted SCOTUS petitions in the 2020s era.
14. `uv run fedcourts query --court scotus --include-open --limit 100` (second run, warm cache)
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Outcome: Returned 100 recent SCOTUS rows from warm service cache.
15. `uv run fedcourts query --court scotus --docket-number 24-352`
    - Transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
    - Outcome: Returned `scotus/72484065` (*United States ex rel. Angelo v. Allstate Ins. Co.*, No. 24-352).
16. `uv run fedcourts query --court scotus --judge "James C. Ho" --judge "Irma Carrillo Ramirez" --limit 20`
    - Transfer: `ranged corpus reads: 641 GET(s), 167837696 byte(s)`
    - Outcome: Empty result (live-channel SCOTUS rows do not populate the `judges` column).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="AbbVie Fitch", fields=["caseName", "docketNumber", "court_id", "dateFiled", "status"])`
   - Outcome: Failed (`Rate limit exceeded: HTTP 429: Request was throttled. Rate limit exceeded: 1400/day.`).
2. `mcp_courtlistener_search(type="o", case_name="AbbVie Murrill", fields=["caseName", "docketNumber", "court_id", "dateFiled", "status"])`
   - Outcome: Failed (`Rate limit exceeded: HTTP 429: Request was throttled. Rate limit exceeded: 1400/day.`).
3. `mcp_courtlistener_search(type="r", court="scotus", q=""340B" OR "Fitch" OR "Murrill" OR "Hanaway"", fields=["caseName", "docketNumber", "dateFiled", "description"])`
   - Outcome: Failed (`Rate limit exceeded: HTTP 429: Request was throttled. Rate limit exceeded: 1400/day.`).

## 3. Web Searches

- None attempted.
