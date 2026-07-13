# Retrieval log

## Committed base-rate context

- Read `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition” and “SCOTUS cert petitions by Term.” The 2025 modern-cert estimate was 4.9% granted, but I did not use it as the numerical anchor because this case is a direct appeal under 28 U.S.C. § 1253 rather than a discretionary cert petition.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 10 --corpus-backend ranged` — attempted to obtain recent SCOTUS priors. It failed before returning results because the corpus object's S3 hostname could not be resolved. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `Singleton Allen Alabama congressional redistricting Voting Rights Act`, limited to filings before September 10, 2025 — located *Allen v. Milligan* and other general Alabama redistricting authorities.
- RECAP search by lower-court docket number `2:21-cv-01291-AMM`, limited to filings before September 10, 2025 — returned no results with the initial structured docket-number filter.
- Opinion search by case name `Singleton v. Allen`, limited to filings before September 10, 2025 — confirmed that the current lower-court ruling was not indexed as a published opinion under that exact name.
- Opinion search for pre-September 10, 2025 `Callais`/Louisiana congressional-redistricting authorities — surfaced *Alexander v. South Carolina State Conference of the NAACP* as relevant general law; no post-disposition material about this Supreme Court appeal was sought.
- RECAP full-text search for `"Singleton" "2:21-cv-01291"`, limited to filings before September 10, 2025 — located the Northern District of Alabama docket and related redistricting cases.
- Focused RECAP search for the same docket in `alnd`, limited to filings before September 10, 2025 — obtained CourtListener docket id `60607496` and confirmed availability of pre-appeal filings.
- Docket-entry endpoint schema lookup — identified the supported filters and fields for a date-bounded lower-court docket request.
- Docket-entry endpoint call for docket `60607496`, May 1 through September 9, 2025 — confirmed the direct appeal, the injunction, and the notice invoking 28 U.S.C. § 1253.
- Pagination of that date-bounded endpoint query — retrieved the May 8, 2025 findings, conclusions, and injunction, including the lower court's summary of the record, its intentional-discrimination holding, and its treatment of *Milligan* and *Alexander*.
- Opinion search for `602 U.S. 1` — located *Alexander v. South Carolina State Conference of the NAACP* and its CourtListener opinion record.
- Opinion endpoint lookup for the *Alexander* opinion — consulted the passages describing the presumption of legislative good faith, the need to disentangle race and politics, and the alternative-map analysis.
- Opinion search for `599 U.S. 1` — located *Allen v. Milligan* and its CourtListener opinion record.
- Opinion endpoint lookup for the *Milligan* opinion — consulted the passages describing the *Gingles* preconditions, totality-of-circumstances inquiry, and rejection of Alabama's proposed race-neutral benchmark.

No web searches or REST fallback calls were made. The CourtListener MCP server worked, so REST fallback was unnecessary.
