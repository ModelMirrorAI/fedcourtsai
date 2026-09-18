# Retrieval beyond the provisioned inputs

## Committed aggregate context

- Read the modern-cert disposition and circuit sections, paid relist and CVSG cuts, and sal-v4 segment table in `metrics/statpack.md`.
- Inspected aggregate structure and the relevant Term segment fields in `metrics/statpack.json`. Pooled exact high-band reached values for Terms 2017-2024: weighted grants 314, denominator 898, rate 0.34966592427616927. No case-level corpus rows were consulted.
- No `fedcourts query` or `open-events` call was made; there is no ranged-corpus transfer line to report.

## Historical precedent through CourtListener MCP

1. `search(type="o", citation="673 F.3d 430", num_results=2)` returned Carrier Corporation v. Outokumpu Oyj, Sixth Circuit, filed March 2, 2012, opinion ID 624024. Purpose: verify a pre-existing comparator cited by both briefs, not retrieve the target petition's outcome.
2. `search_document(opinion_id=624024, query="paper trail", snippet_size=1400)` returned the passage distinguishing nonspecific allegations of secret meetings from sufficiently particular allegations of affirmative concealment through paper-trail controls and coded identities. This passage informed the assessment of the asserted split.

## General web attempts

1. Search query: `site.supremecourt.gov "Rule 10" "Considerations Governing Review on Certiorari"`. No usable result content was returned.
2. Attempted to open Cornell's Supreme Court Rule 10 page, path `/rules/supct/rule_10`. No usable page content was returned. No proposition in the forecast relies on either attempt.

## Operational checks

- Read the task contract, applicable repository instructions and output schemas.
- `uv run fedcourts paths --court scotus --docket 73275236 --event evt-order-cvsg-disposition --role predictor` initially failed because the default uv cache was read-only. Repeating with the cache directed to `/tmp/uv-cache` succeeded. This command returned paths, not docket content.
- Read the local path and serialization helper definitions solely to place and serialize the allowed output files.

No search sought General Dynamics v. Scharpf's current status, subsequent history or disposition. No outcome file, other predictor's forecast, or topic-label artifact was read. No outcome-revealing material was encountered.
