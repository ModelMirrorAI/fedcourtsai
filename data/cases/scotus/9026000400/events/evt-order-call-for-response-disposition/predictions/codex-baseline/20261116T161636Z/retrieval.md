# Retrieval record

## Provisioned and repository materials

- Read `.github/prompts/predict.md` and the prediction schema, followed by the event definition, case-level context, October 29 snapshot, document manifest, questions presented, petition arguments, appellate majority and dissent in the appendix, and empty same-question match list. Read the tooling/flags schemas for output requirements. No outcome or other predictor/evaluator output was read.
- Consulted `metrics/statpack.md`: frozen-band/risk-set interpretation, prior-Term salience rows, paid-segment relist, CVSG, and amicus cuts. The numerical frozen anchor and amicus reference came from the provisioned context.

## CLI calls

Commands below ran from the repository root. No package installation was attempted.

1. `uv run fedcourts paths --court scotus --docket 9026000400 --event evt-order-call-for-response-disposition --role predictor` failed before running the CLI because the default uv cache was read-only.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000400 --event evt-order-call-for-response-disposition --role predictor` succeeded and resolved the case and event paths; no evaluator-only file was named or opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` displayed structured filters. A second help invocation with `COLUMNS=120` and output piped to `head -n 70` displayed the beginning of the same help, including clock semantics.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` returned Robinhood Markets v. Sodha (25-944), Goldman Sachs Bank USA v. Brown (25-1408), and U.S. DOGE Service v. U.S. District Court (25-1103). These are unrelated procedural examples, not denominator evidence or analogies on the questions presented. The bare-year clock uses the docket-derived Term, so returned grants can occur in calendar 2026; this cell is forward and no own-case row was requested.
   - `ranged corpus reads: 39 GET(s), 10158080 byte(s)`
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket 24-304 --limit 1` was rejected: the valid flag is `--docket-number`. No corpus transfer line was printed.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 24-304 --limit 1` succeeded. Returned Labcorp v. Davis, with a January 24, 2025 cert grant and four distributions. The grant field is a cert-stage fact, not its later merits disposition, which was checked through the primary opinion.
   - `ranged corpus reads: 17 GET(s), 4456448 byte(s)`

## CourtListener MCP

1. `search(type="o", citation="964 F.3d 141", num_results=2)` returned Berni v. Barilla, Second Circuit, July 8, 2020; cluster 4766372, opinion 4546719.
2. `search_document(opinion_id=4546719, query="future", snippet_size=650)` returned passages on future injury, informed past purchasers, and the Rule 23(b)(2) class. Used to check the prospective-standing contrast, with attention to the packaging/settlement factual setting.
3. `search(type="o", citation="605 U.S. 327", num_results=1)` returned Labcorp v. Davis, June 5, 2025; cluster 10776843, opinion 11243430. Other search matches were not paginated or read.
4. `search_document(opinion_id=11243430, query="dismissed", snippet_size=1200)` returned the per curiam dismissal and Kavanaugh's dissent, including his explanation of the possible mootness concern and his proposed answer under Rule 23. Used to distinguish the Court's unexplained order from the dissent's explanation. This is a prior case, not the petition being predicted.

## Web attempts

All web attempts returned no usable displayed content, so no factual conclusion relies on them. Searches were directed to precedents, not this petition or anyone's forecast.

1. One `web.run` search batch used these exact queries:
   - `site.supremecourt.gov opinions 2024 Laboratory Corporation Davis 24-304 Kavanaugh dismissed`
   - `site.ca2.uscourts.gov Berni Barilla 964 141 injunction 2020`
   - `site.ca9.uscourts.gov Olean Wholesale 31 F.4th 651 2022 en banc`
2. A second search used `Laboratory Corporation of America Holdings Davis 24-304 June 5 2025 Kavanaugh`.
3. An open attempt used the official Labcorp opinion URL supplied by MCP: `https://www.supremecourt.gov/opinions/24pdf/605us1r40_f1gk.pdf`.

## Validation

The final cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000400/events/evt-order-call-for-response-disposition/predictions/codex-baseline/20261116T161636Z`. This is a local schema/completeness check, not outcome retrieval.
