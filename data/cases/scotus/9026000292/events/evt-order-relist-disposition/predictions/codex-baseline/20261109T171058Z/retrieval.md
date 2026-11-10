# Retrieval record

## Provisioned and repository inputs

Read the prediction contract and schema, event definition, case-level context and November 9 snapshot, document manifest, questions presented, relevant petition and embedded appellate-opinion excerpts, appendix searches, related manifest and both Vide snapshots, and the same-question file. Consulted `metrics/statpack.md`, principally modern cert, circuit, relist, CVSG, and prior-Term sal-v8 reached-band tables. Also read tooling/flag schema material. No other prediction, evaluation, outcome file, or topic-label artifact was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000292 --event evt-order-relist-disposition --role predictor` — failed before execution because the default uv cache was read-only.
2. `uv run fedcourts query --help` — same cache failure.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000292 --event evt-order-relist-disposition --role predictor` — succeeded; path resolution only, no outcome opened.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — succeeded. Help was displayed again with `| cat`, and then with `COLUMNS=160` and `| head -52`; no corpus lookup in these help calls.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition granted --limit 3` — refused: era requires a decade token. No results or transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3` — returned Goldman Sachs Bank USA v. Brown, Scanlan v. Coalition for Open Democracy (an interim application), and Association for Education Fairness v. Montgomery County Board of Education. The combined command's displayed output was truncated; its transfer line was not retained in the visible excerpt. No transfer amount is inferred.
7. Repeated that exact grant query, piping stdout to `jq` for compact fields. Same three results. Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.
8. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 3` — compacted through `jq`; returned Westcott v. Voice of the Experienced, Momin v. Blanche, and Patel v. Government Employees Insurance Company, with distribution counts 2, 1, and 1. Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.

These structured recency examples were not treated as topical matches or a random base-rate sample. No `--full`, `open-events`, own-case query, or companion remote query was used.

## Web calls

1. Search pair: `site.ca11.uscourts.gov Stansell Revolutionary Armed Forces Colombia 2023 agency instrumentality time writ TRIA` and `site.ca9.uscourts.gov Bennett Islamic Republic Iran 2016 TRIA time agency instrumentality blocked assets`. Returned mostly unrelated historical cert-order material plus the already-staged Havlish petition. No own-case outcome surfaced; no result opened from this call.
2. Search pair: `site.media.ca11.uscourts.gov "Stansell" "2022" "1350"` and `site.ca9.uscourts.gov "Bennett" "2016" "963" "blocked"`. Results included unrelated TRIA materials and the pre-baseline Faiq filing described below. No own-case disposition was sought or surfaced.
3. Opened R1, the October 5, 2026 Faiq amicus opposing certiorari, a 29-page primary-source PDF; consulted its statement and arguments, especially pp. 8–20. This is an amicus counterargument, not a respondent's BIO or an outcome. Source: `https://www.supremecourt.gov/DocketPDF/26/26-292/428536/20261005173612123_Faiq%20cert%20op%20%20-%20final%20to%20printer.pdf`. citeturn575440view0

## CourtListener MCP calls

1. `search(type="o", citation="45 F.4th 1340", num_results=2, fields=["id","caseName","citation","dateFiled","absolute_url","snippet"])` — zero results. Did not independently verify the petition's cited Stansell III holding.
2. `search(type="o", q='"Stansell" "1350"', court="ca11", filed_after="2022-01-01", filed_before="2023-01-01", num_results=3, fields=["id","caseName","dateFiled","citation","snippet","absolute_url"])` — returned Keith Stansell v. Samark Jose Lopez Bello, 40 F.4th 1308; A.M. Samara v. Thomas Keith Taylor, 38 F.4th 141; and United States v. Julian Garcon, 54 F.4th 1274. Warned about unavailable requested fields. These were not the sought opinion; none was opened or used as substantive evidence.

## Validation

The required cell validation is run with the working cache override, `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000292/events/evt-order-relist-disposition/predictions/codex-baseline/20261109T171058Z`. It is local validation, not external retrieval.
