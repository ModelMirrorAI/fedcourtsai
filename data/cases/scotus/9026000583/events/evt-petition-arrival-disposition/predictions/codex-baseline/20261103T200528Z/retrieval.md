# Retrieval record

## Provisioned material

Read the event definition, `record/snapshots/2026-11-04.json`, `record/context.json`, and `record/same-question.json`. No filed documents or related snapshots were present. Read the prompt and output schemas. No other prediction or evaluation was consulted.

## Beyond the provisioned record

1. Read the modern cert, circuit, paid-segment relist/CVSG/amicus, and sal-v6 per-Term tables in `metrics/statpack.md`; inspected top-level keys of `metrics/statpack.json`. Used the frozen cert anchor and prior-Term baseline reached denominators. No case-membership measurement artifact was read.
2. Web search attempted: `"Shaikh" "Fox" "25-12004"`. The tool returned no readable result in this session; no factual conclusion rests on it.
3. Web open attempted: `https://media.ca11.uscourts.gov/opinions/pub/files/202512004.pdf`. The tool returned no readable content in this session. The opinion text used below instead came through CourtListener MCP.
4. CourtListener MCP `search(type="o", court="ca11", docket_number="25-12004", num_results=3)`: one matching opinion, Ahmed Shaikh v. Fox News Network, LLC, filed June 4, 2026, cluster 10870293, opinion 11337751. Match checked against the provisioned caption, lower docket, and judgment date. No Supreme Court disposition query.
5. CourtListener MCP `read_document(opinion_id=11337751)`: 18,486-character lower-court opinion; display truncated internally. Read the available caption, facts, and jurisdictional disposition.
6. `uv run --no-cache --no-sync fedcourts query --help`: read structured-filter interface before querying.
7. `uv run --no-cache --no-sync fedcourts query --court scotus --disposition denied --era roberts --decided-before 2026 --limit 3`: refused because `roberts` is not a permitted decade-era token. No corpus transfer line was emitted. Corrected the flag in the next query.
8. `uv run --no-cache --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`: returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. Chicago (25-1098), compact metadata, all denied October 19, 2026. The Term mask admitted prior-Term dockets, even though disposition dates fell in 2026; all preceded this November 3 forward forecast. No own-case outcome appeared. These denial-filtered examples were not used to estimate grant frequency or as substantive analogues.

   `ranged corpus reads: 13 GET(s), 3407872 byte(s)`

9. CourtListener MCP `read_document(opinion_id=11337751, chunk_index=[1,2], chunk_size=6000)`: additional lower-opinion jurisdiction analysis and preservation discussion; output again internally truncated.
10. CourtListener MCP `search_document(opinion_id=11337751, query="exceptions", snippet_size=1400)`: zero literal matches. No new information.

## Local tooling

The initial `uv run fedcourts paths --court scotus --docket 9026000583 --event evt-petition-arrival-disposition --role predictor` failed because uv's default cache directory was read-only. Retrying with `uv run --no-cache --no-sync fedcourts paths ...` succeeded without installation. Schema reads, output writes, and cell validation are local contract operations, not additional case retrieval. Validation uses the same cache/sync controls. No own-case disposition, subsequent history, or decision coverage was sought.
