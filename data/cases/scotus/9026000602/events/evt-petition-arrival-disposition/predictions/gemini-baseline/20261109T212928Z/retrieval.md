# Retrieval Log (`scotus/9026000602`, `evt-petition-arrival-disposition`)

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "587 U.S. 554" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned: 1 row (`scotus/15006766`, *Bradley Weston Taggart v. Shelley A. Lorenzen, Executor of the Estate of Stuart Brown, et al.*, No. 18-489, 587 U.S. 554 (2019), `disposition: "granted"`, `merits_judgment: "vacated"`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Stderr transfer line: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Returned: 5 rows of recent 2020s SCOTUS cert denials (`scotus/73500344`, `scotus/73500351`, `scotus/73500384`, `scotus/73522552`, `scotus/73523164`).

3. `uv run fedcourts query --court scotus --docket-number 25A442`
   - Stderr transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned: 1 row (`scotus/73278760`, *Palanikumar V. Gnanam, et al. v. Nathaniel Chibuzor Keita, et al.*, No. 25A442, `application_kind: "extension"`, filed `2025-10-20`, decided `2025-11-21`, `disposition: "granted"`).

## CourtListener MCP Lookups

- None attempted (the state county-court orders, appellate orders, and hearing transcripts were comprehensively reproduced in `record/documents/appendix.txt` and `record/documents/petition.txt`).

## Web Searches

- None attempted.
