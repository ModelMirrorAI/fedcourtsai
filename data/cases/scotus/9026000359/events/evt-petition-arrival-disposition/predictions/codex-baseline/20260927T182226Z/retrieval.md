# Retrieval record

## Local context beyond the provisioned case inputs

- Read the prediction prompt and prediction, agent-tooling, and agent-flags schemas as output-contract material.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid-segment relist and CVSG cuts, per-Term rows, and the `sal-v4` segment table.
- Read `metrics/statpack.json` structure and selected Term records. Computed the private `baseline` reached anchor over Terms 2017–2025 as the sum of `prefix_est_grant_rate * prefix_weighted_resolved` divided by the sum of `prefix_weighted_resolved`: 638 / 12,720. Also inspected those Terms' paid-fee timing records. No case-level outcomes were read from the pack.
- Ran `uv run fedcourts paths --court scotus --docket 9026000359 --event evt-petition-arrival-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a temporary writable cache succeeded. This was path resolution, not a corpus query.
- No `fedcourts query` or `open-events` lookup was performed; no ranged-corpus-read transfer line was emitted.

## Web attempts

1. One search request containing `site.supremecourt.gov Rule 10 certiorari rarely granted erroneous factual findings misapplication properly stated rule` and `site.loc.gov "Pembaur" "final authority" "475"`. No usable result was returned.
2. Three attempts to open the Supreme Court's filing-and-rules guidance page, each returning no usable content. No content from these attempts informed the prediction. No query named the target petition or sought its outcome.

## CourtListener MCP

1. Opinion search with citation `475 U.S. 469`, one requested result. Returned Randolph Hughes v. Neil Sanders, II, 469 F.3d 475 (November 13, 2006), rather than the requested Supreme Court authority. Disregarded that unrelated result; did not retrieve its full text.
2. Opinion search with case name `Pembaur v. City of Cincinnati`, court `scotus`, one requested result. Retrieved the case record for 475 U.S. 469, decided March 25, 1986, including combined opinion ID 111615.
3. `search_document(opinion_id=111615, query="final authority", snippet_size=700)`. Read the discussion around pp. 481–483 distinguishing discretionary action from final authority over municipal policy. Other excerpts included separate writings; the rationale relies on the identified lead-opinion passage and does not treat a dissent as the Court's holding.

No retrieval sought the target case's disposition or subsequent history, and no target-outcome material was encountered.
