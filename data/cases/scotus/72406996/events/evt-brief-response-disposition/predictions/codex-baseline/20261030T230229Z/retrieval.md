# Retrieval record

## Local CLI and aggregate context

- `uv run fedcourts paths --court scotus --docket 72406996 --event evt-brief-response-disposition --role predictor`: failed before execution because the default uv cache is read-only. Reissued with `UV_NO_CACHE=1`; succeeded and supplied the event path. No evaluator-only file was opened.
- `uv run fedcourts query --help`: same cache failure. `UV_NO_CACHE=1 uv run fedcourts query --help`: succeeded. The help was viewed twice, the second time through `tail -85`, to check supported structured filters and cutoff behavior.
- `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition denied --decided-before 2016 --limit 3`: completed successfully after a substantial wait. It returned one sparse historical denial row, scotus/206, docket 93-5124, era 1990s, with empty caption, no opinion, and no application-kind information. This is not an informative substantive-application comparator and did not alter the forecast. Its stderr transfer line was exactly `ranged corpus reads: 917 GET(s), 240123904 byte(s)`.
- Read `metrics/statpack.md`, interim-docket section, and `metrics/statpack.json`'s interim keys and Term rows. Computed the eligible 2006–2015 window with jq: 0 substantive resolutions, 0 grants, 12,403 unparsed applications. No baseline exists under the minimum-50 rule. Later/current-Term aggregate rates were visible in the table but were not used as substitutes.

## Web calls

1. One search call with two queries: `site.supremecourt.gov opinions Hill McDonough 2006 stay execution equitable 584` and `site.supremecourt.gov opinions 2008 Baze Rees stay execution significant possibility`. Results included a 2015 Arthur filing, later unrelated capital filings, and an official Glossip opinion; none was opened or used. No own-application outcome was sought.
2. Opened the expected official Baze PDF path on supremecourt.gov, `/opinions/07pdf/07-5439.pdf`. It returned an internal fetch error and supplied no text.
3. Search: `Hill McDonough 547 U.S. 573 584 stay execution significant possibility success merits`. Results included the pre-2016 Nken opinion and unrelated filings. No own-case outcome was used.
4. Opened the reproduced Supreme Court opinion Nken v. Holder, 556 U.S. 418 (2009), on Justia, path `/cases/federal/us/556/418/`. Read its stay standard and requirement to justify discretionary interim relief; did not use its immigration facts as a capital-case comparator.

No CourtListener MCP lookup, own-case docket lookup, linked-petition lookup, or outcome lookup was attempted. The single corpus query's full reported transfer is recorded above; no full opinion bodies were requested.
