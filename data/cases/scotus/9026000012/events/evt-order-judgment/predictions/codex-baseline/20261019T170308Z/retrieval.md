# Retrieval record

## Provisioned materials

- Read the case-level context, October 19, 2026 snapshot, event definition, document manifest, and questions presented. Read relevant portions of the petition, opposition, cert reply, and appendix. No merits briefs were provisioned.
- Read the prediction contract and artifact schemas. Inspected path and serialization helpers for output handling; did not inspect other predictors' outputs, evaluations, outcomes, or topic-label artifacts.

## Committed base-rate context

- Read `metrics/statpack.md`, principally `The merits docket (granted cases)`, and calculated the 2016–2025 window from its published Term rows in a local Python command. Observed 377 disturbed / 540 parsed, 590 included grants, and 66 excluded grants. The rows present are 2017–2025. The consulted section supplies no corpus refresh timestamp.
- No `fedcourts query` or `open-events` call was made, and there is no ranged corpus transfer line to report. `fedcourts paths --court scotus --docket 9026000012 --event evt-order-judgment --role predictor` resolved local paths only. Its first invocation failed on the default cache directory; retry with a writable temporary cache succeeded.

## Web attempts

1. A batched web search used `site.supremecourt.gov opinions 2022 20-1199 Students Fair Admissions Harvard individual race` and `site.loc.gov Arlington Heights 429 U.S. 252 discriminatory intent`. The tool returned no usable results or source text.
2. Attempted to open the official SFFA slip-opinion PDF at `https://www.supremecourt.gov/opinions/22pdf/20-1199_hgdj.pdf`. The tool returned no usable content. No substantive claim rests on these web attempts.

## CourtListener MCP

1. `search(type="o", citation="429 U.S. 252", num_results=1)` returned an unrelated Briscoe v. Klaus result. Disregarded it; this was not verification of Arlington Heights.
2. `search(type="o", court="scotus", case_name="Village of Arlington Heights v. Metropolitan Housing", filed_before="2026-10-19", num_results=2, fields=["caseName","dateFiled","citation","opinions","absolute_url"])` located the January 11, 1977 decision, 429 U.S. 252, opinion 109573, and a later cert-denial entry in that older litigation. Used only the 1977 decision.
3. `search_document(opinion_id=109573, query="sensitive inquiry", snippet_size=2500)` returned the majority's discussion at 265–267 of discriminatory purpose, impact, and other circumstantial evidence. Used as general doctrinal context.
4. `search(type="o", court="scotus", case_name="Students for Fair Admissions", filed_after="2023-06-28", filed_before="2023-06-30", num_results=2, fields=["caseName","dateFiled","citation","opinions","absolute_url"])` located duplicate records of the June 29, 2023 decision, 600 U.S. 181, including slip-opinion document 9405814.
5. `search_document(opinion_id=9405814, query="person, not any group", snippet_size=1200)` found no literal match.
6. `search_document(opinion_id=9405814, query="individual", snippet_size=450)` returned excerpts from the syllabus, majority, and separate writings. Used the majority's individual-treatment discussion as general context, not the separate writings as holdings.

No target-case outcome or subsequent-history search was made. No external material revealed this case's merits disposition.
