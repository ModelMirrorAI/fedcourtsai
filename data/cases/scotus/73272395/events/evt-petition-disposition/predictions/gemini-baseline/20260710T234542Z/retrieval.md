# Retrieval Log

## Local Statpack Consulted
- `metrics/statpack.md` (checked overall and court-level SCOTUS base rates).

## CourtListener MCP Lookups
- `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id="73272395")`
  - Successfully retrieved the metadata of the docket `James S. Price v. Barbara Lewien, Warden` (No. 25-7287).
  - Showed that the docket was filed on `2026-04-30` and is still open (unresolved, with null `date_cert_granted` and `date_cert_denied` fields).
- Attempted `mcp_courtlistener_search` and `mcp_courtlistener_call_endpoint`, but they failed with:
  - `REDIS_URL is not set; cannot access session store.`

## Google Web Searches
- Query: `circuit split cumulative error ineffective assistance Strickland`
  - Consulted articles and briefs summarizing the division among the federal circuits regarding cumulative prejudice under *Strickland*. Verified that the 1st, 2nd, 3rd, 7th, 9th, and 10th Circuits allow aggregation, while the 4th, 6th, 8th, and 11th Circuits reject it.
- Query: `double jeopardy manifest necessity mistrial jury polling split foreman`
  - Consulted summaries on *Arizona v. Washington* and the Fifth Amendment requirement for deadlocks. Confirmed that jury polling is discretionary and not a federal constitutional requirement for a finding of "manifest necessity."

## Remote Corpus Queries
- Tried querying the local/remote corpus with `fedcourts query` but was unable to execute due to:
  - Absence of local `corpus.db`
  - Lack of a DVC S3 remote URL configuration in the environment for the ranged corpus-query backend.
