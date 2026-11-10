# Retrieval Log (`scotus/9026000071`, `evt-order-relist-disposition`)

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-828`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 open row (`scotus/73279966`, *The GEO Group, Inc., a Florida Corporation v. Ugochukwu Nwauzor, et al.*, docket number `25-828`, `cvsg_date: "2026-05-18"`, `distributed_for_conference: "2026-11-06"`, `distribution_count: 2`, `disposition: null` as of `last_live_polled: "2026-11-09"`).

## CourtListener MCP and Web Searches

- No CourtListener MCP calls or external web searches were made; the provisioned documents (`petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `decision-below.txt`, `lower-court-docket.txt`, `questions-presented.txt`), the provisioned snapshot (`2026-11-09.json`), and the corpus lookup of companion petition No. 25-828 provided a complete record.
