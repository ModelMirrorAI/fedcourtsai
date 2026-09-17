# Retrieval log

## Provisioned inputs

Read the event definition, case-level snapshot `2026-09-16.json`, context, document manifest, QP text, and relevant sections of the petition. These were the common provisioned baseline. No outcome file, other predictor output, or QP-labeling artifact was read.

## Committed aggregate context

Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cuts, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term reached-band table. Read JSON structure and the baseline risk-set fields in `metrics/statpack.json` to compute the unrounded prior-Term pool. The first JSON Term object inspected was the unscored 2026 row solely to locate field names; neither that row nor Term 2025 entered the anchor.

Executed arithmetic:

```sh
jq '[.terms[] | select(.term >= 2017 and .term < 2025) | .segments[] | select(.band == "baseline") | {numerator: (.prefix_est_grant_rate * .prefix_weighted_resolved), denominator: .prefix_weighted_resolved}] | {grant_estimate: (map(.numerator)|add), resolved_estimate: (map(.denominator)|add), pooled_rate: ((map(.numerator)|add)/(map(.denominator)|add))}' metrics/statpack.json
```

Result: grant estimate 593; resolved estimate 11,580; pooled rate 0.05120898100172712. No live corpus lookup was made, and no ranged-corpus transfer line was emitted. The figures describe the committed pack, not an independently refreshed corpus.

## CourtListener MCP

All case-specific retrieval targeted the lower-court opinion preceding the cert petition, never the Supreme Court outcome.

1. `search(type="o", court="ca4", docket_number="24-1959", filed_before="2025-12-09", num_results=5)`. One result: David Gasper v. EIDP, Inc., filed December 8, 2025; cluster 10750028, opinion 11216613, published. Search identifier: `74339690`.
2. `read_document(opinion_id=11216613, chunk_index=0, chunk_size=13000)`.
3. `read_document(opinion_id=11216613, chunk_index=[1,2,3], chunk_size=13000)`. Some displayed tool output was truncated; targeted smaller reads below supplied the central reasoning and preservation passage.
4. `search_document(opinion_id=11216613, query="waiv", snippet_size=1200)`: no matches. This was not treated as evidence that all issues were preserved.
5. `search_document(opinion_id=11216613, query="5\n", snippet_size=1400)`: six matches, locating the footnote addressing an argument first raised on appeal.
6. `read_document(opinion_id=11216613, chunk_index=4, chunk_size=5000)`: standard of review, circuit agreement, QDRO interpretation, start of footnote 5.
7. `read_document(opinion_id=11216613, chunk_index=5, chunk_size=5000)`: remainder of footnote 5 and contract interpretation.
8. `search_document(opinion_id=11216613, query="Chenery", snippet_size=200)`: no matches.

Source identifier for the retrieved primary opinion: Gasper v. EIDP, Inc., No. 24-1959, Fourth Circuit, December 8, 2025, slip opinion, 16 pages. No subsequent-history link was followed.

## Web attempts

1. Search query: `site.supremecourt.gov rules Rule 10 certiorari erroneous factual findings misapplication properly stated rule law`.
2. Open attempt: `https://www.supremecourt.gov/ctrules/2019RulesoftheCourt.pdf`.

Both web calls returned no usable content or source results in this session. Neither supplied evidence, and no outcome material surfaced.

## Local contract and path tooling

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flags schemas. Ran `uv run fedcourts paths --court scotus --docket 73500263 --event evt-petition-disposition --role predictor`; its first attempt failed because the default uv cache directory was read-only. Retrying with the cache directed to `/tmp/uv-cache` succeeded. This was a local path-resolution operation, not a corpus retrieval. No CourtListener credentials or direct REST fallback were used.
