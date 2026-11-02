# Retrieval record

## Provisioned inputs and local references

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the tooling and flags schemas, and the cell's event definition. Consulted case-level `record/snapshots/2026-11-02.json`, `record/context.json`, `record/documents/documents.json`, `questions-presented.txt`, the petition and embedded appendix, BIO, reply, and `record/same-question.json`. Consulted `metrics/statpack.md` for the prior-Term sal-v6 table and paid-segment relist, CVSG, amicus, and circuit cuts; inspected the top-level statpack JSON keys. No other prediction, evaluation, realized-outcome file, or topic-label artifact was read.

## CLI attempts

All successful uv invocations used `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` after the initial default-cache permission error. No package was installed.

- `uv run fedcourts paths --court scotus --docket 9026000210 --event evt-petition-disposition --role predictor`: initial attempt failed because `/home/codexcell/.cache/uv` was read-only; retry with the temporary cache succeeded and resolved this event's paths.
- `uv run fedcourts query --help`: initial attempt failed for the same cache reason. Successful retry read the structured filters. A further display with `COLUMNS=180` piped through `head -80` widened the help text. None of these help/path calls reported corpus transfer.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 5`: executed twice, with the second result reduced using jq. Both returned DOGE Service, Berry, Blanche v. Ozurumba, Missionaries of Saint John the Baptist, and Marschner. The first combined terminal display was truncated, so its transfer line was not retained in the visible excerpt; the repeat reported exactly `ranged corpus reads: 0 GET(s), 0 byte(s)`.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`: executed twice, with results reduced using jq. Returned DOGE Service, Berry, and Blanche v. Ozurumba, with stored distribution counts 2, 5, and 2. The first combined display was truncated; the second visibly reported exactly `ranged corpus reads: 0 GET(s), 0 byte(s)`.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`: returned Google v. VirtaMove, Hastings College Conservation Committee, and O'Donnell v. Chicago, with distribution counts 2, 2, and 4. Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`.
- `uv run fedcourts query --court scotus --citation '524 U.S. 569' --decided-before 2026 --limit 3`: no matching rows. Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`. The CLI cautioned that only 200 scoped rows carried reporter citations, and recommended MCP for a known-case lookup.

The bare-year filter is a Term/year bar, not a resolution-date bar: returned Term-2025 petitions included October 2026 grant or denial dates. They were already resolved before this forward cell's November 2 date. The samples were outcome-selected context, not empirical estimates or close substantive comparators. None was this docket.

## CourtListener MCP

1. `search(type="o", citation="524 U.S. 569", num_results=3)` returned National Endowment for the Arts v. Finley, decided June 25, 1998, cluster 118240, lead opinion 9433701 and combined opinion 118240.
2. `search_document(opinion_id=9433701, query="different case", snippet_size=1700)` returned no literal match.
3. `search_document(opinion_id=118240, query="different case", snippet_size=1600)` returned the majority's discussion at 586–587 reserving as-applied discriminatory-funding challenges. Used to check that summary reversal is not compelled by an uncomplicated holding. Source: `https://www.courtlistener.com/opinion/118240/national-endowment-for-the-arts-v-finley/`.

## Web calls

- Search: `site.supremecourt.gov "National Endowment for the Arts v. Finley" "Rust"`. The query's malformed site operator returned general precedent pages and some filing references, including this already-provisioned petition. No own-case disposition or post-decision history surfaced. Did not rely on secondary analyses or filing search snippets.
- Search: `site:loc.gov "524 U.S. 569" Finley`. Located the Library of Congress official U.S. Reports opinion and PDF: `https://www.loc.gov/item/usrep524569/` and `https://tile.loc.gov/storage-services/service/ll/usrep/usrep524/usrep524569/usrep524569.pdf`.
- Opened `https://www.loc.gov/item/usrep524569/`; confirmed the primary-source identity, June 25, 1998 date, and official reporter citation. The operative passage was read using MCP, not reconstructed from a search snippet.

No live docket fetch, lower-court subsequent-history search, or own-case outcome search was attempted. General precedent research did not change the forecast into a merits adjudication.

## Validation

Ran `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts validate data`. It exited successfully: `OK: 29781 artifact(s) valid, 71090 reference(s) consistent`.
