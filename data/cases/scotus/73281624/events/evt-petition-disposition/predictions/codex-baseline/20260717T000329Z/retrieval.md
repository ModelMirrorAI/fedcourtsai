# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially "Modern discretionary-cert petitions by disposition," originating-circuit, relist-count, CVSG-status, and per-Term tables.
- Consulted `metrics/statpack.json` for the Term 2025 paid-petition estimate (5.36%).

## Corpus queries

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '568 U.S. 216' --citation '317 U.S. 341' --limit 8`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --citation '568 U.S. 216' --citation '317 U.S. 341' --limit 8`

Both commands failed before returning a row or a `ranged corpus reads` line because DNS resolution for the remote corpus store failed. No corpus priors were used.

## CourtListener MCP

- Opinion search for `"market participant" "Parker immunity"`, limited to federal appellate courts and opinions filed before July 17, 2026. It returned one result, *Genentech, Inc. v. Eli Lilly and Company* (Federal Circuit, 1993).
- Opinion search for `"market participant exception" antitrust`, opinions filed before July 17, 2026. The first page reported 70 results and included *Western Star Hospital Authority v. City of Richmond* (Fourth Circuit, 2021), *Paramount Media Group, Inc. v. Village of Bellwood* (Seventh Circuit, 2019), and the already-provisioned lower-court opinion in this case. I used the search only as a limited check for a developed appellate conflict and did not retrieve this petition's docket or disposition.

No web searches were used.
