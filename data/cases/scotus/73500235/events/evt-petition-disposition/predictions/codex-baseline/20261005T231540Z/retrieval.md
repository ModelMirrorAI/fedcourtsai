# Retrieval log

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-10-05.json`, and the provisioned document manifest, questions presented, petition, and brief in opposition. Read the task instructions and output schemas. The reply's docket entry was visible, but no reply text was retrieved.

## Committed base-rate material

Read `metrics/statpack.md`: modern-cert disposition, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Inspected only the top-level key names of `metrics/statpack.json` while checking for pack dating metadata. Calculated an approximate 17.24% pooled elevated reached rate from all displayed eligible rows, Terms 2017–2024, weighted denominator 2,810. This is a local committed artifact, not a live corpus query.

## CourtListener MCP

1. `search(type="o", citation="67 M.J. 224", num_results=2)` returned United States v. Dean, decided March 12, 2009, cluster 800346. This lookup concerned a historical precedent, not the target petition.
2. `read_document(opinion_id=9500279)` retrieved Dean's majority opinion; the large response was partly truncated in display.
3. `search_document(opinion_id=9500279, query="several of the promises", snippet_size=1600)` retrieved the focused passage at 67 M.J. 227–28 identifying acts of performance, including the factual stipulation and amended witness list. This supplied the passage used in the rationale.

No target-case CourtListener search, docket lookup, later-history lookup, or related-case outcome lookup was performed.

## Web attempts

- Searched `site.supremecourt.gov Rule 10 considerations governing review certiorari judicial proceedings` for general certiorari criteria. The tool returned no usable content.
- Attempted to open the official Court's `filingandrules/2023RulesoftheCourt.pdf`. The tool again returned no usable content. No proposition in the forecast rests on either attempt.

## Local tooling

`uv run fedcourts paths --court scotus --docket 73500235 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Re-running with the uv cache located under `/tmp` succeeded. This command resolves local paths and retrieves no case evidence. No `fedcourts query` or `open-events` call was made, so no ranged-corpus transfer line exists for this run. No corpus blob was read or refreshed. Validation is a local contract check, not substantive retrieval.

No outcome-revealing material was encountered.
