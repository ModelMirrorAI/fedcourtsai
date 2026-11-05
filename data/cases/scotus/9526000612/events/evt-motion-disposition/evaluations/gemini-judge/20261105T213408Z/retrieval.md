# Retrieval Log — `gemini-judge` (`20261105T213408Z`)

## 1. Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000612" --event "evt-motion-disposition" --role evaluator`
   - Output: resolved `case_id`, `corpus`, `event`, and `outcome` paths (no corpus reads).
2. `uv run fedcourts query --court scotus --docket-number 26A612`
   - Transfer: `ranged corpus reads: 15 GET(s), 3801088 byte(s)`
   - Purpose: Verified corpus row metadata for `scotus/9526000612` (`26A612`, `application_kind: "substantive"`, `originating_court: "cadc"`, `originating_docket_number: "26-5131"`, `disposition: "denied"`, `interim_reading: "denied"`).

## 2. CourtListener MCP Lookups

1. `courtlistener.call_endpoint` (`endpoint_id: "docket-entries"`, `query: {"docket": 73235695, "fields": ["id", "date_filed", "entry_number", "description"]}`)
   - Purpose: Verified the docket entry dates on D.C. Circuit No. `26-5131` (`docket_id: 73235695`, entries from April 23, 2026 through October 19, 2026) cited by `gemini-baseline`.
2. `courtlistener.read_document` (`recap_document_id: 496946683`)
   - Purpose: Verified the October 9, 2026 emergency mandamus petition in D.C. Circuit No. `26-1285` cited by `gemini-baseline` in its lower-court procedural reconstruction.

## 3. Web Searches

- None.
