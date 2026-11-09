# Retrieval record

## Provisioned inputs and local reference material

Read the prediction contract, prediction schema, event definition, `record/context.json`, `record/snapshots/2026-11-09.json`, document manifest, questions presented, lower-court docket helper, and relevant sections of the petition, opposition, reply and decision below. Read the paid-segment and prior-Term sections of `metrics/statpack.md` and corresponding `metrics/statpack.json` data. The exact local calculation reproduced 246/712 for the frozen band anchor and 726/3510 for the pooled relist-1-and-up population. No other cell's prediction, evaluation, realized outcome, or QP-topic artifact was read.

## CLI setup and diagnostics

- `uv run fedcourts paths --court scotus --docket 73500225 --event evt-order-relist-disposition --role predictor` initially failed because the default uv cache directory was read-only. No dependencies were installed.
- Reissued that paths command with `UV_CACHE_DIR=/tmp/uv-cache`; it succeeded and identified the expected event path. The evaluator-only outcome was neither named nor opened.
- Read `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` before querying; a second invocation displayed the middle portion of the same help. These were usage inspections, not corpus searches.

## Corpus lookups

All commands used the same temporary uv-cache override. This is a forward cell; the first lookup's optional Term mask was an additional conservative filter, not a replay clock for this cell.

1. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2025 --limit 5`
   - `ranged corpus reads: 70 GET(s), 18284544 byte(s)`
   - Returned Monsanto v. Salas, Monsanto v. Johnson, Petersen v. Doe, Chaney v. United States, and Smith v. Scott. Their docket-number Terms precede 2025, although the visible grant dates extend into 2026; the CLI's bare-year mask is a Term/year filter, not an exact disposition-date ceiling. None is the target petition. Used only to inspect examples of GVRs and heterogeneous distribution counts, not to estimate a conditional rate or suggest topic similarity.
2. `uv run fedcourts query --court scotus --docket-number 25-1206 --limit 1`
   - `ranged corpus reads: 16 GET(s), 4194304 byte(s)`
   - Returned Maryland's separate Moore v. Kipke cross-petition, dismissed August 13, 2026, distribution count zero. This matches the opposition's explanation that Maryland abandoned its private-property consent challenge after Wolford. This is not No. 25-1324's disposition.
3. `uv run fedcourts query --court scotus --docket-number 23-910 --limit 1`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned Antonyuk v. James, GVR on July 2, 2024, with two distributions. Used as a procedural example of Second Amendment reconsideration without plenary review. No opinion body was requested or supplied.
4. `uv run fedcourts query --court scotus --citation '145 S. Ct. 1900' --limit 2`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - No results. The CLI warned that only 200 in-scope rows carried reporter citations and that this filter matches a case's own citations. Treated as a coverage limitation, not an absence of the cited decision; did not retry the sparse corpus filter.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="Wolford v. Lopez", num_results=5)` returned one opinion cluster, 10880241, with combined opinion 11347760, decided June 25, 2026, Supreme Court No. 24-1046. This is intervening precedent, not the target case.
2. `read_document(opinion_id=11347760, chunk_index=0, chunk_size=12500)` returned the opening text/syllabus. It confirms the decision concerns Hawaii's affirmative-consent default on private property open to the public and reversed and remanded. I did not read the entire 202,867-character combined opinion.
3. `search(type="o", court="scotus", case_name="Antonyuk", citation="145 S. Ct. 1900", num_results=3)` returned zero results. The opposition's account of that denial remains a provisioned party representation, not an independently verified MCP result.
4. `search_document(opinion_id=11347760, query="sensitive", snippet_size=420)` returned three passages. These distinguish sensitive-place restrictions from the private-property default and retain the familiar reference to schools and government buildings. Used to check that Wolford does not itself dispose of the entire sensitive-place question.

## Web attempts

- Searched for `site.supremecourt.gov Wolford Lopez 24-1046 question presented certiorari` through the web tool. The tool returned no usable results/content.
- Attempted to open the Supreme Court's public docket page for No. 24-1046 through the web tool. The tool again returned no usable content. CourtListener supplied the substantive verification instead.

No search sought this petition's disposition, current docket, subsequent history, or coverage of its resolution. No external result revealed its outcome. No future lead-case outcome is assumed.

## Completion check

The cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/73500225/events/evt-order-relist-disposition/predictions/codex-baseline/20261109T212928Z`. This is local schema/completeness validation, not outcome retrieval.
