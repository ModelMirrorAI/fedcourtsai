# Retrieval log

## Provisioned and repository inputs

Read the prediction contract and output schemas; the briefed-merits event definition; case-level context and October 22, 2026 snapshot; document manifest and question presented; substantive and procedural sections of both staged merits briefs; the United States merits amicus; the Seventh Circuit order and relevant district-court discussion in the petition appendix; and the staged companion metadata and grant order. Repository context beyond the case record comprised the merits and per-Justice portions of `metrics/statpack.md`, their machine-readable rows in `metrics/statpack.json`, the merits-population cautions in `metrics/README.md`, and roster/claim-schema implementation references. Only strictly pre-OT2025 rows entered the numerical anchors. No other prediction, evaluation, realized outcome, or topic-label artifact was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 73275179 --event evt-brief-judgment --role predictor` failed before path resolution because the default uv cache under the runner's home directory was read-only. No corpus transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 73275179 --event evt-brief-judgment --role predictor` succeeded, naming this case and event and explicitly withholding the evaluator-only outcome path. No corpus transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded and described structured filters and transfer reporting. No corpus transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '597 U.S. 1' --decided-before 2025 --limit 3` returned no matching prior. Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. The accompanying note said that only 200 SCOTUS rows in scope carried any reporter citation and that this filter matches a case's own citations, not cases citing it. The empty response was not treated as absence of the authority.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 3` returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889). Stderr: `ranged corpus reads: 72 GET(s), 18874368 byte(s)`. These were unrelated grant records, with no usable merits analogy. The date filter masks a derived docket/Term year rather than guaranteeing every returned date precedes that year; these were not treated as resolved merits priors or used in the probability adjustment. None was this case or its companion.

## Open-web attempts

The web tool returned no visible result payload for each of these three calls; no web content informed the forecast:

1. Combined searches: `site.supremecourt.gov opinions 2023 Rahimi dangerous unusual common use Heller` and `site.supremecourt.gov opinions 2024 Snope Brown Kavanaugh Thomas AR-15 June 2025`.
2. Combined searches: `site.supremecourt.gov "Snope" "KAVANAUGH" "2025"` and `site.supremecourt.gov "United States v. Rahimi" "2024"`.
3. Attempted direct open of an official-site Snope PDF URL, `https://www.supremecourt.gov/opinions/24pdf/24-203_5ie6.pdf`. The response supplied no content and did not establish that this guessed filename was valid.

All subjects were distinct, preexisting authorities, not this case's outcome.

## CourtListener MCP calls

1. `search(type="o", citation="602 U.S. 680", num_results=1)` returned United States v. Rahimi, decided June 21, 2024, docket 22-915, cluster 10600058, combined opinion 11066646. I used the dated primary authority, not its subsequent citation count.
2. `search_document(opinion_id=11066646, query="historical twin", snippet_size=750)` returned four excerpts. I used the majority's discussion at reported pp. 692–693 and 700–701 concerning historical analogy, reasons for regulation, and extent of burdens, keeping it distinct from the separately labeled Thomas dissent excerpts.
3. `search(type="o", case_name="Snope v. Brown", filed_before="2025-06-03", num_results=2)` returned zero matches. I did not retry with an unrestricted search; the staged briefs already set out the relevant separate statements.
4. `search(type="o", citation="670 F.3d 1244", num_results=1)` returned Heller v. District of Columbia, decided October 4, 2011, docket 10-7036, cluster 614652, identifying the separate Kavanaugh dissent as opinion 9484844.
5. `search_document(opinion_id=9484844, query="semi-automatic rifles", snippet_size=450)` found 48 matches and displayed 20 excerpts. The opening dissent passages, reported pp. 1269–1270, explicitly treated semiautomatic rifles as protected under Heller and distinguished fully automatic weapons. This supports a Kavanaugh-specific inference, not a claim that the circuit majority adopted his position.

No live lookup sought Viramontes's disposition, subsequent docket history, argument, or decision coverage. No outcome-revealing material surfaced.

## Output validation

The cell is checked using `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/73275179/events/evt-brief-judgment/predictions/codex-baseline/20261105T015156Z`. This is a local schema/completeness check, not retrieval of case evidence.
