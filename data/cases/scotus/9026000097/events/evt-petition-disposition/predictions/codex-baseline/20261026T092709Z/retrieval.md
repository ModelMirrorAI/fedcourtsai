# Retrieval record

## Provisioned inputs

Read the case-level context and 2026-10-26 snapshot, event.yaml, questions-presented.txt, petition.txt, relevant reproduced lower-court passages in appendix.txt, and documents.json. No outcome file or other cell's output was read. No current docket lookup or search for this petition's disposition was performed.

## Committed general context

Read metrics/statpack.md and selected fields in metrics/statpack.json. Pooled the OT2017–OT2025 sal-v4 baseline reached estimates: 644 / 12,883 = 0.04998835674920438. No fedcourts query or open-events lookup was made, so no ranged-corpus transfer line applies.

Ran the path resolver with literal authoritative identifiers:

`UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000097 --event evt-petition-disposition --role predictor`

The first invocation without the writable cache override failed before executing the CLI because the default uv cache path was read-only. The overridden invocation succeeded. The resolver marked the outcome as evaluator-only; it was not opened.

## CourtListener MCP

1. search, type=o, q=`caseName:"Kimmel" "Konik"`, num_results=3. An initial, unhelpful precedent lookup returned zero results; nothing from it informed the prediction.
2. search, type=o, q=`"Barrett" "Steubenville"`, num_results=3. Returned the Sixth Circuit precedent at 388 F.3d 967, opinion IDs 2971589 and 788318 among the duplicate versions, and the historical cert-denial entry for that precedent. This was unrelated historical litigation, not the target petition. Used the precedent identification, not the historical cert denial as a quantitative prior.
3. search_document, opinion_id=788318, query=`fundamental`, snippet_size=400. Read the returned passages on parental educational choice, unconstitutional conditions/public employment, and qualified immunity. These confirm the employment-retaliation context and doctrinal language; no target-case disposition surfaced.

## General web searches

The following general-precedent searches were issued through web search:

- `site.supremecourt.gov opinions 2020 Espinoza Montana Department Revenue pdf`
- `site.supremecourt.gov opinions 2022 Carson Makin private school benefit pdf`
- `site.supremecourt.gov "20-1087" "Carson"`

No usable search-result response text was delivered to the engine. No result was opened, no information from these searches shaped the forecast, and none of the queries named the target case. The last query's docket-number guess is not relied upon as a citation.
