# Retrieval log

## Local sources beyond the provisioned record

- Read `metrics/statpack.md`: modern discretionary-cert overview,
  originating-court cuts, paid-segment relist and CVSG cuts, and the `sal-v4`
  per-Term segment table. Only Terms 2017-2024 entered the numerical anchor.
- Read `metrics/statpack.json` aggregate structure and Term segments. Used
  `jq` to pool the `baseline` segment's `prefix_est_grant_rate` multiplied by
  `prefix_weighted_resolved` over 2017-2024, divided by the pooled denominator:
  593 / 11,580 = 0.05120898100172712.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify artifact
  vintage: `55121cdb8 2026-09-14T11:02:00Z`.
- Read task/schema files and the paths/serialization helpers solely for the
  artifact contract. Ran `uv run fedcourts paths --court scotus --docket
  73369987 --event evt-petition-disposition --role predictor`. Its first
  attempt failed on the default cache's read-only filesystem; rerunning with
  a writable temporary cache succeeded.
- No `fedcourts query`, `open-events`, corpus-pull, or corpus-stats lookup was
  used. There are no ranged corpus transfer lines to report.

## Generic web attempts

All returned no usable source text or search results to this session, and
none informed the forecast:

1. Search: `site.supremecourt.gov Rule 10 considerations governing review
   certiorari erroneous factual findings misapplication properly stated rule law`.
2. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
3. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
4. Repeat open of that rules-guidance page.
5. Find `erroneous factual` in
   `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.

No request named this case or sought its outcome.

## CourtListener MCP

1. `search(type="o", citation="584 U.S. 148", num_results=1,
   fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])`.
   Returned Sessions v. Dimaya, decided April 17, 2018; opinion ID 9225905,
   cluster path `/opinion/9231105/sessions-v-dimaya/`. Used to verify the
   identity of the precedent invoked in the petition, not this case's history.
2. `search_document(opinion_id=9225905, query="deportation", snippet_size=350)`.
   Returned thirteen excerpts. Used the discussion contrasting the
   plurality's deportation-gravity rationale and Justice Gorsuch's broader
   civil-sanctions rationale. Did not treat dissenting or concurring material
   in the combined document as a majority holding.

No target-case disposition, later history, other prediction, or evaluator
artifact was retrieved.
