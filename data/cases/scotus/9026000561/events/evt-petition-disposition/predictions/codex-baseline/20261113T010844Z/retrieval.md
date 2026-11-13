# Retrieval record

## Provisioned and local sources

Read the prediction prompt, prediction/tooling/flags schemas, event definition, case-level snapshot `record/snapshots/2026-11-13.json`, `record/context.json`, `record/documents/documents.json`, `questions-presented.txt`, petition text including relevant bound appendix documents, and `record/same-question.json`. Consulted `metrics/statpack.md`: modern-cert disposition/circuit tables, paid-segment relist/CVSG/amicus cuts, and the sal-v8 prior-Term reached-band table. No other prediction or evaluation cell and no `data/qp-topics/` artifact was read.

## CLI attempts and corpus lookups

1. `uv run fedcourts paths --court scotus --docket 9026000561 --event evt-petition-disposition --role predictor` failed before running because the default uv cache was read-only. No transfer line.
2. `uv run fedcourts query --help` failed for the same cache reason. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000561 --event evt-petition-disposition --role predictor` succeeded, resolving case/event paths. No transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. Read the structured filter interface; no transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era roberts --limit 3` was rejected: eras must be decade tokens. The error supplied the accepted vocabulary; no transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 3` succeeded. Returned James Dwight Pavatt's 26-6095 cert petition, his 26A661 substantive application, and Paul Schultz's 26A658 application. Not close substantive comparators and not treated as a statistical sample of cert petitions.
   - `ranged corpus reads: 4 GET(s), 983040 byte(s)`
7. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 2` succeeded. Returned Roybal v. Griffith, 25-442, and Harrington v. Martin, 25-1348. Unrelated GVR examples, not evidence of a disposition trigger for this petition. This is a forward cell; the optional Term filter does not imply that every returned disposition occurred before calendar 2026.
   - `ranged corpus reads: 2 GET(s), 524288 byte(s)`
8. Repeated the preceding command, piping stdout to `jq '{case_name,docket_number,disposition,distribution_count,cvsg_date}'` to display compact results after the earlier combined terminal output was truncated. Roybal had three distributions and a CVSG date; Harrington had two and none. Neither supplies a legal analogy here.
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`

`DECIDED_BEFORE` was checked and was empty. No own-case corpus query, full-opinion hydration, or package installation was attempted.

## CourtListener MCP

1. `search(type="o", court="ca11", docket_number="23-10340", num_results=3)` returned one published opinion: *Sualeh Ashraf v. United States Drug Enforcement Administration*, September 3, 2025, cluster 10665536, opinion 11132123. This is the lower-court authority cited by the petition, not this petition's outcome.
2. `search_document(opinion_id=11132123, query="corrective", snippet_size=800)` returned eight matches, covering the statutory framework, the proposed plan, the Administrator's substantive treatment of it, hearing waiver, and the concurrence's footnote. Used only to check whether this authority establishes a conflict over the particular statutory question. It did not establish one.

## Web attempts

1. A batched search for `site.ca11.uscourts.gov Ashraf DEA 153 F.4th 1161 corrective action 2025` and `site.uscode.house.gov 21 USC 824 corrective action plan determine` returned no visible content. No web result supplied evidence or exposed a forecast.
2. An open of `https://media.ca11.uscourts.gov/opinions/pub/files/202310340.pdf` returned no visible content. Relied on the CourtListener excerpts and provisioned appendix instead.

No live Supreme Court docket retrieval, own-case disposition search, or search for anyone else's forecast was attempted.

## Validation

`UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000561/events/evt-petition-disposition/predictions/codex-baseline/20261113T010844Z` returned `OK: 30261 artifact(s) valid, 71750 reference(s) consistent; cell complete`. Validation is a local output check, not additional case retrieval. The same command was repeated after recording this result.
