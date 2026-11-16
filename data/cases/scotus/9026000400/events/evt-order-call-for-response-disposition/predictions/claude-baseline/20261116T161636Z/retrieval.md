# Retrieval log

Beyond the provisioned inputs:

1. `uv run fedcourts query --help` — read usage.
2. `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — usage error (bad `--era` value); nothing returned.
3. `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 33 GET(s), 8585216 byte(s)`. Five recent granted rows (Robinhood Markets v. Sodha; two Mullin v. … dockets; Goldman Sachs Bank USA v. Brown; Scanlan v. Coalition for Open Democracy). Generic; not used in the number.
4. `uv run fedcourts query --court scotus --docket-number 24-304` — `ranged corpus reads: 17 GET(s), 4456448 byte(s)`. A guessed docket number that happened to return the *Laboratory Corp. of America Holdings v. Davis* row; I read only the caption and counsel list from the truncated output.
5. `metrics/statpack.md` — salience-band table (sal-v8), relist-count cut, amicus-brief-count cut.
6. Web search (standard): "Supreme Court certiorari granted 2026 class certification uninjured class members Article III standing after Labcorp v. Davis" — returned 2025 commentary on the *Labcorp* grant and dismissal (barclaydamon.com, winston.com, natlawreview.com, tcpaworld.com, atlanticlegal.org, jdsupra.com topic pages). No 2026 grant on the question and nothing about this petition's disposition or anyone's forecast of it surfaced. No pages were opened.

No CourtListener MCP calls were made.
