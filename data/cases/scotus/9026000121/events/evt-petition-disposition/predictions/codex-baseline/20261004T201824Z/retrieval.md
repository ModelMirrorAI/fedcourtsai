# Retrieval record

## Provisioned materials

Read this cell's event.yaml, record/context.json, record/snapshots/2026-10-04.json, record/documents/documents.json, questions-presented.txt, and selected petition.txt portions covering jurisdiction, facts, and arguments. No other prediction, evaluation, outcome, or topic-labeling artifact was read.

## Committed general context

- Read metrics/statpack.md: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, originating-court/Term headings, and the sal-v4 reached-band table. A headings search also surfaced other-stage table rows, which were not used as cert anchors.
- Inspected only the top-level keys of metrics/statpack.json to check for build metadata. No case-level membership was retrieved.
- Computed the denominator-weighted approximate baseline reached rate from all displayed 2017–2025 rows: 0.05010888, weighted n=12,720. No remote corpus query or open-events call was made, so no ranged-corpus-read transfer line exists.

## General web attempts

One web search call contained these two queries:

1. `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings`
2. `site.supremecourt.gov Caperton 2009 most matters judicial disqualification constitutional level due process`

Both returned no usable tool content. A subsequent page-open attempt for `https://www.law.cornell.edu/rules/supct/rule_10` also returned no usable content. No substantive proposition relies on these attempts, and no search identified this petition or sought its outcome.

## CourtListener MCP

1. `search(type="o", citation="556 U.S. 868", num_results=1)`: returned Caperton v. A. T. Massey Coal Co., Inc., decided June 8, 2009; cluster 145867, including opinion 9435330. Used only as general preexisting recusal doctrine.
2. `search_document(opinion_id=9435330, query="constitutional", snippet_size=450)`: read excerpts distinguishing constitutional disqualification from broader ethical standards and requiring an objectively intolerable probability of bias. The response included some dissent material; the rationale relies on the majority's discussion at 556 U.S. 876 and 889–90, not the dissent.

No current docket, subsequent history, or disposition of Basso was requested. No outcome-revealing material surfaced.

## Local contract tooling

Read AGENTS.md, the prediction prompt, and prediction/tooling schemas. Ran `fedcourts paths --court scotus --docket 9026000121 --event evt-petition-disposition --role predictor`. The first uv invocation failed because its default cache was read-only; redirecting the cache to a writable temporary location resolved it. These are contract/environment operations rather than factual retrieval.
