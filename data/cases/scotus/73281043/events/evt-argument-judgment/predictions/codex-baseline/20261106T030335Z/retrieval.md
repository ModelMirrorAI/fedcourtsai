# Retrieval and consulted context

## Baseline and local references

Read the provisioned November 5, 2026 snapshot, context, document manifest, questions presented, merits briefs, United States merits amicus, petitioner's merits reply, argument transcript, argument features, and the petition appendix's opinion below. Consulted the prediction contract and schemas, `metrics/statpack.md` (merits and complete-lineup vote sections), and the merits-baseline discussion in `metrics/README.md`. Local calculations pooled only grant Terms 2015–2024 with published rows and vote decision Terms 2020–2024. No own-case subsequent docket or outcome, other-cell prediction, evaluation, or topic-label artifact was read.

The path helper was attempted once as `uv run fedcourts paths --court scotus --docket 73281043 --event evt-argument-judgment --role predictor`; it failed because the default uv cache directory was read-only. The same command with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and was repeated once successfully. It resolved the expected event and case paths and did not expose an outcome path. No packages were installed.

## Corpus calls

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — inspected the structured filters; later repeated with output restricted to the relevant help lines. Both succeeded. No transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '545 U.S. 353' --limit 1` — no matching prior returned. The CLI warned that only 200 SCOTUS rows in scope carried reporter citations and that an empty citation result reflects sparse coverage, not absence of the precedent.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 3` — returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889), all without opinion bodies or usable parsed merits judgments in the returned rows. No substantive analogy or probability adjustment rests on them. The year filter is not an exact decision-date filter; returned grant dates included 2026. This is a forward cell, and none was this case.
   - `ranged corpus reads: 73 GET(s), 19136512 byte(s)`

`DECIDED_BEFORE` was unset, consistent with provisioned forward mode. The explicit filter on the second query was a voluntary restriction, not a replay clock. No broad full-opinion corpus hydration was attempted.

## CourtListener MCP calls

1. `search(type="o", citation="545 U.S. 353", court="scotus", num_results=1)` — found Dodd v. United States, decided June 20, 2005; cluster 799979, lead opinion 9843320. This was a historical precedent lookup, not a lookup of Johnson's case.
2. `read_document(opinion_id=9843320)` — returned Dodd's majority opinion. Its discussion at 545 U.S. 359–360 supports only the general analogy that courts enforce AEDPA's textual successive-motion restrictions despite harsh consequences. Its limitations-period holding does not resolve this case's availability question.

## Web attempts

1. `web.run` search queries: `site.law.cornell.edu/uscode/text/28/2244` and `site.supremecourt.gov Dodd United States 545 353 2005 previously unavailable` — the tool returned no usable output or source text.
2. `web.run` open of `https://www.supremecourt.gov/opinions/22pdf/21-857_4357.pdf` — attempted to consult the historical Jones v. Hendrix opinion; the tool returned no usable output or source text. No information from this attempt informed the forecast.

Neither web attempt sought the disposition or subsequent history of Guerrero v. Johnson. No outcome-revealing material surfaced.
