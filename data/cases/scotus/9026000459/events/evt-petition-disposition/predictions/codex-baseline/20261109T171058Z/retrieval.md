# Retrieval record

Provisioned inputs: event definition; `record/context.json`; `record/snapshots/2026-11-09.json`; document manifest; questions presented; selected petition and appendix passages; decision below, particularly its Batson analysis; lower-court docket summary; and empty same-question list. These are the supplied baseline, not live retrieval. No own-case outcome, subsequent history, evaluator file, other predictor output, or topic-label artifact was read.

## Local contract and corpus tooling

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; checked applicable instruction-file locations.
- `uv run fedcourts paths --court scotus --docket 9026000459 --event evt-petition-disposition --role predictor`: failed before retrieval because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`; returned the case, corpus, and event paths. No outcome file was opened.
- Read committed `metrics/statpack.md`, particularly paid-segment relist, CVSG, zero-amicus, and sal-v8 reached-band statistics. The frozen context anchor, not the current Term's outcome table, provides the calibration baseline.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`: succeeded. Repeated with `COLUMNS=200` and `head -55` to inspect help with a wider layout. Neither help call performed a corpus lookup or printed a transfer line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition gvr --decided-before 2026 --limit 4`: refused because `modern` is not an allowed decade token. No transfer line was printed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2026 --limit 4`: succeeded. Returned Burford German Funding (25-1269), Roofing Designs (25-1367), Silva Ochoa (25-7569), and Garcia v. Hobbs (25-901), all unrelated GVRs with two or three recorded distributions. No opinion bodies were requested; these are route examples, not substantive analogues or a representative sample.
  - Exact stderr: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`.

## Web attempts

1. One `web.run` search batch with three queries: `site.supremecourt.gov "Pitchford" "2026" "Cain"`; `site.ca9.uscourts.gov "Alvarez-Ulloa" "565"`; and `site.ca7.uscourts.gov "Carter" "Wauwatosa" "2024" "Batson"`. The tool returned no visible results or source identifiers. Nothing from this attempt informed the forecast.
2. One `web.run` open attempt for the official Pitchford opinion, `https://www.supremecourt.gov/opinions/25pdf/24-7351_jiel.pdf`. The tool returned no visible text or source identifier. Relied instead on the Court opinion retrieved through MCP.

## CourtListener MCP

1. `search(type="o", case_name="Pitchford v. Cain", court="scotus", filed_before="2026-11-09", num_results=3)`: returned one precedent, cluster 10865525, decided May 28, 2026, docket 24-7351, opinion 11332973. This is the precedent invoked by the petition, not the target petition's disposition.
2. `read_document(opinion_id=11332973, chunk_index=0, chunk_size=12000)`: read the syllabus and opening majority discussion. Confirmed the omitted Batson third step, insufficient opportunity to rebut, waiver issue, reversal and remand, and the opinion lineup. The retrieved precedent predates the snapshot.
3. `search(type="o", citation="784 F.3d 558", num_results=1)`: returned Alvarez-Ulloa, April 21, 2015, opinion 2795325; an additional search hit was available but not requested.
4. `search_document(opinion_id=2795325, query="de novo", snippet_size=1300)`: returned five excerpts. Confirmed the Ninth Circuit's permission for an appellate discrimination determination after a deficient Batson analysis, with remand as an alternative.
5. `search(type="o", citation="648 F.3d 555", num_results=1)`: returned Rutledge, August 8, 2011, opinion 222682.
6. `search_document(opinion_id=222682, query="evidentiary gap", snippet_size=1100)`: returned the Seventh Circuit's requirement to remand for missing step-three credibility findings. Used as corroboration of the other side of the asserted split.

No MCP call failed, no direct CourtListener REST fallback was attempted, and no own-case live docket or disposition query was made.
