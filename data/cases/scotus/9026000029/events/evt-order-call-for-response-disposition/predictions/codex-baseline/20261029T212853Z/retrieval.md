# Retrieval log

No search or lookup sought this petition's outcome or subsequent docket. The cell is forward mode; I nevertheless limited corpus priors to those resolved before September 2, 2026.

## Local inputs and setup

- Read `AGENTS.md`, `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; used schema/model-name inspection only for output construction and validation.
- Read this cell's event, context, `record/snapshots/2026-09-02.json`, document manifest, questions presented, and relevant portions of `petition.txt` and `appendix.txt`. The appendix contains NUL characters, so some excerpts were displayed with NULs removed; no input was modified.
- `uv run fedcourts paths --court scotus --docket 9026000029 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` initially failed because the default uv cache was read-only. Retried both with `UV_CACHE_DIR=/tmp/uv-cache`; both succeeded. The paths command identified the case and event, not an outcome file's contents.
- Consulted the committed `metrics/statpack.md`: modern-cert disposition, paid relist, paid CVSG, paid amicus, and sal-v4 per-Term reached-band tables. Inspected `metrics/statpack.json` top-level metadata keys; no generated-at or corpus-freshness value was available. Pooled the nine strictly prior rendered baseline reached rows using their displayed rounded percentages: approximately 5.1068%, weighted n = 12,913. These are supplied-pack figures, not a fresh live-corpus measurement.

## Corpus calls

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026-09-02 --limit 4`
   - Refused: `Unknown era 'modern'`; help explained that the vocabulary uses decade tokens. No read-stat line was printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-09-02 --limit 4`
   - Succeeded; explicitly reported the September 2, 2026 cutoff.
   - `ranged corpus reads: 45 GET(s), 11730944 byte(s)`
   - Returned National Park Service v. National Trust (26A203), Trump v. California (26A124), Kenneth J. Jouppi v. Alaska (25-246), and Cutberto Viramontes v. Cook County (25-238).
   - The first two were interim applications, not cert comparators. The latter two showed three and twenty-two distributions. No opinion bodies were requested. This small selected set was not used to estimate a grant rate.

## Web attempts

1. Search query: `site.supremecourt.gov opinions Ford Motor Montana 2021 specific jurisdiction Bristol Myers Squibb 2017`. Tool returned no usable results or text.
2. Opened the official Supreme Court Ford opinion PDF at the `opinions/20pdf/19-368_febh.pdf` path. Tool returned no usable document text. The primary opinion was instead checked through CourtListener below.

## CourtListener MCP calls

1. `search(type="o", citation="592 U.S. 351", num_results=1)` returned Ford Motor Co. v. Montana Eighth Judicial District, March 25, 2021, cluster 4867543, opinion 4671322.
2. `search_document(opinion_id=4671322, query="resident-plaintiffs", snippet_size=650)` returned two excerpts contrasting Ford's in-state injuries and residents with Bristol-Myers' lack of a suit-specific connection. Used only this older general precedent.
3. `search(type="o", citation="420 U.S. 469", num_results=1)` returned an unrelated citation match, United States v. Eddie Burroughs, a 2016 D.C. Circuit case. Not used substantively; narrowed the search rather than assuming the citation matched.
4. `search(type="o", court="scotus", case_name="Cox Broadcasting v. Cohn", num_results=1)` returned Cox Broadcasting Corp. v. Cohn, March 3, 1975, cluster 109207, including majority opinion 9426016.
5. `search_document(opinion_id=9426016, query="fourth", snippet_size=1700)` returned no matches.
6. `search_document(opinion_id=9426016, query="seriously erode", snippet_size=1000)` returned the majority's limited finality exception for certain finally resolved federal questions despite pending state proceedings. Used to assess vehicle risk without treating interlocutory review as categorically unavailable.

No other corpus, CourtListener, or web retrieval was attempted. Validation checks schemas and output completeness, not the target's outcome.
