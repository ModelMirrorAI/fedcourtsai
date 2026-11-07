# Retrieval record

## Provisioned and committed local sources

Read the specified prediction prompt and schema; this event's definition; the case-level November 7, 2026 snapshot and context; the document manifest, questions presented, petition, Authority opposition, reply, relevant appendix portions; and the empty same-question list. Consulted `metrics/statpack.md`, particularly modern-cert dispositions, CA5, paid-segment relist/CVSG/amicus cuts, and the sal-v7 per-Term table. These are local inputs, not live case-outcome retrievals. Read the flags and tooling schemas to format the required outputs.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000430 --event evt-petition-disposition --role predictor` failed before retrieval because the default uv cache directory was read-only. No transfer line.
2. `UV_NO_CACHE=1 uv run fedcourts paths --court scotus --docket 9026000430 --event evt-petition-disposition --role predictor` succeeded, resolving the case and event paths and identifying the evaluator-only outcome as off-limits. No outcome file was opened; no transfer line.
3. `UV_NO_CACHE=1 uv run fedcourts query --help` succeeded. Read the structured query interface. No transfer line.
4. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition granted --era roberts --limit 3` failed validation: era must be a decade token, not a chief-justice era. No corpus data or transfer line. Retried with the documented vocabulary and a conservative historical cutoff.
5. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-09-01 --limit 3` succeeded. Returned NPS v. National Trust (26A203), Trump v. California (26A124), and Jouppi v. Alaska (25-246). The first two are substantive interim applications, not cert comparators; none was used to estimate the target's probability. The cutoff was voluntary historical-prior hygiene, not this forward cell's retrieval boundary.

   `ranged corpus reads: 41 GET(s), 10747904 byte(s)`

6. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --docket-number 24-354 --decided-before 2026-09-01 --limit 1` succeeded. Returned FCC v. Consumers' Research, granted November 22, 2024, with a recorded reversed merits judgment on June 27, 2025; no opinion body available. Used as confirmation of separate precedent history, not as a directly comparable grant-rate observation.

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

## Web calls

The following four tool calls returned no usable response content. No search-result snippets, opinions, or federal memorandum text were available to incorporate:

1. A batched search with queries `site.supremecourt.gov opinions 2024 24-354 Consumers Research June 27 2025 private delegation subordinate` and `site.law.cornell.edu 15 USC 3053 abrogate add modify rules`.
2. Search query `site.supremecourt.gov "Consumers’ Research" "2025" "24-354" opinion`.
3. Attempted open of the official precedent PDF at `https://www.supremecourt.gov/opinions/24pdf/24-354_0861.pdf`.
4. Attempted open of the predecision federal opposition linked by the provisioned snapshot at `https://www.supremecourt.gov/DocketPDF/26/26-430/429403/20261013171813628_26-332GovtOpp.pdf`.

No CourtListener MCP calls, open-events calls, own-disposition searches, or live target-docket lookups were made. No claim about the target's outcome surfaced. Validation is a local schema/completeness check, not additional legal retrieval.
