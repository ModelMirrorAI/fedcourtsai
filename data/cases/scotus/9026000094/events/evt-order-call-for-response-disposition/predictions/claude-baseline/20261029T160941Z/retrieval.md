# Retrieval

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: printed usage help rather than rows (the `--era` value was not accepted); re-issued below.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`
  - stderr: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
  - Returned five recent GVR priors (e.g. Monsanto v. Dennis, Hobson v. United States). Used only to check the shape of the GVR population; none is on point.
- WebFetch of the Court's docket page for No. 26-94 (supremecourt.gov). It showed the BIO (Oct 5), the reply (Oct 20) and a distribution for the 11/6/2026 conference. No disposition.
- Committed `metrics/statpack.md` read for base rates.
- No CourtListener MCP calls.
