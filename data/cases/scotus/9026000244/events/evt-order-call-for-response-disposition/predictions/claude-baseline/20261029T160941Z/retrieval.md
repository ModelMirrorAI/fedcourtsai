# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 24-304` failed at first: I omitted `--court`, and the usage error named it. Re-issued with `--court scotus`, it returned the *Labcorp v. Davis* row (scotus/69981163) and printed `ranged corpus reads: 12 GET(s), 3145728 byte(s)`.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` was rejected: `modern` is not an era token.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` returned five recent grants, none on point. It printed `ranged corpus reads: 24 GET(s), 6291456 byte(s)`.
- `metrics/statpack.md`: I read the band, relist, CVSG, amicus and circuit cuts.
- WebFetch of the supremecourt.gov docket page for 26-244 showed the petition still pending, with entries through 2026-10-20: two extensions of the response deadline (now 2026-12-04) and amicus briefs from the Retail Litigation Center and the Chamber of Commerce et al. (2026-10-05).
- WebSearch "Supreme Court certiorari uninjured class members Rule 23(b)(3) Article III 2026 petition granted after LabCorp" returned only 2025 coverage of *Labcorp* (the grant, the argument, the DIG). It found nothing about this case's disposition.
- No CourtListener MCP calls.
