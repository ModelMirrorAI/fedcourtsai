# Retrieval record

## Local inputs and reference material

Read the prediction contract, prediction and tooling schemas, the event definition, provisioned snapshot and context, document manifest, questions presented, and petition argument and relevant bound-appendix passages. Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid-segment relist/CVSG/amicus cuts, and sal-v8 prior-Term reached-band rates. Did not read outcome files, other prediction or evaluation trees, or `data/qp-topics/`.

## CLI attempts and corpus lookup

1. `uv run fedcourts paths --court scotus --docket 9026000518 --event evt-order-call-for-response-disposition --role predictor` — failed before execution because the default uv cache was read-only. No corpus transfer line.
2. `uv run fedcourts query --help` — same cache failure. No corpus transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000518 --event evt-order-call-for-response-disposition --role predictor` — succeeded; confirmed case/event paths and indicated the outcome is evaluator-only. No outcome read and no corpus transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — succeeded; read the structured-filter interface. No corpus transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help | sed -n '85,150p'` — reviewed clock, limit, and hydration options. No corpus transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era roberts --disposition denied --decided-before 2026 --limit 3` — refused: era values are decades, not chief-justice names. The error supplied the vocabulary; no corpus transfer line.
7. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3` — succeeded.

   `ranged corpus reads: 5 GET(s), 1310720 byte(s)`

   Returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce, Warden (25-7555), each denied November 9, 2026, with no opinion body. The bare-year filter uses docket/derived year rather than a strict resolution-date cutoff; these are Term-2025 dockets, not outcomes strictly before calendar 2026. This forward cell permits them, but their subject matter and fee-class mix do not establish a comparable response-requested rate. They supplied no case-specific or numerical adjustment. None is the target petition.

## General-precedent web attempt

One `web.run` call with two searches:

- `site.supremecourt.gov opinions Menominee Indian Tribe Wisconsin United States 2016 equitable tolling extraordinary beyond control`
- `site.govinfo.gov Clinton Jones 520 U.S. 681 1997 official duties private litigation`

The tool returned no visible results or source text. No web result was used, and no search sought this petition's disposition or subsequent history.

## CourtListener MCP

1. `search(type="o", citation="577 U.S. 250", num_results=1, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])` — returned Menominee Indian Tribe of Wis. v. United States, January 25, 2016; opinion ID 3171725. This is general controlling precedent, not the target case.
2. `search_document(opinion_id=3171725, query="beyond", snippet_size=800)` — six excerpts; verified the Court's requirement that extraordinary circumstances causing delay be outside the litigant's control. Used to evaluate the petition's claimed conflict, without treating Menominee as a decision about presidential tolling.

No live target-docket lookup, companion-disposition search, full-opinion corpus hydration, or additional external retrieval was attempted. Cell validation is a local output check, not evidence retrieval.
