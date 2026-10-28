# Retrieval record

## Local inputs and static context

- Read AGENTS.md, the prediction prompt, and the prediction/tooling/flags schema contracts.
- Read this cell's event definition, case-level context and snapshot `2026-10-06.json`, document manifest, questions presented, selected substantive sections of both merits briefs and petitioner's merits reply, and the argument transcript through submission. Read the argument-feature coverage and per-Justice counts.
- Read the committed statpack's merits and prior-Term per-Justice sections, plus the corresponding `merits`, `justice_votes`, and `authorship` objects in `metrics/statpack.json`. A broad initial line search also returned cert-table rows; those rows were not used for this merits forecast.
- A local, read-only Python calculation selected merits grant Terms `2015 <= term < 2025`: 378 disturbed / 537 parsed; 553 eligible grants; 66 exclusions outside those grants. The available rows are OT2017-OT2024. It separately selected prior-Term vote and authorship rows, available for OT2020-OT2024. No case-specific corpus rows were queried.

## CLI calls

- `uv run fedcourts paths --court scotus --docket 73279865 --event evt-argument-judgment --role predictor` initially failed to initialize the default uv cache on a read-only filesystem. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; succeeded. The command named the evaluator-only outcome abstractly; that file was not opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed: the service backend has no client-side connection and directs query/open-events calls to the corpus query service. No corpus vintage was returned. No fallback credential access or direct remote read was attempted.
- No `fedcourts query`, `open-events`, or CourtListener MCP lookup was used; consequently no ranged-corpus-read transfer line was produced.

## Web context lookups

All searches concerned general law and Robison, not this case's own outcome. Search terms issued, including refinements/repetitions, were:

- `site.govinfo.gov 38 USC 511 decisions Secretary benefits 7292 constitutional`
- `site.loc.gov Johnson v Robison 415 U.S. 361 1974`
- `site.govinfo.gov "38 U.S.C. 511" "Secretary shall decide"`
- `site.loc.gov "Johnson v. Robison" "415"`
- `38 USC 511 Secretary shall decide all questions`
- `Johnson Robison 415 361 1974`

Relevant primary-source results included the official U.S. Code, the historical Robison opinion at the Library of Congress, and the official Court's historical U.S. Reports presentation. Search-result pages containing other veterans litigation were not used as evidence of this case's disposition.

Page retrievals/open attempts concerned:

- `https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title38-section511&num=0&edition=prelim` — unsuccessful retrieval.
- `https://www.govinfo.gov/content/pkg/USCODE-2024-title38/html/USCODE-2024-title38-partI-chap5-subchapI-sec511.htm` — official Section 511 context.
- `https://www.govinfo.gov/content/pkg/USCODE-2024-title38/pdf/USCODE-2024-title38-partI-chap5-subchapI-sec511.pdf` — official Section 511 PDF, opened and revisited for the relevant statutory text.
- `https://www.govinfo.gov/content/pkg/USCODE-2024-title38/pdf/USCODE-2024-title38-partV-chap72-subchapIV-sec7292.pdf` — official Section 7292 PDF and the scope of specialized appellate review.

Historical Robison context was available in the primary-source search result at `https://tile.loc.gov/storage-services/service/ll/usrep/usrep415/usrep415361/usrep415361.pdf`. No search for Johnson v. United States Congress, docket 25-735, its Supreme Court disposition, or its post-argument history was made. The forecast uses only the provisioned case record plus these general authorities and the static prior-Term calibration data.
