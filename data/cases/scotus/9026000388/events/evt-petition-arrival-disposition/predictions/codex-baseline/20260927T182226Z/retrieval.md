# Retrieval record

No retrieval sought this petition's disposition, subsequent history, or current docket. No corpus `query` or `open-events` call was made; consequently there are no ranged-corpus transfer lines.

## Local context beyond the provisioned case inputs

- Read the task contract and prediction, agent-flags, and agent-tooling schemas.
- Read `metrics/statpack.md`: modern cert disposition and circuit cuts, paid-segment relist/CVSG cuts, and sal-v4 segment table. Read `metrics/statpack.json` metadata/coverage and prior-Term baseline segment fields; pooled Terms 2017–2025 to obtain 638 / 12,720.
- `git log -1 --format='%cI %h' -- metrics/statpack.md` reported September 26, 2026 at 12:03:37 UTC, commit `96ebdd342`. This dates the committed artifact, not the underlying corpus refresh.
- `uv run fedcourts paths --court scotus --docket 9026000388 --event evt-petition-arrival-disposition --role predictor` initially failed because the default uv cache was read-only. Retried successfully with `uv run --no-sync --no-cache fedcourts paths --court scotus --docket 9026000388 --event evt-petition-arrival-disposition --role predictor`. This only resolved paths and did not read an outcome.

## External retrieval

1. Web search: `"Nahno-Lopez" "625 F.3d 1279"`. No usable result content was returned; nothing from it informed the forecast.
2. CourtListener `search(type="o", citation="625 F.3d 1279", num_results=2)`: returned *Nahno-Lopez v. Houser*, November 9, 2010, opinion 179008.
3. CourtListener `search_document(opinion_id=179008, query="We construe", snippet_size=1500)`: confirmed the federal common-law trespass claim and section 345 jurisdiction discussion.
4. CourtListener `search(type="o", citation="913 F.3d 959", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])`: returned *Davilla v. Enable Midstream Partners L.P.*, January 10, 2019, opinion 4357831.
5. CourtListener `search_document(opinion_id=4357831, query="unclear", snippet_size=1300)`: confirmed footnote 2's express uncertainty whether the circuit had formally recognized or merely assumed the cause of action.

These older opinions corroborated the existence and limitations of the asserted split. No outcome-revealing material about this petition surfaced.
