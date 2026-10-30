# Retrieval record

## Provisioned record

Read the cell's event definition and case-level `record/context.json`,
`record/snapshots/2026-06-16.json`, `record/documents/documents.json`,
`record/documents/questions-presented.txt`, and relevant portions of
`record/documents/petition.txt`, including the appellate summary-order appendix.
No current docket, own-case outcome, other prediction/evaluation, or
question-label artifact was retrieved.

## Beyond the provisioned inputs

1. Read the contract and output schemas, `metrics/statpack.md` (modern cert
   dispositions, circuit context, paid-segment relist, CVSG and amicus cuts,
   and the sal-v4 per-Term band table), and the repository's path,
   serialization, and schema helpers. A local Python calculation pooled the
   printed prior-Term baseline reached rates for OT2017–OT2024, yielding
   approximately 0.052322 on denominator 11,599. No live corpus read was
   performed, so no corpus-transfer line applies.
2. Web search attempted with query:
   `site.supremecourt.gov "Rule 10" "Review on a writ of certiorari" "compelling reasons"`.
   The tool returned no usable result or source text. This was general rules
   context, not a search for this petition or its outcome.
3. Web open attempted for
   `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`.
   The tool returned no usable content. No claim relies on the guessed PDF
   location, its existence, or its contents.
4. CourtListener MCP `search` attempted with `type="o"`,
   `citation="602 U.S. 821"`, `num_results=1`, and fields
   `caseName,dateFiled,citation,id,absolute_url,snippet`, seeking the Erlinger
   precedent cited in the supplied petition. It failed with HTTP 429:
   daily rate limit exceeded, with an indicated wait of 1,823 seconds.
   No case text was returned. No retry and no REST fallback were attempted.

## Local path resolution and validation

`uv run fedcourts paths --court scotus --docket 73272491 --event
evt-order-call-for-response-disposition --role predictor` initially failed
because the default uv cache directory was read-only. Retrying with the cache
under `/tmp/uv-cache` succeeded and returned the case and event paths; the
outcome path was withheld by the predictor interface. This was path resolution,
not a corpus lookup. Validation likewise uses the temporary cache location.
