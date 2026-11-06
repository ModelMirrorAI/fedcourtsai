# Retrieval record

## Provisioned evidence and local reference material

- Read the case-level November 5, 2026 snapshot, `context.json`, `documents/documents.json`, `documents/questions-presented.txt`, relevant portions of `documents/petition.txt`, Appendix A-C in `documents/appendix.txt`, and `same-question.json`. The appendix is marked truncated. Read the target `event.yaml`. Did not read this event's outcome, another prediction, an evaluation, or topic-labeling artifacts.
- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the tooling and flags schemas, and relevant sections of `metrics/statpack.md`: modern cert, relists, CVSG, amici, originating courts, and the sal-v7 per-Term band table. Used the frozen 5.15% cert anchor rather than current-Term outcomes. Inspected `src/fedcourtsai/pipeline/claims.py` and `src/fedcourtsai/pipeline/justices.py` for claim-label and roster spelling only.
- `uv run fedcourts paths --court scotus --docket 9026000218 --event evt-petition-disposition --role predictor` initially failed because the default uv cache path was read-only. The same command prefixed with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. No packages were installed. All subsequent CLI calls used that cache override.
- Read `uv run fedcourts query --help` before the first query; reread its opening options while selecting filters. These help and path calls are tooling discovery, not substantive prior retrieval.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '577 U.S. 385' --limit 3`

   No rows returned. The coverage warning said only 200 SCOTUS rows in scope carry reporter citations, that these are each case's own citations rather than a citing-case index, and that an empty result is more likely an unfilled column than proof a precedent does not exist. Followed its suggestion to use CourtListener for the identified precedent; did not repeat the sparse citation lookup.

   Exact transfer line:

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition summary-reversal --limit 3`

   Completed successfully but returned no prior rows. This unexpectedly required a broad scan. No inference about the substantive availability of summary reversal rests on the empty result; Wearry supplies a directly retrieved example. No additional corpus scans were attempted.

   Exact transfer line:

   `ranged corpus reads: 994 GET(s), 260374528 byte(s)`

`DECIDED_BEFORE` was unset, and the frozen context identifies a forward cell with no replay clock. Neither query targeted this petition or its disposition.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="Wearry v. Cain", num_results=3)` returned one result: *Wearry v. Cain*, 577 U.S. 385, decided March 7, 2016; cluster 3183098, opinion 3183080, docket 14-10008. This is an older Louisiana Brady precedent, not Matthews's case.
2. `read_document(opinion_id=3183080, chunk_index=[0,1], chunk_size=10000)` returned the opening two HTML-text chunks of an eight-chunk opinion. Used the opening statement of reversal and the materiality discussion that the new evidence must undermine confidence in the verdict, without requiring a showing that acquittal was more likely than not. Did not claim to have read the full opinion or its entire separate writing. No live docket search or REST fallback was used.

## Web attempts

1. A single web search call attempted both queries: `site.supremecourt.gov opinions Wearry Cain Brady materiality 2016` and `site.supremecourt.gov opinions Turner United States Brady 2017 materiality`. The tool returned no visible results or content. No factual conclusion rests on these searches.
2. A web open attempted `https://www.supremecourt.gov/opinions/15pdf/14-10008_aplc.pdf`. The tool returned no visible content; the attempted filename was not verified and supplied no evidence. The later CourtListener result identified a different download filename. No further web calls were attempted.

No case-specific web query, current Supreme Court docket retrieval, or search for this petition's disposition was made. No outcome-revealing material about this event was encountered. The forecast rests on the provisioned record, committed statistical context and the identified older precedent.
