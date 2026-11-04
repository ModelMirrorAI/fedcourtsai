# Retrieval record

## Provisioned and stable material

Read `.github/prompts/predict.md`, the prediction and feedback/flags schemas, the event definition, the October 31 snapshot, context, application manifest, and the complete application. Consulted `metrics/statpack.md` and extracted the interim per-Term finer counts from `metrics/statpack.json`. No other cell's predictions or evaluations, outcome record, or topic-labeling artifacts were read.

## Local CLI and corpus calls

1. `uv run fedcourts paths --court scotus --docket 9526000623 --event evt-motion-disposition --role predictor` initially failed because the default uv cache was read-only. No corpus result or transfer line.
2. The same paths command with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and resolved the case/event paths. Its evaluator-only outcome path was not exposed or read.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` was consulted once in full and twice through narrower terminal excerpts to read the structured options. These help calls produced no corpus transfer lines.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 4`
   - `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Returned Google v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), O'Donnell v. Chicago (25-1098), and Utah v. Mullins (25-1115). All are unrelated cert denials. They were not treated as interim comparators or as a grant-rate sample. The Term screen masked tracking fields; it was not a claim that every returned decision predated calendar 2026.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '523 U.S. 272' --decided-before 2026 --limit 2`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - No rows. The tool reported that only 200 scoped rows carried reporter citations and warned that the empty result was likely a coverage gap. Did not retry the sparse filter.

## Historical authority via CourtListener MCP

6. `search(type="o", citation="523 U.S. 272", num_results=1)` returned Pegram v. Honeywell, 361 F.3d 272 (5th Cir. 2004), an unrelated result. Disregarded; no document read.
7. `search(type="o", court="scotus", case_name="Ohio Adult Parole Authority v. Woodard", num_results=2)` located the March 25, 1998 decision, 523 U.S. 272, cluster 118189, and an unrelated-to-the-merits 1997 counsel order in the same historical litigation. Used only the 1998 decision metadata to identify the concurrence.
8. `read_document(opinion_id=9433600)` returned Justice O'Connor's concurrence, joined by Justices Souter, Ginsburg, and Breyer, in Woodard. Read its discussion of limited procedural safeguards and its rejection of the specific procedural objections. This preexisting authority, not material about the forecast case, informed the legal assessment.

## Web attempts

9. `web.run` search for `Ohio Adult Parole Authority v Woodard 523 U.S. 272 1998 O'Connor minimal procedural safeguards clemency` returned no usable results.
10. A second `web.run` call searched `site.govinfo.gov "523 U. S. 272" "clemency"` and `site.supremecourt.gov "Barefoot" "significant possibility" "stay"`. It also returned no usable results. No result page was opened and no web-derived factual claim was used.

No retrieval sought the present application's disposition, the linked petition's outcome, or later coverage of either. Final schema/completeness validation is a local contract check, not retrieval.
