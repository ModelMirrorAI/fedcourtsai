# Retrieval record

## Provisioned inputs and local reference material

Read the prediction prompt, prediction schema, tooling and flag schemas, the event definition, `record/context.json`, `record/snapshots/2026-09-01.json`, `record/documents/documents.json`, the questions presented, the petition body and retained opening portion of its state-opinion appendix, and `record/same-question.json`. Consulted the modern-cert, paid-segment relist/CVSG/amicus, and prior-Term salience-band tables in `metrics/statpack.md`. No other cell's prediction or evaluation was read. No own-case outcome or later history was sought.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000088 --event evt-order-call-for-response-disposition --role predictor` failed before execution because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was on a read-only filesystem. No corpus request or transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000088 --event evt-order-call-for-response-disposition --role predictor` succeeded and confirmed the case and event paths. The evaluator-only outcome was neither named nor opened. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. The same help command was subsequently piped to `sed -n '65,140p'` to inspect the options obscured in the first displayed output. Neither help call queried the corpus or printed a transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition denied --decided-before 2026 --limit 3` was rejected because `modern` is not a decade token. The usage response supplied the accepted era vocabulary. No transfer line.
5. Corrected call: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3` returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce (25-7555), all recorded denied November 9, 2026, with distribution counts two, two, and one. These are unrelated procedural examples, not topical precedents or estimates of this case's odds. This is a forward cell; the optional Term mask is not a day restriction and these unrelated dispositions do not disclose the target's outcome.

   `ranged corpus reads: 8 GET(s), 2031616 byte(s)`

6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '594 U.S. 595' --decided-before 2026 --limit 1` returned no row. It reported that only 195 in-scope SCOTUS rows carry reporter citations and warned that an empty citation lookup is likely sparse coverage rather than absence. Bonta was instead read from the official opinion.

   `ranged corpus reads: 9 GET(s), 2359296 byte(s)`

## Web calls: general precedent only

1. A single `web.run` search call contained two queries: `site.supremecourt.gov opinions 20pdf Americans for Prosperity Foundation Bonta 19-251 exacting scrutiny disclosure` and `site.supremecourt.gov opinions Citizens United 08-205 disclosure express advocacy 368 369`. Results included Bonta's official case page and Citizens United opinion text alongside unrelated general results. No target-case disposition or target-case forecast surfaced. Unrelated results were not used.
2. Opened the official Bonta opinion at `https://www.supremecourt.gov/opinions/20pdf/19-251_p86b.pdf` (52 pages). Consulted its exacting-scrutiny and narrow-tailoring analysis, particularly part II. This was source R1 for the doctrinal comparison, not a prediction of this case.
3. Opened the Citizens United opinion text at `https://www.law.cornell.edu/supremecourt/text/08-205`. Consulted part IV, particularly its treatment of disclaimer/disclosure requirements and its rejection of an express-advocacy-only limit. This was source R2. The judicial opinion text, rather than surrounding commentary, informed the forecast.

## CourtListener MCP calls: lower-court precedent only

1. `search(type="o", court="ca9", case_name="No on E v. Chiu", num_results=3, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` returned March 8 and October 26, 2023 opinions. The latter is opinion **9893329**, the amended opinion and rehearing order.
2. `search_document(opinion_id=9893329, query="Sampson", snippet_size=1100)` returned no matches. No inference of legal inconsistency was drawn from that absence.
3. `search_document(opinion_id=9893329, query="exacting scrutiny", snippet_size=220)` returned 20 of 24 matches. The panel's analysis applied exacting scrutiny to the donor disclaimer rule and rejected the preliminary-injunction showing; excerpts also included separately identified disagreement. Used to distinguish settled disclosure doctrine from APF's proposed extension. Source R3: CourtListener opinion 9893329.
4. `search(type="o", court="cadc", case_name="Van Hollen v. Federal Election Commission", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` returned the January 21, 2016 appellate opinion, **3171275**, 811 F.3d 486, and a separate 2013 district-court opinion. Only the appellate opinion was substantively consulted.
5. `search_document(opinion_id=3171275, query="arbitrary", snippet_size=400)` returned ten matches, including the introduction and part II describing the statutory and arbitrary-and-capricious bases for upholding the FEC's rule. Used to avoid mistaking a permissible federal earmarking regulation for a categorical constitutional command. Source R4: CourtListener opinion 3171275.

No CourtListener failure, direct REST request, own-case live docket request, external case forecast, or target-case outcome retrieval occurred. Local completeness/schema validation is reported by the required `fedcourts validate data --cell` command and is not a precedent lookup.
