# Retrieval log

## Local sources

- Read the repository instructions, prediction prompt, prediction/flags/tooling schemas, event definition, case-level context, and `record/snapshots/2026-10-03.json`. No `record/documents/` files were present.
- Read committed `metrics/statpack.md`: modern-cert disposition, circuit, paid-segment relist/CVSG cuts, and sal-v4 per-Term band table. Anchored only on federal reached rows for 2017–2024. Inspected the top-level keys of `metrics/statpack.json` for metadata; no timestamp was available there.
- Computed the weighted average of the displayed prior-Term percentages locally: 0.7294972375690608, denominator 181.
- Ran `uv run fedcourts paths --court scotus --docket 73500246 --event evt-petition-disposition --role predictor`; initial default-cache permission error, then success with a writable temporary cache. Read path/serialization helpers to keep output placement and serialization consistent.
- No `fedcourts query` or `open-events` lookup; no ranged corpus reads line was emitted. No realized-outcome file, other predictor output, or QP-label artifact was read.

## Web attempts

1. `search_query`: `site.ca4.uscourts.gov "24-2070" "2025" Ozurumba`. No usable result returned.
2. `open`: `https://www.ca4.uscourts.gov/opinions/242070.P.pdf`. No usable content returned. This was an attempted retrieval of the identified lower-court opinion, not a current Supreme Court docket lookup.

## CourtListener MCP

1. `search(type="o", court="ca4", docket_number="24-2070", filed_before="2026-05-29", num_results=3)`. One result: September 2, 2025 published opinion, cluster 10665527, opinion 11132114. This pre-petition opinion supplies the legal controversy.
2. `read_document(opinion_id=11132114, chunk_index=[0,1,2,3,4,5], chunk_size=10000)`. Broad read of the antecedent opinion; returned display was truncated.
3. `search_document(opinion_id=11132114, query="circuit", snippet_size=750)`. Located the panel composition and references to other circuits; display partly truncated.
4. `read_document(opinion_id=11132114, chunk_index=[7,8], chunk_size=10000)`. Read dissent arguments and concluding discussion; display partly truncated.
5. `search_document(opinion_id=11132114, query="We hold", snippet_size=1000)`. Confirmed the majority left broader administrative-law questions unresolved and remanded to the agency.
6. `read_document(opinion_id=11132114, chunk_index=7, chunk_size=5000)`. Targeted majority pp. 15–17, establishing its material-support test and application to cooking services.

All substantive external evidence used comes from this September 2, 2025 lower-court opinion. Statements about a possible circuit conflict are attributed to that opinion, not to independently retrieved comparator holdings. No Supreme Court disposition or post-petition case history was sought or encountered.
