# Retrieval record

## Provisioned and local reference inputs

Read the prediction prompt and schema, this event definition, November 9 snapshot, context, document manifest, questions presented, selected substantive passages of the petition and appendix, BIO and reply, decision-below summary, lower-court-docket report, and same-question file. Consulted the committed `metrics/statpack.md` for prior-Term salience anchors and the relist/CVSG/amicus cuts. Read the flags and tooling schemas. No evaluator outcome file, other local prediction directory, or `data/qp-topics/` artifact was read.

## CLI lookups, including attempts

1. `uv run fedcourts paths --court scotus --docket 9026000071 --event evt-order-relist-disposition --role predictor` failed before running because uv's default cache was on a read-only filesystem. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; it resolved the case and event paths and labeled the outcome evaluator-only. No outcome was opened.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured-filter interface, including the docket-number companion lookup. No corpus transfer line was printed for help.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 4` returned Goldman Sachs v. Brown (25-1408), Scanlan v. Coalition for Open Democracy (26A512), Association for Education Fairness (26-12), and DOJ v. McNutt (26-204). This is a grant-selected convenience sample, not a base-rate sample. Scanlan is an application and was excluded as a cert analogue. The displayed combined response was truncated and the initial `ranged corpus reads` line was not retained in the visible excerpt; no transfer count is invented here.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 25-828 --limit 1` returned the pending Nwauzor companion, case ID scotus/73279966, two distributions, CVSG May 18, 2026, and conference November 6, 2026; no cert grant or denial. Stderr: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`.
5. Repeated `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 4`, piping through jq to retain only caption, docket, disposition and distribution/CVSG fields. Same four rows. Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.

There was no replay clock: context mode is forward and `DECIDED_BEFORE` was unset. No CourtListener MCP lookup was necessary because the matched opinion and lower-court docket were provisioned.

## Web retrieval

1. Search query: `site.supremecourt.gov "25-828" "September 15, 2026" "United States"`. The search unexpectedly returned GitHub pages, including snippets of other cases' committed prediction files, rather than the invited brief. I did not open or rely on those predictions. Disclosed in flags. No result disclosed this petition's own outcome.
2. Opened the Supreme Court's official docket for companion **25-828**, not this petition: `https://www.supremecourt.gov/search.aspx?filename=%2Fdocket%2Fdocketfiles%2Fhtml%2Fpublic%2F25-828.html`. It confirmed a pending petition, the May 18 CVSG, the September 15 invited brief, and November 6 conference distribution. The latest listed proceeding was the October 21 distribution; it showed no cert disposition.
3. Followed docket link 22 to the September 15, 2026 United States amicus brief, official PDF path `https://www.supremecourt.gov/DocketPDF/25/25-828/423789/20260915131829749_25-828%20GEO%20Group%20v.%20Nwauzor.pdf`. Its introduction recommends granting Nwauzor, identifying this petition as a companion candidate, and an alternative hold. Used this recommendation as federal support for the shared issue, not as an invited brief filed in the present docket. No own-case disposition was sought.
