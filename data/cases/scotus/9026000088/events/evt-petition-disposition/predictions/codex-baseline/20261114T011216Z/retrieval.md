# Retrieval record

## Provisioned inputs and local references

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the event definition, `record/snapshots/2026-11-14.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, the petition's argument and available appendix excerpts in `record/documents/petition.txt`, `record/context.json`, and `record/same-question.json`. Also consulted the committed `metrics/statpack.md`, especially the modern cert, paid-segment relist/CVSG/amicus, and sal-v8 reached-band sections, plus the tooling and flags schemas. No other prediction, evaluation, realized-outcome record, or topic-label artifact was read.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000088 --event evt-petition-disposition --role predictor` failed before execution because uv's default cache directory was read-only. No case information returned and no transfer line was printed.
2. Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts paths --court scotus --docket 9026000088 --event evt-petition-disposition --role predictor`. This succeeded, identifying the local case/event paths and the evaluator-only outcome restriction. No corpus query occurred and no transfer line was printed.

No `fedcourts query`, `open-events`, corpus download, package installation, or PDF download was attempted. Local validation uses the same writable-cache override and offline mode.

## Web attempts

1. One `web.run` search call contained two precedent-only queries: `site.supremecourt.gov "Americans for Prosperity Foundation" "narrowly tailored" "2021"` and `site.supremecourt.gov "Citizens United" "disclosure requirements" "express advocacy" "2010"`. The tool returned no visible results or source text. Nothing from it informed the forecast.
2. One `web.run` open attempted the official AFPF opinion at `https://www.supremecourt.gov/opinions/20pdf/19-251_p86b.pdf`. The tool again returned no visible content. No opinion text was obtained through this call.

Neither call searched for this petition, its outcome, or a forecast.

## CourtListener MCP calls

1. `search(type="o", citation="594 U.S. 595", num_results=2)` returned Americans for Prosperity Foundation v. Bonta, decided July 1, 2021, cluster 4896549, combined opinion **4700328**, and one unrelated result caused by the loose citation match. Used only the matching opinion metadata; ignored the unrelated case. The response also supplied the official PDF address used in the web-open attempt above.
2. `search(type="o", q='caseName:"Citizens United v. Federal Election Commission"', court="scotus", filed_after="2010-01-20", filed_before="2010-01-22", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])` returned Citizens United v. FEC, 558 U.S. 310 (January 21, 2010), including lead opinion **9413187**. Used the metadata to select the opinion, not as new information about the pending petition.
3. `search_document(opinion_id=9413187, query="express advocacy", snippet_size=600)` returned eleven excerpts. Used the discussion at **558 U.S. 368–69**, which rejects imposing the express-advocacy boundary on the federal disclosure requirements at issue there. This is a counterweight to treating the petition's Wisconsin Right to Life argument as mechanically controlling.
4. `search_document(opinion_id=4700328, query="narrowly tailored", snippet_size=250)` returned nineteen excerpts. Used the majority's rule that exacting scrutiny requires narrow tailoring, though not the least restrictive means, reflected at **594 U.S. 607–11**. This supports the petition's tailoring theory without deciding its application to election-related disclosures.

These were all external lookup attempts. No live docket or lower-court record for this petition was fetched; the state opinion was read only as provisioned within the petition appendix. No outcome or third-party forecast surfaced.
