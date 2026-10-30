# Retrieval Log

## Corpus Queries (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73500275" --event "evt-order-call-for-response-disposition" --role predictor`
   - Resolved case, corpus, and event paths for `scotus/73500275`.

2. `uv run fedcourts query --help`
   - Inspected CLI filter flags for `fedcourts query`.

3. `uv run fedcourts query --court scotus --docket-number 25-944`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned the open SCOTUS docket row for `scotus/73280982` (*Robinhood Markets, Inc., et al. v. Vinod Sodha, et al.*, No. 25-944), showing `cvsg_date: "2026-06-01"`, `distributed_for_conference: "2026-11-06"`, `distribution_count: 2`.

4. `uv run fedcourts query --court scotus --docket-number 25-1376`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned the open SCOTUS docket row for `scotus/73500275` (*ON24, Inc., et al. v. Leadersel Innotech ESG*, No. 25-1376), showing `distributed_for_conference: "2026-11-06"`, `distribution_count: 2`, `disposition: null`.

5. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 10 recent resolved 2020s SCOTUS priors.

6. `uv run fedcourts query --court scotus --originating-court ca9 --era 2020s --disposition denied --limit 5`
   - Failed with CLI usage error (`No such option: --originating-court`).

7. `uv run fedcourts query --court scotus --originating-court ca9 --era 2020s --disposition granted --limit 5`
   - Failed with CLI usage error (`No such option: --originating-court`).

8. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned 5 recent 2020s SCOTUS GVR priors (including OT 2026 long-conference GVRs).

9. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent 2020s SCOTUS granted priors.

## CourtListener MCP Calls

1. `mcp_courtlistener_search(case_name="Robinhood Markets Sodha", type="o")`
   - Returned HTTP 429 rate-limit error (`Rate limit exceeded: 1400/day. Expected available in 13066 seconds.`).

2. `mcp_courtlistener_search(case_name="Sodha Golubowski", type="o")`
   - Returned HTTP 429 rate-limit error (`Rate limit exceeded: 1400/day. Expected available in 13066 seconds.`).

## Web Searches (`google_web_search`)

1. `google_web_search(query='"ON24" "Leadersel Innotech ESG" Supreme Court 25-1376')`
   - Confirmed `25-1376` is pending, with Brief in Opposition filed September 21, 2026, Reply Brief filed October 6, 2026, and distributed for the November 6, 2026 conference.

2. `google_web_search(query='"Robinhood Markets" "Sodha" Supreme Court 25-944')`
   - Confirmed `25-944` (*Robinhood Markets, Inc. v. Sodha*) is pending and that on October 7, 2026, the Solicitor General filed an invited brief recommending that the Court grant certiorari on Question 1 (Section 11 misleading omissions).

3. `google_web_search(query='"Robinhood Markets" "Sodha" Solicitor General brief "25-944" "ON24"')`
   - Retrieved summary of the Solicitor General's October 7, 2026 brief in `25-944`, which recommended granting review on Question 1 (with a rewrite) in *Robinhood*, denying review on Question 2 (Item 303), and treating *Robinhood* as the superior vehicle over *ON24*.

4. `google_web_search(query='"25-1376" "Robinhood" "Solicitor General" OR "hold"')`
   - Retrieved additional context on the relationship between `25-944` and `25-1376`, including Robinhood's October 20, 2026 supplemental brief and the hold request in *ON24*, with both cases distributed for the November 6, 2026 conference.

5. `google_web_search(query='"ON24" "Leadersel" "Brief in Opposition" OR "Reply" "25-1376"')`
   - Retrieved summary of respondent Leadersel Innotech ESG's September 21, 2026 Brief in Opposition and petitioners' October 6, 2026 Reply Brief in `25-1376`.
