# Retrieval log

## Local inputs and aggregate context

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flags schemas; inspected path/serialization helper names only for output conventions.
- Read this cell's event definition, `record/context.json`, `record/snapshots/2025-10-15.json`, document manifest, questions presented, and relevant sections of the petition, its appended lower-court opinion, and the brief in opposition.
- Ran `uv run fedcourts paths --court scotus --docket 73274796 --event evt-order-cvsg-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; the retry with a writable temporary cache succeeded. No outcome file was opened.
- Read `metrics/statpack.md`: modern cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 band table. Read `metrics/statpack.json` to compute the exact high-band reached pool over the table's displayed prior Terms 2017–2024: weighted denominator 898, grant-equivalents 314, rate 0.34966592427616927. Later-Term rows were not used for the anchor. No live corpus freshness claim is made.
- No `fedcourts query` or `open-events` call was made, so there is no ranged-corpus transfer line to report.

## Web searches

1. `site.supremecourt.gov opinions 2025 Catholic Charities Bureau Wisconsin 24-154` — no usable output returned.
2. `Catholic Charities Bureau Wisconsin Supreme Court June 5 2025 opinion` — no usable output returned.

Both queries concern a different, pre-snapshot precedent, not the target petition. No web result informed the forecast.

## CourtListener MCP

1. `search(type="o", case_name="Catholic Charities Bureau", court="scotus", filed_before="2025-10-15", num_results=3)` — returned three versions of the June 5, 2025 Supreme Court decision, docket 24-154, reported at 605 U.S. 238. No search for citing cases or subsequent history was made.
2. `read_document(opinion_id=11066502, chunk_index=0, chunk_size=12000)` — read the opening chunk, containing the syllabus and opening opinion discussion of theological classifications, denominational neutrality, and strict scrutiny. This was general legal context already cited in the parties' pre-decision briefs. I did not read this precedent's later citing decisions.

No current target-docket lookup, target disposition, government brief, subsequent target history, or another predictor's output was retrieved.
