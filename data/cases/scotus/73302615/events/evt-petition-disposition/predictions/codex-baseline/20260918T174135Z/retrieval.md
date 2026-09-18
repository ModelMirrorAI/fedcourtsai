# Retrieval record

## Provisioned inputs

Read `record/snapshots/2026-09-18.json`, `record/context.json`, the event definition, `record/documents/documents.json`, `questions-presented.txt`, and relevant portions of `petition.txt` and `brief-in-opposition.txt`. No other predictor's output or realized outcome was read.

## Local reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-tooling, and agent-flags schemas.
- Ran `uv run fedcourts paths --court scotus --docket 73302615 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; rerunning with a writable temporary cache succeeded. The command explicitly withheld the outcome path.
- Read the committed `metrics/statpack.md` modern-cert, paid relist/CVSG, circuit, and sal-v4 per-Term band tables. Read `metrics/statpack.json` metadata and matching segment fields to compute the 2017–2024 elevated reached pool: weighted grants 484, weighted resolved 2,810. No live corpus query, `open-events` call, or opinion-body hydration occurred, so there is no ranged-corpus-transfer line to report.

## Web attempts

1. `web.run` search: `site.uscode.house.gov 22 USC 2370 e 2 act of state principles international law`. The tool returned no usable result; no statutory page was consulted from this attempt.
2. `web.run` open of the exact August 26, 2026 counsel-letter URL already linked in the snapshot. The tool returned no usable result.

## Successful dated-filing retrieval

Fetched this same, fixed Supreme Court filing with Python `urllib.request`, a 20-second timeout, and in-memory PDF extraction using `pypdf`; no downloaded file was written:

`https://www.supremecourt.gov/DocketPDF/25/25-1256/420189/20260826142321581_2026-08-26%20Letter%20re%20Withdrawal.pdf`

Read both pages. The August 26 letter says counsel was no longer authorized to represent PDVSA and did not know whether substitute counsel would appear. It concerns counsel's withdrawal, not the petition's disposition. It predates the provisioned September 18 snapshot, and materially informed the modest vehicle-risk adjustment. No linked political statements or other litigation were opened.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="Republic of Hungary v. Simon", filed_before="2026-05-01", num_results=3)`: returned the distinct February 3, 2021 decision, 592 U.S. 207, opinion 4657004. Its body was not read; it was not used as the 2025 authority.
2. `search(type="o", citation="604 U.S. 115", num_results=2)`: returned duplicate records of the February 21, 2025 Simon opinion, including official-report opinion 11243460 and slip opinion 10803824. No further result pages were requested.
3. `search_document(opinion_id=11243460, query="Hickenlooper", snippet_size=1800)`: retrieved passages about the Amendment, FSIA commercial nexus, and tracing. Used as general pre-existing legal context, not information about this petition's outcome. Citations to this litigation's older history in the precedent were not followed.

No search sought this petition's disposition, later history, or decision coverage. No outcome-revealing material for the target event was encountered.
