Beyond the provisioned case record, I consulted the committed metrics/statpack.md cert-disposition, originating-circuit, paid-segment relist, CVSG, amicus, and sal-v8 Term tables, and metrics/statpack.json to reproduce the strictly-prior high-band pool (271/775). No forecast outputs or outcome files were read.

CLI setup and help calls:

- `uv run fedcourts paths --court scotus --docket 9026000292 --event evt-order-call-for-response-disposition --role predictor` failed before execution because uv's default cache directory was read-only.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000292 --event evt-order-call-for-response-disposition --role predictor` succeeded and resolved the case/event paths; it explicitly withheld the evaluator-only outcome path.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --help` displayed the structured filters. Repeated with `COLUMNS=180` to read the full help after display truncation. Neither help call retrieved corpus rows.

Corpus lookup:

- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 4`
  - Transfer: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`.
  - Returned Robinhood Markets v. Sodha (25-944; CVSG June 1, 2026, grant November 13, 2026; three distributions), Goldman Sachs Bank USA v. Brown (25-1408; four distributions), U.S. DOGE Service v. U.S. District Court (25-1103; two), and Corey Duran Berry v. United States (25-7026; five). The clock filters the derived docket Term, so these earlier-Term petitions can have calendar-2026 grant dates. All returned dates preceded this cell's baseline. No full opinion hydration was requested. These are procedural examples, not a representative rate sample, and no row about this case was requested.

CourtListener MCP lookups:

- `search` attempted with `query='court:ca2 docketNumber:"23-258" after:2025-08-25 before:2026-04-05'`, `type='o'`, `order_by='dateFiled desc'`. Rejected because the argument is named `q`, not `query`; no retrieval occurred.
- Corrected `search(q='court:ca2 docketNumber:"23-258" after:2025-08-25 before:2026-04-05', type='o', order_by='dateFiled desc')`. Returned count 0, query ID c45f3b43. This sought only the lower-court opinion/rehearing materials, not the Supreme Court disposition.
- `search(q='court:ca11 "Stansell" after:2022-01-01 before:2023-01-01', type='o', order_by='score desc')`. Returned count 0, query ID 867f0e29. The petition remains the source for its characterization of Stansell III.

No web searches, live Supreme Court docket retrievals, direct CourtListener REST calls, or additional corpus lookups were attempted. The related dockets were provisioned inputs, not external retrieval. The required final validation is a local output check, not a substantive retrieval.
