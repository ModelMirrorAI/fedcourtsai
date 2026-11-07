# Retrieval
- WebFetch supremecourt.gov docket 26-199 (HISA v. NHBPA): petition filed 8/10/2026, responses and reply in, DISTRIBUTED for Conference of 12/4/2026.
- WebFetch supremecourt.gov docket 26-201 (FTC v. NHBPA): same posture, DISTRIBUTED for Conference of 12/4/2026.
- `uv run fedcourts query --court scotus --docket-number 26-335`: returned the Texas v. Black row (open). `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: usage error (unknown era token); re-issued below.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3`: 3 recent GVR priors, none on point. `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
- Read `metrics/statpack.md` relist-count and amicus-count cuts (paid scored segment).
- No CourtListener MCP calls.
