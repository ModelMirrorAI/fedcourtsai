# Retrieval log

- `uv run fedcourts query --help`: read the flags.
- `uv run fedcourts query --court scotus --citation "977 F.3d 984" --limit 5`
  - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
  - It returned no rows. A `note:` said only 200 scotus rows carry citations.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5`
  - It returned "Unknown era 'modern'" (an era is a decade token) and no rows. I ran it a second time to read the error; same result.
- `uv run fedcourts query --court scotus --disposition denied --limit 5`
  - stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  - It returned 5 recent unrelated denials. None was used.
- Web search: "Supreme Court certiorari pretrial detainee medical care objective
  standard Kingsley circuit split 2026"
  - Results: this petition's PDF on supremecourt.gov, plus prior petitions on
    the same split (Sanchez 17-1638, Strain 20-1562, County of San Diego v.
    Sandoval amicus, 23-259 amicus, 21-1210 amicus) and a law-review article.
  - No result claimed a disposition of this petition.
- Committed `metrics/statpack.md`: base rates (salience band, relist, CVSG,
  circuit).
- No CourtListener MCP calls.
