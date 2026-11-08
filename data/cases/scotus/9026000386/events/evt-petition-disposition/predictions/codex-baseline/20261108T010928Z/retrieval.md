# Retrieval record

## Provisioned and repository inputs

Consulted the prediction contract, prediction/tooling/flags schemas, event definition, `record/snapshots/2026-11-08.json`, `record/context.json`, document manifest, questions presented, petition, appendix, lower-court docket summary, and the modern-cert, originating-circuit, paid relist/CVSG/amicus, and prior-Term salience-band portions of `metrics/statpack.md`. No outcome, other-cell output, or topic-label artifact was read.

## Corpus and command attempts

Commands below ran from the repository root. The cache override uses the provisioned environment, without installing packages.

1. `uv run fedcourts paths --court scotus --docket 9026000386 --event evt-petition-disposition --role predictor` failed before retrieval because the default uv cache was read-only.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000386 --event evt-petition-disposition --role predictor` succeeded, resolving the case and event paths. The evaluator-only path was not opened. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded; read the structured-filter help. No transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 3` returned three unrelated substantive applications: Guardado v. Florida (26A623), Guardado v. Comerford (26A634), and Lopez Jaime v. Blanche (26A637). These are not cert comparators and were not used to estimate a grant rate. This combined command's displayed output was truncated, so its initial transfer line was not retained in the visible output. The same query was repeated below to obtain a visible transfer report; I do not infer the first call's transfer count.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3` returned Google v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and O'Donnell v. Chicago (25-1098), all denied, with decision dates masked by the optional prior-Term clock. These were generic contextual examples, not matched unemployment precedents. No full opinion was requested.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

6. Repeated `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 3`, piping results through `jq` for compact display. Returned the same three unrelated applications as item 4; not relied upon substantively.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

## Web attempts

1. `web.search_query`: `site.supremecourt.gov "Rule 10" "misapplication" "certiorari"`. Returned no visible results or usable source text.
2. `web.open`: the Supreme Court's official `filingandrules/rules_guidance.aspx` page. Returned no visible source content.
3. Repeated the same `web.open` once. Again returned no visible source content.

These attempted general procedural verification, not this petition's disposition. No web material was used as evidence, and no own-case outcome surfaced. No CourtListener MCP call was made; the provisioned appendix already contains the matching appellate decision. No live docket refresh was attempted.
