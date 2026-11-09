# Retrieval record

## Local contract and baseline material

Read `.github/prompts/predict.md`, the prediction schema, tooling and flags schema material, and the relevant committed `metrics/statpack.md` sections: modern cert dispositions, prior-Term salience risk sets, relists, CVSG, and amicus counts. Read the case's provisioned event, October 28 snapshot, context, document manifest, questions presented, petition excerpts, decision-below excerpts, appendix excerpts, lower-court docket note, and same-question list. No other cell's output, evaluator outcome, or question-label artifact was read.

Repository/instruction discovery used file listings and checks for applicable AGENTS.md files. `git status --short` was used only to check workspace state. These were not outcome retrievals.

The first `uv run fedcourts paths --court scotus --docket 9026000459 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` attempts failed because uv's default cache was read-only. Subsequent invocations used `UV_CACHE_DIR=/tmp/uv-cache` and `--no-sync`, without installing packages. The paths command was successfully repeated and identified the case and event; the evaluator-only outcome was neither named nor opened. Query help was read, then displayed again in shorter/wider excerpts to inspect its structured filters. These commands returned no additional case evidence.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '456 U.S. 273' --citation '476 U.S. 79' --decided-before 2026 --limit 3`

   Returned no rows. Its coverage note said only 200 SCOTUS rows in scope carried any reporter citation and warned that an empty citation lookup commonly reflects missing metadata, not an absent case. No inference of absent precedent was drawn.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2010s --decided-before 2026 --limit 3`

   Returned Johnson v. Arteaga-Martinez (19-896; three distributions), Hughes v. Northwestern University (19-1401; three distributions and a CVSG), and Dobbs v. Jackson Women's Health Organization (19-1392; 22 distributions). These are generic procedural illustrations, not substantive analogues. Because the filter selects grants, the returned rows were not used to estimate grant odds. No opinion bodies were requested and no own-case outcome was returned.

   `ranged corpus reads: 274 GET(s), 71827456 byte(s)`

Both queries were conservatively restricted to Terms before 2026 despite the cell being forward-mode. There was no open-events lookup.

## Web attempts

The following `web.run` attempts returned no usable source text or reference identifiers in this session; none supplied substantive evidence or an own-case disposition:

- Search batch: `"United States v. Rutledge" "560" "Batson"`; `"Alvarez-Ulloa" "Batson" "de novo"`; `site.supreme.justia.com "Pullman-Standard v. Swint" "291"`.
- Search batch: `site.supremecourt.gov opinions "Pitchford" "2026"`; `"United States v. Alvarez-Ulloa" "784 F.3d 558"`.
- Open attempt: `https://www.supremecourt.gov/opinions/25pdf/24-7351_jiel.pdf`.

No search asked for Grace's disposition, subsequent history, or current docket.

## CourtListener MCP

1. `search(type="o", citation="648 F.3d 555", num_results=2)` returned one match: United States v. Rutledge, Seventh Circuit, August 8, 2011, opinion/cluster 222682. This independently verified case identity and citation, not the full substantive holding.
2. `search_document(opinion_id=222682, query="remand", snippet_size=650)` failed with HTTP 429, reporting 17 seconds until availability. No opinion text was received.
3. `search(type="o", case_name="Pitchford v. Cain", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` returned the May 28, 2026 Supreme Court decision (cluster 10865525, opinion 11332973, official opinion PDF identified) and the January 17, 2025 Fifth Circuit decision, 126 F.4th 422. Further results existed but were not requested. The Supreme Court result confirmed the intervening decision's date; its citation array was empty, so the U.S. Reports citation is attributed to the staged petition.
4. `search_document(opinion_id=11332973, query="opportunity", snippet_size=650)` failed with HTTP 429, reporting 12 seconds until availability. No substantive excerpt was received.
5. `read_document(opinion_id=11332973, chunk_index=0, chunk_size=10500)` failed with HTTP 429, reporting four seconds until availability. No opinion text was received. I stopped upstream text retrieval and relied on the provisioned petition's characterization, explicitly discounted in reasoning.md. No REST fallback was attempted.

## Output validation

The cell is checked with `uv run fedcourts validate data --cell data/cases/scotus/9026000459/events/evt-order-call-for-response-disposition/predictions/codex-baseline/20261109T171058Z`, using a writable uv cache and no-sync mode. This is output-schema validation, not retrieval of a realized outcome.
