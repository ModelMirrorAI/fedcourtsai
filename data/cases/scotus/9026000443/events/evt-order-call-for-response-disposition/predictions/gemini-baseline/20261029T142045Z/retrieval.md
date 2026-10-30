# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-360`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned `scotus/9026000360` (*FedEx Corporation, et al. v. Robert A. Watt, et al.*, No. 26-360), filed `2026-09-16`, originating from `ca6` (`24-5945`), `distributed_for_conference: "2026-11-06"`, `distribution_count: 1`, `disposition: null`, with amicus party `The ERISA Industry Committee`.

2. `uv run fedcourts query --court scotus --docket-number 26-387`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9026000387` (*Bakery, Confectionary, Tobacco Workers and Grain Millers Pension Committee, et al. v. Thomas N. Reichert, et al.*, No. 26-387), filed `2026-09-22`, originating from `ca6` (`24-1442`), `distributed_for_conference: "2026-11-06"`, `distribution_count: 1`, `disposition: null`, with respondent counsel Rachana Ambarish Pathak and amicus party `The ERISA Industry Committee`.

3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Result: Returned 10 recent resolved 2020s SCOTUS rows (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9026000346`, `scotus/9026005347`, `scotus/9526000512`, `scotus/9526000555`, `scotus/9526000556`, `scotus/9526000416`, `scotus/9526000545`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `q=""1055(d)" "actuarial equivalent" "reasonable""`, `fields=["caseName","court","dateFiled","citation","docketNumber"]`, `num_results=10`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 11540 seconds.'}`. Degraded gracefully to provisioned inputs and corpus queries.
