# Retrieval log

## Provisioned inputs

Read the event definition, case-level `record/context.json`, `record/snapshots/2026-09-17.json`, and the provisioned documents manifest, QP text, and full petition text. No appendix, BIO, outcome record, subsequent history, or another predictor's output was consulted.

## Local context beyond the provisioned inputs

- Read `metrics/statpack.md`: modern discretionary-cert disposition counts, originating-circuit breakdown, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table. Numerically pooled the reached-baseline column only for displayed Terms 2017–2024 using the published rounded rates and denominators; result approximately 5.12025%, denominator 11,580.
- Read the task instructions and prediction, flags, and tooling schemas for the artifact contract.
- Ran `uv run fedcourts paths --court scotus --docket 73500239 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only. Retried successfully with a writable temporary cache and `--no-sync`. This was path resolution, not a corpus lookup.
- No `fedcourts query` or `open-events` lookup was made; no ranged-corpus transfer line was produced.

## Web attempts

1. General search query: `site.supremecourt.gov "Rule 10" "misapplication" "Rule 15" "brief in opposition"`.
2. Open attempted for the Supreme Court's filing-and-rules guidance page, path `/filingandrules/rules_guidance.aspx`.
3. Repeated that open after the first returned no content.

All three web calls returned no usable content. No result, rule text, or authority was inferred from them. None searched for Pesta's disposition or docket history.

## CourtListener MCP

1. `search(type="o", citation="547 U.S. 410", num_results=1)`: returned *Garcetti v. Ceballos*, May 30, 2006, cluster 145653, including lead opinion 9434945. Used only to locate the pre-existing precedent; no citation counts or later citing cases were used.
2. `search_document(opinion_id=9434945, query="academic", snippet_size=650)`: returned the majority's page-425 discussion reserving application of the official-duty analysis to scholarship or teaching. Used to verify that limited doctrinal premise, not the proposed Sullivan-maliciousness rule or any fact about this petition.

No outcome-revealing material about this cell's case was retrieved or encountered.
