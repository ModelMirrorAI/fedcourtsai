# Retrieval record

## Local context beyond provisioned case inputs

- Read `metrics/statpack.md`: modern-cert disposition section; paid-segment relist and CVSG cuts; sal-v4 reached-band table. Read the corresponding prior-Term elevated-band aggregates in `metrics/statpack.json`. A local calculation pooled 2017-2024 to 484 / 2,810 = 0.17224199288256228. No individual case rows were retrieved.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: `808f812e9 2026-09-28T12:02:50Z`. This is committed-pack provenance, not corpus freshness.
- No `fedcourts query` or `fedcourts open-events` calls; therefore there are no ranged-corpus transfer lines to report.

## CourtListener MCP

1. `search(type="o", citation="100 U.S. 548", num_results=1, fields=["id", "caseName", "citation", "dateFiled", "absolute_url", "opinions"])`. Returned an unrelated Fifth Circuit case, United States v. Raymond Valas, III, rather than Newton. Discarded; no effect on the prediction.
2. `search(type="o", q='"100 U.S. 548"', case_name="Newton", court="scotus", num_results=2, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])`. Located Newton v. Commissioners, 100 U.S. 548, opinion 90058.
3. `search_document(opinion_id=90058, query="public", snippet_size=500)`. Reviewed excerpts on the public/private distinction, public offices, legislative succession, and contractual construction. Historical background only; no retrieval about this petition's disposition.

## Web attempts

- A batched search for `site.supremecourt.gov Rule 10 considerations governing review certiorari rarely granted misapplication` and `site.loc.gov Dartmouth College Woodward public institution legislature 1819 518` returned no usable content.
- Opening the Supreme Court's rules guidance page, `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`, also returned no usable content. No web material was used.

## Operational tools

Read the prediction prompt, repository instructions, and output schemas. Ran `uv run fedcourts paths --court scotus --docket 73266074 --event evt-petition-disposition --role predictor`. The first invocation failed because the default uv cache directory was read-only; it succeeded with the cache redirected to `/tmp/uv-cache`. Consulted the repository's path and serialization helpers for output handling. These operations supplied no additional case facts. No outcome files, other predictions, or labeling artifacts were read.
