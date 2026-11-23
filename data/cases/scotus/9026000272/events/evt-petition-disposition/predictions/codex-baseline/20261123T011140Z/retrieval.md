I consulted the committed `metrics/statpack.md` tables for modern cert dispositions, originating circuit, the paid segment's relists, CVSGs and amicus briefs, and the prior-Term federal band.

**Corpus**

I read the available filters with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`. I used the existing environment for both lookups.

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --docket-number 24A1030 --limit 1` returned the granted stay application in United States v. Shilling, May 6, 2025. The petition and both briefs describe the order's scope. `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --docket-number 18-676 --limit 1` returned the denial of the Karnoski petition on January 22, 2019. The Talbott petition describes the separate stay order. `ranged corpus reads: 1 GET(s), 262144 byte(s)`

**CourtListener MCP**

- `search` for Ninth Circuit opinions in Shilling, 25-2039, filed before November 23, 2026. The initial search and both retries returned HTTP 429.
- `search` for the Ninth Circuit docket in Shilling, 25-2039. The initial search and one retry returned HTTP 429.
- `search` for the D.D.C. docket in Talbott, 1:25-cv-00240. The first call returned HTTP 429. The second identified docket 69583866 but supplied no scheduling information.
- `call_endpoint` on `docket-entries` for docket 69583866, November 1–22, 2026, seeking a trial-scheduling update. The first call and one retry returned HTTP 429.
- `call_endpoint` on `dockets` for the Ninth Circuit docket 25-2039. The first call and one retry returned HTTP 429.

The statutory and case arguments used in the forecast come from the staged briefs and decision. I did no open-web searches.
