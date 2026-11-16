# Retrieval record

## Local inputs and tooling

Read the prediction contract, prediction and feedback schemas, event definition, provisioned snapshot/context, document manifest, questions presented, petition arguments and relevant appendix, party letter, decision below, lower-court docket summary, and same-question list. Read the modern-cert, originating-circuit, paid-segment relist/CVSG/amicus, and sal-v8 per-Term sections of `metrics/statpack.md`. Repository file/instruction discovery showed filenames only; no outcome contents or other cell output were opened. No outcome was restored through git.

The first `uv run fedcourts paths --court scotus --docket 9026000522 --event evt-order-call-for-response-disposition --role predictor` failed because the default uv cache path was read-only. Repeating it with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. Subsequent uv commands used that cache override. `fedcourts query --help` was consulted twice, the second time displaying its opening section. These were tooling discovery, not case retrieval.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026-01-01 --limit 4`
   - Rejected: unknown era `modern`; the CLI explained that eras are decade tokens. No transfer line was emitted.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-01-01 --limit 4`
   - Returned four pre-clock granted petitions: Terry Pitchford, John Doe v. Dynamic Physical Therapy, Adrian Jules, and Ahmad Abouammo. Their procedural rows were only a broad sanity check, not subject-matched evidence or a denominator for the grant estimate. No full opinions requested.
   - Exact stderr transfer line: `ranged corpus reads: 82 GET(s), 21430272 byte(s)`.
   - The CLI also confirmed the January 1, 2026 cutoff. This voluntarily conservative clock excluded the target petition; the cell itself is forward mode.

## CourtListener MCP

1. `search(type="o", court="ca8", q='"Melton" "Forrest"', num_results=3)` returned Melton's August 13, 2025 published opinion, cluster 10653052, opinion 11119639, appellate No. 23-3398, together with two unrelated matches. Only Melton was pursued.
2. `search(type="o", court="scotus", case_name="MacRae", num_results=1)` returned the unrelated 1995 Clapp v. LeBoeuf, Lamb, Leiby & MacRae denial. It did not verify the modern MacRae statement. No further result pagination or document read followed.
3. `search_document(opinion_id=11119639, query="disruption", snippet_size=600)` returned ten matches. They confirm Melton's requirement for evidence of actual or reasonably anticipated operational harm, the insufficiency of mere controversy by itself, and remaining factual/immunity questions. This informed assessment of the claimed split, not the target's disposition.

## Web calls, in order

All searches sought general precedent, not this petition's disposition or another forecast. Search result lists were sometimes broader than their query text.

1. Search batch: `site.supremecourt.gov "Pickering" "disruption" "Thomas" "2026"`; `site.supremecourt.gov "Moser" "Las Vegas" "2025"`. Results included Pickering background, Moser material, and unexpectedly a FedCourtsAI result for this case whose headline advertised a 5% certiorari forecast. That result was not opened or used. The numerical exposure is disclosed in `flags.json` and `reasoning.md`.
2. Search batch: `"Pickering" "disruption" "Thomas" "2026"`; `"Moser" "Las Vegas" "2025"`. Results included secondary Pickering commentary, Moser materials, and a November 13 ACLJ amicus document concerning the target petition. No target-case page or filing was opened; the later filing snippet was not used to change the frozen amicus count or forecast.
3. Search batch: `"MacRae" "Thomas" "Pickering"`; `"Moser" "Las Vegas" "disruption"`; `"Melton" "Forrest City" "disruption"`. Results included secondary MacRae/Moser discussion and primary or republished Melton material. These served to locate precedent; secondary legal conclusions were not adopted.
4. Search: `MacRae Hanover Thomas denial certiorari June 2025 disruption`. Returned reporting and background on MacRae, not the target case. No commentary page opened.
5. Search: `MacRae Mattos Thomas 24-679`. Returned MacRae reporting and background, identifying No. 24-355 in snippets. No case-outcome retrieval for Inendino and no commentary page opened.
6. Open attempt: `https://www.supremecourt.gov/opinions/24pdf/24-355_i425.pdf`. Returned 404; no opinion text retrieved. This unsuccessful guessed primary-source URL is not cited as verification.
7. Open: `https://ecf.ca8.uscourts.gov/opndir/25/08/233398P.pdf`. Successfully retrieved the official 13-page Eighth Circuit Melton opinion. Its disruption discussion supported the comparison to the decision below.
8. Search: `site:supremecourt.gov/opinions/24pdf "24–355" "THOMAS"`. Returned Supreme Court search snippets mentioning unrelated orders/opinions, not a verified MacRae statement; no further page opened.

No current target docket, target disposition, subsequent target history, forecast page, market, or other cell output was intentionally retrieved. The search-result forecast exposure remains a limitation despite exclusion from the analysis.
