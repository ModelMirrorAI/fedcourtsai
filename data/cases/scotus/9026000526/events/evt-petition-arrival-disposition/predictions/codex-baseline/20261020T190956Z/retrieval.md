# Retrieval record

## Committed base-rate context

- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, paid scored-segment relist and CVSG cuts, and the sal-v4 per-Term segment table.
- Read `metrics/statpack.json` for the baseline reached-rate fields and their denominators. Pooled Terms 2017–2025 only, using `prefix_est_grant_rate * prefix_weighted_resolved` over `prefix_weighted_resolved`: 644 / 12,883 = 0.0499883567. The calculation ran locally through `uv run python`; this was not a corpus query.
- `git log -1 --format='%h %cI' -- metrics/statpack.md metrics/statpack.json` identified the pack's last commit as `ac757d745 2026-10-19T05:54:06Z`. No remote-corpus freshness was established.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were produced.

## General-authority web attempts

These attempts sought general double-jeopardy precedent, not this petition or its subsequent history. The web tool returned no usable content, so none supplied substantive evidence:

1. Search: `site.supremecourt.gov opinions McElrath Georgia 2024 acquittal double jeopardy`.
2. Search, in the same call: `site.supremecourt.gov opinions Evans Michigan 2013 Scott dismissal factual guilt innocence`.
3. Attempted open of the McElrath opinion at `https://www.supremecourt.gov/opinions/23pdf/22-721_kjfl.pdf`.

## CourtListener MCP

1. `search(type="o", citation="437 U.S. 82", num_results=2)`: query id `465bb6da`. The citation filter returned unrelated historical cases rather than Scott; no inference drawn from those results.
2. `search(type="o", q='caseName:"United States v. Scott" AND citation:"437 U.S. 82"', court="scotus", num_results=2)`: query id `62247467`; identified United States v. Scott, cluster 109895, majority opinion 9842021. Used the case identity and opinion pointer, not the search record's inconsistent date metadata.
3. `search_document(opinion_id=9842021, query="close", snippet_size=1000)`: read the opening majority account confirming that the dismissal followed the close of all evidence and concerned prejudice from preindictment delay.
4. `search_document(opinion_id=9842021, query="unrelated", snippet_size=700)`: read the five returned majority-opinion excerpts concerning defense-requested termination for grounds distinct from guilt and the distinction from an acquittal. Authority: United States v. Scott, 437 U.S. 82, 86–87, 97–101 (1978).

No target-case live search, outcome lookup, other predictor output, or labeling-measurement artifact was consulted. Provisioned filings and docket contents are summarized rather than reproduced.
