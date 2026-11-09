# Retrieval log
- WebFetch supremecourt.gov docket 26-117 (Milligan): distributed 10/16, 11/6, 11/13; motion to dismiss or affirm filed 9/18.
- WebFetch supremecourt.gov docket 26-116: matches the snapshot; no entries after 11/9.
- WebSearch (extended) "Alabama congressional map Supreme Court Milligan Caster 2026 appeal Callais": Callais decided 2026; the Court stayed the 26 May PI on 2 Jun 2026; the cases are pending.
- WebFetch scotusblog.com/2026/11/mootness-maps-and-motor-vehicles: relist watch summarizing the mootness dispute; describes the cases as pending.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3` — `ranged corpus reads: 36 GET(s), 9437184 byte(s)`; generic GVR priors, not case-specific.
- `uv run fedcourts query --docket-number 26-117`: printed usage help (no row returned / flag usage issue); no transfer line.
- `uv run fedcourts query --court scotus --disposition gvr --era modern`: usage error (bad era value); no data.
- Read `metrics/statpack.md` relist-count cut.
