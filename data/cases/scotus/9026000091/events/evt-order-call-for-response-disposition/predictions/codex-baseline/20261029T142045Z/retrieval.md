# Retrieval record

## Provisioned inputs and local reference material

- Read the event, `record/context.json`, and
  `record/snapshots/2026-09-09.json`; the document manifest, questions
  presented, petition, and relevant appendix decisions. A read-only assistant
  reviewed only the provisioned appendix and returned a summary; I checked
  the passages used. No other cell's output was consulted.
- Read `metrics/statpack.md` and the relevant `terms[].segments` entries in
  `metrics/statpack.json`. Computed the sal-v4 baseline reached pool over the
  displayed 2017-2025 Terms: 660 / 12,913 = 0.0511112832.
- Read prediction/tooling schemas and the local serialization/path helpers
  to construct and validate this cell's files. No aggregate statistics were
  newly computed from the remote corpus.
- A second read-only assistant reviewed this cell's own output against the
  statistical-review checklist and relevant local metrics references. It
  independently confirmed the prior-Term reached pool, quoted terminal cuts,
  claim conditionals, and writer-probability coherence, with no blockers.
  It made no external retrieval and read no other cell's output.

## Corpus CLI calls

The first two commands below failed because uv's default cache directory was
read-only. All subsequent uv commands used `UV_CACHE_DIR=/tmp/uv-cache`.
This contains no corpus or API credential.

1. `uv run fedcourts paths --court scotus --docket 9026000091 --event evt-order-call-for-response-disposition --role predictor`
   — failed before CLI execution: read-only uv cache.
2. `uv run fedcourts query --help`
   — same cache failure; no retrieval occurred.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000091 --event evt-order-call-for-response-disposition --role predictor`
   — resolved the case, event, and corpus paths. No outcome read.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`
   — read structured filter and replay-clock documentation.
5. `COLUMNS=180 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`
   — repeated help with a wider display to read the flags.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`
   — returned Google LLC v. VirtaMove, No. 25-1230;
   Hastings College Conservation Committee v. California, No. 25-1231;
   and Ryan O'Donnell v. City of Chicago, No. 25-1098. Each was denied
   October 19, 2026; their distribution counts were 2, 2, and 4.
   These are general procedural examples, not substantive matches. The
   bare-year filter screens by Term, not resolution day, so it admitted
   these 2025-Term cases. This is a forward cell; these other cases'
   disposition dates are not a leakage issue, and no claim of strictly
   pre-snapshot decision dates is made.

   `ranged corpus reads: 11 GET(s), 2883584 byte(s)`

7. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 19-659 --decided-before 2026 --limit 1`
   — returned Miladis Salgado v. United States, scotus/66727850;
   denied April 6, 2020; two distributions; no opinion body. This is the
   earlier CAFRA petition identified in the provisioned petition.

   `ranged corpus reads: 11 GET(s), 2883584 byte(s)`

No `--full` query, `open-events` call, or current-case disposition query
was attempted.

## CourtListener MCP

- `search(type="o", citation="578 U.S. 419", num_results=1,
  fields=["caseName", "dateFiled", "citation", "id", "absolute_url", "opinions"])`
  — attempted lookup of CRST Van Expedited v. EEOC. Returned HTTP 429,
  daily rate limit exceeded; no opinion retrieved. No REST fallback used.

## Web tool

One search call contained two general precedent queries:

- `site.supremecourt.gov opinions CRST Van Expedited EEOC 2016 preclusive judgment`
- `site.supremecourt.gov opinions Hardt Reliance Standard 2010 prevailing party`

The tool returned no visible results or source content. A subsequent open of
the official-report PDF likewise returned no visible content:
`https://www.govinfo.gov/content/pkg/USREPORTS-578/pdf/USREPORTS-578-419.pdf`.
No independently retrieved opinion text informed the prediction. Neither
search concerned Ross's Supreme Court disposition or subsequent history.
