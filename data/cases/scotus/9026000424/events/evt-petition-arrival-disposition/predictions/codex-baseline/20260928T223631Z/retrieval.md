# Retrieval record

- Read the committed `metrics/statpack.md`: modern cert disposition and
  originating-circuit sections, paid-segment relist and CVSG cuts, and the
  per-Term sal-v4 segment table. Read `metrics/statpack.json` for exact baseline
  risk-set rates and denominators; pooled only the shown Terms 2017–2025.
  Used `git log -1 --format='%h %cI' -- metrics/statpack.json` to identify the
  artifact revision, `808f812e9`, committed September 28, 2026 at 12:02:50 UTC.
- CourtListener MCP `search`: `type=o`, `court=ca4`,
  `docket_number=26-1130`, `filed_before=2026-09-29`, `num_results=5`.
  Returned zero results. This sought only the lower-court opinion, not the
  Supreme Court petition's disposition.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing
  review certiorari judicial discretion`. No usable result was returned.
- Two web opens attempted for the Supreme Court's official rules-guidance
  page, `/filingandrules/rules_guidance.aspx`. Neither returned usable content;
  no external rule text informed the prediction.
- Ran `uv run fedcourts paths --court scotus --docket 9026000424 --event
  evt-petition-arrival-disposition --role predictor`. The first attempt failed
  because the default uv cache was read-only; retrying with a writable temporary
  cache succeeded. This resolves paths, not substantive corpus facts.
- No `fedcourts query` or `open-events` call was made, so there is no ranged
  corpus-read transfer line. No live Supreme Court docket, case-outcome search,
  evaluator artifact, or other predictor's output was consulted.
