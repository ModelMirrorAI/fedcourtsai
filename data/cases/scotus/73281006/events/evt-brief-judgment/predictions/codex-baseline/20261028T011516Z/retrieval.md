# Retrieval record

No lookup sought this case's outcome, post-decision coverage, another cell's output, or labeling artifacts.

## Committed general context

- Read the merits-docket and complete-lineup per-Justice sections of `metrics/statpack.md` and the corresponding `merits`, `justice_votes`, and `authorship` sections of `metrics/statpack.json`. Used only grant Terms 2015–2024 for the merits pool and Terms before 2025 for votes and writers. Local Python aggregation produced 378/537 disturbed and 537/553 parsed coverage; no live corpus query was used.
- Consulted the prediction and tooling JSON schemas, path-resolution helpers, and serialization helpers to meet the artifact contract. These are implementation context, not case evidence.

## Web attempts: general precedent only

1. `web.search_query`: `site.supremecourt.gov opinions 2020 Pakdel San Francisco finality modest`.
2. In the same call: `site.supremecourt.gov opinions 2013 Susan B Anthony List Driehaus credible threat enforcement`.
3. `web.open`: the official Supreme Court PDF for Pakdel, docket 20-1212, at the Court's `opinions/20pdf/20-1212_3204.pdf` path.

Both web calls returned no usable result or document text. No factual contribution from them was incorporated.

## CourtListener MCP: general precedent only

1. `search(type="o", case_name="Pakdel v. City and County of San Francisco", filed_before="2021-07-01", court="scotus", num_results=3)`. Returned one case, decided June 28, 2021, citation 594 U.S. 474, opinion ID 4699044, cluster ID 4895265, with a brief opening snippet. This verified identity, not the whole opinion's reasoning. Current citation-count and tracking metadata were not used as forecast signals.
2. `read_document(opinion_id=4699044)`. Returned HTTP 429 rate-limit feedback, not opinion text. No direct CourtListener REST fallback was attempted.

No `fedcourts query` or `open-events` calls were made; there is no ranged-corpus-reads line to report. The statpack and provisioned documents remained the substantive evidence base.
