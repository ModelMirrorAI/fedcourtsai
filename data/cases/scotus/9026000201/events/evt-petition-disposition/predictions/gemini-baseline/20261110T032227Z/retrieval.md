# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1325`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: `scotus/73500226` (*Oklahoma v. United States*, No. 25-1325, originating from CA6, filed 2026-05-29, distributed for conference 2026-10-09, `distribution_count: 1`, `disposition: null`).
2. `uv run fedcourts query --court scotus --docket-number 24-429`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: `scotus/72484140` (*Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.*, No. 24-429, originating from CA5 No. 23-10520, granted and disposed of as `gvr` on 2025-06-30).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   - Result: 5 recent 2020s-era granted SCOTUS rows (`scotus/9526000560`, `scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`), including Solicitor General petition `26-204` (*Department of Justice v. McNutt*, originating from CA5, granted 2026-10-19 after 2 distributions).
4. `uv run fedcourts query --court scotus --docket-number 24-433`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: `scotus/72484144` (*Horseracing Integrity and Safety Authority, Inc. v. National Horsemen's Benevolent and Protective Association*, No. 24-433, companion petition from CA5 No. 23-10520, disposed of as `gvr` on 2025-06-30).
5. `uv run fedcourts query --court scotus --docket-number 24A287`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: `scotus/69315289` (*Horseracing Integrity and Safety Authority, Inc. v. National Horsemen's Benevolent and Protective Association*, No. 24A287, stay application from CA5 No. 23-10520, `granted` on 2024-10-28).

## CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="Walmsley", filed_after="2025-07-01")`
   - Result: `count: 0` (confirmed the Eighth Circuit has not issued a post-remand opinion in *Walmsley v. FTC* following the June 2025 GVR).

## Web Searches

- None attempted.
