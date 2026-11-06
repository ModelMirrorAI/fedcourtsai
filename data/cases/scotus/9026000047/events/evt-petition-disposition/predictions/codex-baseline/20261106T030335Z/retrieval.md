# Retrieval record

## Local inputs and base rates

Read the prediction contract and output schemas; this event's event.yaml; the case-level November 6, 2026 snapshot; context.json; documents.json; questions-presented.txt; petition.txt; appendix.txt; and same-question.json. Consulted metrics/statpack.md, specifically modern discretionary-cert dispositions, originating-court scope, paid-segment relist/CVSG/amicus cuts, and the sal-v7 per-Term reached table. These are aggregate priors, not another cell's forecast. No corpus query or open-events request was made, so there is no ranged-corpus-read transfer line.

`uv run fedcourts paths --court scotus --docket 9026000047 --event evt-petition-disposition --role predictor` was attempted twice without a cache override and failed with a read-only uv cache error. The successful retry used `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` and returned this case, the corpus path, and this event path. No evaluator-only file was read. Local shell inspection was limited to instructions, schemas, aggregate statistics, provisioned case records, and cell validation; it did not read predictions or evaluations from another cell.

## Web attempts

1. `web.run` search: `site.supremecourt.gov "Flowers Foods" "Brock" "2026"`. The tool returned no usable results or source text.
2. `web.run` searches in one call: `"Flowers Foods" "Brock" Supreme Court opinion` and `site.supremecourt.gov "Bissonnette" "601" "246"`. The tool returned no usable results or source text.
3. `web.run` open attempt for the unverified candidate official opinion path `https://www.supremecourt.gov/opinions/25pdf/608us2r37_i425.pdf`. No usable content was returned; the guessed path supplied no evidence and was not relied upon.

These attempts concerned precedents, not this petition's disposition. No search for Amazon v. Clinton's outcome or subsequent history was made.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="Flowers Foods v. Brock", num_results=3)`: one result, Flowers Foods, Inc. v. Brock, cluster 10865526, opinion 11332974, docket 24-935, decided May 28, 2026, authored by Gorsuch. This is the intervening precedent, not the target petition.
2. `read_document(opinion_id=11332974)`: fetched the combined Supreme Court opinion, 29,837 characters. Used its holding, affirmance, and final discussion reserving other limits on the exemption. The response displayed the opening and concluding portions with an intervening truncation; I do not claim to have read the omitted middle from that response.
3. `search_document(opinion_id=11332974, query="unanimous", snippet_size=300)`: one match identifying Gorsuch's opinion for a unanimous Court.

The CourtListener primary opinion, rather than the unsuccessful official-site attempts, independently verifies the legal context. No retrieved material revealed the disposition of No. 26-47.

## Validation

Validate this cell with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000047/events/evt-petition-disposition/predictions/codex-baseline/20261106T030335Z`. The cache override only resolves a filesystem permission issue; it changes neither the inputs nor the prediction.
