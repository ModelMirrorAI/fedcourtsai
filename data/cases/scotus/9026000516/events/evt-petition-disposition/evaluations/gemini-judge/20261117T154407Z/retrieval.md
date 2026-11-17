# Retrieval Log — `gemini-judge` (`20261117T154407Z`)

## 1. Historical Statpack Reconstructions (`uv run fedcourts statpack-at`)
1. `uv run fedcourts statpack-at data/cases/scotus/9026000516/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` (and identical checks for `codex-baseline` and `claude-baseline`, plus extraction to `/home/runner/.gemini/tmp/fedcourtsai/statpack-at/gemini-baseline` for local inspection)
   - Resolved all three candidates' prediction-time statpack build to `build_sha: dedb32b153e67d254af10083c3ee247cecd56116` (`digest: sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, landed `2026-10-31T10:28:26-04:00`).

## 2. Corpus Queries (`uv run fedcourts`)
1. `uv run fedcourts paths --court "scotus" --docket "9026000516" --event "evt-petition-disposition" --role evaluator`
   - Verified cell paths (`case_id scotus/9026000516`).
2. `uv run fedcourts query --court scotus --docket-number 25-7462`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified `claude-baseline`'s cited comparator *Lamor Whitehead v. United States* (`scotus/73393227`, `disposition: "gvr"`, `date_cert_granted: "2026-10-05"`).
3. `uv run fedcourts query --court scotus --docket-number 26-5216`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified `claude-baseline`'s cited comparator *Brian Hobson v. United States* (`scotus/9026005216`, `disposition: "gvr"`, `date_cert_granted: "2026-10-13"`, `distribution_count: 1`).

## 3. CourtListener MCP Calls
1. `mcp_courtlistener_read_document(opinion_id=11343328, chunk_index=[0, 1, 2], chunk_size=10000)` and `mcp_courtlistener_read_document(opinion_id=11343328, chunk_index=3, chunk_size=10000)`
   - Read the Supreme Court's opinion in *Abouammo v. United States*, 608 U.S. 597 (2026), to verify the candidates' doctrinal characterizations of 18 U.S.C. § 1519 and criminal venue principles.

## 4. Web Searches
- None.
