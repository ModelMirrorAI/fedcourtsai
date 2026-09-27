# Retrieval record

## Provisioned case inputs

Read the event definition and case-level `record/context.json`, `record/snapshots/2026-09-17.json`, `record/documents/documents.json`, `questions-presented.txt`, and relevant sections of `petition.txt`. No target-case outcome or subsequent docket was sought.

## Committed base-rate context

Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table. Read corresponding baseline prefix rates and weighted denominators from `metrics/statpack.json`; pooled displayed prior Terms 2017–2025 to 638 / 12,720 = 0.05015723270440252. No remote corpus lookup, `fedcourts query`, or `open-events` call was made; no ranged-corpus transfer line was emitted.

## General legal context

1. Web search batch: `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.uscourts.gov Court Federal Claims jurisdiction money mandating United States Testan 424 392`. No usable tool content returned; nothing from these searches supported the forecast.
2. CourtListener MCP `search(type="o", citation="424 U.S. 392", num_results=1, fields=["id", "caseName", "dateFiled", "citation", "absolute_url", "opinions"])`. Returned Brantley v. Republic Mortgage Insurance Company, 424 F.3d 392, not Testan. Discarded; not used as legal evidence.
3. CourtListener MCP `search(type="o", court="scotus", case_name="United States v. Testan", num_results=2, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`. Located the 424 U.S. 392 opinion, opinion id 109386, and a separate costs order. Only the substantive opinion was used. The search metadata lists May 3, 1976, while the opinion's header states March 2, 1976; the reasoning cites the year and reporter rather than treating the costs-order date as the merits date.
4. Web open attempt: Cornell's Supreme Court Rule 10 page. No usable tool content returned; no assertion relies on that attempted read.
5. CourtListener MCP `search_document(opinion_id=109386, query="money", snippet_size=450)`. Consulted passages concerning the Court of Claims' limited jurisdiction, equitable relief, and the need for an independently money-mandating substantive basis, principally 424 U.S. at 398–402. No target-case facts were retrieved.

## Local contract and tooling checks

Read the task instructions and prediction, flags, and tooling schemas, and inspected serialization/path helpers for output handling. Ran `uv run fedcourts paths --court scotus --docket 9026000351 --event evt-petition-arrival-disposition --role predictor`; the first attempt failed because the default uv cache was read-only, and the retry with a temporary cache succeeded. These are not corpus evidence lookups. Validation is a schema/integrity check, not a source of case-outcome evidence.
