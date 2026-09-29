# Retrieval log

## Provisioned inputs

Read event.yaml, record/context.json, record/snapshots/2026-09-28.json, record/documents/documents.json, and record/documents/application.txt for this cell. No outcome file, other predictor output, or labeling-measurement artifact was read. No search targeted this case's disposition or subsequent history.

## Committed base-rate context

Read metrics/statpack.md, specifically its introductory coverage information and interim-applications section. Inspected metrics/statpack.json's keys, coverage, and interim counts, and computed the 2016–2025 pool from its interim.terms array: 31 grants / 296 resolved = 0.10472972972972973. Current-Term counts were visible in the table but excluded from the anchor. No fedcourts query or open-events call was made; there is no ranged-corpus transfer line to report.

## General web retrieval attempts

The following web.run searches returned no usable result payload or source text. None informed the forecast as retrieved evidence:

1. `site.supremecourt.gov opinions 2025 FDA Wages White Lion arbitrary capricious review`
2. `site.supremecourt.gov opinions 2025 United States Skrmetti 23-477`
3. `FDA v Wages White Lion 2025 Supreme Court opinion`
4. `Hollingsworth Perry 558 U.S. 183 190 stay`
5. `18 USC 3626 preliminary injunctive relief`
6. `"23-477" "supremecourt.gov/opinions/24pdf"`
7. `"Hollingsworth" "09A648" "supremecourt.gov/opinions"`

An attempted web.run open of `https://www.supremecourt.gov/opinions/24pdf/23-477_2cp3.pdf` also returned no usable content; that attempted URL was not a verified source. These requests concerned general law and separate, prior cases only.

## CourtListener MCP

1. `search(type="o", citation="558 U.S. 183", num_results=1, fields=["caseName","citation","dateFiled","absolute_url","opinions"])`: returned Hollingsworth v. Perry, January 13, 2010; lead opinion 9413203.
2. `search_document(opinion_id=9413203, query="reasonable probability", snippet_size=700)`: read the stay requirements at 558 U.S. 190; used for the general standard.
3. `search(type="o", case_name="FDA v. Wages", court="scotus", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])`: returned FDA v. Wages and White Lion Investments, LLC, 604 U.S. 542, April 2, 2025; opinion 11243447.
4. `search_document(opinion_id=11243447, query="narrow", snippet_size=750)`: read the narrow-review passage and a separate harmless-error/remand discussion; used the former, without treating the latter as a blanket harmless-error rule.
5. `search(type="o", citation="973 F.3d 1263", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])`: returned Hoffer, August 31, 2020; opinion 4561662.
6. `search_document(opinion_id=4561662, query="particularized", snippet_size=850)`: read excerpts on PLRA findings, including the majority's requirement and dissenting disagreement. Used the majority's principle as circuit authority and did not transpose the underlying medical merits.
7. `search(type="o", citation="605 U.S. 495", court="scotus", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])`: returned United States v. Skrmetti, June 18, 2025; opinion 11243418.
8. `search_document(opinion_id=11243418, query="rational basis", snippet_size=450)`: returned "No text is available for this document." No substantive passage was available or relied upon from this lookup.

No direct CourtListener REST request was made. No case-specific live retrieval occurred.

## Local operational checks

Read the prediction, tooling, and flags schemas, path/identifier helpers, and serialization helpers to comply with the output contract. Ran `uv run fedcourts paths --court scotus --docket 9526000416 --event evt-order-response-requested-disposition --role predictor`; the first attempt failed because the default cache was read-only, and the retry with the cache placed in writable temporary storage succeeded. Schema and data validation are local artifact checks, not sources of outcome information.
