# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
  Returned four substantive applications (People Not Politicians v. Onder; NRCC v. Brown; National Park Service v. National Trust; Trump v. California) and one cert docket (Jouppi v. Alaska). None is a comparable section 1981 or public-accommodation petition; not used beyond confirming the corpus service was reachable.

## CourtListener MCP lookups

- `call_endpoint docket-entries` for docket 73500242: 0 results (SCOTUS dockets carry no entry rows here).
- `search type=d court=scotus case_name="Hager v. Brinker"`: 0 results.
- `get_endpoint_item dockets 73500242`: case name "Blessing Nwosu v. 1600 West Loop South, L.L.C.", docket 25-1340, filed 2026-06-01, `date_terminated: null`. Confirms the petition is still pending, consistent with the forward cell.
- `search type=d court=scotus q=Nwosu`: 0 results.

## Web searches

None.
