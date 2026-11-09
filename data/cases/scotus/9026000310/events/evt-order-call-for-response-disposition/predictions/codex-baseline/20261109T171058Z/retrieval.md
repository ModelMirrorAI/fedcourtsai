# Retrieval record

## Scope

The baseline was the provisioned October 22, 2026 snapshot, context, event definition, document manifest, questions presented, petition, current appellate opinion, lower-court docket summary, selected appendix passages, and empty same-question candidate list. I did not query this petition's outcome, later history, current Supreme Court docket, another prediction, or an evaluation. This is a forward cell; the optional `--decided-before 2026` filters below conservatively exclude this petition's docket-number Term from corpus examples.

## Local reference and command attempts

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; inspected the schema structures using `jq` as well as raw reads. Read the modern-cert, paid-segment relist/CVSG/amicus cuts and `sal-v8` per-Term reached-band table in `metrics/statpack.md`. These are committed reference material, not additional case-state retrieval.
- `uv run fedcourts paths --court scotus --docket 9026000310 --event evt-order-call-for-response-disposition --role predictor` failed before running because `/home/codexcell/.cache/uv` was read-only. No package installation was attempted.
- Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000310 --event evt-order-call-for-response-disposition --role predictor`; succeeded and returned the case, corpus, and event paths, with the outcome explicitly evaluator-only. No outcome was opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. Its first display was partly lost to combined-output truncation, so it was repeated with `| sed -n '1,85p'` to read the filter definitions. Neither help call reports a transfer line.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3`

   Transfer: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`.

   Returned Google LLC v. VirtaMove, Corp. (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. City of Chicago (25-1098), each denied October 19, 2026, with stored distribution counts 2, 2, and 4 respectively. These are broad procedural examples, not fact-matched employment precedents; none materially supplies the grant probability. No full opinion requested.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '510 U.S. 17' --decided-before 2026 --limit 1`

   Transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`.

   Returned no row. The command reported that only 200 in-scope rows carry reporter citations and that this is an own-citation lookup, warning that a zero result is likely a sparse-field gap. I did not interpret it as an absence of Harris or as a precedential signal, and did not retry the sparse corpus filter.

## CourtListener MCP

1. `search(type="o", citation="157 F.4th 172", num_results=3, fields=["caseName","dateFiled","citation","court","absolute_url","id","opinions"])` returned zero results (query `649291ac`).
2. `search(type="o", case_name="Chislett", court="ca2", filed_before="2026-10-23", num_results=3, fields=["caseName","dateFiled","citation","court","absolute_url","id","opinions"])` returned Chislett v. N.Y.C. Department of Education, decided September 25, 2025, opinion ID **11144199**, cluster path `/opinion/10677612/chislett-v-nyc-dept-of-educ/` (query `44d3ef26`). The response warned that a requested result field was unavailable; the opinion ID and dated result were returned successfully. Its citation field was empty, explaining why the citation lookup did not locate it.
3. `search_document(opinion_id=11144199, query="constant drumbeat", snippet_size=1400)` returned one passage around opinion page 38 and its continuation, confirming that training is not inherently unlawful, that how it is conducted matters, and that the analysis also considered harassment in workplace interactions.
4. `search_document(opinion_id=11144199, query="trainings", snippet_size=350)` returned 20 of 42 matching passages, including the claim's section 1983 framing, repeated trainings, individual interactions, and complaints. Used only to check whether the petition's comparator is a single-session counterpart; it is not. No later history of Chislett or of Young was sought.

## Web attempts

1. `web.search_query(q='site.supremecourt.gov opinions "Ames" "2025" "23-1039"')`: the tool returned no visible result or usable source text.
2. `web.open(ref_id='https://www.supremecourt.gov/opinions/24pdf/23-1039_c0n2.pdf')`: the tool likewise returned no visible payload. I did not verify the guessed PDF address or rely on it as a retrieved opinion.

These attempts concerned general Title VII precedent, not Young's pending petition. No proposition in the forecast depends on the unavailable web material. The provisioned petition and appellate opinion already discuss Ames; that is the basis for the limited reference in the rationale.

## Completion

Validation uses `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000310/events/evt-order-call-for-response-disposition/predictions/codex-baseline/20261109T171058Z`. This is a local output-contract check, not a lookup of case outcomes.
