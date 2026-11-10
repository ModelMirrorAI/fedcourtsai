# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --case-name "Horseracing Integrity" --limit 20` (and `--case-name "National Horsemen"`)
   - Result: Failed with exit code 2 (`No such option: --case-name`; re-issued using `--docket-number`).

2. `uv run fedcourts query --court scotus --docket-number 26-201`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned companion FTC petition `scotus/9026000201` (*Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.*), distributed for Conference of `2026-12-04`.

3. `uv run fedcourts query --court scotus --docket-number 25-1325`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned Sixth Circuit petition `scotus/73500226` (*Oklahoma v. United States*), distributed for Conference of `2026-10-09`, still open (`disposition: null`).

4. `uv run fedcourts query --court scotus --docket-number 24-433`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned prior Authority petition `scotus/72484144`, `disposition: "gvr"` on `2025-06-30`.

5. `uv run fedcourts query --court scotus --docket-number 24-429`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned prior FTC petition `scotus/72484140`, `disposition: "gvr"` on `2025-06-30`.

6. `uv run fedcourts query --court scotus --docket-number 24A287`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned prior emergency stay application `scotus/69315289`, `disposition: "granted"` on `2024-10-28`.

7. `uv run fedcourts query --court scotus --docket-number 25-1325 --full`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Confirmed full record metadata for `scotus/73500226`.

8. `uv run fedcourts query --court scotus --docket-number 26-201 --full`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Confirmed full record metadata for `scotus/9026000201`.

9. `uv run fedcourts query --court scotus --docket-number 24-472 --full`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned prior NHBPA cross-petition `scotus/72484185`, `disposition: "gvr"` on `2025-06-30`.

10. `uv run fedcourts query --court scotus --docket-number 23-402 --full`
    - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Result: Returned first Sixth Circuit petition `scotus/72479967` (*Oklahoma, et al. v. United States, et al.*), `disposition: "denied"` on `2024-06-24`.

11. `uv run fedcourts query --court scotus --docket-number 26-332 --full`
    - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Result: Returned Gulf Coast cross-petition `scotus/9026000332`, distributed for Conference of `2026-12-04`.

12. `uv run fedcourts query --court scotus --docket-number 26-335 --full`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Returned Texas cross-petition `scotus/9026000335`, distributed for Conference of `2026-12-04`.

13. `uv run fedcourts query --court scotus --docket-number 26-445 --full`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Unrelated docket (`adidas America, Inc. v. Thom Browne, Inc.`).

14. `uv run fedcourts query --court scotus --docket-number 24-420 --full`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Returned Eighth Circuit petition `scotus/72484133` (*Walmsley v. FTC*), `disposition: "gvr"` on `2025-06-30`.

## CourtListener MCP & Web Search

- No CourtListener MCP calls or external web searches were needed beyond the provisioned case record and local corpus lookups.
