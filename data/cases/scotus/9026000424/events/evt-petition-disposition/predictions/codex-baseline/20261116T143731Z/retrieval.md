# Retrieval record

The substantive baseline was the provisioned case-level record, not a refreshed live docket. No own-case outcome, post-disposition history, other predictor output, or third-party forecast was requested or read. All commands ran from the repository root. `UV_NO_CACHE=1` bypassed a read-only default uv cache; it did not install packages.

## CLI discovery and local reference material

- `uv run fedcourts paths --court scotus --docket 9026000424 --event evt-petition-disposition --role predictor`: initially failed because uv could not create `/home/codexcell/.cache/uv/CACHEDIR.TAG` on a read-only filesystem. No case result returned.
- `uv run fedcourts query --help`: the same initial cache failure; no lookup ran.
- `UV_NO_CACHE=1 uv run fedcourts paths --court scotus --docket 9026000424 --event evt-petition-disposition --role predictor`: succeeded, identifying the case and event paths and marking the outcome evaluator-only. No outcome file was opened.
- `UV_NO_CACHE=1 uv run fedcourts query --help`: succeeded. A later `COLUMNS=160 UV_NO_CACHE=1 uv run fedcourts query --help | sed -n '40,105p'` also succeeded and displayed the clock, filter, and backend options.
- Read the committed `metrics/statpack.md` modern-cert, originating-circuit, paid-segment relist/CVSG/amicus, and per-Term salience sections. Inspected `metrics/statpack.json` keys and its first Term record, then used `jq` to pool baseline-band `prefix_weighted_resolved` and `prefix_est_grant_rate` over 2016 <= Term < 2026. Nine available rows, Terms 2017–2025, yielded 655 / 12,662 = 0.05172958458379403, matching the frozen anchor. The first inspected Term record was 2026 and was excluded from the pooled estimate.
- Read the prediction, tooling, and flags schemas, and used `command -v apply_patch` and `git status --short` for output preparation. These were local contract/workspace checks, not additional case evidence.

## Corpus queries

1. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --originating-court ca4 --era 2020s --decided-before 2026 --limit 5`
   - Refused: `--originating-court` is not a supported query option. The error printed the supported filters. No corpus read-stat line or cases returned. Reissued using supported flags below.
2. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --citation '593 U.S. 67' --decided-before 2026 --limit 3`
   - No matching row. Coverage warning: only 195 SCOTUS rows carry reporter citations, and the field describes the row's own citation, not cases citing an authority. Did not interpret the empty result as the absence of the precedent.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
3. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --era 2020s --decided-before 2026 --limit 5`
   - Returned Robinhood Markets v. Sodha (25-944, grant, three distributions and a CVSG), Roybal v. Griffith (25-442, GVR, three distributions and a CVSG), Harrington v. Martin (25-1348, GVR, two distributions), Jesenik v. United States (25-7515, denial, two distributions), and MacRitchie v. United States (25-7522, denial, two distributions). These are heterogeneous structured priors, not fact-matched comparators or an unbiased frequency sample. No returned case was this petition. Used only as procedural context, not as a numerical estimator.
   - `ranged corpus reads: 8 GET(s), 2031616 byte(s)`

## CourtListener MCP

1. `search(type="o", citation="886 F.3d 375", num_results=3)`: one result, Sky Cable, LLC v. DIRECTV, Inc., March 28, 2018; cluster 4481792, opinion 4259045.
2. `search_document(opinion_id=4259045, query="nonparty", snippet_size=600)`: eight excerpts. Confirmed the general party-only appeal rule, its interested-and-participating-nonparty exception, and the case-specific dismissal of Mrs. Coley's appeal. This is the precedent cited below, not later history of Boddie's petition.
3. `search(type="o", citation="593 U.S. 67", num_results=2, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: AMG Capital Management, LLC v. FTC, April 22, 2021, opinion 4679977, was the relevant first result. Also returned an unrelated Vax-D result, which supplied no evidence for this forecast.
4. `search_document(opinion_id=4679977, query="hold", snippet_size=220)`: seventeen excerpts, mostly references to Porter v. Warner Holding; too indirect to isolate the intended holding.
5. `search_document(opinion_id=4679977, query="does not authorize", snippet_size=450)`: two excerpts, including the syllabus's express holding that Section 13(b) does not authorize restitution or disgorgement. This confirmed the limited statutory premise, not its application to this particular receivership.

## General web attempts

- One `web.run` search call attempted two general official-site searches: `site.supremecourt.gov opinions 20pdf AMG Capital Management FTC 19-508` and `site.supremecourt.gov Rule 10 certiorari rarely granted erroneous factual findings misapplication properly stated rule law`. The tool produced no readable results. No own-case name or docket number was searched.
- One `web.run` open attempted the official AMG opinion PDF at the Supreme Court's `opinions/20pdf/19-508_l6gn.pdf` path. The tool produced no readable output. The relevant primary text was subsequently verified with CourtListener MCP, not direct REST.

## Completion check

The cell is checked using `UV_NO_CACHE=1 uv run fedcourts validate data --cell data/cases/scotus/9026000424/events/evt-petition-disposition/predictions/codex-baseline/20261116T143731Z`. The first check printed `OK: 30353 artifact(s) valid, 71806 reference(s) consistent; cell complete`. The same command is repeated after a summary wording clarification. This is local output validation, not case retrieval.
