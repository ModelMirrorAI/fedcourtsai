# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era modern --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:` line
  was printed (the query never reached the corpus). No priors retrieved;
  proceeded on the provisioned inputs and the committed statpack.
- Read the committed `metrics/statpack.md` for base rates: modern
  discretionary-cert disposition split, relist-count buckets, CVSG buckets,
  originating-court table (incl. state courts), and the per-Term table
  (paid/IFP filings, grant rates).

## CourtListener MCP

- `search(type=d, court=scotus, docket_number="25-1235")` → 0 results.
- `search(type=d, court=scotus, q="Leslie Sanders" "Long Beach")` → 0 results.

Both were a forward-mode sanity check that the petition is not already decided
(mis-provisioned cell). The docket is not in CourtListener's search index;
nothing outcome-revealing surfaced. No further retrieval — the case is
fact-bound and the provisioned petition text plus statpack base rates were
sufficient.

## Web searches

None.
