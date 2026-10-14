# Retrieval log

## Provisioned evidence

Read the cell's event.yaml, record/context.json, record/snapshots/2026-10-13.json, document manifest, questions-presented.txt, and relevant substantive sections of petition.txt, brief-in-opposition.txt, and cert-reply.txt. The petition reading included retained portions of the appended First Circuit opinion. No outcome file, other predictor output, or labeling-measurement artifact was read.

## Local context beyond the provisioned case inputs

- Read the task instructions, prediction and feedback schemas, and path/serialization helpers to implement the output contract.
- Read metrics/statpack.md: modern discretionary-cert scope, originating-circuit context, paid-segment relist and CVSG cuts, and sal-v4 band table. Used metrics/statpack.json to compute the high-band reached rate over displayed Terms 2017-2024: 314 weighted grants / 898 weighted resolved petitions. The pack has no build timestamp; I do not represent it as a fresh live-corpus extraction.
- Ran `uv run fedcourts paths --court scotus --docket 73514289 --event evt-petition-disposition --role predictor`. The first attempt failed because the default cache directory was read-only; rerunning with a writable temporary cache succeeded. This is path resolution, not a corpus lookup.
- No `fedcourts query` or `fedcourts open-events` call was made. There is therefore no ranged corpus reads transfer line.

## Web attempts: general precedent only

1. Searched `site.supremecourt.gov opinions Davis Monroe 526 U.S. 629 clearly unreasonable harassment`. No usable result content was returned.
2. Attempted to open the Library of Congress U.S. Reports PDF for Davis at `https://tile.loc.gov/storage-services/service/ll/usrep/usrep526/usrep526629/usrep526629.pdf`. No usable content was returned. No inference rests on either web attempt.

## CourtListener MCP: general precedent only

1. `search(type="o", citation="526 U.S. 629", num_results=1)` returned an unrelated 2008 district-court case, Thomas M. Gilbert Architects, PC v. Accent Builders and Developers, LLC. It was disregarded; its full opinion was not retrieved.
2. `search(type="o", court="scotus", case_name="Davis v. Monroe", filed_before="2000-01-01", num_results=2, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])` located Davis, 526 U.S. 629, decided May 24, 1999, with lead opinion ID 9433803. The search also surfaced a January 11, 1999 procedural order in Davis, not in the forecast case; that order was not used.
3. `search_document(opinion_id=9433803, query="clearly unreasonable", snippet_size=850)` returned four snippets. Used the majority's discussion at 648-649 concerning the contextual deliberate-indifference standard, dismissal-stage resolution, and limits on judicial second-guessing of school discipline.

No search sought this petition's disposition, subsequent history, or decision coverage. No outcome-revealing material about this petition surfaced.
