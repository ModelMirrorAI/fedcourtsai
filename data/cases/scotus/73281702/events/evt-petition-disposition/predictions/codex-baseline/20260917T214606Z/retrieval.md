# Retrieval record

## Provisioned inputs

- Read the event definition and case-level `record/context.json` and `record/snapshots/2026-09-17.json`.
- Read `record/documents/documents.json`, `questions-presented.txt`, the petition's argument and relevant lower-opinion appendix excerpts, and relevant BIO portions.
- Read the prediction contract and artifact schemas. Ran `fedcourts paths --court scotus --docket 73281702 --event evt-petition-disposition --role predictor` to resolve paths; did not open any outcome file.

## Beyond the provisioned inputs

1. Read committed `metrics/statpack.md`: modern-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Inspected corresponding `metrics/statpack.json` Term segments. Used jq to pool the elevated bracketed-reached risk set over displayed Terms 2017–2024, obtaining 484 estimated grants / 2,810 weighted resolutions = 0.1722419929. No remote corpus query was made; no ranged-corpus transfer line was emitted.
2. Web search query: `Richardson United States 526 U.S. 813 821 child abuse statutes unanimity opinion`. The tool returned no usable content or source reference.
3. Web open attempt for the Justia Richardson opinion page, path `/cases/federal/us/526/813/`. The tool returned no usable content or source reference.
4. CourtListener MCP `search(type="o", citation="526 U.S. 813", num_results=1)`: identified Richardson v. United States, decided June 1, 1999, opinion 118295. This was a precedent lookup, not a search for the target petition.
5. CourtListener MCP `search_document(opinion_id=118295, query="sexual", snippet_size=2300)`: located the majority's discussion of state continuous-abuse laws and related dissent passages.
6. CourtListener MCP `read_document(opinion_id=118295, chunk_index=[3,4], chunk_size=5000)`: read the majority's discussion around reporter pages 820–23, including the special-proof-difficulties and pre-incorporation language.
7. Retrieved only the September 15, 2026 reply PDF identified in the provisioned snapshot, from the Supreme Court's official document server. Used Python urllib and pypdf entirely in memory, without saving a downloaded document. Source identifier:

   `https://www.supremecourt.gov/DocketPDF/25/25-1195/424387/20260915164932677_25-1195%20Reply%20Brief.pdf`

   The PDF contained 13 pages. First extraction requested PDF pages 4–13; console truncation omitted part of the middle. A second fetch/extraction read PDF pages 7–10 to recover those passages. The substantive reply, printed pp. 1–8, informed the forecast. No link to a later docket or disposition was followed.

## Boundaries and tooling

- Forward mode; snapshot cutoff and decided-before clock are null. Retrieved case-specific material was an already-filed reply listed in the baseline.
- No outcome, other predictor output, current docket, or subsequent-history material was sought or received.
- No `fedcourts query` or `open-events` call; no ranged-corpus reads to report.
- Initial `uv run fedcourts paths` failed because the default uv cache was read-only. Repeating with a writable temporary cache succeeded. This was a local environment issue, not a missing case record.
