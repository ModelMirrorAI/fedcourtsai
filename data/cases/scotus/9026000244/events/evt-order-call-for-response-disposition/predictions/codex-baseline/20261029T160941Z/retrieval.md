# Retrieval

## Provisioned and committed materials

Read AGENTS.md, the prediction prompt and relevant schemas; this event's event.yaml; record/context.json; record/snapshots/2026-09-04.json; the documents manifest, questions-presented.txt, relevant portions of petition.txt and appendix.txt. Read the committed metrics/statpack.md, including its modern-cert disposition, sal-v4 per-Term reached, relist, CVSG and amicus sections. Searched metrics/statpack.json for build/vintage metadata; no matching build timestamp was returned. The pack figures are identified as committed-pack figures, not a current corpus census. A local Python calculation pooled the nine allowed prior-Term baseline rows, obtaining approximately 0.051068 over weighted n=12,913 from rounded displayed rates.

The path resolver, query help, schema inspection, serialization/path helper inspection and output validation are operational checks, not additional case evidence. Initial `uv run fedcourts paths --court scotus --docket 9026000244 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` attempts failed because the default uv cache was read-only. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; both worked. Query help was also reread with a wider display to inspect structured filters.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '145 S. Ct. 1133' --decided-before 2026 --limit 3`

   Result: no returned rows. The CLI warned that only 200 scoped SCOTUS rows carried reporter citations, so the empty result was not evidence of the precedent's absence.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`

   Result: three general prior-docket grants, docket numbers 25-1103, 25-7026 and 25-1343, each showing an October 13, 2026 cert grant. The Term filter is not a September 2026 day cutoff. This is a forward cell, so these unrelated prior-docket rows are permissible retrieval; nevertheless I did not use them as substantive analogues or to adjust the forecast. No query sought the target petition or its later history.

   `ranged corpus reads: 25 GET(s), 6553600 byte(s)`

## General legal-context web attempts

All three attempts returned no usable text or source result:

1. Search: `site.supremecourt.gov opinions 2024 Labcorp Davis 24-304 Kavanaugh dismissed uninjured class members`.
2. Search: `site.supremecourt.gov "24-304" "KAVANAUGH" "2025"`.
3. Open attempt: the official Court opinion PDF path ending in `opinions/24pdf/24-304_3e04.pdf`.

These were attempts to confirm an earlier, different proceeding identified in the supplied petition, not searches for the target case. No legal proposition is attributed to a successfully retrieved web source.

## CourtListener MCP

Search: type `o`, court `scotus`, query `caseName:"Laboratory Corporation" AND caseName:Davis`, num_results 3.

Result: HTTP 429 daily rate limit; no opinion or case text returned. Used the provisioned filing's account instead. No direct CourtListener REST request or credential access was attempted.

## Independent record check

A read-only subagent reviewed only the provisioned appendix and questions presented, without external retrieval or file writes. It distinguished the panel's legal standing ruling from its assumed existence of uninjured refund recipients and its separate predominance analysis. I checked those points directly against Appendix 3a-5a and 43a-44a before using them. No other cell's forecast, evaluation, target outcome or topic-label artifact was read.
