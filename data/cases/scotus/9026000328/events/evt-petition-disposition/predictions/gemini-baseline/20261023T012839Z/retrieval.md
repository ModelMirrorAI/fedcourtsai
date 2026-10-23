# Retrieval Log

## Corpus Lookups (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000328 --event evt-petition-disposition --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --docket-number 26-159 --include-open --full`
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Retrieved corpus record for related petition *Peter Protopapas v. Whittaker Clark & Daniels, Inc., et al.* (No. 26-159).
3. `uv run fedcourts query --court scotus --docket-number 26-263 --include-open --full`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Retrieved corpus record for related petition *Official Committee of Talc Claimants v. Whittaker, Clark & Daniels Inc, et al.* (No. 26-263).
4. `uv run fedcourts query --court scotus --docket-number 25-213 --include-open --full`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Retrieved corpus record for prior related South Carolina receivership petition *Atlas Turner, Inc. v. Donna B. Welch, et al.* (No. 25-213, cert. denied Jan. 12, 2026).
5. `uv run fedcourts query --court scotus --docket-number 26-350 --include-open --full`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Retrieved corpus record for companion vide petition *Altrad Investment Authority S.A.S, et al. v. Cape Intermediate Holdings Limited, et al.* (No. 26-350).

*(Note: Three initial `uv run fedcourts query` invocations with positional strings `"Whittaker Clark"`, `"Atlas Turner"`, and `"Protopapas"` exited with usage errors before switching to `--docket-number` flags; they performed no corpus reads.)*

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca3", case_name="Whittaker Clark & Daniels", fields=["caseName", "dateFiled", "citation", "cluster_id", "docketNumber"])`
   - Returned HTTP 429 (`Rate limit exceeded: 300/hour`). Degraded gracefully to the provisioned inputs and local corpus tools.

## Web Searches

- None.
