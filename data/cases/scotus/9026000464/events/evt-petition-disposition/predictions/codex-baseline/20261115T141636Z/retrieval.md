# Retrieval record

## Provisioned inputs and local context

Read the prediction contract, prediction schema, tooling schema, event definition, `record/context.json`, and `record/snapshots/2026-11-15.json`. Consulted the document manifest, questions presented, petition, complete appellate opinion, lower-court docket summary, and selected appendix passages, especially the Board's discussion of alternate theories and conclusion at A-72–A-75. Read the committed `metrics/statpack.md` modern-cert, originating-circuit, paid-segment relist/CVSG/amicus, and sal-v8 prior-Term tables. Did not read another prediction, an evaluation, outcome file, or topic-labeling artifact.

## Corpus and CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000464 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; it returned the case/event paths and explicitly withheld the evaluator-only outcome path. No outcome was opened.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` read before querying; a later repeat piped to `tail -68` inspected the remaining options. Help calls are not corpus retrievals and printed no transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 3` failed validation: `modern` is not an era token. No corpus transfer line was printed. The error supplied the decade-token vocabulary.
4. Corrected call: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`.

   Transfer: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`.

   Returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce, Warden (25-7555), each denied November 9, 2026. The Term filter uses the derived docket year, so it can return dispositions in the following calendar year. All dates were before this forward prediction. These are generic denial-conditioned priors, not subject-matched comparators; I did not use this selected sample to estimate a grant probability or infer anything about the target's disposition. No opinion bodies were requested.

## CourtListener MCP

1. `search(type="o", citation="153 F.3d 1338", court="cafc", num_results=2)` returned one historical opinion: H.B. Mac, Inc. v. United States, filed August 19, 1998; opinion/cluster 757546, docket 97-5054.
2. `search_document(opinion_id=757546, query="bright line", snippet_size=1600)` returned one passage around reporter pages 1346–47. It states that the reasonableness of reliance on distant borings depends on geology and topography rather than a bright-line rule. Used to check the precedent the provisioned opinion applies, not to look up the target's later history.

## General-law web attempts

1. One `web.run` call attempted two general searches: `site.supremecourt.gov rules Rule 10 writ certiorari rarely granted erroneous factual findings misapplication properly stated rule law` and `site.acquisition.gov FAR 52.236-2 Differing Site Conditions`. The tool returned no usable result payload. No search snippets or retrieved text informed the forecast.
2. One `web.run` call attempted to open the Supreme Court's `2023RulesoftheCourt.pdf` under its official `filingandrules` directory. Again no usable result payload was returned. No document content was relied on.

No search named this target petition, sought its disposition or later history, or sought anyone else's forecast. No external forecast or outcome-revealing material surfaced.

## Output checks

The cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000464/events/evt-petition-disposition/predictions/codex-baseline/20261115T141636Z`. This is a local schema/completeness check, not retrieval of case material.
