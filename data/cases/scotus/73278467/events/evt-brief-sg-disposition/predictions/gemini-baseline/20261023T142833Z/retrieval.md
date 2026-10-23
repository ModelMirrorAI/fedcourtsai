# Retrieval Log — `scotus/73278467` (`evt-brief-sg-disposition`)

## 1. Corpus CLI Lookups (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 73278467 --event evt-brief-sg-disposition --role predictor`
  - Resolved case, corpus, and event paths (no ranged corpus read transfer).
- `uv run fedcourts query --court scotus --disposition gvr --limit 10`
  - Transfer log: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
  - Consulted recent SCOTUS GVR dispositions in the corpus to inspect how GVR outcomes and distribution counts are recorded.

## 2. CourtListener MCP Lookups

- `mcp_courtlistener_search` (`type="o"`, `court="ca10"`, `case_name="Fowler v. Stitt"`, `num_results=5`, `fields=["caseName", "dateFiled", "citation", "docketNumber", "status"]`)
  - Checked whether the Tenth Circuit had issued a new published opinion on remand in *Fowler v. Stitt* (No. 23-5080); only the original June 18, 2024 opinion (`104 F.4th 770`) appeared in the index.

## 3. Web Searches

- None.
