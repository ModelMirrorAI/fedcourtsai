# Retrieval record

## Provisioned and committed inputs

Read the event definition, case-level November 8 snapshot and context, document manifest, questions presented, substantive petition and reply text, and both oppositions combined in the provisioned opposition file. Read the related-case manifest and staged snapshot for No. 26-332. Read the prediction/tooling/flags schemas and the relevant cert sections of `metrics/statpack.md` and `metrics/statpack.json`. No outcome file, other prediction, evaluation, or `data/qp-topics/` material was read.

The statpack arithmetic used only OT2017–OT2025 state-band reached counts, producing 98/420 = 0.23333333333333334, consistent with the frozen context anchor. Terminal relist, CVSG, and amicus cuts were read for population shape only.

## Corpus calls

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. A later display of the same help used `COLUMNS=140 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help | sed -n '1,65p'`. These were interface-help reads, not corpus retrievals, and printed no transfer lines.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 4` was refused because `modern` is not a valid decade token. It returned the structured-filter vocabulary and no cases or transfer line. The corrected query follows.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 4` succeeded.

   `ranged corpus reads: 14 GET(s), 3670016 byte(s)`

   Returned Google LLC v. VirtaMove, No. 25-1230; Hastings College Conservation Committee v. California, No. 25-1231; Ryan O'Donnell v. City of Chicago, No. 25-1098; and Utah v. Mullins, No. 25-1115. The rows reported denial on October 19, 2026 and distribution counts 2, 2, 4, and 3. This forward cell has no replay clock; the optional year filter is a docket-Term bound, not a claim that these decisions predated January 2026. All returned dates precede the November 8 forecast. No opinion text was requested. These are broad procedural comparisons, not topic-matched priors, and do not determine the numerical adjustment.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-199 --include-open --limit 2`, piped through `jq` to display only identity and procedural fields, succeeded.

   `ranged corpus reads: 15 GET(s), 3932160 byte(s)`

   Returned `scotus/9026000199`, Horseracing Integrity and Safety Authority v. National Horsemen's Benevolent and Protective Association. Disposition, cert grant/denial dates, conference field, and CVSG date were null; distribution count was zero. No decision or opinion was retrieved.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-201 --include-open --limit 2`, with the same `jq` projection, succeeded.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

   Returned `scotus/9026000201`, Federal Trade Commission v. National Horsemen's Benevolent and Protective Association, also with no disposition, grant/denial dates, conference field, or CVSG date and distribution count zero. The zero transfer reflects the warmed service cache, not an omitted call. Neither lead-case lookup queried this cell's own docket.

## Web attempts

1. `web.run` search query: `site.supremecourt.gov opinions 2025 FCC Consumers Research 24-354 private parties retains decision making power`. The tool returned no usable result content.
2. `web.run` opening of the attempted official opinion path `https://www.supremecourt.gov/opinions/24pdf/24-354_0861.pdf` returned no usable document content. The path was an attempted lookup, not a verified source. Neither attempt searched for Texas's petition disposition or its subsequent history; no factual inference rests on these empty responses.

## CourtListener MCP

1. `search(type="o", citation="606 U.S. 656", court="scotus", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` returned FCC v. Consumers' Research, filed June 27, 2025, opinion ID 11243407. It verified precedent identity and date, not the substance of the private-delegation analysis. The result identified the Court's preliminary-print PDF as `https://www.supremecourt.gov/opinions/24pdf/606us2r64_8nj9.pdf`; that PDF was not separately opened.
2. `search_document(opinion_id=11243407, query="retains decision", snippet_size=550)` failed with HTTP 429, reporting a rate limit of 25 requests per minute and an expected 36-second wait. No opinion passage was returned. I did not retry or use a REST fallback; doctrinal reasoning rests on the provisioned briefs.

## Operational commands

The initial required `uv run fedcourts paths --court scotus --docket 9026000335 --event evt-petition-disposition --role predictor` failed because uv's default cache directory was read-only. Repeating it with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and resolved the case and event paths. All subsequent uv commands used that cache override. These commands were path/interface checks rather than retrieval of case outcomes. The only intended output artifacts are in this prediction cell.
