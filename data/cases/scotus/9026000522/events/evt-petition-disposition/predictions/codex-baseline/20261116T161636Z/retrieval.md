# Retrieval log

## Provisioned and repository inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the tooling and flags schemas, the cell's event definition, case-level context and snapshot, document manifest, questions presented, relevant petition argument and appendix passages, the party letter, relevant decision-below passages, lower-court docket summary, and `same-question.json`. The latter listed no matches; no companion was inferred. Read the relevant modern-cert, circuit, paid relist/CVSG/amicus, and sal-v8 prior-Term tables in `metrics/statpack.md`. Did not read another prediction, an evaluation, any realized outcome file, or anything under `data/qp-topics/`.

## CLI and corpus calls

All successful `uv run` commands used the environment prefix `UV_CACHE_DIR=/tmp/uv-cache`; no package was installed.

1. `uv run fedcourts paths --court scotus --docket 9026000522 --event evt-petition-disposition --role predictor` initially failed before running because uv's default cache directory was read-only. Repeated with the cache override and obtained the expected case and event paths. A later identical successful invocation reconfirmed those paths. No outcome file was opened.
2. `uv run fedcourts query --help` read the structured filters. Repeated with `COLUMNS=130` and `head -65` for readable filter documentation. These were help calls, not corpus data reads.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 4`: returned Robinhood Markets v. Sodha (25-944), Mullin v. Refugee and Immigrant Center (26-239), Mullin v. Friends of the Ruidosa Church (26A560, a substantive application), and Goldman Sachs v. Brown (25-1408). The first command's large combined output was truncated in the displayed tool result, so its transfer line was not retained in that excerpt. No rate was estimated from this selected sample.
4. `uv run fedcourts query --court scotus --era 2020s --citation '606 U.S. 937' --limit 2 | jq -c '{case_id,case_name,docket_number,disposition,date_decided,citations}'`: no rows. The tool explained that only 195 in-scope rows had reporter citations and that a missing result is likely missing-column coverage, not missing precedent. Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`.
5. Repeated call 3, this time piping through `jq -c '{case_id,case_name,docket_number,disposition,distribution_count,application_kind}'` to keep the output compact. Same four cases; cert distribution counts 3, 2, and 4, plus the application with 0. Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`.

## Web attempts

These searches concerned precedents, not this petition or its outcome. None supplied usable precedent text for the forecast. Results unrelated to the requested authorities were not relied on.

1. One `web.run` batch searched `site.supremecourt.gov MacRae June 2025 Thomas Pickering speculative disruption`; `Melton v City of Forrest City 147 F.4th 898 2025 court opinion`; and `Noble Cincinnati Hamilton County Public Library 112 F.4th 373 opinion 2024`. No usable source content was rendered.
2. One batch searched `site.supremecourt.gov "MacRae" "speculative"` and `site.ca6.uscourts.gov "Noble" "24a0175p.06"`. No usable primary-source content was obtained.
3. Attempted opening `https://www.supremecourt.gov/opinions/24pdf/24-355_i425.pdf` while looking for the historical MacRae statement. This unverified candidate URL did not supply usable text; it was not treated as the correct opinion.
4. Searched `site.supremecourt.gov/opinions "MacRae" "24-359"`. No usable primary-source content was obtained; the tentative docket number was not relied on.
5. Searched `"MacRae v. Mattos" "supremecourt.gov/opinions"`. No usable primary-source content was obtained.

## CourtListener MCP

1. `search(type="o", court="ca8", case_name="Melton", docket_number="23-3398", num_results=3, fields=[caseName,dateFiled,citation,opinions,absolute_url,docketNumber])`: one result, Steven Melton v. City of Forrest City, August 13, 2025; cluster 10653052, opinion 11119639. Primary court PDF identified as `https://ecf.ca8.uscourts.gov/opndir/25/08/233398P.pdf`.
2. `search(type="o", court="ca6", citation="112 F.4th 373", num_results=2, fields=[caseName,dateFiled,citation,opinions,absolute_url,docketNumber])`: Noble v. Cincinnati & Hamilton County Public Library, August 9, 2024, No. 23-3853; cluster 10035855, opinion 10502456. Primary court PDF identified as `http://www.opn.ca6.uscourts.gov/opinions.pdf/24a0169p-06.pdf`.
3. `search_document(opinion_id=[11119639,10502456], query="public", snippet_size=550)`: public-service facts and speech analysis from the two opinions. Broad results were numerous, so follow-up calls targeted the dispositive passages.
4. `search_document(opinion_id=11119639, query="record and the prediction", snippet_size=1500)`: one relevant passage explaining the need to substantiate a prediction, jury resolution of a mismatch, and rejection of automatic deference. This independently supports the petition's Melton comparison, without establishing that all factual distinctions disappear.
5. `search_document(opinion_id=10502456, query="public-facing", snippet_size=1250)`: majority footnote 5 and a dissent passage. The majority emphasized no demonstrated patron exposure/objection; the dissent stressed trust and public-safety concerns. Both informed the assessment of the split and factual distinctions.
6. `search(type="o", court="scotus", case_name="MacRae", num_results=3, fields=[caseName,dateFiled,citation,opinions,absolute_url,docketNumber])`: returned unrelated historical captions, not the relevant modern statement. No follow-up historical docket or outcome retrieval was made. The forecast attributes the Thomas statement to the provisioned petition rather than representing this as independent verification.

No CourtListener request failed, no REST fallback was used, and no current Supreme Court docket or filing outside the provisioned record was retrieved.

## Validation

The final cell is checked using `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000522/events/evt-petition-disposition/predictions/codex-baseline/20261116T161636Z`.
