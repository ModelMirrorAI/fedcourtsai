# Retrieval record

## Local material

- Read the provisioned event, October 5, 2026 snapshot, context, document manifest, questions presented, and selected substantive sections of the petition and opposition. No outcome or other predictor's output was read.
- Read `metrics/statpack.md`: modern discretionary-cert, originating-circuit, paid-segment relist/CVSG, and sal-v4 per-Term reached-band cuts. Read the corresponding `metrics/statpack.json` and calculated the state reached pool for 2017–2025 as 99/419. No corpus `query` or `open-events` call was made; there are no ranged-corpus transfer lines to report.
- Consulted the task instructions, output schemas, path helper and serialization helper for the output contract. Ran `uv run fedcourts paths --court scotus --docket 9026000018 --event evt-petition-disposition --role predictor`. Its first invocation failed because the default cache location was read-only; retrying with a writable temporary cache succeeded. Validation is an output check, not substantive retrieval.

## External calls

1. Web search: `site.supremecourt.gov opinions 2010 Turner Rogers 564 431 capable repetition evading review`. The tool returned no visible result content; no substantive information was obtained.
2. Web open: official Supreme Court opinion path `/opinions/10pdf/10-10.pdf`. The tool returned no visible document content; no substantive information was obtained.
3. CourtListener MCP `search(type="o", citation="564 U.S. 431", num_results=1)`. Returned an unrelated City of Concord petition-denial result dated November 30, 2015. Disregarded; this was not the target petition and did not inform the forecast.
4. CourtListener MCP `search(type="o", case_name="Turner v. Rogers", court="scotus", filed_after="2011-06-01", filed_before="2011-07-01", num_results=2)`. Located the June 20, 2011 opinion, 564 U.S. 431, including majority-opinion id 9441801.
5. CourtListener MCP `search_document(opinion_id=9441801, query="too short", snippet_size=1800)`. Read the mootness discussion at 439–440 confirming the separate duration and recurrence requirements and its treatment of the 12-month imprisonment period. Used as general precedent only.

No search targeted this case's Supreme Court disposition, subsequent history, or coverage. No target-case outcome surfaced.
