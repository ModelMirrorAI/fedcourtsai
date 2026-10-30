# Retrieval Log

1. **Corpus CLI — Path resolution (`fedcourts paths`):**
   - Command: `uv run fedcourts paths --court scotus --docket 73272491 --event evt-order-call-for-response-disposition --role predictor`
   - Result: Resolved `case_id = scotus/73272491`, `corpus = corpus/corpus.db`, `event = data/cases/scotus/73272491/events/evt-order-call-for-response-disposition/event.yaml`.

2. **Corpus CLI — Help lookups:**
   - Commands:
     - `uv run fedcourts query --help`
     - `uv run fedcourts same-question-list --help` (returned exit code 2: no such command, suggested `same-question-lists`)
     - `uv run fedcourts same-question-lists --help`

3. **CourtListener MCP — Opinion search:**
   - Tool: `mcp_courtlistener_search(q='"Libretti" "Southern Union" forfeiture Apprendi', type='o')`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 1829 seconds.`).

4. **Corpus CLI — Citation query (`fedcourts query`):**
   - Command: `uv run fedcourts query --court scotus --citation "146 S. Ct. 564" --citation "146 S. Ct. 875" --citation "145 S. Ct. 518" --citation "602 U.S. 821" --limit 10`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (note printed that only 200 rows in `scotus` scope carry reporter citations).

5. **Corpus CLI — Prior petition lookup by docket number (`fedcourts query`):**
   - Command: `uv run fedcourts query --court scotus --docket-number "23-95" --limit 5`
   - Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 1 row: `scotus/72483418` (*Philip Esformes v. United States*, No. 23-95, filed `2023-08-02`, cert denied `2023-12-11` at `distribution_count = 1`, `response_requested = null`).

6. **Corpus CLI — Originating panel judge query (`fedcourts query`):**
   - Command: `uv run fedcourts query --court scotus --judge "Kearse" --judge "Jacobs" --judge "Kahn" --decided-before 2025 --limit 5`
   - Stderr: `ranged corpus reads: 639 GET(s), 167510016 byte(s)`
   - Result: 0 rows returned (SCOTUS rows do not populate lower-court panel judges in `judges`).
