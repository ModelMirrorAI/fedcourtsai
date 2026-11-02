# Retrieval

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 8`: rejected with a usage message (`modern` is not a valid era token).
- `uv run fedcourts query --court scotus --disposition gvr --limit 8`
  - `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
  - Returned recent GVR rows, including Hobson v. United States (26-5216) and Whitehead v. United States.
- `uv run fedcourts query --docket-number 26-5216`: usage error (needs `--court`).
- `uv run fedcourts query --court scotus --docket-number 26-5216`
  - `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
  - Result: GVR on 2026-10-13, CA5 origin, one distribution, no response requested recorded.
- WebSearch (standard): "Abouammo v. United States venue Supreme Court 2026 remanded in light of"
  - Returned the case summary (decided 11 June 2026, 9-0, Kagan, J.) and a supremecourt.gov PDF, "25-7462 Whitehead Mem GVR" (an SG memorandum on a GVR in light of *Abouammo*).
  - Nothing about this case's own disposition.
- Statpack (`metrics/statpack.md`): read the modern-cert, circuit, relist, CVSG, amicus and sal-v6 band sections.
- No CourtListener MCP calls.
