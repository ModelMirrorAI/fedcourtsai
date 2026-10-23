# Retrieval beyond the provisioned inputs

## Committed statistical context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term reached-band table.
- Read the corresponding `metrics/statpack.json` structure and baseline-band counts. Computed the anchor with:

```sh
jq '[.terms[:10][] | select(.term < 2026 and .salience_version == "sal-v4") | .segments[] | select(.band=="baseline") | {denominator:.prefix_weighted_resolved,grants:(.prefix_est_grant_rate*.prefix_weighted_resolved)}] | {terms:length,denominator:(map(.denominator)|add),grants:(map(.grants)|add),rate:((map(.grants)|add)/(map(.denominator)|add))}' metrics/statpack.json
```

Result: nine prior Terms, weighted denominator 12,883, estimated grants 644, rate 0.04998835674920438. `git log -1 --format='%h %cI' -- metrics/statpack.json` returned `ac757d745 2026-10-19T05:54:06Z`. This dates the committed artifact, not its underlying corpus freshness.

No `fedcourts query` or `open-events` corpus lookup was made. No ranged-corpus-read transfer lines were produced.

## CourtListener MCP

1. `search(type="o", citation="92 F.4th 36", num_results=2, fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions", "absolute_url"])`. Returned Public Interest Legal Foundation, Inc. v. Bellows, February 2, 2024, cluster 9471807, opinion 9929645. This is an earlier, separate case, not the target petition.
2. `search_document(opinion_id=9929645, query="output and end product", snippet_size=1400)`. No match.
3. `search_document(opinion_id=9929645, query="end product", snippet_size=1500)`. No match.
4. `search_document(opinion_id=9929645, query="Voter File", snippet_size=600)`. Returned introductory holding and factual/procedural context for Maine's voter file.
5. `search_document(opinion_id=9929645, query="output", snippet_size=1000)`. Returned the First Circuit's explanation that the voter file reflects registration and maintenance activities and is subject to the federal disclosure provision. Used to corroborate the provisioned petition appendix's description of the split.

## General official-source web searches

- `site.justice.gov National Voter Registration Act Section 8 public disclosure voter registration records 20507`
- `site.justice.gov/crt "Section 8" "public inspection" "records"`
- `site.ca1.uscourts.gov "23-1361" "Bellows"`

These tool calls surfaced no usable results or source text and supplied no additional evidence. No search requested the target case's outcome or subsequent history.

## Contract and tooling reads

Read the named prediction/feedback schemas, repository instructions, and relevant path, ID, and serialization helpers to place and validate the output. Consulted the statistical-review checklist for a self-check of denominators, conditional probabilities, and leakage-safe pooling. These were implementation references, not additional case evidence.
