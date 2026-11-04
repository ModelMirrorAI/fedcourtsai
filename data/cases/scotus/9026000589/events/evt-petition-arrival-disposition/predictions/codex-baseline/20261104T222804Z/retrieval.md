# Retrieval record

## Local reference material

Read the prediction prompt, prediction/tooling/flags schemas, the event, context, dated snapshot, document manifest, questions presented, petition body and selected appendix material, supplied decision below and lower-court docket summary, and same-question list. Consulted `metrics/statpack.md` modern-cert, originating-circuit, relist, CVSG, and sal-v6 band sections and the corresponding prior-Term federal risk-set fields in `metrics/statpack.json`. No material under `data/qp-topics/`, outcomes, other cells' predictions, or evaluations was read.

## Corpus and CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000589 --event evt-petition-arrival-disposition --role predictor` failed before running: the default uv cache at `/home/codexcell/.cache/uv` was read-only. No case information returned.
2. `UV_NO_CACHE=1 uv run fedcourts paths --court scotus --docket 9026000589 --event evt-petition-arrival-disposition --role predictor` succeeded, showing the case, corpus and event paths and withholding the evaluator-only outcome. Repeated once later with the same result. No outcome was opened.
3. `UV_NO_CACHE=1 uv run fedcourts query --help` succeeded. Repeated once with the output limited to the first 65 lines; both were help reads, not corpus retrievals.
4. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition granted --era roberts --decided-before 2026 --limit 3` was rejected because `roberts` is not a decade-era token. The diagnostic supplied valid vocabulary. No prior rows or transfer line returned.
5. Corrected query: `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` returned three prior petition rows: *U.S. DOGE Service v. U.S. District Court*, No. 25-1103; *Berry v. United States*, No. 25-7026; and *Blanche v. Ozurumba*, No. 25-1343. All recorded October 13, 2026 grants. These are unrelated petitions, not a representative sample or a basis for estimating this case's odds. The 2026 clock is the docket-Term bar, not a January 1 decision-date bar; this cell is forward.

   `ranged corpus reads: 32 GET(s), 8388608 byte(s)`

6. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --docket-number 26-210 --limit 1` checked the separate *Trump v. Thakur* petition cited in this petition's footnote 3. Returned case `scotus/9026000210`: pending, docketed August 19, 2026, last polled November 2, one distribution for the November 13 conference, no recorded grant, denial, or CVSG. Its questions and briefs were not retrieved. This supplies limited possible alternative-vehicle context, not proof of an identical question or a Court-directed link.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

No `--full` hydration or `open-events` call was used. All uv retries disabled caching; no packages were installed.

## Web attempts

The following `web.run` calls returned no usable output, so they supplied no facts:

1. Two search queries: `site.supremecourt.gov "Department of Education" "California" "24A910" opinion` and `site.supremecourt.gov "NIH" "American Public Health" "24A884"`. The latter docket-number search was an unsuccessful guess, not a verified identifier.
2. Two search queries: `site.supremecourt.gov/opinions/24pdf "24A910"` and `site.supremecourt.gov/opinions/24pdf "American Public Health"`.
3. Attempted opening of `https://www.supremecourt.gov/opinions/24pdf/24a910_f2bh.pdf`. No usable document returned; this guessed filename was not treated as a source.

None sought the target petition's outcome, subsequent history, or decision coverage.

## CourtListener MCP calls

1. `search(type="o", citation="604 U.S. 650", court="scotus", num_results=1)` returned *Department of Education v. California*, decided April 4, 2025; cluster 10776858, opinion 11243445, docket 24A910. Query ID `b1c5dc09`.
2. `search(type="o", citation="606 U.S. 998", court="scotus", num_results=1)` returned zero results. Query ID `435d4039`. The petition's NIH citation was not independently verified.
3. `read_document(opinion_id=11243445, chunk_index=0, chunk_size=9000)` returned the opening chunk of the official preliminary-print opinion, including the per curiam stay reasoning, its jurisdictional analysis, and the beginning of the separate writings. Used only as general, earlier legal context.
4. `search(type="o", court="scotus", q='"National Institutes" "American Public"', filed_before="2026-01-01", num_results=2)` reported four matches and returned *Morse v. Frederick* and *Murthy v. Missouri*. Query ID `cfbe0ed7`. Both were irrelevant and ignored; no full documents were read.
5. `search(type="o", court="scotus", case_name="National Institutes of Health v. American Public Health", filed_after="2025-01-01", filed_before="2026-01-01", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` returned zero results. Query ID `c9695d7c`. Stopped rather than treating a coverage gap as absence of the precedent.

No CourtListener call searched the target Supreme Court case. The supplied lower-court judgment and docket summary were read locally, not fetched anew.
