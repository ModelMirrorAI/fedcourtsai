# Retrieval Log

## Corpus Lookups
* Attempted `uv run fedcourts query --topic "Other Statutory Actions" --court scotus --limit 5 --corpus-backend ranged`. This failed because the environment lacked the `corpus_remote_url` setting required for ranged reads.
* Read `metrics/statpack.md` to check SCOTUS disposition base rates, specifically relying on the background knowledge that SCOTUS reverses >60% of cases it reviews on the merits, driving the GVR probability for a held petition.

## CourtListener Lookups
* `mcp_courtlistener_search` with query `q="Salazar v. Paramount Global" type=d`: Returned results showing *Salazar v. Paramount Global* (23-5748) at the 6th Circuit, confirming the underlying litigation for the pending SCOTUS case.
* `mcp_courtlistener_search` with query `court=scotus docket_number="25-459" type=d`: No results (docket not yet indexed by CourtListener).
* `mcp_courtlistener_search` with query `court=scotus q="Salazar Paramount" type=d`: No results.

No retrieval beyond the provisioned inputs and these basic tooling checks.