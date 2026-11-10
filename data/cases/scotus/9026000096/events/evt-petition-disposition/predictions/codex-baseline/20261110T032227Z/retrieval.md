# Retrieval record

## Provisioned inputs and local reference material

Read the prediction contract and output schemas, then the event definition, `record/context.json`, `record/snapshots/2026-11-10.json`, document manifest and questions presented; consulted the federal petition, Tribes' opposition, federal cert reply, matching lower-court opinion and lower-court docket. Read the related manifest and provisioned **Vide** companion snapshot for No. 26-109. No companion disposition was requested separately.

Beyond the provisioned case materials, consulted `metrics/statpack.md` and selected fields of `metrics/statpack.json` for the modern-cert, federal-band, originating-circuit, relist, CVSG and amicus cuts. A local jq calculation pooled the displayed federal reached rows for Terms before 2026: 155/212, matching the frozen cert anchor. Read the roster spellings in `src/fedcourtsai/pipeline/justices.py` and the schemas for prediction/tooling/flags. No material under `data/qp-topics/`, another prediction, an evaluation, or the realized-outcome file was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000096 --event evt-petition-disposition --role predictor` failed before execution because the default uv cache at `/home/codexcell/.cache/uv` was read-only. No case information was returned.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000096 --event evt-petition-disposition --role predictor` succeeded, returning the expected case/event paths and marking the outcome evaluator-only. The outcome was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` was called, then called once more with output restricted to the structured-filter options. These were help reads, not corpus queries.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '605 U.S. 168' --citation '601 U.S. 42' --limit 2` attempted a known-precedent lookup for Seven County Infrastructure Coalition and Department of Agriculture v. Kirtz, authorities mentioned in the provisioned federal papers. It returned **no rows**. Stderr reported:

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

   It also warned that only 200 SCOTUS rows in scope had reporter citations, that the filter matches a case's own citations rather than a citing-authority graph, and that an empty result more likely reflects coverage than nonexistence. No opinion body or adverse inference was taken from this result. The unset `DECIDED_BEFORE` variable was checked; this cell is forward mode.

No CourtListener MCP call, direct CourtListener REST call, or `open-events` call was attempted. No package was installed. The contract's validation command was run using the writable uv cache; validation is a local output check, not case retrieval.

## Web calls

Searches were confined in purpose to general statutory text, not the predicted petition's disposition or subsequent history.

1. One `web.run` search call contained these queries:
   - `site.uscode.house.gov 43 1702 1716 public lands without regard acquired ownership exchange`
   - `site.govinfo.gov FLPMA 701(f) nothing in this Act shall be deemed to repeal any existing law by implication`
2. An open call requested `https://uscode.house.gov/us/usc/119-120/t43/s1716/` for the statutory exchange provision.
3. A further search call contained:
   - `43 USC 1702 public lands without regard to how acquired ownership`
   - `Federal Land Policy Management Act 701(f) existing law implication`

Each web call returned no readable response in the tool transcript. Accordingly, these were attempted checks, not successful independent source verification, and no search result or fetched page was incorporated into the forecast. The intended references were the official 43 U.S.C. 1702(e) public-lands definition, 43 U.S.C. 1716(a) exchange authority, and FLPMA section 701(f)'s anti-implied-repeal provision. I instead used their text as reproduced in the provisioned filings. No factual update to this case's procedural record or legislative enactment was taken from web retrieval. The probability rests on the provisioned pre-decision filings, docket and committed base rates, not web coverage of this case.
