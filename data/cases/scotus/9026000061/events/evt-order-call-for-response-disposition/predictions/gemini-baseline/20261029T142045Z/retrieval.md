# Retrieval Log

## 1. Corpus Tooling (`uv run fedcourts`)

1. **Path resolution:**
   - Command: `uv run fedcourts paths --court "scotus" --docket "9026000061" --event "evt-order-call-for-response-disposition" --role predictor`
   - Result: Resolved `case_id` (`scotus/9026000061`), `corpus` (`corpus/corpus.db`), and `event` path. No ranged corpus reads.

2. **Corpus query — recent 2020s SCOTUS cert denials:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 5 resolved 2020s SCOTUS denial priors (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`).

3. **Corpus query — recent 2020s SCOTUS cert grants:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   - Result: Returned 5 resolved 2020s SCOTUS grant priors (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`), including cert petitions with multiple distributions and higher salience scores (`scotus/9026000012`, `scotus/9026000204`, `scotus/73281386`).

4. **Corpus query — attempted unsupported flag (`--originating-court`):**
   - Command: `uv run fedcourts query --court scotus --originating-court ca9 --era 2020s --disposition denied --limit 5`
   - Result: Exit code 2 (`No such option: --originating-court`); no corpus reads executed.

## 2. CourtListener MCP Calls

1. **Opinion search for *Sedlik v. Von Drachenberg* (9th Cir.):**
   - Tool: `mcp_courtlistener_search`
   - Arguments: `{"case_name": "Sedlik v. Von Drachenberg", "court": "ca9", "fields": ["caseName", "dateFiled", "citation", "docketNumber", "status"], "num_results": 5, "type": "o"}`
   - Result: Failed with upstream rate-limit error (`HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 11828 seconds.'}`). Degraded gracefully to the provisioned case documents and corpus priors.

## 3. Web Searches

- None attempted.
