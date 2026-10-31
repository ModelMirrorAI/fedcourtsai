# Retrieval record

## Local context and CLI setup

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; inspected applicable instruction-file locations. No AGENTS.md was found. Read this event's definition and the provisioned case-level snapshot, context, document manifest, question presented, relevant petition and appendix portions, and same-question list. No outcome file, other prediction, or labeling-artifact content was read.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000370 --event evt-petition-disposition --role predictor`. It failed because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`; it resolved the case and event paths and withheld the evaluator-only outcome path.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` successfully to inspect the structured-filter interface.
- Read the committed `metrics/statpack.md`, particularly modern-cert dispositions, originating circuit, paid-segment relist/CVSG/amicus cuts, and the sal-v4 reached-band table. Used only prior-Term rows for the band anchor and the frozen context anchor. Pooled endpoint cuts were descriptive cross-checks, not forward-hazard estimates.

## Corpus lookup

Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3`

Reported stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`

Returned recent grant-side records for David M. Scanlan v. Coalition for Open Democracy, Association for Education Fairness v. Montgomery County Board of Education, and Department of Justice v. Scott McNutt. These were not antitrust analogues; the first was an application. No opinion bodies were requested and none of these records informed a case-specific legal inference.

## CourtListener MCP

1. `search(type="o", citation="781 F.3d 264", num_results=2, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions", "snippet"])`. Returned Collins Inkjet Corporation v. Eastman Kodak Co., decided March 16, 2015; lead-opinion ID 9814946, combined-opinion ID 2982827, and concurrence ID 9814947. The tool warned that the top-level `snippet` field was unavailable, but nested opinion snippets and identifiers were returned.
2. `search_document(opinion_id=9814946, query="economic equivalent", snippet_size=1600)`. Returned the passage explaining the below-cost-equivalence requirement for a tie enforced solely through differential pricing. This directly supported, while narrowing, the petition's conflict argument.
3. `search_document(opinion_id=9814946, query="affirm", snippet_size=750)`. Returned three passages, including the conclusion affirming Collins's preliminary injunction. This prevented treating the precedent as automatic protection for any seller quoting above-cost prices.

## Web-tool attempts

1. One search call with two queries: `site.supremecourt.gov opinions 2008 linkLine 07-512` and `site.ca6.uscourts.gov Collins Inkjet Kodak 781 264 2015`. The web tool returned no visible results or usable content.
2. One open call for the Sixth Circuit's official Collins PDF, `https://www.ca6.uscourts.gov/opinions.pdf/15a0045p-06.pdf`. Again, the web tool returned no visible results or usable content. The prediction relies on the CourtListener opinion text instead.

Neither attempt sought this petition's disposition or subsequent history. No usable external web page was incorporated.

## Validation

Ran the contract's `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data` after writing the output files. It passed: `OK: 29745 artifact(s) valid, 71084 reference(s) consistent`. Validation is a local schema/contract check, not retrieval of substantive case material.
