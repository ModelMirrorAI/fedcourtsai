# Retrieval log

## Local inputs and aggregate context

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction/tooling/flags schemas. Used `fedcourts paths --court scotus --docket 73363395 --event evt-petition-disposition --role predictor` to resolve paths; its first invocation failed because the default uv cache was read-only, and a temporary-cache invocation succeeded.
- Read this event's `event.yaml`, the case-level `record/context.json`, `record/snapshots/2026-09-16.json`, `record/documents/documents.json`, `questions-presented.txt`, and selected sections of `petition.txt`, particularly its questions, procedural account, factual theory, and reasons for granting review.
- Read the modern-cert, origin, paid-segment relist/CVSG, and salience tables in `metrics/statpack.md`; inspected matching Term and coverage fields in `metrics/statpack.json`. Used jq to pool 2017–2024 sal-v4 baseline reached rates: numerator 593, weighted denominator 11,580, rate 0.05120898100172712.
- `git log -1 --format='%h %cI %s' -- metrics/statpack.json` established the aggregate artifact's local commit vintage, September 14, 2026. This is not a remote-corpus freshness check.
- No `fedcourts query` or `open-events` retrieval was made; there are no ranged-corpus transfer lines to report. No other predictor output or realized-outcome artifact was read.

## Web attempts

Three web calls returned no usable results or source text:

1. Searches: `site.supremecourt.gov Rule 10 petition certiorari erroneous factual findings misapplication properly stated rule`; `site.law.cornell.edu constitution seventh amendment civil jury trial states not incorporated`.
2. Searches: `site.supremecourt.gov "Rule 10" "erroneous factual findings"`; `site.constitution.congress.gov "Seventh Amendment" "not" "states"`.
3. Attempted open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.

None concerned the target case's outcome, and none contributed substantive retrieved evidence.

## CourtListener MCP

1. `search(type="o", citation="92 U.S. 90", num_results=1)` returned an unrelated Cruz v. Bristol Myers Squibb opinion from 2014, rather than the intended precedent. Its snippet was not used; no further results were fetched.
2. `search(type="o", court="scotus", case_name="Walker v. Sauvinet", num_results=2)` returned Walker v. Sauvinet, 92 U.S. 90, dated April 24, 1876, opinion 89245.
3. `read_document(opinion_id=89245)` supplied the full Walker opinion. Used its discussion at pages 92–93 of the federal jury guarantee and Fourteenth Amendment due process in state civil proceedings. No target-case search, docket lookup, or subsequent-history retrieval was performed.
